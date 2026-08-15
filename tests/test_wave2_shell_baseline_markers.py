from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE2_SHELL_PAGES = (
    "app.py",
    "pages/1_Domain_Health_Checker.py",
    "pages/2_DNS_Record_Checker.py",
    "pages/3_SSL_Certificate_Checker.py",
    "pages/4_HTTP_Status_Checker.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/128_Health_Diagnostics.py",
)


def test_wave2_shell_pages_keep_baseline_markers_for_shell_and_content():
    for rel_path in WAVE2_SHELL_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"

