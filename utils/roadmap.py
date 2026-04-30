"""Static roadmap and feedback board data."""

from __future__ import annotations

from dataclasses import dataclass

from utils.project_links import github_feature_request_url, github_repository_url


ROADMAP_CATEGORIES = ("Tools", "Reports", "Security", "AI Ideas", "UX / Design", "Integrations")
ROADMAP_STATUSES = ("Implemented", "Planned", "In Progress", "AI Recommended")


@dataclass(frozen=True)
class RoadmapItem:
    title: str
    category: str
    status: str
    votes: int
    description: str
    rationale: str


ROADMAP_ITEMS: tuple[RoadmapItem, ...] = (
    RoadmapItem(
        title="Domain Health Checker",
        category="Tools",
        status="Implemented",
        votes=92,
        description="DNS, TLS, HTTP, email security, recommendations, and exports.",
        rationale="Core troubleshooting workflow for IT admins and MSP engineers.",
    ),
    RoadmapItem(
        title="DNS Record Checker",
        category="Tools",
        status="Implemented",
        votes=74,
        description="A, AAAA, MX, TXT, NS, CNAME, SOA, SPF, and DMARC lookups.",
        rationale="Fast public DNS inspection without storing queried domains.",
    ),
    RoadmapItem(
        title="SSL Certificate Checker",
        category="Security",
        status="Implemented",
        votes=68,
        description="Certificate subject, issuer, SANs, dates, and expiration status.",
        rationale="Helps catch certificate incidents before renewal windows are missed.",
    ),
    RoadmapItem(
        title="HTTP Status Checker",
        category="Tools",
        status="Implemented",
        votes=63,
        description="Status, redirects, response timing, headers, and security hints.",
        rationale="Useful first-pass check for public websites and APIs.",
    ),
    RoadmapItem(
        title="JSON Formatter, Base64, JWT, and Cron tools",
        category="Tools",
        status="Implemented",
        votes=58,
        description="Everyday text utilities for public-safe troubleshooting.",
        rationale="Keeps common admin tasks in one fast toolkit.",
    ),
    RoadmapItem(
        title="Azure AI log summaries",
        category="AI Ideas",
        status="Implemented",
        votes=51,
        description="Optional Azure AI summary for sanitized log troubleshooting submissions.",
        rationale="Adds contextual help while preserving opt-in, sanitized-only behavior.",
    ),
    RoadmapItem(
        title="Roadmap and feedback board",
        category="UX / Design",
        status="In Progress",
        votes=47,
        description="Public board for implemented work, planned work, and user ideas.",
        rationale="Makes priorities visible and gives users a clear path to suggest improvements.",
    ),
    RoadmapItem(
        title="Downloadable HTML reports",
        category="Reports",
        status="Planned",
        votes=83,
        description="Export polished standalone HTML reports from health checks.",
        rationale="MSPs can share findings with customers without extra formatting work.",
    ),
    RoadmapItem(
        title="More DNS and email security checks",
        category="Security",
        status="Planned",
        votes=79,
        description="Expand SPF, DMARC, MX, DNSSEC, MTA-STS, and TLS reporting.",
        rationale="Email security posture is a recurring operational need.",
    ),
    RoadmapItem(
        title="One-off uptime and latency trend visualization",
        category="Reports",
        status="Planned",
        votes=61,
        description="Show short-lived trend charts without storing historical checks.",
        rationale="Gives context during incident checks while keeping the app persistence-free.",
    ),
    RoadmapItem(
        title="GitHub reaction-based voting",
        category="Integrations",
        status="Planned",
        votes=44,
        description="Use GitHub issue reactions as the real vote source for feature ideas.",
        rationale="Keeps feedback public and avoids adding a custom database.",
    ),
    RoadmapItem(
        title="AI-generated remediation checklists",
        category="AI Ideas",
        status="AI Recommended",
        votes=72,
        description="Turn safe rule-based findings into short action checklists.",
        rationale="Recommended because it builds on existing findings without requiring raw secret input.",
    ),
    RoadmapItem(
        title="AI-assisted feature triage for maintainers",
        category="AI Ideas",
        status="AI Recommended",
        votes=55,
        description="Summarize GitHub feature requests for maintainers in an admin workflow.",
        rationale="Could help prioritize user ideas later, but should remain opt-in and secret-safe.",
    ),
    RoadmapItem(
        title="Tool bundle recommendations",
        category="UX / Design",
        status="AI Recommended",
        votes=49,
        description="Suggest the next tool to run based on current troubleshooting context.",
        rationale="Helps users move from DNS to SSL to HTTP checks without a heavy workflow engine.",
    ),
    RoadmapItem(
        title="ConnectWise and PSA export ideas",
        category="Integrations",
        status="AI Recommended",
        votes=37,
        description="Explore lightweight exports that can be pasted into ticketing systems.",
        rationale="MSP users often need customer-ready notes after troubleshooting.",
    ),
)


def category_counts() -> dict[str, int]:
    """Return roadmap category counts derived from the static item list."""
    counts: dict[str, int] = {category: 0 for category in ROADMAP_CATEGORIES}
    for item in ROADMAP_ITEMS:
        counts[item.category] = counts.get(item.category, 0) + 1
    return counts


def roadmap_categories() -> tuple[str, ...]:
    return tuple(category_counts().keys())


def filter_roadmap_items(query: str = "", category: str = "All") -> tuple[RoadmapItem, ...]:
    """Filter roadmap items by search query and category."""
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
            ]
        ).lower()
        return normalized_query in searchable

    return tuple(item for item in ROADMAP_ITEMS if matches(item))


def roadmap_items_by_status(items: tuple[RoadmapItem, ...]) -> dict[str, tuple[RoadmapItem, ...]]:
    return {
        status: tuple(item for item in items if item.status == status)
        for status in ROADMAP_STATUSES
    }


__all__ = [
    "ROADMAP_ITEMS",
    "ROADMAP_CATEGORIES",
    "ROADMAP_STATUSES",
    "RoadmapItem",
    "category_counts",
    "filter_roadmap_items",
    "github_feature_request_url",
    "github_repository_url",
    "roadmap_categories",
    "roadmap_items_by_status",
]
