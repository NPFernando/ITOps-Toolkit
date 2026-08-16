from types import SimpleNamespace

from utils import ip_geolocation
from utils.ip_geolocation import lookup_ip_geolocation


def test_lookup_ip_geolocation_rejects_empty_input():
    result = lookup_ip_geolocation("")

    assert result["ok"] is False
    assert "Enter an IP address" in result["error"]


def test_lookup_ip_geolocation_rejects_invalid_ip():
    result = lookup_ip_geolocation("not-an-ip")

    assert result["ok"] is False
    assert "valid IPv4 or IPv6" in result["error"]


def test_lookup_ip_geolocation_public_ip_parses_successful_response(monkeypatch):
    """Public API behavior is covered without making the suite rate-limit- or
    network-dependent; live endpoint availability is not an application unit
    test contract."""
    payload = {
        "status": "success",
        "country": "United States",
        "regionName": "Virginia",
        "city": "Ashburn",
        "zip": "20149",
        "lat": 39.03,
        "lon": -77.5,
        "timezone": "America/New_York",
        "isp": "Google LLC",
        "org": "Google Public DNS",
        "as": "AS15169 Google LLC",
    }
    monkeypatch.setattr(
        ip_geolocation.requests,
        "get",
        lambda *args, **kwargs: SimpleNamespace(status_code=200, json=lambda: payload),
    )

    result = lookup_ip_geolocation("8.8.8.8")

    assert result["ok"] is True
    assert result["country"] == "United States"
    assert result["asn"] == "AS15169 Google LLC"


def test_lookup_ip_geolocation_live_private_ip_returns_error():
    result = lookup_ip_geolocation("192.168.1.1")

    assert result["ok"] is False
    assert result["error"]


def test_lookup_ip_geolocation_live_ipv6():
    result = lookup_ip_geolocation("2001:4860:4860::8888")

    assert result["ok"] is True
    assert result["country"]
