"""Generate QR codes for URLs/text or Wi-Fi credentials."""

from __future__ import annotations

import io
from typing import Any

import qrcode

MAX_TEXT_LENGTH = 1000
WIFI_SECURITY_TYPES: tuple[str, ...] = ("WPA", "WEP", "nopass")
_WIFI_ESCAPE_CHARS = ("\\", ";", ",", ":", '"')


def _escape_wifi_field(value: str) -> str:
    escaped = value
    for char in _WIFI_ESCAPE_CHARS:
        escaped = escaped.replace(char, "\\" + char)
    return escaped


def build_wifi_payload(ssid: str, password: str, security: str = "WPA", hidden: bool = False) -> dict[str, Any]:
    """Build a WIFI: QR payload string per the format most phone cameras recognize."""
    result: dict[str, Any] = {"ok": False, "payload": "", "error": None}
    if security not in WIFI_SECURITY_TYPES:
        result["error"] = f"Unknown security type. Choose one of: {', '.join(WIFI_SECURITY_TYPES)}."
        return result
    if not ssid.strip():
        result["error"] = "Enter a network name (SSID)."
        return result
    if security != "nopass" and not password:
        result["error"] = "Enter a password, or choose security type 'nopass' for an open network."
        return result

    payload = (
        f"WIFI:T:{security};"
        f"S:{_escape_wifi_field(ssid)};"
        f"P:{_escape_wifi_field(password) if security != 'nopass' else ''};"
        f"H:{'true' if hidden else 'false'};;"
    )
    result.update({"ok": True, "payload": payload})
    return result


def generate_qr_code(data: str) -> dict[str, Any]:
    """Render ``data`` as a QR code and return it as PNG bytes."""
    result: dict[str, Any] = {"ok": False, "png_bytes": None, "error": None}
    cleaned = data or ""
    if not cleaned.strip():
        result["error"] = "Enter some text, a URL, or build a Wi-Fi payload."
        return result
    if len(cleaned) > MAX_TEXT_LENGTH:
        result["error"] = f"Input is longer than {MAX_TEXT_LENGTH} characters."
        return result

    try:
        image = qrcode.make(cleaned)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
    except Exception as exc:
        result["error"] = f"Could not generate a QR code: {exc}"
        return result

    result.update({"ok": True, "png_bytes": buffer.getvalue()})
    return result
