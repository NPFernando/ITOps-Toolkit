from __future__ import annotations

import os
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from utils import roadmap


# Newer streamlit resolves AppTest.from_file()'s relative paths against the
# file that calls it (this test file's directory), not the working
# directory -- an absolute path avoids that resolution entirely.
ROADMAP_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "10_Roadmap_Feedback.py")
ROADMAP_PAGE_TIMEOUT = 60


@pytest.fixture(autouse=True)
def _clear_roadmap_cache(monkeypatch):
    """Clear st.cache_data before each test in this file.

    The roadmap page now scopes its board-cache key with PYTEST_CURRENT_TEST
    for test isolation, but this file still clears process-global
    st.cache_data between tests to keep each scenario explicit and avoid
    accidental coupling from unrelated cached calls.
    """
    st.cache_data.clear()
    monkeypatch.setenv("ITOPS_CACHE_SCOPE", os.getenv("PYTEST_CURRENT_TEST", "runtime"))


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "info", "error", "caption"):
        collection = getattr(app, collection_name, [])
        for item in collection:
            parts.append(str(getattr(item, "body", getattr(item, "value", ""))))
    return "\n".join(parts)


def test_roadmap_feedback_page_renders_hybrid_board_and_links(monkeypatch):
    def fake_board(repo_url=None):
        return roadmap.RoadmapBoard(
            (
                roadmap.RoadmapItem(
                    title="Seed export idea",
                    category="Reports",
                    status="Planned",
                    votes=5,
                    description="A seeded report idea.",
                    rationale="Curated by maintainers.",
                    source="seed",
                ),
                roadmap.RoadmapItem(
                    title="GitHub request",
                    category="Tools",
                    status="In Progress",
                    votes=2,
                    description="A public GitHub issue.",
                    rationale="Requested by a user.",
                    source="github",
                    url="https://github.com/NPFernando/ITOps-Toolkit/issues/42",
                    number=42,
                ),
                roadmap.RoadmapItem(
                    title="AI checklist idea",
                    category="AI Ideas",
                    status="AI Recommended",
                    votes=9,
                    description="A curated AI idea.",
                    rationale="Static recommendation.",
                    source="seed",
                ),
            )
        )

    monkeypatch.setattr(roadmap, "load_roadmap_board", fake_board)

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=ROADMAP_PAGE_TIMEOUT)
    app.run()

    assert not app.exception
    text = _page_text(app)

    assert "Roadmap & Feedback" in text
    assert "Submit idea" in text
    assert "Public-safe feedback only" in text
    assert "AI Recommended is curated" in text
    assert "static, curated tag, not AI output" in text
    assert "Streamlit does not store feedback" in text
    assert "Outcome: roadmap cache checked" in text
    assert "Outcome: roadmap sync complete" in text
    assert "Cached for up to 5 minutes." in text
    assert "Tools" in text
    assert "Reports" in text
    assert "Complete" in text
    assert "Planned" in text
    assert "In Progress" in text
    assert "AI Recommended" in text
    assert "GitHub #42" in text
    assert "https://github.com/NPFernando/ITOps-Toolkit/issues/new" in text
    markdown_html = "\n".join(m.value for m in app.markdown)
    assert 'class="roadmap-notice' in markdown_html
    assert 'role="note"' in markdown_html
    assert 'aria-hidden="true"' in markdown_html


def test_roadmap_feedback_page_ai_triage_unavailable_without_config(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(roadmap, "load_roadmap_board", lambda repo_url=None: roadmap.RoadmapBoard(roadmap.ROADMAP_ITEMS))

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=ROADMAP_PAGE_TIMEOUT)
    app.run()

    assert not app.exception
    text = _page_text(app)
    assert "AI-assisted triage" in text
    assert "AI triage unavailable" in text
    assert "Outcome: roadmap cache checked" in text
    assert "Outcome: AI triage unavailable" in text
    assert not any(b.label.startswith("Summarize") for b in app.button)


def test_roadmap_feedback_page_ai_triage_runs_when_configured_and_clicked(monkeypatch):
    from utils import ai_tools

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")
    monkeypatch.setattr(
        roadmap,
        "load_roadmap_board",
        lambda repo_url=None: roadmap.RoadmapBoard(
            (
                roadmap.RoadmapItem(
                    title="Command palette",
                    category="UX / Design",
                    status="Planned",
                    votes=18,
                    description="Ctrl+K launcher",
                    rationale="Power users expect it",
                    source="seed",
                ),
            )
        ),
    )

    def fake_summarize(items, client_factory=None):
        return {"enabled": True, "provider": "azure_openai", "status": "success", "summary": "Prioritize the command palette."}

    monkeypatch.setattr(ai_tools, "summarize_feature_requests_with_azure", fake_summarize)

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=ROADMAP_PAGE_TIMEOUT)
    app.run()
    assert not app.exception

    triage_button = next(b for b in app.button if b.label.startswith("Summarize"))
    triage_button.click().run()
    assert not app.exception

    text = _page_text(app)
    assert "Outcome: AI triage cache checked" in text
    assert "Outcome: AI triage generated" in text
    assert "Cached for up to 1 hour." in text
    assert "AI triage summary" in text
    assert "Prioritize the command palette." in text


def test_roadmap_feedback_page_ai_triage_click_reuses_cache(monkeypatch):
    from utils import ai_tools

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")
    monkeypatch.setattr(
        roadmap,
        "load_roadmap_board",
        lambda repo_url=None: roadmap.RoadmapBoard(
            (
                roadmap.RoadmapItem(
                    title="Cached triage item",
                    category="Tools",
                    status="Planned",
                    votes=7,
                    description="Cache this",
                    rationale="Keep behavior",
                    source="seed",
                ),
            )
        ),
    )
    calls = {"count": 0}

    def fake_summarize(items, client_factory=None):
        calls["count"] += 1
        return {"enabled": True, "provider": "azure_openai", "status": "success", "summary": "Cached summary."}

    monkeypatch.setattr(ai_tools, "summarize_feature_requests_with_azure", fake_summarize)

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=ROADMAP_PAGE_TIMEOUT)
    app.run()
    assert not app.exception

    button = next(b for b in app.button if b.label.startswith("Summarize"))
    button.click().run()
    button = next(b for b in app.button if b.label.startswith("Summarize"))
    button.click().run()

    assert not app.exception
    assert calls["count"] == 1
    assert "Outcome: AI triage cache checked" in _page_text(app)
    assert "Cached summary." in _page_text(app)


def test_roadmap_feedback_page_renders_github_fallback_note(monkeypatch):
    def fake_board(repo_url=None):
        return roadmap.RoadmapBoard(
            roadmap.ROADMAP_ITEMS,
            "GitHub API rate limit reached. Showing seed roadmap data.",
        )

    monkeypatch.setattr(roadmap, "load_roadmap_board", fake_board)

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=ROADMAP_PAGE_TIMEOUT)
    app.run()

    assert not app.exception
    text = _page_text(app)
    assert "GitHub roadmap sync temporarily unavailable" in text
    assert "The upstream service is rate-limiting requests." in text
    assert "Refresh later to retry GitHub issue sync." in text
    assert "GitHub API rate limit reached" not in text


def test_roadmap_feedback_page_ai_triage_error_uses_sanitized_failure_copy(monkeypatch):
    from utils import ai_tools

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")
    monkeypatch.setattr(
        roadmap,
        "load_roadmap_board",
        lambda repo_url=None: roadmap.RoadmapBoard(
            (
                roadmap.RoadmapItem(
                    title="Command palette",
                    category="UX / Design",
                    status="Planned",
                    votes=18,
                    description="Ctrl+K launcher",
                    rationale="Power users expect it",
                    source="seed",
                ),
            )
        ),
    )

    monkeypatch.setattr(
        ai_tools,
        "summarize_feature_requests_with_azure",
        lambda items, client_factory=None: {
            "enabled": False,
            "status": "error",
            "message": "Connection failed token=super-secret to https://internal.example.local",
        },
    )

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=ROADMAP_PAGE_TIMEOUT)
    app.run()
    assert not app.exception

    triage_button = next(b for b in app.button if b.label.startswith("Summarize"))
    triage_button.click().run()
    assert not app.exception

    text = _page_text(app)
    assert "AI triage temporarily unavailable" in text
    assert "Next step: Check Azure OpenAI configuration and retry when the service is available." in text
    assert "super-secret" not in text
    assert "internal.example.local" not in text
