"""Build a copy-pasteable curl command from method/URL/headers/body.

The inverse of utils/webhook_tools.py's send_request() -- same validation
shape and the same parse_headers() helper, but assembles a shell command
instead of making a real HTTP request.
"""

from __future__ import annotations

import shlex
from typing import Any
from urllib.parse import urlparse

from utils.http_tools import MAX_URL_LENGTH
from utils.webhook_tools import ALLOWED_METHODS, MAX_BODY_LENGTH, MAX_HEADERS_LENGTH, parse_headers

BODY_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def build_curl_command(url: str, method: str, headers_text: str = "", body: str = "") -> dict[str, Any]:
    """Validate inputs and assemble a shell-safe `curl` command line."""
    result: dict[str, Any] = {"ok": False, "error": None, "command": None}

    url = (url or "").strip()
    method_upper = (method or "").strip().upper()

    if not url:
        result["error"] = "Enter a URL."
        return result
    if len(url) > MAX_URL_LENGTH:
        result["error"] = f"URL is longer than {MAX_URL_LENGTH} characters."
        return result
    parsed = urlparse(url)
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

    parts = ["curl", "-X", method_upper]
    for key, value in headers.items():
        parts += ["-H", f"{key}: {value}"]
    if body and method_upper in BODY_METHODS:
        parts += ["-d", body]
    parts.append(url)

    result["ok"] = True
    result["command"] = " ".join(shlex.quote(part) for part in parts)
    return result
