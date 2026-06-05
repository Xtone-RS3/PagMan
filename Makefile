# =========================
# CONFIG
# =========================

SHELL := /bin/bash

UV := uv
PY := $(UV) run python

# Force uv to ALWAYS use .venv
export UV_PROJECT_ENVIRONMENT := .venv
export UV_CACHE_DIR=/sgoinfre/gasoares/.cache/uv
export XDG_CACHE_HOME=/sgoinfre/gasoares/.cache
export TMPDIR=/sgoinfre/gasoares/tmp

# =========================
# INSTALL
# =========================

install:
	@echo "Syncing environment with uv..."
	@uv sync


# =========================
# RUN
# =========================

run:
	install
	@echo "Running..."
# 	@$(PY) -m $(MODULE) index --max_chunk_size 2000


# =========================
# LINT
# =========================

lint:
	@echo "Running flake8 + mypy..."
	@$(UV) run flake8 src
	@$(UV) run mypy src --ignore-missing-imports


# =========================
# CLEAN
# =========================

clean:
	@echo "Cleaning cache..."
	@rm -rf __pycache__ .mypy_cache .pytest_cache
	@find . -name "*.pyc" -delete


fclean: clean
	@echo "Full clean (env not touched)"
	@rm -rf data/output/search_results


# =========================
# HELP
# =========================

help:
	@echo "Available targets:"
	@echo "  make install"
	@echo "  make run"
	@echo "  make lint"
	@echo "  make clean"
