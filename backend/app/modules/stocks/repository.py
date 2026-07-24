"""Stocks module — repository layer (persistence)."""

from collections.abc import Iterable, Sequence
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import DailyPrice, Stock
from app.providers.types import DailyBar, StockListing

# Postgres caps a statement at 65535 bind parameters. daily_prices has 7
# columns, so 1000 rows/statement leaves plenty of headroom and keeps each
# transaction small enough to retry cheaply.
CHUNK_SIZE = 1000


def chunks(rows: Sequence[dict], size: int = CHUNK_SIZE) -> Iterable[Sequence[dict]]:
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


class StocksRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_symbols(self, market: str | None = None) -> list[tuple[str, str]]:
        """回傳 (symbol, market) 清單，供批次決定要抓哪些股票."""
        statement = select(Stock.symbol, Stock.market).order_by(Stock.symbol)
        if market:
            statement = statement.where(Stock.market == market)
        result = await self._session.execute(statement)
        return [(row[0], row[1]) for row in result.all()]

    async def upsert_stocks(self, listings: Sequence[StockListing]) -> int:
        """主檔用 upsert：每天重跑要能更新改名/改產業，而不是重複插入."""
        if not listings:
            return 0

        rows: list[dict[str, Any]] = [
            {
                "symbol": listing.symbol,
                "name": listing.name,
                "industry": listing.industry,
                "market": listing.market,
            }
            for listing in listings
        ]

        for chunk in chunks(rows):
            statement = insert(Stock).values(list(chunk))
            statement = statement.on_conflict_do_update(
                index_elements=[Stock.symbol],
                set_={
                    "name": statement.excluded.name,
                    "industry": statement.excluded.industry,
                    "market": statement.excluded.market,
                },
            )
            await self._session.execute(statement)

        await self._session.commit()
        return len(rows)

    async def upsert_daily_prices(self, bars: Sequence[DailyBar]) -> int:
        """同一天重跑要覆蓋而非爆主鍵衝突（盤中跑過、收盤後再跑一次很常見）."""
        if not bars:
            return 0

        rows: list[dict[str, Any]] = [
            {
                "symbol": bar.symbol,
                "date": bar.date,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in bars
        ]

        for chunk in chunks(rows):
            statement = insert(DailyPrice).values(list(chunk))
            statement = statement.on_conflict_do_update(
                index_elements=[DailyPrice.symbol, DailyPrice.date],
                set_={
                    "open": statement.excluded.open,
                    "high": statement.excluded.high,
                    "low": statement.excluded.low,
                    "close": statement.excluded.close,
                    "volume": statement.excluded.volume,
                },
            )
            await self._session.execute(statement)

        await self._session.commit()
        return len(rows)
