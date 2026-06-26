# =========================
# CONFIG
# =========================

# pyinstaller \
    --onefile \
    --windowed \
    --add-data "pacmen_and_gums:pacmen_and_gums" \
    --add-data "ghosts:ghosts" \
    --add-data "HS.json:." \
    --add-data "config.json:." \
    --add-data "mazegenerator:mazegenerator" srcs/game.py --exclude-module pkg_resources

SHELL := /bin/bash

UV := uv
PY := $(UV) run python
export PYGAME_HIDE_SUPPORT_PROMPT=1

# Force uv to ALWAYS use .venv
# 	@if [ -d "/sgoinfre" ]; then \
# 		export UV_PROJECT_ENVIRONMENT=.venv; \
# 		export UV_CACHE_DIR=/sgoinfre/$(USER)/.cache/uv; \
# 		export XDG_CACHE_HOME=/sgoinfre/$(USER)/.cache; \
# 		export TMPDIR=/sgoinfre/$(USER)/tmp; \
# 	fi

# =========================
# INSTALL
# =========================

install:
	@echo "Syncing environment with uv..."
	@uv sync
	@UV_SKIP_WHEEL_FILENAME_CHECK=1 uv pip install mazegenerator-00001-py3-none-any.whl


# =========================
# RUN
# =========================

run: install
	@echo "Running..."
	@$(PY) srcs/game.py


# =========================
# LINT
# =========================

lint:
	@echo "Running flake8 + mypy..."
	@$(UV) run flake8 srcs
	@$(UV) run mypy srcs --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


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
