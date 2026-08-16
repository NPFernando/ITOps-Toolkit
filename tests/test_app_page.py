from pathlib import Path

from streamlit.testing.v1 import AppTest


# Newer streamlit resolves AppTest.from_file()'s relative paths against the
# file that calls it (this test file's directory), not the working
# directory -- an absolute path avoids that resolution entirely.
APP_PAGE = str(Path(__file__).resolve().parent.parent / "app.py")
UI_MODULE = Path(__file__).resolve().parent.parent / "utils" / "ui.py"


def test_css_injects_before_sidebar_and_has_no_blocking_import():
    """Regression: apply_app_shell() used to render the sidebar's custom HTML
    before injecting the stylesheet that styles it, and the stylesheet's
    first rule used to be a blocking @import fetching Google Fonts -- CSS
    spec requires @import to precede every other rule in its stylesheet, so
    every other rule (backgrounds, hiding native Streamlit chrome, sidebar/
    card styling) couldn't take effect until that font finished loading.
    Together these produced a visible flash of unstyled content on page load
    and navigation."""
    at = AppTest.from_file(APP_PAGE, default_timeout=30).run()
    assert not at.exception, at.exception

    # CSS is intentionally rendered through st.html(), not st.markdown():
    # CommonMark can expose a large multi-line <style> block as visible text.
    # Assert the implementation contract directly while AppTest verifies page
    # startup did not raise.
    ui_source = UI_MODULE.read_text(encoding="utf-8")
    assert "@import" not in ui_source, "blocking @import reintroduced"
    assert 'rel="stylesheet"' in ui_source, "no font stylesheet link found"
    assert "st.html(css)" in ui_source, "CSS should use raw HTML rendering"
    assert ui_source.index("_inject_global_css(\"dark\")") < ui_source.index("render_sidebar(active_page)")


def test_home_pills_are_required_and_cannot_deselect_to_none():
    """Regression: st.pills defaults to required=False, meaning a click on an
    already-selected pill deselects it to None. The sort pill's value used to
    feed directly into a bare dict lookup with no fallback -- a KeyError that
    crashed the whole home page. The profession pill's None wasn't caught
    either, leaving `show_all` stuck True and the heading rendering the
    literal string "None Tools". Both must stay required=True."""
    at = AppTest.from_file(APP_PAGE, default_timeout=30).run()
    assert not at.exception, at.exception
    next(b for b in at.button if b.label == "Show all tools").click().run()
    assert not at.exception, at.exception

    profession_pill = next(p for p in at.pills if p.key == "home_profession_filter")
    sort_pill = next(p for p in at.pills if p.key == "home_sort_mode")
    assert profession_pill.proto.required is True
    assert sort_pill.proto.required is True


def test_hide_all_tools_button_reflects_combined_show_all_state():
    """Regression: the "Hide all tools" button used to reflect only the raw
    home_show_all flag, not the actual combined show_all state (flag OR an
    active search/profession filter). This meant the button could read "Show
    all tools" while the section was already expanded by a filter, and
    clicking it while a filter was doing the showing set the flag True --
    which then outlived the filter, leaving the section stuck open even
    after clearing it."""
    at = AppTest.from_file(APP_PAGE, default_timeout=30).run()
    assert not at.exception, at.exception

    # A profession filter alone should already show "Hide all tools", not
    # "Show all tools" -- the button must reflect the combined state.
    profession_pill = next(p for p in at.pills if p.key == "home_profession_filter")
    profession_pill.set_value("Network Engineer").run(timeout=30)
    assert not at.exception, at.exception
    assert "Hide all tools" in [b.label for b in at.button]

    # Clicking "Hide all tools" while the filter is still active must reset
    # the sticky flag to False (the section keeps showing via the filter,
    # but the flag no longer outlives it).
    next(b for b in at.button if b.label == "Hide all tools").click().run(timeout=30)
    assert not at.exception, at.exception
    flag = at.session_state["home_show_all"] if "home_show_all" in at.session_state else False
    assert flag is False
    assert "Hide all tools" in [b.label for b in at.button]

    # Resetting the filter back to "All" must collapse back to "Show all
    # tools" -- not stay stuck open.
    profession_pill2 = next(p for p in at.pills if p.key == "home_profession_filter")
    profession_pill2.set_value("All").run(timeout=30)
    assert not at.exception, at.exception
    assert "Show all tools" in [b.label for b in at.button]
