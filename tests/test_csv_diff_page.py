from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "59_CSV_Diff_Viewer.py")
CSV_A = "id,name\n1,Alice\n2,Bob\n"
CSV_B = "id,name\n1,Alicia\n3,Carol\n"


def test_compare_shows_differences_table():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("id")
    app.text_area[0].set_value(CSV_A)
    app.text_area[1].set_value(CSV_B)
    app.button[0].click().run()
    assert not app.exception

    dataframes = app.dataframe
    assert len(dataframes) == 1


def test_identical_csvs_show_success():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value("id")
    app.text_area[0].set_value(CSV_A)
    app.text_area[1].set_value(CSV_A)
    app.button[0].click().run()
    assert not app.exception
    assert any("identical" in s.value for s in app.success)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("id")
    app.text_area[0].set_value(CSV_A)
    app.text_area[1].set_value(CSV_B)
    app.button[0].click().run()
    assert not app.exception
    before = len(app.dataframe)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.dataframe) == before
