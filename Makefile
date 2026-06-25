# =========================
# CONFIG
# =========================

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
	@$(PY) game.py


# =========================
# LINT
# =========================

lint:
	@echo "Running flake8 + mypy..."
	@$(UV) run flake8 ghosts.py pacman.py movement.py player.py game.py gums.py ui.py
	@$(UV) run mypy ghosts.py pacman.py movement.py player.py game.py gums.py ui.py --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


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
