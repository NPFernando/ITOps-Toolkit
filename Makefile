.PHONY: help setup install install-dev run test compile audit-ui dependency-check contract-tests qa release-gates release-evidence pre-merge pre-release clean

PYTHON ?= python3
VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip
STREAMLIT := $(VENV)/bin/streamlit
PORT ?= 8502
RELEASE_GATES_TESTS := \
	tests/test_streamlit_pages.py \
	tests/test_health_diagnostics_page.py \
	tests/test_cache_policy.py \
	tests/test_adapters.py \
	tests/test_github_issues.py \
	tests/test_ai_tools.py \
	tests/test_ui_audit_inventory.py \
	tests/test_maintenance_consistency.py

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

audit-ui: ## Generate the static UI/UX page inventory
	$(PYTHON) scripts/ui_audit_inventory.py

dependency-check: ## Check installed dependency consistency and Python lint rules
	$(VENV_PYTHON) -m pip check
	$(VENV_PYTHON) -m ruff check app.py pages utils tests

contract-tests: ## Run adapter, UI, and external-provider contract tests
	$(VENV_PYTHON) -m pytest -q tests/test_reliability.py tests/test_catalog_quality.py tests/test_adapters.py tests/test_webhook_tools.py tests/test_robots_validator.py tests/test_cve_tools.py tests/test_github_issues.py tests/test_ui_helpers.py tests/test_app_page.py

test: ## Run pytest
	$(VENV_PYTHON) -m pytest

qa: compile test ## Run local quality checks

release-gates: compile ## Run fast pre-merge reliability/release checks
	$(VENV_PYTHON) -m pytest $(RELEASE_GATES_TESTS)

release-evidence: audit-ui release-gates dependency-check contract-tests ## Generate inventory, release gates, and dependency evidence
	@printf '%s\n' "Release evidence inputs refreshed: docs/ui-ux-audit-inventory.json"

pre-merge: release-gates ## Alias: run pre-merge confidence gates

pre-release: qa ## Alias: run full pre-release quality checks

clean: ## Remove local Python caches and pytest cache
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -exec rm -rf {} +
