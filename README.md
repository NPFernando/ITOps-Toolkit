# ITOps Toolkit

[![QA](https://github.com/NPFernando/ITOps-Toolkit/actions/workflows/qa.yml/badge.svg)](https://github.com/NPFernando/ITOps-Toolkit/actions/workflows/qa.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b)
![Status](https://img.shields.io/badge/status-public--safe-brightgreen)
![Data](https://img.shields.io/badge/data-no%20persistent%20storage-success)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Free public tools for IT admins, automation engineers, MSP engineers, and DevOps users.

ITOps Toolkit is a public-safe Streamlit dashboard for common troubleshooting tasks. It does not require login, does not use a database, and does not permanently store user-entered domains, logs, JSON, JWTs, or encoded text.

## Features

- Domain Health Checker with DNS, SSL, HTTP, DNSSEC, SPF/DMARC posture, MTA-STS, TLS-RPT, recommendations, CSV, Markdown, and standalone HTML exports.
- DNS Record Checker for A, AAAA, MX, TXT, NS, CNAME, SOA, SPF, and DMARC records.
- SSL Certificate Checker with subject, issuer, SANs, validity dates, and expiration status.
- HTTP Status Checker with redirects, response time, selected headers, and security recommendations.
- JSON Formatter with validation, formatting, minifying, and download support.
- Base64 encoder and decoder.
- JWT Decoder that reads header and payload without verifying or sending the token externally.
- Cron Explainer for common 5-field cron expressions.
- Log Troubleshooting Assistant with rule-based, public-safe analysis and optional Azure AI summaries.
- Roadmap & Feedback board with curated seed items, live public GitHub Issues, planned work, completed work, and static AI recommendations.

## Local Setup

Use Python 3.11 or newer.

### Makefile workflow

```bash
make setup
make run
```

Then open the local Streamlit URL shown in the terminal. By default, `make run` starts Streamlit on port `8502`. Override it when needed:

```bash
make run PORT=8503
```

Useful local commands:

```bash
make help       # list available commands
make qa         # compile Python files and run tests
make test       # run pytest only
make clean      # remove local Python caches
```

### Manual workflow

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

For local development and tests, install the dev requirements after activating the virtual environment:

```bash
pip install -r requirements-dev.txt
```

## How to Run

With the Makefile:

```bash
make run
```

Or manually after activating the virtual environment:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

Local Streamlit file watching is disabled in `.streamlit/config.toml` for stability on WSL-mounted Windows drives. Restart the Streamlit command after editing files.

## Local Secrets

The app does not require secrets for normal rule-based operation. Optional Azure AI summaries for the Log Troubleshooting Assistant require a local-only Streamlit secrets file:

```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Then set values in `.streamlit/secrets.toml`. That file is ignored by git and must not be committed.

The example includes placeholders for direct OpenAI and Azure AI Foundry/Azure OpenAI configuration:

- `OPENAI_API_KEY`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_VERSION`

Only Azure AI Foundry/Azure OpenAI is wired today. Direct `OPENAI_API_KEY` support is reserved and does not enable AI summaries. Azure AI summaries are opt-in per Log Troubleshooting submission and send only sanitized log text to the configured Azure OpenAI deployment.

Optional public links:

- `ITOPS_GITHUB_URL` overrides the default repository URL used by the GitHub button, Roadmap & Feedback issue links, and read-only public GitHub Issues feed. It is not a secret.

For setup and manual validation steps, see [docs/azure-ai-setup.md](docs/azure-ai-setup.md).

## Tests

With the Makefile:

```bash
make qa
```

Or manually:

```bash
python -m compileall app.py pages utils
python -m pytest
```

The pytest suite uses fakes for DNS, HTTP, TLS, GitHub Issues, and Azure/OpenAI adapter tests. It does not require external network access, browser automation, secrets, or OpenAI credentials.

## Deployment Notes

This app is ready for Streamlit Community Cloud:

1. Push the project to a public or private GitHub repository.
2. Create a new Streamlit Community Cloud app.
3. Set the main file path to `app.py`.
4. Optionally set `ITOPS_GITHUB_URL` if deploying a fork and directing feedback to a different repository.
5. Do not add secrets unless optional Azure AI summaries are needed. See [docs/azure-ai-setup.md](docs/azure-ai-setup.md) for the required keys and smoke checks.

No database or background worker is required. Roadmap feedback reads public GitHub Issues anonymously. Azure OpenAI is optional and used only when configured and explicitly enabled on a log-analysis submission.

## Release Readiness

Before deployment, use [docs/release-checklist.md](docs/release-checklist.md). For release summaries, use [docs/release-notes-template.md](docs/release-notes-template.md).

## UI Design Notes

The dashboard shell, tool metadata, navigation, and reusable visual components live in `utils/ui.py`. Future UI changes should follow `docs/design-system.md`.

## Roadmap Feedback

The Roadmap & Feedback page merges curated seed data from `data/roadmap_seed.json` with public GitHub Issues from the configured repository. User ideas are submitted through GitHub Issues; Streamlit does not store or write feedback.

Maintainer labels:

- `enhancement`: include the issue as a feature request.
- `status:in-progress` or `in progress`: show an open issue in the In Progress column.
- `status:complete` or `complete`: show an open issue in the Complete column. Closed issues also show as Complete.
- Optional category labels can match `Tools`, `Reports`, `Security`, `AI Ideas`, `UX / Design`, or `Integrations`; otherwise the issue form's Category field is used.

## Security Notes

- Do not paste passwords, private keys, production tokens, API keys, or sensitive customer data.
- User input is processed in memory only.
- Download exports are generated in memory only.
- The app does not intentionally log user input.
- `.streamlit/secrets.toml`, `.env`, and `.env.*` are ignored by git.
- JWTs are decoded locally without signature verification and are not sent externally.
- The log assistant uses rule-based analysis by default and sends sanitized logs to Azure OpenAI only when Azure settings are configured and the user opts in for that submission.

## Screenshots

Use [docs/screenshot-guide.md](docs/screenshot-guide.md) for release QA capture targets. Save temporary screenshots outside the repository, such as `/tmp/itops-screenshots`.

## Future Roadmap

The in-app Roadmap & Feedback page is the source of truth for public planned items, completed items, live GitHub feature requests, and curated AI recommendations. Feedback submission opens GitHub Issues and does not store ideas in Streamlit.

- Add uptime and latency trend visualization for one-off checks without persistence.
