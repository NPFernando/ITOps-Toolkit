"""IP geolocation lookup via the free ip-api.com public API (no key required)."""

from __future__ import annotations

import ipaddress
from typing import Any

import requests


IP_API_URL = "http://ip-api.com/json/{ip}"
IP_API_TIMEOUT = 8
IP_API_FIELDS = "status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
_HEADERS = {"User-Agent": "ITOpsToolkit/1.0 public-safe-checker"}


def _empty_result(ip: str) -> dict[str, Any]:
    return {
        "ok": False,
        "query": ip,
        "country": None,
        "region": None,
        "city": None,
        "postal": None,
        "latitude": None,
        "longitude": None,
        "timezone": None,
        "isp": None,
        "org": None,
        "asn": None,
        "error": None,
    }


def lookup_ip_geolocation(ip: str) -> dict[str, Any]:
    """Resolve an IP address to approximate geography, ASN, and ISP/org info."""
    cleaned = (ip or "").strip()
    result = _empty_result(cleaned)

    if not cleaned:
        result["error"] = "Enter an IP address."
        return result
    try:
        ipaddress.ip_address(cleaned)
    except ValueError:
        result["error"] = "Enter a valid IPv4 or IPv6 address."
        return result

    try:
        response = requests.get(
            IP_API_URL.format(ip=cleaned),
            params={"fields": IP_API_FIELDS},
            headers=_HEADERS,
            timeout=IP_API_TIMEOUT,
        )
    except requests.RequestException as exc:
        result["error"] = f"IP geolocation lookup failed: {exc}"
        return result

    if response.status_code == 429:
        result["error"] = "Rate limit reached. Wait a moment and try again."
        return result
    if response.status_code != 200:
        result["error"] = f"IP geolocation lookup failed with status {response.status_code}."
        return result

    try:
        payload = response.json()
    except ValueError:
        result["error"] = "IP geolocation lookup returned an unexpected response."
        return result

    if payload.get("status") != "success":
        result["error"] = payload.get("message", "IP geolocation lookup failed.").capitalize()
        return result

    result.update(
        {
            "ok": True,
            "country": payload.get("country"),
            "region": payload.get("regionName"),
            "city": payload.get("city"),
            "postal": payload.get("zip"),
            "latitude": payload.get("lat"),
            "longitude": payload.get("lon"),
            "timezone": payload.get("timezone"),
            "isp": payload.get("isp"),
            "org": payload.get("org"),
            "asn": payload.get("as"),
        }
    )
    return result
