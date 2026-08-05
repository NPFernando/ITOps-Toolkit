from utils import ipv6_tools


def test_convert_ipv6_compresses_and_expands():
    result = ipv6_tools.convert_ipv6("2001:0db8:0000:0000:0000:ff00:0042:8329")

    assert result["ok"] is True
    assert result["compressed"] == "2001:db8::ff00:42:8329"
    assert result["expanded"] == "2001:0db8:0000:0000:0000:ff00:0042:8329"


def test_convert_ipv6_already_compressed_input():
    result = ipv6_tools.convert_ipv6("2001:db8::1")

    assert result["ok"] is True
    assert result["compressed"] == "2001:db8::1"
    assert result["expanded"] == "2001:0db8:0000:0000:0000:0000:0000:0001"


def test_convert_ipv6_rejects_invalid_address():
    result = ipv6_tools.convert_ipv6("not-valid")

    assert result["ok"] is False
    assert "Invalid IPv6 address" in result["error"]


def test_convert_ipv6_rejects_ipv4_address():
    result = ipv6_tools.convert_ipv6("192.168.1.1")

    assert result["ok"] is False


def test_convert_ipv6_requires_input():
    result = ipv6_tools.convert_ipv6("")

    assert result["ok"] is False
    assert "Enter an IPv6 address" in result["error"]
