"""Application settings, loaded from environment variables (.env in local dev)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "local"

    # Supavisor transaction-mode pooler (port 6543) — used at runtime by the
    # API service and the batch job. See docs/infra/gcp-setup.md.
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    # Supavisor session-mode pooler (port 5432) — used only by Alembic
    # migrations, which need a real session (not transaction pooling).
    database_migration_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    redis_url: str = "redis://localhost:6379/0"

    # TODO: Fugle API credentials — backend-only, never exposed to frontend.
    fugle_api_key: str = ""

    jwt_secret: str = "change-me-in-production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
