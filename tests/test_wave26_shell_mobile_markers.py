from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE26_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/139_Git_Command_Cheat_Sheet.py",
    "pages/140_BIP39_Mnemonic_Generator_Validator.py",
    "pages/141_Lorem_Ipsum_Generator.py",
    "pages/142_Text_to_Binary_Hex_Octal_Converter.py",
)


def test_wave26_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE26_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave26_pages_use_shared_group_headings_and_mobile_actions():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            'with tool_form_panel("home_primary_action"):',
            'render_control_heading("Filter by profession")',
            'render_control_heading("Navigation")',
            'render_control_heading("Catalog action")',
            'st.button(button_label, icon=button_icon, use_container_width=True)',
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            'render_control_heading("Keyword search")',
            'render_control_heading("Category filter")',
            'with tool_form_panel("roadmap_ai_triage_action"):',
            'render_control_heading("Triage action")',
            'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        ],
        "pages/139_Git_Command_Cheat_Sheet.py": [
            'with tool_form_panel("git_command_cheat_sheet"):',
            'render_control_heading("Search")',
            'render_control_heading("Category")',
            'submitted = st.form_submit_button("Show matching commands", use_container_width=True)',
        ],
        "pages/140_BIP39_Mnemonic_Generator_Validator.py": [
            'with tool_form_panel("bip39_mnemonic_generator_validator"):',
            'with tool_form_panel("bip39_mnemonic_validator"):',
            'render_control_heading("Generation settings")',
            'render_control_heading("Mnemonic phrase")',
            'st.form_submit_button("Generate mnemonic", use_container_width=True)',
            'st.form_submit_button("Validate mnemonic", use_container_width=True)',
        ],
        "pages/141_Lorem_Ipsum_Generator.py": [
            'with tool_form_panel("lorem_ipsum_generator"):',
            'render_control_heading("Output shape")',
            'render_control_heading("Deterministic seed")',
            'submitted = st.form_submit_button("Generate lorem ipsum", use_container_width=True)',
        ],
        "pages/142_Text_to_Binary_Hex_Octal_Converter.py": [
            'with tool_form_panel("text_to_binary_hex_octal_converter"):',
            'render_control_heading("Source text")',
            'submitted = st.form_submit_button("Convert text", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "render_control_heading" in source, f"{rel_path}: missing wave-26 shared heading helper usage"
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-26 shell/mobile snippet {snippet!r}"

    for rel_path in WAVE26_PAGES[2:]:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "st.columns(2)" not in source, f"{rel_path}: should avoid fixed two-column form layouts on small screens"
