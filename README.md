# TwInsight

台股觀察與選股工具。GitHub public monorepo：`frontend/`（Next.js）+ `backend/`
（FastAPI modular monolith）。

**部署方式：本地 Docker Compose**（依需求規格書 v3.0，個人自用）。GitHub 上只跑 CI，
不做自動部署 —— 詳見 [部署](#部署)。

> 目前是架構骨架階段：路由/service/repository 都是空殼 + TODO，選股演算法、技術指標、
> 認證邏輯尚未實作。

## 技術棧

- **前端**：Next.js (App Router) + TypeScript + Tailwind CSS + shadcn/ui + Zustand +
  TanStack Query + ECharts。
- **後端**：FastAPI + SQLAlchemy 2.x (async, Psycopg 3) + Pydantic v2 + Alembic，
  Modular Monolith（8 模組：auth/stocks/chips/technical/screener/watchlist/alerts/jobs）。
- **資料庫**：PostgreSQL（docker-compose 內），Alembic 管理 migration。
- **快取**：Redis（docker-compose 內）——盤中報價快照、選股結果快取。API rate limit
  走進程內記憶體（單一進程，不需共享狀態），不佔 Redis。
- **批次**：盤後選股/指標批次入口在 `backend/app/jobs/`，本地以排程或手動觸發執行。

## 本地開發

需要：Docker、Node 22+、[uv](https://docs.astral.sh/uv/)。

```bash
# 全部（Postgres + Redis + 後端 API + 前端），一個指令
make dev
```

前端：http://localhost:3000　後端：http://localhost:8080/health

複製 `backend/.env.example` → `backend/.env`、`frontend/.env.example` →
`frontend/.env.local`，依需要調整。

> **要改前端並看到熱重載？** compose 裡的前端是 production build（`next build`
> + standalone server），改了程式碼不會即時反映。開發當下請讓 `make dev` 跑著提供
> 後端，另開終端機跑 `make dev-frontend`（host 上的 `next dev`，會佔用 3000 埠，
> 所以請先 `docker compose stop frontend`）。

> **API 位址為何有兩個變數？** 瀏覽器跑在你的主機上，要走對外埠
> `http://localhost:8080`（`NEXT_PUBLIC_API_BASE_URL`，build 時烤進前端包）；
> 但前端容器內的 SSR 程式碼要走 compose 網路 `http://api:8080`
> （`API_BASE_URL`，執行時讀取）。在 host 上跑 `next dev` 時後者未設，會自動
> 退回前者。

> **本機已經在跑 Postgres / Redis？** `make dev` 預設要 5432 / 6379 / 8080 / 3000，
> 若被占用會起不來。複製根目錄 `.env.example` → `.env`，把 `POSTGRES_PORT` /
> `REDIS_PORT` / `API_PORT` / `FRONTEND_PORT`
> 改成沒被占用的埠（例如 15432 / 16379）。容器之間仍走標準內部埠，只有 host 對外
> 的埠會變。若你也改了 `POSTGRES_PORT` 並在 host 直接跑 `make migrate`，記得同步把
> `backend/.env` 的 `DATABASE_URL` host 埠改一致。

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
frontend/
  Dockerfile          production Next.js server（next build + standalone）
backend/
  app/
    core/            設定、DB engine、Redis client
    modules/          8 個模組，各自 router.py / service.py / repository.py
    jobs/             批次腳本入口（run_batch.py）
  alembic/           migration
  Dockerfile.api      API image（無 pandas/numpy，體積小）
  Dockerfile.job      批次 image（含 pandas/numpy/pandas-ta/yfinance）
.github/workflows/    CI only（PR 時跑 lint/test/build）
```

## 部署

**v1 採本地 Docker Compose 部署,GitHub 上只有 CI、沒有 CD。**

```bash
git pull
make dev          # 重新 build 並啟動（docker compose up --build）
```

CI（`frontend-ci.yml` / `backend-ci.yml`）只在 PR 時驗證 lint / typecheck / 測試 /
build / Alembic migration，通過後 merge，實際部署由你在本機執行上面的指令。

> **為什麼不做雲端 CD？** 規格書 v3.0 的定位是個人自用 + 本地 Docker Compose。本地執行
> 也是唯一能在零現金成本下支援盤中即時 WebSocket 推送的方式（自己的機器就是常駐主機）。
> 代價：機器需開著才有服務、盤後排程需機器在線、無公開網址。
> 日後若要改走雲端託管，先前的建置步驟可從 git 歷史取回
> （`git log --all -- docs/infra/gcp-setup.md`）。
