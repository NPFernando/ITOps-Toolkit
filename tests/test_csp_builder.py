from __future__ import annotations

from utils.csp_builder import build_csp


def test_builds_directive_with_quoted_keyword():
    result = build_csp({"default-src": "self"})

    assert result["ok"] is True
    assert result["output"] == "default-src 'self';"


def test_mixes_keyword_and_host_sources():
    result = build_csp({"script-src": "self unsafe-inline https://cdn.example.com"})

    assert result["ok"] is True
    assert result["output"] == "script-src 'self' 'unsafe-inline' https://cdn.example.com;"


def test_accepts_comma_separated_sources():
    result = build_csp({"default-src": "self, https://example.com"})

    assert result["ok"] is True
    assert "'self' https://example.com" in result["output"]


def test_multiple_directives_joined_with_semicolons():
    result = build_csp({"default-src": "self", "img-src": "*"})

    assert result["ok"] is True
    assert result["output"] == "default-src 'self'; img-src *;"


def test_blank_directives_are_skipped():
    result = build_csp({"default-src": "self", "script-src": ""})

    assert result["ok"] is True
    assert "script-src" not in result["output"]


def test_rejects_none_combined_with_other_sources():
    result = build_csp({"default-src": "none self"})

    assert result["ok"] is False
    assert "'none' must be the only source" in result["error"]


def test_rejects_unknown_directive():
    result = build_csp({"bogus-src": "self"})

    assert result["ok"] is False
    assert "Unknown directive" in result["error"]


def test_rejects_empty_input():
    result = build_csp({})

    assert result["ok"] is False
    assert result["error"] == "Enter at least one directive with sources."
