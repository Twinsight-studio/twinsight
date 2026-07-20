.PHONY: dev dev-frontend down test test-frontend test-backend lint migrate

dev: ## Start Postgres + Redis + backend API (docker compose)
	docker compose up --build

dev-frontend: ## Run frontend dev server (separate terminal from `make dev`)
	cd frontend && npm run dev

down:
	docker compose down

test: test-frontend test-backend

test-frontend:
	cd frontend && npm ci && npm run lint && npm run typecheck && npm run test && npm run build

test-backend:
	cd backend && uv sync && uv run ruff check . && uv run pytest

lint:
	cd frontend && npm run lint
	cd backend && uv run ruff check .

migrate: ## Run Alembic migrations against DATABASE_MIGRATION_URL
	cd backend && uv run alembic upgrade head
