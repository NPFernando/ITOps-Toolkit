from utils.reliability import classify_http_status, diagnostics, update_diagnostics


def test_diagnostics_has_additive_provider_and_rate_limit_fields():
    result = diagnostics(
        attempts=2,
        duration_ms=41.5,
        provider="nvd",
        rate_limit_remaining=7,
        rate_limit_reset_seconds=30,
    )

    assert result == {
        "error_code": None,
        "failure_mode": None,
        "attempts": 2,
        "retryable": False,
        "duration_ms": 41.5,
        "provider": "nvd",
        "rate_limit_remaining": 7,
        "rate_limit_reset_seconds": 30,
    }


def test_update_diagnostics_preserves_existing_result_keys():
    result = {"ok": False, "error": "temporary"}
    update_diagnostics(result, error_code="timeout", failure_mode="transient", provider="http")

    assert result["ok"] is False
    assert result["error"] == "temporary"
    assert result["error_code"] == "timeout"
    assert result["provider"] == "http"


def test_classify_http_status_identifies_rate_limit_as_retryable():
    assert classify_http_status(429, {429, 503}) == ("http_429", "transient", True)
    assert classify_http_status(404, {429, 503}) == ("http_404", "persistent", False)
