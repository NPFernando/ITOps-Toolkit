"""Check whether any of a list of CIDR blocks/IPs overlap.

Complements CIDR Aggregator (which merges/collapses ranges) and Subnet
Calculator (which describes a single range) -- this flags overlap between
separately-entered ranges, a common pre-flight check before allocating a
new subnet block.
"""

from __future__ import annotations

import ipaddress
from typing import Any

MAX_INPUT_LENGTH = 20_000
MAX_ENTRIES = 500  # O(n^2) pairwise comparison -- kept smaller than CIDR Aggregator's cap


def check_cidr_overlaps(raw_text: str) -> dict[str, Any]:
    """Parse a newline-separated list of IPs/CIDR blocks and report any overlapping pairs."""
    result: dict[str, Any] = {"ok": False, "error": None, "input_count": 0, "overlaps": [], "has_overlaps": False}

    value = (raw_text or "").strip()
    if not value:
        result["error"] = "Enter two or more IP addresses or CIDR blocks, one per line."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if len(lines) > MAX_ENTRIES:
        result["error"] = f"Enter no more than {MAX_ENTRIES:,} entries."
        return result
    if len(lines) < 2:
        result["error"] = "Enter at least two entries to check for overlap."
        return result

    networks = []
    for line in lines:
        entry = line if "/" in line else f"{line}/32" if ":" not in line else f"{line}/128"
        try:
            networks.append((line, ipaddress.ip_network(entry, strict=False)))
        except ValueError as exc:
            result["error"] = f"Invalid entry {line!r}: {exc}"
            return result

    overlaps: list[dict[str, str]] = []
    for i in range(len(networks)):
        label_a, net_a = networks[i]
        for j in range(i + 1, len(networks)):
            label_b, net_b = networks[j]
            if net_a.version == net_b.version and net_a.overlaps(net_b):
                overlaps.append({"a": label_a, "b": label_b})

    result.update({"ok": True, "input_count": len(lines), "overlaps": overlaps, "has_overlaps": bool(overlaps)})
    return result
