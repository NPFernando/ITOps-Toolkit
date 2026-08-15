from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE13_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/115_Password_Policy_Checker.py",
    "pages/116_ISO8601_Duration_Tool.py",
    "pages/117_JSON_Merge_Patch.py",
    "pages/118_Column_Aligner.py",
)


def test_wave13_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE13_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave13_primary_actions_are_full_width():
    expected_snippets = {
        "app.py": 'st.button(button_label, icon=button_icon, use_container_width=True)',
        "pages/10_Roadmap_Feedback.py": 'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        "pages/115_Password_Policy_Checker.py": 'st.form_submit_button("Check", use_container_width=True)',
        "pages/116_ISO8601_Duration_Tool.py": 'st.form_submit_button("Parse", use_container_width=True)',
        "pages/116_ISO8601_Duration_Tool.py#build": 'st.form_submit_button("Build", use_container_width=True)',
        "pages/117_JSON_Merge_Patch.py": 'st.form_submit_button("Merge", use_container_width=True)',
        "pages/118_Column_Aligner.py": 'st.form_submit_button("Align", use_container_width=True)',
    }
    for rel_path, snippet in expected_snippets.items():
        path = rel_path.split("#", 1)[0]
        source = (PROJECT_ROOT / path).read_text(encoding="utf-8")
        assert snippet in source, f"{path}: expected full-width primary action"
