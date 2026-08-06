import uuid

from utils.id_generator import MAX_COUNT, _CROCKFORD_ALPHABET, generate_ulid, generate_ulids, generate_uuids


def test_generate_ulid_is_26_chars_from_crockford_alphabet():
    ulid = generate_ulid()

    assert len(ulid) == 26
    assert all(c in _CROCKFORD_ALPHABET for c in ulid)


def test_generate_ulid_is_deterministic_for_fixed_timestamp():
    # Same millisecond timestamp always encodes to the same first 10 characters;
    # only the trailing 16 random characters vary.
    a = generate_ulid(timestamp_ms=1_700_000_000_000)
    b = generate_ulid(timestamp_ms=1_700_000_000_000)

    assert a[:10] == b[:10]
    assert a[10:] != b[10:]


def test_generate_ulid_sorts_lexicographically_by_timestamp():
    earlier = generate_ulid(timestamp_ms=1_000)
    later = generate_ulid(timestamp_ms=2_000)

    assert earlier < later


def test_generate_uuids_returns_valid_uuid4_strings():
    result = generate_uuids(5)

    assert result["ok"] is True
    assert len(result["ids"]) == 5
    for value in result["ids"]:
        parsed = uuid.UUID(value)
        assert parsed.version == 4


def test_generate_uuids_produces_unique_values():
    result = generate_uuids(50)

    assert len(set(result["ids"])) == 50


def test_generate_uuids_rejects_out_of_range_count():
    assert generate_uuids(0)["ok"] is False
    assert generate_uuids(MAX_COUNT + 1)["ok"] is False


def test_generate_ulids_returns_requested_count_and_unique_values():
    result = generate_ulids(20)

    assert result["ok"] is True
    assert len(result["ids"]) == 20
    assert len(set(result["ids"])) == 20


def test_generate_ulids_rejects_out_of_range_count():
    assert generate_ulids(0)["ok"] is False
    assert generate_ulids(MAX_COUNT + 1)["ok"] is False
