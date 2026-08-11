"""Build or explain an HTTP Cache-Control header value.

Distinct from HTTP Header Parser (generic header block parsing, no
per-directive explanations) and Security Headers Checker (fetches a live
URL, doesn't build a header). Directive descriptions follow RFC 9111.
"""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 1_000

DIRECTIVE_DESCRIPTIONS: dict[str, str] = {
    "no-cache": "The response can be stored, but must be revalidated with the origin before each reuse.",
    "no-store": "The response must not be stored in any cache at all.",
    "must-revalidate": "Once stale, the cache must revalidate before reuse -- it cannot serve a stale copy even if disconnected from the origin.",
    "proxy-revalidate": "Like must-revalidate, but only applies to shared (proxy/CDN) caches, not private browser caches.",
    "public": "The response may be stored by any cache, even if it would normally be private (e.g. behind auth).",
    "private": "The response is specific to one user and must not be stored by shared caches (proxies/CDNs).",
    "immutable": "The response body will not change while still fresh -- the client can skip revalidation entirely until max-age expires.",
    "no-transform": "Caches/proxies must not modify the response body (e.g. image recompression).",
}
_NUMERIC_DIRECTIVES = ("max-age", "s-maxage", "stale-while-revalidate", "stale-if-error")


def build_cache_control(flags: list[str], max_age: int | None = None, s_maxage: int | None = None) -> dict[str, Any]:
    """Build a Cache-Control header value from selected flag directives and optional ages."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    unknown = [flag for flag in flags if flag not in DIRECTIVE_DESCRIPTIONS]
    if unknown:
        result["error"] = f"Unknown directive(s): {', '.join(unknown)}."
        return result
    if "public" in flags and "private" in flags:
        result["error"] = "public and private are mutually exclusive."
        return result
    if "no-store" in flags and max_age is not None:
        result["error"] = "no-store and max-age are contradictory -- no-store means don't cache at all."
        return result

    parts = list(flags)
    if max_age is not None:
        parts.append(f"max-age={max_age}")
    if s_maxage is not None:
        parts.append(f"s-maxage={s_maxage}")

    if not parts:
        result["error"] = "Select at least one directive."
        return result

    result.update({"ok": True, "output": ", ".join(parts)})
    return result


def explain_cache_control(header_value: str) -> dict[str, Any]:
    """Parse a Cache-Control header value and explain each directive."""
    result: dict[str, Any] = {"ok": False, "error": None, "directives": None}

    value = (header_value or "").strip()
    if not value:
        result["error"] = "Paste a Cache-Control header value."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    directives = []
    for raw_token in value.split(","):
        token = raw_token.strip()
        if not token:
            continue
        name, _, param = token.partition("=")
        name = name.strip().lower()
        param = param.strip()
        if name in DIRECTIVE_DESCRIPTIONS:
            directives.append({"directive": token, "description": DIRECTIVE_DESCRIPTIONS[name]})
        elif name in _NUMERIC_DIRECTIVES:
            unit = {"max-age": "the response is fresh", "s-maxage": "shared caches consider it fresh (overrides max-age for them)", "stale-while-revalidate": "a stale copy may still be served while revalidating in the background", "stale-if-error": "a stale copy may be served if revalidation fails (e.g. origin is down)"}[name]
            directives.append({"directive": token, "description": f"For {param or 'N'} seconds after the response, {unit}."})
        else:
            directives.append({"directive": token, "description": "Unrecognized directive."})

    if not directives:
        result["error"] = "No directives found."
        return result

    result.update({"ok": True, "directives": directives})
    return result
