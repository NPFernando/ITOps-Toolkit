.PHONY: help setup install install-dev run test compile qa clean

PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit
PORT ?= 8502

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*##"; printf "Available commands:\n"} /^[a-zA-Z_-]+:.*##/ {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: $(VENV)/bin/activate install-dev ## Create virtual environment and install development dependencies

$(VENV)/bin/activate:
	@if command -v uv >/dev/null 2>&1; then \
		uv venv $(VENV) --python $(PYTHON); \
	else \
		$(PYTHON) -m venv $(VENV); \
	fi

install: $(VENV)/bin/activate ## Install runtime dependencies
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install --python $(VENV_PYTHON) -r requirements.txt; \
	else \
		$(VENV_PYTHON) -m pip install --upgrade pip && \
		$(VENV_PIP) install -r requirements.txt; \
	fi

install-dev: $(VENV)/bin/activate ## Install development and test dependencies
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install --python $(VENV_PYTHON) -r requirements-dev.txt; \
	else \
		$(VENV_PYTHON) -m pip install --upgrade pip && \
		$(VENV_PIP) install -r requirements-dev.txt; \
	fi

run: ## Run Streamlit locally
	$(STREAMLIT) run app.py --server.headless true --server.port $(PORT)

compile: ## Compile Python files
	$(VENV_PYTHON) -m compileall app.py pages utils

test: ## Run pytest
	$(VENV_PYTHON) -m pytest

qa: compile test ## Run local quality checks

clean: ## Remove local Python caches and pytest cache
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -exec rm -rf {} +
