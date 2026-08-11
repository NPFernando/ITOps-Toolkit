"""Generate fake test data (names, emails, usernames, phone numbers) for filling in forms/fixtures.

Synthetic data from small built-in name lists -- not a realistic
population sample, just enough variety to exercise form validation, UI
layouts, and test fixtures. Uses reserved example domains (example.com,
example.org, example.net -- IANA-reserved per RFC 2606, guaranteed to
never resolve to a real mailbox) rather than a real-looking domain.
"""

from __future__ import annotations

import random
from typing import Any

MAX_COUNT = 100

_FIRST_NAMES = (
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Priya", "Wei", "Fatima", "Hiroshi",
    "Aisha", "Diego", "Yuki", "Omar", "Elena", "Kwame",
)
_LAST_NAMES = (
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Nguyen", "Kim", "Patel", "Chen",
    "Okafor", "Kowalski", "Andersson", "Rossi", "Silva", "Yamamoto",
)
_EXAMPLE_DOMAINS = ("example.com", "example.org", "example.net")


def generate_test_data(count: int, seed: int | None = None) -> dict[str, Any]:
    """Generate ``count`` fake test records: full_name, email, username, phone."""
    result: dict[str, Any] = {"ok": False, "error": None, "records": None}

    if count < 1:
        result["error"] = "Enter a count of at least 1."
        return result
    if count > MAX_COUNT:
        result["error"] = f"Enter a count of at most {MAX_COUNT}."
        return result

    rng = random.Random(seed)
    records = []
    for _ in range(count):
        first, last = rng.choice(_FIRST_NAMES), rng.choice(_LAST_NAMES)
        username = f"{first.lower()}.{last.lower()}{rng.randint(1, 99)}"
        domain = rng.choice(_EXAMPLE_DOMAINS)
        # 555-0100 through 555-0199 is the only part of the 555 prefix
        # reserved for fictional use in North America (the rest of 555 is
        # a real, assignable exchange) -- guaranteed not to collide with a
        # real subscriber number.
        phone = f"555-01{rng.randint(0, 99):02d}"
        records.append(
            {
                "full_name": f"{first} {last}",
                "email": f"{username}@{domain}",
                "username": username,
                "phone": phone,
            }
        )

    result.update({"ok": True, "records": records})
    return result
