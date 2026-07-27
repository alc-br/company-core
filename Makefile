.PHONY: help install dev test lint format migrate shell server celery worker beat

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync --all-extras --group=dev

dev: ## Start development server (Django + Vite)
	uv run python manage.py runserver

server: ## Start Django server
	uw run python manage.py runserver 0.0.0.0:8000

celery: ## Start Celery worker + beat
	uv run celery -A company_core worker -l INFO --beat --pool=solo

worker: ## Start Celery worker only
	uv run celery -A company_core worker -l INFO --queues=default,billing,ai,webhooks,workflows,analytics,notifications

beat: ## Start Celery beat scheduler
	uv run celery -A company_core beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

migrate: ## Apply database migrations
	uv run python manage.py migrate

makemigrations: ## Create new migrations
	uv run python manage.py makemigrations

shell: ## Open Django shell
	uv run python manage.py shell

dbshell: ## Open database shell
	uv run python manage.py dbshell

test: ## Run tests with coverage
	uv run pytest --cov=apps --cov-report=term-missing --cov-report=html:htmlcov -v

test-fast: ## Run tests without coverage
	uv run pytest -v --tb=short

test-unit: ## Run only unit tests
	uv run pytest -v -m unit

test-integration: ## Run only integration tests
	uv run pytest -v -m integration

lint: ## Run linter
	uv run ruff check apps/ company_core/

format: ## Format code
	uv run ruff format apps/ company_core/

typecheck: ## Run type checker
	uv run mypy apps/

check: lint typecheck test ## Run all checks (lint + typecheck + test)

createsuperuser: ## Create a superuser
	uv run python manage.py createsuperuser

collectstatic: ## Collect static files
	uv run python manage.py collectstatic --noinput

bootstrap-celery: ## Bootstrap Celery beat schedule
	uv run python manage.py bootstrap_celery_tasks

docker-up: ## Start Docker services
	docker compose up -d

docker-down: ## Stop Docker services
	docker compose down

docker-build: ## Build Docker images
	docker compose build

docker-logs: ## View Docker logs
	docker compose logs -f

docker-clean: ## Remove Docker volumes and containers
	docker compose down -v --rmi local
