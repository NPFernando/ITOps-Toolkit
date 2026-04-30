"""Risk scoring for domain health checks."""

from __future__ import annotations

from typing import Any


def status_from_score(score: int) -> str:
    if score >= 80:
        return "Healthy"
    if score >= 50:
        return "Warning"
    return "Critical"


def calculate_risk_score(
    http_ok: bool,
    ssl_ok: bool,
    ssl_days_remaining: int | None,
    mx_found: bool,
    spf_found: bool,
    dmarc_found: bool,
) -> dict[str, Any]:
    """Calculate the requested 0-100 health score and recommendations."""
    score = 100
    deductions: list[dict[str, Any]] = []

    def subtract(points: int, reason: str) -> None:
        nonlocal score
        score -= points
        deductions.append({"points": points, "reason": reason})

    if not http_ok:
        subtract(25, "Website not reachable or returned an error.")
    if not ssl_ok:
        subtract(25, "SSL certificate is invalid or expired.")
    elif ssl_days_remaining is not None and ssl_days_remaining < 30:
        subtract(15, "SSL certificate expires in less than 30 days.")
    if not mx_found:
        subtract(15, "No MX records were found.")
    if not spf_found:
        subtract(15, "Missing SPF record.")
    if not dmarc_found:
        subtract(15, "Missing DMARC record.")

    final_score = max(0, score)
    return {
        "score": final_score,
        "status": status_from_score(final_score),
        "deductions": deductions,
        "recommendations": [item["reason"] for item in deductions],
    }
