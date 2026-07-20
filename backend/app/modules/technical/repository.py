"""技術指標計算（MA/RSI/MACD 等） — repository layer (persistence).

TODO: implement. Repositories own SQLAlchemy queries for this module's
tables; nothing outside this file should issue raw queries against them.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class TechnicalRepository:
    """TODO: implement technical persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
