from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE44_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/141_Lorem_Ipsum_Generator.py",
    "pages/142_Text_to_Binary_Hex_Octal_Converter.py",
)


def test_wave44_pages_keep_shell_and_visual_icon_markers():
    for rel_path in WAVE44_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "wave44-shell-mobile")' in source, f"{rel_path}: missing wave-44 marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave44_mapped_page_headings_remain_scan_friendly():
    expected_snippets = {
        "app.py": (
            'render_section_heading(\n        "Browsing setup",',
            'eyebrow="Step 1",',
            'render_section_heading(\n        "Catalog visibility",',
            'eyebrow="Step 2",',
            'st.caption("Read order: choose profession and navigation mode first, then run the catalog action below.")',
        ),
        "pages/10_Roadmap_Feedback.py": (
            'render_section_heading(\n    "Browse roadmap items",',
            'eyebrow="Step 1",',
            'render_section_heading(\n        "Filter setup",',
            'eyebrow="Step 1a",',
            'render_section_heading(\n    "Roadmap results",',
            'eyebrow="Step 2",',
            'render_section_heading(\n    "AI-assisted triage",',
            'eyebrow="Step 3",',
            'render_section_heading("Optional triage", eyebrow="Step 3a", heading_level="h3")',
            'st.caption("If you\'re new, keep category on All first, apply filters, then narrow category only if needed.")',
        ),
        "pages/141_Lorem_Ipsum_Generator.py": (
            'render_section_heading(\n        "Output setup",',
            'eyebrow="Step 1",',
            'render_section_heading(\n        "Generated lorem output",',
            'eyebrow="Step 2",',
            'st.caption("For first use: pick Words and a small count, then generate before trying seeded repeats.")',
        ),
        "pages/142_Text_to_Binary_Hex_Octal_Converter.py": (
            'render_section_heading(\n        "Input setup",',
            'eyebrow="Step 1",',
            'render_section_heading(\n        "Encoded output",',
            'eyebrow="Step 2",',
            'st.caption("For first use: enter one short word, convert, then compare the same byte order across outputs.")',
        ),
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-44 heading hierarchy snippet {snippet!r}"
