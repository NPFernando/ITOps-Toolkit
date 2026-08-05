from utils import cidr_aggregator


def test_aggregate_cidrs_collapses_adjacent_networks():
    result = cidr_aggregator.aggregate_cidrs("192.168.0.0/24\n192.168.1.0/24\n10.0.0.0/8")

    assert result["ok"] is True
    assert result["input_count"] == 3
    assert result["output_count"] == 2
    cidrs = {n["cidr"] for n in result["networks"]}
    assert cidrs == {"10.0.0.0/8", "192.168.0.0/23"}


def test_aggregate_cidrs_handles_bare_ips_as_host_routes():
    result = cidr_aggregator.aggregate_cidrs("8.8.8.8\n8.8.8.9")

    assert result["ok"] is True
    assert result["output_count"] == 1
    assert result["networks"][0]["cidr"] == "8.8.8.8/31"


def test_aggregate_cidrs_handles_mixed_ipv4_and_ipv6():
    result = cidr_aggregator.aggregate_cidrs("8.8.8.8\n2001:db8::1")

    assert result["ok"] is True
    assert result["output_count"] == 2
    versions = {n["version"] for n in result["networks"]}
    assert versions == {4, 6}


def test_aggregate_cidrs_rejects_invalid_entry():
    result = cidr_aggregator.aggregate_cidrs("not-an-ip")

    assert result["ok"] is False
    assert "Invalid entry" in result["error"]


def test_aggregate_cidrs_requires_input():
    result = cidr_aggregator.aggregate_cidrs("")

    assert result["ok"] is False
    assert "Enter" in result["error"]


def test_aggregate_cidrs_rejects_oversized_input():
    oversized = "a" * (cidr_aggregator.MAX_INPUT_LENGTH + 1)

    result = cidr_aggregator.aggregate_cidrs(oversized)

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_aggregate_cidrs_no_addresses_materialized_for_huge_ranges():
    # Regression-style test for the same bug class as the Subnet Calculator
    # OOM fixed earlier this session: collapse_addresses() must operate on
    # network/prefix objects, never materialize individual host addresses.
    result = cidr_aggregator.aggregate_cidrs("::/0\n0.0.0.0/0")

    assert result["ok"] is True
    assert result["output_count"] == 2
