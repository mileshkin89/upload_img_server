# session.py

from typing import Optional
from psycopg_pool import ConnectionPool
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__)

_pool: Optional[ConnectionPool] = None


def get_connection_pool() -> ConnectionPool:
    """
    Retrieve or create a connection pool for PostgreSQL.

    This function initializes a connection pool for PostgreSQL if it doesn't already exist.
    The connection pool is reused across multiple calls to avoid redundant database connections.

    Returns:
        ConnectionPool: A psycopg connection pool object.
    """
    global _pool
    if _pool is None:
        logger.info(f"Creating connection pool with URL: {config.database_url}")
        _pool = ConnectionPool(
            conninfo=config.database_url,
            min_size=2,
            max_size=20,
            open=True
        )
    return _pool