# Release Notes Template

Use this template for deployment notes, GitHub releases, or pull request summaries.

## Summary

- Release:
- Date:
- Deployment target: Streamlit Community Cloud
- Main file: `app.py`

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
- Log Troubleshooting AI unavailable state:
- Optional Azure AI state, if secrets were available:

## Known Limitations

- Browser screenshot QA is manual/local and not part of CI.
- Direct `OPENAI_API_KEY` support is reserved and not wired.
- Azure AI summaries require API-key configuration and per-submission opt-in.
- The toolkit does not persist historical checks or trends.

## Deployment Notes

- Streamlit app entrypoint is `app.py`.
- Add Streamlit Cloud secrets only if optional Azure AI summaries are needed.
- Do not commit `.streamlit/secrets.toml`, `.env`, QA screenshots, or generated caches.
