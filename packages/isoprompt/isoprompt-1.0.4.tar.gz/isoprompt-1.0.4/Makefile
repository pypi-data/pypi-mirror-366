# IsoPrompt - Makefile for build automation

# Colors
BLUE=\033[0;34m
YELLOW=\033[1;33m
RED=\033[0;31m
GREEN=\033[0;32m
RESET=\033[0m

.PHONY: help install install-dev clean format lint test validate build publish version

help:
	@echo "$(BLUE)IsoPrompt - Available Make Targets$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}'

install: ## Install package in development mode
	@echo "$(YELLOW)Installing isoprompt in development mode...$(RESET)"
	python -m pip install -e .

install-dev: ## Install package with development dependencies
	@echo "$(YELLOW)Installing isoprompt with development dependencies...$(RESET)"
	python -m pip install -e ".[dev]"

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

format: ## Format code using black and isort
	python -m black isoprompt/
	python -m isort isoprompt/

lint: ## Run linters (flake8, mypy)
	python -m flake8 isoprompt/ --max-line-length=88 --extend-ignore=E203,W503,E501,D100,D200,D202,D205,W293,W291
	python -m mypy isoprompt/ --ignore-missing-imports

test: ## Run tests with pytest
	python -m pytest tests/ -v --cov=isoprompt --cov-report=term-missing

validate: clean format lint ## Run all validation steps

build: clean ## Build package distributions
	python -m build

all: clean format lint validate build publish

publish: ## Publish package to PyPI
	@echo "$(YELLOW)Building distributions...$(RESET)"
	python -m build
	@echo "$(YELLOW)Publishing to PyPI...$(RESET)"
	python -m twine upload dist/*

version: ## Show package version
	@if [ -f "isoprompt/__init__.py" ]; then \
		echo "Package version: $$(grep '__version__' isoprompt/__init__.py | cut -d'"' -f2)"; \
	else \
		echo "$(RED)Error: isoprompt/__init__.py not found.$(RESET)"; \
		exit 1; \
	fi 