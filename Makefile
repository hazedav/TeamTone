# TeamTone Makefile

.PHONY: help lint format test run scrape clean

help:
	@echo "TeamTone - Available Commands:"
	@echo ""
	@echo "  make lint        Run code linting with ruff"
	@echo "  make format      Auto-format code with ruff"
	@echo "  make test        Run test suite with pytest"
	@echo "  make run         Run the interactive TeamTone CLI"
	@echo "  make scrape      Scrape filament data from 3dfilamentprofiles.com"
	@echo "  make clean       Remove Python cache files"
	@echo ""

lint:
	@echo "Running ruff linter..."
	uv run ruff check teamtone/

format:
	@echo "Formatting code with ruff..."
	uv run ruff format teamtone/
	uv run ruff check --fix teamtone/

test:
	@echo "Running test suite with pytest..."
	uv run pytest teamtone/fetch/test_scrape_filaments.py -v

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
