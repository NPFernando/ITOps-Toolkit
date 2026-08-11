from __future__ import annotations

import base64

from utils.basic_auth_tool import build_basic_auth_header, parse_basic_auth_header


def test_build_header():
    result = build_basic_auth_header("alice", "password123")

    assert result["ok"] is True
    assert result["output"] == "Basic YWxpY2U6cGFzc3dvcmQxMjM="


def test_build_rejects_colon_in_username():
    result = build_basic_auth_header("ali:ce", "x")

    assert result["ok"] is False
    assert "colon" in result["error"]


def test_build_rejects_empty_username():
    result = build_basic_auth_header("", "x")

    assert result["ok"] is False
    assert result["error"] == "Enter a username."


def test_build_allows_empty_password():
    result = build_basic_auth_header("alice", "")

    assert result["ok"] is True


def test_parse_full_header_value():
    result = parse_basic_auth_header("Basic YWxpY2U6cGFzc3dvcmQxMjM=")

    assert result["ok"] is True
    assert result["username"] == "alice"
    assert result["password"] == "password123"


def test_parse_bare_token():
    result = parse_basic_auth_header("YWxpY2U6cGFzc3dvcmQxMjM=")

    assert result["ok"] is True
    assert result["username"] == "alice"


def test_parse_password_may_contain_colon():
    result = parse_basic_auth_header(build_basic_auth_header("alice", "p:ss:word")["output"])

    assert result["ok"] is True
    assert result["username"] == "alice"
    assert result["password"] == "p:ss:word"


def test_parse_rejects_invalid_base64():
    result = parse_basic_auth_header("Basic not-valid-base64!!!")

    assert result["ok"] is False
    assert "Not valid Base64" in result["error"]


def test_parse_rejects_missing_colon_separator():
    token = base64.b64encode(b"nocolonhere").decode()
    result = parse_basic_auth_header(f"Basic {token}")

    assert result["ok"] is False
    assert "separator" in result["error"]


def test_parse_rejects_empty_input():
    result = parse_basic_auth_header("")

    assert result["ok"] is False
