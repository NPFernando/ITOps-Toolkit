"""HTTP security header grading, similar to securityheaders.com."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse

import requests

from utils.http_tools import MAX_URL_LENGTH, normalize_url


MIN_RECOMMENDED_HSTS_MAX_AGE = 31536000  # 1 year, matches common HSTS preload guidance

GRADE_THRESHOLDS = (
    (6, "A"),
    (5, "B"),
    (3, "C"),
    (1, "D"),
)


def _check_hsts(value: str | None) -> dict[str, Any]:
    if not value:
        return {"header": "Strict-Transport-Security", "present": False, "status": "fail", "note": "Missing -- browsers will not enforce HTTPS-only for this site."}
    note = "Present."
    status = "pass"
    max_age = None
    for part in value.split(";"):
        part = part.strip()
        if part.lower().startswith("max-age="):
            try:
                max_age = int(part.split("=", 1)[1])
            except ValueError:
                max_age = None
    if max_age is None:
        status = "warn"
        note = "Present, but max-age is missing or unparseable."
    elif max_age < MIN_RECOMMENDED_HSTS_MAX_AGE:
        status = "warn"
        note = f"Present, but max-age ({max_age}s) is below the commonly recommended {MIN_RECOMMENDED_HSTS_MAX_AGE}s (1 year)."
    if "includesubdomains" not in value.lower():
        note += " Consider adding includeSubDomains."
    return {"header": "Strict-Transport-Security", "present": True, "status": status, "value": value, "note": note}


def _check_csp(value: str | None) -> dict[str, Any]:
    if not value:
        return {"header": "Content-Security-Policy", "present": False, "status": "fail", "note": "Missing -- no restriction on script/style/frame sources."}
    lowered = value.lower()
    status = "pass"
    note = "Present."
    if "unsafe-inline" in lowered or "unsafe-eval" in lowered:
        status = "warn"
        note = "Present, but allows 'unsafe-inline' or 'unsafe-eval', which weakens XSS protection."
    elif "default-src *" in lowered or "default-src: *" in lowered:
        status = "warn"
        note = "Present, but default-src * allows any source."
    return {"header": "Content-Security-Policy", "present": True, "status": status, "value": value, "note": note}


def _check_presence(name: str, value: str | None, missing_note: str) -> dict[str, Any]:
    if not value:
        return {"header": name, "present": False, "status": "fail", "note": missing_note}
    return {"header": name, "present": True, "status": "pass", "value": value, "note": "Present."}


def _grade(checks: list[dict[str, Any]]) -> str:
    points = sum(1 for c in checks if c["status"] == "pass") + 0.5 * sum(1 for c in checks if c["status"] == "warn")
    for threshold, letter in GRADE_THRESHOLDS:
        if points >= threshold:
            return letter
    return "F"


def _empty_result(url: str) -> dict[str, Any]:
    return {
        "ok": False,
        "url": normalize_url(url),
        "status_code": None,
        "response_time_ms": None,
        "final_url": None,
        "grade": None,
        "checks": [],
        "error": None,
    }


def check_security_headers(url: str, timeout: int = 10) -> dict[str, Any]:
    """Fetch a URL and grade its response security headers."""
    normalized = normalize_url(url)
    result = _empty_result(url)

    if not normalized:
        result["error"] = "Enter a URL or domain."
        return result
    if len(normalized) > MAX_URL_LENGTH:
        result["error"] = f"URL is longer than {MAX_URL_LENGTH} characters."
        return result
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        result["error"] = "Enter a valid HTTP or HTTPS URL."
        return result

    headers = {"User-Agent": "ITOpsToolkit/1.0 public-safe-checker"}
    started = time.perf_counter()
    response: requests.Response | None = None
    try:
        response = requests.get(normalized, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        response.close()
    except requests.exceptions.SSLError as exc:
        result["error"] = f"TLS/SSL error: {exc}"
        return result
    except requests.exceptions.Timeout:
        result["error"] = "HTTP request timed out."
        return result
    except requests.exceptions.ConnectionError as exc:
        result["error"] = f"Connection failed: {exc}"
        return result
    except requests.exceptions.RequestException as exc:
        result["error"] = f"HTTP request failed: {exc}"
        return result
    finally:
        if response is not None:
            response.close()

    h = response.headers
    checks = [
        _check_hsts(h.get("strict-transport-security")),
        _check_csp(h.get("content-security-policy")),
        _check_presence("X-Frame-Options", h.get("x-frame-options"), "Missing -- page can be embedded in a frame on any site (clickjacking risk)."),
        _check_presence("X-Content-Type-Options", h.get("x-content-type-options"), "Missing -- browsers may MIME-sniff responses, weakening content-type protections."),
        _check_presence("Referrer-Policy", h.get("referrer-policy"), "Missing -- full URLs (including query strings) may leak via the Referer header to other sites."),
        _check_presence("Permissions-Policy", h.get("permissions-policy"), "Missing -- no restriction on browser features (camera, geolocation, etc.) available to this page."),
    ]

    result.update(
        {
            "ok": True,
            "status_code": response.status_code,
            "response_time_ms": elapsed_ms,
            "final_url": response.url,
            "grade": _grade(checks),
            "checks": checks,
        }
    )
    return result
