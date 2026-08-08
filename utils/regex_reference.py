"""Static reference data for common regex patterns."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegexEntry:
    name: str
    pattern: str
    description: str


REGEX_PATTERNS: tuple[RegexEntry, ...] = (
    RegexEntry("Email address", r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$", "A simple email address (local part + domain)."),
    RegexEntry("IPv4 address", r"^(\d{1,3}\.){3}\d{1,3}$", "Four dot-separated 1-3 digit groups (does not validate the 0-255 range)."),
    RegexEntry(
        "IPv6 address",
        r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$",
        "A fully expanded IPv6 address (does not match the compressed :: form).",
    ),
    RegexEntry(
        "URL",
        r"^https?://[^\s/$.?#].[^\s]*$",
        "A basic http/https URL.",
    ),
    RegexEntry("US phone number", r"^\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$", "A 10-digit US phone number in common formats."),
    RegexEntry(
        "UUID",
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        "Any RFC 4122 UUID, regardless of version.",
    ),
    RegexEntry("Hex color", r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", "A 3- or 6-digit hex color code, with leading #."),
    RegexEntry("US ZIP code", r"^\d{5}(-\d{4})?$", "A 5-digit US ZIP code, optionally with a +4 extension."),
    RegexEntry("Slug", r"^[a-z0-9]+(-[a-z0-9]+)*$", "A URL-friendly slug: lowercase letters, digits, and single hyphens."),
    RegexEntry("HTML tag", r"<([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>(.*?)</\1>", "An opening/closing HTML tag pair with its inner content."),
    RegexEntry("Integer", r"^-?\d+$", "An optionally-negative whole number."),
    RegexEntry("Decimal number", r"^-?\d+(\.\d+)?$", "An optionally-negative integer or decimal number."),
    RegexEntry("MAC address", r"^([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}$", "A colon- or hyphen-separated MAC address."),
    RegexEntry("ISO 8601 date", r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$", "A date, or full date-time with optional timezone."),
)


def search_patterns(query: str) -> tuple[RegexEntry, ...]:
    """Filter REGEX_PATTERNS by name, pattern, or description (case-insensitive substring match)."""
    needle = (query or "").strip().lower()
    if not needle:
        return REGEX_PATTERNS
    return tuple(
        entry
        for entry in REGEX_PATTERNS
        if needle in entry.name.lower() or needle in entry.pattern.lower() or needle in entry.description.lower()
    )
