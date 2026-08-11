"""Lint ~/.ssh/config content for structural mistakes.

Checks structure only (a directive appearing before any Host/Match block,
an empty Host block, a Host pattern repeated verbatim -- ssh applies only
the first matching value per keyword, so a later duplicate is silently
ignored) -- deliberately does NOT validate individual directive names
against a fixed list, since OpenSSH has ~100 valid ssh_config keywords and
an incomplete allowlist would cause false positives on valid but less
common ones.
"""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 50_000


def lint_ssh_config(text: str) -> dict[str, Any]:
    """Lint ssh_config-formatted text and return a list of line-numbered issues."""
    result: dict[str, Any] = {"ok": False, "error": None, "issues": []}

    if not (text or "").strip():
        result["error"] = "Paste ~/.ssh/config content to lint."
        return result

    result["ok"] = True
    issues: list[dict[str, Any]] = []

    current_block: tuple[int, str] | None = None
    current_block_directive_count = 0
    seen_host_patterns: dict[str, int] = {}

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        parts = stripped.split(None, 1)
        keyword = parts[0].lower()
        argument = parts[1] if len(parts) > 1 else ""

        if keyword in ("host", "match"):
            if current_block is not None and current_block_directive_count == 0:
                issues.append({"line": current_block[0], "message": f"'{current_block[1]}' block has no directives."})
            current_block = (line_number, stripped)
            current_block_directive_count = 0
            if keyword == "host":
                if not argument:
                    issues.append({"line": line_number, "message": "'Host' with no pattern."})
                elif argument in seen_host_patterns:
                    issues.append(
                        {
                            "line": line_number,
                            "message": f"Duplicate 'Host {argument}' (first seen on line {seen_host_patterns[argument]}) -- ssh only applies the first match's settings for each keyword.",
                        }
                    )
                else:
                    seen_host_patterns[argument] = line_number
            continue

        if current_block is None:
            issues.append({"line": line_number, "message": f"'{stripped}' appears before any Host/Match block."})
            continue

        current_block_directive_count += 1
        if not argument:
            issues.append({"line": line_number, "message": f"'{parts[0]}' has no value."})

    if current_block is not None and current_block_directive_count == 0:
        issues.append({"line": current_block[0], "message": f"'{current_block[1]}' block has no directives."})

    result["issues"] = issues
    return result
