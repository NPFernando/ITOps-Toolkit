# ITOps Toolkit Design System

This guide documents the UI direction used for the Streamlit dashboard and tool pages.

## Visual Direction

- Use a close match to the reference dashboard: dark left navigation, light work area, blue ITOps branding, and restrained security/operations visuals.
- Keep the interface practical for IT admins, MSP engineers, automation engineers, and DevOps users. The UI should feel fast, trustworthy, and work-focused.
- Preserve public-safe messaging near inputs that may receive domains, URLs, logs, JWTs, JSON, or encoded text.

## Layout

- Use the shared shell from `utils/ui.py` for global CSS, sidebar navigation, tool metadata, page headers, cards, and notices.
- Home page structure:
  - Hero section with product title, short value statement, search input, trust chips, and the IT/security visual.
  - Home navigation mode switch: Quick access (personalized sections) and All tools (full catalog).
  - Guided **Start Here Workflows** section to route first-time users through common triage flows.
  - Quick access sections may include Your Favorites, Recently Used (or Popular to Start), Shared Favorites, and New & Noteworthy.
  - All tools mode supports search + profession filtering + sort controls.
  - Feature strip for reliability, privacy, public-safe use, open source status, and mobile support.
  - Important notice band for sensitive-data handling.
- Roadmap & Feedback page structure:
  - Header with public roadmap context, Roadmap/Feedback tabs, and GitHub actions.
  - Board summary cards for public categories across seed and GitHub issue items.
  - Search and category filters above four roadmap columns: Planned, In Progress, Complete, and AI Recommended.
  - Seed vote-style numbers are curated display values; GitHub issue numbers use public reaction totals.
- Tool pages use a compact page header and keep the form-first workflow visible above results.
- Native Streamlit multipage navigation is disabled with `client.showSidebarNavigation = false`; use the shared sidebar shell instead.
- Streamlit native theme tokens in `.streamlit/config.toml` must stay aligned with the shared shell. They control the first loading frame before `utils/ui.py` CSS is injected, including sidebar color, app background, and toolbar visibility.
- Cards use an 8px radius, subtle borders, and no nested cards.

## Color And Typography

- Primary blue: `#126bff`.
- Dark sidebar: `#071a33` to `#061429`.
- Text ink: `#07142f`.
- Muted text: `#52637f`.
- Border line: `#d7e2f5`.
- Accent colors:
  - DNS/public-safe green: `#23b84d`.
  - SSL/JWT purple: `#7047e8`.
  - HTTP/open-source orange: `#ff6b13`.
  - JSON teal: `#11aab8`.
- Typography uses Manrope through the shared CSS. Keep letter spacing at `0`.

## Components

- Sidebar:
  - Brand block, navigation, safety card, and about card are required.
  - Primary top-level links are Home and Roadmap & Feedback, followed by grouped tool links.
  - Quick-search input and grouped navigation should keep strong contrast and clear spacing so scanning still works in long tool lists.
  - Active navigation state uses the blue gradient treatment.
  - Keep Streamlit's collapse and expand controls visible; hide native page navigation and deploy/tool chrome without hiding `stExpandSidebarButton`.
  - Add new tools by extending the `TOOLS` metadata in `utils/ui.py`.
  - Keep the command palette (`Ctrl/Cmd+K`) aligned with the same `TOOLS` metadata and page-link navigation behavior.
- Tool cards:
  - Use the central tool title, description, icon text, accent color, and Streamlit page link.
  - Show category metadata inside each card for faster visual scanning on the home grid.
  - Buttons should navigate through Streamlit page links.
- Page headers:
  - Use `render_page_header` instead of page-local `st.title` and `st.caption` combinations.
  - Keep the small uppercase overline (`<category> Tool`) above the title to reinforce page context.
  - Header illustrations are optional and category-driven; keep them low-clutter and decorative so titles/descriptions remain primary.
  - Use the warning parameter for sensitive-data reminders.
- Tool page panels:
  - Wrap the primary input workflow in `tool_form_panel` and introduce it with `render_form_intro`.
  - Use `render_empty_state` before first submission so blank pages explain what will appear; optional generated illustrations should remain secondary.
  - Use `render_section_heading` for results, headers, recommendations, and downloads; maintain eyebrow + heading + optional description hierarchy.
  - Use `tool_result_panel` and `tool_download_panel` for framed result and export areas.
  - Use `display_rows_frame` for mixed field/value result tables before passing them to `st.dataframe`.
  - Use `render_status_note` for compact success, info, warning, neutral, or optional AI state messages.
- Notices:
  - Use `render_important_notice` for the home-page sensitive-data message.
- Roadmap board:
  - Use `utils/roadmap.py` for seed loading, GitHub issue normalization, category counts, filtering, and GitHub feedback URLs.
  - Use `utils/github_issues.py` for read-only anonymous GitHub Issues API calls.
  - Label curated AI suggestions as static recommendations based on the toolkit direction. Do not call Azure/OpenAI from the roadmap page.
  - Keep feedback public-safe copy visible near submit links.
  - Show GitHub issue source badges and links for live public requests; show seed badges for curated local items.
- Generated assets:
  - Runtime visual hooks are centralized in `utils/ui.py`:
    - `HOME_HERO_ILLUSTRATION`
    - `TOOL_CARD_ICON_ASSETS`
    - `CATEGORY_TOOL_CARD_ICON_ASSETS`
    - `TOOL_HEADER_ILLUSTRATION_BY_CATEGORY`
    - `EMPTY_STATE_ILLUSTRATIONS`
    - `ROADMAP_BADGE_ICONS`
  - Use exported outputs under `docs/assets/icons/exported/` and `docs/assets/illustrations/exported/` for runtime/documentation visuals.
  - Keep editable originals under `docs/assets/*/source` and regenerate exports instead of editing exported files directly.

## Generated Visuals Policy

- Generated SVGs are enhancement-only UI media; they must never be required for tool execution, validation, or results.
- Keep visual mappings semantic by context (network/security/data/etc.) and source all runtime mappings from `utils/ui.py`, not page-local constants.
- Prefer lightweight SVG exports for runtime hooks; reserve posters for documentation/release surfaces.
- Every generated visual used in runtime must have a graceful fallback path.

## Decorative vs Semantic Usage

- Runtime UI-generated images (hero, card icons, page-header illustrations, empty-state illustrations, roadmap badge icons) are decorative and rendered with empty alt plus `aria-hidden`/presentation semantics.
- Meaningful user-facing text (tool titles, category labels, status words like Planned/In Progress/Complete, source labels like Seed/GitHub) must remain in adjacent text, not only in imagery.
- Documentation images may be semantic; in docs, provide concise alt text when an image carries meaning.

## Fallback Rules

- Asset load boundary: `_svg_data_uri` returns `None` when an SVG is missing or invalid path/extension; callers must degrade safely.
- Home hero: falls back to the built-in CSS hero visual when the generated hero SVG is unavailable.
- Tool cards: fall back to text icon abbreviations from `ToolMeta.icon` when mapped SVGs are unavailable.
- Page headers and empty states: omit the illustration slot when no mapped SVG resolves; keep title/description primary.
- Roadmap badges: fall back to compact text glyphs when SVG badges are unavailable.

## Responsive Rules

- The sidebar remains Streamlit-native so users can collapse it on narrow screens.
- Home hero content stacks naturally on mobile.
- Generated hero visual reduces minimum height at smaller breakpoints (`<=1100px`, `<=720px`) to keep above-the-fold content readable.
- Touch targets for pills/buttons should stay at least ~2.3rem tall so filter/sort controls remain usable on phones.
- Quick-access and All-tools sections should wrap naturally; avoid fixed card widths that break mixed sections (favorites/recents/shared/new).
- Feature strips collapse from five columns to two columns and then one column.
- Tool cards should not rely on fixed text widths; long labels must wrap cleanly.
- Tool-page action buttons (submit/download) should wrap label text and expand full-width on narrow screens.
- Tool page headers with illustrations switch from side-by-side to stacked layout on narrow screens; illustration width becomes full-width below mobile breakpoint.
- Roadmap columns may scroll vertically on desktop, then stack naturally on narrow screens.

## Accessibility Rules

- Keep visible `:focus-visible` styles across links, buttons, and form controls in the shared shell CSS.
- Prefer semantic notice containers (`role="note"`) for shared warning/info blocks (home notice, roadmap notices).
- Preserve keyboard accessibility for sidebar quick search, pills (mode/filter/sort), and command palette triggers.
- Keep roadmap card/body text sizes readable after styling changes; avoid shrinking below body-readable sizes.

## Phase 8 Cross-page Consistency Baseline

- Treat `docs/ui-consistency-audit-matrix-phase8.md` as the release baseline for header/form/empty-state/action-label/notice patterns.
- Tool pages should converge on shared primitives (`render_page_header`, `render_form_intro`, `render_empty_state`, `render_section_heading`, shared status/failure notes).
- `Roadmap & Feedback` and `Health Diagnostics` are intentional non-tool exceptions; keep them documented when their layout differs.
- For mobile QA, keep `<=720px` checks explicit: stacked page-header illustrations, full-width wrapped action buttons, and readable tap targets.

## Phase 9 Wave 2 Standards (Shell, Mobile, Visual, A11y)

- **Shell integrity:** keep shared shell behaviors stable (custom sidebar, command palette trigger, grouped navigation, quick search, and safe notice copy).
- **Mobile baseline (`<=720px`):** no clipped labels, no horizontal scroll in main content, full-width wrapped submit/download actions, and stacked header illustrations.
- **Visual mapping safety:** home hero, tool-card icon mappings, category fallbacks, and roadmap badges must degrade to readable text/glyph fallbacks when SVG assets are unavailable.
- **Accessibility baseline:** preserve keyboard reachability for sidebar/filter/actions, keep `:focus-visible` contrast in dark/light surfaces, keep notice semantics (`role="note"`), and keep decorative SVGs non-semantic (`aria-hidden`, empty alt).
- **Exception handling:** if a non-tool layout intentionally diverges (Roadmap/Health Diagnostics), keep the exception documented and readable on desktop/mobile.

### Wave 2 QA handoff guidance

- Use `docs/release-checklist.md` Wave 2 regression checks as release gates.
- Capture only synthetic/sanitized evidence in release notes.
- Treat shell/mobile/visual/a11y regressions as release blockers until resolved or explicitly documented.

## Phase 10 Wave 3 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell clarity:** keep primary actions and warnings text-first and obvious even when decorative visuals fail to load.
- **Mobile baseline (`<=720px`):** keep action labels, badges, and status chips fully readable/wrapped with no horizontal overflow.
- **Visual mapping integrity:** for weak-cue tool slugs, prefer slug-specific icon mappings before category defaults; keep text badge fallback readable.
- **Accessibility guardrail:** decorative SVGs stay non-semantic (`aria-hidden`, empty alt), while all actionable meaning remains in adjacent text/labels.
- **QA gate behavior:** treat Wave 3 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 3 QA handoff guidance

- Run Wave 3 checks in `docs/release-checklist.md` before release.
- Record Wave 3 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep exceptions explicit (for example, non-tool layouts) and confirm they remain readable on desktop/mobile.

## Phase 11 Wave 4 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep grouped navigation, quick search, command palette trigger, and warning/notice copy stable across wave-4 tool additions.
- **Mobile baseline (`<=720px`):** keep wave-4 action labels, badges, and status chips wrapped/readable with no horizontal overflow.
- **Visual mapping integrity:** keep wave-4 slug-specific icon mappings first, then category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep decorative SVGs non-semantic (`aria-hidden`, empty alt), preserve keyboard flow for shell/tool actions, and keep visible focus states.
- **QA gate behavior:** treat Wave 4 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 4 QA handoff guidance

- Run Wave 4 checks in `docs/release-checklist.md` before release.
- Record Wave 4 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-4 updates.

## Phase 12 Wave 5 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep grouped navigation, quick search, command palette trigger, and wave-5 labels/status cues text-first and readable.
- **Mobile baseline (`<=720px`):** keep wave-5 action labels, chips, and helper text wrapped/readable with no clipped text or horizontal overflow.
- **Visual mapping integrity:** keep wave-5 slug-specific icon mappings first (`sql_formatter`, `curl_builder`, `encoding_detector`, `url_parser`, `gitignore_tester`), then category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep decorative SVGs non-semantic (`aria-hidden`, empty alt), preserve keyboard flow for shell/tool actions, and keep visible focus states and note semantics.
- **QA gate behavior:** treat Wave 5 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 5 QA handoff guidance

- Run Wave 5 checks in `docs/release-checklist.md` before release.
- Record Wave 5 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-5 updates.

## Phase 13 Wave 6 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep grouped navigation, quick search, command palette trigger, and wave-6 labels/status cues text-first and readable.
- **Mobile baseline (`<=720px`):** keep wave-6 action labels, chips, and helper text wrapped/readable with no clipped text or horizontal overflow.
- **Visual mapping integrity:** keep wave-6 slug-specific icon mappings first (`password_generator`, `url_encoder_decoder`, `timestamp_converter`, `user_agent_parser`, `cidr_overlap`), then category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep decorative SVGs non-semantic (`aria-hidden`, empty alt), preserve keyboard flow for shell/tool actions, and keep visible focus states and note semantics.
- **QA gate behavior:** treat Wave 6 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 6 QA handoff guidance

- Run Wave 6 checks in `docs/release-checklist.md` before release.
- Record Wave 6 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-6 updates.

## Phase 14 Wave 7 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep grouped navigation, quick search, command palette trigger, and wave-7 labels/status cues text-first and readable.
- **Mobile baseline (`<=720px`):** keep wave-7 action labels, chips, and helper text wrapped/readable with no clipped text or horizontal overflow.
- **Visual mapping integrity:** keep wave-7 slug-specific icon mappings first (`m365_sku_decoder`, `chmod_calculator`, `semver_tools`, `iso8601_duration`, `ssh_config_validator`), then category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep decorative SVGs non-semantic (`aria-hidden`, empty alt), preserve keyboard flow for shell/tool actions, and keep visible focus states and note semantics.
- **QA gate behavior:** treat Wave 7 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 7 QA handoff guidance

- Run Wave 7 checks in `docs/release-checklist.md` before release.
- Record Wave 7 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-7 updates.

## Phase 15 Wave 8 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep grouped navigation, quick search, command palette trigger, and wave-8 labels/status cues text-first and readable.
- **Mobile baseline (`<=720px`):** keep wave-8 action labels, chips, and helper text wrapped/readable with no clipped text or horizontal overflow.
- **Visual mapping integrity:** keep wave-8 slug-specific icon mappings first (`subnet_calculator`, `ip_geolocation`, `totp_generator`, `http_header_parser`, `byte_size_converter`), then category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep decorative SVGs non-semantic (`aria-hidden`, empty alt), preserve keyboard flow for shell/tool actions, and keep visible focus states and note semantics.
- **QA gate behavior:** treat Wave 8 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 8 QA handoff guidance

- Run Wave 8 checks in `docs/release-checklist.md` before release.
- Record Wave 8 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-8 updates.

## Phase 16 Wave 9 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep grouped navigation, quick search, command palette trigger, and wave-9 labels/status cues text-first and readable.
- **Mobile baseline (`<=720px`):** keep wave-9 action labels, chips, and helper text wrapped/readable with no clipped text or horizontal overflow.
- **Visual mapping integrity:** keep wave-9 slug-specific icon mappings first (`mac_address_tool`, `email_header_analyzer`, `text_diff_checker`, `cidr_aggregator`, `ipv6_compressor`), then category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep decorative SVGs non-semantic (`aria-hidden`, empty alt), preserve keyboard flow for shell/tool actions, and keep visible focus states and note semantics.
- **QA gate behavior:** treat Wave 9 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 9 QA handoff guidance

- Run Wave 9 checks in `docs/release-checklist.md` before release.
- Record Wave 9 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-9 updates.

## Phase 17 Wave 10 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable across Home, Roadmap, Domain Health Checker, WHOIS Lookup, Bulk Domain Health, DNS Propagation Checker, DKIM Selector Lookup, Email Record Builder, and Health Diagnostics.
- **Mobile baseline (`<=720px`):** keep form/results readability and tap targets aligned to shared shell CSS; avoid page-scoped mobile overrides that drift from the common baseline.
- **Visual mapping integrity:** keep wave-10 planned slugs mapped to generated assets before category defaults (`outlook_safelinks_decoder`, `docker_run_compose_converter`, `nato_phonetic_converter`, `wifi_qr_generator`, `hmac_generator`, `ipv6_ula_generator`, `random_mac_generator`, `list_converter`, `email_normalizer`, `ipv4_format_converter`, `ipv4_range_expander`, `git_command_cheat_sheet`, `bip39_mnemonic`, `lorem_ipsum_generator`, `text_radix_converter`).
- **Accessibility guardrail:** keep notice semantics and tone intent clear (`role="status"` for neutral outcomes, shared failure semantics for blocking errors), while preserving keyboard flow and visible focus rings.
- **QA gate behavior:** treat Wave 10 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 10 QA handoff guidance

- Run Wave 10 checks in `docs/release-checklist.md` before release.
- Record Wave 10 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-10 updates.

## Phase 18 Wave 11 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable across wave-11 pages and prior-wave shell surfaces.
- **Mobile baseline (`<=720px`):** keep wave-11 forms/results readable and tap-friendly with wrapped labels/chips, no clipped text, and no horizontal overflow.
- **Visual mapping integrity:** keep wave-11 slug-specific icon mappings first (`csv_column_selector`, `line_numberer`, `column_aligner`, `csr_generator`, `caa_record_builder`), then category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep neutral/blocking outcome semantics aligned to shared status/failure note patterns, preserve keyboard flow, and keep visible focus rings.
- **QA gate behavior:** treat Wave 11 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 11 QA handoff guidance

- Run Wave 11 checks in `docs/release-checklist.md` before release.
- Record Wave 11 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-11 updates.

## Phase 19 Wave 12 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable across wave-12 pages and prior-wave shell surfaces.
- **Mobile baseline (`<=720px`):** keep wave-12 forms/results readable and tap-friendly with wrapped labels/chips, no clipped text, and no horizontal overflow.
- **Visual mapping integrity:** keep wave-12 slug-specific icon mappings first (`base62_tool`, `unified_diff_generator`, `jwk_pem_converter`, `cert_chain_validator`, `wsl_path_converter`, `markdown_link_extractor`), then category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep neutral/blocking outcome semantics aligned to shared status/failure note patterns, preserve keyboard flow, and keep visible focus rings.
- **QA gate behavior:** treat Wave 12 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 12 QA handoff guidance

- Run Wave 12 checks in `docs/release-checklist.md` before release.
- Record Wave 12 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-12 updates.

## Phase 20 Wave 13 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Password Policy Checker, ISO 8601 Duration Tool, JSON Merge Patch, and Column Aligner.
- **Mobile baseline (`<=720px`):** keep wave-13 primary actions full-width and tap-friendly (`use_container_width=True`) with no clipped labels or horizontal overflow.
- **Visual mapping integrity:** keep wave-13 slug-specific icon mappings first (`password_policy_checker`, `iso8601_duration`, `json_merge_patch`, `column_aligner`), then category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 13 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 13 QA handoff guidance

- Run Wave 13 checks in `docs/release-checklist.md` before release.
- Record Wave 13 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-13 updates.

## Phase 21 Wave 14 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, SSH Config Validator, CSR Generator, CAA Record Builder, and Base62 Encoder/Decoder.
- **Mobile baseline (`<=720px`):** keep wave-14 primary actions full-width and tap-friendly (`use_container_width=True`), keep form controls wrapped/readable, and avoid forced horizontal selector layouts that clip options.
- **Visual mapping integrity:** keep slug-specific icon mappings readable for wave-14 touchpoints (`ssh_config_validator`, `csr_generator`, `caa_record_builder`, `base62_tool`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home, Roadmap filters, and form actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 14 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 14 QA handoff guidance

- Run Wave 14 checks in `docs/release-checklist.md` before release.
- Record Wave 14 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-14 updates.

## Phase 22 Wave 15 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Unified Diff Generator, JWK/PEM Converter, Certificate Chain Validator, and WSL Path Converter.
- **Mobile baseline (`<=720px`):** keep wave-15 primary actions full-width and tap-friendly (`use_container_width=True`), avoid forced two-column input layouts on wave-15 pages, and keep conversion target controls readable on small screens.
- **Visual mapping integrity:** keep wave-15 touchpoint slug mappings readable (`unified_diff_generator`, `jwk_pem_converter`, `cert_chain_validator`, `wsl_path_converter`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home, Roadmap filter/actions, and wave-15 form actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 15 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 15 QA handoff guidance

- Run Wave 15 checks in `docs/release-checklist.md` before release.
- Record Wave 15 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-15 updates.

## Phase 23 Wave 16 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Markdown Link Extractor, and Health Diagnostics.
- **Mobile baseline (`<=720px`):** keep wave-16 primary actions full-width and tap-friendly (`use_container_width=True`), ensure form-panel groupings stay single-column readable, and keep runbook/action links easy to tap.
- **Visual mapping integrity:** keep wave-16 touchpoint slug mapping readable for `markdown_link_extractor` before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home mode toggles, Roadmap filters/AI triage actions, and Markdown extraction actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 16 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 16 QA handoff guidance

- Run Wave 16 checks in `docs/release-checklist.md` before release.
- Record Wave 16 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-16 updates.

## Phase 24 Wave 17 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Markdown TOC Generator, Number to Words, JSON to TypeScript, CSS Gradient Generator, JWT Claims Reference, and CSP Header Builder.
- **Mobile baseline (`<=720px`):** keep wave-17 primary actions full-width and tap-friendly (`use_container_width=True`), keep filter/form panels single-column readable, and avoid forced two-column control layouts on wave-17 pages.
- **Visual mapping integrity:** keep wave-17 touchpoint slug mappings readable (`markdown_toc_generator`, `number_to_words`, `json_to_typescript`, `css_gradient_generator`, `jwt_claims_reference`, `csp_builder`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home controls, Roadmap filters/AI triage action, and wave-17 form actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 17 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 17 QA handoff guidance

- Run Wave 17 checks in `docs/release-checklist.md` before release.
- Record Wave 17 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-17 updates.

## Phase 25 Wave 18 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Robots Meta Tag Builder, Cache Control Tool, Markdown Table Formatter, CSV Column Selector, HTTP Methods Reference, and Line Numberer.
- **Mobile baseline (`<=720px`):** keep wave-18 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-18 controls single-column readable, and avoid forced two-column control layouts on wave-18 touchpoint pages.
- **Visual mapping integrity:** keep wave-18 touchpoint slug mappings readable (`robots_meta_builder`, `cache_control_tool`, `markdown_table_formatter`, `csv_column_selector`, `http_methods_reference`, `line_numberer`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home controls, Roadmap filters/AI triage action, and wave-18 form actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 18 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 18 QA handoff guidance

- Run Wave 18 checks in `docs/release-checklist.md` before release.
- Record Wave 18 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-18 updates.

## Phase 26 Wave 19 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, PII Redactor, Env File Diff, Cron Overlap Checker, Test Data Generator, Password Policy Checker, and ISO8601 Duration Tool.
- **Mobile baseline (`<=720px`):** keep wave-19 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-19 controls single-column readable, and avoid forced two-column control layouts on wave-19 touchpoint pages.
- **Visual mapping integrity:** keep wave-19 touchpoint slug mappings readable (`pii_redactor`, `env_file_diff`, `cron_overlap_checker`, `test_data_generator`, `password_policy_checker`, `iso8601_duration`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home controls, Roadmap filters/AI triage action, and wave-19 form actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 19 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 19 QA handoff guidance

- Run Wave 19 checks in `docs/release-checklist.md` before release.
- Record Wave 19 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-19 updates.

## Phase 27 Wave 20 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, JSON Merge Patch, Column Aligner, SSH Config Validator, CSR Generator, CAA Record Builder, and Base62 Encoder/Decoder.
- **Mobile baseline (`<=720px`):** keep wave-20 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-20 controls single-column readable, and avoid forced two-column control layouts on wave-20 touchpoint pages.
- **Visual mapping integrity:** keep wave-20 touchpoint slug mappings readable (`json_merge_patch`, `column_aligner`, `ssh_config_validator`, `csr_generator`, `caa_record_builder`, `base62_tool`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home controls, Roadmap filters/AI triage action, and wave-20 form actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 20 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 20 QA handoff guidance

- Run Wave 20 checks in `docs/release-checklist.md` before release.
- Record Wave 20 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-20 updates.

## Phase 28 Wave 21 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Unified Diff Generator, JWK/PEM Converter, Certificate Chain Validator, WSL Path Converter, Markdown Link Extractor, and Health Diagnostics.
- **Mobile baseline (`<=720px`):** keep wave-21 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-21 controls single-column readable, and avoid forced two-column form layouts on wave-21 touchpoint pages.
- **Visual mapping integrity:** keep wave-21 touchpoint slug mappings readable (`unified_diff_generator`, `jwk_pem_converter`, `cert_chain_validator`, `wsl_path_converter`, `markdown_link_extractor`, `health_diagnostics`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home controls, Roadmap filters/AI triage action, and wave-21 form/runbook actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 21 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 21 QA handoff guidance

- Run Wave 21 checks in `docs/release-checklist.md` before release.
- Record Wave 21 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-21 updates.

## Phase 29 Wave 22 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Docker Run to Compose, NATO Phonetic Converter, WiFi QR Code Generator, HMAC Generator, IPv6 ULA Generator, and Random MAC Address Generator.
- **Mobile baseline (`<=720px`):** keep wave-22 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-22 grouped controls single-column readable, and avoid forced two-column form layouts on wave-22 touchpoint pages.
- **Visual mapping integrity:** keep wave-22 touchpoint slug mappings readable (`docker_run_to_compose`, `nato_phonetic_converter`, `wifi_qr_generator`, `hmac_generator`, `ipv6_ula_generator`, `random_mac_generator`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home controls, Roadmap filters/AI triage action, and wave-22 form actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 22 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 22 QA handoff guidance

- Run Wave 22 checks in `docs/release-checklist.md` before release.
- Record Wave 22 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-22 updates.

## Phase 30 Wave 23 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, List Converter, Email Address Normalizer, IPv4 Address Format Converter, IPv4 Range Expander, Git Command Cheat Sheet, and BIP39 Mnemonic Generator/Validator.
- **Mobile baseline (`<=720px`):** keep wave-23 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-23 grouped controls single-column readable, and avoid forced two-column form layouts on wave-23 touchpoint pages.
- **Visual mapping integrity:** keep wave-23 touchpoint slug mappings readable (`list_converter`, `email_address_normalizer`, `ipv4_format_converter`, `ipv4_range_expander`, `git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home controls, Roadmap filters/AI triage action, and wave-23 form actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 23 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 23 QA handoff guidance

- Run Wave 23 checks in `docs/release-checklist.md` before release.
- Record Wave 23 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-23 updates.

## Phase 31 Wave 24 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile baseline (`<=720px`):** keep wave-24 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-24 grouped controls single-column readable, and avoid fixed two-column form layouts on wave-24 touchpoint pages.
- **Visual mapping integrity:** keep wave-24 touchpoint slug mappings readable (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home controls, Roadmap filters/AI triage action, and wave-24 form submit/generate/convert actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 24 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 24 QA handoff guidance

- Run Wave 24 checks in `docs/release-checklist.md` before release.
- Record Wave 24 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-24 updates.

## Phase 32 Wave 25 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile baseline (`<=720px`):** keep wave-25 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-25 grouped controls single-column readable, and avoid fixed two-column form layouts on wave-25 touchpoint pages.
- **Visual mapping integrity:** keep wave-25 touchpoint slug mappings readable (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact for Home controls, Roadmap filters/AI triage action, and wave-25 form submit/generate/convert actions, with neutral/blocking outcomes aligned to shared status/failure note semantics.
- **QA gate behavior:** treat Wave 25 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 25 QA handoff guidance

- Run Wave 25 checks in `docs/release-checklist.md` before release.
- Record Wave 25 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-25 updates.

## Phase 33 Wave 26 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile baseline (`<=720px`):** keep wave-26 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-26 grouped controls single-column readable with shared control headings, and avoid fixed two-column form layouts on wave-26 touchpoint pages.
- **Visual mapping integrity:** keep wave-26 touchpoint slug mappings readable (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact, and preserve explicit neutral/warning/success status semantics (`role="status"`/`role="alert"` + `aria-live`) for Home and Roadmap states plus wave-26 tool outcomes.
- **QA gate behavior:** treat Wave 26 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 26 QA handoff guidance

- Run Wave 26 checks in `docs/release-checklist.md` before release.
- Record Wave 26 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-26 updates.

## Phase 34 Wave 27 Standards (Shell, Mobile, Visual, A11y + QA Gates)

- **Shell consistency:** keep shared shell + baseline markers (`shell-ready`, `content-rendered`) stable on Home, Roadmap & Feedback, Git Command Cheat Sheet, BIP39 Mnemonic Generator/Validator, Lorem Ipsum Generator, and Text to Binary/Hex/Octal Converter.
- **Mobile baseline (`<=720px`):** keep wave-27 form panels and primary actions full-width/tap-friendly (`use_container_width=True`), keep wave-27 grouped controls single-column readable with shared control headings, and avoid fixed two-column form layouts on wave-27 touchpoint pages.
- **Visual mapping integrity:** keep wave-27 touchpoint slug mappings readable (`git_command_cheat_sheet`, `bip39_mnemonic_generator_validator`, `lorem_ipsum_generator`, `text_to_binary_hex_octal_converter`) before category defaults, with text badge fallback always readable.
- **Accessibility guardrail:** keep keyboard flow and visible focus rings intact, and preserve explicit neutral/warning/success status semantics (`role="status"`/`role="alert"` + `aria-live`) for Home and Roadmap states plus wave-27 tool outcomes.
- **QA gate behavior:** treat Wave 27 shell/mobile/visual/a11y regressions as release blockers unless an intentional exception is documented.

### Wave 27 QA handoff guidance

- Run Wave 27 checks in `docs/release-checklist.md` before release.
- Record Wave 27 outcomes in `docs/release-notes-template.md` using synthetic/sanitized evidence only.
- Keep non-tool exceptions explicit and confirm desktop/mobile readability after wave-27 updates.

## Maintenance Rules

- Do not duplicate tool titles, descriptions, paths, or accent colors outside `utils/ui.py`.
- Do not add a separate navigation library unless Streamlit page links no longer support the required behavior.
- Do not log or persist user-entered domains, URLs, logs, JWTs, JSON, or encoded text.
- Do not store roadmap feedback in Streamlit. New ideas should leave the app through GitHub Issues; curated defaults belong in `data/roadmap_seed.json`.
- Any new user-facing page should call `apply_app_shell` immediately after `st.set_page_config`.
- Health Diagnostics page content should remain runtime-safe only: no secrets, no user payload echoing, and no external sensitive probes.
- Any new preloader, spinner, skeleton, or transition styling must use the light blue/white work area and dark sidebar tokens. Avoid default gray loading surfaces.
- Any material change to the shell, home layout, or tool navigation should update this file and `docs/architecture.md` when boundaries change.
- For cross-page implementation follow-ups, use `docs/ui-consistency-audit-matrix-phase8.md` as the actionable baseline matrix for header/form/empty-state/action-label/notice consistency.

## Phase 4 Contributor Reliability Playbook

- Place **fragment** patterns (`st.fragment`) in shell/home UI hotspots (`app.py`, `utils/ui.py`) where quick interactions should rerun locally instead of rerunning the full app shell.
- Place **cache** patterns (`st.cache_data`) in read-only page data loaders/adapters with short TTLs and shared `utils/cache_policy.py` controls (TTL tiers, cache keys, test scope, freshness copy).
- Place **state** patterns (`st.session_state`) in page-level workflows for transient form/results state; never persist user-entered diagnostics content.
- Keep **dev baseline instrumentation** local-only (`ITOPS_DEV_BASELINE=1`) and limited to baseline surfaces (Home, Roadmap & Feedback, Domain Health Checker, DNS Record Checker, SSL Certificate Checker, HTTP Status Checker).
