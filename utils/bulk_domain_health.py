"""Batch orchestration for running the Domain Health checks across many domains."""

from __future__ import annotations

from typing import Any

from utils.dns_tools import MAX_DOMAIN_LENGTH, get_dns_summary, normalize_domain
from utils.http_tools import check_http_status
from utils.scoring import calculate_risk_score
from utils.ssl_tools import get_certificate_info
from utils.text_tools import validate_length

MAX_DOMAINS_PER_BATCH = 25


def parse_domain_list(raw_text: str) -> list[str]:
    """Split pasted/uploaded text into a deduped, order-preserving list of candidate domains.

    Accepts one domain per line, or a CSV where the domain is the first column
    (a trailing comma-separated remainder on a line is simply ignored).
    """
    seen: set[str] = set()
    domains: list[str] = []
    for line in (raw_text or "").splitlines():
        candidate = line.split(",")[0].strip()
        if not candidate or candidate.lower() in {"domain", "domains", "hostname"}:
            continue
        if candidate not in seen:
            seen.add(candidate)
            domains.append(candidate)
    return domains


def _row_for_error(raw_domain: str, error: str) -> dict[str, Any]:
    return {
        "domain": raw_domain,
        "risk_score": None,
        "risk_status": "Unknown",
        "http_status": None,
        "dns_status": "Unknown",
        "ssl_days_remaining": None,
        "error": error,
    }


def run_bulk_health_check(domains: list[str], include_dmarc: bool = True) -> list[dict[str, Any]]:
    """Run the Domain Health Checker's core checks for each domain, capped at MAX_DOMAINS_PER_BATCH."""
    results: list[dict[str, Any]] = []
    for raw_domain in domains[:MAX_DOMAINS_PER_BATCH]:
        ok, error = validate_length(raw_domain, MAX_DOMAIN_LENGTH, "Domain")
        if not ok:
            results.append(_row_for_error(raw_domain, error))
            continue
        normalized = normalize_domain(raw_domain)
        if not normalized:
            results.append(_row_for_error(raw_domain, "Could not parse a domain name."))
            continue

        dns_summary = get_dns_summary(normalized, include_dmarc=include_dmarc)
        ssl_result = get_certificate_info(normalized)
        http_result = check_http_status(normalized)
        dmarc_for_score = bool(dns_summary["dmarc_found"]) if include_dmarc else True
        risk = calculate_risk_score(
            http_ok=bool(http_result["ok"]),
            ssl_ok=bool(ssl_result["ok"]),
            ssl_days_remaining=ssl_result["days_remaining"],
            mx_found=bool(dns_summary["mx_found"]),
            spf_found=bool(dns_summary["spf_found"]),
            dmarc_found=dmarc_for_score,
        )

        results.append(
            {
                "domain": normalized,
                "risk_score": risk["score"],
                "risk_status": risk["status"],
                "http_status": http_result["status_code"],
                "dns_status": dns_summary["status"],
                "ssl_days_remaining": ssl_result["days_remaining"],
                "error": http_result["error"] or ssl_result["error"],
            }
        )
    return results
