from __future__ import annotations

import requests

from utils import robots_validator


class FakeResponse:
    def __init__(self, status_code=200, text="", content=b""):
        self.status_code = status_code
        self.text = text
        self.content = content or text.encode("utf-8")


ROBOTS_CLEAN = "User-agent: *\nDisallow: /admin\nSitemap: https://example.com/sitemap.xml\n"
ROBOTS_WITH_ISSUES = "Disallow: /admin\nBadDirective: nope\nUser-agent: *\n"
SITEMAP_XML = '<?xml version="1.0"?><urlset><url><loc>https://example.com/</loc></url></urlset>'


def test_validate_robots_txt_clean_file(monkeypatch):
    def fake_get(url, headers=None, timeout=None):
        if url.endswith("/robots.txt"):
            return FakeResponse(200, ROBOTS_CLEAN)
        return FakeResponse(200, content=SITEMAP_XML.encode())

    monkeypatch.setattr(robots_validator.requests, "get", fake_get)

    result = robots_validator.validate_robots_txt("example.com")

    assert result["ok"] is True
    assert result["issues"] == []
    assert result["sitemaps"] == [{"url": "https://example.com/sitemap.xml", "ok": True, "detail": "Valid <urlset>."}]


def test_validate_robots_txt_flags_directive_before_user_agent_and_unrecognized(monkeypatch):
    monkeypatch.setattr(robots_validator.requests, "get", lambda url, headers=None, timeout=None: FakeResponse(200, ROBOTS_WITH_ISSUES))

    result = robots_validator.validate_robots_txt("example.com")

    assert result["ok"] is True
    assert any("before any 'User-agent'" in issue for issue in result["issues"])
    assert any("unrecognized directive" in issue for issue in result["issues"])


def test_validate_robots_txt_handles_404(monkeypatch):
    monkeypatch.setattr(robots_validator.requests, "get", lambda url, headers=None, timeout=None: FakeResponse(404))

    result = robots_validator.validate_robots_txt("example.com")

    assert result["ok"] is False
    assert "No robots.txt found" in result["error"]


def test_validate_robots_txt_handles_connection_error(monkeypatch):
    def fake_get(url, headers=None, timeout=None):
        raise requests.exceptions.ConnectionError("nope")

    monkeypatch.setattr(robots_validator.requests, "get", fake_get)

    result = robots_validator.validate_robots_txt("example.com")

    assert result["ok"] is False
    assert "Connection failed" in result["error"]


def test_validate_robots_txt_rejects_empty_domain():
    result = robots_validator.validate_robots_txt("")

    assert result["ok"] is False
    assert result["error"] == "Enter a domain name."


def test_validate_robots_txt_reports_malformed_sitemap_xml(monkeypatch):
    def fake_get(url, headers=None, timeout=None):
        if url.endswith("/robots.txt"):
            return FakeResponse(200, "Sitemap: https://example.com/sitemap.xml\n")
        return FakeResponse(200, content=b"not xml at all <<<")

    monkeypatch.setattr(robots_validator.requests, "get", fake_get)

    result = robots_validator.validate_robots_txt("example.com")

    assert result["sitemaps"][0]["ok"] is False
    assert "Not well-formed XML" in result["sitemaps"][0]["detail"]


def test_validate_robots_txt_caps_sitemaps_checked(monkeypatch):
    many_sitemaps = "".join(f"Sitemap: https://example.com/sitemap{i}.xml\n" for i in range(10))
    calls = []

    def fake_get(url, headers=None, timeout=None):
        calls.append(url)
        if url.endswith("/robots.txt"):
            return FakeResponse(200, many_sitemaps)
        return FakeResponse(200, content=SITEMAP_XML.encode())

    monkeypatch.setattr(robots_validator.requests, "get", fake_get)

    result = robots_validator.validate_robots_txt("example.com")

    assert len(result["sitemaps"]) == robots_validator.MAX_SITEMAPS_CHECKED
