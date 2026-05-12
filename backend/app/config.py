from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Notes API"
    environment: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./notes.db"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
