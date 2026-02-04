SHELL := /bin/bash

.PHONY: help setup setup-conda run-api run-web format clean

help:
	@echo "Common tasks:"
	@echo "  make setup         # Install Python deps via pip"
	@echo "  make setup-conda   # Create conda env from environment.yml"
	@echo "  make run-api       # Start FastAPI server on :8000"
	@echo "  make run-web       # Start Vite dev server for frontend"
	@echo "  make clean         # Remove caches and build artifacts"

setup:
	pip install -r requirements.txt

setup-conda:
	conda env create -f environment.yml || conda env update -f environment.yml --prune
	@echo "Activate with: conda activate opennet-slot"

run-api:
	PYTHONPATH=src uvicorn api.server:app --reload --port 8000

run-web:
	cd web && npm install && npm run dev

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov coverage coverage.xml \
		build dist *.egg-info web/node_modules web/dist web/.vite web/coverage
