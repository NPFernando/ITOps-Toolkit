from __future__ import annotations

from utils.html_entity_tools import decode_html_entities, encode_html_entities


def test_encode_html_entities_basic():
    assert encode_html_entities('<b>bold</b> & "quotes"') == "&lt;b&gt;bold&lt;/b&gt; &amp; &quot;quotes&quot;"


def test_encode_html_entities_empty_input():
    assert encode_html_entities("") == ""


def test_decode_html_entities_round_trips():
    encoded = encode_html_entities('<b>bold</b> & "quotes"')

    result = decode_html_entities(encoded)

    assert result["ok"] is True
    assert result["result"] == '<b>bold</b> & "quotes"'


def test_decode_html_entities_numeric_character_references():
    result = decode_html_entities("&#39;&#x27;")

    assert result["ok"] is True
    assert result["result"] == "''"


def test_decode_html_entities_leaves_unrecognized_entities_as_is():
    # "&zzz...;" matches no real HTML5 named entity (even as a substring
    # prefix, unlike e.g. "&not" which legitimately matches the legacy
    # "&not;" -> NOT SIGN entity without a trailing semicolon).
    result = decode_html_entities("&zzznotarealentityzzz;")

    assert result["ok"] is True
    assert result["result"] == "&zzznotarealentityzzz;"


def test_decode_html_entities_rejects_empty_input():
    result = decode_html_entities("")

    assert result["ok"] is False
    assert result["error"] == "Enter HTML-entity-encoded text to decode."


def test_decode_html_entities_rejects_oversized_input():
    result = decode_html_entities("a" * 20_001)

    assert result["ok"] is False
    assert "longer than" in result["error"]
