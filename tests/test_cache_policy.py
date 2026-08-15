from __future__ import annotations

from datetime import datetime, timezone

from utils.cache_policy import cache_freshness_message, compose_cache_key, runtime_cache_scope
from utils.roadmap import RoadmapItem


def test_runtime_cache_scope_defaults_to_runtime(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    assert runtime_cache_scope() == "runtime"


def test_runtime_cache_scope_uses_test_id(monkeypatch):
    monkeypatch.delenv("ITOPS_CACHE_SCOPE", raising=False)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_x.py::test_case (call)")
    assert runtime_cache_scope() == "tests/test_x.py::test_case"


def test_runtime_cache_scope_prefers_explicit_override(monkeypatch):
    monkeypatch.setenv("ITOPS_CACHE_SCOPE", "manual-scope")
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "tests/test_x.py::test_case (call)")
    assert runtime_cache_scope() == "manual-scope"


def test_compose_cache_key_is_stable_for_same_content():
    key_a = compose_cache_key("roadmap-board", repo_url="https://github.com/a/b", scope="runtime")
    key_b = compose_cache_key("roadmap-board", scope="runtime", repo_url="https://github.com/a/b")
    assert key_a == key_b


def test_compose_cache_key_changes_when_parameters_change():
    key_a = compose_cache_key("roadmap-board", repo_url="https://github.com/a/b", scope="runtime")
    key_b = compose_cache_key("roadmap-board", repo_url="https://github.com/a/c", scope="runtime")
    assert key_a != key_b


def test_compose_cache_key_handles_dataclass_payloads():
    items = (
        RoadmapItem(
            title="A",
            category="Tools",
            status="Planned",
            votes=1,
            description="d",
            rationale="r",
        ),
    )
    key_a = compose_cache_key("roadmap-ai-triage", open_items=items, scope="runtime")
    key_b = compose_cache_key("roadmap-ai-triage", open_items=items, scope="runtime")
    assert key_a == key_b


def test_cache_freshness_message_for_fresh_data():
    tone, message = cache_freshness_message(
        "Roadmap board",
        "2026-08-15T10:00:00+00:00",
        300,
        now=datetime(2026, 8, 15, 10, 4, 0, tzinfo=timezone.utc),
    )
    assert tone == "neutral"
    assert "Cached for up to 5 minutes." in message
    assert "Roadmap board last refreshed" in message


def test_cache_freshness_message_for_stale_data():
    tone, message = cache_freshness_message(
        "Roadmap board",
        "2026-08-15T10:00:00+00:00",
        300,
        now=datetime(2026, 8, 15, 10, 7, 0, tzinfo=timezone.utc),
    )
    assert tone == "warning"
    assert "Showing cached data for Roadmap board." in message
    assert "older than the 5 minutes freshness target." in message
