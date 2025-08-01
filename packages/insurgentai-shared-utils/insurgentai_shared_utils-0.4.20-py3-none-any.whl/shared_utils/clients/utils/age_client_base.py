from abc import ABC, abstractmethod
from typing import Any, ContextManager
from .postgres_client import PostgresClient

class AGEClientBase(ABC):
    """Abstract base class for apache age enabeld database clients."""
    def __init__(self):
        self._postgres_client = PostgresClient()
        # Expose postgres client attributes for easy access
        self.user = self._postgres_client.user
        self.password = self._postgres_client.password
        self.host = self._postgres_client.host
        self.port = self._postgres_client.port
        self.dbname = self._postgres_client.dbname
        self.connection_params = self._postgres_client.connection_params

    @abstractmethod
    def managed_connection(self) -> ContextManager[Any]:
        """context-managed connection with auto commit/rollback/close."""
        pass

    @abstractmethod
    def create_connection(self) -> Any:
        """Caller is responsible for commit/rollback/close."""
        pass
