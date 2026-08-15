# Assets Index (phase8 + wave2 + wave3 + wave4 + wave5 + wave6 + wave7 + wave8 + wave9 + wave10 + wave11 + wave12 + wave13 + wave14 + wave15 + wave16 + wave17 + wave18 + wave19)

Generated assets available under `docs/assets/**/exported`. Runtime mappings are implemented in `utils/ui.py`.

## Runtime asset hooks

### Home hero

- `illustrations/exported/illustration-home-hero-ops-flow-light-1600x900-v01.svg`

### Tool card icon mappings (`TOOL_CARD_ICON_ASSETS`)

- DNS icon:
  - `domain_health`, `dns_records`
- SSL icon:
  - `ssl_certificate`
- HTTP probe icon:
  - `http_status`, `webhook_tester`
- Uptime icon:
  - `uptime_trend`
- Incident/response icon:
  - `security_headers`, `cve_lookup`
- JWT inspect icon:
  - `jwt_decoder`, `jwt_encoder`, `jwt_weak_secret`, `jwt_claims_reference`
- JSON validate icon:
  - `json_formatter`, `json_diff`, `json_path_query`, `json_merge_patch`, `json_to_typescript`
- Encoding tools icon:
  - `base64_tool`, `base32_tools`, `base58_tool`, `base62_tool`, `base_converter`
- Regex match icon:
  - `regex_tester`, `regex_replace`, `regex_cheat_sheet`, `pattern_extractor`
- Cron schedule icon:
  - `cron_explainer`, `cron_builder`, `cron_overlap`
- Hash digest icon:
  - `hash_generator`, `file_integrity`, `bcrypt_tool`
- Port scan icon:
  - `port_reference`, `tls_scanner`
- Diff/patch icon:
  - `unified_diff_generator`
- Key format conversion icon:
  - `jwk_pem_converter`
- Certificate chain icon:
  - `cert_chain_validator`
- Path bridge icon:
  - `wsl_path_converter`
- Link extraction icon:
  - `markdown_link_extractor`
- Health diagnostics icon:
  - `health_diagnostics`

When no card icon asset resolves, cards display the text badge from `ToolMeta.icon`.

### Tool card category defaults (`CATEGORY_TOOL_CARD_ICON_ASSETS`)

When a tool has no slug-specific icon mapping, card icons now fall back to category defaults:

- `Network` → `icon-workflow-dns-lookup-outline-24x24-v01.svg`
- `Security` → `icon-workflow-incident-response-outline-24x24-v01.svg`
- `Web & Dev` → `icon-workflow-http-probe-outline-24x24-v01.svg`
- `Data & Text` → `icon-workflow-json-validate-outline-24x24-v01.svg`
- `Ops & Automation` → `icon-workflow-automation-runbook-outline-24x24-v01.svg`
- `Reference` → `icon-workflow-reference-catalog-outline-24x24-v01.svg`

### Tool header category illustrations (`TOOL_HEADER_ILLUSTRATION_BY_CATEGORY`)

- `Network` → `illustration-tool-network-header-flow-light-1600x900-v01.svg`
- `Security` → `illustration-tool-security-header-shield-light-1600x900-v01.svg`
- `Web & Dev` → `illustration-tool-web-dev-header-http-light-1600x900-v01.svg`
- `Data & Text` → `illustration-tool-data-text-header-parse-light-1600x900-v01.svg`
- `Ops & Automation` → `illustration-tool-ops-automation-header-pipeline-light-1600x900-v01.svg`
- `Reference` → `illustration-tool-reference-header-catalog-light-1600x900-v01.svg`

### Empty-state illustrations (`EMPTY_STATE_ILLUSTRATIONS`)

- `ready` → `illustration-empty-state-ready-checklist-light-1200x675-v01.svg`
- `network` → `illustration-empty-state-ready-network-light-1200x675-v01.svg`
- `security` → `illustration-empty-state-ready-shield-light-1200x675-v01.svg`

### Roadmap badge icons (`ROADMAP_BADGE_ICONS`)

- Status: planned, in progress, done, AI recommended
- Source: seed, GitHub

When a roadmap badge asset is unavailable, compact text fallback glyphs are used.

### Phase 8 QA focus for visual mappings

- Verify mapped SVGs render on Home, at least one page per category, and Roadmap badges.
- Verify fallback text badges/glyphs remain readable when any mapped SVG is missing.
- Keep mappings centralized in `utils/ui.py`; do not duplicate page-local icon maps.

### Phase 9 Wave 2 add-on QA focus

- Include one mobile viewport check (`<=720px`) while validating mapped/fallback visuals.
- Include one keyboard-only pass to ensure visual fallbacks do not remove actionable text labels.

### Phase 10 Wave 3 add-on QA focus

- Confirm wave-3 weak-cue slugs resolve to slug-specific icon assets instead of category defaults.
- Confirm slug-specific icon mappings still fall back to text badges when assets are unavailable.
- Include one `<=720px` viewport pass to confirm wave-3 icon/cue surfaces keep readable labels and no clipped chips.
- Include one keyboard-only pass to confirm visual updates did not hide actionable meaning behind decorative media.

### Phase 11 Wave 4 icon mapping extensions

- Auth controls icon: `basic_auth_tool`, `keypair_generator`, `password_policy_checker`, `password_entropy`
- Time operations icon: `business_hours`, `world_clock`, `log_duration`, `date_calculator`
- Data sanitization icon: `pii_redactor`, `csv_cleaner`, `whitespace_visualizer`
- API/reference icon: `windows_event_reference`, `windows_error_reference`, `exit_code_reference`, `timezone_abbreviation_reference`, `http_methods_reference`

### Phase 11 Wave 4 add-on QA focus

- Confirm wave-4 slugs resolve to slug-specific assets before category defaults.
- Confirm slug-specific wave-4 icons still fall back to text badges if SVG rendering is unavailable.
- Include one shell pass confirming grouped navigation + quick search + command palette still expose readable text cues after wave-4 icon updates.
- Include one `<=720px` viewport pass to confirm wave-4 labels/badges/chips stay readable with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-4 visual changes do not hide actionable meaning or break focus visibility.

### Phase 12 Wave 5 icon mapping extensions

- Query/format icon: `sql_formatter`
- Request builder icon: `curl_builder`
- Encoding detect icon: `encoding_detector`
- URL parse icon: `url_parser`
- Gitignore matching icon: `gitignore_tester`

### Phase 13 Wave 6 icon mapping extensions

- Password generation icon: `password_generator`
- URL encoding icon: `url_encoder_decoder`
- Timestamp conversion icon: `timestamp_converter`
- User-agent parsing icon: `user_agent_parser`
- CIDR overlap icon: `cidr_overlap`

### Phase 14 Wave 7 icon mapping extensions

- M365 SKU lookup icon: `m365_sku_decoder`
- Permission bits icon: `chmod_calculator`
- Semantic version compare icon: `semver_tools`
- Duration timeline icon: `iso8601_duration`
- SSH config check icon: `ssh_config_validator`

### Phase 15 Wave 8 icon mapping extensions

- Subnet planning icon: `subnet_calculator`
- IP geolocation icon: `ip_geolocation`
- TOTP token icon: `totp_generator`
- HTTP header parsing icon: `http_header_parser`
- Byte-size conversion icon: `byte_size_converter`

### Phase 16 Wave 9 icon mapping extensions

- MAC address formatting icon: `mac_address_tool`
- Email header trace icon: `email_header_analyzer`
- Text diff comparison icon: `text_diff_checker`
- CIDR aggregation icon: `cidr_aggregator`
- IPv6 compression icon: `ipv6_compressor`

### Phase 17 Wave 10 icon mapping extensions

- Safe Links decode icon: `outlook_safelinks_decoder` (`safelinks_decoder`, `m365_safelinks_decoder`)
- Docker run/compose conversion icon: `docker_run_compose_converter` (`docker_compose_converter`)
- NATO phonetic conversion icon: `nato_phonetic_converter` (`nato_alphabet_converter`)
- Wi-Fi QR generation icon: `wifi_qr_generator` (`wifi_qr_code_generator`)
- HMAC generation icon: `hmac_generator`
- IPv6 ULA generation icon: `ipv6_ula_generator`
- Random MAC generation icon: `random_mac_generator` (`random_mac_address_generator`)
- List conversion icon: `list_converter`
- Email normalization icon: `email_normalizer` (`email_address_normalizer`)
- IPv4 format conversion icon: `ipv4_format_converter`
- IPv4 range expansion icon: `ipv4_range_expander`
- Git command reference icon: `git_command_cheat_sheet`
- BIP39 mnemonic icon: `bip39_mnemonic` (`bip39_mnemonic_generator_validator`)
- Lorem ipsum generation icon: `lorem_ipsum_generator`
- Text radix conversion icon: `text_radix_converter`

### Phase 18 Wave 11 icon mapping extensions

- CSV column selector icon: `csv_column_selector`
- Line numbering icon: `line_numberer`
- Column alignment icon: `column_aligner`
- CSR generation icon: `csr_generator`
- CAA record builder icon: `caa_record_builder`

### Phase 19 Wave 12 icon mapping extensions

- Base62 encoding icon: `base62_tool`
- Unified diff icon: `unified_diff_generator`
- JWK/PEM conversion icon: `jwk_pem_converter`
- Certificate chain validation icon: `cert_chain_validator`
- Path conversion icon: `wsl_path_converter`
- Markdown link extraction icon: `markdown_link_extractor`

### Phase 20 Wave 13 icon mapping extensions

- Password policy icon: `password_policy_checker`
- ISO 8601 duration icon: `iso8601_duration`
- JSON merge patch icon: `json_merge_patch`
- Column align icon: `column_aligner`

### Phase 21 Wave 14 icon mapping coverage

- SSH config check icon: `ssh_config_validator`
- CSR generation icon: `csr_generator`
- CAA record builder icon: `caa_record_builder`
- Base62 encoding icon: `base62_tool`

### Phase 22 Wave 15 icon mapping coverage

- Unified diff icon: `unified_diff_generator`
- JWK/PEM conversion icon: `jwk_pem_converter`
- Certificate chain validation icon: `cert_chain_validator`
- Path conversion icon: `wsl_path_converter`

### Phase 23 Wave 16 icon mapping coverage

- Markdown link extraction icon: `markdown_link_extractor`

### Phase 24 Wave 17 icon mapping coverage

- Markdown TOC icon: `markdown_toc_generator`
- Number conversion icon: `number_to_words`
- JSON types icon: `json_to_typescript`
- CSS gradient icon: `css_gradient_generator`
- JWT claims icon: `jwt_claims_reference`
- CSP header icon: `csp_builder`

### Phase 26 Wave 19 icon mapping coverage

- PII redaction icon: `pii_redactor`
- Env file diff icon: `env_file_diff`
- Cron overlap icon: `cron_overlap_checker`
- Test data fixture icon: `test_data_generator`
- Password policy icon: `password_policy_checker`
- ISO 8601 duration icon: `iso8601_duration`

### Phase 27 Wave 20 icon mapping coverage

- JSON merge patch icon: `json_merge_patch`
- Column aligner icon: `column_aligner`
- SSH config validator icon: `ssh_config_validator`
- CSR generation icon: `csr_generator`
- CAA record builder icon: `caa_record_builder`
- Base62 encoding icon: `base62_tool`

### Phase 12 Wave 5 add-on QA focus

- Confirm wave-5 slugs resolve to slug-specific assets before category defaults.
- Confirm slug-specific wave-5 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming grouped navigation + quick search + command palette still expose readable text cues after wave-5 icon updates.
- Include one `<=720px` viewport pass to confirm wave-5 labels/badges/chips/helper text stay readable with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-5 visual changes do not hide actionable meaning or break focus visibility.

### Phase 13 Wave 6 add-on QA focus

- Confirm wave-6 weak-cue slugs resolve to slug-specific assets before category defaults.
- Confirm slug-specific wave-6 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming grouped navigation + quick search + command palette still expose readable text cues after wave-6 icon updates.
- Include one `<=720px` viewport pass to confirm wave-6 labels/badges/chips/helper text stay readable with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-6 visual changes do not hide actionable meaning or break focus visibility.

### Phase 14 Wave 7 add-on QA focus

- Confirm wave-7 weak-cue slugs resolve to slug-specific assets before category defaults.
- Confirm slug-specific wave-7 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming grouped navigation + quick search + command palette still expose readable text cues after wave-7 icon updates.
- Include one `<=720px` viewport pass to confirm wave-7 labels/badges/chips/helper text stay readable with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-7 visual changes do not hide actionable meaning or break focus visibility.

### Phase 15 Wave 8 add-on QA focus

- Confirm wave-8 weak-cue slugs resolve to slug-specific assets before category defaults.
- Confirm slug-specific wave-8 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming grouped navigation + quick search + command palette still expose readable text cues after wave-8 icon updates.
- Include one `<=720px` viewport pass to confirm wave-8 labels/badges/chips/helper text stay readable with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-8 visual changes do not hide actionable meaning or break focus visibility.

### Phase 16 Wave 9 add-on QA focus

- Confirm wave-9 weak-cue slugs resolve to slug-specific assets before category defaults.
- Confirm slug-specific wave-9 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming grouped navigation + quick search + command palette still expose readable text cues after wave-9 icon updates.
- Include one `<=720px` viewport pass to confirm wave-9 labels/badges/chips/helper text stay readable with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-9 visual changes do not hide actionable meaning or break focus visibility.

### Phase 17 Wave 10 add-on QA focus

- Confirm wave-10 planned slugs resolve to slug-specific assets before category defaults.
- Confirm slug-specific wave-10 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on wave-10 pages.
- Include one `<=720px` viewport pass to confirm wave-10 forms/results stay readable without page-scoped mobile CSS overrides.
- Include one keyboard-only pass to confirm wave-10 notice semantics and focus visibility remain intact.

### Phase 18 Wave 11 add-on QA focus

- Confirm wave-11 slugs resolve to slug-specific assets before category defaults (`csv_column_selector`, `line_numberer`, `column_aligner`, `csr_generator`, `caa_record_builder`).
- Confirm slug-specific wave-11 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on wave-11 pages.
- Include one `<=720px` viewport pass to confirm wave-11 forms/results stay readable with wrapped labels/chips and no clipping/overflow.
- Include one keyboard-only pass to confirm wave-11 notice semantics and focus visibility remain intact.

### Phase 19 Wave 12 add-on QA focus

- Confirm wave-12 slugs resolve to slug-specific assets before category defaults (`base62_tool`, `unified_diff_generator`, `jwk_pem_converter`, `cert_chain_validator`, `wsl_path_converter`, `markdown_link_extractor`).
- Confirm slug-specific wave-12 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on wave-12 pages.
- Include one `<=720px` viewport pass to confirm wave-12 forms/results stay readable with wrapped labels/chips and no clipping/overflow.
- Include one keyboard-only pass to confirm wave-12 notice semantics and focus visibility remain intact.

### Phase 20 Wave 13 add-on QA focus

- Confirm wave-13 slugs resolve to slug-specific assets before category defaults (`password_policy_checker`, `iso8601_duration`, `json_merge_patch`, `column_aligner`).
- Confirm slug-specific wave-13 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on Home, Roadmap, and wave-13 pages.
- Include one `<=720px` viewport pass to confirm wave-13 primary actions stay full-width/tap-friendly with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-13 notice semantics and focus visibility remain intact.

### Phase 21 Wave 14 add-on QA focus

- Confirm wave-14 touchpoint slugs resolve to slug-specific assets before category defaults (`ssh_config_validator`, `csr_generator`, `caa_record_builder`, `base62_tool`).
- Confirm slug-specific wave-14 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on Home, Roadmap, and wave-14 pages.
- Include one `<=720px` viewport pass to confirm wave-14 primary actions stay full-width/tap-friendly with readable controls and no clipping/overflow.
- Include one keyboard-only pass to confirm wave-14 notice semantics and focus visibility remain intact.

### Phase 22 Wave 15 add-on QA focus

- Confirm wave-15 touchpoint slugs resolve to slug-specific assets before category defaults (`unified_diff_generator`, `jwk_pem_converter`, `cert_chain_validator`, `wsl_path_converter`).
- Confirm slug-specific wave-15 icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on Home, Roadmap, and wave-15 pages.
- Include one `<=720px` viewport pass to confirm wave-15 primary actions stay full-width/tap-friendly, with single-column-friendly inputs and no clipping/overflow.
- Include one keyboard-only pass to confirm wave-15 notice semantics and focus visibility remain intact.

### Phase 23 Wave 16 add-on QA focus

- Confirm wave-16 touchpoint slug resolves to slug-specific assets before category defaults (`markdown_link_extractor`).
- Confirm the wave-16 slug-specific icon still falls back to a text badge when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on Home, Roadmap, Markdown Link Extractor, and Health Diagnostics.
- Include one `<=720px` viewport pass to confirm Home controls, Roadmap filters/AI triage action, and Markdown extraction submit action stay full-width/tap-friendly with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-16 notice semantics and focus visibility remain intact.

### Phase 24 Wave 17 add-on QA focus

- Confirm wave-17 touchpoint slugs resolve to slug-specific assets before category defaults (`markdown_toc_generator`, `number_to_words`, `json_to_typescript`, `css_gradient_generator`, `jwt_claims_reference`, `csp_builder`).
- Confirm wave-17 slug-specific icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on Home, Roadmap, and wave-17 touchpoint pages.
- Include one `<=720px` viewport pass to confirm Home controls, Roadmap filters/AI triage action, and wave-17 submit actions stay full-width/tap-friendly with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-17 notice semantics and focus visibility remain intact.

### Phase 25 Wave 18 add-on QA focus

- Confirm wave-18 touchpoint slugs resolve to slug-specific assets before category defaults (`robots_meta_builder`, `cache_control_tool`, `markdown_table_formatter`, `csv_column_selector`, `http_methods_reference`, `line_numberer`).
- Confirm wave-18 slug-specific icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on Home, Roadmap, and wave-18 touchpoint pages.
- Include one `<=720px` viewport pass to confirm Home controls, Roadmap filters/AI triage action, and wave-18 submit actions stay full-width/tap-friendly with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-18 notice semantics and focus visibility remain intact.

### Phase 26 Wave 19 add-on QA focus

- Confirm wave-19 touchpoint slugs resolve to slug-specific assets before category defaults (`pii_redactor`, `env_file_diff`, `cron_overlap_checker`, `test_data_generator`, `password_policy_checker`, `iso8601_duration`).
- Confirm wave-19 slug-specific icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on Home, Roadmap, and wave-19 touchpoint pages.
- Include one `<=720px` viewport pass to confirm Home controls, Roadmap filters/AI triage action, and wave-19 submit actions stay full-width/tap-friendly with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-19 notice semantics and focus visibility remain intact.

### Phase 27 Wave 20 add-on QA focus

- Confirm wave-20 touchpoint slugs resolve to slug-specific assets before category defaults (`json_merge_patch`, `column_aligner`, `ssh_config_validator`, `csr_generator`, `caa_record_builder`, `base62_tool`).
- Confirm wave-20 slug-specific icons still fall back to text badges when SVG rendering is unavailable.
- Include one shell pass confirming shared shell + baseline markers remain visible/unchanged on Home, Roadmap, and wave-20 touchpoint pages.
- Include one `<=720px` viewport pass to confirm Home controls, Roadmap filters/AI triage action, and wave-20 submit actions stay full-width/tap-friendly with no clipping/overflow.
- Include one keyboard-only pass to confirm wave-20 notice semantics and focus visibility remain intact.

## Docs/release media inventory

### Posters

- `posters/exported/poster-toolkit-operations-flow-hero-landscape-2400x1350-v01.svg`
- `posters/exported/poster-toolkit-trust-shield-hero-portrait-1080x1350-v01.svg`
- `posters/exported/poster-roadmap-execution-hero-landscape-2400x1350-v01.svg`
- `posters/exported/poster-security-operations-hero-landscape-2400x1350-v01.svg`

Use posters in README/docs/release headers (one primary visual per section to avoid clutter).
