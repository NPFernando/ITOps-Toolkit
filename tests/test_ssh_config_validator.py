from __future__ import annotations

from utils.ssh_config_validator import lint_ssh_config


def test_clean_config_has_no_issues():
    result = lint_ssh_config("Host prod\n    HostName 1.2.3.4\n    User admin\n")

    assert result["ok"] is True
    assert result["issues"] == []


def test_directive_before_any_host_block():
    result = lint_ssh_config("User root\nHost prod\n    HostName 1.2.3.4")

    assert result["ok"] is True
    assert any("before any Host/Match" in issue["message"] for issue in result["issues"])


def test_duplicate_host_pattern():
    result = lint_ssh_config("Host prod\n    User a\nHost prod\n    User b")

    assert any("Duplicate" in issue["message"] for issue in result["issues"])


def test_empty_host_block():
    result = lint_ssh_config("Host empty\nHost prod\n    User admin")

    assert any("no directives" in issue["message"] for issue in result["issues"])


def test_host_with_no_pattern():
    result = lint_ssh_config("Host\n    User admin")

    assert any("no pattern" in issue["message"] for issue in result["issues"])


def test_directive_with_no_value():
    result = lint_ssh_config("Host prod\n    User")

    assert any("no value" in issue["message"] for issue in result["issues"])


def test_comments_and_blank_lines_skipped():
    result = lint_ssh_config("# comment\n\nHost prod\n    User admin\n")

    assert result["issues"] == []


def test_match_block_treated_like_host_block():
    result = lint_ssh_config("Match host prod\n    User admin")

    assert result["issues"] == []


def test_rejects_empty_input():
    result = lint_ssh_config("")

    assert result["ok"] is False
