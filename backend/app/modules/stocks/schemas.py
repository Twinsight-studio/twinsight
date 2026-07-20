"""Pydantic schemas for the stocks module."""

from datetime import datetime

from app.core.schema import CamelModel


class QuoteResponse(CamelModel):
    """Intraday snapshot quote. Served from Redis (`quote:{symbol}`, TTL 30s),
    refreshed from the Fugle provider on cache miss.
    """

    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    updated_at: datetime
