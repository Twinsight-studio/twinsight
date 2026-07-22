"""技術指標計算 — 純函式，輸入日線、輸出指標，不碰 DB 也不打外部 API.

盤後批次算好存表（見 docs/plans/2026-07-22-data-layer.md）：P3 選股要對全
市場掃技術面條件，查詢時即算撐不住規格書「頁面 <2 秒」的要求。

參數採台股慣例：KD 用 (9,3,3)、RSI 14、MACD (12,26,9)、布林 (20,2)。
"""

from dataclasses import dataclass
from datetime import date as Date
from decimal import Decimal

import pandas as pd
import pandas_ta as ta

from app.providers.types import DailyBar

MA_PERIODS = (5, 10, 20, 60)
RSI_LENGTH = 14
KD_K, KD_D, KD_SMOOTH = 9, 3, 3
MACD_FAST, MACD_SLOW, MACD_SIGNAL = 12, 26, 9
BB_LENGTH, BB_STD = 20, 2

# 算出所有指標所需的最少日線根數（MA60 是最長的窗）。少於這個數就只會得到
# 一堆 None，不如不算。
MIN_BARS = max(MA_PERIODS)


@dataclass(frozen=True, slots=True)
class IndicatorRow:
    symbol: str
    date: Date
    ma5: Decimal | None
    ma10: Decimal | None
    ma20: Decimal | None
    ma60: Decimal | None
    rsi14: Decimal | None
    kd_k: Decimal | None
    kd_d: Decimal | None
    macd: Decimal | None
    macd_signal: Decimal | None
    macd_hist: Decimal | None
    bb_upper: Decimal | None
    bb_middle: Decimal | None
    bb_lower: Decimal | None


def _dec(value: object, places: str = "0.0001") -> Decimal | None:
    if value is None or pd.isna(value):
        return None
    return Decimal(str(value)).quantize(Decimal(places))


def _pick(frame: pd.DataFrame | None, prefix: str) -> pd.Series | None:
    """按欄位前綴取值.

    pandas-ta 的欄位名帶參數且會隨版本變動（0.4.x 的布林是
    `BBL_20_2.0_2.0`，舊版是 `BBL_20_2.0`），寫死全名會在升版時靜默失效。
    """
    if frame is None:
        return None
    for column in frame.columns:
        if column.startswith(prefix):
            return frame[column]
    return None


def bars_to_frame(bars: list[DailyBar]) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "date": [b.date for b in bars],
            "open": [float(b.open) for b in bars],
            "high": [float(b.high) for b in bars],
            "low": [float(b.low) for b in bars],
            "close": [float(b.close) for b in bars],
            "volume": [b.volume for b in bars],
        }
    )
    return frame.sort_values("date").reset_index(drop=True)


def compute_indicators(symbol: str, bars: list[DailyBar]) -> list[IndicatorRow]:
    """回傳每個交易日一列指標；資料不足時回空 list."""
    if len(bars) < MIN_BARS:
        return []

    frame = bars_to_frame(bars)
    close, high, low = frame["close"], frame["high"], frame["low"]

    mas = {period: ta.sma(close, length=period) for period in MA_PERIODS}
    rsi = ta.rsi(close, length=RSI_LENGTH)
    stoch = ta.stoch(high, low, close, k=KD_K, d=KD_D, smooth_k=KD_SMOOTH)
    macd = ta.macd(close, fast=MACD_FAST, slow=MACD_SLOW, signal=MACD_SIGNAL)
    bbands = ta.bbands(close, length=BB_LENGTH, std=BB_STD)

    kd_k, kd_d = _pick(stoch, "STOCHk"), _pick(stoch, "STOCHd")
    macd_line, macd_hist = _pick(macd, "MACD_"), _pick(macd, "MACDh")
    macd_signal = _pick(macd, "MACDs")
    bb_lower, bb_mid, bb_upper = (
        _pick(bbands, "BBL"),
        _pick(bbands, "BBM"),
        _pick(bbands, "BBU"),
    )

    def at(series: pd.Series | None, i: int) -> object:
        return None if series is None else series.iloc[i]

    rows: list[IndicatorRow] = []
    for i in range(len(frame)):
        rows.append(
            IndicatorRow(
                symbol=symbol,
                date=frame["date"].iloc[i],
                ma5=_dec(at(mas[5], i)),
                ma10=_dec(at(mas[10], i)),
                ma20=_dec(at(mas[20], i)),
                ma60=_dec(at(mas[60], i)),
                rsi14=_dec(at(rsi, i)),
                kd_k=_dec(at(kd_k, i)),
                kd_d=_dec(at(kd_d, i)),
                macd=_dec(at(macd_line, i)),
                macd_signal=_dec(at(macd_signal, i)),
                macd_hist=_dec(at(macd_hist, i)),
                bb_upper=_dec(at(bb_upper, i)),
                bb_middle=_dec(at(bb_mid, i)),
                bb_lower=_dec(at(bb_lower, i)),
            )
        )
    return rows
