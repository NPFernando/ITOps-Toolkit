import time

from utils import diff_tools


def test_compare_text_reports_added_and_removed_lines():
    result = diff_tools.compare_text("line1\nline2\nline3", "line1\nline2 changed\nline3\nline4")

    assert result["ok"] is True
    assert result["added"] == 2
    assert result["removed"] == 1
    types = [line["type"] for line in result["lines"]]
    assert "removed" in types
    assert "added" in types
    assert "equal" in types


def test_compare_text_identical_input_has_full_similarity():
    result = diff_tools.compare_text("same\ntext\nhere", "same\ntext\nhere")

    assert result["ok"] is True
    assert result["similarity"] == 100.0
    assert result["added"] == 0
    assert result["removed"] == 0


def test_compare_text_ignore_whitespace_treats_trimmed_lines_as_equal():
    with_ws = diff_tools.compare_text("hello  ", "hello", ignore_whitespace=False)
    without_ws = diff_tools.compare_text("hello  ", "hello", ignore_whitespace=True)

    assert with_ws["added"] == 1 and with_ws["removed"] == 1
    assert without_ws["added"] == 0 and without_ws["removed"] == 0


def test_compare_text_rejects_oversized_input():
    oversized = "a" * (diff_tools.MAX_INPUT_LENGTH + 1)

    result = diff_tools.compare_text(oversized, "short")

    assert result["ok"] is False
    assert "longer than" in result["error"]


def test_compare_text_rejects_too_many_lines():
    too_many = "\n".join("x" for _ in range(diff_tools.MAX_LINES + 1))

    result = diff_tools.compare_text(too_many, "short")

    assert result["ok"] is False
    assert "more than" in result["error"]


def test_compare_text_handles_pathological_repeated_lines_within_timeout():
    # Confirmed manually: difflib.SequenceMatcher with autojunk=False on this
    # shape of input (many repeated lines + one differing line) does not
    # finish within 15s. The default autojunk=True resolves it in
    # milliseconds, but the process-timeout backstop exists precisely so a
    # heuristic isn't the only thing standing between this and a hung
    # worker on a public server.
    start = time.time()
    a = ("X\n" * 10_000) + "unique_a"
    b = ("X\n" * 10_000) + "unique_b"
    result = diff_tools.compare_text(a, b)
    elapsed = time.time() - start

    assert result["ok"] is True
    assert elapsed < diff_tools.DIFF_TIMEOUT_SECONDS + 5
