"""Estimate a password's entropy from character-set diversity and length.

Distinct from Password Generator (which creates new passwords, not scores
existing ones). Deliberately scoped to a straightforward character-pool
entropy estimate, not a dictionary/pattern-based cracking-time model --
that would need an external wordlist/library this app doesn't have, and
this measure is honest about what it actually checks (character diversity,
not whether the password is a known-common one).
"""

from __future__ import annotations

import math
from typing import Any

MAX_INPUT_LENGTH = 128

_SYMBOL_POOL_SIZE = 32  # common printable ASCII symbols, not an exhaustive count

_STRENGTH_BUCKETS: tuple[tuple[float, str], ...] = (
    (28, "Very weak"),
    (36, "Weak"),
    (60, "Reasonable"),
    (128, "Strong"),
)
_STRONGEST_LABEL = "Very strong"


def _pool_size(password: str) -> int:
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(not c.isalnum() for c in password):
        pool += _SYMBOL_POOL_SIZE
    return pool


def _strength_label(entropy_bits: float) -> str:
    for threshold, label in _STRENGTH_BUCKETS:
        if entropy_bits < threshold:
            return label
    return _STRONGEST_LABEL


def estimate_entropy(password: str) -> dict[str, Any]:
    """Estimate entropy (bits) for ``password`` from its character-set diversity and length."""
    result: dict[str, Any] = {"ok": False, "error": None, "entropy_bits": None, "pool_size": None, "strength_label": None}

    if not password:
        result["error"] = "Enter a password to check."
        return result
    if len(password) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    pool_size = _pool_size(password)
    entropy_bits = len(password) * math.log2(pool_size) if pool_size > 0 else 0.0

    result.update(
        {
            "ok": True,
            "entropy_bits": round(entropy_bits, 1),
            "pool_size": pool_size,
            "strength_label": _strength_label(entropy_bits),
        }
    )
    return result
