from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE38_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/141_Lorem_Ipsum_Generator.py",
    "pages/142_Text_to_Binary_Hex_Octal_Converter.py",
)


def test_wave38_pages_keep_shell_and_visual_icon_markers():
    for rel_path in WAVE38_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "wave38-shell-mobile")' in source, f"{rel_path}: missing wave-38 marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave38_roadmap_heading_hierarchy_snippets_remain_scan_friendly():
    source = (PROJECT_ROOT / "pages/10_Roadmap_Feedback.py").read_text(encoding="utf-8")
    expected_snippets = (
        'render_section_heading(\n    "Browse roadmap items",',
        'eyebrow="Step 1",',
        'render_section_heading(\n    "Roadmap results",',
        'eyebrow="Step 2",',
        'render_section_heading(\n    "AI-assisted triage",',
        'eyebrow="Step 3",',
        'heading_level="h3",',
    )
    for snippet in expected_snippets:
        assert snippet in source, f"pages/10_Roadmap_Feedback.py: missing wave-38 heading hierarchy snippet {snippet!r}"
