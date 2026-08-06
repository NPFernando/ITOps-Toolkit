"""Convert an integer between binary, octal, decimal, and hexadecimal."""

from __future__ import annotations

from typing import Any

BASES: dict[str, int] = {"Binary": 2, "Octal": 8, "Decimal": 10, "Hexadecimal": 16}
MAX_DIGITS = 128  # generous headroom while still bounding int() parse cost on hostile input


def convert_base(value: str, from_base_label: str) -> dict[str, Any]:
    """Parse ``value`` as ``from_base_label`` and return it rendered in every supported base."""
    result: dict[str, Any] = {"ok": False, "decimal": None, "values": {}, "error": None}

    if from_base_label not in BASES:
        result["error"] = f"Unknown base. Choose one of: {', '.join(BASES)}."
        return result

    cleaned = (value or "").strip()
    if not cleaned:
        result["error"] = "Enter a number."
        return result

    negative = cleaned.startswith("-")
    digits = cleaned[1:] if negative else cleaned
    # Strip a same-base prefix (0b/0o/0x) if the user included one.
    prefix = {2: "0b", 8: "0o", 16: "0x"}.get(BASES[from_base_label])
    if prefix and digits.lower().startswith(prefix):
        digits = digits[len(prefix):]

    if not digits:
        result["error"] = "Enter a number."
        return result
    if len(digits) > MAX_DIGITS:
        result["error"] = f"Number is longer than {MAX_DIGITS} digits."
        return result

    try:
        parsed = int(digits, BASES[from_base_label])
    except ValueError:
        result["error"] = f"\"{value}\" is not a valid {from_base_label.lower()} number."
        return result

    if negative:
        parsed = -parsed

    values = {
        "Binary": bin(parsed)[2:] if parsed >= 0 else "-" + bin(parsed)[3:],
        "Octal": oct(parsed)[2:] if parsed >= 0 else "-" + oct(parsed)[3:],
        "Decimal": str(parsed),
        "Hexadecimal": (hex(parsed)[2:] if parsed >= 0 else "-" + hex(parsed)[3:]).upper(),
    }

    result.update({"ok": True, "decimal": parsed, "values": values})
    return result
