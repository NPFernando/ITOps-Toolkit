"""Convert pasted text between CRLF, LF, and CR line endings."""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 100_000
TARGETS: tuple[str, ...] = ("CRLF", "LF", "CR")

_LINE_ENDINGS = {"CRLF": "\r\n", "LF": "\n", "CR": "\r"}


def _normalize_to_lf(text: str) -> str:
    # Order matters: collapse CRLF pairs first, then any remaining bare CR --
    # otherwise a CRLF pair would be double-converted into two newlines.
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _detect_style(text: str) -> str:
    has_crlf = "\r\n" in text
    without_crlf = text.replace("\r\n", "")
    has_bare_cr = "\r" in without_crlf
    has_lf = "\n" in without_crlf
    styles = {name for name, present in (("CRLF", has_crlf), ("CR", has_bare_cr), ("LF", has_lf)) if present}
    if len(styles) > 1:
        return "Mixed"
    if styles:
        return styles.pop()
    return "None (single line, no line breaks)"


def convert_line_endings(text: str, target: str) -> dict[str, Any]:
    """Convert ``text``'s line endings to ``target`` (CRLF/LF/CR)."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None, "detected_input_style": None}

    if not (text or ""):
        result["error"] = "Paste text to convert."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result
    if target not in TARGETS:
        result["error"] = f"Unknown target: {target}."
        return result

    normalized = _normalize_to_lf(text)
    output = normalized.replace("\n", _LINE_ENDINGS[target])

    result.update({"ok": True, "output": output, "detected_input_style": _detect_style(text)})
    return result
