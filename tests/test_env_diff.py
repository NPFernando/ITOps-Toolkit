from __future__ import annotations

from utils.env_diff import diff_env


def test_detects_added_removed_changed():
    result = diff_env("A=1\nB=2\nC=3", "A=1\nB=changed\nD=4")

    assert result["ok"] is True
    assert result["added"] == [{"key": "D", "value": "4"}]
    assert result["removed"] == [{"key": "C", "value": "3"}]
    assert result["changed"] == [{"key": "B", "old": "2", "new": "changed"}]
    assert result["unchanged_count"] == 1


def test_identical_files_have_no_differences():
    result = diff_env("A=1\nB=2", "A=1\nB=2")

    assert result["ok"] is True
    assert result["added"] == []
    assert result["removed"] == []
    assert result["changed"] == []
    assert result["unchanged_count"] == 2


def test_skips_comments_and_blank_lines():
    result = diff_env("# comment\nA=1\n\nB=2", "A=1\nB=2")

    assert result["ok"] is True
    assert result["unchanged_count"] == 2


def test_handles_export_prefix():
    result = diff_env("export A=1", "A=1")

    assert result["ok"] is True
    assert result["unchanged_count"] == 1


def test_rejects_empty_input():
    result = diff_env("", "A=1")

    assert result["ok"] is False
    assert "Paste both" in result["error"]


def test_rejects_no_kv_lines():
    result = diff_env("# just a comment", "# also a comment")

    assert result["ok"] is False
    assert "No KEY=VALUE lines" in result["error"]
