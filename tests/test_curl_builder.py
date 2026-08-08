from __future__ import annotations

from utils.curl_builder import build_curl_command


def test_build_curl_command_get_with_no_headers_or_body():
    result = build_curl_command("https://example.com/webhook", "GET")

    assert result["ok"] is True
    assert result["command"] == "curl -X GET https://example.com/webhook"


def test_build_curl_command_post_includes_headers_and_body_shell_quoted():
    result = build_curl_command(
        "https://example.com/webhook",
        "POST",
        headers_text="Content-Type: application/json\nAuthorization: Bearer abc def",
        body='{"a": 1}',
    )

    assert result["ok"] is True
    assert result["command"] == (
        "curl -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer abc def' "
        "-d '{\"a\": 1}' https://example.com/webhook"
    )


def test_build_curl_command_ignores_body_for_get():
    result = build_curl_command("https://example.com", "GET", body="should not appear")

    assert result["ok"] is True
    assert "-d" not in result["command"]


def test_build_curl_command_rejects_empty_url():
    result = build_curl_command("", "GET")

    assert result["ok"] is False
    assert result["error"] == "Enter a URL."


def test_build_curl_command_rejects_invalid_url():
    result = build_curl_command("not-a-url", "GET")

    assert result["ok"] is False
    assert "valid HTTP or HTTPS URL" in result["error"]


def test_build_curl_command_rejects_invalid_method():
    result = build_curl_command("https://example.com", "BOGUS")

    assert result["ok"] is False
    assert "Method must be one of" in result["error"]


def test_build_curl_command_rejects_malformed_headers():
    result = build_curl_command("https://example.com", "GET", headers_text="not-a-header-line")

    assert result["ok"] is False
    assert "Key: Value" in result["error"]
