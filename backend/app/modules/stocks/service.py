"""Stocks module — service layer.

TODO: implement. Flow for get_quote: check Redis key `quote:{symbol}`
(TTL 30s) -> on hit return cached QuoteResponse -> on miss call
FugleProvider.fetch_quote and write the result back to Redis with TTL 30s.
"""

from app.modules.stocks.provider import FugleProvider
from app.modules.stocks.repository import StocksRepository
from app.modules.stocks.schemas import QuoteResponse


class StocksService:
    def __init__(self, repository: StocksRepository, provider: FugleProvider) -> None:
        self._repository = repository
        self._provider = provider

    async def get_quote(self, symbol: str) -> QuoteResponse:
        raise NotImplementedError
