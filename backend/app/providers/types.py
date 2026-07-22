"""Provider 之間共用的資料傳輸物件.

刻意**不** import pandas / yfinance 等重依賴：這些型別會被 repository 用到，
而 repository 會被 API 匯入，但 API image 不裝 pandas（見 Dockerfile.api）。
把 DTO 放在有 pandas 的模組裡，會讓 API 容器一啟動就 ModuleNotFoundError。
"""

from dataclasses import dataclass
from datetime import date as Date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class StockListing:
    symbol: str
    name: str
    industry: str | None
    market: str  # "TSE" | "OTC"


@dataclass(frozen=True, slots=True)
class DailyBar:
    symbol: str
    date: Date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
