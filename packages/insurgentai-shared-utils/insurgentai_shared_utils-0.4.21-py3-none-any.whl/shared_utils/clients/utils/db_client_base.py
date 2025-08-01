from abc import ABC, abstractmethod
from typing import Any, ContextManager
from .postgres_client import PostgresClient
from sqlmodel import Session, create_engine


class DBClientBase():
    """Abstract base class for postgres database clients."""
    def __init__(self):
        self._postgres_client = PostgresClient()
        # Expose postgres client attributes for easy access
        self.user = self._postgres_client.user
        self.password = self._postgres_client.password
        self.host = self._postgres_client.host
        self.port = self._postgres_client.port
        self.dbname = self._postgres_client.dbname
    
    @abstractmethod
    def managed_session(self) -> ContextManager[Any]:
        """context-managed session with auto commit/rollback/close."""
        pass

    @abstractmethod
    def create_session(self) -> Session:
        """Caller is responsible for commit/rollback/close."""
        pass
