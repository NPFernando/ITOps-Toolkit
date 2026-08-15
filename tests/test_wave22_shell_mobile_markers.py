from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


WAVE22_PAGES = (
    "app.py",
    "pages/10_Roadmap_Feedback.py",
    "pages/129_Docker_Run_to_Compose.py",
    "pages/130_NATO_Phonetic_Converter.py",
    "pages/131_WiFi_QR_Code_Generator.py",
    "pages/132_HMAC_Generator.py",
    "pages/133_IPv6_ULA_Generator.py",
    "pages/134_Random_MAC_Address_Generator.py",
)


def test_wave22_pages_keep_shell_and_baseline_markers():
    for rel_path in WAVE22_PAGES:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "apply_app_shell(" in source, f"{rel_path}: missing shared shell"
        assert 'mark_page_baseline(_baseline, "shell-ready")' in source, f"{rel_path}: missing shell-ready marker"
        assert 'mark_page_baseline(_baseline, "content-rendered")' in source, f"{rel_path}: missing content marker"
        assert "render_page_baseline(_baseline)" in source, f"{rel_path}: missing baseline render"


def test_wave22_mobile_grouped_controls_and_full_width_primary_actions():
    expected_snippets = {
        "app.py": [
            'with tool_form_panel("home_navigation_controls"):',
            'with tool_form_panel("home_primary_action"):',
            'st.button(button_label, icon=button_icon, use_container_width=True)',
        ],
        "pages/10_Roadmap_Feedback.py": [
            'with tool_form_panel("roadmap_filters"):',
            'with tool_form_panel("roadmap_ai_triage_action"):',
            'st.button(f"Summarize {len(open_items)} open items with AI", icon=":material/auto_awesome:", use_container_width=True)',
        ],
        "pages/129_Docker_Run_to_Compose.py": [
            'with tool_form_panel("docker_run_to_compose"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Docker run command</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Compose service name</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Convert to compose", use_container_width=True)',
        ],
        "pages/130_NATO_Phonetic_Converter.py": [
            'with tool_form_panel("nato_phonetic_converter"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Input text</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Convert to NATO phonetic", use_container_width=True)',
        ],
        "pages/131_WiFi_QR_Code_Generator.py": [
            'with tool_form_panel("wifi_qr_generator"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Network identity</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Security and password</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Generate WiFi QR code", use_container_width=True)',
        ],
        "pages/132_HMAC_Generator.py": [
            'with tool_form_panel("hmac_generator"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Message payload</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Signing secret</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Digest algorithm</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Generate HMAC digest", use_container_width=True)',
        ],
        "pages/133_IPv6_ULA_Generator.py": [
            'with tool_form_panel("ipv6_ula_generator"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Generation seed</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Subnet preview</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Generate ULA prefix", use_container_width=True)',
        ],
        "pages/134_Random_MAC_Address_Generator.py": [
            'with tool_form_panel("random_mac_generator"):',
            'st.markdown(\'<div class="tool-panel-eyebrow">Addressing mode</div>\', unsafe_allow_html=True)',
            'st.markdown(\'<div class="tool-panel-eyebrow">Deterministic test seed</div>\', unsafe_allow_html=True)',
            'submitted = st.form_submit_button("Generate MAC address", use_container_width=True)',
        ],
    }

    for rel_path, snippets in expected_snippets.items():
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        for snippet in snippets:
            assert snippet in source, f"{rel_path}: missing wave-22 shell/mobile snippet {snippet!r}"

    for rel_path in WAVE22_PAGES[2:]:
        source = (PROJECT_ROOT / rel_path).read_text(encoding="utf-8")
        assert "st.columns(2)" not in source, f"{rel_path}: should avoid fixed two-column form layouts on small screens"
