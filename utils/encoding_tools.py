"""Detect a text file's character encoding and convert it to UTF-8.

Uses charset-normalizer (already installed as a transitive dependency of
requests) for statistical charset detection. Byte-level ambiguity between
similar 8-bit encodings (e.g. cp1250 vs latin-1) is an inherent limitation
of statistical detection, not something this tool can resolve with
certainty -- the reported confidence reflects that.
"""

from __future__ import annotations

from typing import Any

from charset_normalizer import from_bytes

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB, generous for a text file
PREVIEW_CHARS = 500


def detect_encoding(data: bytes) -> dict[str, Any]:
    """Detect the most likely character encoding of ``data``."""
    result: dict[str, Any] = {"ok": False, "error": None, "encoding": None, "confidence": None, "preview": None, "size_bytes": len(data)}

    if not data:
        result["error"] = "Upload a file to detect its encoding."
        return result
    if len(data) > MAX_FILE_SIZE_BYTES:
        result["error"] = f"File is larger than {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
        return result

    matches = from_bytes(data)
    best = matches.best()
    if best is None:
        result["error"] = "Could not confidently detect an encoding for this file -- it may be binary."
        return result

    decoded = str(best)
    result.update(
        {
            "ok": True,
            "encoding": best.encoding,
            "confidence": round((1 - best.chaos) * 100, 1),
            "preview": decoded[:PREVIEW_CHARS],
        }
    )
    return result


def convert_to_utf8(data: bytes) -> dict[str, Any]:
    """Detect ``data``'s encoding and re-encode its content as UTF-8."""
    result: dict[str, Any] = {"ok": False, "error": None, "encoding": None, "utf8_text": None}

    detected = detect_encoding(data)
    if not detected["ok"]:
        result["error"] = detected["error"]
        return result

    matches = from_bytes(data)
    best = matches.best()
    result.update({"ok": True, "encoding": best.encoding, "utf8_text": str(best)})
    return result
