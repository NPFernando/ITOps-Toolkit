"""CVE lookup via the NIST National Vulnerability Database (NVD) public API."""

from __future__ import annotations

import re
from typing import Any

import requests


NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_TIMEOUT = 10
MAX_QUERY_LENGTH = 200
MAX_KEYWORD_RESULTS = 10
_HEADERS = {"User-Agent": "ITOpsToolkit/1.0 public-safe-checker"}
_CVE_ID_PATTERN = re.compile(r"^CVE-\d{4}-\d{4,}$", re.IGNORECASE)

# NVD returns multiple CVSS versions when present; prefer the newest available.
_CVSS_METRIC_PRIORITY = ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2")


def _best_cvss(metrics: dict[str, Any]) -> dict[str, Any] | None:
    for key in _CVSS_METRIC_PRIORITY:
        entries = metrics.get(key) or []
        if entries:
            data = entries[0].get("cvssData", {})
            return {
                "version": data.get("version"),
                "base_score": data.get("baseScore"),
                "base_severity": data.get("baseSeverity") or entries[0].get("baseSeverity"),
                "vector_string": data.get("vectorString"),
            }
    return None


def _english_description(descriptions: list[dict[str, str]]) -> str:
    for entry in descriptions:
        if entry.get("lang") == "en":
            return entry.get("value", "")
    return descriptions[0].get("value", "") if descriptions else ""


def _summarize_cve(cve: dict[str, Any]) -> dict[str, Any]:
    cvss = _best_cvss(cve.get("metrics", {}))
    return {
        "id": cve.get("id"),
        "status": cve.get("vulnStatus"),
        "published": cve.get("published"),
        "last_modified": cve.get("lastModified"),
        "description": _english_description(cve.get("descriptions", [])),
        "cvss": cvss,
        "references": [ref.get("url") for ref in cve.get("references", []) if ref.get("url")][:5],
    }


def _empty_result(query: str) -> dict[str, Any]:
    return {"ok": False, "query": query, "results": [], "total_results": 0, "error": None}


def lookup_cve(query: str) -> dict[str, Any]:
    """Look up a CVE by exact ID (CVE-YYYY-NNNN) or search by keyword."""
    cleaned = (query or "").strip()
    result = _empty_result(cleaned)

    if not cleaned:
        result["error"] = "Enter a CVE ID or a search keyword."
        return result
    if len(cleaned) > MAX_QUERY_LENGTH:
        result["error"] = f"Query is longer than {MAX_QUERY_LENGTH} characters."
        return result

    if _CVE_ID_PATTERN.match(cleaned):
        params = {"cveId": cleaned.upper()}
    else:
        params = {"keywordSearch": cleaned, "resultsPerPage": MAX_KEYWORD_RESULTS}

    try:
        response = requests.get(NVD_URL, params=params, headers=_HEADERS, timeout=NVD_TIMEOUT)
    except requests.RequestException as exc:
        result["error"] = f"CVE lookup failed: {exc}"
        return result

    if response.status_code == 404:
        result["error"] = "No matching CVE found."
        return result
    if response.status_code == 429:
        result["error"] = "NVD rate limit reached. Wait a moment and try again."
        return result
    if response.status_code != 200:
        result["error"] = f"CVE lookup failed with status {response.status_code}."
        return result

    try:
        payload = response.json()
    except ValueError:
        result["error"] = "CVE lookup returned an unexpected response."
        return result

    vulnerabilities = payload.get("vulnerabilities", [])
    if not vulnerabilities:
        result["error"] = "No matching CVE found."
        return result

    result.update(
        {
            "ok": True,
            "results": [_summarize_cve(v["cve"]) for v in vulnerabilities],
            "total_results": payload.get("totalResults", len(vulnerabilities)),
        }
    )
    return result
