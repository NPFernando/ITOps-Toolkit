from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "128_Health_Diagnostics.py")


def _run_page() -> AppTest:
    app = AppTest.from_file(PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def _table_rows(app: AppTest) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for frame in app.dataframe:
        rows.extend(frame.value.to_dict("records"))
    return rows


def _row_by_check(rows: list[dict[str, str]], check: str) -> dict[str, str]:
    return next(row for row in rows if row["Check"] == check)


def test_health_diagnostics_page_renders_key_sections():
    app = _run_page()
    page_markdown = " ".join(m.value for m in app.markdown)

    assert "Health Diagnostics" in page_markdown
    assert "Runtime basics" in page_markdown
    assert "Optional integrations" in page_markdown
    assert "Feature flags" in page_markdown
    assert "Safe smoke checks" in page_markdown
    assert len(app.dataframe) >= 4


def test_health_diagnostics_page_reflects_feature_and_integration_status(monkeypatch):
    monkeypatch.setenv("ITOPS_DEV_BASELINE", "1")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")

    rows = _table_rows(_run_page())

    assert _row_by_check(rows, "ITOPS_DEV_BASELINE")["Status"] == "Enabled"
    assert _row_by_check(rows, "Azure OpenAI (optional)")["Status"] == "Configured"
    assert _row_by_check(rows, "Cache probe")["Status"] == "Pass"
    assert _row_by_check(rows, "Roadmap seed parse")["Status"] == "Pass"
