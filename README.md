# TwInsight

台股觀察與選股工具。GitHub public monorepo：`frontend/`（Next.js，部署到 Cloudflare
Workers）+ `backend/`（FastAPI modular monolith，部署到 GCP Cloud Run）。

> 目前是架構骨架階段：路由/service/repository 都是空殼 + TODO，選股演算法、技術指標、
> 認證邏輯尚未實作。

## 技術棧

- **前端**：Next.js (App Router) + TypeScript + Tailwind CSS + shadcn/ui + Zustand +
  TanStack Query + ECharts，透過 OpenNext 部署到 Cloudflare Workers（Free plan）。
- **後端**：FastAPI + SQLAlchemy 2.x (async, Psycopg 3) + Pydantic v2 + Alembic，
  Modular Monolith（8 模組：auth/stocks/chips/technical/screener/watchlist/alerts/jobs），
  部署到 GCP Cloud Run。
- **資料庫**：Supabase Postgres，透過 Supavisor pooler 連線（runtime 走 transaction-mode
  6543，migration 走 session-mode 5432 — 細節見 `backend/app/core/db.py`）。
- **快取**：Upstash Redis（快照/rate-limit/lock，不存歷史行情）。
- **批次**：Cloud Scheduler → Cloud Run Job，盤後跑選股/指標批次 + Supabase keep-alive。

## 本地開發

需要：Docker、Node 22+、[uv](https://docs.astral.sh/uv/)。

```bash
# 後端 + Postgres + Redis（一個指令）
make dev

# 另開一個終端機跑前端
make dev-frontend
```

前端：http://localhost:3000　後端：http://localhost:8080/health

複製 `backend/.env.example` → `backend/.env`、`frontend/.env.example` →
`frontend/.env.local`，依需要調整。

### 個別跑測試

```bash
make test              # 前端 + 後端全部
make test-frontend     # npm ci + lint + typecheck + test + build
make test-backend      # uv sync + ruff + pytest
```

### Alembic migration

```bash
cd backend
uv run alembic revision -m "描述"   # 產生新的 migration
uv run alembic upgrade head          # 套用（本地連 docker-compose 的 Postgres）
```

## 目錄結構

```
frontend/           Next.js app
backend/
  app/
    core/            設定、DB engine、Redis client
    modules/          8 個模組，各自 router.py / service.py / repository.py
    jobs/             批次腳本入口（run_batch.py、keep_alive.py）
  alembic/           migration
  Dockerfile.api      twinsight-api image（無 pandas/numpy，降低冷啟動）
  Dockerfile.job      twinsight-job image（含 pandas/numpy/pandas-ta/yfinance）
.github/workflows/    CI（PR）+ CD（merge to main）
docs/infra/           雲端資源建置 runbook
```

## 部署

merge 到 `main` 會自動觸發：
- `deploy-frontend.yml`（`frontend/**` 有改動時）→ OpenNext build → `wrangler deploy`
- `deploy-backend.yml`（`backend/**` 有改動時）→ build+push 兩個 image → Alembic
  migration → 更新 Cloud Run Service + Job

部署需要的雲端資源（GCP/Supabase/Upstash/Cloudflare/Fugle）與對應的 GitHub secrets，
照 [`docs/infra/gcp-setup.md`](docs/infra/gcp-setup.md) 設一次。
# ci verify
