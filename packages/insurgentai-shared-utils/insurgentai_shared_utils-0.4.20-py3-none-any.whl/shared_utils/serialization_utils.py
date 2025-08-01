from uuid import UUID
from functools import wraps
from unicodedata import normalize
import inspect
import re

def deserialize_event(contract_class):
    """
    Decorator to deserialize event data into an event contract class instance.
    Works with both sync and async callback functions.
    """
    def decorator(callback_fn):
        # Check if the callback is an async function
        if inspect.iscoroutinefunction(callback_fn):
            @wraps(callback_fn)
            async def async_wrapper(msg_id, event_data):
                try:
                    obj = contract_class(**event_data)
                except Exception as e:
                    print(f"Deserialization failed for {contract_class.__name__}: {e}")
                    return
                return await callback_fn(obj)
            return async_wrapper
        else:
            @wraps(callback_fn)
            def sync_wrapper(msg_id, event_data):
                try:
                    obj = contract_class(**event_data)
                except Exception as e:
                    print(f"Deserialization failed for {contract_class.__name__}: {e}")
                    return
                return callback_fn(obj)
            return sync_wrapper
    return decorator

def to_db_repr(string):
    return string.replace("'", '"').replace("\\", "/")

def to_age_graph_id(u: UUID) -> str:
    """
    Converts a UUID to an Apache AGE-compatible graph name string.
    Ensures the name:
    - Contains only valid identifier characters (letters, digits, underscores)
    """
    return f"{str(u).replace('-', '_')}"

def normalize_entity_id(name: str) -> str:
    """
    Normalize arbitrary entity names into deterministic string IDs.
    - Strips accents
    - Lowercases
    - Replaces non-alphanumeric runs with a single underscore
    - Trims leading/trailing underscores
    - Collapses internal whitespace
    """
    # Normalize Unicode characters (e.g., é -> e)
    name = normalize('NFKD', name)
    name = name.encode('ascii', 'ignore').decode('ascii')
    
    # Lowercase
    name = name.lower()

    # Replace any sequence of non-alphanumeric characters with underscore
    name = re.sub(r'[^a-z0-9]+', '_', name)

    # Trim leading/trailing underscores
    name = name.strip('_')

    return name