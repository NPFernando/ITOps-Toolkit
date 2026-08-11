"""Check whether two cron schedules ever fire at the same minute within a lookahead window.

Useful for avoiding two jobs contending for the same resource (a shared
DB connection pool, a lock file) without noticing they're scheduled to
run simultaneously. Reuses croniter (already a dependency, used by Cron
Explainer/Builder) rather than hand-rolling cron parsing.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from croniter import croniter

MAX_LOOKAHEAD_DAYS = 90
# Hard cap on how many occurrences we'll compute per schedule, so a
# once-a-minute schedule combined with a long lookahead window can't turn
# this into an unbounded loop.
MAX_OCCURRENCES_PER_SCHEDULE = 200_000


def _occurrences_within(expression: str, start: datetime, end: datetime) -> list[datetime] | None:
    if not croniter.is_valid(expression):
        return None
    iterator = croniter(expression, start)
    times = []
    while True:
        next_time = iterator.get_next(datetime)
        if next_time > end:
            break
        times.append(next_time)
        if len(times) > MAX_OCCURRENCES_PER_SCHEDULE:
            break
    return times


def find_cron_overlaps(expression_a: str, expression_b: str, lookahead_days: int = 7) -> dict[str, Any]:
    """Find run times where both cron schedules fire in the same minute."""
    result: dict[str, Any] = {"ok": False, "error": None, "overlaps": None, "count_a": 0, "count_b": 0}

    expression_a, expression_b = (expression_a or "").strip(), (expression_b or "").strip()
    if not expression_a or not expression_b:
        result["error"] = "Enter both cron expressions."
        return result
    if not (1 <= lookahead_days <= MAX_LOOKAHEAD_DAYS):
        result["error"] = f"Lookahead must be between 1 and {MAX_LOOKAHEAD_DAYS} days."
        return result

    start = datetime.now().replace(second=0, microsecond=0)
    end = start + timedelta(days=lookahead_days)

    times_a = _occurrences_within(expression_a, start, end)
    if times_a is None:
        result["error"] = f"'{expression_a}' is not a valid cron expression."
        return result
    times_b = _occurrences_within(expression_b, start, end)
    if times_b is None:
        result["error"] = f"'{expression_b}' is not a valid cron expression."
        return result

    overlaps = sorted(set(times_a) & set(times_b))
    result.update(
        {
            "ok": True,
            "overlaps": [t.strftime("%Y-%m-%d %H:%M") for t in overlaps],
            "count_a": len(times_a),
            "count_b": len(times_b),
        }
    )
    return result
