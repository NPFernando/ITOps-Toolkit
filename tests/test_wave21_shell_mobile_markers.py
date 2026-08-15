from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE21_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/123_Unified_Diff_Generator.py",
    "pages/124_JWK_PEM_Converter.py",
    "pages/125_Certificate_Chain_Validator.py",
    "pages/126_WSL_Path_Converter.py",
    "pages/127_Markdown_Link_Extractor.py",
    "pages/128_Health_Diagnostics.py",
)


def test_wave21_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE21_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave21_mobile_layout_grouped_controls_and_primary_actions():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            'with tool_form_panel("home_sort_controls"):',
            'with tool_form_panel("home_primary_action"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Catalog action</div>\', unsafe_allow_html=True)',
            'st.button(button_label, icon=button_icon, use_container_width=True)',
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Keyword search</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Category filter</div>\', unsafe_allow_html=True)',
            'with tool_form_panel("roadmap_ai_triage_action"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Triage action</div>\', unsafe_allow_html=True)',
            'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        ],
        "pages/123_Unified_Diff_Generator.py": [
            'with tool_form_panel("unified_diff_generator"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Original text</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Changed text</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Patch metadata</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Generate diff", use_container_width=True)',
        ],
        "pages/124_JWK_PEM_Converter.py": [
            'with tool_form_panel("jwk_to_pem"):',
            'with tool_form_panel("pem_to_jwk"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">JWK input</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">PEM input</div>\', unsafe_allow_html=True)',
            'st.form_submit_button("Convert to PEM", use_container_width=True)',
            'st.form_submit_button("Convert to JWK", use_container_width=True)',
        ],
        "pages/125_Certificate_Chain_Validator.py": [
            'with tool_form_panel("cert_chain_validator"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">PEM chain input</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Validate chain", use_container_width=True)',
        ],
        "pages/126_WSL_Path_Converter.py": [
            'with tool_form_panel("wsl_path_converter"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Source path</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Target format</div>\', unsafe_allow_html=True)',
            'st.radio("Convert to", TARGETS, horizontal=False)',
            'submitted = st.form_submit_button("Convert", use_container_width=True)',
        ],
        "pages/127_Markdown_Link_Extractor.py": [
            'with tool_form_panel("markdown_link_extractor"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Markdown source</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Extract links", use_container_width=True)',
        ],
        "pages/128_Health_Diagnostics.py": [
            'with tool_form_panel("health_diagnostics_runbook_action"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Runbook action</div>\', unsafe_allow_html=True)',
            'st.link_button("Open public ops runbook", runbook_display, width="stretch")',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-21 shell/mobile snippet {snippet!r}"

    removed_mobile_patterns = {
        "pages/123_Unified_Diff_Generator.py": ['st.columns(2)'],
        "pages/124_JWK_PEM_Converter.py": ['st.columns(2)'],
        "pages/126_WSL_Path_Converter.py": ['st.columns(2)'],
    }
    for rel_path, snippets in removed_mobile_patterns.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet not in source, f"{rel_path}: should remove mobile-hostile form layout snippet {snippet!r}"
