"""盤後批次 — 抓資料、算指標、寫 DB.

執行（收盤後，約 14:35）：
    docker compose run --rm job                    # 全市場
    docker compose run --rm job --limit 20         # 只跑前 20 檔，開發用
    docker compose run --rm job --symbols 2330,2317

流程：
    1. 證交所 OpenAPI → upsert `stocks` 主檔（決定可交易的股票池）
    2. yfinance      → upsert `daily_prices`
    3. 從 daily_prices 算指標 → upsert `technical_indicators`
    每一步都寫 `job_runs`，批次靜默失敗時才看得出來。

FinMind 的籌碼/財報尚未接上（需要 API token，見 docs/plans/）。
"""

import argparse
import asyncio
import traceback
from datetime import UTC, datetime

from sqlalchemy import update

from app.core.db import async_session_factory, engine
from app.core.models import JobRun
from app.modules.stocks.repository import StocksRepository
from app.modules.technical.calculator import compute_indicators
from app.modules.technical.repository import TechnicalRepository
from app.providers.twse import TwseProvider
from app.providers.yfinance_client import YFinanceProvider

JOB_NAME = "post_market_batch"

# yfinance 沒有正式的速率限制文件，但短時間內大量請求會被擋。序列處理配上小
# 延遲最穩；真的要加速應該改用它的批次 download，而不是拉高併發。
FETCH_DELAY_SECONDS = 0.3


async def _start_job_run() -> int:
    async with async_session_factory() as session:
        run = JobRun(job_name=JOB_NAME, status="running")
        session.add(run)
        await session.commit()
        return run.id


async def _finish_job_run(run_id: int, status: str, message: str) -> None:
    async with async_session_factory() as session:
        await session.execute(
            update(JobRun)
            .where(JobRun.id == run_id)
            .values(
                status=status,
                message=message[:2000],
                finished_at=datetime.now(UTC),
            )
        )
        await session.commit()


async def sync_stock_universe() -> int:
    listings = await TwseProvider().fetch_listings()
    async with async_session_factory() as session:
        count = await StocksRepository(session).upsert_stocks(listings)
    print(f"[batch] stocks upserted: {count}")
    return count


async def sync_prices_and_indicators(
    symbols: list[str] | None, limit: int | None, period: str
) -> tuple[int, int]:
    async with async_session_factory() as session:
        universe = await StocksRepository(session).list_symbols()

    if symbols:
        wanted = set(symbols)
        universe = [(s, m) for s, m in universe if s in wanted]
    if limit:
        universe = universe[:limit]

    print(f"[batch] fetching prices for {len(universe)} symbols (period={period})")

    provider = YFinanceProvider()
    total_bars = total_indicators = 0

    for index, (symbol, market) in enumerate(universe, start=1):
        try:
            bars = await provider.fetch_history(symbol, market, period=period)
        except Exception as exc:  # noqa: BLE001 — 單檔失敗不該中斷整批
            print(f"[batch] {symbol} price fetch failed: {exc!r}")
            continue

        if not bars:
            continue

        indicators = compute_indicators(symbol, bars)

        async with async_session_factory() as session:
            total_bars += await StocksRepository(session).upsert_daily_prices(bars)
            if indicators:
                total_indicators += await TechnicalRepository(
                    session
                ).upsert_indicators(indicators)

        if index % 50 == 0:
            print(f"[batch] progress {index}/{len(universe)}")
        await asyncio.sleep(FETCH_DELAY_SECONDS)

    print(f"[batch] daily_prices upserted: {total_bars}")
    print(f"[batch] technical_indicators upserted: {total_indicators}")
    return total_bars, total_indicators


async def run(symbols: list[str] | None, limit: int | None, period: str) -> None:
    run_id = await _start_job_run()
    try:
        stocks = await sync_stock_universe()
        bars, indicators = await sync_prices_and_indicators(symbols, limit, period)
        await _finish_job_run(
            run_id,
            "success",
            f"stocks={stocks} bars={bars} indicators={indicators}",
        )
        print("[batch] done")
    except Exception:
        await _finish_job_run(run_id, "failed", traceback.format_exc())
        raise
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="TwInsight 盤後批次")
    parser.add_argument("--symbols", help="逗號分隔的股票代號，預設為全部")
    parser.add_argument("--limit", type=int, help="只處理前 N 檔（開發用）")
    parser.add_argument("--period", default="1y", help="yfinance 期間，預設 1y")
    args = parser.parse_args()

    symbols = (
        [s.strip() for s in args.symbols.split(",") if s.strip()]
        if args.symbols
        else None
    )
    asyncio.run(run(symbols, args.limit, args.period))


if __name__ == "__main__":
    main()
