"""Generic HTTP request tester (a lightweight webhook/API request tool)."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse

import requests

from utils.http_tools import MAX_URL_LENGTH, normalize_url

ALLOWED_METHODS: tuple[str, ...] = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
MAX_HEADERS_LENGTH = 4000
MAX_BODY_LENGTH = 20000
MAX_RESPONSE_BODY_PREVIEW = 20000
REQUEST_TIMEOUT = 15


def parse_headers(raw_text: str) -> tuple[dict[str, str], str | None]:
    """Parse "Key: Value" lines into a headers dict. Returns (headers, error)."""
    headers: dict[str, str] = {}
    for line_number, line in enumerate((raw_text or "").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            return {}, f"Line {line_number} is not in 'Key: Value' format."
        key, value = stripped.split(":", 1)
        key = key.strip()
        if not key:
            return {}, f"Line {line_number} has an empty header name."
        headers[key] = value.strip()
    return headers, None


def _empty_result(url: str, method: str) -> dict[str, Any]:
    return {
        "ok": False,
        "url": url,
        "method": method,
        "status_code": None,
        "reason": None,
        "response_time_ms": None,
        "response_headers": {},
        "response_body": None,
        "response_body_truncated": False,
        "error": None,
    }


def send_request(url: str, method: str, headers_text: str = "", body: str = "") -> dict[str, Any]:
    """Send a single HTTP request with custom method/headers/body and return a safe result envelope."""
    normalized_url = normalize_url(url)
    method_upper = (method or "").strip().upper()
    result = _empty_result(normalized_url, method_upper)

    if not normalized_url:
        result["error"] = "Enter a URL."
        return result
    if len(normalized_url) > MAX_URL_LENGTH:
        result["error"] = f"URL is longer than {MAX_URL_LENGTH} characters."
        return result
    parsed = urlparse(normalized_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        result["error"] = "Enter a valid HTTP or HTTPS URL."
        return result
    if method_upper not in ALLOWED_METHODS:
        result["error"] = f"Method must be one of: {', '.join(ALLOWED_METHODS)}."
        return result
    if len(headers_text or "") > MAX_HEADERS_LENGTH:
        result["error"] = f"Headers are longer than {MAX_HEADERS_LENGTH} characters."
        return result
    if len(body or "") > MAX_BODY_LENGTH:
        result["error"] = f"Body is longer than {MAX_BODY_LENGTH} characters."
        return result

    headers, header_error = parse_headers(headers_text)
    if header_error:
        result["error"] = header_error
        return result
    headers.setdefault("User-Agent", "ITOpsToolkit/1.0 public-safe-checker")

    send_body = body if method_upper in {"POST", "PUT", "PATCH", "DELETE"} and body else None

    started = time.perf_counter()
    try:
        response = requests.request(
            method_upper,
            normalized_url,
            headers=headers,
            data=send_body,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
    except requests.exceptions.Timeout:
        result["error"] = "Request timed out."
        return result
    except requests.exceptions.SSLError as exc:
        result["error"] = f"TLS/SSL error: {exc}"
        return result
    except requests.exceptions.ConnectionError as exc:
        result["error"] = f"Connection failed: {exc}"
        return result
    except requests.exceptions.RequestException as exc:
        result["error"] = f"Request failed: {exc}"
        return result

    elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
    body_text = response.text or ""
    truncated = len(body_text) > MAX_RESPONSE_BODY_PREVIEW

    result.update(
        {
            "ok": response.status_code < 400,
            "status_code": response.status_code,
            "reason": response.reason,
            "response_time_ms": elapsed_ms,
            "response_headers": dict(response.headers),
            "response_body": body_text[:MAX_RESPONSE_BODY_PREVIEW],
            "response_body_truncated": truncated,
        }
    )
    return result
