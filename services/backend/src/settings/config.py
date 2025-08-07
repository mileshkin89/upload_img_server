"""
config.py

Application configuration module.

Loads environment variables using `dotenv` and parses them into structured,
type-safe settings using `pydantic`. Provides a centralized and reusable
configuration object for application-wide access.

Features:
- Loads `.env` file from `backend/.env`.
- Validates and parses environment variables using `AppConfig`.
- Supports default values and type coercion.
- Resolves base paths for uploads and logs.
"""
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for resolving relative paths
BASE_DIR = Path(__file__).parent.parent.parent

load_dotenv()


class AppConfig(BaseSettings):
    """
    Application settings class.

    Inherits from `pydantic.BaseSettings` and automatically loads values
    from environment variables. Supports type validation and default values
    for commonly used application-level settings such as database credentials,
    file size limits, supported formats, and more.

    Attributes:
        UPLOAD_DIR (Path): Directory for uploaded files.
        LOG_DIR (Path): Directory where logs are stored.
        WEB_SERVER_WORKERS (int): Number of web server workers to launch.
        WEB_SERVER_START_PORT (int): Starting port number for worker processes.
        POSTGRES_DB (str): PostgreSQL database name.
        POSTGRES_DB_PORT (int): PostgreSQL port.
        POSTGRES_USER (str): PostgreSQL username.
        POSTGRES_PASSWORD (str): PostgreSQL password.
        POSTGRES_HOST (str): PostgreSQL hostname.
        MAX_FILE_SIZE (int): Maximum allowed file size in bytes (default: 5MB).
        SUPPORTED_FORMATS (set[str]): Set of supported file extensions.

    Configuration:
        Loads settings from the `.env` file located at `backend/.env` relative to BASE_DIR.
    """
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
        """
        Construct PostgreSQL connection string.

        Returns:
            str: Database connection URL in the format:
                postgresql://<user>:<password>@<host>:<port>/<database>
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_DB_PORT}/{self.POSTGRES_DB}"
        )


# Global application config instance
config = AppConfig()

