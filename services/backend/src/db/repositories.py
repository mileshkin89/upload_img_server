"""
repositories.py

Image repository implementation for PostgreSQL using psycopg connection pool.

This module provides a concrete repository class (`PostgresImageRepository`) to perform
CRUD operations on the `images` table, including creation, deletion, pagination,
sorting, and total record counting. It also handles low-level database exceptions and
wraps them in domain-specific custom errors.
"""

from psycopg_pool import ConnectionPool
from db.dto import ImageDTO, ImageDetailsDTO
from exceptions.repository_errors import EntityCreationError, EntityDeletionError, QueryExecutionError
from psycopg.errors import Error as PsycopgError
from settings.logging_config import get_logger

logger = get_logger(__name__)


class PostgresImageRepository:
    """
    Repository class for managing image entities stored in a PostgreSQL database.

    This class provides methods to create, delete, and retrieve image records,
    including support for pagination and sorting. It operates using a connection pool
    for efficient access to the database.
    """
    def __init__(self, pool: ConnectionPool):
        """
        Initializes the repository with a PostgreSQL connection pool.

        Args:
            pool (ConnectionPool): An instance of psycopg's connection pool.
        """
        self._pool = pool


    def create(self, image: ImageDTO) -> ImageDetailsDTO:
        """
        Inserts a new image record into the database.

        Args:
            image (ImageDTO): Data transfer object containing image metadata.

        Returns:
            ImageDetailsDTO: An object containing the stored image details, including
            generated ID and upload time.

        Raises:
            EntityCreationError: If the insert operation fails.
        """
        query = """
            INSERT INTO images (filename, original_name, size, file_type)
            VALUES (%s, %s, %s, %s)
            RETURNING id, upload_time
        """
        try:
            with self._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        query,
                        (image.filename, image.original_name, image.size, image.file_type),
                    )
                    db_id, upload_time = cur.fetchone()
                    conn.commit()
        except PsycopgError as e:
            raise EntityCreationError("Image", str(e))
        except Exception as e:
            raise EntityCreationError("Image", str(e))
        else:
            return ImageDetailsDTO(
                id=db_id,
                filename=image.filename,
                original_name=image.original_name,
                size=image.size,
                file_type=image.file_type,
                upload_time=upload_time.isoformat() if upload_time else None,
            )



    def delete_by_filename(self, filename: str) -> bool:
        """
         Deletes an image record by its unique filename.

         Args:
             filename (str): The UUID-based filename of the image to delete.

         Returns:
             bool: True if the image was successfully deleted, False if no matching record was found.

         Raises:
             EntityDeletionError: If the deletion operation fails.
         """
        query = "DELETE FROM images WHERE filename = %s RETURNING id"
        try:
            with self._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (filename,))
                    result = cur.fetchone()
                    conn.commit()
                    return result is not None
        except PsycopgError as e:
            raise EntityDeletionError("Image", filename, str(e))



    def get_list_paginated_sorted(self, limit: int, offset: int, sort_param: str, sort_value: str) -> list[ImageDetailsDTO]:
        """
        Retrieves a paginated and sorted list of images.

        Args:
            limit (int): The maximum number of records to return.
            offset (int): The number of records to skip (for pagination).
            sort_param (str): The column name to sort by (e.g., 'upload_time').
            sort_value (str): The sort direction ('ASC' or 'DESC').

        Returns:
            list[ImageDetailsDTO]: A list of image records as DTOs.

        Raises:
            QueryExecutionError: If the query execution fails.
        """
        query = f"""
            SELECT id, filename, original_name, size, upload_time, file_type::text
            FROM images
            ORDER BY {sort_param} {sort_value.upper()}
            LIMIT %s OFFSET %s
        """
        try:
            with self._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (limit, offset))
                    results = cur.fetchall()
        except PsycopgError as e:
            raise QueryExecutionError("get_list_paginated", str(e))
        else:
            return [
                ImageDetailsDTO(
                    id=row[0],
                    filename=row[1],
                    original_name=row[2],
                    size=row[3],
                    upload_time=row[4].isoformat() if row[4] else None,
                    file_type=row[5],
                )
                for row in results
            ]


    def count_all(self) -> int:
        """
        Returns the total number of image records in the database.

        Returns:
            int: Total number of records in the `images` table.

        Raises:
            QueryExecutionError: If the count query fails.
        """
        query = "SELECT COUNT(*) FROM images"
        try:
            with self._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    return cur.fetchone()[0]
        except PsycopgError as e:
            raise QueryExecutionError("count_all", str(e))


