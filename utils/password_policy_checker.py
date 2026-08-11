"""Check a password against a configurable complexity policy.

Distinct from Password Strength Checker (measures entropy, a continuous
estimate) and Password Generator (creates new passwords) -- this checks
pass/fail compliance against explicit rules, the kind an org sets for its
users (e.g. "at least 12 characters, one digit, one symbol").
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 256

_UPPER_RE = re.compile(r"[A-Z]")
_LOWER_RE = re.compile(r"[a-z]")
_DIGIT_RE = re.compile(r"\d")
_SYMBOL_RE = re.compile(r"[^A-Za-z0-9\s]")
_WHITESPACE_RE = re.compile(r"\s")


def check_password_policy(
    password: str,
    min_length: int = 12,
    require_upper: bool = True,
    require_lower: bool = True,
    require_digit: bool = True,
    require_symbol: bool = True,
    disallow_whitespace: bool = True,
) -> dict[str, Any]:
    """Check ``password`` against the given policy, returning pass/fail per rule."""
    result: dict[str, Any] = {"ok": False, "error": None, "compliant": None, "rules": None}

    if not password:
        result["error"] = "Enter a password to check."
        return result
    if len(password) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result
    if min_length < 1:
        result["error"] = "Minimum length must be at least 1."
        return result

    rules = [{"rule": f"At least {min_length} characters", "passed": len(password) >= min_length}]
    if require_upper:
        rules.append({"rule": "Contains an uppercase letter", "passed": bool(_UPPER_RE.search(password))})
    if require_lower:
        rules.append({"rule": "Contains a lowercase letter", "passed": bool(_LOWER_RE.search(password))})
    if require_digit:
        rules.append({"rule": "Contains a digit", "passed": bool(_DIGIT_RE.search(password))})
    if require_symbol:
        rules.append({"rule": "Contains a symbol", "passed": bool(_SYMBOL_RE.search(password))})
    if disallow_whitespace:
        rules.append({"rule": "No whitespace characters", "passed": not _WHITESPACE_RE.search(password)})

    result.update({"ok": True, "compliant": all(r["passed"] for r in rules), "rules": rules})
    return result
