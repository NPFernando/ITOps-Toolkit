from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import roadmap


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = PROJECT_ROOT / "pages"


def _run(rel_path: str) -> AppTest:
    app = AppTest.from_file(str(PROJECT_ROOT / rel_path), default_timeout=30)
    app.run()
    assert not app.exception
    return app


def _run_page(page_name: str) -> AppTest:
    app = AppTest.from_file(str(PAGES_DIR / page_name), default_timeout=30)
    app.run()
    assert not app.exception
    return app


def _markdown(app: AppTest) -> str:
    return " ".join(item.value for item in app.markdown)


def test_wave26_home_page_uses_explicit_neutral_warning_success_statuses():
    app = _run("app.py")

    md = _markdown(app)
    assert "tool-status-note-neutral" in md
    assert "Outcome: quick access ready" in md
    assert 'role="status"' in md
    assert 'aria-live="polite"' in md

    search = next(widget for widget in app.text_input if widget.key == "tool_search")
    search.set_value("tool-that-does-not-exist-zzz").run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: catalog filters need adjustment" in md
    assert 'role="alert"' in md

    search = next(widget for widget in app.text_input if widget.key == "tool_search")
    search.set_value("").run()
    next(button for button in app.button if button.label == "Show all tools").click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: full catalog visible" in md


def test_wave26_roadmap_page_uses_explicit_neutral_success_statuses(monkeypatch):
    monkeypatch.setattr(
        roadmap,
        "load_roadmap_board",
        lambda repo_url=None: roadmap.RoadmapBoard(roadmap.ROADMAP_ITEMS),
    )
    app = _run_page("10_Roadmap_Feedback.py")
    md = _markdown(app)

    assert "tool-status-note-neutral" in md
    assert "Outcome: roadmap cache checked" in md
    assert "tool-status-note-success" in md
    assert "Outcome: roadmap sync complete" in md
    assert 'role="status"' in md
    assert 'aria-live="polite"' in md


def test_wave26_tool_pages_preserve_explicit_accessibility_status_markers():
    for page_name in (
        "139_Git_Command_Cheat_Sheet.py",
        "140_BIP39_Mnemonic_Generator_Validator.py",
        "141_Lorem_Ipsum_Generator.py",
        "142_Text_to_Binary_Hex_Octal_Converter.py",
    ):
        app = _run_page(page_name)
        md = _markdown(app)
        assert "tool-status-note-neutral" in md
        assert 'role="status"' in md
        assert 'aria-live="polite"' in md
