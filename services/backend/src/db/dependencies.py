# dependencies.py

from db.session import get_connection_pool
from db.repositories import PostgresImageRepository
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__)

_image_repository = None


def get_image_repository():
    """
    Retrieve or create a singleton instance of the image repository.

    This function initializes the PostgresImageRepository with a connection pool,
    if it doesn't already exist. The repository instance is reused across multiple calls
    to manage database operations.

    Returns:
        PostgresImageRepository: An instance of the image repository.
    """
    global _image_repository
    if _image_repository is None:
        pool = get_connection_pool()
        _image_repository = PostgresImageRepository(pool)
        logger.info(f"Connecting to DB: {config.database_url}")
    return _image_repository
