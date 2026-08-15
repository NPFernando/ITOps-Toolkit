"""Shared cache policy controls for user-facing cached surfaces."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Any


CACHE_TTL_TIER_SHORT_SECONDS = 300
CACHE_TTL_TIER_MEDIUM_SECONDS = 3600

ROADMAP_BOARD_CACHE_TTL_SECONDS = CACHE_TTL_TIER_SHORT_SECONDS
ROADMAP_AI_TRIAGE_CACHE_TTL_SECONDS = CACHE_TTL_TIER_MEDIUM_SECONDS


def runtime_cache_scope() -> str:
    """Stable runtime scope for cache isolation in tests."""
    manual_scope = (os.getenv("ITOPS_CACHE_SCOPE") or "").strip()
    if manual_scope:
        return manual_scope
    current_test = (os.getenv("PYTEST_CURRENT_TEST") or "").strip()
    if not current_test:
        return "runtime"
    return current_test.split(" (", 1)[0] or "runtime"


def compose_cache_key(namespace: str, **parts: Any) -> str:
    """Return a stable cache key from canonicalized, hashable content."""
    payload = {"namespace": namespace, "parts": _canonicalize(parts)}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:24]
    return f"{namespace}:{digest}"


def cache_freshness_message(
    surface_label: str,
    cached_at_iso: str,
    ttl_seconds: int,
    now: datetime | None = None,
) -> tuple[str, str]:
    """Return (tone, message) freshness text aligned to reliability contract."""
    cached_at = _parse_timestamp(cached_at_iso)
    effective_now = now or datetime.now(timezone.utc)
    age_seconds = max(0, int((effective_now - cached_at).total_seconds()))
    ttl_human = _human_ttl(ttl_seconds)
    refreshed_at = cached_at.strftime("%Y-%m-%d %H:%M:%S UTC")

    if age_seconds > ttl_seconds:
        message = (
            f"Showing cached data for {surface_label}. Last refreshed {refreshed_at}. "
            f"This is older than the {ttl_human} freshness target."
        )
        return "warning", message

    message = (
        f"{surface_label} last refreshed {refreshed_at}. "
        f"Cached for up to {ttl_human}."
    )
    return "neutral", message


def _canonicalize(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if is_dataclass(value):
        return _canonicalize(asdict(value))
    if isinstance(value, dict):
        return {str(key): _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if isinstance(value, set):
        return sorted(_canonicalize(item) for item in value)
    return str(value)


def _human_ttl(ttl_seconds: int) -> str:
    if ttl_seconds % 3600 == 0:
        hours = ttl_seconds // 3600
        return f"{hours} hour" if hours == 1 else f"{hours} hours"
    if ttl_seconds % 60 == 0:
        minutes = ttl_seconds // 60
        return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"
    return f"{ttl_seconds} seconds"


def _parse_timestamp(value: str) -> datetime:
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


__all__ = [
    "CACHE_TTL_TIER_MEDIUM_SECONDS",
    "CACHE_TTL_TIER_SHORT_SECONDS",
    "ROADMAP_AI_TRIAGE_CACHE_TTL_SECONDS",
    "ROADMAP_BOARD_CACHE_TTL_SECONDS",
    "cache_freshness_message",
    "compose_cache_key",
    "runtime_cache_scope",
]
