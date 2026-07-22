.PHONY: dev dev-frontend down test test-frontend test-backend lint migrate

dev: ## Start the full stack (Postgres + Redis + API + frontend)
	docker compose up --build

dev-frontend: ## Frontend dev server on the host, for hot reload (see README)
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

migrate: ## Run Alembic migrations against DATABASE_URL
	cd backend && uv run alembic upgrade head
