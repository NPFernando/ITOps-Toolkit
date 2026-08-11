from __future__ import annotations

from utils.gitignore_tester import check_paths


def _ignored_map(result):
    return {row["path"]: row["ignored"] for row in result["results"]}


def test_wildcard_matches_at_any_depth():
    result = check_paths("*.log", "app.log\nsrc/app.log")

    assert result["ok"] is True
    assert _ignored_map(result) == {"app.log": True, "src/app.log": True}


def test_leading_slash_anchors_to_root():
    result = check_paths("/TODO", "TODO\nsub/TODO")

    assert _ignored_map(result) == {"TODO": True, "sub/TODO": False}


def test_middle_slash_anchors_pattern_too():
    # Regression guard: only a pattern with NO slash (besides a possible
    # trailing one) matches at any depth -- a slash anywhere in the middle
    # anchors the pattern to the .gitignore's own directory, same as a
    # leading slash. Verified directly against real `git check-ignore`.
    result = check_paths("doc/*.txt", "doc/notes.txt\nsub/doc/notes.txt")

    assert _ignored_map(result) == {"doc/notes.txt": True, "sub/doc/notes.txt": False}


def test_trailing_slash_is_directory_only_but_not_anchored():
    result = check_paths("build/", "build\nsrc/build\nbuild.txt")

    assert _ignored_map(result) == {"build": True, "src/build": True, "build.txt": False}


def test_double_star_matches_zero_or_more_directories():
    # Verified directly against real `git check-ignore`: "**" can match
    # zero path segments, so doc/**/*.txt matches doc/notes.txt directly.
    result = check_paths("doc/**/*.txt", "doc/notes.txt\ndoc/server/arch.txt")

    assert _ignored_map(result) == {"doc/notes.txt": True, "doc/server/arch.txt": True}


def test_negation_re_includes_a_path():
    result = check_paths("*.log\n!important.log", "app.log\nimportant.log\nsrc/app.log")

    assert _ignored_map(result) == {"app.log": True, "important.log": False, "src/app.log": True}


def test_comments_and_blank_lines_are_skipped():
    result = check_paths("# comment\n\n*.log", "app.log")

    assert _ignored_map(result) == {"app.log": True}


def test_last_matching_pattern_wins():
    result = check_paths("*.log\n*.log\n!*.log", "app.log")

    assert _ignored_map(result) == {"app.log": False}


def test_bracket_character_class():
    # Regression: [...] classes were being re.escape()'d as literal
    # characters instead of translated into a regex character class, so
    # "*.[oa]" matched nothing at all. Verified directly against real
    # `git check-ignore`.
    result = check_paths("*.[oa]", "file.o\nfile.a\nfile.b")

    assert _ignored_map(result) == {"file.o": True, "file.a": True, "file.b": False}


def test_negated_bracket_character_class():
    result = check_paths("[!abc].txt", "d.txt\na.txt")

    assert _ignored_map(result) == {"d.txt": True, "a.txt": False}


def test_question_mark_matches_single_character():
    result = check_paths("file?.txt", "file1.txt\nfile12.txt")

    assert _ignored_map(result) == {"file1.txt": True, "file12.txt": False}


def test_rejects_empty_gitignore():
    result = check_paths("", "app.log")

    assert result["ok"] is False
    assert "Paste .gitignore" in result["error"]


def test_rejects_empty_paths():
    result = check_paths("*.log", "")

    assert result["ok"] is False
    assert "Enter at least one path" in result["error"]


def test_reports_matched_pattern():
    result = check_paths("*.log", "app.log")

    assert result["results"][0]["matched_pattern"] == "*.log"
