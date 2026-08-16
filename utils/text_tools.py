"""Text parsing, formatting, and decoding helpers."""

from __future__ import annotations

import base64
import binascii
import json
import re
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote, quote_plus, unquote, unquote_plus

import jwt
from croniter import croniter


MAX_LOG_LENGTH = 20_000
MAX_JSON_LENGTH = 100_000
MAX_URL_LENGTH = 20_000
JWT_ENCODE_ALGORITHMS = ("HS256", "HS384", "HS512")


def validate_length(value: str, max_length: int, label: str) -> tuple[bool, str | None]:
    if len(value or "") > max_length:
        return False, f"{label} is longer than {max_length:,} characters."
    return True, None


def format_json_text(value: str, minify: bool = False, indent: int = 2) -> dict[str, Any]:
    ok, error = validate_length(value, MAX_JSON_LENGTH, "JSON")
    if not ok:
        return {"ok": False, "error": error, "result": None}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
            "line": exc.lineno,
            "column": exc.colno,
            "result": None,
        }
    except RecursionError:
        # json.loads recurses per nesting level; deeply nested input (still
        # well under MAX_JSON_LENGTH) can exceed Python's recursion limit.
        return {
            "ok": False,
            "error": "JSON is nested too deeply to parse.",
            "result": None,
        }

    if minify:
        result = json.dumps(parsed, separators=(",", ":"), ensure_ascii=False)
    else:
        result = json.dumps(parsed, indent=indent, ensure_ascii=False)
    return {"ok": True, "error": None, "result": result, "parsed": parsed}


def json_stats(parsed: Any) -> dict[str, Any]:
    """Compute type, top-level size, max nesting depth, and node count for parsed JSON.

    Walks iteratively (not recursively) so it can't hit Python's recursion
    limit on deeply nested input that already parsed successfully.
    """
    node_count = 0
    max_depth = 1
    stack: list[tuple[Any, int]] = [(parsed, 1)]
    while stack:
        node, depth = stack.pop()
        node_count += 1
        max_depth = max(max_depth, depth)
        if isinstance(node, dict):
            stack.extend((child, depth + 1) for child in node.values())
        elif isinstance(node, list):
            stack.extend((child, depth + 1) for child in node)

    if isinstance(parsed, dict):
        json_type, top_level_count = "object", len(parsed)
    elif isinstance(parsed, list):
        json_type, top_level_count = "array", len(parsed)
    else:
        json_type, top_level_count = type(parsed).__name__, None

    return {
        "type": json_type,
        "top_level_count": top_level_count,
        "max_depth": max_depth,
        "node_count": node_count,
    }


MAX_JSON_SEARCH_RESULTS = 200


def search_json_paths(parsed: Any, query: str) -> list[dict[str, Any]]:
    """Find keys or scalar values containing ``query`` (case-insensitive) and return their paths.

    Walks iteratively, capped at MAX_JSON_SEARCH_RESULTS matches, so a large
    document with a common search term can't produce an unbounded result list.
    """
    needle = (query or "").strip().lower()
    if not needle:
        return []

    matches: list[dict[str, Any]] = []
    stack: list[tuple[Any, str]] = [(parsed, "$")]
    while stack and len(matches) < MAX_JSON_SEARCH_RESULTS:
        node, path = stack.pop()
        if isinstance(node, dict):
            for key, child in node.items():
                child_path = f"{path}.{key}"
                if needle in str(key).lower():
                    matches.append({"path": child_path, "match": "key", "value": _json_preview(child)})
                    if len(matches) >= MAX_JSON_SEARCH_RESULTS:
                        break
                stack.append((child, child_path))
        elif isinstance(node, list):
            for index, child in enumerate(node):
                stack.append((child, f"{path}[{index}]"))
        else:
            if node is not None and needle in str(node).lower():
                matches.append({"path": path, "match": "value", "value": _json_preview(node)})

    return matches[:MAX_JSON_SEARCH_RESULTS]


def _json_preview(value: Any, max_length: int = 80) -> str:
    text = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)
    return text if len(text) <= max_length else f"{text[:max_length]}..."


def encode_base64_text(value: str) -> str:
    return base64.b64encode((value or "").encode("utf-8")).decode("ascii")


def decode_base64_text(value: str) -> dict[str, Any]:
    # Strips all whitespace, not just the ends -- base64.b64decode(validate=True)
    # rejects any embedded whitespace, but wrapped/multi-line base64 (the standard
    # `base64` CLI output format, or anything copy-pasted from a text file) is a
    # normal, valid input shape that would otherwise fail with a misleading error.
    cleaned = re.sub(r"\s+", "", value or "")
    try:
        decoded = base64.b64decode(cleaned.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        return {"ok": False, "error": f"Invalid Base64 input: {exc}", "result": None}
    return {"ok": True, "error": None, "result": decoded.decode("utf-8", errors="replace")}


def encode_url_text(value: str, plus_for_space: bool = False) -> dict[str, Any]:
    """Percent-encode ``value``. ``plus_for_space`` uses application/x-www-form-urlencoded rules."""
    ok, error = validate_length(value, MAX_URL_LENGTH, "Input")
    if not ok:
        return {"ok": False, "error": error, "result": None}
    encoder = quote_plus if plus_for_space else quote
    return {"ok": True, "error": None, "result": encoder(value or "", safe="")}


def decode_url_text(value: str, plus_for_space: bool = False) -> dict[str, Any]:
    """Percent-decode ``value``. ``plus_for_space`` treats literal ``+`` as a space."""
    ok, error = validate_length(value, MAX_URL_LENGTH, "Input")
    if not ok:
        return {"ok": False, "error": error, "result": None}
    decoder = unquote_plus if plus_for_space else unquote
    return {"ok": True, "error": None, "result": decoder(value or "", errors="replace")}


def datetime_from_timestamp(value: Any) -> str | None:
    if value is None:
        return None
    try:
        timestamp = int(value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(timestamp, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")


def decode_jwt_unverified(token: str) -> dict[str, Any]:
    token_value = (token or "").strip()
    if not token_value:
        return {"ok": False, "error": "Enter a JWT token.", "header": None, "payload": None}
    try:
        header = jwt.get_unverified_header(token_value)
        payload = jwt.decode(
            token_value,
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_aud": False,
                "verify_iat": False,
                "verify_iss": False,
            },
        )
    except jwt.PyJWTError as exc:
        return {"ok": False, "error": f"Could not decode JWT: {exc}", "header": None, "payload": None}

    return {
        "ok": True,
        "error": None,
        "header": header,
        "payload": payload,
        "expires_at": datetime_from_timestamp(payload.get("exp")),
        "issued_at": datetime_from_timestamp(payload.get("iat")),
        "issuer": payload.get("iss"),
        "audience": payload.get("aud"),
    }


def encode_jwt(payload_json: str, secret: str, algorithm: str) -> dict[str, Any]:
    """Build and sign a JWT from a JSON payload using an HMAC algorithm and shared secret.

    HMAC-only (HS256/HS384/HS512) -- asymmetric algorithms would need key-pair
    input, which is out of scope for a quick local testing tool.
    """
    result: dict[str, Any] = {"ok": False, "error": None, "token": None}
    if algorithm not in JWT_ENCODE_ALGORITHMS:
        result["error"] = f"Unsupported algorithm: {algorithm}."
        return result
    if not secret:
        result["error"] = "Enter a secret key."
        return result

    ok, error = validate_length(payload_json, MAX_JSON_LENGTH, "Payload")
    if not ok:
        result["error"] = error
        return result

    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        result["error"] = f"Invalid payload JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        return result
    if not isinstance(payload, dict):
        result["error"] = "Payload JSON must be an object."
        return result

    try:
        token = jwt.encode(payload, secret, algorithm=algorithm)
    except jwt.PyJWTError as exc:
        result["error"] = f"Could not encode JWT: {exc}"
        return result

    result.update({"ok": True, "token": token})
    return result


def _field_description(name: str, value: str) -> str:
    if value == "*":
        return f"every {name}"
    if value.startswith("*/"):
        return f"every {value[2:]} {name}s"
    if "," in value:
        return f"{name} values {value}"
    if "-" in value:
        return f"{name} range {value}"
    return f"{name} {value}"


def fallback_cron_description(expression: str) -> str:
    fields = expression.split()
    if len(fields) != 5:
        return "Use the common 5-field format: minute hour day-of-month month day-of-week."
    minute, hour, day_of_month, month, day_of_week = fields
    parts = [
        _field_description("minute", minute),
        _field_description("hour", hour),
        _field_description("day of month", day_of_month),
        _field_description("month", month),
        _field_description("day of week", day_of_week),
    ]
    return "Runs at " + ", ".join(parts) + "."


def describe_cron(expression: str) -> str:
    try:
        from cron_descriptor import ExpressionDescriptor  # type: ignore

        return str(ExpressionDescriptor(expression).get_description())
    except Exception:
        return fallback_cron_description(expression)


def explain_cron(expression: str, count: int = 5) -> dict[str, Any]:
    value = (expression or "").strip()
    if len(value.split()) != 5:
        return {
            "ok": False,
            "error": "Only common 5-field cron expressions are supported.",
            "description": fallback_cron_description(value),
            "next_runs": [],
        }
    if not croniter.is_valid(value):
        return {
            "ok": False,
            "error": "Cron expression is not valid.",
            "description": fallback_cron_description(value),
            "next_runs": [],
        }

    iterator = croniter(value, datetime.now())
    return {
        "ok": True,
        "error": None,
        "description": describe_cron(value),
        "next_runs": [iterator.get_next(datetime).strftime("%Y-%m-%d %H:%M:%S") for _ in range(count)],
    }


MAX_ICS_RUNS = 50


def _ics_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def cron_ics_export(expression: str, count: int = 10) -> dict[str, Any]:
    """Build a downloadable .ics calendar with one event per upcoming cron run time."""
    result: dict[str, Any] = {"ok": False, "error": None, "ics": None}
    value = (expression or "").strip()
    if len(value.split()) != 5 or not croniter.is_valid(value):
        result["error"] = "Enter a valid 5-field cron expression first."
        return result
    if not (1 <= count <= MAX_ICS_RUNS):
        result["error"] = f"Count must be between 1 and {MAX_ICS_RUNS}."
        return result

    now = datetime.now(UTC)
    iterator = croniter(value, now)
    summary = _ics_escape(f"Cron: {value}")
    stamp = now.strftime("%Y%m%dT%H%M%SZ")

    events = []
    for index in range(count):
        run_at = iterator.get_next(datetime)
        run_at_utc = run_at if run_at.tzinfo else run_at.replace(tzinfo=UTC)
        dtstart = run_at_utc.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
        events.append(
            "\r\n".join(
                [
                    "BEGIN:VEVENT",
                    f"UID:cron-{stamp}-{index}@itops-toolkit",
                    f"DTSTAMP:{stamp}",
                    f"DTSTART:{dtstart}",
                    f"SUMMARY:{summary}",
                    "END:VEVENT",
                ]
            )
        )

    ics = "\r\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//ITOps Toolkit//Cron Explainer//EN",
            "CALSCALE:GREGORIAN",
            *events,
            "END:VCALENDAR",
            "",
        ]
    )
    result.update({"ok": True, "ics": ics})
    return result
