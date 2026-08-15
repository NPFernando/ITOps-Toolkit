from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "36_Email_Record_Builder.py")


def test_email_record_builder_shows_empty_state_before_build():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "Ready to build SPF" in markdown


def test_email_record_builder_builds_spf_record():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("_spf.google.com")
    app.button[0].click().run()
    assert not app.exception

    code = " ".join(block.value for block in app.code)
    markdown = " ".join(block.value for block in app.markdown)
    assert "v=spf1" in code
    assert "SPF record ready" in markdown


def test_email_record_builder_spf_warning_outcome_is_shown():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.button[0].click().run()
    assert not app.exception

    markdown = " ".join(block.value for block in app.markdown)
    assert "SPF record generated with warnings" in markdown
    assert "SPF guidance" in markdown
