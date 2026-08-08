"""Probe a host for which TLS protocol versions it accepts.

Similar in spirit to a lightweight SSL Labs check: connect once per protocol
version and report accepted/rejected. Scope is deliberately narrower than a
full scanner in two ways:

1. Only TLSv1.2 and TLSv1.3 are actually testable here. This environment's
   OpenSSL build has SSLv3/TLSv1.0/TLSv1.1 compiled out entirely -- verified
   directly: constructing an SSL context restricted to any of those three
   raises `[SSL: NO_PROTOCOLS_AVAILABLE]` before any network I/O happens,
   regardless of what the target server supports. Those three are reported
   as "not_testable", a status kept visually and textually distinct from
   "rejected" -- conflating "this environment can't test it" with "the
   server rejected it" would be actively misleading for a security tool.
   The not_testable check itself is done locally via an in-memory BIO
   handshake attempt, so it costs zero network round trips.
2. No per-cipher-suite enumeration. `SSLContext.set_ciphers()` has the same
   category of local-availability gap (e.g. RC4-SHA fails locally before any
   network attempt on this build), and maintaining a cipher-string list is a
   disproportionate maintenance burden for what this tool aims to be. The
   negotiated cipher for each successfully-accepted protocol is still
   reported, since it comes free from the handshake.
"""

from __future__ import annotations

import socket
import ssl
from typing import Any

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain

MAX_PORT = 65535

_PROTOCOL_VERSIONS: tuple[tuple[str, ssl.TLSVersion], ...] = (
    ("SSLv3", ssl.TLSVersion.SSLv3),
    ("TLSv1.0", ssl.TLSVersion.TLSv1),
    ("TLSv1.1", ssl.TLSVersion.TLSv1_1),
    ("TLSv1.2", ssl.TLSVersion.TLSv1_2),
    ("TLSv1.3", ssl.TLSVersion.TLSv1_3),
)


def _build_context(version: ssl.TLSVersion) -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.minimum_version = version
    context.maximum_version = version
    return context


def _is_locally_testable(context: ssl.SSLContext, hostname: str) -> bool:
    """Detect the NO_PROTOCOLS_AVAILABLE case with no network I/O."""
    try:
        in_bio = ssl.MemoryBIO()
        out_bio = ssl.MemoryBIO()
        sslobj = context.wrap_bio(in_bio, out_bio, server_hostname=hostname)
        try:
            sslobj.do_handshake()
        except ssl.SSLWantReadError:
            pass  # Expected: handshake needs real bytes from a real peer.
        return True
    except ssl.SSLError:
        return False


def _probe_version(name: str, version: ssl.TLSVersion, host: str, port: int, timeout: int) -> dict[str, Any]:
    context = _build_context(version)
    if not _is_locally_testable(context, host):
        return {"version": name, "status": "not_testable", "detail": "Not testable in this environment (protocol unsupported by the local TLS library)."}

    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=host) as tls_sock:
                cipher = tls_sock.cipher()
                detail = f"Negotiated cipher: {cipher[0]}." if cipher else "Accepted."
                return {"version": name, "status": "accepted", "detail": detail}
    except ssl.SSLError as exc:
        return {"version": name, "status": "rejected", "detail": f"Rejected by server: {exc}"}
    except socket.timeout:
        return {"version": name, "status": "connection_error", "detail": "Connection timed out."}
    except OSError as exc:
        return {"version": name, "status": "connection_error", "detail": f"Could not connect: {exc}"}


def scan_tls(host: str, port: int = 443, timeout: int = 5) -> dict[str, Any]:
    """Probe a host:port for accepted TLS protocol versions."""
    normalized = normalize_domain(host)
    result: dict[str, Any] = {"ok": False, "error": None, "host": normalized, "port": port, "results": []}

    if not normalized:
        result["error"] = "Enter a host name."
        return result
    if len(normalized) > MAX_DOMAIN_LENGTH:
        result["error"] = f"Host is longer than {MAX_DOMAIN_LENGTH} characters."
        return result
    if port < 1 or port > MAX_PORT:
        result["error"] = "Port must be between 1 and 65535."
        return result

    result["ok"] = True
    result["results"] = [_probe_version(name, version, normalized, port, timeout) for name, version in _PROTOCOL_VERSIONS]
    return result
