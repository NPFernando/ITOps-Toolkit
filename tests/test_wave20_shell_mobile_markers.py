from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE20_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/117_JSON_Merge_Patch.py",
    "pages/118_Column_Aligner.py",
    "pages/119_SSH_Config_Validator.py",
    "pages/120_CSR_Generator.py",
    "pages/121_CAA_Record_Builder.py",
    "pages/122_Base62_Encoder_Decoder.py",
)


def test_wave20_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE20_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave20_mobile_layout_grouped_controls_and_primary_actions():
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
        "pages/117_JSON_Merge_Patch.py": [
            'with tool_form_panel("json_merge_patch"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Target JSON</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Patch JSON</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Merge", use_container_width=True)',
        ],
        "pages/118_Column_Aligner.py": [
            'with tool_form_panel("column_aligner"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Input text</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Align", use_container_width=True)',
        ],
        "pages/119_SSH_Config_Validator.py": [
            'with tool_form_panel("ssh_config_validator"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">SSH config content</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Lint", use_container_width=True)',
        ],
        "pages/120_CSR_Generator.py": [
            'with tool_form_panel("csr_generator"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Organization details</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Location details</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Generate CSR", use_container_width=True)',
        ],
        "pages/121_CAA_Record_Builder.py": [
            'with tool_form_panel("caa_record_builder"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Authorization settings</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Build record", use_container_width=True)',
        ],
        "pages/122_Base62_Encoder_Decoder.py": [
            'with tool_form_panel("base62_encode"):',
            'with tool_form_panel("base62_decode"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Encode input</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Decode input</div>\', unsafe_allow_html=True)',
            'encode_submitted = st.form_submit_button("Encode", use_container_width=True)',
            'decode_submitted = st.form_submit_button("Decode", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-20 shell/mobile snippet {snippet!r}"

    removed_mobile_patterns = {
        "pages/117_JSON_Merge_Patch.py": ['st.columns(2, gap="small")'],
        "pages/120_CSR_Generator.py": ['st.columns(2)', "c1, c2 = st.columns(2)", "c3, c4 = st.columns(2)"],
    }
    for rel_path, snippets in removed_mobile_patterns.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet not in source, f"{rel_path}: should remove mobile-hostile form layout snippet {snippet!r}"
