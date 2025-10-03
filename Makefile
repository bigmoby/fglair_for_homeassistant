# Makefile for FGLair Home Assistant Integration

.PHONY: help setup test lint format clean install-dev

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	@echo "🚀 Setting up development environment..."
	@./scripts/setup

test: ## Run tests
	@echo "🧪 Running tests..."
	@bash -c "source venv/bin/activate && python -m pytest tests/ -v"

test-coverage: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	@bash -c "source venv/bin/activate && python -m pytest tests/ --cov=custom_components/fglair_heatpump_controller --cov-report=html --cov-report=term"

lint: ## Run linting tools
	@echo "🔍 Running linting..."
	@bash -c "source venv/bin/activate && pre-commit run --all-files"

format: ## Format code
	@echo "✨ Formatting code..."
	@bash -c "source venv/bin/activate && ruff format ."
	@bash -c "source venv/bin/activate && ruff check --fix ."

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/

install-dev: ## Install in development mode
	@echo "📦 Installing in development mode..."
	@bash -c "source venv/bin/activate && pip install -e ."

install: ## Install the package
	@echo "📦 Installing package..."
	@bash -c "source venv/bin/activate && pip install ."

develop: ## Start development server
	@echo "🔧 Starting development server..."
	@./scripts/develop

check: lint test ## Run all checks (lint + test)

ci: setup check ## Run CI pipeline locally
