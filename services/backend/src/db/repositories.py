
from psycopg_pool import ConnectionPool
from db.dto import ImageDTO, ImageDetailsDTO
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
        except Exception as e:
            logger.error(f"Error create image record in DB: ", str(e))


