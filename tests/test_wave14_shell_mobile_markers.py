from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE14_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/119_SSH_Config_Validator.py",
    "pages/120_CSR_Generator.py",
    "pages/121_CAA_Record_Builder.py",
    "pages/122_Base62_Encoder_Decoder.py",
)


def test_wave14_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE14_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave14_mobile_layout_and_primary_actions():
    expected_snippets = {
        "app.py": [
            'st.button(button_label, icon=button_icon, use_container_width=True)',
            'with tool_form_panel("home_navigation_controls"):',
        ],
        "pages/10_Roadmap_Feedback.py": [
            'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
            'with tool_form_panel("roadmap_filters"):',
            'render_form_intro("Search and filter roadmap", "Use keyword search and category pills to narrow the board.")',
        ],
        "pages/119_SSH_Config_Validator.py": ['st.form_submit_button("Lint", use_container_width=True)'],
        "pages/120_CSR_Generator.py": [
            'st.form_submit_button("Generate CSR", use_container_width=True)',
            "c3, c4 = st.columns(2)",
            'country = st.text_input("Country (2-letter)", placeholder="US", max_chars=2)',
        ],
        "pages/121_CAA_Record_Builder.py": [
            'st.form_submit_button("Build record", use_container_width=True)',
            'tag = st.radio("Tag", TAGS)',
        ],
        "pages/122_Base62_Encoder_Decoder.py": [
            'st.form_submit_button("Encode", use_container_width=True)',
            'st.form_submit_button("Decode", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-14 shell/mobile snippet {snippet!r}"

    caa_source = (PROJECT_ROOT / "pages/121_CAA_Record_Builder.py").read_text(encoding="utf-8")
    assert 'horizontal=True' not in caa_source, "CAA tag selector should not force horizontal layout on small screens"
