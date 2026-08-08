from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

ID_GENERATOR_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "40_ID_Generator.py")


def _run_page() -> AppTest:
    app = AppTest.from_file(ID_GENERATOR_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def test_id_generator_page_generates_uuids_by_default():
    app = _run_page()
    app.button[0].click().run()
    assert not app.exception

    assert len(app.code) == 1
    ids = app.code[0].value.splitlines()
    assert len(ids) == 10  # default slider value


def test_id_generator_page_pluralizes_uuid_heading_correctly():
    """Regression: f"{count} {result_type}(s)" rendered "10 UUID (v4)(s)" --
    the "(s)" landed after the trailing parenthetical instead of the noun."""
    app = _run_page()
    app.button[0].click().run()
    assert not app.exception

    headings = " ".join(m.value for m in app.markdown)
    assert "10 UUIDs (v4)" in headings
    assert "(v4)(s)" not in headings


def test_id_generator_page_clicking_download_does_not_hide_results():
    """Regression: st.download_button triggers a rerun just like a plain widget
    outside st.form. Results must be keyed off session_state, not the transient
    `submitted` flag, or the whole results section disappears right after the
    file downloads."""
    app = _run_page()
    app.button[0].click().run()
    assert not app.exception
    assert len(app.code) == 1

    app.download_button[0].click().run()
    assert not app.exception

    assert len(app.code) == 1
    assert len(app.dataframe) == 1


def test_id_generator_page_switching_to_ulid_generates_ulids():
    app = _run_page()
    app.radio[0].set_value("ULID")
    app.button[0].click().run()
    assert not app.exception

    ids = app.code[0].value.splitlines()
    assert len(ids) == 10
    assert all(len(value) == 26 for value in ids)
