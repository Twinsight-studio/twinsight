"""TwInsight backend — FastAPI entrypoint (twinsight-api image).

Modular monolith: each module in app/modules/* owns its router/service/
repository; this file only wires modules together.
"""

import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
# routes exist) — restrict to the frontend's origin once it's fixed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
)

# Public API, no auth layer (side project, no membership system) — this is
# the only thing standing between it and unlimited hammering.
# ponytail: in-process fixed-window counter, NOT Redis — a single API
# process serves all traffic, so local memory is exactly as correct as
# shared state and needs no round-trip. Move to Redis if the API is ever
# scaled to more than one process/replica.
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60

_rate_windows: dict[str, tuple[int, float]] = {}  # ip -> (count, window_start)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    forwarded_for = request.headers.get("x-forwarded-for", "")
    client_ip = forwarded_for.split(",")[0].strip() or (
        request.client.host if request.client else "unknown"
    )

    now = time.monotonic()
    count, window_start = _rate_windows.get(client_ip, (0, now))
    if now - window_start >= RATE_LIMIT_WINDOW_SECONDS:
        count, window_start = 0, now
    count += 1
    _rate_windows[client_ip] = (count, window_start)

    # ponytail: prune expired windows only when the dict gets big, keeps
    # memory bounded without a background task.
    if len(_rate_windows) > 10_000:
        cutoff = now - RATE_LIMIT_WINDOW_SECONDS
        for ip in [k for k, v in _rate_windows.items() if v[1] < cutoff]:
            del _rate_windows[ip]

    if count > RATE_LIMIT_REQUESTS:
        return JSONResponse({"detail": "Too Many Requests"}, status_code=429)

    return await call_next(request)


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
