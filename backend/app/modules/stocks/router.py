"""Stocks module — API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.redis import get_redis
from app.modules.stocks.repository import StocksRepository
from app.modules.stocks.schemas import QuoteResponse
from app.modules.stocks.service import StocksService
from app.providers.fugle import FugleError, FugleProvider

router = APIRouter(prefix="/api/v1/stocks", tags=["stocks"])


def get_stocks_service(session: AsyncSession = Depends(get_db)) -> StocksService:
    return StocksService(StocksRepository(session), FugleProvider(), get_redis())


@router.get("/{symbol}/quote", response_model=QuoteResponse)
async def get_quote(
    symbol: str, service: StocksService = Depends(get_stocks_service)
) -> QuoteResponse:
    """Intraday snapshot quote, polled by the frontend every 30s.

    Cache-aside on Redis (`quote:{symbol}`, TTL 30s); a miss falls through to
    Fugle.
    """
    try:
        return await service.get_quote(symbol)
    except FugleError as exc:
        # 上游行情商掛掉是 502，不是我們的 500 —— 也避免把 API key 相關的
        # 錯誤訊息原文吐給呼叫端。
        raise HTTPException(status_code=502, detail="行情來源暫時無法取得") from exc
