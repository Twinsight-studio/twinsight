"""批次 job 執行紀錄查詢/手動觸發 — repository layer (persistence).

實際批次腳本在 app/jobs/run_batch.py。

TODO: implement. Repositories own SQLAlchemy queries for this module's
tables; nothing outside this file should issue raw queries against them.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class JobsRepository:
    """TODO: implement jobs persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
