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
- Roadmap & Feedback: board cards, search, filters, roadmap columns, public-safe warning, and GitHub issue links render cleanly.
- Domain Health Checker: empty form renders without exceptions.
- DNS Record Checker: form renders and does not show Streamlit form warnings.
- JSON Formatter or Log Troubleshooting Assistant: text-heavy layout has no clipped controls.
- Mobile viewport: no overlapping text, clipped labels, cramped buttons, or horizontal scroll.

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

Use `docs/screenshot-guide.md` for required captures. Save temporary QA screenshots outside the repo, such as `/tmp/itops-screenshots`.

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

Use `docs/release-notes-template.md` to summarize the release, QA commands, privacy posture, and known limitations.
