"""Validate a Luhn-checksummed number (credit card, IMEI, etc.) and compute its check digit."""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 32
_SEPARATORS = re.compile(r"[\s-]")


def _luhn_checksum_valid(digits: str) -> bool:
    total = 0
    for index, char in enumerate(reversed(digits)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total % 10 == 0


def _compute_check_digit(payload_digits: str) -> int:
    """Compute the check digit that would make ``payload_digits`` + check digit pass Luhn."""
    total = 0
    for index, char in enumerate(reversed(payload_digits)):
        value = int(char)
        if index % 2 == 0:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return (10 - (total % 10)) % 10


def validate_luhn(number_str: str) -> dict[str, Any]:
    """Validate a Luhn-checksummed number and compute the check digit for its payload."""
    result: dict[str, Any] = {"ok": False, "error": None, "digits_only": None, "is_valid": None, "check_digit": None}

    value = (number_str or "").strip()
    if not value:
        result["error"] = "Enter a number to validate."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    digits_only = _SEPARATORS.sub("", value)
    if not digits_only.isdigit():
        result["error"] = "Enter only digits, spaces, or hyphens."
        return result
    if len(digits_only) < 2:
        result["error"] = "Enter at least 2 digits."
        return result

    result.update(
        {
            "ok": True,
            "digits_only": digits_only,
            "is_valid": _luhn_checksum_valid(digits_only),
            "check_digit": _compute_check_digit(digits_only[:-1]),
        }
    )
    return result
