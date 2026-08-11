from __future__ import annotations

from utils.caa_record_builder import build_caa_record


def test_builds_issue_record():
    result = build_caa_record("issue", "letsencrypt.org")

    assert result["ok"] is True
    assert result["record"] == '0 issue "letsencrypt.org"'
    assert result["zone_line"] == '@ CAA 0 issue "letsencrypt.org"'


def test_critical_flag_sets_128():
    result = build_caa_record("issue", "letsencrypt.org", critical=True)

    assert result["record"].startswith("128 ")


def test_semicolon_value_allowed_for_issue():
    result = build_caa_record("issue", ";")

    assert result["ok"] is True
    assert result["record"] == '0 issue ";"'


def test_iodef_record():
    result = build_caa_record("iodef", "mailto:security@example.com")

    assert result["ok"] is True
    assert result["record"] == '0 iodef "mailto:security@example.com"'


def test_rejects_unknown_tag():
    result = build_caa_record("bogus", "value")

    assert result["ok"] is False
    assert "Unknown tag" in result["error"]


def test_rejects_empty_value():
    result = build_caa_record("issue", "")

    assert result["ok"] is False
