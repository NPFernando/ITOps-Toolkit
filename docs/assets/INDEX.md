# Assets Index (phase2)

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
- Port scan icon:
  - `port_reference`, `tls_scanner`

When no card icon asset resolves, cards display the text badge from `ToolMeta.icon`.

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

## Docs/release media inventory

### Posters

- `posters/exported/poster-toolkit-operations-flow-hero-landscape-2400x1350-v01.svg`
- `posters/exported/poster-toolkit-trust-shield-hero-portrait-1080x1350-v01.svg`
- `posters/exported/poster-roadmap-execution-hero-landscape-2400x1350-v01.svg`
- `posters/exported/poster-security-operations-hero-landscape-2400x1350-v01.svg`

Use posters in README/docs/release headers (one primary visual per section to avoid clutter).
