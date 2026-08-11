"""Validate an IBAN (International Bank Account Number).

Checks structure (country-specific length) and the mod-97 checksum defined
in ISO 7064. Distinct from Luhn Checksum Validator, which implements a
different algorithm (used for card numbers, not bank accounts).
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 64

# Fixed total length (country code + check digits + BBAN) per ISO 13616,
# for every country that issues IBANs -- verified against the SWIFT IBAN
# registry. Not exhaustive of every ISO 3166 country (most don't use IBAN).
_COUNTRY_LENGTHS: dict[str, int] = {
    "AD": 24, "AE": 23, "AL": 28, "AT": 20, "AZ": 28, "BA": 20, "BE": 16, "BG": 22,
    "BH": 22, "BR": 29, "BY": 28, "CH": 21, "CR": 22, "CY": 28, "CZ": 24, "DE": 22,
    "DK": 18, "DO": 28, "EE": 20, "EG": 29, "ES": 24, "FI": 18, "FO": 18, "FR": 27,
    "GB": 22, "GE": 22, "GI": 23, "GL": 18, "GR": 27, "GT": 28, "HR": 21, "HU": 28,
    "IE": 22, "IL": 23, "IQ": 23, "IS": 26, "IT": 27, "JO": 30, "KW": 30, "KZ": 20,
    "LB": 28, "LC": 32, "LI": 21, "LT": 20, "LU": 20, "LV": 21, "LY": 25, "MC": 27,
    "MD": 24, "ME": 22, "MK": 19, "MR": 27, "MT": 31, "MU": 30, "NL": 18, "NO": 15,
    "PK": 24, "PL": 28, "PS": 29, "PT": 25, "QA": 29, "RO": 24, "RS": 22, "SA": 24,
    "SC": 31, "SE": 24, "SI": 19, "SK": 24, "SM": 27, "ST": 25, "SV": 28, "TL": 23,
    "TN": 24, "TR": 26, "UA": 29, "VA": 22, "VG": 24, "XK": 20,
}

_ALLOWED_CHARS_RE = re.compile(r"^[A-Z0-9]+$")


def validate_iban(raw: str) -> dict[str, Any]:
    """Validate an IBAN's structure and checksum."""
    result: dict[str, Any] = {"ok": False, "error": None, "valid": None}

    value = (raw or "").strip()
    if not value:
        result["error"] = "Enter an IBAN."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    iban = value.replace(" ", "").upper()
    if not _ALLOWED_CHARS_RE.match(iban):
        result["error"] = "IBAN must contain only letters and digits (spaces are ignored)."
        return result
    if len(iban) < 5:
        result["error"] = "IBAN is too short to contain a country code and check digits."
        return result

    country = iban[:2]
    check_digits = iban[2:4]
    if not country.isalpha():
        result["error"] = f"'{country}' is not a valid two-letter country code."
        return result
    if not check_digits.isdigit():
        result["error"] = f"Check digits must be numeric, got '{check_digits}'."
        return result
    if country not in _COUNTRY_LENGTHS:
        result["error"] = f"'{country}' is not a recognized IBAN country code."
        return result

    expected_length = _COUNTRY_LENGTHS[country]
    if len(iban) != expected_length:
        result["error"] = f"{country} IBANs must be {expected_length} characters, got {len(iban)}."
        return result

    rearranged = iban[4:] + iban[:4]
    numeric = "".join(str(int(char, 36)) for char in rearranged)
    is_valid = int(numeric) % 97 == 1

    result.update(
        {
            "ok": True,
            "valid": is_valid,
            "country": country,
            "check_digits": check_digits,
            "formatted": " ".join(iban[i : i + 4] for i in range(0, len(iban), 4)),
        }
    )
    return result
