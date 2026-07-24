#!/bin/sh
# API 容器啟動時先把 schema 帶到最新，再起服務 —— 讓 `docker compose up`
# 開箱即用，不必記得手動 `make migrate`。
#
# ponytail: 單一 API 進程的本地部署這樣最省事。若哪天 API 擴成多副本，改成
# 獨立的一次性 migrate 服務，避免多副本同時 upgrade 互搶。
set -e

echo "[entrypoint] running database migrations..."
alembic upgrade head

echo "[entrypoint] starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
