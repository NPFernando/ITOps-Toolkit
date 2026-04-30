import jwt

from utils import text_tools


def test_validate_length_accepts_and_rejects_values():
    assert text_tools.validate_length("abc", 3, "Value") == (True, None)

    ok, error = text_tools.validate_length("abcd", 3, "Value")

    assert ok is False
    assert error == "Value is longer than 3 characters."


def test_format_json_text_formats_minifies_and_reports_errors():
    formatted = text_tools.format_json_text('{"status":"ok","items":[1]}')
    minified = text_tools.format_json_text('{"status": "ok"}', minify=True)
    invalid = text_tools.format_json_text('{"status": }')

    assert formatted["ok"] is True
    assert formatted["result"] == '{\n  "status": "ok",\n  "items": [\n    1\n  ]\n}'
    assert minified["result"] == '{"status":"ok"}'
    assert invalid["ok"] is False
    assert "Invalid JSON at line 1" in invalid["error"]


def test_format_json_text_rejects_oversized_input():
    result = text_tools.format_json_text("x" * (text_tools.MAX_JSON_LENGTH + 1))

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_base64_encode_decode_and_invalid_input():
    encoded = text_tools.encode_base64_text("hello")
    decoded = text_tools.decode_base64_text(encoded)
    invalid = text_tools.decode_base64_text("not valid base64!")

    assert encoded == "aGVsbG8="
    assert decoded == {"ok": True, "error": None, "result": "hello"}
    assert invalid["ok"] is False
    assert invalid["result"] is None


def test_decode_jwt_unverified_valid_and_invalid_tokens():
    token = jwt.encode(
        {"iss": "issuer", "aud": "audience", "iat": 0, "exp": 60},
        "secret" * 8,
        algorithm="HS256",
        headers={"kid": "key-1"},
    )

    result = text_tools.decode_jwt_unverified(token)
    invalid = text_tools.decode_jwt_unverified("not-a-jwt")

    assert result["ok"] is True
    assert result["header"]["kid"] == "key-1"
    assert result["issuer"] == "issuer"
    assert result["audience"] == "audience"
    assert result["issued_at"] == "1970-01-01 00:00:00 UTC"
    assert invalid["ok"] is False
    assert "Could not decode JWT" in invalid["error"]


def test_datetime_from_timestamp_handles_missing_and_invalid_values():
    assert text_tools.datetime_from_timestamp(None) is None
    assert text_tools.datetime_from_timestamp("not-int") is None
    assert text_tools.datetime_from_timestamp(0) == "1970-01-01 00:00:00 UTC"


def test_explain_cron_valid_and_invalid_paths():
    valid = text_tools.explain_cron("*/15 * * * *", count=2)
    wrong_fields = text_tools.explain_cron("* * * *")
    invalid = text_tools.explain_cron("61 * * * *")

    assert valid["ok"] is True
    assert len(valid["next_runs"]) == 2
    assert wrong_fields["ok"] is False
    assert "5-field" in wrong_fields["error"]
    assert invalid["ok"] is False
    assert invalid["error"] == "Cron expression is not valid."
