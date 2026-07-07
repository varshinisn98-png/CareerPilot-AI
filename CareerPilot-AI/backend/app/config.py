from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/careerpilot"

    # JWT
    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Gemini
    gemini_api_key: str = ""

    # App
    app_env: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:8501"

    # Upload
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10

    # Vector DB
    vector_db_path: str = "vector_db"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
