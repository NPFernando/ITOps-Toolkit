"""Parse a pasted block of raw HTTP request/response headers.

Distinct from Security Headers Checker and HTTP Status Checker, both of
which fetch headers live from a URL -- this parses headers a user already
has in hand (from browser devtools, a support ticket, a `curl -v` output),
with no network call at all.
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 100_000

_REQUEST_OR_STATUS_LINE = re.compile(
    r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|TRACE|CONNECT)\s+\S+\s+HTTP/\d(\.\d)?$|^HTTP/\d(\.\d)?\s+\d{3}",
    re.IGNORECASE,
)

_HEADER_EXPLANATIONS: dict[str, str] = {
    "content-type": "The media type of the body.",
    "content-length": "The size of the body, in bytes.",
    "cache-control": "Caching directives for clients and intermediate caches.",
    "content-encoding": "Compression applied to the body (e.g. gzip, br).",
    "set-cookie": "Sets a cookie on the client.",
    "location": "Redirect target, used with 3xx status codes.",
    "strict-transport-security": "Forces HTTPS for future requests (HSTS).",
    "x-frame-options": "Controls whether the page can be embedded in a frame.",
    "content-security-policy": "Restricts which resources the page may load.",
    "x-content-type-options": "Prevents MIME-type sniffing (nosniff).",
    "referrer-policy": "Controls how much referrer information is sent.",
    "access-control-allow-origin": "CORS: which origins may read the response.",
    "authorization": "Credentials for authenticating the request.",
    "user-agent": "Identifies the client software making the request.",
    "server": "Identifies the server software handling the request.",
    "etag": "An opaque identifier for a specific version of the resource.",
    "vary": "Which request headers affect the cached response.",
    "connection": "Controls whether the connection stays open (keep-alive/close).",
    "transfer-encoding": "Encoding applied for transferring the body (e.g. chunked).",
    "date": "The date and time the message was generated.",
}


def parse_headers_block(text: str) -> dict[str, Any]:
    """Parse a pasted block of raw HTTP headers, with an optional leading request/status line."""
    result: dict[str, Any] = {"ok": False, "error": None, "request_line": None, "headers": []}

    value = (text or "").strip("\n")
    if not value.strip():
        result["error"] = "Paste a block of HTTP headers."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    lines = [line for line in value.splitlines() if line.strip()]
    request_line = None
    if lines and _REQUEST_OR_STATUS_LINE.match(lines[0].strip()):
        request_line = lines[0].strip()
        lines = lines[1:]

    headers: list[dict[str, str]] = []
    for line in lines:
        if ":" not in line:
            result["error"] = f"Could not parse line as 'Name: value': {line!r}"
            return result
        name, _, raw_value = line.partition(":")
        name = name.strip()
        value_stripped = raw_value.strip()
        headers.append({"name": name, "value": value_stripped, "explanation": _HEADER_EXPLANATIONS.get(name.lower(), "")})

    if not headers:
        result["error"] = "No headers found -- expected one 'Name: value' pair per line."
        return result

    result.update({"ok": True, "request_line": request_line, "headers": headers})
    return result
