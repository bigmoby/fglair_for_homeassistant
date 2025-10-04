# Makefile for FGLair Home Assistant Integration

.PHONY: help setup test test-coverage lint format clean install-dev

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Setup development environment
	@echo "🚀 Setting up development environment..."
	@./scripts/setup

test: ## Run all tests
	@echo "🧪 Running all tests..."
	@bash -c "source venv/bin/activate && python3 -m pytest tests/ -v"

test-coverage: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	@bash -c "source venv/bin/activate && python3 -m pytest tests/ -v --cov=custom_components.fglair_heatpump_controller --cov-report=term-missing"


lint-ruff: ## Run ruff linting
	@echo "🔍 Running ruff linting..."
	@bash -c "source venv/bin/activate && python3 -m ruff check custom_components/fglair_heatpump_controller/"

lint-mypy: ## Run mypy type checking
	@echo "🔍 Running mypy type checking..."
	@bash -c "source venv/bin/activate && python3 -m mypy custom_components/fglair_heatpump_controller/"

format: ## Format code
	@echo "✨ Formatting code..."
	@bash -c "source venv/bin/activate && python3 -m ruff format custom_components/fglair_heatpump_controller/"
	@bash -c "source venv/bin/activate && python3 -m ruff check --fix custom_components/fglair_heatpump_controller/"

format-ruff: ## Format code with ruff
	@echo "✨ Formatting code with ruff..."
	@bash -c "source venv/bin/activate && python3 -m ruff format custom_components/fglair_heatpump_controller/"
	@bash -c "source venv/bin/activate && python3 -m ruff check --fix custom_components/fglair_heatpump_controller/"

pre-commit-install: ## Install pre-commit hooks
	@echo "🔧 Installing pre-commit hooks..."
	@bash -c "source venv/bin/activate && pre-commit install"

pre-commit-uninstall: ## Uninstall pre-commit hooks
	@echo "🔧 Uninstalling pre-commit hooks..."
	@bash -c "source venv/bin/activate && pre-commit uninstall"

pre-commit-run: ## Run pre-commit on all files
	@echo "🔧 Running pre-commit on all files..."
	@bash -c "source venv/bin/activate && pre-commit run --all-files"

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .coverage
	@rm -rf htmlcov/

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
