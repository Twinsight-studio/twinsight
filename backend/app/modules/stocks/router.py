"""Stocks module — API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.modules.stocks.provider import FugleProvider
from app.modules.stocks.repository import StocksRepository
from app.modules.stocks.schemas import QuoteResponse
from app.modules.stocks.service import StocksService

router = APIRouter(prefix="/api/v1/stocks", tags=["stocks"])


def get_stocks_service(session: AsyncSession = Depends(get_db)) -> StocksService:
    return StocksService(StocksRepository(session), FugleProvider())


@router.get("/{symbol}/quote", response_model=QuoteResponse)
async def get_quote(
    symbol: str, service: StocksService = Depends(get_stocks_service)
) -> QuoteResponse:
    """Intraday snapshot quote, polled by the frontend every 30s.

    Cache-aside on Redis (`quote:{symbol}`, TTL 30s); miss falls through to
    the Fugle provider. TODO: implement StocksService.get_quote.
    """
    return await service.get_quote(symbol)
