"""HTTP status and header inspection helpers."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse

import requests


MAX_URL_LENGTH = 2048
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
    }


def check_http_status(url: str, timeout: int = 10) -> dict[str, Any]:
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
    try:
        response = requests.get(
            normalized,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
            stream=True,
        )
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        response.close()
    except requests.exceptions.SSLError as exc:
        result["error"] = f"TLS/SSL error: {exc}"
        result["recommendations"].append("Check the certificate chain and hostname match.")
        return result
    except requests.exceptions.Timeout:
        result["error"] = "HTTP request timed out."
        result["recommendations"].append("Check network reachability and application response time.")
        return result
    except requests.exceptions.ConnectionError as exc:
        result["error"] = f"Connection failed: {exc}"
        result["recommendations"].append("Check DNS, firewall rules, listener ports, and service health.")
        return result
    except requests.exceptions.RequestException as exc:
        result["error"] = f"HTTP request failed: {exc}"
        return result
    finally:
        if response is not None:
            response.close()

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
        }
    )
    return result
