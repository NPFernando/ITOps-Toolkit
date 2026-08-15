from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from utils import roadmap


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ROADMAP_PAGE = str(PROJECT_ROOT / "pages" / "10_Roadmap_Feedback.py")
APP_PAGE = str(PROJECT_ROOT / "app.py")
GIT_PAGE = str(PROJECT_ROOT / "pages" / "139_Git_Command_Cheat_Sheet.py")
BIP39_PAGE = str(PROJECT_ROOT / "pages" / "140_BIP39_Mnemonic_Generator_Validator.py")
LOREM_PAGE = str(PROJECT_ROOT / "pages" / "141_Lorem_Ipsum_Generator.py")
TEXT_RADIX_PAGE = str(PROJECT_ROOT / "pages" / "142_Text_to_Binary_Hex_Octal_Converter.py")


def _markdown(app: AppTest) -> str:
    return " ".join(item.value for item in app.markdown)


def test_wave27_home_statuses_keep_explicit_neutral_warning_success_semantics():
    app = AppTest.from_file(APP_PAGE, default_timeout=30)
    app.run()
    assert not app.exception

    markdown = _markdown(app)
    assert "Outcome: quick access ready" in markdown
    assert "tool-status-note-neutral" in markdown
    assert 'role="status"' in markdown
    assert 'aria-live="polite"' in markdown

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


def test_wave27_roadmap_filters_apply_via_full_width_action_with_explicit_states(monkeypatch):
    monkeypatch.setattr(
        roadmap,
        "load_roadmap_board",
        lambda repo_url=None: roadmap.RoadmapBoard(
            (
                roadmap.RoadmapItem(
                    title="DNS export",
                    category="Reports",
                    status="Planned",
                    votes=3,
                    description="Export DNS checks.",
                    rationale="Useful for audits.",
                    source="seed",
                ),
                roadmap.RoadmapItem(
                    title="Alert digest",
                    category="Operations",
                    status="In Progress",
                    votes=7,
                    description="Daily digest.",
                    rationale="Reduce alert fatigue.",
                    source="seed",
                ),
            )
        ),
    )

    app = AppTest.from_file(ROADMAP_PAGE, default_timeout=30)
    app.run()
    assert not app.exception
    assert any(button.label == "Apply filters" for button in app.button)
    assert "2 roadmap items shown" in _markdown(app)
    assert "Outcome: roadmap board ready" in _markdown(app)
    assert "tool-status-note-neutral" in _markdown(app)

    search = next(widget for widget in app.text_input if widget.label == "Search roadmap")
    search.set_value("no-such-roadmap-item").run()
    assert not app.exception
    assert "2 roadmap items shown" in _markdown(app)

    next(button for button in app.button if button.label == "Apply filters").click().run()
    assert not app.exception
    assert "0 roadmap items shown" in _markdown(app)
    assert "Outcome: roadmap filters need adjustment" in _markdown(app)
    assert "tool-status-note-warning" in _markdown(app)
    assert 'role="alert"' in _markdown(app)
    assert 'role="status"' in _markdown(app)


def test_wave27_git_bip39_lorem_and_text_converter_status_wording_is_explicit():
    git_app = AppTest.from_file(GIT_PAGE, default_timeout=30)
    git_app.run()
    assert not git_app.exception
    markdown = _markdown(git_app)
    assert "Outcome: command reference ready" in markdown
    assert "tool-status-note-neutral" in markdown

    git_app.text_input[0].set_value("reflog")
    next(widget for widget in git_app.button if widget.label == "Show matching commands").click().run()
    assert not git_app.exception
    markdown = _markdown(git_app)
    assert "Outcome: command list filtered" in markdown
    assert "tool-status-note-success" in markdown

    git_app.text_input[0].set_value("no-match-git-command")
    next(widget for widget in git_app.button if widget.label == "Show matching commands").click().run()
    assert not git_app.exception
    markdown = _markdown(git_app)
    assert "Outcome: command filtering blocked" in markdown
    assert "tool-status-note-warning" in markdown
    assert 'role="alert"' in markdown

    bip39_app = AppTest.from_file(BIP39_PAGE, default_timeout=30)
    bip39_app.run()
    assert not bip39_app.exception
    next(widget for widget in bip39_app.button if widget.label == "Generate mnemonic").click().run()
    assert not bip39_app.exception
    markdown = _markdown(bip39_app)
    assert "Outcome: mnemonic generation complete" in markdown
    assert "tool-status-note-success" in markdown

    bip39_app.text_area[0].set_value("invalid words here")
    next(widget for widget in bip39_app.button if widget.label == "Validate mnemonic").click().run()
    assert not bip39_app.exception
    markdown = _markdown(bip39_app)
    assert "Outcome: mnemonic validation blocked" in markdown
    assert "tool-status-note-warning" in markdown
    assert 'role="alert"' in markdown

    lorem_app = AppTest.from_file(LOREM_PAGE, default_timeout=30)
    lorem_app.run()
    assert not lorem_app.exception
    markdown = _markdown(lorem_app)
    assert "Outcome: lorem generation awaiting input" in markdown
    assert "tool-status-note-neutral" in markdown

    lorem_seed = next(widget for widget in lorem_app.text_input if widget.key == "lorem_seed")
    lorem_seed.set_value("wave27")
    lorem_count = next(widget for widget in lorem_app.number_input if widget.key == "lorem_count")
    lorem_count.set_value(6)
    next(widget for widget in lorem_app.button if widget.label == "Generate lorem ipsum").click().run()
    assert not lorem_app.exception
    assert lorem_app.code[0].value == "magna eiusmod tempor fugiat sit esse"
    markdown = _markdown(lorem_app)
    assert "Outcome: lorem text generated" in markdown
    assert "tool-status-note-success" in markdown

    text_app = AppTest.from_file(TEXT_RADIX_PAGE, default_timeout=30)
    text_app.run()
    assert not text_app.exception
    next(widget for widget in text_app.button if widget.label == "Convert text").click().run()
    assert not text_app.exception
    markdown = _markdown(text_app)
    assert "Outcome: text conversion blocked" in markdown
    assert "tool-status-note-warning" in markdown
    assert 'role="alert"' in markdown

    text_app.text_area[0].set_value("Az")
    next(widget for widget in text_app.button if widget.label == "Convert text").click().run()
    assert not text_app.exception
    markdown = _markdown(text_app)
    assert "Outcome: text conversion complete" in markdown
    assert "tool-status-note-success" in markdown
