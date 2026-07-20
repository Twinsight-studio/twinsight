"""使用者註冊/登入/JWT 簽發 — API routes.

TODO: no business logic here yet. Wire actual endpoints once product spec
for the auth module is ready.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# TODO: define auth endpoints (router.get / router.post ...).
