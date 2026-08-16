from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE34_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/141_Lorem_Ipsum_Generator.py",
    "pages/142_Text_to_Binary_Hex_Octal_Converter.py",
)


def test_wave34_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE34_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "wave34-shell-mobile")' in source, f"{rel_path}: missing wave-34 marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave34_pages_keep_mobile_primary_actions_and_read_order_guidance():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            '"Browsing setup",',
            'description="Pick a profession lens and choose quick access or full catalog before running actions.",',
            'eyebrow="Step 1",',
            'with tool_form_panel("home_primary_action"):',
            '"Catalog visibility",',
            'description="Run one full-width action to reveal or collapse catalog results after setup is complete.",',
            'eyebrow="Step 2",',
            'st.caption("Read order: confirm browsing setup, run this full-width action, then review the outcome note before scanning results.")',
            "st.button(button_label, icon=button_icon, use_container_width=True)",
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            '"Filter setup",',
            'description="Set search terms and category scope first so roadmap results are easier to scan.",',
            'eyebrow="Step 1",',
            'render_control_heading("Apply filters")',
            'st.caption("Read order: set search + category, apply filters, then check outcome status before scanning cards.")',
            'st.form_submit_button("Apply filters", use_container_width=True)',
            '"Roadmap results",',
            'description="Review status outcomes first, then scan grouped columns for matching roadmap cards.",',
            'eyebrow="Step 2",',
        ],
        "pages/141_Lorem_Ipsum_Generator.py": [
            'with tool_form_panel("lorem_ipsum_generator"):',
            'render_section_heading(',
            '"Output setup",',
            'eyebrow="Step 1",',
            'render_control_heading("Primary action")',
            'st.caption("Read order: choose output shape and seed, run generate, then review the outcome note and output.")',
            'submitted = st.form_submit_button("Generate lorem ipsum", use_container_width=True)',
        ],
        "pages/142_Text_to_Binary_Hex_Octal_Converter.py": [
            'with tool_form_panel("text_to_binary_hex_octal_converter"):',
            '"Input setup",',
            'eyebrow="Step 1",',
            'render_control_heading("Primary action")',
            'st.caption("Read order: enter source text, run convert, then check status and compare all three encoded outputs.")',
            'submitted = st.form_submit_button("Convert text", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-34 shell/mobile snippet {snippet!r}"

    for rel_path in WAVE34_PAGES[1:]:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "st.columns(2)" not in source, f"{rel_path}: should avoid fixed two-column form layouts on small screens"
