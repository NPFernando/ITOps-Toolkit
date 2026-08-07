"""Static reference data for HTTP status codes.

Standalone from the live HTTP Status Checker -- useful as a quick lookup
when a code shows up in a log rather than from a live check.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StatusEntry:
    code: int
    category: str
    name: str
    description: str


STATUSES: tuple[StatusEntry, ...] = (
    StatusEntry(100, "1xx Informational", "Continue", "The initial part of a request has been received and the client should continue."),
    StatusEntry(101, "1xx Informational", "Switching Protocols", "The server is switching protocols as requested by the client (e.g. to WebSocket)."),
    StatusEntry(200, "2xx Success", "OK", "The request succeeded."),
    StatusEntry(201, "2xx Success", "Created", "The request succeeded and a new resource was created."),
    StatusEntry(202, "2xx Success", "Accepted", "The request was accepted for processing, but processing is not complete."),
    StatusEntry(204, "2xx Success", "No Content", "The request succeeded but there is no content to return."),
    StatusEntry(206, "2xx Success", "Partial Content", "Only part of the resource was returned, matching a Range request header."),
    StatusEntry(301, "3xx Redirection", "Moved Permanently", "The resource has permanently moved to a new URL."),
    StatusEntry(302, "3xx Redirection", "Found", "The resource temporarily resides at a different URL."),
    StatusEntry(303, "3xx Redirection", "See Other", "The response can be found at a different URL using a GET request."),
    StatusEntry(304, "3xx Redirection", "Not Modified", "The cached version of the resource is still valid; no body is returned."),
    StatusEntry(307, "3xx Redirection", "Temporary Redirect", "Like 302, but the request method and body must not change."),
    StatusEntry(308, "3xx Redirection", "Permanent Redirect", "Like 301, but the request method and body must not change."),
    StatusEntry(400, "4xx Client Error", "Bad Request", "The server could not understand the request due to invalid syntax."),
    StatusEntry(401, "4xx Client Error", "Unauthorized", "Authentication is required and has failed or not been provided."),
    StatusEntry(403, "4xx Client Error", "Forbidden", "The client does not have access rights to the content, even if authenticated."),
    StatusEntry(404, "4xx Client Error", "Not Found", "The server cannot find the requested resource."),
    StatusEntry(405, "4xx Client Error", "Method Not Allowed", "The request method is known but not supported by the target resource."),
    StatusEntry(406, "4xx Client Error", "Not Acceptable", "No content matching the Accept headers was found."),
    StatusEntry(408, "4xx Client Error", "Request Timeout", "The server timed out waiting for the request."),
    StatusEntry(409, "4xx Client Error", "Conflict", "The request conflicts with the current state of the server."),
    StatusEntry(410, "4xx Client Error", "Gone", "The resource is permanently gone and no forwarding address is known."),
    StatusEntry(413, "4xx Client Error", "Payload Too Large", "The request body is larger than the server is willing to process."),
    StatusEntry(414, "4xx Client Error", "URI Too Long", "The request URI is longer than the server is willing to interpret."),
    StatusEntry(415, "4xx Client Error", "Unsupported Media Type", "The request body's media type is not supported by the server."),
    StatusEntry(422, "4xx Client Error", "Unprocessable Entity", "The request is well-formed but contains semantic errors (common in REST APIs)."),
    StatusEntry(425, "4xx Client Error", "Too Early", "The server is unwilling to risk processing a request that might be replayed."),
    StatusEntry(429, "4xx Client Error", "Too Many Requests", "The client has sent too many requests in a given time (rate limiting)."),
    StatusEntry(431, "4xx Client Error", "Request Header Fields Too Large", "The request's header fields are too large."),
    StatusEntry(451, "4xx Client Error", "Unavailable For Legal Reasons", "The resource is unavailable due to a legal demand (e.g. censorship)."),
    StatusEntry(500, "5xx Server Error", "Internal Server Error", "The server encountered an unexpected condition and could not fulfill the request."),
    StatusEntry(501, "5xx Server Error", "Not Implemented", "The server does not support the functionality required to fulfill the request."),
    StatusEntry(502, "5xx Server Error", "Bad Gateway", "The server, acting as a gateway or proxy, received an invalid response from the upstream server."),
    StatusEntry(503, "5xx Server Error", "Service Unavailable", "The server is not ready to handle the request, often due to overload or maintenance."),
    StatusEntry(504, "5xx Server Error", "Gateway Timeout", "The server, acting as a gateway or proxy, did not get a response in time from the upstream server."),
    StatusEntry(505, "5xx Server Error", "HTTP Version Not Supported", "The server does not support the HTTP protocol version used in the request."),
    StatusEntry(507, "5xx Server Error", "Insufficient Storage", "The server is unable to store the representation needed to complete the request."),
    StatusEntry(508, "5xx Server Error", "Loop Detected", "The server detected an infinite loop while processing the request."),
    StatusEntry(511, "5xx Server Error", "Network Authentication Required", "The client needs to authenticate to gain network access (common on captive portals)."),
)


def search_statuses(query: str) -> tuple[StatusEntry, ...]:
    """Filter STATUSES by code, category, name, or keyword (case-insensitive substring match)."""
    needle = (query or "").strip().lower()
    if not needle:
        return STATUSES
    return tuple(
        entry
        for entry in STATUSES
        if needle in str(entry.code)
        or needle in entry.category.lower()
        or needle in entry.name.lower()
        or needle in entry.description.lower()
    )
