
from psycopg_pool import ConnectionPool
from db.dto import ImageDTO, ImageDetailsDTO
from exceptions.repository_errors import EntityCreationError, EntityDeletionError, QueryExecutionError
from psycopg.errors import Error as PsycopgError
from settings.logging_config import get_logger

logger = get_logger(__name__)


class PostgresImageRepository:

    def __init__(self, pool: ConnectionPool):
        self._pool = pool


    def create(self, image: ImageDTO) -> ImageDetailsDTO:
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

                    return ImageDetailsDTO(
                        id=db_id,
                        filename=image.filename,
                        original_name=image.original_name,
                        size=image.size,
                        file_type=image.file_type,
                        upload_time=upload_time.isoformat() if upload_time else None,
                    )
        except PsycopgError as e:
            raise EntityCreationError("Image", str(e))
        except Exception as e:
            raise EntityCreationError("Image", str(e))



    def delete_by_filename(self, filename: str) -> bool:
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



    def get_list_paginated(self, limit: int, offset: int) -> list[ImageDetailsDTO]:
        query = """
            SELECT id, filename, original_name, size, upload_time, file_type::text
            FROM images
            ORDER BY upload_time DESC
            LIMIT %s OFFSET %s
        """
        try:
            with self._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (limit, offset))
                    results = cur.fetchall()

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
        except PsycopgError as e:
            raise QueryExecutionError("get_list_paginated", str(e))


    def count_all(self) -> int:
        query = "SELECT COUNT(*) FROM images"
        try:
            with self._pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    return cur.fetchone()[0]
        except PsycopgError as e:
            raise QueryExecutionError("count_all", str(e))


