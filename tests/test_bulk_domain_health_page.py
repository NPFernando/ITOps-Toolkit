from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

BULK_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "28_Bulk_Domain_Health.py")


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "error", "warning"):
        for item in getattr(app, collection_name, []):
            parts.append(str(getattr(item, "value", getattr(item, "body", ""))))
    return "\n".join(parts)


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
    assert "bulk_domain_health_state" in app.session_state
    state = app.session_state["bulk_domain_health_state"]
    assert {"frame", "csv_data", "summary"} <= set(state.keys())
    assert state["summary"]["healthy"] >= 0
    assert "Processing summary" in _page_text(app)

    app.download_button[0].click()
    app.run(timeout=60)
    assert not app.exception
    assert len(app.dataframe) == 1


def test_bulk_domain_health_validation_error_survives_a_rerun():
    """Regression: the "Upload a file or paste at least one domain." validation
    error used to be rendered directly (not persisted to session_state), so it
    vanished the instant any widget outside st.form was touched -- e.g. the
    sidebar's quick-search box -- unlike every other page's validation errors."""
    app = AppTest.from_file(BULK_PAGE, default_timeout=60)
    app.run()
    assert not app.exception

    app.button[0].click()
    app.run(timeout=60)
    assert not app.exception
    assert any("Upload a file or paste at least one domain." in e.value for e in app.error)

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run(timeout=60)
    assert not app.exception
    assert any("Upload a file or paste at least one domain." in e.value for e in app.error)
