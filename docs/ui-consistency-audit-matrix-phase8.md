# UI Consistency Audit Matrix (Phase 8)

Date: 2026-08-15  
Scope: Final Phase 8 cross-page baseline for release QA, with documented intentional exceptions.

## Representative Matrix

| Page | Category | Header | Form intro | Action label | Empty state | Notices | Section headings | Concrete gap(s) |
|---|---|---|---|---|---|---|---|---|
| `pages/1_Domain_Health_Checker.py` | Network diagnostics | `render_page_header` | `render_form_intro` | `Run health check` | `render_empty_state` | Warning + status notes | `render_section_heading` | Baseline reference implementation. |
| `pages/31_Security_Headers_Checker.py` | Security checker | `render_page_header` | `render_form_intro` | `Check headers` | `render_empty_state` | Direct `st.error` for failures | `render_section_heading` | Failure/validation UX bypasses shared failure/status note components. |
| `pages/52_SQL_Formatter.py` | Data formatter | `render_page_header` | `render_form_intro` | No submit (live formatting) | None | Neutral status note used | `render_section_heading` | No explicit pre-result empty state guidance; live-update behavior differs from most tools. |
| `pages/103_JWT_Claims_Reference.py` | Reference/search | `render_page_header` | `render_form_intro` | No submit (search-as-you-type) | Uses `st.info` | None | `render_section_heading` | Empty state pattern not using shared `render_empty_state`. |
| `pages/128_Health_Diagnostics.py` | Operations diagnostics | `render_page_header` | None | N/A | N/A | Mostly captions/tables | `render_section_heading` | Static diagnostic page intentionally skips form intro/empty-state pattern; should be documented as exception. |
| `pages/10_Roadmap_Feedback.py` | Product roadmap | Custom hero (no `render_page_header`) | None | `Submit idea` link + optional AI button | Column-level custom empty state | Shared + custom notices | Uses `render_section_heading` for AI section | Intentional custom layout, but should stay documented as a non-tool-page exception. |

## Repo-wide Spot Findings (practical, not exhaustive)

1. **Action label drift:** submit labels are highly fragmented (for example: `Run`, `Process`, `Build header`, `Look up`, `Check headers`, `Generate token`), making primary actions less predictable across tools.
2. **Empty-state inconsistency:** several reference/lookup pages still use ad-hoc `st.info` or no pre-result state instead of `render_empty_state`.
3. **Notice style inconsistency:** some pages use shared status/failure notes, while others render raw `st.error`/`st.warning` for equivalent states.
4. **Pattern exceptions exist but are valid:** Roadmap and Health Diagnostics are not standard “single form → single result” tools and should be treated as documented exceptions, not regressions.

## Actionable Consistency Rules for Follow-on Tasks

Use these rules when touching pages:

1. **Header rule:** Tool pages must use `render_page_header`; non-tool pages may use custom hero only if the exception is intentional and documented.
2. **Form intro rule:** Any page with user input should include `render_form_intro` directly above the primary workflow.
3. **Action label rule:** Use verb-first labels with clear object. Prefer a constrained set by intent:  
   - Checks/lookups: `Run check` / `Look up`  
   - Builders/generators: `Generate` / `Build`  
   - Converters/formatters: `Convert` / `Format`  
   - Validators/scanners: `Validate` / `Scan`
4. **Empty-state rule:** If a result section is conditional, show `render_empty_state` before first submission/query unless the page is intentionally always-populated.
5. **Notice rule:** Prefer shared note components (`render_status_note`, `render_failure_note`) over direct `st.error`/`st.warning` where equivalent semantics exist.
6. **Section-heading rule:** Result areas should consistently use `render_section_heading` with meaningful eyebrow values (`Results`, `Actions`, `Downloads`, `Optional`, etc.).

## Phase 8 Release Sign-off Usage

Use this matrix as a quick release gate:

1. Confirm no touched tool page regresses shared shell patterns (header/form/empty-state/section headings/notice semantics).
2. Confirm action labels remain intent-consistent and verb-first.
3. Confirm mobile checks (`<=720px`) for one page per category pass without clipping/overlap.
4. Confirm non-tool exceptions (`Roadmap & Feedback`, `Health Diagnostics`) stay intentionally documented and readable.

## Follow-on Backlog (small, high-value)

1. Normalize primary submit labels for check-style tools to a consistent “Run check”/“Look up” convention.
2. Replace ad-hoc info empty states on reference pages with `render_empty_state`.
3. Migrate direct error/warning blocks on checker pages to shared status/failure note helpers where appropriate.
4. Keep `Roadmap & Feedback` and `Health Diagnostics` listed in docs as intentional pattern exceptions.

## Wave 2 Documentation Sync Note (Phase 9)

- Wave 2 release docs now explicitly gate shell integrity, mobile (`<=720px`) behavior, visual fallback readability, and accessibility checks in `docs/design-system.md`, `docs/release-checklist.md`, and `docs/release-notes-template.md`.
- This matrix remains the cross-page consistency baseline; Wave 2 extends release QA emphasis rather than replacing Phase 8 rules.

## Wave 3 Documentation Sync Note (Phase 10)

- Wave 3 release docs now extend shell/mobile/visual/a11y gates with text-first cue clarity and weak-cue slug-specific visual mapping checks.
- This matrix remains the Phase 8 baseline; Wave 3 adds stricter QA evidence requirements without changing the core consistency rules.

## Wave 4 Documentation Sync Note (Phase 11)

- Wave 4 release docs now extend shell/mobile/visual/a11y gates for new wave-4 icon mappings and related tool cues, including shell consistency and accessibility spot checks.
- This matrix remains the Phase 8 baseline; Wave 4 adds release-playbook QA evidence requirements without changing core consistency rules.

## Wave 5 Documentation Sync Note (Phase 12)

- Wave 5 release docs now extend shell/mobile/visual/a11y gates for new wave-5 icon mappings and related tool cues, including shell consistency, mobile helper-text readability, and accessibility spot checks.
- This matrix remains the Phase 8 baseline; Wave 5 adds release-playbook QA evidence requirements without changing core consistency rules.

## Wave 6 Documentation Sync Note (Phase 13)

- Wave 6 release docs now extend shell/mobile/visual/a11y gates for new wave-6 icon mappings and related tool cues, including shell consistency, mobile helper-text readability, and accessibility spot checks.
- This matrix remains the Phase 8 baseline; Wave 6 adds release-playbook QA evidence requirements without changing core consistency rules.

## Wave 7 Documentation Sync Note (Phase 14)

- Wave 7 release docs now extend shell/mobile/visual/a11y gates for new wave-7 icon mappings and related tool cues, including shell consistency, mobile helper-text readability, and accessibility spot checks.
- This matrix remains the Phase 8 baseline; Wave 7 adds release-playbook QA evidence requirements without changing core consistency rules.

## Wave 8 Documentation Sync Note (Phase 15)

- Wave 8 release docs now extend shell/mobile/visual/a11y gates for new wave-8 icon mappings and related tool cues, including shell consistency, mobile helper-text readability, and accessibility spot checks.
- This matrix remains the Phase 8 baseline; Wave 8 adds release-playbook QA evidence requirements without changing core consistency rules.

## Wave 9 Documentation Sync Note (Phase 16)

- Wave 9 release docs now extend shell/mobile/visual/a11y gates for new wave-9 icon mappings and related tool cues, including shell consistency, mobile helper-text readability, and accessibility spot checks.
- This matrix remains the Phase 8 baseline; Wave 9 adds release-playbook QA evidence requirements without changing core consistency rules.

## Wave 10 Documentation Sync Note (Phase 17)

- Wave 10 release docs now extend shell/mobile/visual/a11y gates for wave-10 planned icon mappings plus shared shell baseline-marker coverage and status/failure-note semantics across touched pages.
- This matrix remains the Phase 8 baseline; Wave 10 adds release-playbook QA evidence requirements without changing core consistency rules.
