"""歷史日線 OHLCV — yfinance.

No API key. Data is ~15 min delayed intraday, which is fine because this
only ever feeds the post-market batch; live quotes come from Fugle.

yfinance is synchronous and does network I/O, so every public call here is
wrapped in `asyncio.to_thread` to keep the batch job's event loop free.
"""

import asyncio
from decimal import Decimal

import pandas as pd
import yfinance as yf

from app.providers.types import DailyBar

# 台股在 Yahoo 的代號後綴：上市 .TW、上櫃 .TWO
_SUFFIX = {"TSE": ".TW", "OTC": ".TWO"}



def to_yahoo_symbol(symbol: str, market: str) -> str:
    return f"{symbol}{_SUFFIX.get(market, '.TW')}"


def _to_decimal(value: object) -> Decimal | None:
    if value is None or pd.isna(value):
        return None
    # str() first: Decimal(float) carries the float's binary noise into the
    # DB column, which then shows up in screener comparisons.
    return Decimal(str(round(float(value), 4)))


def _frame_to_bars(symbol: str, frame: pd.DataFrame) -> list[DailyBar]:
    bars: list[DailyBar] = []
    for index, row in frame.iterrows():
        close = _to_decimal(row.get("Close"))
        if close is None:
            continue  # 尚未收盤或停牌，整列跳過
        open_ = _to_decimal(row.get("Open")) or close
        high = _to_decimal(row.get("High")) or close
        low = _to_decimal(row.get("Low")) or close
        raw_volume = row.get("Volume")
        volume = 0 if raw_volume is None or pd.isna(raw_volume) else int(raw_volume)
        bars.append(
            DailyBar(
                symbol=symbol,
                date=index.date() if hasattr(index, "date") else index,
                open=open_,
                high=high,
                low=low,
                close=close,
                volume=volume,
            )
        )
    return bars


def _fetch_sync(yahoo_symbol: str, period: str) -> pd.DataFrame:
    ticker = yf.Ticker(yahoo_symbol)
    return ticker.history(period=period, interval="1d", auto_adjust=False)


class YFinanceProvider:
    """Fetches daily OHLCV history."""

    async def fetch_history(
        self, symbol: str, market: str = "TSE", period: str = "1y"
    ) -> list[DailyBar]:
        """period 用 yfinance 語法：'1mo' / '6mo' / '1y' / '5y' / 'max'."""
        yahoo_symbol = to_yahoo_symbol(symbol, market)
        frame = await asyncio.to_thread(_fetch_sync, yahoo_symbol, period)
        if frame is None or frame.empty:
            return []
        return _frame_to_bars(symbol, frame)
