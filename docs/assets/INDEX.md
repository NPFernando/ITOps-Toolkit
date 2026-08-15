# Assets Index (phase8 + wave2 + wave3 + wave4)

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

## Docs/release media inventory

### Posters

- `posters/exported/poster-toolkit-operations-flow-hero-landscape-2400x1350-v01.svg`
- `posters/exported/poster-toolkit-trust-shield-hero-portrait-1080x1350-v01.svg`
- `posters/exported/poster-roadmap-execution-hero-landscape-2400x1350-v01.svg`
- `posters/exported/poster-security-operations-hero-landscape-2400x1350-v01.svg`

Use posters in README/docs/release headers (one primary visual per section to avoid clutter).
