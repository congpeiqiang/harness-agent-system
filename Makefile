# ============================================================
# Makefile - Build Automation for Harness Agent System
# ============================================================

.PHONY: help install install-dev format lint type-check test test-cov check clean docker-build docker-up docker-down dev

# Default target
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ----------------------------------------------------------
# Installation
# ----------------------------------------------------------

install: ## Install production dependencies
	uv sync --frozen

install-dev: ## Install all dependencies including dev
	uv sync --all-extras

# ----------------------------------------------------------
# Code Quality
# ----------------------------------------------------------

format: ## Format code with ruff
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

lint: ## Lint code with ruff
	uv run ruff check src/ tests/

type-check: ## Run mypy type checking
	uv run mypy src/app

# ----------------------------------------------------------
# Testing
# ----------------------------------------------------------

test: ## Run tests
	uv run pytest tests/ -v

test-unit: ## Run unit tests only
	uv run pytest tests/unit/ -v -m unit

test-integration: ## Run integration tests only
	uv run pytest tests/integration/ -v -m integration

test-cov: ## Run tests with coverage report
	uv run pytest tests/ \
		--cov=src/app \
		--cov-report=html \
		--cov-report=term-missing \
		-v

# ----------------------------------------------------------
# Combined Checks
# ----------------------------------------------------------

check: format lint type-check test ## Run all checks (format, lint, type-check, test)

# ----------------------------------------------------------
# Development
# ----------------------------------------------------------

dev: ## Start development server with auto-reload
	uvicorn app.main:app --reload --host 0.0.0.0 --port 2026

# ----------------------------------------------------------
# Docker
# ----------------------------------------------------------

docker-build: ## Build Docker image
	docker build -f docker/Dockerfile -t harness-agent-system:latest .

docker-up: ## Start services with docker-compose
	docker-compose -f docker/docker-compose.yml up -d

docker-down: ## Stop services with docker-compose
	docker-compose -f docker/docker-compose.yml down

docker-logs: ## View docker-compose logs
	docker-compose -f docker/docker-compose.yml logs -f

docker-prod-up: ## Start production services
	docker-compose -f docker/docker-compose.prod.yml up -d

docker-prod-down: ## Stop production services
	docker-compose -f docker/docker-compose.prod.yml down

# ----------------------------------------------------------
# Cleaning
# ----------------------------------------------------------

clean: ## Clean build artifacts and caches
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf htmlcov/ coverage.xml .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# ----------------------------------------------------------
# Pre-commit
# ----------------------------------------------------------

pre-commit-install: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files
