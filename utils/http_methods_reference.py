"""Static reference table of HTTP methods and their RFC 9110 properties.

Standalone from HTTP Status Checker/Reference -- methods and status codes
are different axes of the HTTP spec. Safe/idempotent/cacheable are the
three properties most often confused or gotten wrong in practice (e.g.
"PUT is idempotent" surprises people used to thinking only GET is safe).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HttpMethodEntry:
    method: str
    safe: bool
    idempotent: bool
    cacheable: bool
    description: str


HTTP_METHODS: tuple[HttpMethodEntry, ...] = (
    HttpMethodEntry("GET", True, True, True, "Retrieve a representation of the resource. Should have no side effects."),
    HttpMethodEntry("HEAD", True, True, True, "Like GET, but returns only headers, no body -- used to check existence/metadata cheaply."),
    HttpMethodEntry("OPTIONS", True, True, False, "Ask what methods/headers are allowed on a resource -- used by CORS preflight requests."),
    HttpMethodEntry("TRACE", True, True, False, "Echoes the received request back, for diagnostic loop-back testing. Rarely used; often disabled for security."),
    HttpMethodEntry("PUT", False, True, False, "Replace the resource entirely with the request body. Repeating it has the same effect as calling it once."),
    HttpMethodEntry("DELETE", False, True, False, "Remove the resource. Repeating it has the same end state (still deleted), even if the second call returns 404."),
    HttpMethodEntry("POST", False, False, False, "Submit data to be processed (e.g. create a new resource, trigger an action). Not idempotent -- repeating it can create duplicates. Cacheable only if the response carries explicit freshness info; treated as not cacheable by default."),
    HttpMethodEntry("PATCH", False, False, False, "Apply a partial modification to the resource. Not guaranteed idempotent, since a patch can be relative (e.g. \"increment by 1\")."),
    HttpMethodEntry("CONNECT", False, False, False, "Establish a tunnel to the server, typically for HTTPS through a proxy."),
)


def search_http_methods(query: str) -> tuple[HttpMethodEntry, ...]:
    """Filter HTTP_METHODS by method name or description (case-insensitive substring match)."""
    needle = (query or "").strip().lower()
    if not needle:
        return HTTP_METHODS
    return tuple(entry for entry in HTTP_METHODS if needle in entry.method.lower() or needle in entry.description.lower())
