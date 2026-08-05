from utils import ui
from utils.ui import (
    POPULAR_TOOLS,
    PROFESSIONS,
    TITLE_TO_SLUG,
    TOOLS,
    display_rows_frame,
    filter_tools,
    recent_or_popular_tools,
)


def test_display_rows_frame_stringifies_mixed_values():
    frame = display_rows_frame(
        [
            {"field": "Status code", "value": 200},
            {"field": "Missing", "value": None},
        ]
    )

    assert frame["value"].tolist() == ["200", "None"]
    assert all(isinstance(value, str) for value in frame["value"].tolist())


def test_render_status_note_escapes_description_and_normalizes_tone(monkeypatch):
    rendered = []

    def fake_markdown(value, unsafe_allow_html=False):
        rendered.append((value, unsafe_allow_html))

    monkeypatch.setattr(ui.st, "markdown", fake_markdown)

    ui.render_status_note("AI <summary>", "<script>alert(1)</script>\nline", tone="unknown")

    html, unsafe = rendered[0]
    assert unsafe is True
    assert "tool-status-note-info" in html
    assert "AI &lt;summary&gt;" in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;<br>line" in html
    assert "<script>" not in html


def test_title_to_slug_covers_every_tool():
    assert len(TITLE_TO_SLUG) == len(TOOLS)
    for tool in TOOLS:
        assert TITLE_TO_SLUG[tool.title] == tool.slug


def test_filter_tools_empty_query_and_profession_returns_everything():
    assert filter_tools() == TOOLS
    assert filter_tools("", "All") == TOOLS


def test_filter_tools_profession_narrows_results():
    results = filter_tools(profession="Network Engineer")

    assert results
    assert all("Network Engineer" in tool.professions for tool in results)
    assert len(results) < len(TOOLS)


def test_filter_tools_query_and_profession_combine_with_and():
    results = filter_tools(query="hash", profession="Network Engineer")

    assert results == ()


def test_filter_tools_unknown_profession_behaves_like_all():
    assert filter_tools(profession="Not A Real Profession") == TOOLS


def test_filter_tools_covers_every_declared_profession():
    for profession in PROFESSIONS:
        assert filter_tools(profession=profession), f"no tool tagged with {profession!r}"


def test_recent_or_popular_tools_falls_back_to_popular_when_empty():
    assert recent_or_popular_tools([]) == POPULAR_TOOLS


def test_recent_or_popular_tools_skips_unknown_slugs_and_dedupes():
    slug = TOOLS[-1].slug
    result = recent_or_popular_tools(["not-a-real-slug", slug, slug])

    assert result[0] == TOOLS[-1]
    assert result.count(TOOLS[-1]) == 1


def test_recent_or_popular_tools_pads_to_five_with_popular_tools_in_order():
    slug = TOOLS[-1].slug
    result = recent_or_popular_tools([slug])

    assert len(result) == 5
    assert result[0] == TOOLS[-1]
    assert result[1:] == tuple(t for t in POPULAR_TOOLS if t.slug != slug)[:4]


def test_recent_or_popular_tools_no_padding_when_five_valid_recents():
    slugs = [tool.slug for tool in TOOLS[:5]][::-1]
    result = recent_or_popular_tools(slugs)

    assert [tool.slug for tool in result] == slugs
