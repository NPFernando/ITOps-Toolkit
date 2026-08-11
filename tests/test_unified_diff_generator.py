from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from utils.unified_diff_generator import generate_unified_diff


def test_generates_diff_for_changed_text():
    result = generate_unified_diff("line1\nline2\nline3\n", "line1\nCHANGED\nline3\n")

    assert result["ok"] is True
    assert result["identical"] is False
    assert "-line2" in result["output"]
    assert "+CHANGED" in result["output"]


def test_identical_texts_report_identical():
    result = generate_unified_diff("same\n", "same\n")

    assert result["ok"] is True
    assert result["identical"] is True
    assert result["output"] == ""


def test_generated_patch_applies_with_real_patch_command():
    # The whole point of this tool is producing a patch usable by the real
    # `patch`/`git apply` tools, not just a diff-shaped string -- verified
    # directly against the real `patch` command.
    with tempfile.TemporaryDirectory() as tmp:
        original_path = Path(tmp) / "file.txt"
        original_path.write_text("line1\nline2\nline3\n")

        result = generate_unified_diff("line1\nline2\nline3\n", "line1\nCHANGED\nline3\n", original_name="file.txt", changed_name="file.txt")
        patch_path = Path(tmp) / "change.patch"
        patch_path.write_text(result["output"])

        subprocess.run(["patch", "-p0", "-d", tmp, "-i", str(patch_path)], check=True, capture_output=True)
        assert original_path.read_text() == "line1\nCHANGED\nline3\n"


def test_rejects_negative_context_lines():
    result = generate_unified_diff("a\n", "b\n", context_lines=-1)

    assert result["ok"] is False
    assert "non-negative" in result["error"]


def test_rejects_both_inputs_empty():
    result = generate_unified_diff("", "")

    assert result["ok"] is False
