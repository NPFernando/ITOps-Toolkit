from __future__ import annotations

from utils.http_header_parser import parse_headers_block


def test_parse_headers_block_detects_status_line():
    text = "HTTP/1.1 200 OK\nContent-Type: application/json\nCache-Control: no-cache\n"

    result = parse_headers_block(text)

    assert result["ok"] is True
    assert result["request_line"] == "HTTP/1.1 200 OK"
    names = [h["name"] for h in result["headers"]]
    assert names == ["Content-Type", "Cache-Control"]
    assert result["headers"][0]["explanation"] == "The media type of the body."


def test_parse_headers_block_detects_request_line():
    text = "GET /path HTTP/1.1\nHost: example.com\n"

    result = parse_headers_block(text)

    assert result["ok"] is True
    assert result["request_line"] == "GET /path HTTP/1.1"
    assert result["headers"][0]["name"] == "Host"


def test_parse_headers_block_headers_only_no_request_line():
    text = "Content-Type: text/html\nX-Custom: value\n"

    result = parse_headers_block(text)

    assert result["ok"] is True
    assert result["request_line"] is None
    assert len(result["headers"]) == 2


def test_parse_headers_block_unknown_header_has_empty_explanation():
    result = parse_headers_block("X-Custom-Header: some-value")

    assert result["headers"][0]["explanation"] == ""


def test_parse_headers_block_rejects_empty_input():
    result = parse_headers_block("")

    assert result["ok"] is False
    assert result["error"] == "Paste a block of HTTP headers."


def test_parse_headers_block_rejects_line_without_colon():
    result = parse_headers_block("not a valid header line")

    assert result["ok"] is False
    assert "Could not parse line" in result["error"]


def test_parse_headers_block_rejects_oversized_input():
    result = parse_headers_block("X: " + "a" * 100_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_parse_headers_block_handles_value_with_colon():
    result = parse_headers_block("Date: Mon, 10 Aug 2026 12:00:00 GMT")

    assert result["ok"] is True
    assert result["headers"][0]["value"] == "Mon, 10 Aug 2026 12:00:00 GMT"
