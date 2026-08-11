"""Generate a new RSA key pair and a Certificate Signing Request (CSR) from subject fields.

The reverse of CSR Decoder (parses an existing CSR). Not for production key
management -- like RSA/SSH Key Pair Generator, this app has no way to
protect a private key once it's rendered to the browser; intended for
spinning up a quick test CSR during troubleshooting.
"""

from __future__ import annotations

from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

RSA_KEY_SIZES: tuple[int, ...] = (2048, 3072, 4096)

_NAME_OID_FIELDS: tuple[tuple[str, Any], ...] = (
    ("common_name", NameOID.COMMON_NAME),
    ("organization", NameOID.ORGANIZATION_NAME),
    ("organizational_unit", NameOID.ORGANIZATIONAL_UNIT_NAME),
    ("locality", NameOID.LOCALITY_NAME),
    ("state", NameOID.STATE_OR_PROVINCE_NAME),
    ("country", NameOID.COUNTRY_NAME),
)


def generate_csr(
    common_name: str,
    organization: str = "",
    organizational_unit: str = "",
    locality: str = "",
    state: str = "",
    country: str = "",
    san_domains: list[str] | None = None,
    rsa_key_size: int = 2048,
) -> dict[str, Any]:
    """Generate an RSA key pair and a CSR for the given subject fields."""
    result: dict[str, Any] = {"ok": False, "error": None, "private_key_pem": "", "csr_pem": ""}

    common_name = (common_name or "").strip()
    if not common_name:
        result["error"] = "Enter a Common Name (e.g. the domain the certificate is for)."
        return result
    if country and len(country) != 2:
        result["error"] = "Country must be a 2-letter code (e.g. US)."
        return result
    if rsa_key_size not in RSA_KEY_SIZES:
        result["error"] = f"Unsupported RSA key size. Choose one of: {', '.join(str(s) for s in RSA_KEY_SIZES)}."
        return result

    field_values = {
        "common_name": common_name,
        "organization": organization.strip(),
        "organizational_unit": organizational_unit.strip(),
        "locality": locality.strip(),
        "state": state.strip(),
        "country": country.strip().upper(),
    }
    attributes = [x509.NameAttribute(oid, field_values[field]) for field, oid in _NAME_OID_FIELDS if field_values[field]]

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=rsa_key_size)
    builder = x509.CertificateSigningRequestBuilder().subject_name(x509.Name(attributes))

    domains = [d.strip() for d in (san_domains or []) if d.strip()]
    if domains:
        builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName(d) for d in domains]), critical=False)

    csr = builder.sign(private_key, hashes.SHA256())

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    csr_pem = csr.public_bytes(serialization.Encoding.PEM)

    result.update({"ok": True, "private_key_pem": private_pem.decode(), "csr_pem": csr_pem.decode()})
    return result
