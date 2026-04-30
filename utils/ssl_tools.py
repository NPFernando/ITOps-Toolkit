"""TLS certificate inspection helpers."""

from __future__ import annotations

import socket
import ssl
from datetime import UTC, datetime
from typing import Any

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain


def _name_parts(parts: tuple[tuple[tuple[str, str], ...], ...]) -> dict[str, str]:
    output: dict[str, str] = {}
    for group in parts:
        for key, value in group:
            output[key] = value
    return output


def _cert_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromtimestamp(ssl.cert_time_to_seconds(value), tz=UTC)


def _empty_result(domain: str, port: int) -> dict[str, Any]:
    return {
        "ok": False,
        "domain": domain,
        "port": port,
        "tls_status": "Unknown",
        "verification_ok": False,
        "subject": {},
        "issuer": {},
        "san_names": [],
        "valid_from": None,
        "valid_until": None,
        "days_remaining": None,
        "error": None,
    }


def get_certificate_info(domain: str, port: int = 443, timeout: int = 5) -> dict[str, Any]:
    """Open a TLS connection and return certificate details without persistence."""
    normalized = normalize_domain(domain)
    result = _empty_result(normalized, port)

    if not normalized:
        result["tls_status"] = "Invalid"
        result["error"] = "Enter a domain name."
        return result
    if len(normalized) > MAX_DOMAIN_LENGTH:
        result["tls_status"] = "Invalid"
        result["error"] = f"Domain is longer than {MAX_DOMAIN_LENGTH} characters."
        return result
    if port < 1 or port > 65535:
        result["tls_status"] = "Invalid"
        result["error"] = "Port must be between 1 and 65535."
        return result

    context = ssl.create_default_context()
    try:
        with socket.create_connection((normalized, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=normalized) as tls_sock:
                cert = tls_sock.getpeercert()
    except ssl.SSLCertVerificationError as exc:
        message = str(exc)
        result["tls_status"] = "Critical" if "expired" in message.lower() else "Warning"
        result["error"] = f"Certificate verification failed: {message}"
        return result
    except ssl.SSLError as exc:
        result["tls_status"] = "Critical"
        result["error"] = f"TLS connection failed: {exc}"
        return result
    except socket.timeout:
        result["tls_status"] = "Unknown"
        result["error"] = "TLS connection timed out."
        return result
    except OSError as exc:
        result["tls_status"] = "Unknown"
        result["error"] = f"Could not connect to TLS endpoint: {exc}"
        return result

    valid_from = _cert_time(cert.get("notBefore"))
    valid_until = _cert_time(cert.get("notAfter"))
    now = datetime.now(UTC)
    days_remaining = (valid_until - now).days if valid_until else None
    san_names = [
        value
        for key, value in cert.get("subjectAltName", [])
        if key.lower() in {"dns", "ip address"}
    ]

    result.update(
        {
            "ok": bool(days_remaining is None or days_remaining >= 0),
            "tls_status": "Critical"
            if days_remaining is not None and days_remaining < 0
            else "Warning"
            if days_remaining is not None and days_remaining < 30
            else "Healthy",
            "verification_ok": True,
            "subject": _name_parts(cert.get("subject", ())),
            "issuer": _name_parts(cert.get("issuer", ())),
            "san_names": san_names,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "days_remaining": days_remaining,
        }
    )
    return result
