"""使用者註冊/登入/JWT 簽發 — repository layer (persistence).

TODO: implement. Repositories own SQLAlchemy queries for this module's
tables; nothing outside this file should issue raw queries against them.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class AuthRepository:
    """TODO: implement auth persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
