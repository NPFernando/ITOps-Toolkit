"""TLS certificate inspection helpers."""

from __future__ import annotations

import errno
import socket
import ssl
import time
from datetime import UTC, datetime
from typing import Any

from utils.dns_tools import MAX_DOMAIN_LENGTH, normalize_domain

# OpenSSL X509_V_ERR_* codes surfaced via ssl.SSLCertVerificationError.verify_code.
# Python's ssl module can't enumerate the full leaf-to-root chain on 3.11/3.12
# (SSLSocket.get_verified_chain() is 3.13+), so chain diagnosis is built from
# these verification-failure codes instead of walking the actual chain.
_CHAIN_DIAGNOSES: dict[int, tuple[str, str]] = {
    2: ("Missing intermediate", "Unable to build the issuer chain -- an intermediate certificate is likely missing."),
    9: ("Not yet valid", "The certificate's validity period has not started yet."),
    10: ("Expired", "The certificate has expired."),
    18: ("Self-signed", "The certificate is self-signed and not issued by a trusted CA."),
    19: ("Self-signed in chain", "A self-signed certificate was found in the chain, but it is not trusted."),
    20: ("Missing intermediate", "Unable to get the local issuer certificate -- the server is likely not sending its intermediate certificate(s)."),
    21: ("Missing intermediate", "Unable to verify the first certificate -- the chain is likely incomplete."),
    24: ("Untrusted root", "The root CA certificate is not trusted."),
    62: ("Hostname mismatch", "The certificate does not match the requested hostname."),
}
DEFAULT_TLS_TIMEOUT_SECONDS = 5
DEFAULT_TLS_RETRY_ATTEMPTS = 3
TLS_RETRY_BACKOFF_SECONDS = 0.25
_RETRYABLE_OS_ERRNOS = {
    errno.ECONNREFUSED,
    errno.ECONNRESET,
    errno.ETIMEDOUT,
    errno.EHOSTUNREACH,
    errno.ENETUNREACH,
}


def _retryable_connection_error(exc: OSError) -> bool:
    if isinstance(exc, socket.gaierror):
        return exc.errno == socket.EAI_AGAIN
    return exc.errno in _RETRYABLE_OS_ERRNOS


def diagnose_chain(verify_code: int | None, verify_message: str | None) -> tuple[str, str]:
    """Map an OpenSSL verify_code to a human-readable chain status and explanation."""
    if verify_code is None:
        return "Trusted", "The certificate chain verified successfully against the system trust store."
    if verify_code in _CHAIN_DIAGNOSES:
        return _CHAIN_DIAGNOSES[verify_code]
    return "Verification failed", verify_message or "The certificate chain failed verification for an unspecified reason."


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
        "chain_status": "Unknown",
        "chain_explanation": None,
        "subject": {},
        "issuer": {},
        "san_names": [],
        "valid_from": None,
        "valid_until": None,
        "days_remaining": None,
        "error": None,
    }


def get_certificate_info(domain: str, port: int = 443, timeout: int = DEFAULT_TLS_TIMEOUT_SECONDS) -> dict[str, Any]:
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
        cert: dict[str, Any] | None = None
        for attempt in range(1, DEFAULT_TLS_RETRY_ATTEMPTS + 1):
            try:
                with socket.create_connection((normalized, port), timeout=timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=normalized) as tls_sock:
                        cert = tls_sock.getpeercert()
                break
            except ssl.SSLCertVerificationError:
                raise
            except ssl.SSLError:
                raise
            except socket.timeout:
                if attempt < DEFAULT_TLS_RETRY_ATTEMPTS:
                    time.sleep(TLS_RETRY_BACKOFF_SECONDS * attempt)
                    continue
                result["tls_status"] = "Unknown"
                result["error"] = f"TLS connection timed out after {DEFAULT_TLS_RETRY_ATTEMPTS} attempts."
                return result
            except OSError as exc:
                if attempt < DEFAULT_TLS_RETRY_ATTEMPTS and _retryable_connection_error(exc):
                    time.sleep(TLS_RETRY_BACKOFF_SECONDS * attempt)
                    continue
                result["tls_status"] = "Unknown"
                result["error"] = f"Could not connect to TLS endpoint: {exc}"
                return result
        if cert is None:
            result["tls_status"] = "Unknown"
            result["error"] = "Could not read a certificate from the TLS endpoint."
            return result
    except ssl.SSLCertVerificationError as exc:
        message = str(exc)
        chain_status, chain_explanation = diagnose_chain(getattr(exc, "verify_code", None), getattr(exc, "verify_message", None))
        result["tls_status"] = "Critical" if "expired" in message.lower() else "Warning"
        result["chain_status"] = chain_status
        result["chain_explanation"] = chain_explanation
        result["error"] = f"Certificate verification failed: {message}"
        return result
    except ssl.SSLError as exc:
        result["tls_status"] = "Critical"
        result["error"] = f"TLS connection failed: {exc}"
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
            "chain_status": "Trusted",
            "chain_explanation": "The certificate chain verified successfully against the system trust store.",
            "subject": _name_parts(cert.get("subject", ())),
            "issuer": _name_parts(cert.get("issuer", ())),
            "san_names": san_names,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "days_remaining": days_remaining,
        }
    )
    return result
