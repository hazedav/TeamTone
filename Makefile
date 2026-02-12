# TeamTone Makefile

# Project directory
TEAMTONE_DIR := teamtone

# Helper to run commands in the teamtone directory
define run_in_teamtone
	cd $(TEAMTONE_DIR) && $(1)
endef

.PHONY: help install lint format test test-integration coverage-report run scrape clean

help:
	@echo "TeamTone - Available Commands:"
	@echo ""
	@echo "  make install          Install dependencies and tools"
	@echo "  make lint             Run code linting with ruff"
	@echo "  make format           Auto-format code with ruff"
	@echo "  make test             Run unit tests with coverage"
	@echo "  make test-integration Run integration tests (live scraper tests)"
	@echo "  make coverage-report  Generate HTML coverage report"
	@echo "  make run              Run the interactive TeamTone CLI"
	@echo "  make scrape           Scrape filament data from 3dfilamentprofiles.com"
	@echo "  make clean            Remove Python cache files"
	@echo ""

install:
	@echo "Installing dependencies..."
	$(call run_in_teamtone,uv sync)
	@echo "Installation complete!"

lint:
	@echo "Running ruff linter..."
	$(call run_in_teamtone,uv run ruff format --check .)
	$(call run_in_teamtone,uv run ruff check .)

format:
	@echo "Formatting code with ruff..."
	$(call run_in_teamtone,uv run ruff format .)
	$(call run_in_teamtone,uv run ruff check --fix .)

test:
	@echo "Running unit tests with coverage..."
	cd $(TEAMTONE_DIR) && uv run pytest ../$(TEAMTONE_DIR) --cov=$(TEAMTONE_DIR) --cov-report=term-missing -v

test-integration:
	@echo "Running integration tests with coverage..."
	cd $(TEAMTONE_DIR) && uv run pytest ../$(TEAMTONE_DIR) --cov=$(TEAMTONE_DIR) --cov-report=term-missing -v -m integration

coverage-report:
	@echo "Generating HTML coverage report..."
	cd $(TEAMTONE_DIR) && uv run pytest ../$(TEAMTONE_DIR) --cov=$(TEAMTONE_DIR) --cov-report=html
	@echo "Coverage report generated at $(TEAMTONE_DIR)/htmlcov/index.html"

run:
	@echo "Starting TeamTone CLI..."
	python run_teamtone.py

scrape:
	@echo "Scraping filament data..."
	python -m teamtone.fetch.scrape_filaments

clean:
	@echo "Cleaning Python cache files..."
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse" 2>nul || echo ""
	@powershell -Command "Get-ChildItem -Path . -Include *.pyc,*.pyo -Recurse -Force | Remove-Item -Force" 2>nul || echo ""
else
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
endif
	@echo "Clean complete!"
