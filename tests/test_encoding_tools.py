from __future__ import annotations

from utils.encoding_tools import MAX_FILE_SIZE_BYTES, convert_to_utf8, detect_encoding


def test_detect_encoding_ascii():
    result = detect_encoding(b"hello world")

    assert result["ok"] is True
    assert result["encoding"] == "ascii"
    assert result["confidence"] == 100.0
    assert result["preview"] == "hello world"


def test_detect_encoding_shift_jis():
    result = detect_encoding("こんにちは".encode("shift_jis"))

    assert result["ok"] is True
    assert result["encoding"] is not None
    assert "こんにちは" in result["preview"]


def test_detect_encoding_rejects_empty_input():
    result = detect_encoding(b"")

    assert result["ok"] is False
    assert result["error"] == "Upload a file to detect its encoding."


def test_detect_encoding_rejects_oversized_input():
    result = detect_encoding(b"x" * (MAX_FILE_SIZE_BYTES + 1))

    assert result["ok"] is False
    assert "larger than" in result["error"]


def test_detect_encoding_truncates_preview():
    result = detect_encoding(b"a" * 10_000)

    assert result["ok"] is True
    assert len(result["preview"]) == 500


def test_convert_to_utf8_roundtrips_shift_jis():
    result = convert_to_utf8("こんにちは".encode("shift_jis"))

    assert result["ok"] is True
    assert result["utf8_text"] == "こんにちは"


def test_convert_to_utf8_rejects_empty_input():
    result = convert_to_utf8(b"")

    assert result["ok"] is False
    assert result["error"] == "Upload a file to detect its encoding."
