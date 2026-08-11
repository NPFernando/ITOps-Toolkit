from __future__ import annotations

from utils.base58_tool import decode_base58, encode_base58


def test_encode_matches_known_test_vector():
    result = encode_base58("Hello World")

    assert result["ok"] is True
    assert result["output"] == "JxF12TrwUP45BMd"


def test_decode_matches_known_test_vector():
    result = decode_base58("JxF12TrwUP45BMd")

    assert result["ok"] is True
    assert result["output"] == "Hello World"


def test_round_trip():
    original = "The quick brown fox jumps over the lazy dog."
    encoded = encode_base58(original)
    decoded = decode_base58(encoded["output"])

    assert decoded["output"] == original


def test_leading_null_bytes_become_leading_ones():
    # Base58 has no digit for zero, so leading 0x00 bytes need explicit
    # handling -- each one becomes a leading '1' in the encoded string.
    result = encode_base58("\x00\x00abc")

    assert result["ok"] is True
    assert result["output"].startswith("11")


def test_decode_rejects_invalid_characters():
    # '0', 'O', 'I', 'l' are deliberately excluded from the Base58 alphabet.
    result = decode_base58("0OIl")

    assert result["ok"] is False
    assert "Not valid Base58" in result["error"]


def test_encode_rejects_empty_input():
    result = encode_base58("")

    assert result["ok"] is False
    assert result["error"] == "Enter text to encode."


def test_decode_rejects_empty_input():
    result = decode_base58("")

    assert result["ok"] is False


def test_decode_rejects_non_utf8_bytes():
    # Base58 encoding of bytes 0xff 0xfe 0xfd -- not valid UTF-8.
    result = decode_base58("2UzCt")

    assert result["ok"] is False
    assert "not valid UTF-8" in result["error"]
