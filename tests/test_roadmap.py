from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from utils import roadmap


def test_category_counts_are_stable_and_non_negative():
    counts = roadmap.category_counts()

    assert tuple(counts) == roadmap.ROADMAP_CATEGORIES
    assert all(value >= 0 for value in counts.values())
    assert sum(counts.values()) == len(roadmap.ROADMAP_ITEMS)


def test_filter_roadmap_items_matches_title_category_status_and_description():
    assert any(item.title == "Downloadable HTML reports" for item in roadmap.filter_roadmap_items("html"))
    assert all(item.category == "Security" for item in roadmap.filter_roadmap_items(category="Security"))
    assert all(item.status == "AI Recommended" for item in roadmap.filter_roadmap_items("AI Recommended"))
    assert any("persistence-free" in item.rationale for item in roadmap.filter_roadmap_items("persistence-free"))
    assert roadmap.filter_roadmap_items("definitely-not-a-roadmap-match") == ()


def test_roadmap_items_by_status_uses_public_column_order():
    grouped = roadmap.roadmap_items_by_status(roadmap.ROADMAP_ITEMS)

    assert tuple(grouped) == roadmap.ROADMAP_STATUSES
    assert all(item.status == status for status, items in grouped.items() for item in items)


def test_github_feedback_url_uses_default_repository(monkeypatch):
    monkeypatch.delenv("ITOPS_GITHUB_URL", raising=False)

    feedback_url = roadmap.github_feature_request_url()
    parsed = urlparse(feedback_url)
    query = parse_qs(parsed.query)

    assert feedback_url.startswith("https://github.com/NPFernando/ITOps-Toolkit/issues/new?")
    assert query["template"] == ["feature_request.yml"]
    assert query["labels"] == ["idea,feedback"]
    assert query["title"] == ["[Idea]: "]


def test_github_feedback_url_respects_repository_override(monkeypatch):
    monkeypatch.setenv("ITOPS_GITHUB_URL", "https://github.com/example/fork/")

    assert roadmap.github_repository_url() == "https://github.com/example/fork"
    assert roadmap.github_feature_request_url().startswith("https://github.com/example/fork/issues/new?")
