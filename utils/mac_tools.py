"""MAC address parsing, validation, and formatting helpers."""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 64

_HEX_PAIR_RE = re.compile(r"^[0-9a-f]{12}$")


def _extract_hex(raw: str) -> str | None:
    """Strip common separators (: - . whitespace) and return 12 lowercase hex chars, or None."""
    stripped = re.sub(r"[:\-.\s]", "", raw.strip().lower())
    if not _HEX_PAIR_RE.match(stripped):
        return None
    return stripped


def analyze_mac(raw: str) -> dict[str, Any]:
    """Validate a MAC address and return canonical formats plus address-class bits."""
    result: dict[str, Any] = {
        "ok": False,
        "input": raw,
        "colon": None,
        "hyphen": None,
        "dot": None,
        "bare": None,
        "oui": None,
        "nic": None,
        "is_unicast": None,
        "is_multicast": None,
        "is_universal": None,
        "is_local": None,
        "error": None,
    }

    value = (raw or "").strip()
    if not value:
        result["error"] = "Enter a MAC address."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result

    hex_chars = _extract_hex(value)
    if hex_chars is None:
        result["error"] = "Enter a valid 48-bit MAC address (e.g. 00:1A:2B:3C:4D:5E)."
        return result

    octets = [hex_chars[i : i + 2] for i in range(0, 12, 2)]
    first_octet = int(octets[0], 16)
    is_multicast = bool(first_octet & 0b00000001)
    is_local = bool(first_octet & 0b00000010)

    result.update(
        {
            "ok": True,
            "colon": ":".join(octets),
            "hyphen": "-".join(octets),
            "dot": ".".join(hex_chars[i : i + 4] for i in range(0, 12, 4)),
            "bare": hex_chars,
            "oui": ":".join(octets[:3]),
            "nic": ":".join(octets[3:]),
            "is_unicast": not is_multicast,
            "is_multicast": is_multicast,
            "is_universal": not is_local,
            "is_local": is_local,
        }
    )
    return result
