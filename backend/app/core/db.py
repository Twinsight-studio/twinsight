"""Async SQLAlchemy engine, wired for Supabase's Supavisor transaction-mode
pooler (port 6543).

Rules (CEO-mandated, do not change without sign-off — see docs/infra/gcp-setup.md):
- Psycopg 3 async driver, not asyncpg.
- NullPool: the pooler already pools connections; a local pool on top of a
  transaction-mode pooler causes prepared-statement/session-state bugs.
- prepare_threshold=None: disables server-side prepared statements, which
  transaction-mode pooling does not support across pooled connections.
- No pool_pre_ping: NullPool opens a fresh connection per checkout anyway.
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,
    connect_args={"prepare_threshold": None},
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency: yields a request-scoped AsyncSession."""
    async with async_session_factory() as session:
        yield session
