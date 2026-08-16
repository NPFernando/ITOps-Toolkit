from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE43_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/141_Lorem_Ipsum_Generator.py",
    "pages/142_Text_to_Binary_Hex_Octal_Converter.py",
)


def test_wave43_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE43_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "wave43-shell-mobile")' in source, f"{rel_path}: missing wave-43 marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave43_pages_keep_grouped_controls_mobile_primary_actions_and_novice_guidance():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            '"Browsing setup",',
            'eyebrow="Step 1",',
            'with tool_form_panel("home_primary_action"):',
            '"Catalog visibility",',
            'eyebrow="Step 2",',
            'st.caption("Read order: choose profession and navigation mode first, then run the catalog action below.")',
            'st.button(button_label, icon=button_icon, use_container_width=True)',
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            '"Filter setup",',
            'eyebrow="Step 1a",',
            'st.caption("If you\'re new, keep category on All first, apply filters, then narrow category only if needed.")',
            'st.form_submit_button("Apply filters", use_container_width=True)',
            '"Roadmap results",',
            'eyebrow="Step 2",',
        ],
        "pages/141_Lorem_Ipsum_Generator.py": [
            'with tool_form_panel("lorem_ipsum_generator"):',
            '"Output setup",',
            'eyebrow="Step 1",',
            'st.caption("For first use: pick Words and a small count, then generate before trying seeded repeats.")',
            'submitted = st.form_submit_button("Generate lorem ipsum", use_container_width=True)',
        ],
        "pages/142_Text_to_Binary_Hex_Octal_Converter.py": [
            'with tool_form_panel("text_to_binary_hex_octal_converter"):',
            '"Input setup",',
            'eyebrow="Step 1",',
            'st.caption("For first use: enter one short word, convert, then compare the same byte order across outputs.")',
            'submitted = st.form_submit_button("Convert text", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-43 shell/mobile snippet {snippet!r}"

    for rel_path in WAVE43_PAGES[1:]:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "st.columns(2)" not in source, f"{rel_path}: should avoid fixed two-column form layouts on small screens"
