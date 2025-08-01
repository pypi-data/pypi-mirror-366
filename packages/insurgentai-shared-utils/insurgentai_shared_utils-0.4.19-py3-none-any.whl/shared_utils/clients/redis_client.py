import asyncio
import logging
import os
import json
import redis
import threading
import inspect
import time
from typing import List, Optional, Union, Any, Dict, Set, Callable, Awaitable
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(threadName)s] %(levelname)s: %(message)s'
)

class RedisClient:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise EnvironmentError("REDIS_URL environment variable is not set")
        self._client = redis.from_url(redis_url)
        self._consumers = {}
        self._callbacks = {}
        self._stop_flags = {}
        self._max_concurrent_tasks = {}
        self._running_tasks: Dict[str, int] = {}
        
        # Thread safety locks
        self._consumer_lock = threading.RLock()  # For consumer creation/deletion
        self._callback_lock = threading.RLock()  # For callback registration
        self._task_count_locks: Dict[str, threading.Lock] = {}  # Per-stream task counting

    def send(self, stream: str, value: BaseModel):
        # Serialize entire object as single JSON string under 'data' field
        message = {"data": value.model_dump_json()}
        self._client.xadd(stream, message)

    # Key-Value Operations
    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis by key."""
        value = self._client.get(key)
        return value.decode('utf-8') if value else None

    def set(self, key: str, value: Union[str, int, float], ex: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis with optional expiration."""
        try:
            return self._client.set(key, str(value), ex=ex)
        except Exception:
            return False

    def get_json(self, key: str) -> Optional[Any]:
        """Get a JSON value from Redis by key and deserialize it."""
        value = self.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a JSON-serializable value in Redis."""
        try:
            json_str = json.dumps(value)
            return self.set(key, json_str, ex=ex)
        except (TypeError, ValueError):
            return False

    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in Redis."""
        return self._client.incrby(key, amount)

    def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement a numeric value in Redis."""
        return self._client.decrby(key, amount)

    def delete(self, *keys: str) -> int:
        """Delete one or more keys from Redis."""
        return self._client.delete(*keys)

    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        return bool(self._client.exists(key))

    def expire(self, key: str, seconds: int) -> bool:
        """Set an expiration time for a key."""
        return bool(self._client.expire(key, seconds))

    def ttl(self, key: str) -> int:
        """Get the time-to-live of a key in seconds."""
        return self._client.ttl(key)

    def create_consumer(self, stream: str, group_id: str, max_concurrent_tasks: int = 10):
        """Create a consumer thread for a specific stream with a maximum number of concurrent tasks."""
        with self._consumer_lock:
            if stream in self._consumers:
                raise RuntimeError(f"Consumer for stream '{stream}' already exists.")

            try:
                self._client.xgroup_create(stream, group_id, id='0', mkstream=True)
            except redis.exceptions.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise

            # Initialize stream settings
            self._callbacks[stream] = []
            self._stop_flags[stream] = False
            self._max_concurrent_tasks[stream] = max_concurrent_tasks
            self._running_tasks[stream] = 0
            self._task_count_locks[stream] = threading.Lock()  # Per-stream lock

        # Dedicated thread for this stream's consumer
        def consume_loop():
            # Create a thread-local event loop for this consumer thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            consumer_name = f"{group_id}-consumer"
            while not self._stop_flags[stream]:

                # Calculate how many messages to read from stream based on currently running tasks
                with self._task_count_locks[stream]:
                    running_task_count = self._running_tasks[stream]
                
                # Skip reading messages if we're at or over the max concurrent tasks limit
                if running_task_count >= self._max_concurrent_tasks[stream]:
                    # Sleep briefly to avoid CPU spinning when at capacity
                    time.sleep(0.1)
                    continue
                    
                read_count = self._max_concurrent_tasks[stream] - running_task_count
                
                resp = self._client.xreadgroup(
                    groupname=group_id,
                    consumername=consumer_name,
                    streams={stream: '>'},
                    count=read_count,
                    block=1000
                )
                if not resp:
                    continue

                # Process messages using the thread-local event loop
                try:
                    loop.run_until_complete(self.handle_messages_async(resp, stream, group_id, loop))
                except Exception as e:
                    print(f"Error processing messages: {e}")

            # Clean up the event loop
            loop.close()

        t = threading.Thread(target=consume_loop, daemon=True, name=f"RedisConsumer-{stream}")
        t.start()
        self._consumers[stream] = t

    def register_callback(self, stream: str, group_id: str, callback: Union[Callable[[str, Any], None], Callable[[str, Any], Awaitable[None]]]):
        """Register a callback for a stream. Creates a consumer if one doesn't exist."""
        with self._callback_lock:
            # Create a consumer if one doesn't exist
            if stream not in self._consumers:
                self.create_consumer(stream, group_id)
            
            # Add the callback to the stream's callback list
            if stream in self._callbacks:
                self._callbacks[stream].append(callback)
            else:
                self._callbacks[stream] = [callback]

    # def handle_messages_sync(self, redis_response, stream:str, group_id:str):
    #     """process messages serially, executing callbacks serially as well"""
    #     for _, messages in redis_response:
    #         for msg_id, fields in messages:
    #             data_json = fields.get(b'data') or fields.get('data')
    #             if data_json:
    #                 try:
    #                     val = json.loads(data_json)
    #                 except Exception:
    #                     val = None
    #             else:
    #                 val = None
    #             for cb in self._callbacks[stream]:
    #                 cb(msg_id, val)
    #             self._client.xack(stream, group_id, msg_id)

    async def handle_messages_async(self, redis_response, stream: str, group_id: str, loop: asyncio.AbstractEventLoop):
        """Process messages asynchronously with proper task tracking."""
        tasks = []
        for _, messages in redis_response:
            for msg_id, fields in messages:
                data_json = fields.get(b'data') or fields.get('data')
                if data_json:
                    try:
                        val = json.loads(data_json)
                    except Exception:
                        val = None
                else:
                    val = None

                # Create a task for this message
                task = loop.create_task(
                    self._process_message(stream, group_id, msg_id, val)
                )
                
                # Track the task
                with self._task_count_locks[stream]:
                    self._running_tasks[stream] += 1
                
                # Add done callback to remove task from tracking
                task.add_done_callback(
                    lambda t, s=stream: self._decrement_task_count(s)
                )
                
                tasks.append(task)
        
        # Wait for all tasks to complete if there are any
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _decrement_task_count(self, stream: str):
        """Decrement the task count for a stream."""
        if stream in self._task_count_locks:
            with self._task_count_locks[stream]:
                if stream in self._running_tasks and self._running_tasks[stream] > 0:
                    self._running_tasks[stream] -= 1

    async def _process_message(self, stream: str, group_id: str, msg_id: str, val: Any):
        """Process a single message by executing all callbacks and then acknowledging."""
        try:
            # Execute all callbacks for this message
            for cb in self._callbacks[stream]:
                try:
                    # Check if callback is a coroutine function
                    if inspect.iscoroutinefunction(cb):
                        await cb(msg_id, val)
                    else:
                        # Run non-async callback in a thread pool
                        logging.info(f"Running non-async callback {cb} in thread pool")
                        await asyncio.to_thread(cb, msg_id, val)
                except Exception as e:
                    logging.error(f"Error in callback for stream {stream}: {e}")
        finally:
            # Always acknowledge the message after all callbacks are executed
            self._client.xack(stream, group_id, msg_id)

    def stop_consumer(self, stream: str):
        """Stop a consumer thread and clean up resources."""
        with self._consumer_lock:
            if stream in self._stop_flags:
                self._stop_flags[stream] = True
                self._consumers[stream].join()
                del self._consumers[stream]
                del self._callbacks[stream]
                del self._stop_flags[stream]
                
                if stream in self._max_concurrent_tasks:
                    del self._max_concurrent_tasks[stream]
                if stream in self._running_tasks:
                    del self._running_tasks[stream]
                if stream in self._task_count_locks:
                    del self._task_count_locks[stream]


redis_client = RedisClient()  # module level singleton instance
    