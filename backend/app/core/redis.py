"""Upstash Redis client — snapshot cache / rate-limit / lock only.

No historical market data belongs here. Quote cache key format: `quote:{symbol}`,
TTL 30s (see app/modules/stocks).
"""

from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import get_settings


@lru_cache
def get_redis() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)
