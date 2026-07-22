"""SQLAlchemy ORM models — the whole schema lives here.

Single file on purpose: Alembic autogenerate needs one metadata object, and
at ~10 tables the navigation cost of splitting per module outweighs the
benefit. Modules own their *queries* (repository.py), not their tables.

No `users` table by design — TwInsight v1 is single-user (see
docs/plans/2026-07-22-data-layer.md). Add user_id via migration if that
ever changes.
"""

from datetime import date as Date
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy import (
    Date as SADate,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# Prices/indicators keep 4 dp; ratios and percentages keep 2-4 dp. Numeric
# (not float) throughout — these are money-adjacent and get compared for
# equality in screener rules.
_PRICE = Numeric(12, 4)
_RATIO = Numeric(10, 4)


class Stock(Base):
    """上市櫃股票主檔 — 證交所 OpenAPI."""

    __tablename__ = "stocks"

    symbol: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    industry: Mapped[str | None] = mapped_column(String(50))
    # TSE = 上市, OTC = 上櫃
    market: Mapped[str] = mapped_column(String(10))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DailyPrice(Base):
    """日線 OHLCV — yfinance."""

    __tablename__ = "daily_prices"

    symbol: Mapped[str] = mapped_column(
        String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"), primary_key=True
    )
    date: Mapped[Date] = mapped_column(SADate, primary_key=True)
    open: Mapped[Decimal] = mapped_column(_PRICE)
    high: Mapped[Decimal] = mapped_column(_PRICE)
    low: Mapped[Decimal] = mapped_column(_PRICE)
    close: Mapped[Decimal] = mapped_column(_PRICE)
    volume: Mapped[int] = mapped_column(BigInteger)


# Screener scans "latest bar across the whole market", so date-first lookups
# matter as much as per-symbol history.
Index("ix_daily_prices_date", DailyPrice.date)


class TechnicalIndicator(Base):
    """盤後預先算好的技術指標 — 來源是 daily_prices，非外部 API.

    預算而非查詢時即算：P3 選股要對全市場掃技術面條件，即算撐不住規格書的
    「頁面 <2 秒」。
    """

    __tablename__ = "technical_indicators"

    symbol: Mapped[str] = mapped_column(
        String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"), primary_key=True
    )
    date: Mapped[Date] = mapped_column(SADate, primary_key=True)

    ma5: Mapped[Decimal | None] = mapped_column(_PRICE)
    ma10: Mapped[Decimal | None] = mapped_column(_PRICE)
    ma20: Mapped[Decimal | None] = mapped_column(_PRICE)
    ma60: Mapped[Decimal | None] = mapped_column(_PRICE)

    rsi14: Mapped[Decimal | None] = mapped_column(_RATIO)
    kd_k: Mapped[Decimal | None] = mapped_column(_RATIO)
    kd_d: Mapped[Decimal | None] = mapped_column(_RATIO)

    macd: Mapped[Decimal | None] = mapped_column(_RATIO)
    macd_signal: Mapped[Decimal | None] = mapped_column(_RATIO)
    macd_hist: Mapped[Decimal | None] = mapped_column(_RATIO)

    bb_upper: Mapped[Decimal | None] = mapped_column(_PRICE)
    bb_middle: Mapped[Decimal | None] = mapped_column(_PRICE)
    bb_lower: Mapped[Decimal | None] = mapped_column(_PRICE)


Index("ix_technical_indicators_date", TechnicalIndicator.date)


class InstitutionalTrade(Base):
    """三大法人買賣超 — FinMind. 單位：股."""

    __tablename__ = "institutional_trades"

    symbol: Mapped[str] = mapped_column(
        String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"), primary_key=True
    )
    date: Mapped[Date] = mapped_column(SADate, primary_key=True)
    foreign_net: Mapped[int] = mapped_column(BigInteger, default=0)
    trust_net: Mapped[int] = mapped_column(BigInteger, default=0)
    dealer_net: Mapped[int] = mapped_column(BigInteger, default=0)
    total_net: Mapped[int] = mapped_column(BigInteger, default=0)


Index("ix_institutional_trades_date", InstitutionalTrade.date)


class MarginTrading(Base):
    """融資融券餘額 — FinMind. 單位：張."""

    __tablename__ = "margin_trading"

    symbol: Mapped[str] = mapped_column(
        String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"), primary_key=True
    )
    date: Mapped[Date] = mapped_column(SADate, primary_key=True)
    margin_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    margin_change: Mapped[int] = mapped_column(BigInteger, default=0)
    short_balance: Mapped[int] = mapped_column(BigInteger, default=0)
    short_change: Mapped[int] = mapped_column(BigInteger, default=0)


Index("ix_margin_trading_date", MarginTrading.date)


class MajorHolder(Base):
    """千張大戶持股 — FinMind，每週更新."""

    __tablename__ = "major_holders"

    symbol: Mapped[str] = mapped_column(
        String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"), primary_key=True
    )
    date: Mapped[Date] = mapped_column(SADate, primary_key=True)
    # 千張以上持股比率 (%)
    holder_ratio: Mapped[Decimal | None] = mapped_column(_RATIO)
    holder_count: Mapped[int | None] = mapped_column(BigInteger)


class Valuation(Base):
    """每日估值 — FinMind (本益比/股價淨值比/殖利率)."""

    __tablename__ = "valuations"

    symbol: Mapped[str] = mapped_column(
        String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"), primary_key=True
    )
    date: Mapped[Date] = mapped_column(SADate, primary_key=True)
    pe_ratio: Mapped[Decimal | None] = mapped_column(_RATIO)
    pb_ratio: Mapped[Decimal | None] = mapped_column(_RATIO)
    dividend_yield: Mapped[Decimal | None] = mapped_column(_RATIO)


Index("ix_valuations_date", Valuation.date)


class FinancialStatement(Base):
    """季度財報 — FinMind. period_end 為該季最後一日."""

    __tablename__ = "financial_statements"

    symbol: Mapped[str] = mapped_column(
        String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"), primary_key=True
    )
    period_end: Mapped[Date] = mapped_column(SADate, primary_key=True)
    eps: Mapped[Decimal | None] = mapped_column(_RATIO)
    revenue: Mapped[int | None] = mapped_column(BigInteger)
    roe: Mapped[Decimal | None] = mapped_column(_RATIO)


class ScreenerResult(Base):
    """每日選股結果 — 盤後批次寫入."""

    __tablename__ = "screener_results"

    date: Mapped[Date] = mapped_column(SADate, primary_key=True)
    symbol: Mapped[str] = mapped_column(
        String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"), primary_key=True
    )
    # 命中的規則名稱，逗號分隔（例：'rsi_oversold,kd_golden_cross'）
    matched_rules: Mapped[str] = mapped_column(Text)
    score: Mapped[Decimal] = mapped_column(_RATIO, default=0)


class WatchlistItem(Base):
    """自選股 — 單人使用，symbol 即唯一鍵."""

    __tablename__ = "watchlist"

    symbol: Mapped[str] = mapped_column(
        String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"), primary_key=True
    )
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AlertSetting(Base):
    """警示設定 — 輪詢報價時由後端判斷是否觸發.

    alert_type: 'pct_change' | 'break_high' | 'volume_spike'
    """

    __tablename__ = "alert_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(10), ForeignKey("stocks.symbol", ondelete="CASCADE"))
    alert_type: Mapped[str] = mapped_column(String(20))
    threshold: Mapped[Decimal] = mapped_column(_RATIO)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


Index("ix_alert_settings_symbol", AlertSetting.symbol)


class JobRun(Base):
    """批次執行紀錄 — 沒有這張表，批次靜默失敗時你不會知道."""

    __tablename__ = "job_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # 'running' | 'success' | 'failed'
    status: Mapped[str] = mapped_column(String(20), default="running")
    message: Mapped[str | None] = mapped_column(Text)


Index("ix_job_runs_job_name_started_at", JobRun.job_name, JobRun.started_at)
