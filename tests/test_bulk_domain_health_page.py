from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

BULK_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "28_Bulk_Domain_Health.py")


def test_bulk_domain_health_page_clicking_download_does_not_hide_results():
    """Regression: st.download_button triggers a rerun just like any widget outside
    st.form. Results must be keyed off session_state, not the transient `submitted`
    flag, or the whole results section disappears right after the CSV downloads."""
    app = AppTest.from_file(BULK_PAGE, default_timeout=60)
    app.run()
    assert not app.exception

    app.text_area[0].set_value("example.com")
    app.button[0].click()
    app.run(timeout=60)
    assert not app.exception
    assert len(app.dataframe) == 1
    assert app.download_button

    app.download_button[0].click()
    app.run(timeout=60)
    assert not app.exception
    assert len(app.dataframe) == 1
