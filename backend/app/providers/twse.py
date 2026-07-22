"""證交所 / 櫃買中心 上市櫃股票清單.

No API key, no rate limit worth worrying about — this is the cheapest
source we have, so it is the one that defines the tradable universe.

TWSE publishes the listed-company table as JSON; TPEx (上櫃) has its own
endpoint. Both return one row per company, including non-common-stock
instruments we filter out (ETF/權證/存託憑證 have longer or lettered codes).
"""

import httpx

from app.providers.types import StockListing

TWSE_LISTED_URL = "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"
TPEX_LISTED_URL = "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O"

_TIMEOUT = httpx.Timeout(30.0)



def _is_common_stock(symbol: str) -> bool:
    """台股普通股是 4 位數字；ETF/權證/DR 等有更長或含字母的代號."""
    return len(symbol) == 4 and symbol.isdigit()


def _parse(rows: list[dict], market: str) -> list[StockListing]:
    out: list[StockListing] = []
    for row in rows:
        symbol = str(row.get("公司代號") or row.get("SecuritiesCompanyCode") or "").strip()
        if not _is_common_stock(symbol):
            continue
        name = str(row.get("公司簡稱") or row.get("CompanyAbbreviation") or "").strip()
        if not name:
            continue
        industry = str(row.get("產業別") or row.get("SecuritiesIndustryCode") or "").strip()
        out.append(
            StockListing(
                symbol=symbol,
                name=name,
                industry=industry or None,
                market=market,
            )
        )
    return out


class TwseProvider:
    """Fetches the listed-stock universe (上市 + 上櫃)."""

    async def fetch_listings(self) -> list[StockListing]:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            listings: list[StockListing] = []
            # 上櫃來源偶爾會掛；有上市的名單就還能運作，所以個別失敗不致命。
            for url, market in ((TWSE_LISTED_URL, "TSE"), (TPEX_LISTED_URL, "OTC")):
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    listings.extend(_parse(response.json(), market))
                except (httpx.HTTPError, ValueError) as exc:
                    if market == "TSE":
                        raise
                    print(f"[twse] {market} listing fetch failed, continuing: {exc!r}")

        # 同一代號理論上不會跨市場重複，但來源是兩個獨立檔案，去重比較保險。
        deduped: dict[str, StockListing] = {}
        for listing in listings:
            deduped.setdefault(listing.symbol, listing)
        return sorted(deduped.values(), key=lambda s: s.symbol)
