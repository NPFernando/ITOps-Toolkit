from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE16_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/127_Markdown_Link_Extractor.py",
    "pages/128_Health_Diagnostics.py",
)


def test_wave16_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE16_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave16_mobile_layout_and_primary_actions():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            'render_form_intro("Choose how to browse tools", "Filter by profession and switch between quick access or full catalog.")',
            'st.button(button_label, icon=button_icon, use_container_width=True)',
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            'with tool_form_panel("roadmap_ai_triage_action"):',
            'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        ],
        "pages/127_Markdown_Link_Extractor.py": [
            'with tool_form_panel("markdown_link_extractor"):',
            'render_form_intro("Paste Markdown text", "Include inline links, reference links, or autolinks to extract into a table.")',
            'submitted = st.form_submit_button("Extract links", use_container_width=True)',
        ],
        "pages/128_Health_Diagnostics.py": [
            'st.link_button("Open public ops runbook", runbook_display, width="stretch")',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-16 shell/mobile snippet {snippet!r}"
