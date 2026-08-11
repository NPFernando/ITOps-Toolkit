from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "74_HTML_Entity_Encoder_Decoder.py")


def test_encode_button_shows_encoded_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value('<b>bold</b> & "quotes"')
    app.button[0].click().run()
    assert not app.exception

    assert app.text_area[1].value == "&lt;b&gt;bold&lt;/b&gt; &amp; &quot;quotes&quot;"


def test_decode_button_shows_decoded_result():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_area[0].set_value("&lt;b&gt;bold&lt;/b&gt;")
    app.button[1].click().run()
    assert not app.exception

    assert app.text_area[1].value == "<b>bold</b>"


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_area[0].set_value("<b>bold</b>")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.text_area)
    assert before > 1

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.text_area) == before
