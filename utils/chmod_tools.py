"""Convert between symbolic (rwxr-xr-x) and octal (755) Unix file permission notation."""

from __future__ import annotations

import re
from typing import Any

_PERM_TRIPLET = ("r", "w", "x")
_OCTAL_RE = re.compile(r"^[0-7]{3,4}$")
_SYMBOLIC_RE = re.compile(r"^[-dlbcps]?([r-][w-][xsS-])([r-][w-][xsS-])([r-][w-][xtT-])$")


def _triplet_to_symbolic(bits: int, special: bool, special_char: str) -> str:
    r = "r" if bits & 4 else "-"
    w = "w" if bits & 2 else "-"
    if special:
        x = special_char.lower() if bits & 1 else special_char.upper()
    else:
        x = "x" if bits & 1 else "-"
    return r + w + x


def octal_to_symbolic(value: str) -> dict[str, Any]:
    """Convert an octal permission string (e.g. "755", "0644", "4755") to symbolic notation."""
    result: dict[str, Any] = {"ok": False, "symbolic": "", "octal": "", "breakdown": [], "error": None}
    cleaned = (value or "").strip()
    if not cleaned:
        result["error"] = "Enter an octal permission (e.g. 755)."
        return result
    if not _OCTAL_RE.match(cleaned):
        result["error"] = "Enter 3 or 4 octal digits, each 0-7 (e.g. 755 or 4755)."
        return result

    special_digit = int(cleaned[0]) if len(cleaned) == 4 else 0
    owner_digit, group_digit, other_digit = (int(d) for d in cleaned[-3:])
    setuid, setgid, sticky = bool(special_digit & 4), bool(special_digit & 2), bool(special_digit & 1)

    owner = _triplet_to_symbolic(owner_digit, setuid, "s")
    group = _triplet_to_symbolic(group_digit, setgid, "s")
    other = _triplet_to_symbolic(other_digit, sticky, "t")

    result.update(
        {
            "ok": True,
            "symbolic": owner + group + other,
            "octal": cleaned,
            "breakdown": [
                {"who": "Owner", "value": owner, "digit": owner_digit},
                {"who": "Group", "value": group, "digit": group_digit},
                {"who": "Other", "value": other, "digit": other_digit},
            ],
            "setuid": setuid,
            "setgid": setgid,
            "sticky": sticky,
        }
    )
    return result


def symbolic_to_octal(value: str) -> dict[str, Any]:
    """Convert a symbolic permission string (e.g. "rwxr-xr-x", "-rwsr-xr-x") to octal notation."""
    result: dict[str, Any] = {"ok": False, "symbolic": "", "octal": "", "breakdown": [], "error": None}
    cleaned = (value or "").strip()
    if not cleaned:
        result["error"] = "Enter a symbolic permission (e.g. rwxr-xr-x)."
        return result
    match = _SYMBOLIC_RE.match(cleaned)
    if not match:
        result["error"] = "Enter 9 permission characters (e.g. rwxr-xr-x), optionally prefixed with a file-type character."
        return result

    owner, group, other = match.groups()
    owner_digit, owner_setuid = _symbolic_triplet_to_digit(owner, "s")
    group_digit, group_setgid = _symbolic_triplet_to_digit(group, "s")
    other_digit, other_sticky = _symbolic_triplet_to_digit(other, "t")

    octal_digits = "".join(str(d) for d in (owner_digit, group_digit, other_digit))
    special_digit = (4 if owner_setuid else 0) + (2 if group_setgid else 0) + (1 if other_sticky else 0)
    octal = (str(special_digit) if special_digit else "") + octal_digits

    result.update(
        {
            "ok": True,
            "symbolic": owner + group + other,
            "octal": octal,
            "breakdown": [
                {"who": "Owner", "value": owner, "digit": owner_digit},
                {"who": "Group", "value": group, "digit": group_digit},
                {"who": "Other", "value": other, "digit": other_digit},
            ],
            "setuid": owner_setuid,
            "setgid": group_setgid,
            "sticky": other_sticky,
        }
    )
    return result


def _symbolic_triplet_to_digit(triplet: str, special_char: str) -> tuple[int, bool]:
    r, w, x = triplet[0], triplet[1], triplet[2]
    digit = (4 if r == "r" else 0) + (2 if w == "w" else 0)
    lower, upper = special_char.lower(), special_char.upper()
    if x in (lower, "x"):
        digit += 1
    special = x in (lower, upper)
    return digit, special
