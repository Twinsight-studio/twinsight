# TwInsight v1 — 架構骨架建置計畫

CEO 已完全定案架構（見本檔底部附錄）。本次任務只做架構骨架 + CI/CD + 環境設定，**不寫業務邏輯程式碼**。

## 範圍

會動的檔案：
- `frontend/` — Next.js (App Router+TS+Tailwind+shadcn/ui) 最小骨架，能過 lint/typecheck/build/OpenNext build
- `backend/` — FastAPI Modular Monolith 骨架（8 模組空殼）、SQLAlchemy 2.x async engine（psycopg3+NullPool+Supavisor 6543）、Alembic（sync psycopg3+Supavisor 5432）、pyproject 用 uv 分兩組依賴（API vs Job）
- `backend/Dockerfile.api`、`backend/Dockerfile.job` — 兩個獨立 image
- `docker-compose.yml` — 本地開發（Postgres+Redis+API）
- `.github/workflows/{frontend-ci,backend-ci,deploy-frontend,deploy-backend}.yml` — path filter、對應 CEO 規格的步驟
- `.env.example`、`README.md`、`docs/infra/gcp-setup.md`（GCP WIF / Cloud Run / Cloud Scheduler 手動設置步驟，因本機無 gcloud 且無憑證，無法代為建立）

禁區：不寫選股/技術指標/認證等業務邏輯，只留 router/service/repository 空殼 + 型別簽名。

## 順序

1. Infra subagent 產出全部骨架檔案（一次到位，本機驗證 lint/build/uv sync 過）
2. COO 獨立驗收：read-back 關鍵檔、實跑 npm run build / uv sync / docker build
3. git commit → `gh repo create Twinsight-studio/twinsight --public --push`
4. 設定 main branch protection（PR + CI 必過才能 merge）
5. 回報 CEO：已完成項目 vs. 需要 CEO 自行提供的雲端帳號/憑證清單

## 驗收條件

- `cd frontend && npm run build` 成功
- `cd backend && uv sync && uv run ruff check . && uv run pytest` 成功
- `docker build -f backend/Dockerfile.api .` 與 `docker build -f backend/Dockerfile.job .` 成功
- 4 個 workflow YAML 語法正確（actionlint 或 `yq` 驗證）、path filter 正確覆蓋 frontend/backend
- repo 在 Twinsight-studio org 下建立成功、main 分支已保護

## 已知無法代辦（需 CEO 提供）

GCP 專案/WIF、Supabase 專案、Upstash Redis、Cloudflare 帳號+API Token、Fugle/FinMind API Key — 本機未裝 gcloud/wrangler/supabase CLI 且無這些服務憑證，只能寫好 workflow 與文件，實際 provisioning 需 CEO 動作。
