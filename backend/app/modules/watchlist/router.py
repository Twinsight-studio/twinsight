"""使用者自選股清單 — API routes.

TODO: no business logic here yet. Wire actual endpoints once product spec
for the watchlist module is ready.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/watchlist", tags=["watchlist"])

# TODO: define watchlist endpoints (router.get / router.post ...).
