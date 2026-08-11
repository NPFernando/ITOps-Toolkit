"""Build or parse an HTTP Basic Authentication header (RFC 7617).

Distinct from Base64 Tool (generic encode/decode) and HTTP Header Parser
(parses a whole raw header block, not specifically this credential format).
"""

from __future__ import annotations

import base64
import binascii
from typing import Any

MAX_INPUT_LENGTH = 1_000


def build_basic_auth_header(username: str, password: str) -> dict[str, Any]:
    """Build an "Authorization: Basic ..." header value from a username/password."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    username = username or ""
    password = password or ""
    if not username:
        result["error"] = "Enter a username."
        return result
    if ":" in username:
        # RFC 7617: the first colon in "user-id:password" is the separator,
        # so a colon in the username would silently swallow part of it into
        # the password on decode.
        result["error"] = "Username must not contain a colon (:)."
        return result
    if len(username) + len(password) > MAX_INPUT_LENGTH:
        result["error"] = f"Combined username/password is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    encoded = base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
    result.update({"ok": True, "output": f"Basic {encoded}"})
    return result


def parse_basic_auth_header(header_value: str) -> dict[str, Any]:
    """Parse an "Authorization: Basic ..." header value back into a username/password."""
    result: dict[str, Any] = {"ok": False, "error": None, "username": None, "password": None}

    value = (header_value or "").strip()
    if not value:
        result["error"] = "Paste an Authorization header value."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    # Accept either the bare Base64 token or the full "Basic <token>" header.
    token = value[6:].strip() if value.lower().startswith("basic ") else value

    try:
        decoded = base64.b64decode(token, validate=True).decode("utf-8")
    except (binascii.Error, ValueError):
        result["error"] = "Not valid Base64."
        return result
    except UnicodeDecodeError:
        result["error"] = "Decoded bytes are not valid UTF-8 text."
        return result

    if ":" not in decoded:
        result["error"] = "Decoded value has no ':' separator -- not a valid Basic Auth credential."
        return result

    username, _, password = decoded.partition(":")
    result.update({"ok": True, "username": username, "password": password})
    return result
