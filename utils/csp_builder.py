"""Build a Content-Security-Policy header value from directive/source-list pairs.

Distinct from Security Headers Checker (fetches a live URL and checks
whether a CSP is present/reasonable) -- this builds one locally, with no
network call. Known CSP keyword sources ('self', 'none', 'unsafe-inline',
'unsafe-eval', 'unsafe-hashes', 'strict-dynamic', 'report-sample') are
auto-quoted per the spec; anything else (a host, scheme, or nonce/hash) is
left unquoted, since CSP only quotes its own reserved keywords.
"""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 2_000

DIRECTIVES: tuple[str, ...] = (
    "default-src",
    "script-src",
    "style-src",
    "img-src",
    "font-src",
    "connect-src",
    "media-src",
    "object-src",
    "frame-src",
    "frame-ancestors",
    "base-uri",
    "form-action",
    "worker-src",
)

_KEYWORD_SOURCES = {
    "self",
    "none",
    "unsafe-inline",
    "unsafe-eval",
    "unsafe-hashes",
    "strict-dynamic",
    "report-sample",
}


def _format_source(source: str) -> str:
    return f"'{source}'" if source in _KEYWORD_SOURCES else source


def build_csp(directive_sources: dict[str, str]) -> dict[str, Any]:
    """Build a CSP header value from {directive: space-or-comma-separated sources}."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    clauses = []
    for directive, raw_sources in directive_sources.items():
        sources_text = (raw_sources or "").strip()
        if not sources_text:
            continue
        if directive not in DIRECTIVES:
            result["error"] = f"Unknown directive: {directive}."
            return result
        sources = [s for s in sources_text.replace(",", " ").split() if s]
        if "none" in sources and len(sources) > 1:
            result["error"] = f"{directive}: 'none' must be the only source if used."
            return result
        clauses.append(f"{directive} {' '.join(_format_source(s) for s in sources)}")

    if not clauses:
        result["error"] = "Enter at least one directive with sources."
        return result

    output = "; ".join(clauses) + ";"
    if len(output) > MAX_INPUT_LENGTH:
        result["error"] = f"Resulting header is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    result.update({"ok": True, "output": output})
    return result
