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


def test_azure_openai_summary_non_retryable_error_stops_without_retries(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/openai/v1/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")

    calls = {"count": 0}

    class FakeResponses:
        def create(self, **kwargs):
            calls["count"] += 1
            raise ValueError("invalid request payload")

    class FakeClient:
        responses = FakeResponses()

    result = ai_tools.optional_ai_summary(
        "timeout from upstream",
        opted_in=True,
        client_factory=lambda **_: FakeClient(),
    )

    assert result["enabled"] is False
    assert result["status"] == "error"
    assert result["error_type"] == "ValueError"
    assert calls["count"] == 1


def test_azure_openai_summary_retries_retryable_errors(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/openai/v1/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")
    monkeypatch.setattr(ai_tools.time, "sleep", lambda *_: None)

    calls = {"count": 0}
    RetryableError = type("APIConnectionError", (Exception,), {})

    class FakeResponses:
        def create(self, **kwargs):
            calls["count"] += 1
            if calls["count"] < 3:
                raise RetryableError("temporary connection reset")

            class Response:
                output_text = "Recovered after retry."

            return Response()

    class FakeClient:
        responses = FakeResponses()

    result = ai_tools.optional_ai_summary(
        "timeout from upstream",
        opted_in=True,
        client_factory=lambda **_: FakeClient(),
    )

    assert result["enabled"] is True
    assert result["status"] == "success"
    assert calls["count"] == 3


class _FakeRoadmapItem:
    def __init__(self, title, category="Tools", status="AI Recommended", votes=10, description="", rationale="", source="seed"):
        self.title = title
        self.category = category
        self.status = status
        self.votes = votes
        self.description = description
        self.rationale = rationale
        self.source = source


def test_summarize_feature_requests_unavailable_without_azure_config(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)

    result = ai_tools.summarize_feature_requests_with_azure([_FakeRoadmapItem("Idea 1")])

    assert result["enabled"] is False
    assert result["status"] == "unavailable"


def test_summarize_feature_requests_unavailable_with_no_items(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")

    result = ai_tools.summarize_feature_requests_with_azure([])

    assert result["enabled"] is False
    assert result["status"] == "unavailable"
    assert "no open roadmap items" in result["message"]


def test_summarize_feature_requests_sends_only_public_fields(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")

    calls = []

    class FakeResponses:
        def create(self, **kwargs):
            calls.append(kwargs)

            class Response:
                output_text = "Prioritize the command palette and PWA ideas first."

            return Response()

    class FakeClient:
        responses = FakeResponses()

    items = [
        _FakeRoadmapItem("Command palette", votes=18, description="Ctrl+K launcher", rationale="Power users expect it"),
        _FakeRoadmapItem("PWA support", votes=11, source="github"),
    ]

    result = ai_tools.summarize_feature_requests_with_azure(items, client_factory=lambda **_: FakeClient())

    response_call = calls[0]
    assert result["enabled"] is True
    assert result["status"] == "success"
    assert "Command palette" in response_call["input"]
    assert "PWA support" in response_call["input"]
    assert "test-key" not in response_call["input"]


def test_summarize_feature_requests_returns_error_when_provider_response_has_no_text(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/openai/v1/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")

    class EmptyResponse:
        output_text = ""
        output = []

    class FakeResponses:
        def create(self, **kwargs):
            return EmptyResponse()

    class FakeClient:
        responses = FakeResponses()

    result = ai_tools.summarize_feature_requests_with_azure(
        [_FakeRoadmapItem("Idea 1")],
        client_factory=lambda **_: FakeClient(),
    )

    assert result["enabled"] is False
    assert result["status"] == "error"
    assert result["message"] == "AI triage summary returned no text."


def test_summarize_feature_requests_hides_provider_errors(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "secret-api-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/openai/v1/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")

    class FakeResponses:
        def create(self, **kwargs):
            raise RuntimeError("secret-api-key was rejected")

    class FakeClient:
        responses = FakeResponses()

    result = ai_tools.summarize_feature_requests_with_azure(
        [_FakeRoadmapItem("Idea 1")],
        client_factory=lambda **_: FakeClient(),
    )

    assert result["enabled"] is False
    assert result["status"] == "error"
    assert result["error_type"] == "RuntimeError"
    assert "secret-api-key" not in result["message"]


def test_summarize_feature_requests_retries_retryable_errors(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://example.openai.azure.com/openai/v1/")
    monkeypatch.setenv("AZURE_OPENAI_DEPLOYMENT", "gpt-test")
    monkeypatch.setattr(ai_tools.time, "sleep", lambda *_: None)

    calls = {"count": 0}
    RetryableError = type("RateLimitError", (Exception,), {})

    class FakeResponses:
        def create(self, **kwargs):
            calls["count"] += 1
            if calls["count"] < 3:
                raise RetryableError("rate limited")

            class Response:
                output_text = "Triage summary after retries."

            return Response()

    class FakeClient:
        responses = FakeResponses()

    result = ai_tools.summarize_feature_requests_with_azure(
        [_FakeRoadmapItem("Idea 1")],
        client_factory=lambda **_: FakeClient(),
    )

    assert result["enabled"] is True
    assert result["status"] == "success"
    assert calls["count"] == 3
