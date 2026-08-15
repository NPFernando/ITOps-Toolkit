from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import cve_tools


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "32_CVE_Lookup.py")


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "error", "success"):
        for item in getattr(app, collection_name, []):
            parts.append(str(getattr(item, "value", getattr(item, "body", ""))))
    return "\n".join(parts)


def test_cve_lookup_shows_result_details(monkeypatch):
    monkeypatch.setattr(
        cve_tools,
        "lookup_cve",
        lambda _: {
            "ok": True,
            "total_results": 1,
            "results": [
                {
                    "id": "CVE-2021-44228",
                    "status": "Analyzed",
                    "description": "Example issue.",
                    "published": "2021-12-10T00:00:00.000",
                    "last_modified": "2021-12-20T00:00:00.000",
                    "references": ["https://example.com/advisory"],
                    "cvss": {
                        "base_score": 10.0,
                        "base_severity": "CRITICAL",
                        "vector_string": "AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                    },
                }
            ],
        },
    )

    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    app.text_input[0].set_value("CVE-2021-44228")
    next(b for b in app.button if b.label == "Search").click()
    app.run()
    assert not app.exception

    metrics = {m.label: m.value for m in app.metric}
    assert metrics["Status"] == "Analyzed"
    assert metrics["Severity"] == "CRITICAL"
    assert len(app.dataframe) == 1
    text = _page_text(app)
    assert "CVE lookup completed" in text
    assert 'role="status"' in text


def test_cve_lookup_empty_state_before_submit():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    md = " ".join(m.value for m in app.markdown)
    assert "tool-empty-state" in md


def test_cve_lookup_blank_query_shows_accessible_failure_note():
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    next(b for b in app.button if b.label == "Search").click()
    app.run()
    assert not app.exception

    text = _page_text(app)
    assert "CVE lookup needs attention" in text
    assert "Retry the search or refine the query." in text
    assert 'role="alert"' in text
