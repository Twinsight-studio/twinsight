"""External market-data provider client (Fugle).

TODO: implement. This is the only place allowed to hold/use the Fugle API
key (app.core.config.Settings.fugle_api_key) — never expose it to the
frontend.
"""

from app.modules.stocks.schemas import QuoteResponse


class FugleProvider:
    """TODO: implement Fugle REST/WebSocket client for quote lookups."""

    async def fetch_quote(self, symbol: str) -> QuoteResponse:
        raise NotImplementedError
