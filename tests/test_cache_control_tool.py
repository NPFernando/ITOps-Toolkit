from __future__ import annotations

from utils.cache_control_tool import build_cache_control, explain_cache_control


def test_build_with_flags_and_max_age():
    result = build_cache_control(["public", "must-revalidate"], max_age=3600)

    assert result["ok"] is True
    assert result["output"] == "public, must-revalidate, max-age=3600"


def test_build_rejects_public_and_private_together():
    result = build_cache_control(["public", "private"])

    assert result["ok"] is False
    assert "mutually exclusive" in result["error"]


def test_build_rejects_no_store_with_max_age():
    result = build_cache_control(["no-store"], max_age=60)

    assert result["ok"] is False
    assert "contradictory" in result["error"]


def test_build_rejects_unknown_directive():
    result = build_cache_control(["bogus"])

    assert result["ok"] is False
    assert "Unknown directive" in result["error"]


def test_build_rejects_empty_selection():
    result = build_cache_control([])

    assert result["ok"] is False


def test_explain_known_flag_directive():
    result = explain_cache_control("public")

    assert result["ok"] is True
    assert "may be stored by any cache" in result["directives"][0]["description"]


def test_explain_numeric_directive():
    result = explain_cache_control("max-age=3600")

    assert result["ok"] is True
    assert "3600 seconds" in result["directives"][0]["description"]


def test_explain_unrecognized_directive():
    result = explain_cache_control("bogus-directive")

    assert result["ok"] is True
    assert result["directives"][0]["description"] == "Unrecognized directive."


def test_explain_multiple_directives():
    result = explain_cache_control("public, max-age=3600, must-revalidate")

    assert result["ok"] is True
    assert len(result["directives"]) == 3


def test_explain_rejects_empty_input():
    result = explain_cache_control("")

    assert result["ok"] is False
