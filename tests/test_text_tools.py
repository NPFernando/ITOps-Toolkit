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


def test_format_json_text_supports_custom_indent():
    result = text_tools.format_json_text('{"a": 1}', indent=4)

    assert result["result"] == '{\n    "a": 1\n}'


def test_format_json_text_handles_deeply_nested_input_without_crashing():
    deeply_nested = "[" * 50_000 + "]" * 50_000

    result = text_tools.format_json_text(deeply_nested)

    assert result["ok"] is False
    assert "nested too deeply" in result["error"]


def test_json_stats_reports_type_size_depth_and_node_count():
    stats = text_tools.json_stats({"a": 1, "b": {"c": [1, 2, 3]}})

    assert stats["type"] == "object"
    assert stats["top_level_count"] == 2
    assert stats["max_depth"] == 4
    assert stats["node_count"] == 7

    scalar_stats = text_tools.json_stats(42)
    assert scalar_stats["type"] == "int"
    assert scalar_stats["top_level_count"] is None
    assert scalar_stats["max_depth"] == 1
    assert scalar_stats["node_count"] == 1


def test_search_json_paths_matches_keys_and_values_and_caps_results():
    data = {"status": "ok", "items": [{"name": "alpha"}, {"name": "beta"}]}

    key_matches = text_tools.search_json_paths(data, "status")
    value_matches = text_tools.search_json_paths(data, "alpha")
    no_query = text_tools.search_json_paths(data, "")

    assert key_matches == [{"path": "$.status", "match": "key", "value": "ok"}]
    assert value_matches == [{"path": "$.items[0].name", "match": "value", "value": "alpha"}]
    assert no_query == []

    huge = {f"key{i}": "needle" for i in range(text_tools.MAX_JSON_SEARCH_RESULTS + 50)}
    capped = text_tools.search_json_paths(huge, "needle")
    assert len(capped) == text_tools.MAX_JSON_SEARCH_RESULTS


def test_base64_encode_decode_and_invalid_input():
    encoded = text_tools.encode_base64_text("hello")
    decoded = text_tools.decode_base64_text(encoded)
    invalid = text_tools.decode_base64_text("not valid base64!")

    assert encoded == "aGVsbG8="
    assert decoded == {"ok": True, "error": None, "result": "hello"}
    assert invalid["ok"] is False
    assert invalid["result"] is None


def test_base64_decode_handles_wrapped_multiline_input():
    # Regression: base64.b64decode(validate=True) rejects any embedded
    # whitespace, so wrapped/multi-line base64 -- the standard `base64` CLI
    # output format, or anything copy-pasted from a text file -- used to fail
    # with a misleading "Invalid Base64 input" error despite being valid.
    original = "hello world this is a test string" * 3
    encoded = text_tools.encode_base64_text(original)
    wrapped = "\n".join(encoded[i : i + 40] for i in range(0, len(encoded), 40))

    decoded = text_tools.decode_base64_text(wrapped)

    assert decoded == {"ok": True, "error": None, "result": original}


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


def test_encode_url_text_percent_encodes_reserved_characters():
    result = text_tools.encode_url_text("hello world/test?a=b&c=d")

    assert result["ok"] is True
    assert result["result"] == "hello%20world%2Ftest%3Fa%3Db%26c%3Dd"


def test_encode_url_text_plus_for_space_uses_form_encoding():
    result = text_tools.encode_url_text("a b+c", plus_for_space=True)

    assert result["ok"] is True
    assert result["result"] == "a+b%2Bc"


def test_decode_url_text_reverses_encoding():
    encoded = text_tools.encode_url_text("hello world/test?a=b")["result"]
    result = text_tools.decode_url_text(encoded)

    assert result["ok"] is True
    assert result["result"] == "hello world/test?a=b"


def test_decode_url_text_plus_for_space_converts_plus_to_space():
    result = text_tools.decode_url_text("a+b%2Bc", plus_for_space=True)

    assert result["ok"] is True
    assert result["result"] == "a b+c"


def test_decode_url_text_without_plus_for_space_keeps_literal_plus():
    result = text_tools.decode_url_text("a+b", plus_for_space=False)

    assert result["ok"] is True
    assert result["result"] == "a+b"


def test_url_tools_reject_oversized_input():
    oversized = "a" * (text_tools.MAX_URL_LENGTH + 1)

    assert text_tools.encode_url_text(oversized)["ok"] is False
    assert text_tools.decode_url_text(oversized)["ok"] is False
