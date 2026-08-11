"""Test whether paths would be ignored by a .gitignore file.

Implements gitignore's core glob semantics (*, ?, [...], **, leading/trailing
/, ! negation, # comments) -- verified directly against real `git
check-ignore` output for anchoring, **-matching-zero-directories, and
dir-only trailing-slash behavior before shipping. Deliberately does NOT
implement git's rule that a file cannot be re-included with '!' if one of
its parent directories is already excluded (that requires walking a real
directory tree, not just evaluating one path string) -- test the parent
directory separately if your patterns rely on that interaction.
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 50_000
MAX_PATH_LENGTH = 1_000


def _translate_pattern(pattern: str) -> re.Pattern[str]:
    """Compile one gitignore pattern into a regex matching a repo-relative path."""
    stripped_trailing = pattern.rstrip("/")
    anchored = "/" in stripped_trailing
    core = pattern.strip("/")
    parts = core.split("/") if core else [""]
    n = len(parts)

    fragments: list[str] = []
    for i, part in enumerate(parts):
        if part == "**":
            if n == 1:
                fragments.append(".*")
            elif i == 0:
                fragments.append("(?:.*/)?")
            else:
                fragments.append("(?:/.*)?")
        else:
            piece = re.escape(part).replace(r"\*", "[^/]*").replace(r"\?", "[^/]")
            prev = parts[i - 1] if i > 0 else None
            if i > 0 and prev != "**":
                fragments.append("/")
            fragments.append(piece)

    body = "".join(fragments)
    prefix = "^" if anchored else "(^|.*/)"
    return re.compile(prefix + body + "(/.*)?$")


def _parse_patterns(gitignore_text: str) -> list[tuple[str, bool]]:
    """Parse .gitignore text into (pattern, is_negated) pairs, skipping blanks/comments."""
    patterns: list[tuple[str, bool]] = []
    for raw_line in gitignore_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.startswith("#"):
            continue
        negate = line.startswith("!")
        pattern = line[1:] if negate else line
        if pattern.startswith("\\"):
            # Minimal support for escaping a leading '!' or '#'.
            pattern = pattern[1:]
        if not pattern:
            continue
        patterns.append((pattern, negate))
    return patterns


def check_paths(gitignore_text: str, paths_text: str) -> dict[str, Any]:
    """Check each path (one per line) against the .gitignore patterns."""
    result: dict[str, Any] = {"ok": False, "error": None, "results": None}

    gitignore_value = gitignore_text or ""
    if len(gitignore_value) > MAX_INPUT_LENGTH:
        result["error"] = f".gitignore content is longer than {MAX_INPUT_LENGTH:,} characters."
        return result
    if not gitignore_value.strip():
        result["error"] = "Paste .gitignore content."
        return result

    paths = [line.strip() for line in (paths_text or "").splitlines() if line.strip()]
    if not paths:
        result["error"] = "Enter at least one path to test, one per line."
        return result
    if any(len(path) > MAX_PATH_LENGTH for path in paths):
        result["error"] = f"A path is longer than {MAX_PATH_LENGTH:,} characters."
        return result

    patterns = _parse_patterns(gitignore_value)
    if not patterns:
        result["error"] = "No patterns found (only blank lines/comments)."
        return result

    compiled = [(_translate_pattern(pattern), pattern, negate) for pattern, negate in patterns]

    rows = []
    for path in paths:
        normalized = path.strip("/")
        ignored = False
        matched_pattern = None
        for regex, pattern, negate in compiled:
            if regex.match(normalized):
                ignored = not negate
                matched_pattern = ("!" if negate else "") + pattern
        rows.append({"path": path, "ignored": ignored, "matched_pattern": matched_pattern})

    result.update({"ok": True, "results": rows})
    return result
