from __future__ import annotations

from utils.test_data_generator import generate_test_data


def test_generates_requested_count():
    result = generate_test_data(5, seed=1)

    assert result["ok"] is True
    assert len(result["records"]) == 5


def test_same_seed_is_deterministic():
    a = generate_test_data(10, seed=42)
    b = generate_test_data(10, seed=42)

    assert a["records"] == b["records"]


def test_no_seed_still_succeeds():
    result = generate_test_data(3)

    assert result["ok"] is True
    assert len(result["records"]) == 3


def test_records_have_expected_fields():
    result = generate_test_data(1, seed=1)

    record = result["records"][0]
    assert set(record.keys()) == {"full_name", "email", "username", "phone"}
    assert "@example." in record["email"]
    assert record["phone"].startswith("555-01")


def test_rejects_zero_count():
    result = generate_test_data(0)

    assert result["ok"] is False
    assert "at least 1" in result["error"]


def test_rejects_count_above_max():
    result = generate_test_data(101)

    assert result["ok"] is False
    assert "at most" in result["error"]
