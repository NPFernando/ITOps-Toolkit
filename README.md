# ITOps Toolkit

Free public tools for IT admins, automation engineers, MSP engineers, and DevOps users.

ITOps Toolkit is a public-safe Streamlit dashboard for common troubleshooting tasks. It does not require login, does not use a database, and does not permanently store user-entered domains, logs, JSON, JWTs, or encoded text.

## Features

- Domain Health Checker with DNS, SSL, HTTP, email security, recommendations, CSV export, and Markdown export.
- DNS Record Checker for A, AAAA, MX, TXT, NS, CNAME, SOA, SPF, and DMARC records.
- SSL Certificate Checker with subject, issuer, SANs, validity dates, and expiration status.
- HTTP Status Checker with redirects, response time, selected headers, and security recommendations.
- JSON Formatter with validation, formatting, minifying, and download support.
- Base64 encoder and decoder.
- JWT Decoder that reads header and payload without verifying or sending the token externally.
- Cron Explainer for common 5-field cron expressions.
- Log Troubleshooting Assistant with rule-based, public-safe analysis and optional Azure AI summaries.

## Local Setup

Use Python 3.11 or newer.

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

For setup and manual validation steps, see [docs/azure-ai-setup.md](docs/azure-ai-setup.md).

## Tests

```bash
python -m compileall app.py pages utils
python -m pytest
```

The pytest suite uses fakes for DNS, HTTP, and TLS adapter tests. It does not require external network access, browser automation, secrets, or OpenAI credentials.

## Deployment Notes

This app is ready for Streamlit Community Cloud:

1. Push the project to a public or private GitHub repository.
2. Create a new Streamlit Community Cloud app.
3. Set the main file path to `app.py`.
4. Do not add secrets unless optional Azure AI summaries are needed. See [docs/azure-ai-setup.md](docs/azure-ai-setup.md) for the required keys and smoke checks.

No database or background worker is required. Azure OpenAI is optional and used only when configured and explicitly enabled on a log-analysis submission.

## UI Design Notes

The dashboard shell, tool metadata, navigation, and reusable visual components live in `utils/ui.py`. Future UI changes should follow `docs/design-system.md`.

## Security Notes

- Do not paste passwords, private keys, production tokens, API keys, or sensitive customer data.
- User input is processed in memory only.
- Download exports are generated in memory only.
- The app does not intentionally log user input.
- `.streamlit/secrets.toml`, `.env`, and `.env.*` are ignored by git.
- JWTs are decoded locally without signature verification and are not sent externally.
- The log assistant uses rule-based analysis by default and sends sanitized logs to Azure OpenAI only when Azure settings are configured and the user opts in for that submission.

## Screenshot Placeholders

Add screenshots after deployment:

- Home page
- Domain Health Checker
- DNS Record Checker
- Log Troubleshooting Assistant

## Future Roadmap

- Add downloadable HTML reports.
- Add more DNS and email security checks.
- Add uptime and latency trend visualization for one-off checks without persistence.
