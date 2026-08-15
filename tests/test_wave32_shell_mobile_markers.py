from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE32_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/141_Lorem_Ipsum_Generator.py",
    "pages/142_Text_to_Binary_Hex_Octal_Converter.py",
)


def test_wave32_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE32_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "wave32-shell-mobile")' in source, f"{rel_path}: missing wave-32 marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave32_pages_keep_grouped_controls_mobile_actions_and_visual_hierarchy():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            'with tool_form_panel("home_primary_action"):',
            'render_control_heading("Filter by profession")',
            'render_control_heading("Navigation")',
            'render_control_heading("Catalog action")',
            "st.button(button_label, icon=button_icon, use_container_width=True)",
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            'with st.form("roadmap-filters-form"):',
            'render_control_heading("Keyword search")',
            'render_control_heading("Category filter")',
            'render_control_heading("Apply filters")',
            'st.form_submit_button("Apply filters", use_container_width=True)',
            'with tool_form_panel("roadmap_ai_triage_action"):',
            'render_control_heading("Triage action")',
            'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        ],
        "pages/141_Lorem_Ipsum_Generator.py": [
            'with tool_form_panel("lorem_ipsum_generator"):',
            'render_section_heading("Output setup", eyebrow="Step 1")',
            'render_control_heading("Output shape")',
            'render_control_heading("Deterministic seed")',
            'render_control_heading("Primary action")',
            'submitted = st.form_submit_button("Generate lorem ipsum", use_container_width=True)',
            'render_section_heading("Generated lorem output", eyebrow="Step 2")',
        ],
        "pages/142_Text_to_Binary_Hex_Octal_Converter.py": [
            'with tool_form_panel("text_to_binary_hex_octal_converter"):',
            'render_section_heading("Input setup", eyebrow="Step 1")',
            'render_control_heading("Source text")',
            'render_control_heading("Primary action")',
            'submitted = st.form_submit_button("Convert text", use_container_width=True)',
            'render_section_heading("Encoded output", eyebrow="Step 2")',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "render_control_heading" in source, f"{rel_path}: missing wave-32 heading helper usage"
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-32 shell/mobile snippet {snippet!r}"

    for rel_path in WAVE32_PAGES[1:]:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "st.columns(2)" not in source, f"{rel_path}: should avoid fixed two-column form layouts on small screens"
