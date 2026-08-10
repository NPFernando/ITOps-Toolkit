from __future__ import annotations

from utils.base32_tools import decode_base32_text, encode_base32_text


def test_encode_base32_text():
    assert encode_base32_text("hello world") == "NBSWY3DPEB3W64TMMQ======"


def test_decode_base32_text_round_trips():
    result = decode_base32_text("NBSWY3DPEB3W64TMMQ======")

    assert result["ok"] is True
    assert result["result"] == "hello world"


def test_decode_base32_text_accepts_lowercase():
    result = decode_base32_text("nbswy3dpeb3w64tmmq======")

    assert result["ok"] is True
    assert result["result"] == "hello world"


def test_decode_base32_text_accepts_whitespace_wrapped_input():
    result = decode_base32_text("NBSWY3DP\nEB3W64TM MQ======")

    assert result["ok"] is True
    assert result["result"] == "hello world"


def test_decode_base32_text_rejects_invalid_characters():
    result = decode_base32_text("not valid base32!!")

    assert result["ok"] is False
    assert "Invalid Base32" in result["error"]


def test_decode_base32_text_rejects_empty_input():
    result = decode_base32_text("")

    assert result["ok"] is False
    assert result["error"] == "Enter Base32 text to decode."


def test_decode_base32_text_rejects_oversized_input():
    result = decode_base32_text("A" * 20_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]
