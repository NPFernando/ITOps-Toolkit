"""Project links used by the public app shell and feedback flow."""

from __future__ import annotations

import os
from urllib.parse import urlencode


DEFAULT_GITHUB_URL = "https://github.com/NPFernando/ITOps-Toolkit"


def github_repository_url() -> str:
    """Return the configured public repository URL."""
    return (os.getenv("ITOPS_GITHUB_URL", "").strip() or DEFAULT_GITHUB_URL).rstrip("/")


def github_feature_request_url() -> str:
    """Return the GitHub issue form URL for public feature ideas."""
    query = urlencode(
        {
            "template": "feature_request.yml",
            "labels": "idea,feedback",
            "title": "[Idea]: ",
        }
    )
    return f"{github_repository_url()}/issues/new?{query}"
