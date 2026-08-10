from __future__ import annotations

from utils.cidr_overlap import MAX_ENTRIES, check_cidr_overlaps


def test_check_cidr_overlaps_detects_overlap():
    result = check_cidr_overlaps("10.0.0.0/24\n10.0.0.128/25\n192.168.0.0/24")

    assert result["ok"] is True
    assert result["has_overlaps"] is True
    assert result["overlaps"] == [{"a": "10.0.0.0/24", "b": "10.0.0.128/25"}]


def test_check_cidr_overlaps_no_overlap():
    result = check_cidr_overlaps("10.0.0.0/24\n192.168.0.0/24")

    assert result["ok"] is True
    assert result["has_overlaps"] is False
    assert result["overlaps"] == []


def test_check_cidr_overlaps_bare_ip_normalized_to_slash_32():
    result = check_cidr_overlaps("10.0.0.1\n10.0.0.0/24")

    assert result["ok"] is True
    assert result["has_overlaps"] is True


def test_check_cidr_overlaps_ipv6_bare_address_normalized_to_slash_128():
    result = check_cidr_overlaps("::1\n::1/128")

    assert result["ok"] is True
    assert result["has_overlaps"] is True


def test_check_cidr_overlaps_different_ip_versions_never_overlap():
    result = check_cidr_overlaps("10.0.0.0/24\n::/0")

    assert result["ok"] is True
    assert result["has_overlaps"] is False


def test_check_cidr_overlaps_rejects_single_entry():
    result = check_cidr_overlaps("10.0.0.0/24")

    assert result["ok"] is False
    assert "at least two" in result["error"]


def test_check_cidr_overlaps_rejects_empty_input():
    result = check_cidr_overlaps("")

    assert result["ok"] is False


def test_check_cidr_overlaps_rejects_invalid_entry():
    result = check_cidr_overlaps("not-an-ip\n10.0.0.0/24")

    assert result["ok"] is False
    assert "Invalid entry" in result["error"]


def test_check_cidr_overlaps_rejects_too_many_entries():
    lines = "\n".join(f"10.0.{i}.0/24" for i in range(MAX_ENTRIES + 1))
    result = check_cidr_overlaps(lines)

    assert result["ok"] is False
    assert "no more than" in result["error"]
