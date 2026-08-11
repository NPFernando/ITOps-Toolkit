"""Parse, compare, and sort version strings per Semantic Versioning 2.0.0.

Uses the official regex and precedence rules published at semver.org
(item 11): numeric pre-release identifiers compare numerically, alphanumeric
identifiers compare lexically (ASCII order), a numeric identifier always has
lower precedence than an alphanumeric one, and a version with a pre-release
has lower precedence than the same version without one. Build metadata is
parsed but never affects precedence, per spec.
"""

from __future__ import annotations

import re
from functools import cmp_to_key
from typing import Any

MAX_INPUT_LENGTH = 20_000

# Official SemVer 2.0.0 regex, verified directly against the spec's own
# examples (https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string).
_SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def parse_semver(version: str) -> dict[str, Any]:
    """Parse a single version string into its SemVer components."""
    result: dict[str, Any] = {"ok": False, "error": None}

    value = (version or "").strip()
    if not value:
        result["error"] = "Enter a version string."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    match = _SEMVER_RE.match(value)
    if not match:
        result["error"] = f"'{value}' is not a valid SemVer 2.0.0 version."
        return result

    result.update(
        {
            "ok": True,
            "major": int(match["major"]),
            "minor": int(match["minor"]),
            "patch": int(match["patch"]),
            "prerelease": match["prerelease"],
            "buildmetadata": match["buildmetadata"],
        }
    )
    return result


def _prerelease_identifiers(prerelease: str | None) -> list[str] | None:
    return prerelease.split(".") if prerelease else None


def _compare_identifier(a: str, b: str) -> int:
    a_is_numeric, b_is_numeric = a.isdigit(), b.isdigit()
    if a_is_numeric and b_is_numeric:
        return (int(a) > int(b)) - (int(a) < int(b))
    if a_is_numeric != b_is_numeric:
        # Numeric identifiers always have lower precedence than alphanumeric.
        return -1 if a_is_numeric else 1
    return (a > b) - (a < b)


def compare_versions(parsed_a: dict[str, Any], parsed_b: dict[str, Any]) -> int:
    """Return -1, 0, or 1 per SemVer precedence rules for two parsed versions."""
    for field in ("major", "minor", "patch"):
        if parsed_a[field] != parsed_b[field]:
            return -1 if parsed_a[field] < parsed_b[field] else 1

    pre_a, pre_b = _prerelease_identifiers(parsed_a["prerelease"]), _prerelease_identifiers(parsed_b["prerelease"])
    if pre_a is None and pre_b is None:
        return 0
    if pre_a is None or pre_b is None:
        # A pre-release version has lower precedence than a normal version.
        return 1 if pre_a is None else -1

    for ident_a, ident_b in zip(pre_a, pre_b, strict=False):
        cmp = _compare_identifier(ident_a, ident_b)
        if cmp != 0:
            return cmp
    if len(pre_a) != len(pre_b):
        # A larger set of pre-release fields has higher precedence, if all
        # preceding identifiers are equal.
        return -1 if len(pre_a) < len(pre_b) else 1
    return 0


def sort_versions(versions: list[str], descending: bool = False) -> dict[str, Any]:
    """Parse and sort a list of version strings by SemVer precedence."""
    result: dict[str, Any] = {"ok": False, "error": None, "sorted": None}

    if not versions:
        result["error"] = "Enter at least one version string."
        return result

    parsed = []
    for raw in versions:
        parsed_version = parse_semver(raw)
        if not parsed_version["ok"]:
            result["error"] = parsed_version["error"]
            return result
        parsed.append((raw.strip(), parsed_version))

    parsed.sort(key=cmp_to_key(lambda a, b: compare_versions(a[1], b[1])), reverse=descending)
    result.update({"ok": True, "sorted": [raw for raw, _ in parsed]})
    return result
