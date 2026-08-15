from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE33_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/141_Lorem_Ipsum_Generator.py",
    "pages/142_Text_to_Binary_Hex_Octal_Converter.py",
)


def test_wave33_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE33_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "wave33-shell-mobile")' in source, f"{rel_path}: missing wave-33 marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave33_pages_keep_grouped_controls_and_mobile_primary_actions():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            'render_section_heading("Browsing setup", eyebrow="Step 1")',
            'with tool_form_panel("home_primary_action"):',
            'render_section_heading("Catalog visibility", eyebrow="Step 2")',
            'render_control_heading("Catalog action")',
            "st.button(button_label, icon=button_icon, use_container_width=True)",
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            'render_section_heading("Filter setup", eyebrow="Step 1")',
            'with st.form("roadmap-filters-form"):',
            'st.form_submit_button("Apply filters", use_container_width=True)',
            'with tool_form_panel("roadmap_ai_triage_action"):',
            'render_section_heading("Optional triage", eyebrow="Step 2")',
            'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        ],
        "pages/141_Lorem_Ipsum_Generator.py": [
            'with tool_form_panel("lorem_ipsum_generator"):',
            'render_section_heading(',
            '"Output setup",',
            'description="Choose unit, count, and optional deterministic seed before generating text.",',
            'eyebrow="Step 1",',
            'render_control_heading("Primary action")',
            'submitted = st.form_submit_button("Generate lorem ipsum", use_container_width=True)',
            '"Generated lorem output",',
            'description="Review and copy output. Reuse the same seed to reproduce identical text.",',
            'eyebrow="Step 2",',
        ],
        "pages/142_Text_to_Binary_Hex_Octal_Converter.py": [
            'with tool_form_panel("text_to_binary_hex_octal_converter"):',
            'render_section_heading(',
            '"Input setup",',
            'description="Enter source text, then run one action to produce all byte-format outputs.",',
            'eyebrow="Step 1",',
            'render_control_heading("Primary action")',
            'submitted = st.form_submit_button("Convert text", use_container_width=True)',
            '"Encoded output",',
            'description="Scan binary, hexadecimal, and octal rows together for quick verification.",',
            'eyebrow="Step 2",',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "render_control_heading" in source, f"{rel_path}: missing wave-33 heading helper usage"
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-33 shell/mobile snippet {snippet!r}"

    for rel_path in WAVE33_PAGES[1:]:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "st.columns(2)" not in source, f"{rel_path}: should avoid fixed two-column form layouts on small screens"
