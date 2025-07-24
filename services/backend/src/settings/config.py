from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for resolving relative paths
BASE_DIR = Path(__file__).parent.parent.parent


load_dotenv()


class AppConfig(BaseSettings):
    UPLOAD_DIR: Path
    LOG_DIR: Path
    FRONTEND_DIR: Path = BASE_DIR.parent / "frontend"

    WEB_SERVER_WORKERS: int
    WEB_SERVER_START_PORT: int

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / "backend/.env"),
        env_file_encoding="utf-8"
    )


# Global application config instance
config = AppConfig()

