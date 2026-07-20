"""Stocks module — repository layer (persistence).

TODO: implement. Owns SQLAlchemy queries against stock metadata tables.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class StocksRepository:
    """TODO: implement stock metadata persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
