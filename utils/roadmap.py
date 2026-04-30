"""Hybrid roadmap and feedback board data."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Iterable

from utils import github_issues
from utils.project_links import github_feature_request_url, github_repository_url


ROADMAP_CATEGORIES = ("Tools", "Reports", "Security", "AI Ideas", "UX / Design", "Integrations")
ROADMAP_STATUSES = ("Planned", "In Progress", "Complete", "AI Recommended")
ROADMAP_SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "roadmap_seed.json"
DEFAULT_CATEGORY = "Tools"


@dataclass(frozen=True)
class RoadmapItem:
    title: str
    category: str
    status: str
    votes: int
    description: str
    rationale: str
    source: str = "seed"
    url: str = ""
    updated_at: str = ""
    number: int | None = None


@dataclass(frozen=True)
class RoadmapBoard:
    items: tuple[RoadmapItem, ...]
    github_error: str | None = None


def load_seed_items(path: Path | str = ROADMAP_SEED_PATH) -> tuple[RoadmapItem, ...]:
    """Load curated roadmap seed items from a tracked JSON file."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(raw_items, list):
        raise ValueError("Roadmap seed file must contain an items list.")
    return tuple(_seed_item_from_dict(item) for item in raw_items)


def load_roadmap_board(repo_url: str | None = None, fetch_github: bool = True) -> RoadmapBoard:
    """Return merged seed items and public GitHub issue requests."""
    seed_items = load_seed_items()
    if not fetch_github:
        return RoadmapBoard(seed_items)

    result = github_issues.fetch_public_issues(repo_url or github_repository_url())
    issue_items = tuple(
        item
        for item in (github_issue_to_roadmap_item(issue) for issue in result.issues)
        if item is not None
    )
    return RoadmapBoard(seed_items + issue_items, result.error)


def github_issue_to_roadmap_item(issue: dict[str, Any]) -> RoadmapItem | None:
    """Normalize one GitHub issue payload into a roadmap item."""
    if "pull_request" in issue:
        return None

    body = str(issue.get("body") or "")
    labels = _label_names(issue)
    title = _clean_issue_title(str(issue.get("title") or "Untitled GitHub request"))
    category = _category_from_issue(body, labels)
    status = _status_from_issue(issue, labels)
    description = _issue_form_field(body, "What should be added or improved?") or _body_excerpt(body)
    rationale = _issue_form_field(body, "Who benefits and why?") or "Opened from a public GitHub feature request."
    reactions = issue.get("reactions") if isinstance(issue.get("reactions"), dict) else {}

    return RoadmapItem(
        title=title,
        category=category,
        status=status,
        votes=_safe_int(reactions.get("total_count")),
        description=description,
        rationale=rationale,
        source="github",
        url=str(issue.get("html_url") or ""),
        updated_at=str(issue.get("updated_at") or issue.get("created_at") or ""),
        number=_safe_optional_int(issue.get("number")),
    )


def category_counts(items: Iterable[RoadmapItem] | None = None) -> dict[str, int]:
    """Return roadmap category counts derived from the given item list."""
    counts: dict[str, int] = {category: 0 for category in ROADMAP_CATEGORIES}
    for item in tuple(items) if items is not None else ROADMAP_ITEMS:
        counts[item.category] = counts.get(item.category, 0) + 1
    return counts


def roadmap_categories() -> tuple[str, ...]:
    return ROADMAP_CATEGORIES


def filter_roadmap_items(
    query: str = "",
    category: str = "All",
    items: Iterable[RoadmapItem] | None = None,
) -> tuple[RoadmapItem, ...]:
    """Filter roadmap items by search query and category."""
    source_items = tuple(items) if items is not None else ROADMAP_ITEMS
    normalized_query = (query or "").strip().lower()
    normalized_category = (category or "All").strip()

    def matches(item: RoadmapItem) -> bool:
        if normalized_category != "All" and item.category != normalized_category:
            return False
        if not normalized_query:
            return True
        searchable = " ".join(
            [
                item.title,
                item.category,
                item.status,
                item.description,
                item.rationale,
                item.source,
                item.url,
                item.updated_at,
                str(item.number or ""),
                f"#{item.number}" if item.number else "",
            ]
        ).lower()
        return normalized_query in searchable

    return tuple(item for item in source_items if matches(item))


def roadmap_items_by_status(items: Iterable[RoadmapItem]) -> dict[str, tuple[RoadmapItem, ...]]:
    item_tuple = tuple(items)
    return {
        status: tuple(item for item in item_tuple if item.status == status)
        for status in ROADMAP_STATUSES
    }


def _seed_item_from_dict(item: Any) -> RoadmapItem:
    required_fields = {"title", "category", "status", "votes", "description", "rationale"}
    if not isinstance(item, dict) or not required_fields.issubset(item):
        raise ValueError("Roadmap seed item is missing required fields.")
    return RoadmapItem(
        title=str(item["title"]),
        category=_known_category(str(item["category"])),
        status=_known_status(str(item["status"])),
        votes=_safe_int(item["votes"]),
        description=str(item["description"]),
        rationale=str(item["rationale"]),
        source="seed",
        url=str(item.get("url") or ""),
        updated_at=str(item.get("updated_at") or ""),
        number=_safe_optional_int(item.get("number")),
    )


def _status_from_issue(issue: dict[str, Any], labels: tuple[str, ...]) -> str:
    if str(issue.get("state") or "").lower() == "closed":
        return "Complete"
    normalized_labels = {_normalize_label(label) for label in labels}
    if normalized_labels & {"status:complete", "status:done", "complete", "done"}:
        return "Complete"
    if normalized_labels & {"status:in-progress", "status:in progress", "in-progress", "in progress"}:
        return "In Progress"
    return "Planned"


def _category_from_issue(body: str, labels: tuple[str, ...]) -> str:
    body_category = _issue_form_field(body, "Category")
    if body_category:
        return _known_category(body_category)

    for label in labels:
        normalized = _normalize_label(label)
        if normalized.startswith("category:"):
            return _known_category(normalized.removeprefix("category:"))
        for category in ROADMAP_CATEGORIES:
            if normalized == category.lower():
                return category
    return DEFAULT_CATEGORY


def _issue_form_field(body: str, label: str) -> str:
    match = re.search(
        rf"###\s+{re.escape(label)}\s*\n+(.*?)(?=\n###\s+|\Z)",
        body,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return ""
    lines = [line.strip() for line in match.group(1).splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _body_excerpt(body: str) -> str:
    cleaned = " ".join(line.strip() for line in body.splitlines() if line.strip())
    return cleaned[:220] if cleaned else "Public GitHub feature request."


def _label_names(issue: dict[str, Any]) -> tuple[str, ...]:
    labels = issue.get("labels")
    if not isinstance(labels, list):
        return ()
    names: list[str] = []
    for label in labels:
        if isinstance(label, dict) and label.get("name"):
            names.append(str(label["name"]))
        elif isinstance(label, str):
            names.append(label)
    return tuple(names)


def _clean_issue_title(title: str) -> str:
    return re.sub(r"^\s*\[Idea\]:\s*", "", title, flags=re.IGNORECASE).strip() or "Untitled GitHub request"


def _known_category(value: str) -> str:
    normalized = _normalize_label(value)
    for category in ROADMAP_CATEGORIES:
        if normalized == category.lower():
            return category
    return DEFAULT_CATEGORY


def _known_status(value: str) -> str:
    normalized = _normalize_label(value)
    for status in ROADMAP_STATUSES:
        if normalized == status.lower():
            return status
    if normalized == "implemented":
        return "Complete"
    return "Planned"


def _normalize_label(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _safe_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _safe_optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


ROADMAP_ITEMS = load_seed_items()


__all__ = [
    "ROADMAP_CATEGORIES",
    "ROADMAP_ITEMS",
    "ROADMAP_STATUSES",
    "RoadmapBoard",
    "RoadmapItem",
    "category_counts",
    "filter_roadmap_items",
    "github_feature_request_url",
    "github_issue_to_roadmap_item",
    "github_repository_url",
    "load_roadmap_board",
    "load_seed_items",
    "roadmap_categories",
    "roadmap_items_by_status",
]
