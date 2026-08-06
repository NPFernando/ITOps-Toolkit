from utils.ip_geolocation import lookup_ip_geolocation


def test_lookup_ip_geolocation_rejects_empty_input():
    result = lookup_ip_geolocation("")

    assert result["ok"] is False
    assert "Enter an IP address" in result["error"]


def test_lookup_ip_geolocation_rejects_invalid_ip():
    result = lookup_ip_geolocation("not-an-ip")

    assert result["ok"] is False
    assert "valid IPv4 or IPv6" in result["error"]


def test_lookup_ip_geolocation_live_public_ip():
    result = lookup_ip_geolocation("8.8.8.8")

    assert result["ok"] is True
    assert result["country"] == "United States"
    assert result["asn"]


def test_lookup_ip_geolocation_live_private_ip_returns_error():
    result = lookup_ip_geolocation("192.168.1.1")

    assert result["ok"] is False
    assert result["error"]


def test_lookup_ip_geolocation_live_ipv6():
    result = lookup_ip_geolocation("2001:4860:4860::8888")

    assert result["ok"] is True
    assert result["country"]
