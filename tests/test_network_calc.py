from utils import network_calc


def test_calculate_subnet_ipv4_cidr():
    result = network_calc.calculate_subnet("192.168.1.0/24")

    assert result["ok"] is True
    assert result["version"] == 4
    assert result["network"] == "192.168.1.0"
    assert result["netmask"] == "255.255.255.0"
    assert result["wildcard_mask"] == "0.0.0.255"
    assert result["broadcast"] == "192.168.1.255"
    assert result["first_host"] == "192.168.1.1"
    assert result["last_host"] == "192.168.1.254"
    assert result["total_addresses"] == 256
    assert result["usable_hosts"] == 254
    assert result["is_private"] is True


def test_calculate_subnet_bare_ipv4_defaults_to_slash_32():
    result = network_calc.calculate_subnet("8.8.8.8")

    assert result["ok"] is True
    assert result["prefix_length"] == 32
    assert result["network"] == "8.8.8.8"
    assert result["is_private"] is False


def test_calculate_subnet_ipv6_cidr():
    result = network_calc.calculate_subnet("2001:db8::/64")

    assert result["ok"] is True
    assert result["version"] == 6
    assert result["network"] == "2001:db8::"
    assert result["broadcast"] is None
    assert result["wildcard_mask"] is None
    assert result["total_addresses"] == 2**64


def test_calculate_subnet_host_bits_set_normalizes_non_strict():
    result = network_calc.calculate_subnet("192.168.1.5/24")

    assert result["ok"] is True
    assert result["network"] == "192.168.1.0"


def test_calculate_subnet_validation_and_errors():
    assert network_calc.calculate_subnet("")["error"] == "Enter an IPv4 or IPv6 address or CIDR block."
    assert "Invalid" in network_calc.calculate_subnet("not-an-ip")["error"]
    assert "longer than" in network_calc.calculate_subnet("1" * 200)["error"]


def test_calculate_subnet_slash_31_point_to_point_uses_both_addresses():
    # RFC 3021: Python's ipaddress module special-cases /31 to treat both
    # addresses as usable point-to-point endpoints.
    result = network_calc.calculate_subnet("10.0.0.0/31")

    assert result["ok"] is True
    assert result["first_host"] == "10.0.0.0"
    assert result["last_host"] == "10.0.0.1"
    assert result["usable_hosts"] == 2


def test_calculate_subnet_slash_32_is_single_host():
    result = network_calc.calculate_subnet("10.0.0.5/32")

    assert result["ok"] is True
    assert result["first_host"] == "10.0.0.5"
    assert result["last_host"] == "10.0.0.5"
    assert result["usable_hosts"] == 1
