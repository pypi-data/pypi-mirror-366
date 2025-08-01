import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from .utils.db_client_base import DBClientBase

class AsyncDBClient(DBClientBase):
    """Async database client for connecting to a Postgres database.
    Requires environment variables:
    - POSTGRES_USER: The username for the database.
    - POSTGRES_PASSWORD: The password for the database.
    - POSTGRES_HOST: The host of the database (default: localhost).
    - POSTGRES_PORT: The port of the database (default: 5432).
    - POSTGRES_DB: The name of the database.
    """
    def __init__(self):
        super().__init__()
        self.database_url = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"
        self.engine = create_async_engine(self.database_url, echo=False)
        self.async_session_maker = async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    @asynccontextmanager
    async def managed_session(self):
        """context-managed async session with auto commit/rollback/close."""
        session = self.async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def create_session(self) -> AsyncSession:
        """Create a persistent async session. Caller is responsible for commit/rollback/close."""
        return self.async_session_maker()


# Module level singleton instance
async_db_client = AsyncDBClient()
