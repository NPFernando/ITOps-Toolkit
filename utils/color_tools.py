"""Color code conversion helpers (HEX, RGB, HSL)."""

from __future__ import annotations

import colorsys
import re
from typing import Any

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")
_RGB_RE = re.compile(r"^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*[\d.]+\s*)?\)$", re.IGNORECASE)
_HSL_RE = re.compile(r"^hsla?\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*(?:,\s*[\d.]+\s*)?\)$", re.IGNORECASE)

MAX_INPUT_LENGTH = 64


def _from_rgb(r: int, g: int, b: int) -> dict[str, Any]:
    for value in (r, g, b):
        if not 0 <= value <= 255:
            return {"ok": False, "error": "RGB values must be between 0 and 255."}

    hex_code = f"#{r:02x}{g:02x}{b:02x}"
    hue, lightness, saturation = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hsl = f"hsl({round(hue * 360)}, {round(saturation * 100)}%, {round(lightness * 100)}%)"
    return {
        "ok": True,
        "error": None,
        "hex": hex_code,
        "rgb": f"rgb({r}, {g}, {b})",
        "hsl": hsl,
        "r": r,
        "g": g,
        "b": b,
    }


def parse_color(value: str) -> dict[str, Any]:
    """Parse a HEX, rgb()/rgba(), or hsl()/hsla() color string and return all three forms."""
    result: dict[str, Any] = {"ok": False, "error": None}
    text = (value or "").strip()
    if not text:
        result["error"] = "Enter a color as HEX (#rrggbb), rgb(), or hsl()."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result

    hex_match = _HEX_RE.match(text)
    if hex_match:
        digits = hex_match.group(1)
        if len(digits) == 3:
            digits = "".join(ch * 2 for ch in digits)
        r, g, b = (int(digits[i : i + 2], 16) for i in (0, 2, 4))
        return _from_rgb(r, g, b)

    rgb_match = _RGB_RE.match(text)
    if rgb_match:
        r, g, b = (int(group) for group in rgb_match.groups())
        return _from_rgb(r, g, b)

    hsl_match = _HSL_RE.match(text)
    if hsl_match:
        hue, saturation, lightness = (int(group) for group in hsl_match.groups())
        if not (0 <= hue <= 360 and 0 <= saturation <= 100 and 0 <= lightness <= 100):
            result["error"] = "HSL values must be h: 0-360, s/l: 0-100."
            return result
        r, g, b = colorsys.hls_to_rgb(hue / 360, lightness / 100, saturation / 100)
        return _from_rgb(round(r * 255), round(g * 255), round(b * 255))

    result["error"] = "Could not parse that color. Try #rrggbb, rgb(r, g, b), or hsl(h, s%, l%)."
    return result
