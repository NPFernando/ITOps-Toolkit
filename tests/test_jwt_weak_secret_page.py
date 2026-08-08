from __future__ import annotations

import warnings
from pathlib import Path

import jwt
from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "63_JWT_Weak_Secret_Checker.py")


def _token(secret="secret"):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return jwt.encode({"sub": "1"}, secret, algorithm="HS256")


def test_weak_secret_shows_error():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value(_token("secret"))
    app.button[0].click().run()
    assert not app.exception

    assert any("Weak secret found" in e.value for e in app.error)


def test_strong_secret_shows_success():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value(_token("a-very-long-random-secret-nobody-would-guess-1234567890"))
    app.button[0].click().run()
    assert not app.exception
    assert any("No match" in s.value for s in app.success)


def test_alg_none_shows_unsigned_warning_not_asymmetric_info():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()

    app.text_input[0].set_value(jwt.encode({"sub": "1"}, "", algorithm="none"))
    app.button[0].click().run()
    assert not app.exception

    assert any("UNSIGNED" in e.value for e in app.error)
    assert not any("asymmetric" in i.value for i in app.info)


def test_empty_state_shown_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_results_persist_after_sidebar_interaction():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value(_token("secret"))
    app.button[0].click().run()
    assert not app.exception
    before = len(app.error)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("test").run()
    assert not app.exception
    assert len(app.error) == before
