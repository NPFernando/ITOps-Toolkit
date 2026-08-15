from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE12_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/111_PII_Redactor.py",
    "pages/112_Env_File_Diff.py",
    "pages/113_Cron_Overlap_Checker.py",
    "pages/114_Test_Data_Generator.py",
    "pages/119_SSH_Config_Validator.py",
    "pages/128_Health_Diagnostics.py",
)


def test_wave12_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE12_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave12_primary_actions_are_full_width():
    expected_snippets = {
        "app.py": 'st.button(button_label, icon=button_icon, use_container_width=True)',
        "pages/10_Roadmap_Feedback.py": 'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        "pages/111_PII_Redactor.py": 'st.form_submit_button("Redact", use_container_width=True)',
        "pages/112_Env_File_Diff.py": 'st.form_submit_button("Compare", use_container_width=True)',
        "pages/113_Cron_Overlap_Checker.py": 'st.form_submit_button("Check for overlaps", use_container_width=True)',
        "pages/114_Test_Data_Generator.py": 'st.form_submit_button("Generate", use_container_width=True)',
        "pages/119_SSH_Config_Validator.py": 'st.form_submit_button("Lint", use_container_width=True)',
    }
    for rel_path, snippet in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert snippet in source, f"{rel_path}: expected full-width primary action"
