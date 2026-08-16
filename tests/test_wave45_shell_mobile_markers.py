from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE45_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/141_Lorem_Ipsum_Generator.py",
    "pages/142_Text_to_Binary_Hex_Octal_Converter.py",
)


def test_wave45_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE45_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "wave45-shell-mobile")' in source, f"{rel_path}: missing wave-45 marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave45_pages_keep_grouped_controls_read_order_and_full_width_actions():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            '"Browsing setup",',
            'with tool_form_panel("home_primary_action"):',
            '"Catalog visibility",',
            'st.caption("Read order: confirm browsing setup, run this full-width action, then review the outcome note before scanning results.")',
            'st.caption("Status tip: if the outcome says filters need adjustment, clear one filter and try again.")',
            'st.caption("New here? Start in Quick access, then open All tools only when needed.")',
            "st.button(button_label, icon=button_icon, use_container_width=True)",
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            '"Filter setup",',
            'st.caption("Read order: set search + category, apply filters, then check outcome status before scanning cards.")',
            'st.caption("Status tip: outcome notes tell you whether results are ready or filters need adjustment.")',
            'st.caption("New here? Clear filters if results look empty, then apply one filter at a time.")',
            'st.form_submit_button("Apply filters", use_container_width=True)',
        ],
        "pages/141_Lorem_Ipsum_Generator.py": [
            'with tool_form_panel("lorem_ipsum_generator"):',
            '"Output setup",',
            'st.caption("Read order: choose output shape and seed, run generate, then review the outcome note and output.")',
            'st.caption("Status tip: neutral means waiting for input; success means text is ready to copy.")',
            'st.caption("New here? Leave seed blank for random text, then add a seed only for repeatable output.")',
            'submitted = st.form_submit_button("Generate lorem ipsum", use_container_width=True)',
        ],
        "pages/142_Text_to_Binary_Hex_Octal_Converter.py": [
            'with tool_form_panel("text_to_binary_hex_octal_converter"):',
            '"Input setup",',
            'st.caption("Read order: enter source text, run convert, then check status and compare all three encoded outputs.")',
            'st.caption("Status tip: warning means input is missing; success means all encodings are ready.")',
            'st.caption("New here? Start with a short word, then compare binary, hex, and octal byte order.")',
            'submitted = st.form_submit_button("Convert text", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-45 shell/mobile snippet {snippet!r}"

    for rel_path in WAVE45_PAGES[1:]:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "st.columns(2)" not in source, f"{rel_path}: should avoid fixed two-column form layouts on small screens"
