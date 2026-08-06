from __future__ import annotations

import hashlib
from pathlib import Path

from streamlit.testing.v1 import AppTest

FILE_INTEGRITY_PAGE = str(Path(__file__).resolve().parent.parent / "pages" / "43_File_Integrity_Comparator.py")


def _run_page() -> AppTest:
    app = AppTest.from_file(FILE_INTEGRITY_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    return app


def test_file_integrity_page_requires_file_a():
    app = _run_page()
    app.button[0].click().run()
    assert not app.exception
    assert any("Upload at least File A" in e.value for e in app.error)


def test_file_integrity_page_identical_files_match():
    app = _run_page()
    uploaders = app.get("file_uploader")
    file_a = next(f for f in uploaders if f.key == "file_integrity_a")
    file_b = next(f for f in uploaders if f.key == "file_integrity_b")
    file_a.upload("a.txt", b"hello world")
    file_b.upload("b.txt", b"hello world")

    app.button[0].click().run()
    assert not app.exception
    assert any("identical" in s.body.lower() for s in app.success)


def test_file_integrity_page_different_files_do_not_match():
    app = _run_page()
    uploaders = app.get("file_uploader")
    file_a = next(f for f in uploaders if f.key == "file_integrity_a")
    file_b = next(f for f in uploaders if f.key == "file_integrity_b")
    file_a.upload("a.txt", b"hello world")
    file_b.upload("b.txt", b"different content")

    app.button[0].click().run()
    assert not app.exception
    assert any("differ" in e.value.lower() for e in app.error)


def test_file_integrity_page_matches_expected_hash():
    app = _run_page()
    uploaders = app.get("file_uploader")
    file_a = next(f for f in uploaders if f.key == "file_integrity_a")
    file_a.upload("a.txt", b"hello world")

    expected_input = next(t for t in app.text_input if t.label == "Expected hash (optional)")
    expected_input.set_value(hashlib.sha256(b"hello world").hexdigest())

    app.button[0].click().run()
    assert not app.exception
    assert any("Matches the expected hash (SHA256)" in s.body for s in app.success)


def test_file_integrity_page_wrong_expected_hash_does_not_match():
    app = _run_page()
    uploaders = app.get("file_uploader")
    file_a = next(f for f in uploaders if f.key == "file_integrity_a")
    file_a.upload("a.txt", b"hello world")

    expected_input = next(t for t in app.text_input if t.label == "Expected hash (optional)")
    expected_input.set_value("0" * 64)

    app.button[0].click().run()
    assert not app.exception
    assert any("Does not match" in e.value for e in app.error)
