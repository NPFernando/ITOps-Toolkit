from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "39_M365_SKU_Decoder.py")


def test_m365_sku_decoder_filters_to_matching_sku():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("SPE_E3").run()
    assert not app.exception

    frame = app.dataframe[0].value
    assert len(frame) == 1
    assert frame.iloc[0]["SKU string"] == "SPE_E3"


def test_m365_sku_decoder_shows_info_on_no_match():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("not-a-real-sku-zzz").run()
    assert not app.exception

    assert any("No SKUs matched that search." in info.value for info in app.info)


def test_m365_sku_decoder_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("SPE_E3").run()
    assert not app.exception

    before = len(app.dataframe[0].value)
    assert before == 1

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("sku").run()
    assert not app.exception
    assert len(app.dataframe[0].value) == before
