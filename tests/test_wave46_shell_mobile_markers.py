from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE46_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/141_Lorem_Ipsum_Generator.py",
    "pages/142_Text_to_Binary_Hex_Octal_Converter.py",
)


def test_wave46_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE46_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "wave46-shell-mobile")' in source, f"{rel_path}: missing wave-46 marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave46_pages_keep_grouped_controls_read_order_and_full_width_actions():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            '"Browsing setup",',
            'with tool_form_panel("home_primary_action"):',
            '"Catalog visibility",',
            'st.caption("Read order: review browsing setup, run this full-width action, then verify status notes and tool results.")',
            'st.caption("Status tip: confirm the outcome note after each action before changing filters.")',
            'st.caption("Quick tip: check the status note before changing filters.")',
            "st.button(button_label, icon=button_icon, use_container_width=True)",
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            '"Filter setup",',
            'st.caption("Read order: set search + category, apply filters, then review status outcomes before scanning cards.")',
            'st.caption("Status tip: check the outcome note first so you know whether to refine filters or continue.")',
            'st.caption("Quick tip: read the status note before scanning cards.")',
            'st.form_submit_button("Apply filters", use_container_width=True)',
        ],
        "pages/141_Lorem_Ipsum_Generator.py": [
            'with tool_form_panel("lorem_ipsum_generator"):',
            '"Output setup",',
            'st.caption("Read order: configure output shape and seed, run generate, then review status guidance and output.")',
            'st.caption("Status tip: read the outcome note first to confirm whether text is ready or more input is needed.")',
            'st.caption("Quick tip: confirm the status note before copying output.")',
            'submitted = st.form_submit_button("Generate lorem ipsum", use_container_width=True)',
        ],
        "pages/142_Text_to_Binary_Hex_Octal_Converter.py": [
            'with tool_form_panel("text_to_binary_hex_octal_converter"):',
            '"Input setup",',
            'st.caption("Read order: enter source text, run convert, then confirm status and compare all three encoded outputs.")',
            'st.caption("Status tip: read the outcome note first to confirm whether input is missing or conversion succeeded.")',
            'st.caption("Quick tip: confirm the status note before comparing encodings.")',
            'submitted = st.form_submit_button("Convert text", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-46 shell/mobile snippet {snippet!r}"

    for rel_path in WAVE46_PAGES[1:]:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "st.columns(2)" not in source, f"{rel_path}: should avoid fixed two-column form layouts on small screens"
