"""價格/條件警示規則與觸發 — repository layer (persistence).

TODO: implement. Repositories own SQLAlchemy queries for this module's
tables; nothing outside this file should issue raw queries against them.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class AlertsRepository:
    """TODO: implement alerts persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
