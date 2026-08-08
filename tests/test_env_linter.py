from __future__ import annotations

from utils.env_linter import lint_env


def test_lint_env_rejects_empty_input():
    result = lint_env("")

    assert result["ok"] is False
    assert result["error"] == "Paste .env content to lint."


def test_lint_env_clean_file_has_no_issues():
    result = lint_env("# a comment\nFOO=bar\nexport BAR=\"quoted value\"\n")

    assert result["ok"] is True
    assert result["issues"] == []


def test_lint_env_flags_duplicate_keys():
    result = lint_env("FOO=bar\nFOO=baz\n")

    messages = [i["message"] for i in result["issues"] if i["line"] == 2]
    assert any("Duplicate key 'FOO'" in m and "line 1" in m for m in messages)


def test_lint_env_flags_missing_equals():
    result = lint_env("NOEQUALS\n")

    assert result["issues"] == [{"line": 1, "message": "Missing '=' -- not a valid KEY=VALUE line."}]


def test_lint_env_flags_key_whitespace_before_equals():
    result = lint_env("FOO ='bar'\n")

    assert any("whitespace before '='" in i["message"] for i in result["issues"])


def test_lint_env_flags_invalid_identifier_key():
    result = lint_env("1FOO=bar\n")

    assert any("not a valid identifier" in i["message"] for i in result["issues"])


def test_lint_env_flags_trailing_whitespace():
    result = lint_env("FOO=bar   \n")

    assert any(i["message"] == "Trailing whitespace." for i in result["issues"])


def test_lint_env_flags_unterminated_quote():
    result = lint_env('FOO="bar\n')

    assert any("Unterminated" in i["message"] for i in result["issues"])


def test_lint_env_flags_unquoted_value_with_spaces():
    result = lint_env("FOO=hello world\n")

    assert any("Unquoted value contains spaces" in i["message"] for i in result["issues"])


def test_lint_env_ignores_comments_and_blank_lines():
    result = lint_env("\n# comment\n\nFOO=bar\n")

    assert result["issues"] == []
