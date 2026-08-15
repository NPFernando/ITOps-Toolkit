# Streamlit Alignment & Performance Audit (Phase 3)

Date: 2026-08-15  
Scope: architecture-level audit and recommendations only (no broad refactors)

## Baseline

- App stack pins `streamlit==1.61.1` (`requirements.txt`).
- Multipage app uses `app.py` + `pages/` directory with custom shell navigation (`utils/ui.py`).
- Native sidebar navigation is disabled (`.streamlit/config.toml`: `client.showSidebarNavigation = false`).

## 1) Current repository usage

### Caching

- `@st.cache_data` appears only in `pages/10_Roadmap_Feedback.py`:
  - `_cached_roadmap_board(..., ttl=300)` for merged seed + GitHub roadmap reads.
  - `_cached_triage_summary(..., ttl=3600)` for optional AI triage summarization.
- No `@st.cache_resource` usage.
- Most network-heavy tools (DNS/HTTP/SSL/CVE/WHOIS-style lookups) are uncached and recompute each submit.

### Rerun model

- The codebase is strongly form-driven (`st.form` used across most tool pages), which aligns with Streamlit guidance to batch reruns until submit.
- Explicit `st.rerun()` is used in targeted UX paths only (favorites reordering/toggle and home “show/hide tools” flow), primarily in `app.py` and `utils/ui.py`.
- Pages preserve result visibility across unrelated reruns by storing post-submit output in session state (intentional pattern, documented in page comments and `utils/ui.py::run_validated_lookup`).

### Session State

- Heavy, deliberate use of `st.session_state` across tool pages for:
  - persisted form results,
  - validation/error state,
  - UX toggles and page behavior.
- Query-param + localStorage mirror pattern in `utils/ui.py` persists recents/favorites/share links without server persistence.

### Navigation

- Current model:
  - `pages/` directory routing,
  - custom grouped sidebar rendered by `apply_app_shell`,
  - `st.page_link` for navigation links (with fallback handling).
- `st.navigation` / `st.Page` are not currently used.

### Large-data rendering

- Rendering is mostly `st.dataframe(..., width="stretch", hide_index=True)` on live-check outputs.
- `utils/ui.py::display_rows_frame` normalizes mixed values for consistent display.
- `st.table` is used mostly for static/smaller reference outputs.
- Highest volume page (`28_Bulk_Domain_Health.py`) is intentionally capped (`MAX_DOMAINS_PER_BATCH = 25`), limiting true large-data pressure.

## 2) Alignment vs latest Streamlit recommendations

Reference docs used:

- Caching overview: <https://docs.streamlit.io/develop/concepts/architecture/caching>
- Session State: <https://docs.streamlit.io/develop/concepts/architecture/session-state>
- Fragments: <https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment>
- Multipage overview (`st.navigation` preference): <https://docs.streamlit.io/develop/concepts/multipage-apps/overview>
- `st.navigation` API: <https://docs.streamlit.io/develop/api-reference/navigation/st.navigation>

| Area | Current state | Recommendation alignment |
|---|---|---|
| Caching | Minimal (`Roadmap` page only) | **Partial**: correct usage where present, underused elsewhere |
| Rerun control | Strong `st.form` usage + selective reruns | **Strong** |
| Session state | Widespread explicit persistence patterns | **Strong** |
| Fragments | Selective home-grid use (`render_fragment` around high-card-count sections + fragment-scoped rerun for favorite interactions) | **Partial** |
| Navigation | `pages/` + `st.page_link` custom shell | **Partial** (valid pattern; modern preferred path is `st.navigation`) |
| Data rendering | Mostly moderate-sized tables; no major virtualization strategy needed yet | **Adequate for current scale** |

## 3) Adopt-now vs defer decisions

## Adopt now

1. **Add TTL-based `@st.cache_data` to repeated read-heavy lookups that are safe to reuse briefly**  
   - Targets: CVE lookup, selected DNS/HTTP reference lookups, roadmap-adjacent read APIs.  
   - Why now: low code churn, immediate latency wins, reduced repeated external calls.  
   - Risk: stale results if TTL too long (mitigate with short TTLs and clear UI wording).

2. **Document cache policy per lookup type (freshness vs speed)**  
   - Why now: reduces future inconsistency and accidental stale-data regressions.  
   - Risk: low.

3. **Standardize session-state key conventions for result/error payloads**  
   - Why now: already mostly consistent; small cleanup improves maintainability for 100+ pages.  
   - Risk: low if done incrementally.

## Defer

1. **Migration from `pages/` routing to full `st.navigation`/`st.Page` router**
   - Rationale: current shell uses custom grouped links/search/favorites/query-param behavior tightly coupled to existing pattern.
   - Risk if done now: medium-high (URL behavior, tests, link sharing, sidebar UX regression).

2. **Broad fragmentization (`@st.fragment`) of shell/page components**
   - Rationale: fragments help when partial reruns are hot spots, but most pages are submit-driven and already manageable.
   - Risk if done now: medium (cross-container side effects, duplicated state complexity).

3. **Advanced large-table patterns (pagination/lazy query backends)**
   - Rationale: current row counts are intentionally bounded; limited immediate ROI.
   - Risk if done now: unnecessary complexity.

## 4) Prioritized technical opportunities (for this codebase)

1. **High priority / low risk:** expand `st.cache_data` with short TTLs for expensive read-only lookups.
2. **High priority / low risk:** add a short “cache freshness” note pattern to affected pages.
3. **Medium priority / low risk:** tighten session-state key naming conventions into a small helper contract.
4. **Medium priority / medium risk:** continue incremental fragment rollout only where profiling shows repeat UI churn and low cross-state coupling.
5. **Lower priority / higher risk:** evaluate `st.navigation` migration only after a dedicated compatibility spike (URL stability, shared favorites, tests).

## Risk summary

- **Primary near-term risk:** stale cached external results if TTLs are not scoped carefully.
- **Primary deferred risk:** navigation migration can regress URL semantics and custom shell behavior.
- **Current posture:** stable and aligned for a form-first diagnostics app; biggest practical gain is targeted caching expansion, not major framework-level rewrites.

## Phase 3 performance playbook (placement)

- **Fragments (`st.fragment`)**: apply to shell/home interaction hotspots (`app.py`, `utils/ui.py`) where partial reruns avoid full-shell reruns.
- **Caching (`st.cache_data`)**: apply to read-only data loaders/merge helpers with short TTL and explicit freshness messaging.
- **State (`st.session_state`)**: apply to page-level form/result UX state only; keep values session-local and non-persistent.
- **Dev baseline instrumentation**: dev-only, local opt-in via `ITOPS_DEV_BASELINE=1`; current baseline surfaces are Home, Roadmap & Feedback, Domain Health Checker, DNS Record Checker, SSL Certificate Checker, and HTTP Status Checker.
