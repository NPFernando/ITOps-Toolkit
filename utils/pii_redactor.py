"""Redact common sensitive-looking patterns (emails, phone numbers, IPv4s, credit card-looking
numbers, US SSNs) from pasted text before sharing it in a ticket, log, or chat.

Regex-based heuristics, not a real PII detector -- deliberately disclosed as
such (like Password Strength Checker's entropy-only scope). Will miss
context-dependent PII (a bare name, an address) and can false-positive on
numbers that only look like a credit card or SSN. All patterns are matched
in a single combined pass so overlapping candidates (e.g. a 16-digit
sequence that also happens to contain a valid-looking phone substring)
each get redacted exactly once, not double-processed.
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 200_000

_PATTERNS: dict[str, str] = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "ipv4": r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b",
    "phone": r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "credit_card": r"\b(?:\d[ -]?){13,19}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
}

LABELS: dict[str, str] = {
    "email": "Email addresses",
    "ipv4": "IPv4 addresses",
    "phone": "Phone numbers",
    "credit_card": "Credit card-looking numbers",
    "ssn": "US SSNs (###-##-####)",
}

# credit_card's pattern is a broad, greedy 13-19-digit run, so it must be
# tried last -- otherwise it could swallow a more specific SSN/phone match
# that happens to sit inside a longer digit sequence.
_PRIORITY_ORDER = ("email", "ipv4", "ssn", "phone", "credit_card")


def redact(text: str, enabled_types: list[str]) -> dict[str, Any]:
    """Redact the selected PII types from ``text``, returning the result and a per-type count."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None, "counts": None}

    value = text or ""
    if not value:
        result["error"] = "Paste some text."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    unknown = [t for t in enabled_types if t not in _PATTERNS]
    if unknown:
        result["error"] = f"Unknown type(s): {', '.join(unknown)}."
        return result
    if not enabled_types:
        result["error"] = "Select at least one type to redact."
        return result

    ordered = [t for t in _PRIORITY_ORDER if t in enabled_types]
    combined = re.compile("|".join(f"(?P<{t}>{_PATTERNS[t]})" for t in ordered))

    counts: dict[str, int] = dict.fromkeys(enabled_types, 0)

    def _replace(match: re.Match[str]) -> str:
        matched_type = match.lastgroup
        counts[matched_type] += 1
        return f"[REDACTED_{matched_type.upper()}]"

    output = combined.sub(_replace, value)
    result.update({"ok": True, "output": output, "counts": counts})
    return result
