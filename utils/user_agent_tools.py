"""User-Agent string parsing helpers.

Best-effort, rule-based parsing covering common browsers, OSes, and bots --
not an exhaustive database like ua-parser. Good enough for "what likely hit
my server", not for billing-grade analytics.
"""

from __future__ import annotations

import re
from typing import Any

MAX_INPUT_LENGTH = 2_000

_BOT_PATTERNS = (
    ("Googlebot", re.compile(r"Googlebot")),
    ("Bingbot", re.compile(r"bingbot")),
    ("DuckDuckBot", re.compile(r"DuckDuckBot")),
    ("Slackbot", re.compile(r"Slackbot")),
    ("Twitterbot", re.compile(r"Twitterbot")),
    ("facebookexternalhit", re.compile(r"facebookexternalhit")),
    ("curl", re.compile(r"^curl/", re.IGNORECASE)),
    ("python-requests", re.compile(r"python-requests")),
    ("Postman", re.compile(r"PostmanRuntime")),
    ("Generic bot/crawler", re.compile(r"bot|crawler|spider", re.IGNORECASE)),
)

# Order matters: Edge/OPR/Chrome all include "Safari" and often "Chrome" in
# their UA string for compatibility, so more specific tokens must be checked
# first.
_BROWSER_PATTERNS = (
    ("Edge", re.compile(r"Edg(?:A|iOS)?/([\d.]+)")),
    ("Opera", re.compile(r"(?:OPR|Opera)/([\d.]+)")),
    ("Samsung Internet", re.compile(r"SamsungBrowser/([\d.]+)")),
    ("Firefox", re.compile(r"Firefox/([\d.]+)")),
    ("Chrome", re.compile(r"Chrome/([\d.]+)")),
    ("Safari", re.compile(r"Version/([\d.]+).*Safari")),
)

_OS_PATTERNS = (
    ("Windows", re.compile(r"Windows NT ([\d.]+)")),
    ("iOS", re.compile(r"iPhone OS ([\d_]+)|CPU OS ([\d_]+)")),
    ("macOS", re.compile(r"Mac OS X ([\d_]+)")),
    ("Android", re.compile(r"Android ([\d.]+)")),
    ("Linux", re.compile(r"Linux")),
    ("Chrome OS", re.compile(r"CrOS")),
)

_WINDOWS_VERSION_NAMES = {
    "10.0": "10/11",
    "6.3": "8.1",
    "6.2": "8",
    "6.1": "7",
}


def _detect_bot(ua: str) -> str | None:
    for name, pattern in _BOT_PATTERNS:
        if pattern.search(ua):
            return name
    return None


def _detect_browser(ua: str) -> tuple[str | None, str | None]:
    for name, pattern in _BROWSER_PATTERNS:
        match = pattern.search(ua)
        if match:
            return name, match.group(1)
    return None, None


def _detect_os(ua: str) -> tuple[str | None, str | None]:
    for name, pattern in _OS_PATTERNS:
        match = pattern.search(ua)
        if not match:
            continue
        version = next((g for g in match.groups() if g), None) if match.groups() else None
        if version:
            version = version.replace("_", ".")
            if name == "Windows":
                version = _WINDOWS_VERSION_NAMES.get(version, version)
        return name, version
    return None, None


def _detect_device_type(ua: str) -> str:
    if re.search(r"iPad|Tablet", ua):
        return "Tablet"
    if re.search(r"Mobi|iPhone|Android", ua):
        return "Mobile"
    return "Desktop"


def parse_user_agent(ua_string: str) -> dict[str, Any]:
    """Break a User-Agent string down into likely browser, OS, and device details."""
    result: dict[str, Any] = {"ok": False, "error": None}
    value = (ua_string or "").strip()
    if not value:
        result["error"] = "Enter a User-Agent string."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH:,} characters."
        return result

    bot = _detect_bot(value)
    browser_name, browser_version = _detect_browser(value)
    os_name, os_version = _detect_os(value)
    device_type = "Bot" if bot else _detect_device_type(value)

    result.update(
        {
            "ok": True,
            "is_bot": bot is not None,
            "bot_name": bot,
            "browser": browser_name,
            "browser_version": browser_version,
            "os": os_name,
            "os_version": os_version,
            "device_type": device_type,
        }
    )
    return result
