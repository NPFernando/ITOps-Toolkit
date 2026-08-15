"""Read-only GitHub Issues adapter for public roadmap feedback."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any

import requests

from utils.project_links import github_repository_slug, github_repository_url


DEFAULT_GITHUB_TIMEOUT_SECONDS = 8
DEFAULT_GITHUB_RETRY_ATTEMPTS = 3
GITHUB_RETRY_BACKOFF_SECONDS = 0.4
RETRYABLE_GITHUB_STATUS_CODES = {408, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class GitHubIssuesResult:
    issues: tuple[dict[str, Any], ...]
    error: str | None = None


def fetch_public_issues(
    repo_url: str | None = None,
    *,
    per_page: int = 100,
    timeout: int = DEFAULT_GITHUB_TIMEOUT_SECONDS,
) -> GitHubIssuesResult:
    """Fetch public GitHub issues anonymously and ignore pull requests."""
    repository_url = repo_url or github_repository_url()
    slug = github_repository_slug(repository_url)
    if slug is None:
        return GitHubIssuesResult((), "GitHub repository URL is invalid. Showing seed roadmap data.")

    owner, repo = slug
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    response: requests.Response | None = None
    for attempt in range(1, DEFAULT_GITHUB_RETRY_ATTEMPTS + 1):
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
            if response.status_code in RETRYABLE_GITHUB_STATUS_CODES and attempt < DEFAULT_GITHUB_RETRY_ATTEMPTS:
                time.sleep(GITHUB_RETRY_BACKOFF_SECONDS * attempt)
                continue
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < DEFAULT_GITHUB_RETRY_ATTEMPTS:
                time.sleep(GITHUB_RETRY_BACKOFF_SECONDS * attempt)
                continue
            return GitHubIssuesResult(
                (),
                f"GitHub issues timed out or could not connect after {DEFAULT_GITHUB_RETRY_ATTEMPTS} attempts. Showing seed roadmap data.",
            )
        except requests.RequestException:
            return GitHubIssuesResult((), "GitHub issues are unavailable. Showing seed roadmap data.")

    if response is None:
        return GitHubIssuesResult((), "GitHub issues are unavailable. Showing seed roadmap data.")

    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        return GitHubIssuesResult((), "GitHub API rate limit reached. Showing seed roadmap data.")
    if response.status_code >= 400:
        return GitHubIssuesResult(
            (),
            f"GitHub issues are unavailable (HTTP {response.status_code}). Showing seed roadmap data.",
        )

    try:
        payload = response.json()
    except ValueError:
        return GitHubIssuesResult((), "GitHub issue response was invalid. Showing seed roadmap data.")

    if not isinstance(payload, list):
        return GitHubIssuesResult((), "GitHub issue response was invalid. Showing seed roadmap data.")

    issues = tuple(item for item in payload if isinstance(item, dict) and "pull_request" not in item)
    return GitHubIssuesResult(issues)


__all__ = ["GitHubIssuesResult", "fetch_public_issues"]
