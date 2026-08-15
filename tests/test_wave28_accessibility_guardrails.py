from __future__ import annotations

import os
from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from utils import roadmap


PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_PAGE = str(PROJECT_ROOT / "app.py")
ROADMAP_PAGE = str(PROJECT_ROOT / "pages" / "10_Roadmap_Feedback.py")
CSR_PAGE = str(PROJECT_ROOT / "pages" / "120_CSR_Generator.py")
CAA_PAGE = str(PROJECT_ROOT / "pages" / "121_CAA_Record_Builder.py")
GIT_PAGE = str(PROJECT_ROOT / "pages" / "139_Git_Command_Cheat_Sheet.py")
BIP39_PAGE = str(PROJECT_ROOT / "pages" / "140_BIP39_Mnemonic_Generator_Validator.py")


@pytest.fixture(autouse=True)
def _clear_cache_scope(monkeypatch):
    st.cache_data.clear()
    monkeypatch.setenv("ITOPS_CACHE_SCOPE", os.getenv("PYTEST_CURRENT_TEST", "runtime"))


def _markdown(app: AppTest) -> str:
    return " ".join(item.value for item in app.markdown)


def test_wave28_home_and_roadmap_keep_explicit_neutral_warning_success_outcomes(monkeypatch):
    app = AppTest.from_file(APP_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    markdown = _markdown(app)
    assert "Outcome: quick access ready" in markdown
    assert "tool-status-note-neutral" in markdown
    assert 'role="status"' in markdown

    search = next(widget for widget in app.text_input if widget.key == "tool_search")
    search.set_value("tool-that-does-not-exist-zzz").run()
    assert not app.exception
    markdown = _markdown(app)
    assert "Outcome: catalog filters need adjustment" in markdown
    assert "tool-status-note-warning" in markdown
    assert 'role="alert"' in markdown

    search = next(widget for widget in app.text_input if widget.key == "tool_search")
    search.set_value("").run()
    next(button for button in app.button if button.label == "Show all tools").click().run()
    assert not app.exception
    markdown = _markdown(app)
    assert "Outcome: full catalog visible" in markdown
    assert "tool-status-note-success" in markdown

    monkeypatch.setattr(
        roadmap,
        "load_roadmap_board",
        lambda repo_url=None: roadmap.RoadmapBoard(roadmap.ROADMAP_ITEMS),
    )
    roadmap_app = AppTest.from_file(ROADMAP_PAGE, default_timeout=30)
    roadmap_app.run()
    assert not roadmap_app.exception
    markdown = _markdown(roadmap_app)
    assert "Outcome: roadmap cache checked" in markdown
    assert "Outcome: roadmap sync complete" in markdown
    assert "tool-status-note-success" in markdown


def test_wave28_csr_and_caa_pages_use_explicit_outcome_wording():
    csr_app = AppTest.from_file(CSR_PAGE, default_timeout=30)
    csr_app.run()
    assert not csr_app.exception
    markdown = _markdown(csr_app)
    assert "Outcome: CSR generation ready" in markdown
    assert "tool-status-note-neutral" in markdown

    next(button for button in csr_app.button if button.label == "Generate CSR").click().run()
    assert not csr_app.exception
    markdown = _markdown(csr_app)
    assert "Outcome: CSR generation blocked" in markdown
    assert "tool-status-note-warning" in markdown

    csr_app.text_input[0].set_value("example.com")
    next(button for button in csr_app.button if button.label == "Generate CSR").click().run()
    assert not csr_app.exception
    markdown = _markdown(csr_app)
    assert "Outcome: CSR generation complete" in markdown
    assert "tool-status-note-success" in markdown

    caa_app = AppTest.from_file(CAA_PAGE, default_timeout=30)
    caa_app.run()
    assert not caa_app.exception
    markdown = _markdown(caa_app)
    assert "Outcome: CAA record builder ready" in markdown
    assert "tool-status-note-neutral" in markdown

    next(button for button in caa_app.button if button.label == "Build record").click().run()
    assert not caa_app.exception
    markdown = _markdown(caa_app)
    assert "Outcome: CAA record build blocked" in markdown
    assert "tool-status-note-warning" in markdown

    caa_app.text_input[0].set_value("letsencrypt.org")
    next(button for button in caa_app.button if button.label == "Build record").click().run()
    assert not caa_app.exception
    markdown = _markdown(caa_app)
    assert "Outcome: CAA record build complete" in markdown
    assert "tool-status-note-success" in markdown


def test_wave28_git_and_bip39_pages_keep_outcome_semantics():
    git_app = AppTest.from_file(GIT_PAGE, default_timeout=30)
    git_app.run()
    assert not git_app.exception
    markdown = _markdown(git_app)
    assert "Outcome: command reference ready" in markdown
    assert "tool-status-note-neutral" in markdown

    git_app.text_input[0].set_value("no-match-git-command")
    next(button for button in git_app.button if button.label == "Show matching commands").click().run()
    assert not git_app.exception
    markdown = _markdown(git_app)
    assert "Outcome: command filtering blocked" in markdown
    assert "tool-status-note-warning" in markdown

    bip39_app = AppTest.from_file(BIP39_PAGE, default_timeout=30)
    bip39_app.run()
    assert not bip39_app.exception
    next(button for button in bip39_app.button if button.label == "Generate mnemonic").click().run()
    assert not bip39_app.exception
    markdown = _markdown(bip39_app)
    assert "Outcome: mnemonic generation complete" in markdown
    assert "tool-status-note-success" in markdown

    bip39_app.text_area[0].set_value("invalid words here")
    next(button for button in bip39_app.button if button.label == "Validate mnemonic").click().run()
    assert not bip39_app.exception
    markdown = _markdown(bip39_app)
    assert "Outcome: mnemonic validation blocked" in markdown
    assert "tool-status-note-warning" in markdown
