# Azure AI Foundry Setup And QA

This app can generate optional Azure AI summaries on the Log Troubleshooting Assistant page. Rule-based analysis remains the default. The app sends sanitized logs to Azure OpenAI only when Azure settings are configured and the user checks the AI summary opt-in for that submission.

## Required Azure Values

Set these values in local Streamlit secrets or Streamlit Community Cloud secrets:

- `AZURE_OPENAI_API_KEY`: API key for the Azure AI Foundry / Azure OpenAI resource.
- `AZURE_OPENAI_ENDPOINT`: Resource endpoint, for example `https://<resource-name>.openai.azure.com` or `https://<resource-name>.services.ai.azure.com`.
- `AZURE_OPENAI_DEPLOYMENT`: Model deployment name from Azure AI Foundry.

These values are present but not active behavior switches:

- `AZURE_OPENAI_API_VERSION`: Optional and reserved for compatibility. The current v1 Responses API path does not require dated `api-version` parameters.
- `OPENAI_API_KEY`: Reserved for future direct OpenAI support. Direct OpenAI API calls are not enabled in this app.

## Local Setup

Copy the placeholder secrets file:

```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Use placeholder-free values in `.streamlit/secrets.toml`:

```toml
# Optional direct OpenAI placeholder. Not used by the app today.
OPENAI_API_KEY = ""

# Azure AI Foundry / Azure OpenAI settings for optional log summaries.
AZURE_OPENAI_API_KEY = "replace-with-your-azure-key"
AZURE_OPENAI_ENDPOINT = "https://replace-with-resource-name.openai.azure.com"
AZURE_OPENAI_DEPLOYMENT = "replace-with-deployment-name"
AZURE_OPENAI_API_VERSION = ""
```

Never commit `.streamlit/secrets.toml`. It is ignored by git and should stay local-only.

## Endpoint Rules

The app accepts either resource endpoint shape:

- `https://<resource-name>.openai.azure.com`
- `https://<resource-name>.services.ai.azure.com`

The app normalizes the endpoint to the Azure v1 Responses API base URL by appending `/openai/v1/` when needed. Supplying an endpoint that already ends in `/openai/v1/` is also supported.

Microsoft's current Azure OpenAI Responses API examples use the `OpenAI` Python client, an Azure `/openai/v1/` base URL, and `client.responses.create(...)`. The API version lifecycle docs also state that the v1 GA API no longer requires dated `api-version` parameters.

Sources:

- [Use the Azure OpenAI Responses API](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/chatgpt-quickstart)
- [Azure OpenAI in Microsoft Foundry Models v1 API](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/api-version-lifecycle)

## Streamlit Cloud Setup

In Streamlit Community Cloud:

1. Open the app settings.
2. Add secrets using the same TOML keys from the local setup section.
3. Save secrets and restart or redeploy the app.
4. Do not add `.streamlit/secrets.toml` to the repository.

## Manual Local QA

Run the app:

```bash
.venv/bin/streamlit run app.py --server.port 8502
```

Check the app health:

```bash
curl http://localhost:8502/_stcore/health
```

Expected result: `ok`.

Without Azure secrets:

- Open the Log Troubleshooting Assistant page.
- Confirm the Azure AI checkbox is disabled.
- Submit a synthetic sanitized log sample.
- Confirm rule-based findings render and no AI summary is requested.

With real Azure secrets:

- Restart Streamlit after editing `.streamlit/secrets.toml`.
- Open the Log Troubleshooting Assistant page.
- Confirm the Azure AI checkbox is enabled.
- Submit once with the checkbox unchecked and confirm only rule-based findings render.
- Submit once with the checkbox checked and confirm the optional Azure AI summary renders.
- Use synthetic logs only, for example:

```text
2026-04-30T10:15:00Z ERROR certificate verify failed for https://example.internal
2026-04-30T10:15:01Z WARN upstream returned status 502
```

## Manual Deployment QA

After adding Streamlit Cloud secrets and redeploying:

- Confirm the app starts and the home page loads.
- Open the Log Troubleshooting Assistant page.
- Repeat the unchecked and checked log-summary tests using synthetic sanitized logs.
- Confirm provider errors show a safe fallback message without tracebacks or secret values.
- Confirm no user-entered logs, prompts, responses, or secrets are committed, logged, or persisted by the app.

## Troubleshooting

- Checkbox disabled: confirm all three required Azure values are set and non-empty.
- Provider error after opt-in: confirm the deployment name exactly matches the Azure model deployment name.
- Endpoint error: use the resource endpoint without extra paths, or provide the full `/openai/v1/` base URL.
- No summary text: retry with a shorter synthetic log sample and confirm the deployment supports the Responses API.
- Direct `OPENAI_API_KEY` does nothing: this is expected; direct OpenAI support is not wired.
