from __future__ import annotations

from streamlit.testing.v1 import AppTest

from utils import ai_tools


LOG_PAGE = "pages/9_Log_Troubleshooting_Assistant.py"
SAMPLE_LOG = "token=secret certificate verify failed"


def _run_log_page() -> AppTest:
    app = AppTest.from_file(LOG_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def _page_text(app: AppTest) -> str:
    parts: list[str] = []
    for collection_name in ("markdown", "warning", "info", "error", "caption"):
        collection = getattr(app, collection_name, [])
        for item in collection:
            parts.append(str(getattr(item, "body", getattr(item, "value", ""))))
    for item in app.dataframe:
        parts.append(str(item.value))
    return "\n".join(parts)


def _finding_rows(app: AppTest) -> list[dict[str, str]]:
    assert len(app.dataframe) == 1
    return app.dataframe[0].value.to_dict("records")


def _set_azure_config(monkeypatch, configured: bool) -> None:
    values = {
        "AZURE_OPENAI_API_KEY": "secret-api-key",
        "AZURE_OPENAI_ENDPOINT": "https://example.openai.azure.com",
        "AZURE_OPENAI_DEPLOYMENT": "gpt-test",
        "AZURE_OPENAI_API_VERSION": "",
        "OPENAI_API_KEY": "",
    }

    def fake_secret_value(name: str) -> str:
        if not configured:
            return ""
        return values.get(name, "")

    monkeypatch.setattr(ai_tools, "_secret_value", fake_secret_value)


def _submit_log(app: AppTest, use_ai_summary: bool) -> AppTest:
    app.text_area[0].set_value(SAMPLE_LOG)
    app.checkbox[0].set_value(use_ai_summary)
    app.button[0].click()
    app.run()
    assert not app.exception
    return app


def test_log_page_ai_checkbox_disabled_without_azure_config(monkeypatch):
    _set_azure_config(monkeypatch, configured=False)

    app = _run_log_page()
    text = _page_text(app)

    assert len(app.checkbox) == 1
    assert app.checkbox[0].label == "Generate optional Azure AI summary"
    assert app.checkbox[0].disabled is True
    assert app.checkbox[0].value is False
    assert "Azure AI summary unavailable" in text
    assert "Rule-based analysis still works" in text


def test_log_page_ai_checkbox_enabled_with_azure_config(monkeypatch):
    _set_azure_config(monkeypatch, configured=True)

    app = _run_log_page()
    text = _page_text(app)

    assert len(app.checkbox) == 1
    assert app.checkbox[0].disabled is False
    assert app.checkbox[0].value is False
    assert "Azure AI summary available" in text
    assert "Optional and off by default" in text


def test_log_page_unchecked_submit_skips_ai_without_external_call(monkeypatch):
    _set_azure_config(monkeypatch, configured=True)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Azure summary adapter should not run without opt-in")

    monkeypatch.setattr(ai_tools, "summarize_logs_with_azure", fail_if_called)

    app = _submit_log(_run_log_page(), use_ai_summary=False)
    text = _page_text(app)
    findings = _finding_rows(app)

    assert findings[0]["likely_issue"] == "SSL certificate error"
    assert "Azure AI summary skipped" in text
    assert "secret-api-key" not in text


def test_log_page_checked_submit_renders_fake_ai_success(monkeypatch):
    _set_azure_config(monkeypatch, configured=True)
    calls = []

    def fake_optional_ai_summary(sanitized_text, findings=None, opted_in=False, client_factory=None):
        calls.append(
            {
                "sanitized_text": sanitized_text,
                "findings": findings,
                "opted_in": opted_in,
                "client_factory": client_factory,
            }
        )
        return {
            "enabled": True,
            "provider": "azure_openai",
            "status": "success",
            "message": "Azure AI summary generated from sanitized log text only.",
            "summary": "Fake Azure summary: check the certificate chain and renewal status.",
        }

    monkeypatch.setattr(ai_tools, "optional_ai_summary", fake_optional_ai_summary)

    app = _submit_log(_run_log_page(), use_ai_summary=True)
    text = _page_text(app)

    assert calls
    assert calls[0]["opted_in"] is True
    assert calls[0]["sanitized_text"] == "[REDACTED] certificate verify failed"
    assert "Optional Azure AI summary" in text
    assert "Fake Azure summary" in text
    assert "secret-api-key" not in text


def test_log_page_checked_submit_renders_safe_ai_error(monkeypatch):
    _set_azure_config(monkeypatch, configured=True)

    def fake_optional_ai_summary(sanitized_text, findings=None, opted_in=False, client_factory=None):
        return {
            "enabled": False,
            "provider": "azure_openai",
            "status": "error",
            "message": "Azure AI summary could not be generated. Rule-based results are still available.",
            "error_type": "RuntimeError",
        }

    monkeypatch.setattr(ai_tools, "optional_ai_summary", fake_optional_ai_summary)

    app = _submit_log(_run_log_page(), use_ai_summary=True)
    text = _page_text(app)
    findings = _finding_rows(app)

    assert findings[0]["likely_issue"] == "SSL certificate error"
    assert "Azure AI summary could not be generated" in text
    assert "Rule-based results are still available" in text
    assert "secret-api-key" not in text
