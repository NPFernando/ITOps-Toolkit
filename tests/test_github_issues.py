from __future__ import annotations

import requests

from utils import github_issues


class FakeResponse:
    def __init__(self, status_code=200, payload=None, headers=None):
        self.status_code = status_code
        self._payload = payload
        self.headers = headers or {}

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def test_fetch_public_issues_filters_pull_requests(monkeypatch):
    captured = {}

    def fake_get(url, params=None, headers=None, timeout=None):
        captured.update({"url": url, "params": params, "headers": headers, "timeout": timeout})
        return FakeResponse(
            payload=[
                {"number": 1, "title": "Issue"},
                {"number": 2, "title": "PR", "pull_request": {"url": "https://api.github.com/pulls/2"}},
            ]
        )

    monkeypatch.setattr(github_issues.requests, "get", fake_get)

    result = github_issues.fetch_public_issues("https://github.com/NPFernando/ITOps-Toolkit")

    assert result.error is None
    assert tuple(issue["number"] for issue in result.issues) == (1,)
    assert captured["url"] == "https://api.github.com/repos/NPFernando/ITOps-Toolkit/issues"
    assert captured["params"] == {"state": "all", "per_page": 100}


def test_fetch_public_issues_handles_rate_limit(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse(status_code=403, headers={"X-RateLimit-Remaining": "0"}, payload=[])

    monkeypatch.setattr(github_issues.requests, "get", fake_get)

    result = github_issues.fetch_public_issues("https://github.com/NPFernando/ITOps-Toolkit")

    assert result.issues == ()
    assert result.error == "GitHub API rate limit reached. Showing seed roadmap data."


def test_fetch_public_issues_handles_request_errors(monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(github_issues.requests, "get", fake_get)

    result = github_issues.fetch_public_issues("https://github.com/NPFernando/ITOps-Toolkit")

    assert result.issues == ()
    assert result.error == "GitHub issues are unavailable. Showing seed roadmap data."


def test_fetch_public_issues_rejects_invalid_repo_url():
    result = github_issues.fetch_public_issues("https://example.com/not/github")

    assert result.issues == ()
    assert result.error == "GitHub repository URL is invalid. Showing seed roadmap data."
