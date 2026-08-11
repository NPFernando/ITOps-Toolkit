from __future__ import annotations

import uuid

from utils.deterministic_uuid import generate_deterministic_uuid


def test_generate_deterministic_uuid_v5_matches_stdlib():
    result = generate_deterministic_uuid("DNS", "example.com", 5)

    assert result["ok"] is True
    assert result["result"] == str(uuid.uuid5(uuid.NAMESPACE_DNS, "example.com"))


def test_generate_deterministic_uuid_v3_matches_stdlib():
    result = generate_deterministic_uuid("URL", "https://example.com", 3)

    assert result["ok"] is True
    assert result["result"] == str(uuid.uuid3(uuid.NAMESPACE_URL, "https://example.com"))


def test_generate_deterministic_uuid_is_deterministic():
    first = generate_deterministic_uuid("DNS", "example.com", 5)
    second = generate_deterministic_uuid("DNS", "example.com", 5)

    assert first["result"] == second["result"]


def test_generate_deterministic_uuid_all_namespaces():
    for namespace in ("DNS", "URL", "OID", "X.500"):
        result = generate_deterministic_uuid(namespace, "test", 5)
        assert result["ok"] is True


def test_generate_deterministic_uuid_rejects_empty_name():
    result = generate_deterministic_uuid("DNS", "", 5)

    assert result["ok"] is False
    assert result["error"] == "Enter a name to hash."


def test_generate_deterministic_uuid_rejects_unknown_namespace():
    result = generate_deterministic_uuid("BOGUS", "test", 5)

    assert result["ok"] is False
    assert "Unknown namespace" in result["error"]


def test_generate_deterministic_uuid_rejects_unsupported_version():
    result = generate_deterministic_uuid("DNS", "test", 4)

    assert result["ok"] is False
    assert "Unsupported version" in result["error"]


def test_generate_deterministic_uuid_rejects_oversized_name():
    result = generate_deterministic_uuid("DNS", "a" * 501, 5)

    assert result["ok"] is False
    assert "longer than" in result["error"]
