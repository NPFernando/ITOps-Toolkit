"""Project links used by the public app shell and feedback flow."""

from __future__ import annotations

import os
from urllib.parse import urlparse
from urllib.parse import urlencode


DEFAULT_GITHUB_URL = "https://github.com/NPFernando/ITOps-Toolkit"


def github_repository_url() -> str:
    """Return the configured public repository URL."""
    return (os.getenv("ITOPS_GITHUB_URL", "").strip() or DEFAULT_GITHUB_URL).rstrip("/")


def github_repository_slug(repo_url: str | None = None) -> tuple[str, str] | None:
    """Return the GitHub owner/repo pair for a public repository URL."""
    parsed = urlparse((repo_url or github_repository_url()).rstrip("/"))
    if parsed.netloc.lower() != "github.com":
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        return None
    return parts[0], parts[1].removesuffix(".git")


def github_feature_request_url() -> str:
    """Return the GitHub issue form URL for public feature ideas."""
    query = urlencode(
        {
            "template": "feature_request.yml",
            "labels": "enhancement",
            "title": "[Idea]: ",
        }
    )
    return f"{github_repository_url()}/issues/new?{query}"
