"""Technical module — repository layer (persistence)."""

from collections.abc import Sequence
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import TechnicalIndicator
from app.modules.stocks.repository import chunks
from app.modules.technical.calculator import IndicatorRow

_INDICATOR_FIELDS = (
    "ma5",
    "ma10",
    "ma20",
    "ma60",
    "rsi14",
    "kd_k",
    "kd_d",
    "macd",
    "macd_signal",
    "macd_hist",
    "bb_upper",
    "bb_middle",
    "bb_lower",
)


class TechnicalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_indicators(self, indicators: Sequence[IndicatorRow]) -> int:
        """重算覆蓋：指標是從 daily_prices 推導的，來源修正後要能重跑."""
        if not indicators:
            return 0

        rows: list[dict[str, Any]] = [
            {
                "symbol": row.symbol,
                "date": row.date,
                **{field: getattr(row, field) for field in _INDICATOR_FIELDS},
            }
            for row in indicators
        ]

        for chunk in chunks(rows):
            statement = insert(TechnicalIndicator).values(list(chunk))
            statement = statement.on_conflict_do_update(
                index_elements=[TechnicalIndicator.symbol, TechnicalIndicator.date],
                set_={
                    field: getattr(statement.excluded, field)
                    for field in _INDICATOR_FIELDS
                },
            )
            await self._session.execute(statement)

        await self._session.commit()
        return len(rows)
