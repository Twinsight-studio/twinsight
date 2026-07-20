"""Alembic migration environment.

Runs against Supabase's Supavisor SESSION-mode pooler (port 5432), not the
transaction-mode pooler the app uses at runtime — migrations need a real
session, and CI runners are IPv4-only so the IPv6 direct endpoint is out.
Sync Psycopg 3, plain engine (no NullPool tuning needed here).
"""

from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context
from app.core.config import get_settings

# TODO: import Base.metadata from app models once models exist, e.g.:
# from app.core.models import Base
# target_metadata = Base.metadata
target_metadata = None

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

settings = get_settings()


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_migration_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(settings.database_migration_url)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
