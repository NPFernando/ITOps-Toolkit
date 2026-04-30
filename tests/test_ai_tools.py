from utils import ai_tools
from utils.text_tools import MAX_LOG_LENGTH


def test_sanitize_text_redacts_common_secret_shapes():
    text = (
        "password=super-secret "
        "key AKIAABCDEFGHIJKLMNOP "
        "jwt abcdefghijklmnopqrstuvwxyz.abcdefghijklmnopqrstuvwxyz.abcdefghijklmnopqrstuvwxyz"
    )

    sanitized = ai_tools.sanitize_text(text)

    assert "super-secret" not in sanitized
    assert "AKIAABCDEFGHIJKLMNOP" not in sanitized
    assert "abcdefghijklmnopqrstuvwxyz.abcdefghijklmnopqrstuvwxyz.abcdefghijklmnopqrstuvwxyz" not in sanitized
    assert sanitized.count("[REDACTED]") == 3


def test_analyze_logs_detects_known_patterns_and_uses_sanitized_text():
    result = ai_tools.analyze_logs_rule_based("token=abc123 certificate verify failed")

    assert result["ok"] is True
    assert result["sanitized"] == "[REDACTED] certificate verify failed"
    assert result["findings"][0]["likely_issue"] == "SSL certificate error"
    assert result["findings"][0]["severity"] == "Critical"


def test_analyze_logs_fallback_when_no_pattern_matches():
    result = ai_tools.analyze_logs_rule_based("application started successfully")

    assert result["ok"] is True
    assert result["findings"][0]["likely_issue"] == "No known pattern detected"
    assert result["findings"][0]["severity"] == "Unknown"


def test_analyze_logs_rejects_oversized_input():
    result = ai_tools.analyze_logs_rule_based("x" * (MAX_LOG_LENGTH + 1))

    assert result["ok"] is False
    assert result["findings"] == []
    assert result["sanitized"] == ""


def test_direct_openai_key_does_not_enable_optional_ai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)

    result = ai_tools.optional_ai_summary("logs", opted_in=True)

    assert ai_tools.optional_ai_provider() is None
    assert result["enabled"] is False
    assert result["status"] == "unavailable"


def test_optional_ai_summary_detects_azure_openai_and_skips_without_opt_in(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")

    result = ai_tools.optional_ai_summary("logs")

    assert ai_tools.optional_ai_provider() == "azure_openai"
    assert result["enabled"] is False
    assert result["status"] == "skipped"
    assert "opt-in" in result["message"]


def test_incomplete_azure_openai_config_is_not_enabled(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("AZURE_OPENAI_ENDPOINT", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_DEPLOYMENT", raising=False)

    result = ai_tools.optional_ai_summary("logs")

    assert ai_tools.optional_ai_provider() is None
    assert result["enabled"] is False
    assert result["status"] == "unavailable"


def test_azure_openai_summary_uses_responses_api_and_sanitized_input(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")

    calls = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)

            class Response:
                output_text = "Likely certificate failure. Check the certificate chain and renewal status."

            return Response()

    class FakeClient:
        responses = FakeResponses()

    def fake_client_factory(**kwargs):
        calls.append({"client": kwargs})
        return FakeClient()

    result = ai_tools.optional_ai_summary(
        "[REDACTED] certificate verify failed",
        findings=[{"severity": "Critical", "likely_issue": "SSL certificate error", "possible_cause": "Expired cert"}],
        opted_in=True,
        client_factory=fake_client_factory,
    )

    client_call = calls[0]["client"]
    response_call = calls[1]

    assert result["enabled"] is True
    assert result["status"] == "success"
    assert client_call["base_url"] == "https://example.openai.azure.com/openai/v1/"
    assert response_call["model"] == "gpt-test"
    assert "responses" not in response_call
    assert "certificate verify failed" in response_call["input"]
    assert "test-key" not in response_call["input"]


def test_azure_openai_summary_hides_provider_errors(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret-api-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/openai/v1/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")

    class FakeResponses:
        def create(self, **kwargs):
            raise RuntimeError("secret-api-key was rejected")

    class FakeClient:
        responses = FakeResponses()

    result = ai_tools.optional_ai_summary(
        "[REDACTED] timeout",
        opted_in=True,
        client_factory=lambda **_: FakeClient(),
    )

    assert result["enabled"] is False
    assert result["status"] == "error"
    assert result["error_type"] == "RuntimeError"
    assert "secret-api-key" not in result["message"]
