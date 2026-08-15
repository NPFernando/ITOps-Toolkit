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


def test_wave23_pages_show_neutral_status_before_submit():
    pages = (
        "135_List_Converter.py",
        "136_Email_Address_Normalizer.py",
        "137_IPv4_Address_Format_Converter.py",
        "138_IPv4_Range_Expander.py",
        "139_Git_Command_Cheat_Sheet.py",
        "140_BIP39_Mnemonic_Generator_Validator.py",
    )

    for page_name in pages:
        app = _run(page_name)
        md = _markdown(app)
        if page_name != "139_Git_Command_Cheat_Sheet.py":
            assert "tool-empty-state" in md
        assert "tool-status-note-neutral" in md
        assert 'role="status"' in md
        assert 'aria-live="polite"' in md


def test_list_converter_warning_and_success_states():
    app = _run("135_List_Converter.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: list conversion blocked" in md

    app.text_area[0].set_value("beta\nalpha\nbeta")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: list conversion complete" in md
    output = " ".join(item.value for item in app.code)
    assert "beta" in output


def test_email_normalizer_warning_and_success_states():
    app = _run("136_Email_Address_Normalizer.py")

    app.text_area[0].set_value("not-an-email")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: email normalization blocked" in md

    app.text_area[0].set_value("Alice+alerts@Example.com")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: email normalization complete" in md
    output = " ".join(item.value for item in app.code)
    assert "alice@example.com" in output


def test_ipv4_format_converter_warning_and_success_states():
    app = _run("137_IPv4_Address_Format_Converter.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: IPv4 conversion blocked" in md

    app.text_input[0].set_value("192.168.0.1")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: IPv4 conversion complete" in md
    output = " ".join(item.value for item in app.code)
    assert "Integer:" in output


def test_ipv4_range_expander_warning_and_success_states():
    app = _run("138_IPv4_Range_Expander.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: IPv4 range expansion blocked" in md

    app.text_input[0].set_value("10.0.0.0/30")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: IPv4 range expansion complete" in md
    output = " ".join(item.value for item in app.code)
    assert "10.0.0.0" in output


def test_git_cheat_sheet_renders_reference_results():
    app = _run("139_Git_Command_Cheat_Sheet.py")

    md = _markdown(app)
    assert "tool-status-note-neutral" in md
    assert "Outcome: command reference ready" in md
    code = " ".join(item.value for item in app.code)
    assert "git status -sb" in code

    app.text_input[0].set_value("reflog")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-success" in md
    assert "Outcome: command filter results ready" in md
    code = " ".join(item.value for item in app.code)
    assert "git reflog" in code

    app.text_input[0].set_value("definitely-no-match-command")
    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "tool-status-note-warning" in md
    assert "Outcome: command filter needs adjustment" in md


def test_bip39_generator_and_validator_states():
    app = _run("140_BIP39_Mnemonic_Generator_Validator.py")

    app.button[0].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "Outcome: mnemonic generation complete" in md
    generated = " ".join(item.value for item in app.code)
    assert len(generated.split()) == 12

    app.text_area[0].set_value("abandon ability about above absent absorb abstract access accident account achieve acoustic")
    app.button[1].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "Outcome: mnemonic validation complete" in md

    app.text_area[0].set_value("invalid words here")
    app.button[1].click().run()
    assert not app.exception
    md = _markdown(app)
    assert "Outcome: mnemonic validation blocked" in md
    assert "tool-status-note-warning" in md
