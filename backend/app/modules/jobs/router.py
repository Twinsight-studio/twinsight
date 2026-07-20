"""批次 job 執行紀錄查詢/手動觸發（實際批次腳本在 app/jobs/run_batch.py） — API routes.

TODO: no business logic here yet. Wire actual endpoints once product spec
for the jobs module is ready.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

# TODO: define jobs endpoints (router.get / router.post ...).
