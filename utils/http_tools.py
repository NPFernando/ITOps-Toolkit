"""HTTP status and header inspection helpers."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse

import requests

from utils.reliability import diagnostics


MAX_URL_LENGTH = 2048
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 0.3
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}
SELECTED_HEADERS = [
    "server",
    "content-type",
    "strict-transport-security",
    "x-frame-options",
    "content-security-policy",
]


def normalize_url(url: str) -> str:
    value = (url or "").strip()
    if value and "://" not in value:
        value = f"https://{value}"
    return value


def _empty_result(url: str) -> dict[str, Any]:
    return {
        "ok": False,
        "input_url": url,
        "url": normalize_url(url),
        "status_code": None,
        "reason": None,
        "response_time_ms": None,
        "final_url": None,
        "uses_https": False,
        "redirect_chain": [],
        "headers": {},
        "recommendations": [],
        "error": None,
        **diagnostics(provider="http"),
    }


def check_http_status(url: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict[str, Any]:
    """Check a URL using requests and return a safe serializable result."""
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
    for attempt in range(1, DEFAULT_RETRY_ATTEMPTS + 1):
        result["attempts"] = attempt
        try:
            response = requests.get(
                normalized,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
                stream=True,
            )
            if response.status_code in RETRYABLE_STATUS_CODES and attempt < DEFAULT_RETRY_ATTEMPTS:
                response.close()
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            break
        except requests.exceptions.SSLError:
            result["error"] = "TLS/SSL error while connecting to the endpoint."
            result["error_code"] = "tls_error"
            result["failure_mode"] = "persistent"
            result["duration_ms"] = round((time.perf_counter() - started) * 1000, 1)
            result["recommendations"].append("Check the certificate chain and hostname match.")
            return result
        except requests.exceptions.Timeout:
            if attempt < DEFAULT_RETRY_ATTEMPTS:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            result["error"] = f"HTTP request timed out after {DEFAULT_RETRY_ATTEMPTS} attempts."
            result["error_code"] = "timeout"
            result["failure_mode"] = "transient"
            result["retryable"] = True
            result["duration_ms"] = round((time.perf_counter() - started) * 1000, 1)
            result["recommendations"].append("Check network reachability and application response time.")
            return result
        except requests.exceptions.ConnectionError:
            if attempt < DEFAULT_RETRY_ATTEMPTS:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            result["error"] = f"Connection failed after {DEFAULT_RETRY_ATTEMPTS} attempts."
            result["error_code"] = "connection_error"
            result["failure_mode"] = "transient"
            result["retryable"] = True
            result["duration_ms"] = round((time.perf_counter() - started) * 1000, 1)
            result["recommendations"].append("Check DNS, firewall rules, listener ports, and service health.")
            return result
        except requests.exceptions.RequestException:
            result["error"] = "HTTP request failed before a response was received."
            result["error_code"] = "request_error"
            result["failure_mode"] = "persistent"
            result["duration_ms"] = round((time.perf_counter() - started) * 1000, 1)
            return result

    if response is None:
        result["error"] = "HTTP request failed before a response was received."
        result["error_code"] = "request_error"
        result["failure_mode"] = "persistent"
        result["duration_ms"] = round((time.perf_counter() - started) * 1000, 1)
        return result

    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)

    selected_headers = {
        key: response.headers.get(key, "")
        for key in SELECTED_HEADERS
        if response.headers.get(key)
    }
    final_url = response.url
    uses_https = urlparse(final_url).scheme == "https"
    redirect_chain = [
        {
            "status_code": item.status_code,
            "url": item.url,
            "location": item.headers.get("location", ""),
        }
        for item in response.history
    ]

    recommendations: list[str] = []
    if not uses_https:
        recommendations.append("Use HTTPS for the final URL.")
    if uses_https and "strict-transport-security" not in selected_headers:
        recommendations.append("Add the Strict-Transport-Security header.")
    if "x-frame-options" not in selected_headers:
        recommendations.append("Add X-Frame-Options or frame-ancestors in CSP.")
    if "content-security-policy" not in selected_headers:
        recommendations.append("Add a Content-Security-Policy header.")
    if response.status_code >= 500:
        recommendations.append("Investigate upstream service, gateway, or application errors.")
    elif response.status_code >= 400:
        recommendations.append("Confirm the URL path, authentication requirements, and routing.")

    try:
        error_code = None
        failure_mode = None
        retryable = False
        if response.status_code >= 400:
            error_code = f"http_{response.status_code}"
            failure_mode = "transient" if response.status_code in RETRYABLE_STATUS_CODES else "persistent"
            retryable = response.status_code in RETRYABLE_STATUS_CODES
        rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
        rate_limit_reset = response.headers.get("X-RateLimit-Reset")
        result.update(
            {
                "ok": response.status_code < 400,
                "status_code": response.status_code,
                "reason": response.reason,
                "response_time_ms": elapsed_ms,
                "final_url": final_url,
                "uses_https": uses_https,
                "redirect_chain": redirect_chain,
                "headers": selected_headers,
                "recommendations": recommendations,
                "error_code": error_code,
                "failure_mode": failure_mode,
                "retryable": retryable,
                "duration_ms": elapsed_ms,
                "provider": "http",
                "rate_limit_remaining": int(rate_limit_remaining) if rate_limit_remaining and rate_limit_remaining.isdigit() else None,
                "rate_limit_reset_seconds": (
                    max(int(rate_limit_reset) - int(time.time()), 0)
                    if rate_limit_reset and rate_limit_reset.isdigit()
                    else None
                ),
            }
        )
        return result
    finally:
        response.close()
