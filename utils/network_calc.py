"""IPv4/IPv6 subnet calculator helpers."""

from __future__ import annotations

import ipaddress
from typing import Any

MAX_INPUT_LENGTH = 128


def calculate_subnet(cidr_text: str) -> dict[str, Any]:
    """Parse a CIDR string (or bare IP, treated as a /32 or /128) and return subnet details."""
    value = (cidr_text or "").strip()
    result: dict[str, Any] = {
        "ok": False,
        "input": cidr_text,
        "version": None,
        "network": None,
        "netmask": None,
        "wildcard_mask": None,
        "prefix_length": None,
        "broadcast": None,
        "first_host": None,
        "last_host": None,
        "total_addresses": None,
        "usable_hosts": None,
        "is_private": None,
        "error": None,
    }

    if not value:
        result["error"] = "Enter an IPv4 or IPv6 address or CIDR block."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result
    if "/" not in value:
        value = f"{value}/32" if ":" not in value else f"{value}/128"

    try:
        network = ipaddress.ip_network(value, strict=False)
    except ValueError as exc:
        result["error"] = f"Invalid IPv4/IPv6 address or CIDR block: {exc}"
        return result

    # Compute first/last usable host and usable-host count arithmetically.
    # Do NOT materialize network.hosts() into a list: for large ranges
    # (e.g. an IPv6 /64 has 2**64 addresses) that allocates unbounded
    # memory and can OOM the process on a single user-supplied input.
    max_prefixlen = network.max_prefixlen
    if network.prefixlen == max_prefixlen:
        # /32 (IPv4) or /128 (IPv6): the single address is usable.
        first_addr = last_addr = network.network_address
        usable_hosts = 1
    elif network.prefixlen == max_prefixlen - 1:
        # /31 (IPv4, RFC 3021) or /127 (IPv6): both addresses are usable.
        first_addr = network.network_address
        last_addr = network.broadcast_address
        usable_hosts = 2
    else:
        first_addr = network.network_address + 1
        last_addr = network.broadcast_address - 1
        usable_hosts = network.num_addresses - 2

    if network.version == 4:
        broadcast = str(network.broadcast_address)
        # Wildcard mask is the bitwise inverse of the netmask.
        wildcard = ipaddress.IPv4Address(int(network.hostmask))
    else:
        broadcast = None
        wildcard = None

    first_host = str(first_addr)
    last_host = str(last_addr)

    result.update(
        {
            "ok": True,
            "version": network.version,
            "network": str(network.network_address),
            "netmask": str(network.netmask),
            "wildcard_mask": str(wildcard) if wildcard is not None else None,
            "prefix_length": network.prefixlen,
            "broadcast": broadcast,
            "first_host": first_host,
            "last_host": last_host,
            "total_addresses": network.num_addresses,
            "usable_hosts": usable_hosts,
            "is_private": network.is_private,
            "cidr": str(network),
        }
    )
    return result
