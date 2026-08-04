from utils import email_header_tools

SAMPLE_HEADERS = """\
Received: by mail.example.com with SMTP id abc123; Fri, 31 Jul 2026 10:02:15 +0000
Received: from mx.example.com (mx.example.com [203.0.113.5])
    by mail.example.com with ESMTPS id def456
    for <user@example.com>; Fri, 31 Jul 2026 10:02:10 +0000
Received: from sender.example.org (sender.example.org [198.51.100.9])
    by mx.example.com with ESMTP id ghi789
    for <user@example.com>; Fri, 31 Jul 2026 10:02:00 +0000
Authentication-Results: mx.example.com;
    spf=pass smtp.mailfrom=sender.example.org;
    dkim=pass header.d=example.org;
    dmarc=pass header.from=example.org
From: Sender Name <sender@example.org>
To: user@example.com
Subject: Test message
Date: Fri, 31 Jul 2026 10:01:55 +0000
Message-ID: <abc123@sender.example.org>

Body text goes here.
"""


def test_parse_email_headers_extracts_summary_fields():
    result = email_header_tools.parse_email_headers(SAMPLE_HEADERS)

    assert result["ok"] is True
    assert result["summary"]["From"] == "Sender Name <sender@example.org>"
    assert result["summary"]["Subject"] == "Test message"
    assert result["summary"]["Message-ID"] == "<abc123@sender.example.org>"


def test_parse_email_headers_orders_hops_chronologically():
    result = email_header_tools.parse_email_headers(SAMPLE_HEADERS)

    assert result["hop_count"] == 3
    hops = result["received_hops"]
    # First hop chronologically is sender.example.org -> mx.example.com (the last Received line in the raw source).
    assert hops[0]["from"] == "sender.example.org"
    assert hops[0]["by"] == "mx.example.com"
    assert hops[-1]["by"] == "mail.example.com"


def test_parse_email_headers_computes_hop_delays():
    result = email_header_tools.parse_email_headers(SAMPLE_HEADERS)

    hops = result["received_hops"]
    assert hops[0]["delay_seconds"] is None  # first hop has no prior timestamp to diff against
    assert hops[1]["delay_seconds"] == 10.0
    assert hops[2]["delay_seconds"] == 5.0


def test_parse_email_headers_extracts_authentication_results():
    result = email_header_tools.parse_email_headers(SAMPLE_HEADERS)

    assert len(result["authentication_results"]) == 1
    assert "spf=pass" in result["authentication_results"][0]
    assert "dkim=pass" in result["authentication_results"][0]


def test_parse_email_headers_validation_errors():
    assert email_header_tools.parse_email_headers("")["error"] == "Paste raw email headers."
    result = email_header_tools.parse_email_headers("a" * (email_header_tools.MAX_INPUT_LENGTH + 1))
    assert "longer than" in result["error"]


def test_parse_email_headers_handles_no_received_headers():
    result = email_header_tools.parse_email_headers("From: a@example.com\nSubject: hi\n")

    assert result["ok"] is True
    assert result["hop_count"] == 0
    assert result["received_hops"] == []
