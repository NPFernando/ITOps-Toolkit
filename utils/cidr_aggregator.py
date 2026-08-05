"""CIDR / IP range aggregation helpers."""

from __future__ import annotations

import ipaddress
from typing import Any

MAX_INPUT_LENGTH = 20_000
MAX_ENTRIES = 2_000


def aggregate_cidrs(raw_text: str) -> dict[str, Any]:
    """Parse a newline-separated list of IPs/CIDR blocks and return the minimal covering supernets."""
    result: dict[str, Any] = {"ok": False, "error": None, "input_count": 0, "output_count": 0, "networks": []}

    value = (raw_text or "").strip()
    if not value:
        result["error"] = "Enter one or more IP addresses or CIDR blocks, one per line."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    lines = [line.strip() for line in value.splitlines() if line.strip()]
    if len(lines) > MAX_ENTRIES:
        result["error"] = f"Enter no more than {MAX_ENTRIES:,} entries."
        return result

    networks = []
    for line in lines:
        entry = line if "/" in line else f"{line}/32" if ":" not in line else f"{line}/128"
        try:
            networks.append(ipaddress.ip_network(entry, strict=False))
        except ValueError as exc:
            result["error"] = f"Invalid entry {line!r}: {exc}"
            return result

    # collapse_addresses() requires uniform IP version; collapse each
    # version's group separately, then combine.
    ipv4_networks = [net for net in networks if net.version == 4]
    ipv6_networks = [net for net in networks if net.version == 6]
    collapsed = list(ipaddress.collapse_addresses(ipv4_networks)) if ipv4_networks else []
    collapsed += list(ipaddress.collapse_addresses(ipv6_networks)) if ipv6_networks else []
    collapsed.sort(key=lambda net: (net.version, int(net.network_address)))

    result.update(
        {
            "ok": True,
            "input_count": len(lines),
            "output_count": len(collapsed),
            "networks": [
                {"cidr": str(net), "total_addresses": net.num_addresses, "version": net.version} for net in collapsed
            ],
        }
    )
    return result
