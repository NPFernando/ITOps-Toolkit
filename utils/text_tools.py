"""Text parsing, formatting, and decoding helpers."""

from __future__ import annotations

import base64
import binascii
import json
from datetime import UTC, datetime
from typing import Any

import jwt
from croniter import croniter


MAX_LOG_LENGTH = 20_000
MAX_JSON_LENGTH = 100_000


def validate_length(value: str, max_length: int, label: str) -> tuple[bool, str | None]:
    if len(value or "") > max_length:
        return False, f"{label} is longer than {max_length:,} characters."
    return True, None


def format_json_text(value: str, minify: bool = False) -> dict[str, Any]:
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

    if minify:
        result = json.dumps(parsed, separators=(",", ":"), ensure_ascii=False)
    else:
        result = json.dumps(parsed, indent=2, ensure_ascii=False)
    return {"ok": True, "error": None, "result": result, "parsed": parsed}


def encode_base64_text(value: str) -> str:
    return base64.b64encode((value or "").encode("utf-8")).decode("ascii")


def decode_base64_text(value: str) -> dict[str, Any]:
    try:
        decoded = base64.b64decode((value or "").encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        return {"ok": False, "error": f"Invalid Base64 input: {exc}", "result": None}
    return {"ok": True, "error": None, "result": decoded.decode("utf-8", errors="replace")}


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
