from __future__ import annotations

from utils.wsl_path_converter import TARGETS, convert_path


def test_windows_to_wsl():
    result = convert_path(r"C:\Users\naveen\file.txt", TARGETS[0])

    assert result["ok"] is True
    assert result["output"] == "/mnt/c/Users/naveen/file.txt"


def test_windows_to_gitbash():
    result = convert_path(r"C:\Users\naveen\file.txt", TARGETS[1])

    assert result["ok"] is True
    assert result["output"] == "/c/Users/naveen/file.txt"


def test_wsl_to_windows():
    result = convert_path("/mnt/c/Users/naveen/file.txt", TARGETS[2])

    assert result["ok"] is True
    assert result["output"] == r"C:\Users\naveen\file.txt"


def test_gitbash_to_windows():
    result = convert_path("/c/Users/naveen/file.txt", TARGETS[2])

    assert result["ok"] is True
    assert result["output"] == r"C:\Users\naveen\file.txt"


def test_wsl_to_gitbash():
    result = convert_path("/mnt/c/Users/naveen/file.txt", TARGETS[1])

    assert result["ok"] is True
    assert result["output"] == "/c/Users/naveen/file.txt"


def test_bare_drive_root_round_trips():
    # Regression: a bare drive root ("/mnt/c" or "C:\") used to only work
    # in one direction -- Windows root -> WSL root worked, but the
    # resulting "/mnt/c" (no trailing slash/segment) couldn't be converted
    # back, since the parser required a trailing "/..." segment.
    assert convert_path("/mnt/c", TARGETS[2])["output"] == "C:\\"
    assert convert_path("C:\\", TARGETS[0])["output"] == "/mnt/c"
    assert convert_path("/c", TARGETS[2])["output"] == "C:\\"


def test_rejects_unrecognized_path():
    result = convert_path("not/a/windows/path", TARGETS[0])

    assert result["ok"] is False
    assert "Could not recognize" in result["error"]


def test_rejects_empty_input():
    result = convert_path("", TARGETS[0])

    assert result["ok"] is False


def test_rejects_unknown_target():
    result = convert_path(r"C:\foo", "bogus")

    assert result["ok"] is False
    assert "Unknown target" in result["error"]
