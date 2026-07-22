"""Application settings, loaded from environment variables (.env in local dev)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"

    # PostgreSQL (docker-compose). Used by both the app (async engine) and
    # Alembic (sync engine) — same URL, the driver mode differs per engine.
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    redis_url: str = "redis://localhost:6379/0"

    # TODO: Fugle API credentials — backend-only, never exposed to frontend.
    fugle_api_key: str = ""

    jwt_secret: str = "change-me-in-production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
