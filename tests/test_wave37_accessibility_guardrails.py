from __future__ import annotations

import os
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_PAGE = str(PROJECT_ROOT / "app.py")
ROADMAP_PAGE = str(PROJECT_ROOT / "pages" / "10_Roadmap_Feedback.py")
LOREM_PAGE = str(PROJECT_ROOT / "pages" / "141_Lorem_Ipsum_Generator.py")
TEXT_RADIX_PAGE = str(PROJECT_ROOT / "pages" / "142_Text_to_Binary_Hex_Octal_Converter.py")


@pytest.fixture(autouse=True)
def _clear_cache_scope(monkeypatch):
    st.cache_data.clear()
    monkeypatch.setenv("ITOPS_CACHE_SCOPE", os.getenv("PYTEST_CURRENT_TEST", "runtime"))


def _markdown(app: AppTest) -> str:
    return " ".join(item.value for item in app.markdown)


def _assert_polite_status_live_region(markdown: str) -> None:
    assert 'role="status"' in markdown
    assert 'aria-live="polite"' in markdown
    assert 'aria-atomic="true"' in markdown
    assert 'tabindex="0"' in markdown


def _assert_warning_status_live_region(markdown: str) -> None:
    assert 'role="alert"' in markdown
    assert 'aria-live="assertive"' in markdown
    assert 'aria-atomic="true"' in markdown
    assert 'tabindex="0"' in markdown


def test_wave37_home_and_roadmap_status_semantics_and_live_regions():
    app = AppTest.from_file(APP_PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = _markdown(app)
    assert "Outcome: quick access ready" in markdown
    assert "tool-status-note-neutral" in markdown
    _assert_polite_status_live_region(markdown)

    search = next(widget for widget in app.text_input if widget.key == "tool_search")
    search.set_value("tool-that-does-not-exist-zzz").run()
    assert not app.exception

    markdown = _markdown(app)
    assert "Outcome: catalog filters need adjustment" in markdown
    assert "tool-status-note-warning" in markdown
    _assert_warning_status_live_region(markdown)

    roadmap_app = AppTest.from_file(ROADMAP_PAGE, default_timeout=30)
    roadmap_app.run()
    assert not roadmap_app.exception

    roadmap_markdown = _markdown(roadmap_app)
    assert "Outcome: public feedback safety reminder" in roadmap_markdown
    assert "Outcome: AI Recommended label clarified" in roadmap_markdown
    assert "tool-status-note-warning" in roadmap_markdown
    assert "tool-status-note-neutral" in roadmap_markdown
    assert 'aria-label="Warning status: Outcome: public feedback safety reminder"' in roadmap_markdown
    assert 'aria-label="Neutral status: Outcome: AI Recommended label clarified"' in roadmap_markdown
    _assert_warning_status_live_region(roadmap_markdown)
    _assert_polite_status_live_region(roadmap_markdown)


def test_wave37_lorem_and_text_converter_keep_deterministic_a11y_states():
    lorem_app = AppTest.from_file(LOREM_PAGE, default_timeout=30)
    lorem_app.run()
    assert not lorem_app.exception

    markdown = _markdown(lorem_app)
    assert "Outcome: lorem generation awaiting input" in markdown
    assert "tool-status-note-neutral" in markdown
    _assert_polite_status_live_region(markdown)

    seed = next(widget for widget in lorem_app.text_input if widget.key == "lorem_seed")
    seed.set_value("wave32")
    count = next(widget for widget in lorem_app.number_input if widget.key == "lorem_count")
    count.set_value(6)
    next(widget for widget in lorem_app.button if widget.label == "Generate lorem ipsum").click().run()
    assert not lorem_app.exception

    assert lorem_app.code[0].value == "enim qui cupidatat mollit labore cillum"
    markdown = _markdown(lorem_app)
    assert "Outcome: lorem text generated" in markdown
    assert "tool-status-note-success" in markdown
    assert 'aria-label="Success status: Outcome: lorem text generated"' in markdown
    _assert_polite_status_live_region(markdown)

    text_app = AppTest.from_file(TEXT_RADIX_PAGE, default_timeout=30)
    text_app.run()
    assert not text_app.exception

    markdown = _markdown(text_app)
    assert "Outcome: conversion awaiting input" in markdown
    assert "tool-status-note-neutral" in markdown
    _assert_polite_status_live_region(markdown)

    next(widget for widget in text_app.button if widget.label == "Convert text").click().run()
    assert not text_app.exception

    markdown = _markdown(text_app)
    assert "Outcome: text conversion blocked" in markdown
    assert "tool-status-note-warning" in markdown
    assert 'aria-label="Warning status: Outcome: text conversion blocked"' in markdown
    _assert_warning_status_live_region(markdown)

    text_app.text_area[0].set_value("Az")
    next(widget for widget in text_app.button if widget.label == "Convert text").click().run()
    assert not text_app.exception

    output = text_app.code[0].value
    assert "Binary: 01000001 01111010" in output
    assert "Hex: 41 7A" in output
    assert "Octal: 101 172" in output
    markdown = _markdown(text_app)
    assert "Outcome: text conversion complete" in markdown
    assert "tool-status-note-success" in markdown
    assert 'aria-label="Success status: Outcome: text conversion complete"' in markdown
    _assert_polite_status_live_region(markdown)


def test_wave37_read_order_guardrails_for_mapped_pages():
    expected_read_order = {
        "app.py": 'st.caption("Read order: review browsing setup, run this full-width action, then verify status notes and tool results.")',
        "pages/10_Roadmap_Feedback.py": 'st.caption("Read order: set search + category, apply filters, then review status outcomes before scanning cards.")',
        "pages/141_Lorem_Ipsum_Generator.py": 'st.caption("Read order: configure output shape and seed, run generate, then review status guidance and output.")',
        "pages/142_Text_to_Binary_Hex_Octal_Converter.py": 'st.caption("Read order: enter source text, run convert, then confirm status and compare all three encoded outputs.")',
    }
    for rel_path, snippet in expected_read_order.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert snippet in source, f"{rel_path}: missing deterministic read-order guidance"
