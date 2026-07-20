"""Stress-tests NullPool + Psycopg3 async against a transaction-mode pooler.

Proves the runtime DB config (see app/core/db.py: NullPool,
prepare_threshold=None, no pool_pre_ping) survives concurrent load without
"prepared statement already exists" / session-state errors — the class of
bug that shows up specifically with transaction-mode connection pooling
(Supavisor/PgBouncer). Run against a local PgBouncer in CI; not fancy on
purpose, just enough concurrency to catch that class of bug.

Usage: uv run python scripts/pooler_stress_test.py --dsn <postgresql+psycopg://...>
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

CONCURRENT_TASKS = 300
BURST_ROUNDS = 3


async def select_task(engine, task_id: int) -> None:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT :v AS v"), {"v": task_id})
        assert result.scalar_one() == task_id


async def transaction_task(engine, task_id: int) -> None:
    should_rollback = task_id % 2 == 0
    async with engine.begin() as conn:
        await conn.execute(text("CREATE TEMP TABLE IF NOT EXISTS t (n int)"))
        await conn.execute(text("INSERT INTO t (n) VALUES (:v)"), {"v": task_id})
        if should_rollback:
            raise _Rollback


class _Rollback(Exception):
    pass


async def run_burst(engine, round_no: int) -> None:
    tasks = []
    for i in range(CONCURRENT_TASKS):
        if i % 2 == 0:
            tasks.append(select_task(engine, round_no * CONCURRENT_TASKS + i))
        else:
            coro = transaction_task(engine, round_no * CONCURRENT_TASKS + i)

            async def _wrapped(c=coro):
                try:
                    await c
                except _Rollback:
                    pass  # deliberate rollback path, not a failure

            tasks.append(_wrapped())

    random.shuffle(tasks)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    errors = [r for r in results if isinstance(r, Exception) and not isinstance(r, _Rollback)]
    if errors:
        print(f"Round {round_no}: {len(errors)} errors, first: {errors[0]!r}")
        raise SystemExit(1)
    print(f"Round {round_no}: {len(tasks)} tasks OK")


async def main(dsn: str) -> None:
    engine = create_async_engine(
        dsn,
        poolclass=NullPool,
        connect_args={"prepare_threshold": None},
    )
    try:
        for round_no in range(BURST_ROUNDS):
            await run_burst(engine, round_no)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsn", required=True)
    args = parser.parse_args()
    try:
        asyncio.run(main(args.dsn))
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"Pooler stress test failed: {exc!r}")
        sys.exit(1)
    print("Pooler stress test passed.")
