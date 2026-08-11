"""Static reference table of common timezone abbreviations.

Many abbreviations are genuinely ambiguous (e.g. "CST" is used for US
Central, China, and Cuba standard time, at three different UTC offsets) --
this is a well-documented real-world hazard, not an edge case, so ambiguous
abbreviations deliberately appear as multiple separate entries rather than
picking one "winning" meaning. Curated, not exhaustive of every regional
abbreviation in use.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimezoneAbbreviationEntry:
    abbreviation: str
    utc_offset: str
    name: str


TIMEZONE_ABBREVIATIONS: tuple[TimezoneAbbreviationEntry, ...] = (
    TimezoneAbbreviationEntry("UTC", "UTC+00:00", "Coordinated Universal Time"),
    TimezoneAbbreviationEntry("GMT", "UTC+00:00", "Greenwich Mean Time"),
    TimezoneAbbreviationEntry("BST", "UTC+01:00", "British Summer Time"),
    TimezoneAbbreviationEntry("IST", "UTC+05:30", "India Standard Time"),
    TimezoneAbbreviationEntry("IST", "UTC+02:00", "Israel Standard Time"),
    TimezoneAbbreviationEntry("IST", "UTC+01:00", "Irish Standard Time"),
    TimezoneAbbreviationEntry("CET", "UTC+01:00", "Central European Time"),
    TimezoneAbbreviationEntry("CEST", "UTC+02:00", "Central European Summer Time"),
    TimezoneAbbreviationEntry("EET", "UTC+02:00", "Eastern European Time"),
    TimezoneAbbreviationEntry("EEST", "UTC+03:00", "Eastern European Summer Time"),
    TimezoneAbbreviationEntry("WET", "UTC+00:00", "Western European Time"),
    TimezoneAbbreviationEntry("WEST", "UTC+01:00", "Western European Summer Time"),
    TimezoneAbbreviationEntry("MSK", "UTC+03:00", "Moscow Standard Time"),
    TimezoneAbbreviationEntry("EST", "UTC-05:00", "US Eastern Standard Time"),
    TimezoneAbbreviationEntry("EDT", "UTC-04:00", "US Eastern Daylight Time"),
    TimezoneAbbreviationEntry("CST", "UTC-06:00", "US Central Standard Time"),
    TimezoneAbbreviationEntry("CST", "UTC+08:00", "China Standard Time"),
    TimezoneAbbreviationEntry("CST", "UTC-05:00", "Cuba Standard Time"),
    TimezoneAbbreviationEntry("CDT", "UTC-05:00", "US Central Daylight Time"),
    TimezoneAbbreviationEntry("MST", "UTC-07:00", "US Mountain Standard Time"),
    TimezoneAbbreviationEntry("MDT", "UTC-06:00", "US Mountain Daylight Time"),
    TimezoneAbbreviationEntry("PST", "UTC-08:00", "US Pacific Standard Time"),
    TimezoneAbbreviationEntry("PDT", "UTC-07:00", "US Pacific Daylight Time"),
    TimezoneAbbreviationEntry("AKST", "UTC-09:00", "Alaska Standard Time"),
    TimezoneAbbreviationEntry("AKDT", "UTC-08:00", "Alaska Daylight Time"),
    TimezoneAbbreviationEntry("HST", "UTC-10:00", "Hawaii Standard Time"),
    TimezoneAbbreviationEntry("AST", "UTC-04:00", "Atlantic Standard Time"),
    TimezoneAbbreviationEntry("ADT", "UTC-03:00", "Atlantic Daylight Time"),
    TimezoneAbbreviationEntry("NST", "UTC-03:30", "Newfoundland Standard Time"),
    TimezoneAbbreviationEntry("BRT", "UTC-03:00", "Brasilia Time"),
    TimezoneAbbreviationEntry("ART", "UTC-03:00", "Argentina Time"),
    TimezoneAbbreviationEntry("SAST", "UTC+02:00", "South Africa Standard Time"),
    TimezoneAbbreviationEntry("EAT", "UTC+03:00", "East Africa Time"),
    TimezoneAbbreviationEntry("WAT", "UTC+01:00", "West Africa Time"),
    TimezoneAbbreviationEntry("GST", "UTC+04:00", "Gulf Standard Time"),
    TimezoneAbbreviationEntry("PKT", "UTC+05:00", "Pakistan Standard Time"),
    TimezoneAbbreviationEntry("BST", "UTC+06:00", "Bangladesh Standard Time"),
    TimezoneAbbreviationEntry("ICT", "UTC+07:00", "Indochina Time"),
    TimezoneAbbreviationEntry("WIB", "UTC+07:00", "Western Indonesia Time"),
    TimezoneAbbreviationEntry("SGT", "UTC+08:00", "Singapore Time"),
    TimezoneAbbreviationEntry("HKT", "UTC+08:00", "Hong Kong Time"),
    TimezoneAbbreviationEntry("AWST", "UTC+08:00", "Australian Western Standard Time"),
    TimezoneAbbreviationEntry("JST", "UTC+09:00", "Japan Standard Time"),
    TimezoneAbbreviationEntry("KST", "UTC+09:00", "Korea Standard Time"),
    TimezoneAbbreviationEntry("ACST", "UTC+09:30", "Australian Central Standard Time"),
    TimezoneAbbreviationEntry("AEST", "UTC+10:00", "Australian Eastern Standard Time"),
    TimezoneAbbreviationEntry("AEDT", "UTC+11:00", "Australian Eastern Daylight Time"),
    TimezoneAbbreviationEntry("NZST", "UTC+12:00", "New Zealand Standard Time"),
    TimezoneAbbreviationEntry("NZDT", "UTC+13:00", "New Zealand Daylight Time"),
)


def search_timezone_abbreviations(query: str) -> tuple[TimezoneAbbreviationEntry, ...]:
    """Filter TIMEZONE_ABBREVIATIONS by abbreviation, offset, or name (case-insensitive substring match)."""
    needle = (query or "").strip().lower()
    if not needle:
        return TIMEZONE_ABBREVIATIONS
    return tuple(
        entry
        for entry in TIMEZONE_ABBREVIATIONS
        if needle in entry.abbreviation.lower() or needle in entry.utc_offset.lower() or needle in entry.name.lower()
    )
