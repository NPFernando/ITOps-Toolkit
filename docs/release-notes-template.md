# Release Notes Template

Use this template for deployment notes, GitHub releases, or pull request summaries.

## Summary

- Release:
- Date:
- Deployment target: Streamlit Community Cloud
- Main file: `app.py`
- Optional visual header: `docs/assets/posters/exported/poster-toolkit-trust-shield-hero-portrait-1080x1350-v01.svg`
- QA baseline: Phase 9 wave-2 shell/mobile/visual/a11y checks completed
- QA baseline add-on: Phase 10 wave-3 shell/mobile/visual/a11y QA gates completed

## User-Facing Changes

- 

## Security And Privacy Notes

- No login or database is required.
- User input is processed in memory only.
- Do not paste passwords, private keys, production tokens, API keys, or sensitive customer data.
- Optional Azure AI summaries are opt-in per Log Troubleshooting submission.
- Azure AI receives sanitized logs only when configured and explicitly enabled.

## QA Commands

```bash
.venv/bin/python -m compileall app.py pages utils
.venv/bin/python -m pytest
.venv/bin/streamlit run app.py --server.headless true --server.port 8502
curl http://localhost:8502/_stcore/health
```

## Manual QA Completed

- Home desktop:
- Home mobile:
- Sidebar navigation:
- Tool-card navigation:
- Domain Health Checker empty form:
- DNS Record Checker:
- JSON Formatter or Log Troubleshooting Assistant:
- Phase 8 consistency baseline (`docs/ui-consistency-audit-matrix-phase8.md`) spot check:
- Visual mapping fallback spot check (home/tool/roadmap):
- Wave 2 shell/navigation spot check (sidebar/search/command palette):
- Wave 2 mobile spot check (`<=720px`, no clipping/overflow):
- Wave 2 accessibility spot check (keyboard/focus/notice semantics):
- Wave 3 shell clarity spot check (text-first cues/actions still clear):
- Wave 3 mobile cue readability spot check (`<=720px`, no badge/chip clipping):
- Wave 3 visual mapping spot check (weak-cue slug-specific icon priority + fallback):
- Wave 3 accessibility spot check (decorative SVG semantics + keyboard/focus):
- Log Troubleshooting AI unavailable state:
- Optional Azure AI state, if secrets were available:

## UX Quality Outcomes (Release Reporting Kit)

Capture a short, public-safe outcome summary for each release.

| Area | Outcome | Evidence |
| --- | --- | --- |
| Navigation and wayfinding |  | e.g., Sidebar and tool-card routes open correctly |
| Readability and layout |  | e.g., No clipped text/controls on desktop + mobile |
| Task completion confidence |  | e.g., Forms and diagnostics render without errors |
| Public-safe behavior |  | e.g., No secrets shown; fallback notes stay safe |

Notes:
- Keep this section concise (4-8 bullets max across outcomes/notes).
- Reference synthetic or sanitized QA inputs only.
- Do not include customer domains, logs, tokens, keys, or screenshots with sensitive data.

## Known Limitations

- Browser screenshot QA is manual/local and not part of CI.
- Direct `OPENAI_API_KEY` support is reserved and not wired.
- Azure AI summaries require API-key configuration and per-submission opt-in.
- The toolkit does not persist historical checks or trends.

## Deployment Notes

- Streamlit app entrypoint is `app.py`.
- Add Streamlit Cloud secrets only if optional Azure AI summaries are needed.
- Do not commit `.streamlit/secrets.toml`, `.env`, QA screenshots, or generated caches.
