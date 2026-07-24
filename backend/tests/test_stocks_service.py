"""報價服務的快取行為 — 用假的 Redis，CI 沒有 Redis 容器."""

from datetime import UTC, datetime

from app.modules.stocks.service import StocksService, quote_cache_key


class FakeRedis:
    """只實作 get/set，並記錄呼叫次數."""

    def __init__(self, *, fail: bool = False) -> None:
        self.store: dict[str, str] = {}
        self.fail = fail
        self.set_calls: list[tuple[str, int | None]] = []

    async def get(self, key: str) -> str | None:
        if self.fail:
            raise ConnectionError("redis down")
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        if self.fail:
            raise ConnectionError("redis down")
        self.store[key] = value
        self.set_calls.append((key, ex))


class CountingProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def fetch_quote(self, symbol: str) -> dict:
        self.calls += 1
        return {
            "symbol": symbol,
            "price": 100.0 + self.calls,  # 每次不同，才看得出是否走快取
            "change": 1.0,
            "change_percent": 1.0,
            "volume": 500,
            "updated_at": datetime.now(UTC),
        }


def _service(redis: FakeRedis, provider: CountingProvider) -> StocksService:
    return StocksService(repository=None, provider=provider, redis=redis)


async def test_miss_calls_provider_and_caches_with_30s_ttl() -> None:
    redis, provider = FakeRedis(), CountingProvider()
    quote = await _service(redis, provider).get_quote("2330")

    assert provider.calls == 1
    assert quote.symbol == "2330"
    assert redis.set_calls == [(quote_cache_key("2330"), 30)]


async def test_second_call_is_served_from_cache() -> None:
    redis, provider = FakeRedis(), CountingProvider()
    service = _service(redis, provider)

    first = await service.get_quote("2330")
    second = await service.get_quote("2330")

    assert provider.calls == 1, "第二次不該再打 Fugle"
    assert first.price == second.price


async def test_different_symbols_do_not_share_cache() -> None:
    redis, provider = FakeRedis(), CountingProvider()
    service = _service(redis, provider)

    await service.get_quote("2330")
    await service.get_quote("2317")

    assert provider.calls == 2
    assert set(redis.store) == {quote_cache_key("2330"), quote_cache_key("2317")}


async def test_redis_failure_still_serves_the_quote() -> None:
    # 快取是最佳化不是資料來源；Redis 掛了 endpoint 不該跟著掛。
    redis, provider = FakeRedis(fail=True), CountingProvider()
    quote = await _service(redis, provider).get_quote("2330")

    assert quote.symbol == "2330"
    assert provider.calls == 1
