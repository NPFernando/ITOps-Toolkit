"""Static reference table of JWT claims.

Standalone from JWT Decoder/Encoder -- useful when you just need to
remember what a claim name means without decoding a real token. The
registered claims are defined in RFC 7519 SS4.1; the rest are widely-used
public/private conventions (e.g. OpenID Connect), not part of the RFC --
marked accordingly so this doesn't imply a false standardization.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClaimEntry:
    claim: str
    name: str
    category: str
    description: str


JWT_CLAIMS: tuple[ClaimEntry, ...] = (
    ClaimEntry("iss", "Issuer", "Registered (RFC 7519)", "Identifies the principal that issued the JWT."),
    ClaimEntry("sub", "Subject", "Registered (RFC 7519)", "Identifies the principal that is the subject of the JWT (e.g. a user ID)."),
    ClaimEntry("aud", "Audience", "Registered (RFC 7519)", "Identifies the recipient(s) the JWT is intended for."),
    ClaimEntry("exp", "Expiration Time", "Registered (RFC 7519)", "Unix timestamp after which the JWT must be rejected."),
    ClaimEntry("nbf", "Not Before", "Registered (RFC 7519)", "Unix timestamp before which the JWT must not be accepted."),
    ClaimEntry("iat", "Issued At", "Registered (RFC 7519)", "Unix timestamp when the JWT was issued."),
    ClaimEntry("jti", "JWT ID", "Registered (RFC 7519)", "Unique identifier for the JWT, used to prevent replay."),
    ClaimEntry("scope", "Scope", "Common (OAuth 2.0)", "Space-separated list of granted permissions/scopes. Not in RFC 7519, but near-universal in OAuth 2.0 access tokens."),
    ClaimEntry("client_id", "Client ID", "Common (OAuth 2.0)", "Identifier of the OAuth client the token was issued to."),
    ClaimEntry("name", "Full Name", "Common (OpenID Connect)", "The subject's full display name."),
    ClaimEntry("given_name", "Given Name", "Common (OpenID Connect)", "The subject's first/given name."),
    ClaimEntry("family_name", "Family Name", "Common (OpenID Connect)", "The subject's last/family name."),
    ClaimEntry("email", "Email", "Common (OpenID Connect)", "The subject's email address."),
    ClaimEntry("email_verified", "Email Verified", "Common (OpenID Connect)", "Whether the subject's email address has been verified."),
    ClaimEntry("picture", "Picture URL", "Common (OpenID Connect)", "URL of the subject's profile picture."),
    ClaimEntry("roles", "Roles", "Common (private claim)", "Application-defined roles assigned to the subject. Not standardized -- the exact key varies by provider (roles, role, groups...)."),
    ClaimEntry("azp", "Authorized Party", "Common (OpenID Connect)", "The client the ID token was issued to, when it differs from aud."),
    ClaimEntry("at_hash", "Access Token Hash", "Common (OpenID Connect)", "Hash of the access token, letting the client validate it matches the ID token."),
)


def search_jwt_claims(query: str) -> tuple[ClaimEntry, ...]:
    """Filter JWT_CLAIMS by claim key, name, category, or description (case-insensitive substring match)."""
    needle = (query or "").strip().lower()
    if not needle:
        return JWT_CLAIMS
    return tuple(
        entry
        for entry in JWT_CLAIMS
        if needle in entry.claim.lower()
        or needle in entry.name.lower()
        or needle in entry.category.lower()
        or needle in entry.description.lower()
    )
