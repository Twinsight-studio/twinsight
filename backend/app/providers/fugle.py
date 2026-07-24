"""即時報價 — Fugle MarketData REST.

Backend-only: this is the single place the Fugle API key is read
(`Settings.fugle_api_key`). It must never reach the frontend bundle.

REST snapshot rather than the WebSocket stream: v1 polls every 30s (see
README), so a stateless request per poll is enough and avoids holding a
subscription open.
"""

from datetime import UTC, datetime

import httpx

from app.core.config import get_settings

BASE_URL = "https://api.fugle.tw/marketdata/v1.0/stock"
_TIMEOUT = httpx.Timeout(10.0)


class FugleError(RuntimeError):
    """Raised when Fugle is unreachable, rejects the key, or omits a price."""


class FugleProvider:
    """Fetches intraday snapshot quotes."""

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key if api_key is not None else get_settings().fugle_api_key

    async def fetch_quote(self, symbol: str) -> dict:
        """回傳正規化後的報價欄位；失敗時丟 FugleError."""
        if not self._api_key:
            raise FugleError("FUGLE_API_KEY is not configured")

        url = f"{BASE_URL}/intraday/quote/{symbol}"
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.get(url, headers={"X-API-KEY": self._api_key})
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise FugleError(
                f"Fugle returned {exc.response.status_code} for {symbol}"
            ) from exc
        except httpx.HTTPError as exc:
            raise FugleError(f"Fugle request failed for {symbol}: {exc!r}") from exc

        # 盤前/停牌時沒有 lastPrice，退回參考價；兩者都沒有才算失敗。
        price = payload.get("lastPrice")
        if price is None:
            price = payload.get("previousClose") or payload.get("referencePrice")
        if price is None:
            raise FugleError(f"Fugle returned no price for {symbol}")

        return {
            "symbol": payload.get("symbol", symbol),
            "price": float(price),
            "change": float(payload.get("change") or 0.0),
            "change_percent": float(payload.get("changePercent") or 0.0),
            "volume": int(payload.get("total", {}).get("tradeVolume") or 0),
            "updated_at": datetime.now(UTC),
        }
