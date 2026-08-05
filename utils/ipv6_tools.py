"""IPv6 address compression/expansion helpers."""

from __future__ import annotations

import ipaddress
from typing import Any

MAX_INPUT_LENGTH = 128


def convert_ipv6(value: str) -> dict[str, Any]:
    """Return both the compressed (::) and fully expanded form of an IPv6 address."""
    result: dict[str, Any] = {"ok": False, "error": None, "compressed": None, "expanded": None}
    text = (value or "").strip()
    if not text:
        result["error"] = "Enter an IPv6 address."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result

    try:
        address = ipaddress.IPv6Address(text)
    except ValueError as exc:
        result["error"] = f"Invalid IPv6 address: {exc}"
        return result

    result.update({"ok": True, "compressed": address.compressed, "expanded": address.exploded})
    return result
