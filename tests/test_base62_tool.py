from __future__ import annotations

from utils.base62_tool import decode_base62, encode_base62


def test_encode_zero():
    result = encode_base62("0")

    assert result["ok"] is True
    assert result["output"] == "0"


def test_encode_known_value():
    result = encode_base62("12345")

    assert result["ok"] is True
    assert result["output"] == "3D7"


def test_decode_known_value():
    result = decode_base62("3D7")

    assert result["ok"] is True
    assert result["output"] == "12345"


def test_round_trip_large_value():
    original = "9223372036854775807"
    encoded = encode_base62(original)
    decoded = decode_base62(encoded["output"])

    assert decoded["output"] == original


def test_encode_rejects_negative():
    result = encode_base62("-5")

    assert result["ok"] is False
    assert "non-negative" in result["error"]


def test_encode_rejects_non_numeric():
    result = encode_base62("abc")

    assert result["ok"] is False


def test_decode_rejects_invalid_characters():
    result = decode_base62("!!")

    assert result["ok"] is False
    assert "Not valid Base62" in result["error"]


def test_encode_rejects_empty_input():
    result = encode_base62("")

    assert result["ok"] is False


def test_decode_rejects_empty_input():
    result = decode_base62("")

    assert result["ok"] is False
