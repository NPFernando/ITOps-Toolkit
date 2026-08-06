"""One-off, in-memory latency trend probe -- no historical checks are stored."""

from __future__ import annotations

import time
from typing import Any

from utils.http_tools import MAX_URL_LENGTH, check_http_status, normalize_url

MIN_CHECKS = 3
MAX_CHECKS = 20
MAX_INTERVAL_SECONDS = 5.0


def run_latency_trend(url: str, checks: int, interval_seconds: float) -> dict[str, Any]:
    """Run ``checks`` sequential HTTP checks against ``url``, sleeping ``interval_seconds``
    between each. Every sample lives only in the returned dict for this one page render --
    nothing is written to disk, a database, or any store that survives the request."""
    normalized = normalize_url(url)
    result: dict[str, Any] = {
        "ok": False,
        "url": normalized,
        "samples": [],
        "uptime_pct": None,
        "avg_latency_ms": None,
        "min_latency_ms": None,
        "max_latency_ms": None,
        "error": None,
    }

    if not normalized:
        result["error"] = "Enter a URL."
        return result
    if len(normalized) > MAX_URL_LENGTH:
        result["error"] = f"URL is longer than {MAX_URL_LENGTH} characters."
        return result
    if not MIN_CHECKS <= checks <= MAX_CHECKS:
        result["error"] = f"Number of checks must be between {MIN_CHECKS} and {MAX_CHECKS}."
        return result
    if not 0 <= interval_seconds <= MAX_INTERVAL_SECONDS:
        result["error"] = f"Interval must be between 0 and {MAX_INTERVAL_SECONDS} seconds."
        return result

    samples: list[dict[str, Any]] = []
    for index in range(checks):
        check = check_http_status(normalized)
        samples.append(
            {
                "index": index + 1,
                "ok": bool(check["ok"]),
                "status_code": check["status_code"],
                "response_time_ms": check["response_time_ms"],
                "error": check["error"],
            }
        )
        if index < checks - 1 and interval_seconds > 0:
            time.sleep(interval_seconds)

    successful = [s for s in samples if s["ok"] and s["response_time_ms"] is not None]
    latencies = [s["response_time_ms"] for s in successful]

    result.update(
        {
            "ok": True,
            "samples": samples,
            "uptime_pct": round(100 * sum(1 for s in samples if s["ok"]) / len(samples), 1),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else None,
            "min_latency_ms": min(latencies) if latencies else None,
            "max_latency_ms": max(latencies) if latencies else None,
        }
    )
    return result
