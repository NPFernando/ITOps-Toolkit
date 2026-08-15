from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE10_PAGES = (
    "app.py",
    "pages/1_Domain_Health_Checker.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/27_WHOIS_Lookup.py",
    "pages/28_Bulk_Domain_Health.py",
    "pages/33_DNS_Propagation_Checker.py",
    "pages/35_DKIM_Selector_Lookup.py",
    "pages/36_Email_Record_Builder.py",
    "pages/128_Health_Diagnostics.py",
)


def test_wave10_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE10_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"

