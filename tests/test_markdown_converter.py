from __future__ import annotations

from utils.markdown_converter import convert_markdown


def test_markdown_to_html_converts_headings_and_emphasis():
    result = convert_markdown("# Hello\n\n**bold** and *italic*", "Markdown to HTML")

    assert result["ok"] is True
    assert "<h1>Hello</h1>" in result["output"]
    assert "<strong>bold</strong>" in result["output"]
    assert "<em>italic</em>" in result["output"]


def test_markdown_to_html_converts_lists():
    result = convert_markdown("- a\n- b", "Markdown to HTML")

    assert result["ok"] is True
    assert "<li>a</li>" in result["output"]
    assert "<li>b</li>" in result["output"]


def test_html_to_markdown_converts_basic_tags():
    result = convert_markdown("<h1>Hello</h1><p><strong>bold</strong></p>", "HTML to Markdown")

    assert result["ok"] is True
    # markdownify renders h1 as a Setext-style underlined heading, not ATX "# ".
    assert "Hello" in result["output"]
    assert "=====" in result["output"]
    assert "**bold**" in result["output"]


def test_convert_markdown_rejects_empty_input():
    result = convert_markdown("", "Markdown to HTML")

    assert result["ok"] is False
    assert result["error"] == "Enter some text to convert."


def test_convert_markdown_rejects_unknown_direction():
    result = convert_markdown("hello", "Sideways")

    assert result["ok"] is False
    assert "Unknown direction" in result["error"]


def test_convert_markdown_rejects_oversized_input():
    result = convert_markdown("a" * 100_001, "Markdown to HTML")

    assert result["ok"] is False
    assert "longer than" in result["error"]
