from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

JSON_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "5_JSON_Formatter.py")


def _run_page() -> AppTest:
    app = AppTest.from_file(JSON_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def test_json_formatter_page_validates_json():
    app = _run_page()
    app.text_area[0].set_value('{"a": 1}')
    app.button[0].click().run()
    assert not app.exception
    assert len(app.json) == 1


def test_json_formatter_page_toggling_expand_all_does_not_hide_results():
    """Regression: st.toggle triggers a rerun outside st.form. Results must be
    keyed off session_state, not the transient *_clicked flags, or the whole
    results section disappears the instant "Expand all" is touched."""
    app = _run_page()
    app.text_area[0].set_value('{"a": 1}')
    app.button[0].click().run()
    assert not app.exception
    assert len(app.json) == 1

    app.toggle[0].set_value(False).run()
    assert not app.exception
    assert len(app.json) == 1


def test_json_formatter_page_searching_does_not_hide_results():
    app = _run_page()
    app.text_area[0].set_value('{"a": 1, "b": 2}')
    app.button[0].click().run()
    assert not app.exception

    search = next(t for t in app.text_input if t.label == "Search keys and values")
    search.set_value("a").run()
    assert not app.exception
    assert len(app.json) == 1


def test_json_formatter_page_clicking_download_does_not_hide_results():
    app = _run_page()
    app.text_area[0].set_value('{"a": 1}')
    app.radio[0].set_value("Format JSON")
    app.button[0].click().run()
    assert not app.exception
    assert app.download_button

    app.download_button[0].click().run()
    assert not app.exception
    assert len(app.json) == 1
