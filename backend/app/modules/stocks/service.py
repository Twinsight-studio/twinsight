"""Stocks module — service layer."""

from redis.asyncio import Redis

from app.modules.stocks.repository import StocksRepository
from app.modules.stocks.schemas import QuoteResponse
from app.providers.fugle import FugleProvider

QUOTE_CACHE_TTL_SECONDS = 30


def quote_cache_key(symbol: str) -> str:
    return f"quote:{symbol}"


class StocksService:
    def __init__(
        self,
        repository: StocksRepository,
        provider: FugleProvider,
        redis: Redis,
    ) -> None:
        self._repository = repository
        self._provider = provider
        self._redis = redis

    async def get_quote(self, symbol: str) -> QuoteResponse:
        """Cache-aside on Redis (`quote:{symbol}`, TTL 30s).

        A cache read failure must not take the endpoint down with it — Redis
        here is an optimisation, not the source of truth, so we fall through
        to the provider and simply skip the write-back.
        """
        key = quote_cache_key(symbol)

        cached = None
        try:
            cached = await self._redis.get(key)
        except Exception as exc:  # noqa: BLE001 — cache is best-effort
            print(f"[stocks] quote cache read failed for {symbol}: {exc!r}")

        if cached:
            return QuoteResponse.model_validate_json(cached)

        quote = QuoteResponse(**await self._provider.fetch_quote(symbol))

        try:
            await self._redis.set(
                key, quote.model_dump_json(), ex=QUOTE_CACHE_TTL_SECONDS
            )
        except Exception as exc:  # noqa: BLE001 — cache is best-effort
            print(f"[stocks] quote cache write failed for {symbol}: {exc!r}")

        return quote
