"""Read-only GitHub Issues adapter for public roadmap feedback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

from utils.project_links import github_repository_slug, github_repository_url


@dataclass(frozen=True)
class GitHubIssuesResult:
    issues: tuple[dict[str, Any], ...]
    error: str | None = None


def fetch_public_issues(
    repo_url: str | None = None,
    *,
    per_page: int = 100,
    timeout: int = 8,
) -> GitHubIssuesResult:
    """Fetch public GitHub issues anonymously and ignore pull requests."""
    repository_url = repo_url or github_repository_url()
    slug = github_repository_slug(repository_url)
    if slug is None:
        return GitHubIssuesResult((), "GitHub repository URL is invalid. Showing seed roadmap data.")

    owner, repo = slug
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    try:
        response = requests.get(
            api_url,
            params={"state": "all", "per_page": per_page},
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "ITOpsToolkit/1.0 public-roadmap",
            },
            timeout=timeout,
        )
    except requests.RequestException:
        return GitHubIssuesResult((), "GitHub issues are unavailable. Showing seed roadmap data.")

    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        return GitHubIssuesResult((), "GitHub API rate limit reached. Showing seed roadmap data.")
    if response.status_code >= 400:
        return GitHubIssuesResult((), "GitHub issues are unavailable. Showing seed roadmap data.")

    try:
        payload = response.json()
    except ValueError:
        return GitHubIssuesResult((), "GitHub issue response was invalid. Showing seed roadmap data.")

    if not isinstance(payload, list):
        return GitHubIssuesResult((), "GitHub issue response was invalid. Showing seed roadmap data.")

    issues = tuple(item for item in payload if isinstance(item, dict) and "pull_request" not in item)
    return GitHubIssuesResult(issues)


__all__ = ["GitHubIssuesResult", "fetch_public_issues"]
