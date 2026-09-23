"""Shared, public-safe diagnostics for network-backed tool adapters."""

from __future__ import annotations

from typing import Any, MutableMapping


def diagnostics(
    *,
    error_code: str | None = None,
    failure_mode: str | None = None,
    attempts: int = 0,
    retryable: bool = False,
) -> dict[str, Any]:
    """Return the common diagnostic fields used by adapter result envelopes."""
    return {
        "error_code": error_code,
        "failure_mode": failure_mode,
        "attempts": attempts,
        "retryable": retryable,
    }


def update_diagnostics(
    result: MutableMapping[str, Any],
    *,
    error_code: str | None = None,
    failure_mode: str | None = None,
    attempts: int = 0,
    retryable: bool = False,
) -> MutableMapping[str, Any]:
    """Add or replace common diagnostics without exposing upstream details."""
    result.update(
        diagnostics(
            error_code=error_code,
            failure_mode=failure_mode,
            attempts=attempts,
            retryable=retryable,
        )
    )
    return result


def classify_http_status(status_code: int, retryable_statuses: set[int]) -> tuple[str, str, bool]:
    """Classify an HTTP response using the shared transient/persistent taxonomy."""
    if status_code in retryable_statuses:
        return f"http_{status_code}", "transient", True
    if status_code >= 400:
        return f"http_{status_code}", "persistent", False
    return "success", "healthy", False
