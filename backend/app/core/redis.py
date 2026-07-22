"""Redis client (docker-compose) — cache and cross-container state.

Per spec §7.2: intraday quote snapshots (TTL 30s), screener result cache
(TTL until next open), session data. The API's own rate limiting lives in
process memory instead (single process, no need to share). No historical
market data belongs here — that goes in PostgreSQL.
"""

from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import get_settings


@lru_cache
def get_redis() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)
