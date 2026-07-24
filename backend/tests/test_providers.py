"""Provider 的純邏輯測試 — 不打真實外部 API（CI 不該依賴外網）."""

import pytest

from app.providers.fugle import FugleError, FugleProvider
from app.providers.twse import _parse
from app.providers.yfinance_client import to_yahoo_symbol


def test_parse_keeps_only_four_digit_common_stock() -> None:
    rows = [
        {"公司代號": "2330", "公司簡稱": "台積電", "產業別": "24"},
        {"公司代號": "0050", "公司簡稱": "元大台灣50", "產業別": ""},  # ETF，保留（4 碼數字）
        {"公司代號": "00878", "公司簡稱": "國泰永續高股息"},  # 5 碼 ETF → 濾掉
        {"公司代號": "2330R", "公司簡稱": "某權證"},  # 含字母 → 濾掉
        {"公司代號": "2317", "公司簡稱": ""},  # 無簡稱 → 濾掉
    ]
    parsed = _parse(rows, "TSE")
    assert [p.symbol for p in parsed] == ["2330", "0050"]
    assert parsed[0].name == "台積電"
    assert parsed[0].market == "TSE"


def test_parse_maps_empty_industry_to_none() -> None:
    (listing,) = _parse([{"公司代號": "2330", "公司簡稱": "台積電", "產業別": ""}], "TSE")
    assert listing.industry is None


def test_parse_supports_tpex_english_field_names() -> None:
    rows = [{"SecuritiesCompanyCode": "1240", "CompanyAbbreviation": "茂生農經"}]
    (listing,) = _parse(rows, "OTC")
    assert (listing.symbol, listing.name, listing.market) == ("1240", "茂生農經", "OTC")


def test_yahoo_symbol_suffix_differs_by_market() -> None:
    assert to_yahoo_symbol("2330", "TSE") == "2330.TW"
    assert to_yahoo_symbol("6488", "OTC") == "6488.TWO"
    # 未知市場別退回上市，總比整個抓不到好
    assert to_yahoo_symbol("2330", "???") == "2330.TW"


async def test_fugle_without_api_key_raises_rather_than_calling_out() -> None:
    with pytest.raises(FugleError, match="not configured"):
        await FugleProvider(api_key="").fetch_quote("2330")
