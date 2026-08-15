from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE18_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/105_Robots_Meta_Tag_Builder.py",
    "pages/106_Cache_Control_Tool.py",
    "pages/107_Markdown_Table_Formatter.py",
    "pages/108_CSV_Column_Selector.py",
    "pages/109_HTTP_Methods_Reference.py",
    "pages/110_Line_Numberer.py",
)


def test_wave18_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE18_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave18_mobile_layout_and_grouped_controls():
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
        "pages/105_Robots_Meta_Tag_Builder.py": [
            'with tool_form_panel("robots_meta_builder"):',
            'submitted = st.form_submit_button("Build tag", use_container_width=True)',
        ],
        "pages/106_Cache_Control_Tool.py": [
            'with tool_form_panel("cache_control_build"):',
            'build_submitted = st.form_submit_button("Build header", use_container_width=True)',
            'with tool_form_panel("cache_control_explain"):',
            'explain_submitted = st.form_submit_button("Explain", use_container_width=True)',
        ],
        "pages/107_Markdown_Table_Formatter.py": [
            'with tool_form_panel("markdown_table_formatter"):',
            'submitted = st.form_submit_button("Format", use_container_width=True)',
        ],
        "pages/108_CSV_Column_Selector.py": [
            'with tool_form_panel("csv_column_selector"):',
            'submitted = st.form_submit_button("Select columns", use_container_width=True)',
            'st.download_button("Download as .csv", result["output"], file_name="selected_columns.csv", mime="text/csv", use_container_width=True)',
        ],
        "pages/109_HTTP_Methods_Reference.py": [
            'with tool_form_panel("http_methods_reference"):',
            'submitted = st.form_submit_button("Search methods", use_container_width=True)',
        ],
        "pages/110_Line_Numberer.py": [
            'with tool_form_panel("line_numberer"):',
            'submitted = st.form_submit_button("Add line numbers", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-18 shell/mobile snippet {snippet!r}"

    for rel_path in (
        "pages/105_Robots_Meta_Tag_Builder.py",
        "pages/106_Cache_Control_Tool.py",
        "pages/109_HTTP_Methods_Reference.py",
        "pages/110_Line_Numberer.py",
    ):
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "st.columns(" not in source, f"{rel_path}: controls should not force multi-column layout on small screens"
