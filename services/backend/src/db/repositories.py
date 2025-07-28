
from psycopg_pool import ConnectionPool
from db.dto import ImageDTO, ImageDetailsDTO
from exceptions.repository_errors import EntityCreationError, EntityDeletionError
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



