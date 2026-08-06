from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

CRON_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "8_Cron_Explainer.py")


def _run_page() -> AppTest:
    app = AppTest.from_file(CRON_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def test_cron_explainer_page_explains_a_valid_expression():
    app = _run_page()
    app.text_input[0].set_value("*/15 * * * *")
    app.button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) == 1


def test_cron_explainer_page_clicking_download_does_not_hide_results():
    """Regression: st.download_button triggers a rerun just like any widget outside
    st.form. Results must be keyed off session_state, not the transient `submitted`
    flag, or the whole results section disappears right after the .ics downloads."""
    app = _run_page()
    app.text_input[0].set_value("*/15 * * * *")
    app.button[0].click().run()
    assert not app.exception
    assert app.download_button

    app.download_button[0].click().run()
    assert not app.exception
    assert len(app.dataframe) == 1
