"""Compare two .env files and show added/removed/changed keys.

Distinct from .env File Linter (checks one file for mistakes) and JSON/CSV
Diff (different formats). Parsing mirrors env_linter's conventions: skips
blank lines and comments, strips a leading "export ", and treats the first
"=" as the separator.
"""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 50_000


def _parse_env(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        working = stripped
        if working.startswith("export "):
            working = working[len("export ") :].lstrip()
        key, _, value = working.partition("=")
        key = key.strip()
        if key:
            values[key] = value.strip()
    return values


def diff_env(text_a: str, text_b: str) -> dict[str, Any]:
    """Compare two .env-formatted texts, returning added/removed/changed keys."""
    result: dict[str, Any] = {"ok": False, "error": None, "added": None, "removed": None, "changed": None, "unchanged_count": 0}

    if len(text_a or "") > MAX_INPUT_LENGTH or len(text_b or "") > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result
    if not (text_a or "").strip() or not (text_b or "").strip():
        result["error"] = "Paste both .env files to compare."
        return result

    env_a, env_b = _parse_env(text_a), _parse_env(text_b)
    if not env_a and not env_b:
        result["error"] = "No KEY=VALUE lines found in either file."
        return result

    keys_a, keys_b = set(env_a), set(env_b)
    added = sorted(keys_b - keys_a)
    removed = sorted(keys_a - keys_b)
    changed = sorted(key for key in keys_a & keys_b if env_a[key] != env_b[key])
    unchanged_count = len(keys_a & keys_b) - len(changed)

    result.update(
        {
            "ok": True,
            "added": [{"key": k, "value": env_b[k]} for k in added],
            "removed": [{"key": k, "value": env_a[k]} for k in removed],
            "changed": [{"key": k, "old": env_a[k], "new": env_b[k]} for k in changed],
            "unchanged_count": unchanged_count,
        }
    )
    return result
