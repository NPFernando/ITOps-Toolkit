from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE15_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/123_Unified_Diff_Generator.py",
    "pages/124_JWK_PEM_Converter.py",
    "pages/125_Certificate_Chain_Validator.py",
    "pages/126_WSL_Path_Converter.py",
)


def test_wave15_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE15_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave15_mobile_layout_and_grouped_controls():
    expected_snippets = {
        "app.py": [
            'st.button(button_label, icon=button_icon, use_container_width=True)',
            'with tool_form_panel("home_navigation_controls"):',
            'with tool_form_panel("home_sort_controls"):',
            'render_form_intro("Sort visible tools", "Choose how to order the tools currently shown.")',
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            'with tool_form_panel("roadmap_ai_triage_action"):',
            'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        ],
        "pages/123_Unified_Diff_Generator.py": [
            'st.form_submit_button("Generate diff", use_container_width=True)',
        ],
        "pages/124_JWK_PEM_Converter.py": [
            'st.form_submit_button("Convert to PEM", use_container_width=True)',
            'st.form_submit_button("Convert to JWK", use_container_width=True)',
        ],
        "pages/125_Certificate_Chain_Validator.py": [
            'st.form_submit_button("Validate chain", use_container_width=True)',
        ],
        "pages/126_WSL_Path_Converter.py": [
            'render_form_intro("Enter a path and target format", "Paste a Windows, WSL, or Git Bash path, then choose the output style.")',
            'st.radio("Convert to", TARGETS, horizontal=False)',
            'st.form_submit_button("Convert", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-15 shell/mobile snippet {snippet!r}"

    diff_source = (PROJECT_ROOT / "pages/123_Unified_Diff_Generator.py").read_text(encoding="utf-8")
    assert "st.columns(2)" not in diff_source, "Unified Diff inputs should not force a two-column layout on small screens"

    roadmap_source = (PROJECT_ROOT / "pages/10_Roadmap_Feedback.py").read_text(encoding="utf-8")
    assert roadmap_source.index('mark_page_baseline(_baseline, "content-rendered")') > roadmap_source.index(
        '<div class="roadmap-footer-note">'
    ), "Roadmap baseline marker should render after page content"
