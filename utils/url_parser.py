"""Break a URL down into its component parts."""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlsplit

from utils.http_tools import MAX_URL_LENGTH, normalize_url


def parse_url(url: str) -> dict[str, Any]:
    """Split ``url`` into scheme, host, port, path, query params, and fragment."""
    result: dict[str, Any] = {
        "ok": False,
        "error": None,
        "scheme": None,
        "host": None,
        "port": None,
        "path": None,
        "query_params": [],
        "fragment": None,
    }

    normalized = normalize_url(url)
    if not normalized:
        result["error"] = "Enter a URL."
        return result
    if len(normalized) > MAX_URL_LENGTH:
        result["error"] = f"URL is longer than {MAX_URL_LENGTH} characters."
        return result

    split = urlsplit(normalized)
    if not split.hostname:
        result["error"] = "Could not parse a valid URL -- check the format."
        return result

    result.update(
        {
            "ok": True,
            "scheme": split.scheme,
            "host": split.hostname,
            "port": split.port,
            "path": split.path or "/",
            "query_params": [{"key": key, "value": value} for key, value in parse_qsl(split.query, keep_blank_values=True)],
            "fragment": split.fragment or None,
        }
    )
    return result
