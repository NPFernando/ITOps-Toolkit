from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

from utils import github_issues, roadmap


def _issue(
    *,
    state: str = "open",
    labels: list[str] | None = None,
    body: str = "",
    number: int = 12,
    reactions: int = 4,
) -> dict:
    return {
        "title": "[Idea]: Better report exports",
        "state": state,
        "labels": [{"name": label} for label in (labels or ["enhancement"])],
        "body": body,
        "number": number,
        "html_url": f"https://github.com/NPFernando/ITOps-Toolkit/issues/{number}",
        "updated_at": "2026-04-30T12:00:00Z",
        "reactions": {"total_count": reactions},
    }


def test_seed_file_loads_and_has_required_fields():
    items = roadmap.load_seed_items()
    counts = roadmap.category_counts(items)

    assert items
    assert tuple(counts) == roadmap.ROADMAP_CATEGORIES
    assert all(value >= 0 for value in counts.values())
    assert sum(counts.values()) == len(items)
    assert all(item.source == "seed" for item in items)


def test_seed_file_validation_rejects_missing_required_fields(tmp_path):
    seed_path = tmp_path / "roadmap_seed.json"
    seed_path.write_text(json.dumps({"items": [{"title": "Incomplete"}]}), encoding="utf-8")

    try:
        roadmap.load_seed_items(seed_path)
    except ValueError as exc:
        assert "required fields" in str(exc)
    else:
        raise AssertionError("Expected seed validation to fail")


def test_filter_roadmap_items_matches_seed_and_github_fields():
    github_item = roadmap.RoadmapItem(
        title="Customer-safe report export",
        category="Reports",
        status="Planned",
        votes=3,
        description="Export public-safe notes.",
        rationale="Requested from GitHub.",
        source="github",
        url="https://github.com/NPFernando/ITOps-Toolkit/issues/7",
        number=7,
    )
    items = roadmap.ROADMAP_ITEMS + (github_item,)

    assert any(item.title == "Downloadable HTML reports" for item in roadmap.filter_roadmap_items("html", items=items))
    assert all(item.category == "Reports" for item in roadmap.filter_roadmap_items(category="Reports", items=items))
    assert any(item.number == 7 for item in roadmap.filter_roadmap_items("#7", items=items))
    assert roadmap.filter_roadmap_items("definitely-not-a-roadmap-match", items=items) == ()


def test_roadmap_items_by_status_uses_public_column_order():
    grouped = roadmap.roadmap_items_by_status(roadmap.ROADMAP_ITEMS)

    assert tuple(grouped) == roadmap.ROADMAP_STATUSES
    assert all(item.status == status for status, items in grouped.items() for item in items)


def test_github_issue_normalization_maps_statuses_and_form_fields():
    body = """### What should be added or improved?

Add a richer report export.

### Category

Reports

### Who benefits and why?

MSP engineers can send clearer customer summaries.
"""
    item = roadmap.github_issue_to_roadmap_item(
        _issue(labels=["enhancement", "status:in-progress"], body=body)
    )

    assert item is not None
    assert item.title == "Better report exports"
    assert item.category == "Reports"
    assert item.status == "In Progress"
    assert item.votes == 4
    assert item.source == "github"
    assert item.number == 12
    assert item.description == "Add a richer report export."
    assert "MSP engineers" in item.rationale


def test_github_issue_normalization_maps_closed_and_complete_labels():
    closed_item = roadmap.github_issue_to_roadmap_item(_issue(state="closed"))
    complete_item = roadmap.github_issue_to_roadmap_item(_issue(labels=["complete"]))

    assert closed_item is not None
    assert complete_item is not None
    assert closed_item.status == "Complete"
    assert complete_item.status == "Complete"


def test_github_issue_normalization_ignores_pull_requests():
    issue = _issue()
    issue["pull_request"] = {"url": "https://api.github.com/pulls/1"}

    assert roadmap.github_issue_to_roadmap_item(issue) is None


def test_load_roadmap_board_returns_seed_only_on_github_error(monkeypatch):
    def fake_fetch(*args, **kwargs):
        return github_issues.GitHubIssuesResult((), "GitHub API rate limit reached. Showing seed roadmap data.")

    monkeypatch.setattr(github_issues, "fetch_public_issues", fake_fetch)

    board = roadmap.load_roadmap_board()

    assert board.github_error == "GitHub API rate limit reached. Showing seed roadmap data."
    assert board.items == roadmap.ROADMAP_ITEMS


def test_load_roadmap_board_merges_github_issues(monkeypatch):
    def fake_fetch(*args, **kwargs):
        return github_issues.GitHubIssuesResult((_issue(labels=["enhancement"], number=22),))

    monkeypatch.setattr(github_issues, "fetch_public_issues", fake_fetch)

    board = roadmap.load_roadmap_board()

    assert len(board.items) == len(roadmap.ROADMAP_ITEMS) + 1
    assert any(item.source == "github" and item.number == 22 for item in board.items)


def test_github_feedback_url_uses_default_repository(monkeypatch):
    monkeypatch.delenv("ITOPS_GITHUB_URL", raising=False)

    feedback_url = roadmap.github_feature_request_url()
    parsed = urlparse(feedback_url)
    query = parse_qs(parsed.query)

    assert feedback_url.startswith("https://github.com/NPFernando/ITOps-Toolkit/issues/new?")
    assert query["template"] == ["feature_request.yml"]
    assert query["labels"] == ["enhancement"]
    assert query["title"] == ["[Idea]: "]


def test_github_feedback_url_respects_repository_override(monkeypatch):
    monkeypatch.setenv("ITOPS_GITHUB_URL", "https://github.com/example/fork/")

    assert roadmap.github_repository_url() == "https://github.com/example/fork"
    assert roadmap.github_feature_request_url().startswith("https://github.com/example/fork/issues/new?")
