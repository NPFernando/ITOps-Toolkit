from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

CONFIG_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "38_Config_Format_Converter.py")


def _run_page() -> AppTest:
    app = AppTest.from_file(CONFIG_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def test_config_format_converter_page_converts_json_to_yaml():
    app = _run_page()
    app.selectbox[0].set_value("JSON")
    app.selectbox[1].set_value("YAML")
    app.text_area[0].set_value('{"a": 1}')
    app.button[0].click().run()
    assert not app.exception
    assert len(app.code) == 1


def test_config_format_converter_page_clicking_download_does_not_hide_results():
    """Regression: st.download_button triggers a rerun just like any widget outside
    st.form. Results must be keyed off session_state, not the transient `submitted`
    flag, or the whole results section disappears right after the file downloads."""
    app = _run_page()
    app.selectbox[0].set_value("JSON")
    app.selectbox[1].set_value("YAML")
    app.text_area[0].set_value('{"a": 1}')
    app.button[0].click().run()
    assert not app.exception
    assert app.download_button

    app.download_button[0].click().run()
    assert not app.exception
    assert len(app.code) == 1
