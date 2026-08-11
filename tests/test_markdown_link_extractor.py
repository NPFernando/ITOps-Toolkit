from __future__ import annotations

from utils.markdown_link_extractor import extract_links


def test_extracts_inline_link():
    result = extract_links("Check out [Google](https://google.com).")

    assert result["ok"] is True
    assert result["links"] == [{"text": "Google", "url": "https://google.com", "type": "inline"}]


def test_inline_link_with_title_strips_title():
    result = extract_links('[GitHub](https://github.com "GitHub homepage")')

    assert result["links"][0]["url"] == "https://github.com"


def test_ignores_image_syntax():
    result = extract_links("![alt text](https://example.com/image.png)")

    assert result["ok"] is False
    assert result["error"] == "No links found."


def test_extracts_reference_style_link():
    text = "See [my link][1] for details.\n\n[1]: https://example.com/ref"
    result = extract_links(text)

    assert result["ok"] is True
    assert {"text": "my link", "url": "https://example.com/ref", "type": "reference"} in result["links"]


def test_extracts_shorthand_reference_link():
    text = "See [shorthand][] for details.\n\n[shorthand]: https://example.com/shorthand"
    result = extract_links(text)

    assert {"text": "shorthand", "url": "https://example.com/shorthand", "type": "reference"} in result["links"]


def test_extracts_autolink():
    result = extract_links("Visit <https://example.org> directly.")

    assert result["ok"] is True
    assert {"text": "https://example.org", "url": "https://example.org", "type": "autolink"} in result["links"]


def test_multiple_link_types_together():
    text = "[Inline](https://a.com) and <https://b.com> and [ref][1]\n\n[1]: https://c.com"
    result = extract_links(text)

    types = {link["type"] for link in result["links"]}
    assert types == {"inline", "autolink", "reference"}


def test_rejects_empty_input():
    result = extract_links("")

    assert result["ok"] is False
    assert result["error"] == "Paste some Markdown text."


def test_rejects_no_links_found():
    result = extract_links("Just plain text, no links here.")

    assert result["ok"] is False
    assert result["error"] == "No links found."
