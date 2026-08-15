from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import whois_tools


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "27_WHOIS_Lookup.py")


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "error", "success"):
        for item in getattr(app, collection_name, []):
            parts.append(str(getattr(item, "value", getattr(item, "body", ""))))
    return "\n".join(parts)


def test_whois_lookup_shows_registrar_and_tables(monkeypatch):
    monkeypatch.setattr(
        whois_tools,
        "lookup_whois",
        lambda _: {
            "ok": True,
            "registrar": "Example Registrar",
            "events": [{"label": "Registered", "date": "2020-01-01T00:00:00Z"}],
            "nameservers": ["NS1.EXAMPLE.COM"],
            "status": ["client transfer prohibited"],
        },
    )

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Registrar"] == "Example Registrar"
    assert len(app.dataframe) == 3


def test_whois_lookup_empty_state_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_whois_lookup_results_persist_after_sidebar_interaction(monkeypatch):
    monkeypatch.setattr(
        whois_tools,
        "lookup_whois",
        lambda _: {
            "ok": True,
            "registrar": "Example Registrar",
            "events": [],
            "nameservers": ["NS1.EXAMPLE.COM"],
            "status": ["ok"],
        },
    )

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception
    before = len(app.metric)
    assert before > 0

    search = next(t for t in app.text_input if t.key == "sidebar_quick_search")
    search.set_value("whois").run()
    assert not app.exception
    assert len(app.metric) == before


def test_whois_lookup_shows_neutral_note_when_rdap_data_is_sparse(monkeypatch):
    monkeypatch.setattr(
        whois_tools,
        "lookup_whois",
        lambda _: {
            "ok": True,
            "registrar": None,
            "events": [],
            "nameservers": [],
            "status": [],
        },
    )

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    app.text_input[0].set_value("example.com")
    app.button[0].click().run()
    assert not app.exception

    text = _page_text(app)
    assert "WHOIS lookup returned limited data" in text
    assert "Registration events unavailable" in text
    assert "Name server list unavailable" in text
    assert "Domain status codes unavailable" in text
    assert 'role="status"' in text


def test_whois_lookup_page_has_no_page_scoped_mobile_css():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = "\n".join(block.value for block in app.markdown)
    assert "@media (max-width: 768px)" not in markdown
