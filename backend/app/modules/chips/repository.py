"""籌碼面資料（三大法人買賣超、融資融券） — repository layer (persistence).

TODO: implement. Repositories own SQLAlchemy queries for this module's
tables; nothing outside this file should issue raw queries against them.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class ChipsRepository:
    """TODO: implement chips persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
