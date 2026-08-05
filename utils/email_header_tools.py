"""Raw email header parsing: summary fields, Received hop chain, and auth results."""

from __future__ import annotations

import re
from email import message_from_string
from email.utils import parsedate_to_datetime
from typing import Any

MAX_INPUT_LENGTH = 50_000

SUMMARY_FIELDS = ("From", "To", "Cc", "Subject", "Date", "Message-ID", "Return-Path", "Reply-To")

_FROM_RE = re.compile(r"\bfrom\s+(\S+)", re.IGNORECASE)
_BY_RE = re.compile(r"\bby\s+(\S+)", re.IGNORECASE)


def parse_email_headers(raw: str) -> dict[str, Any]:
    """Parse raw email header text and return summary fields, the Received hop chain, and auth results.

    Only the message headers are inspected -- no network calls are made and no external
    verification of SPF/DKIM/DMARC is performed, this only surfaces what the headers
    already say (e.g. from an Authentication-Results header, if present).
    """
    result: dict[str, Any] = {
        "ok": False,
        "summary": {},
        "received_hops": [],
        "hop_count": 0,
        "authentication_results": [],
        "error": None,
    }

    value = (raw or "").strip()
    if not value:
        result["error"] = "Paste raw email headers."
        return result
    if len(value) > MAX_INPUT_LENGTH:
        result["error"] = f"Input is longer than {MAX_INPUT_LENGTH} characters."
        return result

    message = message_from_string(value)

    summary = {field: message.get(field) for field in SUMMARY_FIELDS if message.get(field)}

    # Received headers appear newest-hop-first in the raw source; reverse for a
    # chronological sender -> recipient reading order.
    received_headers = list(reversed(message.get_all("Received") or []))
    hops: list[dict[str, Any]] = []
    previous_timestamp = None
    for index, header in enumerate(received_headers):
        collapsed = " ".join(header.split())
        timestamp = None
        if ";" in collapsed:
            date_part = collapsed.rsplit(";", 1)[-1].strip()
            try:
                timestamp = parsedate_to_datetime(date_part)
            except (TypeError, ValueError, OverflowError):
                timestamp = None

        delay_seconds = None
        if timestamp is not None and previous_timestamp is not None:
            delay_seconds = (timestamp - previous_timestamp).total_seconds()

        from_match = _FROM_RE.search(collapsed)
        by_match = _BY_RE.search(collapsed)
        hops.append(
            {
                "hop": index + 1,
                "from": from_match.group(1) if from_match else None,
                "by": by_match.group(1) if by_match else None,
                "timestamp": timestamp.isoformat() if timestamp else None,
                "delay_seconds": delay_seconds,
                "raw": collapsed,
            }
        )
        if timestamp is not None:
            previous_timestamp = timestamp

    auth_results = [" ".join(value.split()) for value in (message.get_all("Authentication-Results") or [])]

    result.update(
        {
            "ok": True,
            "summary": summary,
            "received_hops": hops,
            "hop_count": len(hops),
            "authentication_results": auth_results,
        }
    )
    return result
