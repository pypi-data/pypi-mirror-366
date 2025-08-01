from os import getenv

class PostgresClient():
    """Abstract base class for database clients."""
    def __init__(self):
        self.user = getenv("POSTGRES_USER")
        self.password = getenv("POSTGRES_PASSWORD")
        self.host = getenv("POSTGRES_HOST")
        self.port = getenv("POSTGRES_PORT")
        self.dbname = getenv("POSTGRES_DB")

        if not self.user:
            raise EnvironmentError("POSTGRES_USER environment variable is not set")
        if not self.password:
            raise EnvironmentError("POSTGRES_PASSWORD environment variable is not set")
        if not self.host:
            raise EnvironmentError("POSTGRES_HOST environment variable is not set")
        if not self.port:
            raise EnvironmentError("POSTGRES_PORT environment variable is not set")
        if not self.dbname:
            raise EnvironmentError("POSTGRES_DB environment variable is not set")

        # psycopg connection parameters
        self.connection_params = {
            "host": self.host,
            "port": self.port,
            "dbname": self.dbname,
            "user": self.user,
            "password": self.password
        }
