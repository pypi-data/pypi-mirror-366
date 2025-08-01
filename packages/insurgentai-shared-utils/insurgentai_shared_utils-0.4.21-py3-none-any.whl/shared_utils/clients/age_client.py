from contextlib import contextmanager
import psycopg
from psycopg import Connection
from .utils.age_client_base import AGEClientBase

class AGEClient(AGEClientBase):
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

    @contextmanager
    def managed_connection(self):
        """context-managed connection with auto commit/rollback/close."""
        conn: Connection = psycopg.connect(**self.connection_params)
        try:
            self._setup_age_session(conn)
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def create_connection(self) -> Connection:
        """Caller is responsible for commit/rollback/close."""
        conn = psycopg.connect(**self.connection_params)
        self._setup_age_session(conn)
        conn.commit()  # commit required after setup. SEE: https://github.com/apache/age/issues/2195
        return conn

    def _setup_age_session(self, conn: Connection) -> None:
        """Setup AGE environment for each session."""
        try:
            with conn.cursor() as cur:
                cur.execute("LOAD 'age';")
                cur.execute("SET search_path = ag_catalog, '$user', public;")
        except Exception:
            raise RuntimeError("Failed to load AGE extension. Ensure it is installed in the PostgreSQL database.")


age_client = AGEClient()  # module level singleton instance
