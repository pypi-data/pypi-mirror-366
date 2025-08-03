from contextlib import asynccontextmanager
from psycopg import AsyncConnection
from .utils.age_client_base import AGEClientBase

class AsyncAGEClient(AGEClientBase):
    """AGE client for connecting to a PostgreSQL database with Apache AGE extension.
    Requires environment variables:
    - POSTGRES_USER: The username for the database.
    - POSTGRES_PASSWORD: The password for the database.
    - POSTGRES_HOST: The host of the database (default: localhost).
    - POSTGRES_PORT: The port of the database (default: 5432).
    - POSTGRES_DB: The name of the database.
    """
    def __init__(self):
        super().__init__()

    @asynccontextmanager
    async def managed_connection(self):
        """context-managed async connection with auto commit/rollback/close."""
        conn: AsyncConnection = await AsyncConnection.connect(**self.connection_params)
        try:
            await self._setup_age_session(conn)
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise
        finally:
            await conn.close()

    async def create_connection(self) -> AsyncConnection:
        """Caller is responsible for commit/rollback/close."""
        conn: AsyncConnection = await AsyncConnection.connect(**self.connection_params)
        self._setup_age_session(conn)
        return conn

    async def _setup_age_session(self, conn: AsyncConnection) -> None:
        """Setup AGE environment for each session."""
        try:
            async with conn.cursor() as cur:
                await cur.execute("LOAD 'age';")
                await cur.execute("SET search_path = ag_catalog, '$user', public;")
        except Exception:
            raise RuntimeError("Failed to load AGE extension. Ensure it is installed in the PostgreSQL database.")


async_age_client = AsyncAGEClient()  # module level singleton instance