"""技術指標計算的測試 — 純函式，不碰網路或 DB."""

from datetime import date, timedelta
from decimal import Decimal

from app.modules.technical.calculator import MIN_BARS, compute_indicators
from app.providers.types import DailyBar


def _bars(closes: list[float], start: date = date(2026, 1, 1)) -> list[DailyBar]:
    return [
        DailyBar(
            symbol="TEST",
            date=start + timedelta(days=i),
            open=Decimal(str(c)),
            high=Decimal(str(c + 1)),
            low=Decimal(str(c - 1)),
            close=Decimal(str(c)),
            volume=1000 + i,
        )
        for i, c in enumerate(closes)
    ]


def test_returns_empty_when_not_enough_bars() -> None:
    # MA60 需要 60 根；不足時給一堆 None 沒有意義，直接不算。
    assert compute_indicators("TEST", _bars([100.0] * (MIN_BARS - 1))) == []


def test_row_per_bar() -> None:
    bars = _bars([100.0 + i for i in range(80)])
    assert len(compute_indicators("TEST", bars)) == len(bars)


def test_ma5_matches_hand_calculation() -> None:
    closes = [float(i) for i in range(1, 81)]  # 1..80
    rows = compute_indicators("TEST", _bars(closes))
    # 最後 5 天是 76,77,78,79,80 → 平均 78
    assert rows[-1].ma5 == Decimal("78.0000")


def test_flat_series_has_neutral_rsi_and_zero_macd() -> None:
    # 價格完全不動：RSI 無漲跌可比（NaN→None），MACD 兩條線重合故為 0。
    rows = compute_indicators("TEST", _bars([50.0] * 80))
    last = rows[-1]
    assert last.ma5 == last.ma20 == Decimal("50.0000")
    assert last.macd == Decimal("0.0000")


def test_bollinger_bands_are_ordered() -> None:
    closes = [100.0 + (i % 7) for i in range(80)]  # 有波動才有帶寬
    last = compute_indicators("TEST", _bars(closes))[-1]
    assert last.bb_lower < last.bb_middle < last.bb_upper


def test_macd_histogram_is_macd_minus_signal() -> None:
    closes = [100.0 + (i % 11) * 1.5 for i in range(80)]
    last = compute_indicators("TEST", _bars(closes))[-1]
    assert abs(last.macd_hist - (last.macd - last.macd_signal)) < Decimal("0.01")
