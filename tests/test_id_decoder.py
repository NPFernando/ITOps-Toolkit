from __future__ import annotations

import uuid

from utils import id_decoder, id_generator


def test_decode_ulid_round_trips_with_generate_ulid():
    generated = id_generator.generate_ulid(timestamp_ms=1_700_000_000_000)
    result = id_decoder.decode_ulid(generated)

    assert result["ok"] is True
    assert result["timestamp_ms"] == 1_700_000_000_000
    assert result["datetime_utc"].startswith("2023-11-14")
    assert len(result["randomness_hex"]) == 20


def test_decode_ulid_accepts_crockford_leniency_and_lowercase():
    generated = id_generator.generate_ulid(timestamp_ms=1_700_000_000_000).lower()
    result = id_decoder.decode_ulid(generated)

    assert result["ok"] is True
    assert result["timestamp_ms"] == 1_700_000_000_000


def test_decode_ulid_rejects_wrong_length():
    result = id_decoder.decode_ulid("TOOSHORT")

    assert result["ok"] is False
    assert "26 characters" in result["error"]


def test_decode_ulid_rejects_invalid_characters():
    # 'U' and 'I' followed by a genuinely invalid char -- Crockford excludes
    # I/L/O/U from its alphabet (I/L/O are aliased, U is rejected outright to
    # avoid visual confusion with V).
    result = id_decoder.decode_ulid("!" * 26)

    assert result["ok"] is False
    assert "Crockford Base32" in result["error"]


def test_decode_ulid_rejects_empty_input():
    result = id_decoder.decode_ulid("")

    assert result["ok"] is False
    assert result["error"] == "Enter a ULID."


def test_decode_uuid_v4_has_no_timestamp():
    result = id_decoder.decode_uuid(str(uuid.uuid4()))

    assert result["ok"] is True
    assert result["version"] == 4
    assert result["timestamp_supported"] is False
    assert result["datetime_utc"] is None


def test_decode_uuid_v1_extracts_timestamp():
    result = id_decoder.decode_uuid(str(uuid.uuid1()))

    assert result["ok"] is True
    assert result["version"] == 1
    assert result["timestamp_supported"] is True
    assert result["datetime_utc"] is not None


def test_decode_uuid_v7_extracts_timestamp():
    # Python 3.12 (pinned in this repo) has no stdlib uuid.uuid7(), so build
    # one manually per RFC 9562: top 48 bits = unix_ts_ms, next 4 = version.
    unix_ts_ms = 1_700_000_000_000
    value = (unix_ts_ms & 0xFFFFFFFFFFFF) << 80
    value |= (7 & 0xF) << 76
    value |= (0x123 & 0xFFF) << 64
    value |= (0b10 & 0x3) << 62
    value |= 0x0BADC0FFEE1234 & 0x3FFFFFFFFFFFFFFF
    v7 = uuid.UUID(int=value)

    result = id_decoder.decode_uuid(str(v7))

    assert result["ok"] is True
    assert result["version"] == 7
    assert result["timestamp_supported"] is True
    assert result["datetime_utc"].startswith("2023-11-14")


def test_decode_uuid_nil_uuid_has_no_version():
    # Regression: the nil UUID (all zeros) has no version bits set --
    # decode_uuid must report version=None rather than raising, and the
    # page must not render a bare "None" for it.
    result = id_decoder.decode_uuid("00000000-0000-0000-0000-000000000000")

    assert result["ok"] is True
    assert result["version"] is None
    assert result["timestamp_supported"] is False


def test_decode_uuid_max_uuid_has_no_version():
    result = id_decoder.decode_uuid("ffffffff-ffff-ffff-ffff-ffffffffffff")

    assert result["ok"] is True
    assert result["version"] is None
    assert result["timestamp_supported"] is False


def test_decode_uuid_rejects_invalid_input():
    result = id_decoder.decode_uuid("not-a-uuid")

    assert result["ok"] is False
    assert result["error"] == "Not a valid UUID."


def test_decode_uuid_rejects_empty_input():
    result = id_decoder.decode_uuid("")

    assert result["ok"] is False
    assert result["error"] == "Enter a UUID."
