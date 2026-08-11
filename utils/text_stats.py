"""Basic text statistics: word/character/sentence counts and word frequency.

No existing general-purpose text-stats tool in this app -- JSON Formatter's
stats are JSON-structure-specific, not applicable to plain prose or logs.

Sentence counting is a simple split on '.', '!', '?' runs -- an
approximation, not real NLP (it doesn't handle abbreviations like "Dr." or
decimal numbers specially). Good enough for a rough count, not a claim of
linguistic accuracy.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

MAX_INPUT_LENGTH = 50_000
TOP_WORDS_COUNT = 10

_WORD_PATTERN = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)*")
_SENTENCE_SPLIT = re.compile(r"[.!?]+")


def analyze_text(text: str) -> dict[str, Any]:
    """Compute word/character/sentence counts and the most frequent words in ``text``."""
    result: dict[str, Any] = {
        "ok": False,
        "error": None,
        "word_count": None,
        "char_count": None,
        "char_count_no_spaces": None,
        "sentence_count": None,
        "top_words": [],
    }

    if not (text or ""):
        result["error"] = "Paste text to analyze."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    words = _WORD_PATTERN.findall(text.lower())
    sentences = [s for s in _SENTENCE_SPLIT.split(text) if s.strip()]
    word_counts = Counter(words).most_common(TOP_WORDS_COUNT)

    result.update(
        {
            "ok": True,
            "word_count": len(words),
            "char_count": len(text),
            "char_count_no_spaces": len(re.sub(r"\s", "", text)),
            "sentence_count": len(sentences),
            "top_words": [{"word": word, "count": count} for word, count in word_counts],
        }
    )
    return result
