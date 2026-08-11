from __future__ import annotations

import uuid
from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "75_Deterministic_UUID_Generator.py")


def test_generate_shows_correct_uuid():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.selectbox[0].set_value("DNS")
    app.radio[0].set_value(5)
    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception

    codes = app.code
    assert len(codes) == 1
    assert codes[0].value == str(uuid.uuid5(uuid.NAMESPACE_DNS, "example.com"))


def test_empty_name_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("")
    app.button[0].click().run()
    assert not app.exception
    assert any("Enter a name" in e.value for e in app.error)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.code)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.code) == before
