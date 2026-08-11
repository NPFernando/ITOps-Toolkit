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


def test_human_to_bytes_large_value_is_exact():
    # Regression: float multiplication silently loses precision at large
    # magnitudes (verified directly: the old float-based implementation
    # was off by billions with no warning). Decimal arithmetic must be
    # exact here.
    result = human_to_bytes("123456789012345", "PB", binary=False)

    assert result["ok"] is True
    assert result["result"] == 123456789012345 * 1000**5


def test_bytes_to_human_rounds_sub_byte_fraction():
    # Regression: int(size) truncated rather than rounded, so "0.5" bytes
    # silently became "0 B" instead of rounding to the nearest byte.
    result = bytes_to_human("0.5")

    assert result["ok"] is True
    assert result["result"] == "1 B"


def test_bytes_to_human_rounds_near_unit_boundary():
    result = bytes_to_human("1023.9")

    assert result["ok"] is True
    assert result["result"] == "1024 B"
