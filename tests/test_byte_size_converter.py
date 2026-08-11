from __future__ import annotations

from utils.byte_size_converter import bytes_to_human, human_to_bytes


def test_bytes_to_human_binary():
    result = bytes_to_human("1536")

    assert result["ok"] is True
    assert result["result"] == "1.50 KiB"


def test_bytes_to_human_decimal():
    result = bytes_to_human("1536", binary=False)

    assert result["ok"] is True
    assert result["result"] == "1.54 KB"


def test_bytes_to_human_large_value():
    result = bytes_to_human(str(5 * 1024**3))

    assert result["ok"] is True
    assert result["result"] == "5.00 GiB"


def test_bytes_to_human_zero():
    result = bytes_to_human("0")

    assert result["ok"] is True
    assert result["result"] == "0 B"


def test_bytes_to_human_rejects_negative():
    result = bytes_to_human("-5")

    assert result["ok"] is False
    assert "non-negative" in result["error"]


def test_bytes_to_human_rejects_non_numeric():
    result = bytes_to_human("abc")

    assert result["ok"] is False
    assert result["error"] == "Enter a valid number."


def test_bytes_to_human_rejects_empty_input():
    result = bytes_to_human("")

    assert result["ok"] is False
    assert result["error"] == "Enter a byte count."


def test_human_to_bytes_binary():
    result = human_to_bytes("5", "GiB")

    assert result["ok"] is True
    assert result["result"] == 5 * 1024**3


def test_human_to_bytes_decimal():
    result = human_to_bytes("1.5", "KB", binary=False)

    assert result["ok"] is True
    assert result["result"] == 1500


def test_human_to_bytes_rejects_unknown_unit():
    result = human_to_bytes("5", "BOGUS")

    assert result["ok"] is False
    assert "Unknown unit" in result["error"]


def test_human_to_bytes_rejects_negative():
    result = human_to_bytes("-1", "GiB")

    assert result["ok"] is False
    assert "non-negative" in result["error"]


def test_bytes_to_human_rejects_oversized_input():
    result = bytes_to_human("1" * 33)

    assert result["ok"] is False
    assert "longer than" in result["error"]
