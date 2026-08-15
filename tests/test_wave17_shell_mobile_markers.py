from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE17_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/99_Markdown_TOC_Generator.py",
    "pages/100_Number_to_Words.py",
    "pages/101_JSON_to_TypeScript.py",
    "pages/102_CSS_Gradient_Generator.py",
    "pages/103_JWT_Claims_Reference.py",
    "pages/104_CSP_Header_Builder.py",
)


def test_wave17_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE17_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave17_mobile_layout_and_primary_actions():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            'with tool_form_panel("home_sort_controls"):',
            'st.button(button_label, icon=button_icon, use_container_width=True)',
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            'with tool_form_panel("roadmap_ai_triage_action"):',
            'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        ],
        "pages/99_Markdown_TOC_Generator.py": [
            'with tool_form_panel("markdown_toc_generator"):',
            'submitted = st.form_submit_button("Generate TOC", use_container_width=True)',
        ],
        "pages/100_Number_to_Words.py": [
            'with tool_form_panel("number_to_words"):',
            'submitted = st.form_submit_button("Convert", use_container_width=True)',
        ],
        "pages/101_JSON_to_TypeScript.py": [
            'with tool_form_panel("json_to_typescript"):',
            'submitted = st.form_submit_button("Generate", use_container_width=True)',
        ],
        "pages/102_CSS_Gradient_Generator.py": [
            'with tool_form_panel("css_gradient_generator"):',
            'gradient_type = st.radio("Type", ("linear", "radial"), horizontal=False)',
            'submitted = st.form_submit_button("Generate", use_container_width=True)',
        ],
        "pages/103_JWT_Claims_Reference.py": [
            'with tool_form_panel("jwt_claims_reference"):',
            'submitted = st.form_submit_button("Search claims", use_container_width=True)',
        ],
        "pages/104_CSP_Header_Builder.py": [
            'with tool_form_panel("csp_builder"):',
            'submitted = st.form_submit_button("Build header", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-17 shell/mobile snippet {snippet!r}"

    toc_source = (PROJECT_ROOT / "pages/99_Markdown_TOC_Generator.py").read_text(encoding="utf-8")
    assert "st.columns(2)" not in toc_source, "Markdown TOC controls should not force a two-column layout on small screens"

    gradient_source = (PROJECT_ROOT / "pages/102_CSS_Gradient_Generator.py").read_text(encoding="utf-8")
    assert "st.columns(2)" not in gradient_source, "CSS Gradient controls should not force a two-column layout on small screens"
