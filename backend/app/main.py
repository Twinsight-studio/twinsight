"""TwInsight backend — FastAPI entrypoint (twinsight-api image).

Modular monolith: each module in app/modules/* owns its router/service/
repository; this file only wires modules together.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.alerts.router import router as alerts_router
from app.modules.auth.router import router as auth_router
from app.modules.chips.router import router as chips_router
from app.modules.jobs.router import router as jobs_router
from app.modules.screener.router import router as screener_router
from app.modules.stocks.router import router as stocks_router
from app.modules.technical.router import router as technical_router
from app.modules.watchlist.router import router as watchlist_router

app = FastAPI(title="TwInsight API")

# ponytail: allow all origins for now (only read-only /health and stub
# routes exist) — restrict to the real Cloudflare Workers origin once the
# frontend has a stable domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
)

for module_router in (
    auth_router,
    stocks_router,
    chips_router,
    technical_router,
    screener_router,
    watchlist_router,
    alerts_router,
    jobs_router,
):
    app.include_router(module_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
