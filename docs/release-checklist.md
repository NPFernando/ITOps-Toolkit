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

Use `docs/release-notes-template.md` to summarize the release, QA commands, privacy posture, known limitations, Wave 2/Wave 3/Wave 4/Wave 5/Wave 6/Wave 7/Wave 8/Wave 9/Wave 10/Wave 11/Wave 12/Wave 13/Wave 14/Wave 15/Wave 16/Wave 17 shell-mobile-visual-a11y outcomes, and the UX Quality Outcomes release reporting kit.

Minimum UX reporting before publish:
- Record one outcome each for navigation, readability/layout, task completion confidence, and public-safe behavior.
- Keep wording concise and public-safe.
- Use only synthetic/sanitized QA evidence (no customer data or secrets).

For incident triage and diagnostics interpretation during or after rollout, see `docs/ops-runbook.md`.
