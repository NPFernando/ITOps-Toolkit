from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE19_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/111_PII_Redactor.py",
    "pages/112_Env_File_Diff.py",
    "pages/113_Cron_Overlap_Checker.py",
    "pages/114_Test_Data_Generator.py",
    "pages/115_Password_Policy_Checker.py",
    "pages/116_ISO8601_Duration_Tool.py",
)


def test_wave19_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE19_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave19_mobile_layout_grouped_controls_and_primary_actions():
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
        "pages/111_PII_Redactor.py": [
            'with tool_form_panel("pii_redactor"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Pattern types</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Redact", use_container_width=True)',
        ],
        "pages/112_Env_File_Diff.py": [
            'with tool_form_panel("env_diff"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">First file</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Compare", use_container_width=True)',
        ],
        "pages/113_Cron_Overlap_Checker.py": [
            'with tool_form_panel("cron_overlap"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Schedule A</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Check for overlaps", use_container_width=True)',
        ],
        "pages/114_Test_Data_Generator.py": [
            'with tool_form_panel("test_data_generator"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Record settings</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Generate", use_container_width=True)',
        ],
        "pages/115_Password_Policy_Checker.py": [
            'with tool_form_panel("password_policy_checker"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Character rules</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Check", use_container_width=True)',
        ],
        "pages/116_ISO8601_Duration_Tool.py": [
            'with tool_form_panel("iso8601_parse"):',
            'with tool_form_panel("iso8601_build"):',
            'build_submitted = st.form_submit_button("Build", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-19 shell/mobile snippet {snippet!r}"

    removed_mobile_patterns = {
        "pages/112_Env_File_Diff.py": ['col_a, col_b = st.columns(2)'],
        "pages/113_Cron_Overlap_Checker.py": ['c1, c2 = st.columns(2)'],
        "pages/114_Test_Data_Generator.py": ['c1, c2 = st.columns(2)'],
        "pages/115_Password_Policy_Checker.py": ['st.columns(3)', 'st.columns(2)'],
        "pages/116_ISO8601_Duration_Tool.py": ['st.columns(2)', 'st.columns(3)'],
    }
    for rel_path, snippets in removed_mobile_patterns.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet not in source, f"{rel_path}: should remove mobile-hostile form layout snippet {snippet!r}"
