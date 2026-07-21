"""Upstash Redis client — cross-container state only (API ↔ batch Job).

Cost policy: Upstash Free is 500K commands/month and is this architecture's
first paid bottleneck, while max-instances=1 means the API is a single
process — so anything the API alone needs (rate limit, quote cache) lives
in process memory, NOT here. Reach for Redis only when state must survive
the API container or be shared with the batch Job. No historical market
data belongs here either way.
"""

from functools import lru_cache

from redis.asyncio import Redis

from app.core.config import get_settings


@lru_cache
def get_redis() -> Redis:
    settings = get_settings()
    return Redis.from_url(settings.redis_url, decode_responses=True)
