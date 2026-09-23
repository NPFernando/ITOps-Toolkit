"""Generic HTTP request tester (a lightweight webhook/API request tool)."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse

import requests

from utils.http_tools import MAX_URL_LENGTH, normalize_url
from utils.reliability import classify_http_status, diagnostics

ALLOWED_METHODS: tuple[str, ...] = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")
MAX_HEADERS_LENGTH = 4000
MAX_BODY_LENGTH = 20000
MAX_RESPONSE_BODY_PREVIEW = 20000
REQUEST_TIMEOUT = 15
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 0.3
RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


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
        **diagnostics(),
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
    response = None
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        result["attempts"] = attempt
        try:
            response = requests.request(
                method_upper,
                normalized_url,
                headers=headers,
                data=send_body,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            if response.status_code in RETRYABLE_STATUS_CODES and attempt < RETRY_ATTEMPTS:
                close = getattr(response, "close", None)
                if close:
                    close()
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            break
        except requests.exceptions.Timeout:
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            result["error"] = "Request timed out."
            result.update(diagnostics(error_code="timeout", failure_mode="transient", attempts=attempt, retryable=True))
            return result
        except requests.exceptions.SSLError:
            result["error"] = "TLS/SSL error while connecting to the endpoint."
            result.update(diagnostics(error_code="tls_error", failure_mode="persistent", attempts=attempt))
            return result
        except requests.exceptions.ConnectionError:
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue
            result["error"] = "Connection failed while reaching the endpoint."
            result.update(diagnostics(error_code="connection_error", failure_mode="transient", attempts=attempt, retryable=True))
            return result
        except requests.exceptions.RequestException:
            result["error"] = "Request failed before a response was received."
            result.update(diagnostics(error_code="request_error", failure_mode="persistent", attempts=attempt))
            return result

    if response is None:
        result["error"] = "Request failed before a response was received."
        result.update(diagnostics(error_code="request_error", failure_mode="persistent", attempts=result["attempts"]))
        return result

    try:
        elapsed_ms = round((time.perf_counter() - started) * 1000, 1)
        body_text = response.text or ""
        truncated = len(body_text) > MAX_RESPONSE_BODY_PREVIEW
        error_code, failure_mode, retryable = classify_http_status(response.status_code, RETRYABLE_STATUS_CODES)

        result.update(
            {
                "ok": response.status_code < 400,
                "status_code": response.status_code,
                "reason": response.reason,
                "response_time_ms": elapsed_ms,
                "response_headers": dict(response.headers),
                "response_body": body_text[:MAX_RESPONSE_BODY_PREVIEW],
                "response_body_truncated": truncated,
                **diagnostics(
                    error_code=None if response.status_code < 400 else error_code,
                    failure_mode=None if response.status_code < 400 else failure_mode,
                    attempts=result["attempts"],
                    retryable=retryable,
                ),
            }
        )
        return result
    finally:
        close = getattr(response, "close", None)
        if close:
            close()
