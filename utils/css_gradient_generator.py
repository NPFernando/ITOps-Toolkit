"""Build a CSS linear-gradient() or radial-gradient() declaration from color stops."""

from __future__ import annotations

import re
from typing import Any

MAX_STOPS = 10
_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def _parse_stops(stops_text: str) -> list[tuple[str, str]] | None:
    """Parse "lines of color[, position%]" into (color, position) pairs, or None if invalid."""
    stops = []
    for raw_line in (stops_text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        color = parts[0]
        if not _HEX_COLOR_RE.match(color):
            return None
        position = ""
        if len(parts) > 1:
            pos_value = parts[1].rstrip("%").strip()
            if not pos_value.lstrip("-").replace(".", "", 1).isdigit():
                return None
            position = f" {pos_value}%"
        stops.append((color, position))
    return stops


def build_gradient(stops_text: str, gradient_type: str = "linear", angle_or_shape: str = "90deg") -> dict[str, Any]:
    """Build a CSS gradient() declaration from newline-separated color stops."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    stops = _parse_stops(stops_text)
    if stops is None:
        result["error"] = "Each line must be a hex color (e.g. #ff0000) optionally followed by a comma and a position (e.g. #ff0000, 25%)."
        return result
    if len(stops) < 2:
        result["error"] = "Enter at least two color stops, one per line."
        return result
    if len(stops) > MAX_STOPS:
        result["error"] = f"Enter at most {MAX_STOPS} color stops."
        return result

    stop_list = ", ".join(f"{color}{position}" for color, position in stops)

    if gradient_type == "linear":
        css_function = f"linear-gradient({angle_or_shape}, {stop_list})"
    elif gradient_type == "radial":
        css_function = f"radial-gradient({angle_or_shape}, {stop_list})"
    else:
        result["error"] = f"Unknown gradient type: {gradient_type}."
        return result

    result.update({"ok": True, "output": f"background: {css_function};"})
    return result
