"""價格/條件警示規則與觸發 — API routes.

TODO: no business logic here yet. Wire actual endpoints once product spec
for the alerts module is ready.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

# TODO: define alerts endpoints (router.get / router.post ...).
