# Release Checklist

Use this checklist before deploying ITOps Toolkit to Streamlit Community Cloud.

## 1. Prepare The Environment

Install development dependencies from a clean or refreshed virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

If the virtual environment already exists, refresh dependencies:

```bash
.venv/bin/pip install -r requirements-dev.txt
```

## 2. Run Automated Checks

Fast confidence gate (pre-merge):

```bash
make release-gates
```

Full release gate:

```bash
.venv/bin/python -m compileall app.py pages utils
.venv/bin/python -m pytest
```

Expected result:

- Compile exits with code `0`.
- Pytest exits with code `0`.
- Tests do not require real DNS, HTTP, TLS, OpenAI, Azure, browser, or secret-backed calls.

## 3. Start The Local App

```bash
.venv/bin/streamlit run app.py --server.headless true --server.port 8502
```

In another terminal, verify health:

```bash
curl http://localhost:8502/_stcore/health
```

Expected result: `ok`.

## 4. Browser QA

Check these pages manually:

- Home page: dark sidebar, light workspace, hero, search, tool cards, feature strip, and notice render cleanly.
- Sidebar navigation: every item opens the correct page and no native Streamlit page list appears.
- Tool cards: each card opens the correct tool page.
- Roadmap & Feedback: seed cards, GitHub issue cards when public issues exist, search, filters, roadmap columns, public-safe warning, fallback note, and GitHub issue links render cleanly.
- Domain Health Checker: empty form renders without exceptions.
- DNS Record Checker: form renders and does not show Streamlit form warnings.
- JSON Formatter or Log Troubleshooting Assistant: text-heavy layout has no clipped controls.
- Mobile viewport: no overlapping text, clipped labels, cramped buttons, or horizontal scroll.

### 4.1 Accessibility Regression Checklist

Validate these quick checks across Home, one tool page, and Roadmap & Feedback:

- Keyboard-only navigation works for sidebar links, quick search, pills/filters, and command palette trigger (`Ctrl/Cmd+K`).
- Visible focus ring appears on links, buttons, and form controls (`:focus-visible` remains obvious in dark sidebar and light workspace).
- Shared notice blocks are announced as notes and keep warning/info text readable.
- Tool/page text stays body-readable (no tiny labels) and long button labels wrap instead of clipping.
- In mobile view (`<=720px`), page-header illustrations stack under text, submit/download buttons are full-width, and taps feel comfortable (about 2.3rem minimum target height).

### 4.2 Phase 8 Consistency Regression Checklist

Use `docs/ui-consistency-audit-matrix-phase8.md` as the baseline and confirm:

- Tool pages touched in the release still use shared header/form/empty-state/section-heading patterns.
- Primary action labels remain verb-first and predictable by intent (`Run check`, `Look up`, `Generate`, `Format`, `Validate`, `Scan`).
- Equivalent warnings/failures use shared note components instead of ad-hoc alert rendering where helper parity exists.
- Intentional exceptions (`Roadmap & Feedback`, `Health Diagnostics`) remain documented and readable on desktop/mobile.
- Home/tool/roadmap visual mappings degrade safely when an SVG mapping is unavailable (text fallback still legible).

### 4.3 Phase 9 Wave 2 Regression Checklist (Shell/Mobile/Visual/A11y)

Confirm these release-blocking checks pass:

- **Shell/navigation:** shared sidebar shell renders correctly, quick search is usable, grouped links route correctly, and command palette trigger (`Ctrl/Cmd+K`) remains reachable.
- **Mobile (`<=720px`):** no horizontal scroll in primary pages, header illustrations stack cleanly, and submit/download controls remain full-width and tap-friendly.
- **Visual fallbacks:** one forced missing-asset spot check confirms home hero/tool card/roadmap badge fallbacks stay readable (no broken-image-only affordance).
- **Accessibility:** keyboard-only navigation still reaches sidebar + primary page actions, focus rings remain visible, and shared notice blocks remain readable/semantic.
- **Exception pages:** `Roadmap & Feedback` and `Health Diagnostics` remain intentional documented exceptions, not accidental regressions.

### 4.4 Phase 10 Wave 3 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell clarity:** primary actions, status cues, and warnings remain clear as text (not icon-only) across Home, one checker tool, and Roadmap.
- **Mobile (`<=720px`):** action labels, badges, and status chips wrap cleanly with no clipped text or horizontal overflow.
- **Visual mapping (wave-3 focus):** weak-cue slugs resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard flow, visible focus rings, and notice semantics remain intact after wave-3 visual updates.
- **Release evidence:** Wave 3 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.5 Phase 11 Wave 4 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared sidebar shell, grouped navigation, quick search, and command palette trigger (`Ctrl/Cmd+K`) stay stable after wave-4 updates.
- **Mobile (`<=720px`):** wave-4 action labels, badges, and status chips stay readable/wrapped with no clipped text or horizontal overflow.
- **Visual mapping (wave-4 focus):** wave-4 slugs resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation, visible focus rings, and notice semantics remain intact on Home, one wave-4 tool page, and Roadmap.
- **Release evidence:** Wave 4 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.6 Phase 12 Wave 5 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared sidebar shell, grouped navigation, quick search, and command palette trigger (`Ctrl/Cmd+K`) stay stable with wave-5 tool additions.
- **Mobile (`<=720px`):** wave-5 labels, chips, and helper text stay readable/wrapped with no clipped text or horizontal overflow.
- **Visual mapping (wave-5 focus):** wave-5 slugs resolve to slug-specific assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation, visible focus rings, and notice semantics remain intact on Home, one wave-5 tool page, and Roadmap.
- **Release evidence:** Wave 5 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.7 Phase 13 Wave 6 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared sidebar shell, grouped navigation, quick search, and command palette trigger (`Ctrl/Cmd+K`) stay stable with wave-6 tool additions.
- **Mobile (`<=720px`):** wave-6 labels, chips, and helper text stay readable/wrapped with no clipped text or horizontal overflow.
- **Visual mapping (wave-6 focus):** wave-6 slugs resolve to slug-specific assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation, visible focus rings, and notice semantics remain intact on Home, one wave-6 tool page, and Roadmap.
- **Release evidence:** Wave 6 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.8 Phase 14 Wave 7 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared sidebar shell, grouped navigation, quick search, and command palette trigger (`Ctrl/Cmd+K`) stay stable with wave-7 tool additions.
- **Mobile (`<=720px`):** wave-7 labels, chips, and helper text stay readable/wrapped with no clipped text or horizontal overflow.
- **Visual mapping (wave-7 focus):** wave-7 slugs resolve to slug-specific assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation, visible focus rings, and notice semantics remain intact on Home, one wave-7 tool page, and Roadmap.
- **Release evidence:** Wave 7 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.9 Phase 15 Wave 8 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared sidebar shell, grouped navigation, quick search, and command palette trigger (`Ctrl/Cmd+K`) stay stable with wave-8 tool additions.
- **Mobile (`<=720px`):** wave-8 labels, chips, and helper text stay readable/wrapped with no clipped text or horizontal overflow.
- **Visual mapping (wave-8 focus):** wave-8 slugs resolve to slug-specific assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation, visible focus rings, and notice semantics remain intact on Home, one wave-8 tool page, and Roadmap.
- **Release evidence:** Wave 8 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.10 Phase 16 Wave 9 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared sidebar shell, grouped navigation, quick search, and command palette trigger (`Ctrl/Cmd+K`) stay stable with wave-9 tool additions.
- **Mobile (`<=720px`):** wave-9 labels, chips, and helper text stay readable/wrapped with no clipped text or horizontal overflow.
- **Visual mapping (wave-9 focus):** wave-9 slugs resolve to slug-specific assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation, visible focus rings, and notice semantics remain intact on Home, one wave-9 tool page, and Roadmap.
- **Release evidence:** Wave 9 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.11 Phase 17 Wave 10 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap, Domain Health Checker, WHOIS Lookup, Bulk Domain Health, DNS Propagation Checker, DKIM Selector Lookup, Email Record Builder, and Health Diagnostics.
- **Mobile (`<=720px`):** wave-10 pages stay readable/tap-friendly with no clipped labels or horizontal overflow, and no page-scoped mobile CSS is required to keep layouts stable.
- **Visual mapping (wave-10 focus):** wave-10 planned slugs resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** neutral outcomes use shared status-note semantics, blocking errors use shared failure semantics, keyboard-only navigation remains intact, and focus rings stay visible.
- **Release evidence:** Wave 10 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.12 Phase 18 Wave 11 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on wave-11 pages and prior-wave shell surfaces.
- **Mobile (`<=720px`):** wave-11 pages stay readable/tap-friendly with wrapped labels/chips, no clipped text, and no horizontal overflow.
- **Visual mapping (wave-11 focus):** wave-11 slugs (`csv_column_selector`, `line_numberer`, `column_aligner`, `csr_generator`, `caa_record_builder`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** neutral outcomes use shared status-note semantics, blocking errors use shared failure semantics, keyboard-only navigation remains intact, and focus rings stay visible.
- **Release evidence:** Wave 11 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.13 Phase 19 Wave 12 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on wave-12 pages and prior-wave shell surfaces.
- **Mobile (`<=720px`):** wave-12 pages stay readable/tap-friendly with wrapped labels/chips, no clipped text, and no horizontal overflow.
- **Visual mapping (wave-12 focus):** wave-12 slugs (`base62_tool`, `unified_diff_generator`, `jwk_pem_converter`, `cert_chain_validator`, `wsl_path_converter`, `markdown_link_extractor`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** neutral outcomes use shared status-note semantics, blocking errors use shared failure semantics, keyboard-only navigation remains intact, and focus rings stay visible.
- **Release evidence:** Wave 12 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.14 Phase 20 Wave 13 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Password Policy Checker, ISO 8601 Duration Tool, JSON Merge Patch, and Column Aligner.
- **Mobile (`<=720px`):** wave-13 primary actions remain full-width/tap-friendly, labels stay readable, and no horizontal overflow appears.
- **Visual mapping (wave-13 focus):** wave-13 slugs (`password_policy_checker`, `iso8601_duration`, `json_merge_patch`, `column_aligner`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 13 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.15 Phase 21 Wave 14 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, SSH Config Validator, CSR Generator, CAA Record Builder, and Base62 Encoder/Decoder.
- **Mobile (`<=720px`):** wave-14 primary actions remain full-width/tap-friendly, page/tool form controls remain readable, and no horizontal overflow appears.
- **Visual mapping (wave-14 focus):** wave-14 touchpoint slugs (`ssh_config_validator`, `csr_generator`, `caa_record_builder`, `base62_tool`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 14 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.16 Phase 22 Wave 15 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Unified Diff Generator, JWK/PEM Converter, Certificate Chain Validator, and WSL Path Converter.
- **Mobile (`<=720px`):** wave-15 primary actions remain full-width/tap-friendly, unified-diff inputs avoid forced two-column layouts, and path-conversion controls remain readable with no horizontal overflow.
- **Visual mapping (wave-15 focus):** wave-15 touchpoint slugs (`unified_diff_generator`, `jwk_pem_converter`, `cert_chain_validator`, `wsl_path_converter`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 15 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.17 Phase 23 Wave 16 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Markdown Link Extractor, and Health Diagnostics.
- **Mobile (`<=720px`):** wave-16 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home navigation controls, Roadmap filters/AI triage action, and Markdown link extraction submit actions.
- **Visual mapping (wave-16 focus):** wave-16 touchpoint slug (`markdown_link_extractor`) resolves to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 16 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.18 Phase 24 Wave 17 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Markdown TOC Generator, Number to Words, JSON to TypeScript, CSS Gradient Generator, JWT Claims Reference, and CSP Header Builder.
- **Mobile (`<=720px`):** wave-17 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-17 tool submit actions.
- **Visual mapping (wave-17 focus):** wave-17 touchpoint slugs (`markdown_toc_generator`, `number_to_words`, `json_to_typescript`, `css_gradient_generator`, `jwt_claims_reference`, `csp_builder`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 17 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.19 Phase 25 Wave 18 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Robots Meta Tag Builder, Cache Control Tool, Markdown Table Formatter, CSV Column Selector, HTTP Methods Reference, and Line Numberer.
- **Mobile (`<=720px`):** wave-18 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-18 tool submit actions.
- **Visual mapping (wave-18 focus):** wave-18 touchpoint slugs (`robots_meta_builder`, `cache_control_tool`, `markdown_table_formatter`, `csv_column_selector`, `http_methods_reference`, `line_numberer`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 18 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.20 Phase 26 Wave 19 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, PII Redactor, Env File Diff, Cron Overlap Checker, Test Data Generator, Password Policy Checker, and ISO8601 Duration Tool.
- **Mobile (`<=720px`):** wave-19 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-19 tool submit actions.
- **Visual mapping (wave-19 focus):** wave-19 touchpoint slugs (`pii_redactor`, `env_file_diff`, `cron_overlap_checker`, `test_data_generator`, `password_policy_checker`, `iso8601_duration`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 19 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.21 Phase 27 Wave 20 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, JSON Merge Patch, Column Aligner, SSH Config Validator, CSR Generator, CAA Record Builder, and Base62 Encoder/Decoder.
- **Mobile (`<=720px`):** wave-20 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-20 tool submit actions.
- **Visual mapping (wave-20 focus):** wave-20 touchpoint slugs (`json_merge_patch`, `column_aligner`, `ssh_config_validator`, `csr_generator`, `caa_record_builder`, `base62_tool`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 20 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.22 Phase 28 Wave 21 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Unified Diff Generator, JWK/PEM Converter, Certificate Chain Validator, WSL Path Converter, Markdown Link Extractor, and Health Diagnostics.
- **Mobile (`<=720px`):** wave-21 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-21 tool/runbook actions.
- **Visual mapping (wave-21 focus):** wave-21 touchpoint slugs (`unified_diff_generator`, `jwk_pem_converter`, `cert_chain_validator`, `wsl_path_converter`, `markdown_link_extractor`, `health_diagnostics`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 21 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.23 Phase 29 Wave 22 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Docker Run to Compose, NATO Phonetic Converter, WiFi QR Code Generator, HMAC Generator, IPv6 ULA Generator, and Random MAC Address Generator.
- **Mobile (`<=720px`):** wave-22 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-22 tool submit actions.
- **Visual mapping (wave-22 focus):** wave-22 touchpoint slugs (`docker_run_to_compose`, `nato_phonetic_converter`, `wifi_qr_generator`, `hmac_generator`, `ipv6_ula_generator`, `random_mac_generator`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 22 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.24 Phase 30 Wave 23 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, List Converter, Email Address Normalizer, IPv4 Address Format Converter, IPv4 Range Expander, Git Command Cheat Sheet, and BIP39 Mnemonic Generator/Validator.
- **Mobile (`<=720px`):** wave-23 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-23 tool submit/generate/validate actions.
- **Visual mapping (wave-23 focus):** wave-23 touchpoint slugs (`list_converter`, `email_address_normalizer`, `ipv4_format_converter`, `ipv4_range_expander`, `git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 23 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.25 Phase 31 Wave 24 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** wave-24 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-24 tool submit/generate/convert actions.
- **Visual mapping (wave-24 focus):** wave-24 touchpoint slugs (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 24 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.26 Phase 32 Wave 25 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** wave-25 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-25 tool submit/generate/convert actions.
- **Visual mapping (wave-25 focus):** wave-25 touchpoint slugs (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and neutral/blocking outcomes continue to use shared status/failure note semantics.
- **Release evidence:** Wave 25 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.27 Phase 33 Wave 26 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** wave-26 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-26 tool submit/generate/convert actions; shared control headings remain readable.
- **Visual mapping (wave-26 focus):** wave-26 touchpoint slugs (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-26 tool outcomes.
- **Release evidence:** Wave 26 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.28 Phase 34 Wave 27 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** wave-27 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-27 tool submit/generate/convert actions; shared control headings remain readable.
- **Visual mapping (wave-27 focus):** wave-27 touchpoint slugs (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-27 tool outcomes.
- **Release evidence:** Wave 27 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.29 Phase 35 Wave 28 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** wave-28 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-28 tool submit/generate/convert actions; shared control headings remain readable.
- **Visual mapping (wave-28 focus):** wave-28 touchpoint slugs (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-28 tool outcomes.
- **Release evidence:** Wave 28 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.30 Phase 36 Wave 29 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** wave-29 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-29 tool submit/generate/convert actions; shared control headings remain readable.
- **Visual mapping (wave-29 focus):** wave-29 touchpoint slugs (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-29 tool outcomes.
- **Release evidence:** Wave 29 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.31 Phase 37 Wave 30 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** wave-30 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-30 tool submit/generate/convert actions; shared control headings remain readable.
- **Visual mapping (wave-30 focus):** wave-30 touchpoint slugs (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-30 tool outcomes.
- **Release evidence:** Wave 30 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.32 Phase 38 Wave 31 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`) remain present on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** wave-31 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-31 tool submit/generate/convert actions; shared control headings remain readable.
- **Visual mapping (wave-31 focus):** wave-31 touchpoint slugs (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) resolve to slug-specific icon assets before category defaults; when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-31 tool outcomes.
- **Release evidence:** Wave 31 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.33 Phase 39 Wave 32 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave32-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** wave-32 form panels and primary actions stay single-column readable and full-width/tap-friendly, including Home controls, Roadmap filters/AI triage action, and wave-32 submit/generate/convert actions; grouped controls keep shared headings and avoid fixed `st.columns(2)` form layouts on wave-32 touchpoint pages.
- **Visual mapping (wave-32 focus):** placeholder-to-real slug aliases resolve to slug-specific icon assets before category defaults (`157_tool_slug_pending_roadmap` + `157_<tool_slug_pending_roadmap>` → `lorem_ipsum_generator`; `158_tool_slug_pending_roadmap` + `158_<tool_slug_pending_roadmap>` → `text_to_binary_hex_octal_converter`); when assets are missing, text fallback badges remain readable.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-32 tool outcomes.
- **Regression tests:** run and pass wave-32 safeguards in `tests/test_ui_helpers.py` (icon alias precedence) and `tests/test_wave32_shell_mobile_markers.py` (shell/mobile marker and layout guardrails).
- **Release evidence:** Wave 32 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.34 Phase 40 Wave 33 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave33-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** grouped controls stay single-column readable with shared control headings, and Home controls, Roadmap filters/AI triage action, plus wave-33 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-33 focus):** placeholder-to-real slug aliases are documented and validated for wave-33 routing (`159_tool_slug_pending_roadmap` + `159_<tool_slug_pending_roadmap>` → `lorem_ipsum_generator`; `160_tool_slug_pending_roadmap` + `160_<tool_slug_pending_roadmap>` → `text_to_binary_hex_octal_converter`), while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-33 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence), `tests/test_wave33_shell_mobile_markers.py` (shell/mobile marker + grouped control guardrails), and `tests/test_wave33_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 33 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.35 Phase 41 Wave 34 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave34-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** grouped controls stay single-column readable with shared control headings, and Home controls, Roadmap filters/AI triage action, plus wave-34 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-34 focus):** placeholder-to-real slug aliases are documented and validated for wave-34 routing (`161_tool_slug_pending_roadmap` + `161_<tool_slug_pending_roadmap>` → `lorem_ipsum_generator`; `162_tool_slug_pending_roadmap` + `162_<tool_slug_pending_roadmap>` → `text_to_binary_hex_octal_converter`), while prior wave-33 aliases (`159*`/`160*`) remain accepted for release evidence continuity and deterministic slug-first icon lookup still precedes category defaults with readable text fallback badges.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-34 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave34_shell_mobile_markers.py` (shell/mobile marker + read-order guardrails), and `tests/test_wave34_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 34 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.36 Phase 42 Wave 35 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave35-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-35 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-35 focus):** placeholder-to-real alias routing notes are documented and validated for wave-35 governance (`163_tool_slug_pending_roadmap` + `163_<tool_slug_pending_roadmap>` → `lorem_ipsum_generator`; `164_tool_slug_pending_roadmap` + `164_<tool_slug_pending_roadmap>` → `text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-35 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave35_shell_mobile_markers.py` (shell/mobile marker + read-order guardrails), and `tests/test_wave35_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 35 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.37 Phase 43 Wave 36 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave36-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-36 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-36 focus):** placeholder-to-real alias routing notes are documented and validated for wave-36 governance (`165_tool_slug_pending_roadmap` + `165_<tool_slug_pending_roadmap>` → wave-36 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `166_tool_slug_pending_roadmap` + `166_<tool_slug_pending_roadmap>` → wave-36 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-36 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave36_shell_mobile_markers.py` (shell/mobile marker + read-order guardrails), and `tests/test_wave36_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 36 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.38 Phase 44 Wave 37 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave37-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 heading hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-37 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-37 focus):** placeholder-to-real alias routing notes are documented and validated for wave-37 governance (`167_tool_slug_pending_roadmap` + `167_<tool_slug_pending_roadmap>` → wave-37 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `168_tool_slug_pending_roadmap` + `168_<tool_slug_pending_roadmap>` → wave-37 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-37 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave37_shell_mobile_markers.py` (shell/mobile marker + heading hierarchy guardrails), and `tests/test_wave37_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 37 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.


### 4.39 Phase 45 Wave 38 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave38-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 heading hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-38 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-38 focus):** placeholder-to-real alias routing notes are documented and validated for wave-38 governance (`169_tool_slug_pending_roadmap` + `169_<tool_slug_pending_roadmap>` → wave-38 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `170_tool_slug_pending_roadmap` + `170_<tool_slug_pending_roadmap>` → wave-38 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-38 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave38_shell_mobile_markers.py` (shell/mobile marker + heading hierarchy guardrails), and `tests/test_wave38_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 38 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.40 Phase 46 Wave 39 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave39-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 heading hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-39 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-39 focus):** placeholder-to-real alias routing notes are documented and validated for wave-39 governance (`171_tool_slug_pending_roadmap` + `171_<tool_slug_pending_roadmap>` → wave-39 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `172_tool_slug_pending_roadmap` + `172_<tool_slug_pending_roadmap>` → wave-39 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-39 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave39_shell_mobile_markers.py` (shell/mobile marker + heading hierarchy guardrails), and `tests/test_wave39_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 39 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.41 Phase 47 Wave 40 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave40-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 heading hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-40 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-40 focus):** placeholder-to-real alias routing notes are documented and validated for wave-40 governance (`173_tool_slug_pending_roadmap` + `173_<tool_slug_pending_roadmap>` → wave-40 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `174_tool_slug_pending_roadmap` + `174_<tool_slug_pending_roadmap>` → wave-40 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-40 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave40_shell_mobile_markers.py` (shell/mobile marker + heading hierarchy guardrails), and `tests/test_wave40_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 40 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.42 Phase 48 Wave 41 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave41-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 heading hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-41 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-41 focus):** placeholder-to-real alias routing notes are documented and validated for wave-41 governance (`175_tool_slug_pending_roadmap` + `175_<tool_slug_pending_roadmap>` → wave-41 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `176_tool_slug_pending_roadmap` + `176_<tool_slug_pending_roadmap>` → wave-41 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-41 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave41_shell_mobile_markers.py` (shell/mobile marker + heading hierarchy guardrails), and `tests/test_wave41_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 41 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.

### 4.43 Phase 49 Wave 42 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave42-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 heading hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-42 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-42 focus):** placeholder-to-real alias routing notes are documented and validated for wave-42 governance (`177_tool_slug_pending_roadmap` + `177_<tool_slug_pending_roadmap>` → wave-42 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `178_tool_slug_pending_roadmap` + `178_<tool_slug_pending_roadmap>` → wave-42 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-42 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave42_shell_mobile_markers.py` (shell/mobile marker + heading hierarchy guardrails), and `tests/test_wave42_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 42 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.


### 4.44 Phase 50 Wave 43 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave43-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 heading hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-43 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-43 focus):** placeholder-to-real alias routing notes are documented and validated for wave-43 governance (`179_tool_slug_pending_roadmap` + `179_<tool_slug_pending_roadmap>` → wave-43 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `180_tool_slug_pending_roadmap` + `180_<tool_slug_pending_roadmap>` → wave-43 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-43 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave43_shell_mobile_markers.py` (shell/mobile marker + heading hierarchy guardrails), `tests/test_wave43_visual_icon_markers.py` (visual slug/icon marker guardrails), and `tests/test_wave43_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 43 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.


### 4.45 Phase 51 Wave 44 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave44-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 heading hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-44 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-44 focus):** placeholder-to-real alias routing notes are documented and validated for wave-44 governance (`181_tool_slug_pending_roadmap` + `181_<tool_slug_pending_roadmap>` → wave-44 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `182_tool_slug_pending_roadmap` + `182_<tool_slug_pending_roadmap>` → wave-44 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-44 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave44_shell_mobile_markers.py` (shell/mobile marker + heading hierarchy guardrails), `tests/test_wave44_visual_icon_markers.py` (visual slug/icon marker guardrails), and `tests/test_wave44_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 44 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.




### 4.46 Phase 52 Wave 45 Regression Checklist (Shell/Mobile/Visual/A11y QA Gates)

Confirm these release-blocking checks pass:

- **Shell consistency:** shared shell + baseline markers (`shell-ready`, `content-rendered`, `wave45-shell-mobile`) remain present on Home, Roadmap & Feedback, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile (`<=720px`):** Step 1/Step 2 heading hierarchy copy remains concise/readable, grouped controls stay single-column readable with shared headings, and Home controls, Roadmap filters/AI triage action, plus wave-45 generate/convert actions remain full-width/tap-friendly with no clipping/overflow.
- **Visual mapping (wave-45 focus):** placeholder-to-real alias routing notes are documented and validated for wave-45 governance (`183_tool_slug_pending_roadmap` + `183_<tool_slug_pending_roadmap>` → wave-45 lorem touchpoint `141_Lorem_Ipsum_Generator.py`/`lorem_ipsum_generator`; `184_tool_slug_pending_roadmap` + `184_<tool_slug_pending_roadmap>` → wave-45 converter touchpoint `142_Text_to_Binary_Hex_Octal_Converter.py`/`text_to_binary_hex_octal_converter`) while deterministic slug-first icon lookup still precedes category defaults and readable text fallback badges remain available.
- **Accessibility:** keyboard-only navigation remains intact, focus rings stay visible, and explicit status semantics (`role="status"`/`role="alert"` with `aria-live`) remain present for Home/Roadmap and wave-45 tool outcomes.
- **Deterministic regression tests:** run and pass `tests/test_ui_helpers.py` (slug precedence + alias mapping), `tests/test_wave45_shell_mobile_markers.py` (shell/mobile marker + heading hierarchy guardrails), `tests/test_wave45_visual_icon_markers.py` (visual slug/icon marker guardrails), and `tests/test_wave45_accessibility_guardrails.py` (status semantics + deterministic outcomes).
- **Release evidence:** Wave 45 outcomes are captured in `docs/release-notes-template.md` with synthetic/sanitized QA evidence only.


## 5. Log Troubleshooting AI States

Without Azure secrets:

- The Azure AI checkbox is disabled.
- The unavailable status note is visible.
- Rule-based log analysis still works.

With local Azure secrets, if available:

- The Azure AI checkbox is enabled.
- Unchecked submit runs rule-based analysis only.
- Checked submit renders the optional Azure AI summary panel.
- Provider errors show a safe fallback note without tracebacks or secret values.

Use synthetic sanitized logs only. Do not paste customer data, passwords, private keys, tokens, or production secrets.

## 6. Screenshot QA

Use `docs/screenshot-guide.md` for required captures. Save temporary QA screenshots in a local untracked workspace folder such as `.artifacts/qa-screenshots/`.

Do not commit screenshots unless a future release explicitly adds tracked documentation images.

## 7. Pre-Commit Safety Check

Confirm none of these are staged or committed:

- `.streamlit/secrets.toml`
- `.env` or `.env.*`
- Real Azure/OpenAI keys or tokens
- QA screenshots
- Generated Python caches
- `.pytest_cache`
- Local virtual environment files

Suggested checks:

```bash
git status --short
git diff --check
git diff --cached --check
```

## 8. Streamlit Cloud Deployment

1. Push the branch to GitHub.
2. Open Streamlit Community Cloud.
3. Create or update the app with `app.py` as the main file.
4. Add Azure secrets only if optional Azure AI summaries are needed.
5. Deploy and repeat the health, navigation, and log-page smoke checks.

## 9. Release Notes

Use `docs/release-notes-template.md` to summarize the release, QA commands, privacy posture, known limitations, Wave 2/Wave 3/Wave 4/Wave 5/Wave 6/Wave 7/Wave 8/Wave 9/Wave 10/Wave 11/Wave 12/Wave 13/Wave 14/Wave 15/Wave 16/Wave 17/Wave 18/Wave 19/Wave 20/Wave 21/Wave 22/Wave 23/Wave 24/Wave 25/Wave 26/Wave 27/Wave 28/Wave 29/Wave 30/Wave 31/Wave 32/Wave 33/Wave 34/Wave 35/Wave 36/Wave 37/Wave 38/Wave 39/Wave 40/Wave 41/Wave 42/Wave 43/Wave 44/Wave 45 shell-mobile-visual-a11y outcomes, and the UX Quality Outcomes release reporting kit.

Minimum UX reporting before publish:
- Record one outcome each for navigation, readability/layout, task completion confidence, and public-safe behavior.
- Keep wording concise and public-safe.
- Use only synthetic/sanitized QA evidence (no customer data or secrets).

For incident triage and diagnostics interpretation during or after rollout, see `docs/ops-runbook.md`.
