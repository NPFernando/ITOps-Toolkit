from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


PAGES_DIR = Path(__file__).resolve().parent.parent / "pages"


def _run(page_name: str) -> AppTest:
    app = AppTest.from_file(str(PAGES_DIR / page_name), default_timeout=30)
    app.run()
    assert not app.exception
    return app


def _markdown(app: AppTest) -> str:
    return " ".join(item.value for item in app.markdown)


def test_wave25_pages_show_neutral_status_on_initial_render():
    pages = (
        "139_Git_Command_Cheat_Sheet.py",
        "140_BIP39_Mnemonic_Generator_Validator.py",
        "141_Lorem_Ipsum_Generator.py",
        "142_Text_to_Binary_Hex_Octal_Converter.py",
    )

    for page_name in pages:
        app = _run(page_name)
        md = _markdown(app)
        assert "tool-status-note-neutral" in md
        assert 'role="status"' in md
        assert 'aria-live="polite"' in md


def test_wave25_git_cheat_sheet_warning_and_success_states_are_explicit():
    app = _run("139_Git_Command_Cheat_Sheet.py")

    md = _markdown(app)
    assert "Outcome: command reference ready" in md

    app.text_input[0].set_value("reflog")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: command list filtered" in md

    app.text_input[0].set_value("definitely-no-match-command")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: command filtering blocked" in md
    assert 'role="alert"' in md


def test_wave25_bip39_validation_warning_and_success_states_are_explicit():
    app = _run("140_BIP39_Mnemonic_Generator_Validator.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: mnemonic generation complete" in md

    app.text_area[0].set_value("invalid words here")
    app.button[1].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: mnemonic validation blocked" in md
    assert 'role="alert"' in md

    app.text_area[0].set_value("abandon ability about above absent absorb abstract access accident account achieve acoustic")
    app.button[1].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: mnemonic validation complete" in md


def test_wave25_lorem_generator_uses_explicit_neutral_and_success_states():
    app = _run("141_Lorem_Ipsum_Generator.py")

    md = _markdown(app)
    assert "Outcome: lorem generation awaiting input" in md

    seed = next(widget for widget in app.text_input if widget.key == "lorem_seed")
    seed.set_value("wave25")
    count = next(widget for widget in app.number_input if widget.key == "lorem_count")
    count.set_value(6)
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: lorem text generated" in md


def test_wave25_text_converter_uses_explicit_warning_and_success_states():
    app = _run("142_Text_to_Binary_Hex_Octal_Converter.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: text conversion blocked" in md
    assert 'role="alert"' in md

    app.text_area[0].set_value("Az")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: text conversion complete" in md
