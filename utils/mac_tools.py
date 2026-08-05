"""MAC address parsing, validation, and formatting helpers."""

from __future__ import annotations

import re
from typing import Any

import requests

MAX_INPUT_LENGTH = 64
VENDOR_LOOKUP_URL = "https://api.macvendors.com/{mac}"
VENDOR_LOOKUP_TIMEOUT = 6

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


def lookup_vendor(oui: str) -> dict[str, Any]:
    """Look up the registered vendor for a MAC address's OUI via a public API.

    Not a bundled dataset -- the real IEEE OUI registry is far too large to
    curate accurately by hand, and shipping wrong vendor attributions in a
    "public-safe, factual" tool would be worse than a live (rate-limited)
    lookup that can say "try again" when it's unsure.
    """
    result: dict[str, Any] = {"ok": False, "error": None, "vendor": None}
    stripped = re.sub(r"[:\-.\s]", "", (oui or "").strip().lower())
    # OUI-only input (6 hex chars) is padded with a dummy NIC portion just to
    # reuse _extract_hex's full-MAC validation; only the OUI matters to the API.
    hex_chars = _extract_hex(stripped if len(stripped) >= 12 else stripped + "0" * (12 - len(stripped)))
    if hex_chars is None or len(stripped) < 6:
        result["error"] = "Enter a valid MAC address or OUI (e.g. 00:1A:2B)."
        return result

    oui_only = hex_chars[:6]
    try:
        response = requests.get(VENDOR_LOOKUP_URL.format(mac=oui_only), timeout=VENDOR_LOOKUP_TIMEOUT)
    except requests.RequestException as exc:
        result["error"] = f"Vendor lookup failed: {exc}"
        return result

    if response.status_code == 404:
        result["error"] = "No registered vendor found for that OUI."
        return result
    if response.status_code == 429:
        result["error"] = "Vendor lookup is rate-limited right now. Try again in a moment."
        return result
    if not response.ok:
        result["error"] = f"Vendor lookup failed with status {response.status_code}."
        return result

    result.update({"ok": True, "vendor": response.text.strip()})
    return result
