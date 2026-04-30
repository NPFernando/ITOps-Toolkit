# AGENTS.md

## Quickstart
- Install: `python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt`
- Dev: `streamlit run app.py`
- Test: `python -m compileall app.py pages utils && python -m pytest`
- Lint/Format: no dedicated formatter is configured
- Build: Streamlit Community Cloud runs the app from `app.py`
- Env/config:
  - Required env vars: none
  - Optional env vars: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, and `AZURE_OPENAI_DEPLOYMENT` enable opt-in Azure AI log summaries; `AZURE_OPENAI_API_VERSION` and `OPENAI_API_KEY` are reserved compatibility placeholders; `ITOPS_GITHUB_URL` overrides public GitHub and feedback links
  - Local env file: do not commit `.env` or `.streamlit/secrets.toml`

## Structure
- Key modules/packages: Streamlit pages in `pages/`
- Shared code location: `utils/`
- Integrations/adapters location: DNS, SSL, and HTTP helpers in `utils/`
- Docs/diagrams location: `docs/` and `docs/diagrams/`

## Conventions
- No duplication: extract shared modules.
- Stable module entrypoints; avoid deep imports.
- DTO to domain mapping happens at boundaries only.
- Domain/Core must not import UI/Adapters.
- Do not log or persist user-entered domains, URLs, logs, JWTs, JSON, or encoded text.
- AI features must stay opt-in per submission, send sanitized text only, and use mocked adapters in automated tests.
- Roadmap and feedback ideas must stay public and backend-free: use `data/roadmap_seed.json` plus read-only public GitHub Issues, with no in-app persistence or AI calls.
- Roadmap GitHub tests must mock `utils/github_issues.py`; do not require live GitHub access in automated tests.
- Azure AI setup and manual QA guidance lives in `docs/azure-ai-setup.md`; keep it accurate when changing AI configuration behavior.
- UI pages must use the shared shell in `utils/ui.py` after `st.set_page_config`.
- Reuse the central tool metadata in `utils/ui.py`; do not duplicate tool titles, paths, icons, descriptions, or accent colors.
- Keep UI cards at 8px radius or less, avoid nested cards, and document new reusable UI patterns in `docs/design-system.md`.

## Testing
- Unit tests live in `tests/` and use `pytest`.
- Adapter tests must use monkeypatches/fakes; do not perform real DNS, HTTP, TLS, OpenAI, or secret-backed calls.
- Streamlit page smoke tests use `streamlit.testing.v1.AppTest` and must not submit forms that trigger external checks.
- Add regression tests for bug fixes.

## Docs
- Keep README accurate.
- Keep `docs/architecture.md` updated for behavior or architecture changes.
- Keep `docs/design-system.md` updated for shell, navigation, and visual system changes.
- Use `docs/release-checklist.md` as the standard pre-deploy checklist and keep release docs current when deployment or QA steps change.

## Definition of Done
- No new duplication introduced.
- Tests updated/added and executed where configured.
- Docs updated if behavior/architecture changed.
- Compile checks pass or exceptions are documented.
- Safe error handling for new external calls.
