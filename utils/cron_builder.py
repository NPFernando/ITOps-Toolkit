"""Build a 5-field cron expression from simple per-field controls.

The reverse of Cron Explainer: that page takes a cron expression and
explains it; this builds the expression from structured choices, then
reuses explain_cron() to validate it and preview the readable
description and next run times, so the two pages stay consistent.
"""

from __future__ import annotations

from typing import Any

from utils.text_tools import explain_cron


FIELD_MODES: tuple[str, ...] = ("Every", "Every N", "Specific")
_FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day": (1, 31),
    "month": (1, 12),
    "weekday": (0, 6),
}


def _field_value(field: str, mode: str, step: int, values: list[int]) -> dict[str, Any]:
    low, high = _FIELD_RANGES[field]
    if mode == "Every":
        return {"ok": True, "value": "*", "error": None}
    if mode == "Every N":
        if step < 1:
            return {"ok": False, "value": "", "error": f"{field.title()} step must be at least 1."}
        return {"ok": True, "value": f"*/{step}", "error": None}
    if mode == "Specific":
        if not values:
            return {"ok": False, "value": "", "error": f"Choose at least one {field} value."}
        out_of_range = [v for v in values if not low <= v <= high]
        if out_of_range:
            return {"ok": False, "value": "", "error": f"{field.title()} values must be between {low} and {high}."}
        return {"ok": True, "value": ",".join(str(v) for v in sorted(set(values))), "error": None}
    return {"ok": False, "value": "", "error": f"Unknown mode for {field}."}


def build_cron_expression(
    minute_mode: str, minute_step: int, minute_values: list[int],
    hour_mode: str, hour_step: int, hour_values: list[int],
    day_mode: str, day_step: int, day_values: list[int],
    month_mode: str, month_step: int, month_values: list[int],
    weekday_mode: str, weekday_step: int, weekday_values: list[int],
) -> dict[str, Any]:
    """Build and validate a cron expression from per-field mode/step/values."""
    fields = [
        _field_value("minute", minute_mode, minute_step, minute_values),
        _field_value("hour", hour_mode, hour_step, hour_values),
        _field_value("day", day_mode, day_step, day_values),
        _field_value("month", month_mode, month_step, month_values),
        _field_value("weekday", weekday_mode, weekday_step, weekday_values),
    ]

    for field in fields:
        if not field["ok"]:
            return {"ok": False, "expression": "", "description": "", "next_runs": [], "error": field["error"]}

    expression = " ".join(field["value"] for field in fields)
    explanation = explain_cron(expression)
    if not explanation["ok"]:
        return {"ok": False, "expression": expression, "description": "", "next_runs": [], "error": explanation["error"]}

    return {
        "ok": True,
        "expression": expression,
        "description": explanation["description"],
        "next_runs": explanation["next_runs"],
        "error": None,
    }
