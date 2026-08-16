from __future__ import annotations

from utils.url_parser import parse_url


def test_parse_url_full_url():
    result = parse_url("https://example.com:8443/path?a=1&b=2#frag")

    assert result["ok"] is True
    assert result["scheme"] == "https"
    assert result["host"] == "example.com"
    assert result["port"] == 8443
    assert result["path"] == "/path"
    assert result["fragment"] == "frag"
    assert result["query_params"] == [{"key": "a", "value": "1"}, {"key": "b", "value": "2"}]


def test_parse_url_repeated_query_keys_preserved():
    result = parse_url("https://example.com/?a=1&a=2")

    assert result["query_params"] == [{"key": "a", "value": "1"}, {"key": "a", "value": "2"}]


def test_parse_url_no_scheme_defaults_to_https():
    result = parse_url("example.com/path")

    assert result["ok"] is True
    assert result["scheme"] == "https"
    assert result["host"] == "example.com"


def test_parse_url_no_path_defaults_to_slash():
    result = parse_url("https://example.com")

    assert result["path"] == "/"


def test_parse_url_no_port_is_none():
    result = parse_url("https://example.com/path")

    assert result["port"] is None


def test_parse_url_rejects_empty_input():
    result = parse_url("")

    assert result["ok"] is False
    assert result["error"] == "Enter a URL."


def test_parse_url_rejects_input_with_no_hostname():
    # A bare scheme with nothing after it has no hostname at all -- urlsplit
    # itself is lenient about hostname characters (matching how the rest of
    # this app treats URL validation), but an empty hostname must still fail.
    result = parse_url("https://")

    assert result["ok"] is False


def test_parse_url_rejects_oversized_input():
    result = parse_url("https://example.com/" + "a" * 2048)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_parse_url_rejects_out_of_range_port_instead_of_crashing():
    # Regression: split.port raises ValueError uncaught for a port outside
    # 0-65535 -- an ordinary typo must not crash the page.
    result = parse_url("https://example.com:99999/")

    assert result["ok"] is False
    assert "Invalid port" in result["error"]


def test_parse_url_rejects_non_numeric_port_instead_of_crashing():
    result = parse_url("https://example.com:abc/")

    assert result["ok"] is False
    assert "Invalid port" in result["error"]
