from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for resolving relative paths
BASE_DIR = Path(__file__).parent.parent.parent


load_dotenv()


class AppConfig(BaseSettings):
    UPLOAD_DIR: Path
    LOG_DIR: Path

    WEB_SERVER_WORKERS: int
    WEB_SERVER_START_PORT: int

    POSTGRES_DB: str
    POSTGRES_DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str

    MAX_FILE_SIZE: int = 5 * 1024 * 1024
    SUPPORTED_FORMATS: set[str] = {'.jpg', '.png', '.gif'}

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / "backend/.env"),
        env_file_encoding="utf-8"
    )

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection string.

        Returns:
            str: Database connection URL in format suitable for psycopg.
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_DB_PORT}/{self.POSTGRES_DB}"
        )


# Global application config instance
config = AppConfig()

