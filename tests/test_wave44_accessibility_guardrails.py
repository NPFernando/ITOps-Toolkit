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


def _captions(app: AppTest) -> str:
    return " ".join(item.value for item in app.caption)


def test_wave44_status_helper_semantics_guardrails():
    source = (PROJECT_ROOT / "utils/ui.py").read_text(encoding="utf-8")
    assert 'role = "alert" if normalized_tone == "warning" else "status"' in source
    assert 'aria_live = "assertive" if normalized_tone == "warning" else "polite"' in source
    assert 'aria_label = f"{normalized_tone.capitalize()} status: {title}"' in source
    assert 'aria-atomic="true"' in source
    assert 'tabindex="0"' in source


def test_wave44_read_order_and_status_live_regions_are_deterministic():
    home_app = AppTest.from_file(APP_PAGE, default_timeout=30)
    home_app.run()
    assert not home_app.exception
    home_markdown = _markdown(home_app)
    home_captions = _captions(home_app)
    assert "Read order: confirm browsing setup, run this full-width action, then review the outcome note before scanning results." in home_captions
    assert "Status tip: if the outcome says filters need adjustment, clear one filter and try again." in home_captions
    assert "Outcome: quick access ready" in home_markdown
    assert 'aria-label="Neutral status: Outcome: quick access ready"' in home_markdown
    assert 'role="status"' in home_markdown
    assert 'aria-live="polite"' in home_markdown
    assert 'aria-atomic="true"' in home_markdown
    assert 'tabindex="0"' in home_markdown

    roadmap_app = AppTest.from_file(ROADMAP_PAGE, default_timeout=30)
    roadmap_app.run()
    assert not roadmap_app.exception
    roadmap_markdown = _markdown(roadmap_app)
    roadmap_captions = _captions(roadmap_app)
    assert "Read order: set search + category, apply filters, then check outcome status before scanning cards." in roadmap_captions
    assert "Status tip: outcome notes tell you whether results are ready or filters need adjustment." in roadmap_captions
    assert "Outcome: public feedback safety reminder" in roadmap_markdown
    assert 'aria-label="Warning status: Outcome: public feedback safety reminder"' in roadmap_markdown
    assert 'role="alert"' in roadmap_markdown
    assert 'aria-live="assertive"' in roadmap_markdown
    assert 'aria-atomic="true"' in roadmap_markdown
    assert 'tabindex="0"' in roadmap_markdown

    lorem_app = AppTest.from_file(LOREM_PAGE, default_timeout=30)
    lorem_app.run()
    assert not lorem_app.exception
    lorem_markdown = _markdown(lorem_app)
    lorem_captions = _captions(lorem_app)
    assert "Read order: choose output shape and seed, run generate, then review the outcome note and output." in lorem_captions
    assert "Status tip: neutral means waiting for input; success means text is ready to copy." in lorem_captions
    assert "Outcome: lorem generation awaiting input" in lorem_markdown
    assert 'aria-label="Neutral status: Outcome: lorem generation awaiting input"' in lorem_markdown
    assert 'role="status"' in lorem_markdown
    assert 'aria-live="polite"' in lorem_markdown
    assert 'aria-atomic="true"' in lorem_markdown
    assert 'tabindex="0"' in lorem_markdown

    text_app = AppTest.from_file(TEXT_RADIX_PAGE, default_timeout=30)
    text_app.run()
    assert not text_app.exception
    text_markdown = _markdown(text_app)
    text_captions = _captions(text_app)
    assert "Read order: enter source text, run convert, then check status and compare all three encoded outputs." in text_captions
    assert "Status tip: warning means input is missing; success means all encodings are ready." in text_captions
    assert "Outcome: conversion awaiting input" in text_markdown
    assert 'aria-label="Neutral status: Outcome: conversion awaiting input"' in text_markdown
    assert 'role="status"' in text_markdown
    assert 'aria-live="polite"' in text_markdown
    assert 'aria-atomic="true"' in text_markdown
    assert 'tabindex="0"' in text_markdown
