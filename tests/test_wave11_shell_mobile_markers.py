from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE11_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/120_CSR_Generator.py",
    "pages/121_CAA_Record_Builder.py",
    "pages/122_Base62_Encoder_Decoder.py",
    "pages/123_Unified_Diff_Generator.py",
    "pages/124_JWK_PEM_Converter.py",
    "pages/125_Certificate_Chain_Validator.py",
    "pages/126_WSL_Path_Converter.py",
    "pages/127_Markdown_Link_Extractor.py",
)


def test_wave11_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE11_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave11_primary_actions_are_full_width():
    expected_snippets = {
        "app.py": 'st.button(button_label, icon=button_icon, use_container_width=True)',
        "pages/10_Roadmap_Feedback.py": 'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        "pages/120_CSR_Generator.py": 'st.form_submit_button("Generate CSR", use_container_width=True)',
        "pages/121_CAA_Record_Builder.py": 'st.form_submit_button("Build record", use_container_width=True)',
        "pages/122_Base62_Encoder_Decoder.py": 'st.form_submit_button("Encode", use_container_width=True)',
        "pages/123_Unified_Diff_Generator.py": 'st.form_submit_button("Generate diff", use_container_width=True)',
        "pages/124_JWK_PEM_Converter.py": 'st.form_submit_button("Convert to PEM", use_container_width=True)',
        "pages/125_Certificate_Chain_Validator.py": 'st.form_submit_button("Validate chain", use_container_width=True)',
        "pages/126_WSL_Path_Converter.py": 'st.form_submit_button("Convert", use_container_width=True)',
        "pages/127_Markdown_Link_Extractor.py": 'st.form_submit_button("Extract links", use_container_width=True)',
    }
    for rel_path, snippet in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert snippet in source, f"{rel_path}: expected full-width primary action"
