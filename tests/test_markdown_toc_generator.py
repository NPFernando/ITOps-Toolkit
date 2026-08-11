from __future__ import annotations

from utils.markdown_toc_generator import generate_toc


def test_basic_headings():
    result = generate_toc("# Title\n\n## Section One\n\n## Section Two")

    assert result["ok"] is True
    assert result["output"] == "- [Title](#title)\n  - [Section One](#section-one)\n  - [Section Two](#section-two)"
    assert result["heading_count"] == 3


def test_duplicate_headings_get_numbered_suffixes():
    # Regression guard for GitHub's actual anchor algorithm: repeated
    # headings get -1, -2, ... suffixes, not overwritten/collided anchors.
    result = generate_toc("# Hello World\n# Hello World\n# Hello World")

    assert "[Hello World](#hello-world)" in result["output"]
    assert "[Hello World](#hello-world-1)" in result["output"]
    assert "[Hello World](#hello-world-2)" in result["output"]


def test_punctuation_stripped_from_slug():
    result = generate_toc("# API Reference (v2)")

    assert "(#api-reference-v2)" in result["output"]


def test_heading_ending_in_literal_hash_is_not_treated_as_closing_sequence():
    # Regression: "## C#" was incorrectly parsed as a closed ATX heading
    # ("## Heading ##" syntax), stripping the trailing "#" from the display
    # text -- but CommonMark requires the closing sequence to be preceded
    # by whitespace, and "C#" has none before its "#".
    result = generate_toc("## C#")

    assert "[C#]" in result["output"]


def test_closed_atx_heading_strips_trailing_hashes():
    result = generate_toc("## Closed Heading ##")

    assert "[Closed Heading](#closed-heading)" in result["output"]


def test_headings_inside_fenced_code_blocks_are_skipped():
    result = generate_toc("```\n# not a heading\n```\n# Real Heading")

    assert result["heading_count"] == 1
    assert "Real Heading" in result["output"]
    assert "not a heading" not in result["output"]


def test_level_range_filter():
    result = generate_toc("# H1\n## H2\n### H3", min_level=2, max_level=2)

    assert result["heading_count"] == 1
    assert "H2" in result["output"]
    assert "H1" not in result["output"]
    assert "H3" not in result["output"]


def test_rejects_empty_input():
    result = generate_toc("")

    assert result["ok"] is False


def test_rejects_no_headings_found():
    result = generate_toc("Just some plain text, no headings.")

    assert result["ok"] is False
    assert "No headings found" in result["error"]
