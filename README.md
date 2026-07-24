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
# 首次：複製環境檔範本（.env 未進版控）
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
# 在 backend/.env 填入 FUGLE_API_KEY（即時報價需要；其餘功能不填也能跑）

# 全部（Postgres + Redis + 後端 API + 前端），一個指令
make dev
```

前端：http://localhost:3000　後端：http://localhost:8080/health

**資料表會在 API 容器啟動時自動建立**（entrypoint 跑 `alembic upgrade head`），
所以 `make dev` 一下去 schema 就到位，不必手動 migrate。但**資料庫是空的** ——
要有股票/K線/籌碼資料，得先跑一次盤後批次（見下方），否則需要讀 DB 的頁面會沒資料。

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

### 盤後批次（抓資料 → 算指標 → 寫 DB）

```bash
docker compose run --rm job                      # 全市場（~1975 檔，很久）
docker compose run --rm job --limit 20           # 只跑前 20 檔，開發用
docker compose run --rm job --symbols 2330,2317  # 指定股票
docker compose run --rm job --period 5y          # yfinance 期間，預設 1y
```

`job` 掛在 `batch` profile 下，所以 `make dev` 不會啟動它 —— 它是一次性任務，
不是常駐服務。每次執行都會寫一筆 `job_runs`，成功或失敗都查得到：

```sql
SELECT job_name, status, message, started_at FROM job_runs ORDER BY id DESC LIMIT 5;
```

規格書要求收盤後 14:35 自動跑；本地部署沒有 Cloud Scheduler，用 `crontab` 或
macOS `launchd` 掛上面的指令即可（機器當下要開著）。

### Alembic migration

套用是自動的（API 容器啟動時跑 `alembic upgrade head`）。新增 migration 或
手動操作時：

```bash
cd backend
uv run alembic revision --autogenerate -m "描述"   # 依 models 差異產生
uv run alembic upgrade head                          # 手動套用（連 docker-compose 的 Postgres）
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
