# 雲端資源建置 Runbook

這台開發機沒有裝 `gcloud`/`wrangler`/`supabase` CLI，也沒有任何雲端帳號憑證，所以下列
步驟需要 CEO 自己在有帳號的機器上執行一次。完成後把對應的值塞進 GitHub repo secrets
（`Settings → Secrets and variables → Actions`），CI/CD 就能接手。

## 0. 裝 CLI（只需做一次，在你要操作雲端資源的機器上）

```bash
brew install --cask google-cloud-sdk
brew install cloudflare-wrangler2   # 或 npm i -g wrangler
brew install supabase/tap/supabase
```

## 1. GCP 專案 + API

```bash
gcloud auth login
gcloud projects create twinsight-prod --name="TwInsight"
gcloud config set project twinsight-prod

gcloud services enable \
  run.googleapis.com \
  cloudscheduler.googleapis.com \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com

gcloud artifacts repositories create twinsight \
  --repository-format=docker \
  --location=asia-northeast1
```

Artifact Registry host/repo path（給 GitHub secrets 用）:
`asia-northeast1-docker.pkg.dev/twinsight-prod/twinsight`

## 2. Workload Identity Federation（給 GitHub Actions 用，不要用 Service Account JSON）

```bash
PROJECT_ID=twinsight-prod
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
REPO="<github-org>/twinsight"   # 換成實際 repo

gcloud iam service-accounts create github-actions-deployer \
  --display-name="GitHub Actions deployer"

gcloud iam workload-identity-pools create github-pool \
  --location=global \
  --display-name="GitHub Actions pool"

gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --display-name="GitHub OIDC" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository=='${REPO}'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

gcloud iam service-accounts add-iam-policy-binding \
  "github-actions-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/attribute.repository/${REPO}"

# Grant the deploy roles the workflow needs
for role in roles/run.admin roles/artifactregistry.writer roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:github-actions-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="$role"
done
```

`GCP_WORKLOAD_IDENTITY_PROVIDER` secret 的值:
`projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-pool/providers/github-provider`

`GCP_SERVICE_ACCOUNT` secret 的值:
`github-actions-deployer@twinsight-prod.iam.gserviceaccount.com`

## 3. Cloud Scheduler（盤後批次 + keep-alive，兩個獨立排程）

```bash
gcloud run jobs create twinsight-job \
  --image=asia-northeast1-docker.pkg.dev/twinsight-prod/twinsight/twinsight-job:latest \
  --region=asia-northeast1

gcloud scheduler jobs create http twinsight-post-market \
  --location=asia-northeast1 \
  --schedule="35 14 * * 1-5" \
  --time-zone="Asia/Taipei" \
  --uri="https://asia-northeast1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/twinsight-job:run" \
  --http-method=POST \
  --oauth-service-account-email="github-actions-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
  # command override: ["python", "-m", "app.jobs.run_batch"]

gcloud scheduler jobs create http twinsight-keep-alive \
  --location=asia-northeast1 \
  --schedule="0 3 */3 * *" \
  --time-zone="Asia/Taipei" \
  --uri="https://asia-northeast1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/twinsight-job:run" \
  --http-method=POST \
  --oauth-service-account-email="github-actions-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
  # command override: ["python", "-m", "app.jobs.keep_alive"]
```

Cloud Run Service 設定（`deploy-backend.yml` 已經照這組跑）:
Region `asia-northeast1`、1 vCPU、512 MiB、`min-instances 0`、`max-instances 1`、
`concurrency 20-40`、request-based billing（預設，不要開 CPU always-on）。

## 4. Supabase 專案

1. https://supabase.com/dashboard → New project → 選 region 離 `asia-northeast1`近的（如 Northeast Asia (Tokyo) 若有；否則選 Southeast Asia）。
2. `Project Settings → Database → Connection string`：
   - **Transaction mode**（port 6543）→ `DATABASE_URL` secret。
   - **Session mode**（port 5432）→ `DATABASE_MIGRATION_URL` secret。
   - 兩者都用 Psycopg 3 async/sync 驅動（`postgresql+psycopg://...`），不要用 asyncpg。
3. 記下密碼，這台機器沒有直接連線能力，之後由 CI 使用。

## 5. Upstash Redis

1. https://console.upstash.com/ → Create database → Region 選 GCP `asia-northeast1`（跟 Cloud Run 同區，降低延遲）。
2. 拿 `REDIS_URL`（含密碼的 rediss:// 連線字串）→ `REDIS_URL` secret。

## 6. Cloudflare（前端 Workers 部署）

```bash
wrangler login
# 記下 Account ID: `wrangler whoami`
```

1. https://dash.cloudflare.com/profile/api-tokens → Create Token → 用 "Edit Cloudflare Workers" 樣板 → `CLOUDFLARE_API_TOKEN` secret。
2. Account ID → `CLOUDFLARE_ACCOUNT_ID` secret。

## 7. Fugle API Key

https://developer.fugle.tw/ 申請 → `FUGLE_API_KEY` secret（後端專用，`deploy-backend.yml` 會塞進 Cloud Run 環境變數，前端永遠拿不到）。

## GitHub repo secrets 清單

| Secret | 用途 |
|---|---|
| `CLOUDFLARE_API_TOKEN` | deploy-frontend.yml → wrangler deploy |
| `CLOUDFLARE_ACCOUNT_ID` | deploy-frontend.yml → wrangler deploy |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | deploy-backend.yml → google-github-actions/auth |
| `GCP_SERVICE_ACCOUNT` | deploy-backend.yml → google-github-actions/auth |
| `GCP_PROJECT_ID` | deploy-backend.yml → gcloud run deploy/jobs |
| `ARTIFACT_REGISTRY` | deploy-backend.yml，例如 `asia-northeast1-docker.pkg.dev/twinsight-prod/twinsight` |
| `ARTIFACT_REGISTRY_HOST` | deploy-backend.yml，例如 `asia-northeast1-docker.pkg.dev`（給 `gcloud auth configure-docker`）|
| `DATABASE_URL` | Cloud Run runtime，Supavisor 6543；也用在 backend-ci.yml 的手動 Supabase smoke test |
| `DATABASE_MIGRATION_URL` | deploy-backend.yml 跑 Alembic，Supavisor 5432 |
| `REDIS_URL` | Cloud Run runtime，Upstash |
| `FUGLE_API_KEY` | Cloud Run runtime，後端專用 |
| `JWT_SECRET` | Cloud Run runtime |

全部設定完、且 `twinsight-job` image 至少手動 `gcloud run jobs create` 過一次後，
merge 到 `main` 就會自動部署前後端。
