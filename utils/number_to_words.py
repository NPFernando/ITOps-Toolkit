"""Spell out an integer in English words (short scale: thousand, million, billion...).

One direction only (number -> words), deliberately -- parsing loosely
formatted English text back into a number is ambiguous (hyphenation, "and"
placement, regional variants) in a way that can't be scoped honestly the
same way the forward direction can.
"""

from __future__ import annotations

from typing import Any

MAX_INPUT_LENGTH = 32
# 999 quintillion range -- comfortably past any value a 64-bit signed
# integer (the practical ceiling for "a number someone actually has") can
# hold, so nothing realistic gets truncated by running out of scale words.
MAX_MAGNITUDE = 999_999_999_999_999_999_999

_ONES = ("", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
_TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety")
_SCALES = ("", "thousand", "million", "billion", "trillion", "quadrillion", "quintillion")


def _three_digits_to_words(n: int) -> str:
    parts = []
    hundreds, remainder = divmod(n, 100)
    if hundreds:
        parts.append(f"{_ONES[hundreds]} hundred")
    if remainder:
        if remainder < 20:
            parts.append(_ONES[remainder])
        else:
            tens, ones = divmod(remainder, 10)
            word = _TENS[tens]
            if ones:
                word += f"-{_ONES[ones]}"
            parts.append(word)
    return " ".join(parts)


def number_to_words(value: str) -> dict[str, Any]:
    """Spell out an integer in English words."""
    result: dict[str, Any] = {"ok": False, "error": None, "output": None}

    text = (value or "").strip()
    if not text:
        result["error"] = "Enter an integer."
        return result
    if len(text) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    try:
        number = int(text)
    except ValueError:
        result["error"] = "Enter a whole number (no decimals)."
        return result

    if abs(number) > MAX_MAGNITUDE:
        result["error"] = f"Number is larger than this tool supports ({MAX_MAGNITUDE:,})."
        return result

    if number == 0:
        result.update({"ok": True, "output": "zero"})
        return result

    negative = number < 0
    n = abs(number)

    groups = []
    scale_index = 0
    while n > 0:
        n, group = divmod(n, 1000)
        if group:
            words = _three_digits_to_words(group)
            groups.append(f"{words} {_SCALES[scale_index]}".strip())
        scale_index += 1

    output = " ".join(reversed(groups))
    if negative:
        output = f"negative {output}"

    result.update({"ok": True, "output": output})
    return result
