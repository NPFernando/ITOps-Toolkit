from __future__ import annotations

from utils.xml_formatter import format_xml


def test_format_xml_pretty_prints_nested_elements():
    result = format_xml("<root><a>1</a><b><c>2</c></b></root>")

    assert result["ok"] is True
    assert "<a>1</a>" in result["output"]
    assert result["output"].count("\n") > 0
    # No blank lines left over from minidom's whitespace-only text nodes.
    assert "\n\n" not in result["output"]


def test_format_xml_minify_removes_whitespace():
    result = format_xml("<root>  <a>1</a>  </root>", minify=True)

    assert result["ok"] is True
    assert result["output"] == "<root>  <a>1</a>  </root>"


def test_format_xml_minify_preserves_significant_whitespace():
    # Whitespace inside elements is significant per the XML spec -- minify
    # must not alter content, so indentation whitespace between tags is
    # preserved rather than stripped (ElementTree's correct, conservative
    # behavior, not a bug).
    pretty = "<root>\n  <a>1</a>\n</root>"

    result = format_xml(pretty, minify=True)

    assert result["ok"] is True
    assert result["output"] == pretty


def test_format_xml_rejects_malformed_xml():
    result = format_xml("<root><unclosed></root>")

    assert result["ok"] is False
    assert "Invalid XML" in result["error"]


def test_format_xml_minify_rejects_malformed_xml():
    result = format_xml("<root><unclosed></root>", minify=True)

    assert result["ok"] is False
    assert "Invalid XML" in result["error"]


def test_format_xml_rejects_empty_input():
    result = format_xml("")

    assert result["ok"] is False
    assert result["error"] == "Paste XML to format."


def test_format_xml_rejects_oversized_input():
    result = format_xml("<a>" + "x" * 100_001 + "</a>")

    assert result["ok"] is False
    assert "longer than" in result["error"]
