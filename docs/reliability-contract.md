# Reliability Contract

This contract defines default reliability behavior for external adapters and user-facing failure handling in ITOps Toolkit.

## 1) Timeout Defaults by Adapter Type

| Adapter type | Default timeout | Notes |
|---|---:|---|
| HTTP (`utils/http_tools.py`) | 10s | End-to-end request with redirects enabled |
| DNS (`utils/dns_tools.py`) | 3s per try, 5s resolver lifetime | Resolver-level timeout/lifetime budget |
| SSL/TLS (`utils/ssl_tools.py`) | 5s | TCP connect + TLS handshake/cert read |
| GitHub Issues (`utils/github_issues.py`) | 8s | Public API read-only issue fetch |
| AI (Azure OpenAI in `utils/ai_tools.py`) | 20s client timeout | Optional, opt-in only, sanitized input only |

## 2) Retry / Backoff Policy

Policy applies to network adapters only (HTTP/DNS/SSL/GitHub/AI):

- **Attempts:** 1 initial try + up to 2 retries (max 3 total)
- **Backoff:** bounded adapter-level linear backoff (`base_seconds * attempt`) using per-adapter constants (for example `0.2-0.5s` base values), capped by max attempts
- **Do not retry** validation/input errors and deterministic client errors
- **Retryable failure classes:**
  - Timeout (`socket.timeout`, DNS timeout, request timeout)
  - Transient connection/reset/refused failures
  - HTTP `429`, `500`, `502`, `503`, `504`
  - GitHub API transient 5xx/rate-limit windows
  - Azure/OpenAI transient transport/service unavailability

## 3) Error Taxonomy and User Message Conventions

All adapter responses should map errors to one of these classes:

- `input_invalid`: malformed or out-of-range user input
- `timeout`: remote service did not respond in budget
- `connectivity`: DNS/connect/reset/network path failure
- `upstream_unavailable`: upstream 5xx/rate-limit/service outage
- `upstream_response_invalid`: non-parseable or schema-invalid response
- `policy_blocked`: security/privacy rule blocked operation
- `internal_error`: unexpected exception

User-facing message rules:

1. Start with clear action context: `"DNS lookup timed out."`, `"GitHub issues are unavailable."`
2. Add safe next step (no secrets): `"Try again in a few seconds."`, `"Check network reachability."`
3. Never include tokens, raw headers, full stack traces, or user-submitted sensitive content.
4. Keep messages public-safe and concise; return technical detail only as sanitized category text.

## 4) Cache Policy Tiers, Stale Indicators, and Invalidation

- **Tier 0 (no cache):** security-sensitive or per-input diagnostics (HTTP/DNS/SSL checks, log analysis input/output)
- **Tier 1 (short TTL cache):** read-only public metadata where freshness matters (example: Roadmap board data, 5 min TTL)
- **Tier 2 (medium TTL cache):** derived summaries over public data (example: Roadmap AI triage summary, 1 hour TTL)

Stale indicators:

- Surface `last_refreshed_at` when cached data is shown
- Mark stale state explicitly (for example: `"Showing cached data"`) when age exceeds nominal refresh interval

Invalidation rules:

- TTL expiry invalidates automatically
- Manual refresh action must bypass cache and repopulate
- Any change to fetch parameters or source repository URL invalidates previous cache key
- Test suites must clear Streamlit cache state between scenarios (`st.cache_data.clear()`)
- Shared policy helper/constants and cache-key composition live in `utils/cache_policy.py` and should be reused for new user-facing cached surfaces

## 5) Logging and Privacy Boundaries for Failures (Public-Safe)

- Do not log or persist user-entered domains, URLs, logs, JWTs, JSON, encoded text, secrets, or tokens.
- Keep failure logs/telemetry to non-sensitive metadata only:
  - adapter type
  - error taxonomy class
  - coarse status/reason code
  - elapsed time bucket
- For AI flows, sanitize text before optional provider calls and never emit unsanitized payloads to logs.
- Exposed failure messages must remain public-safe and should not reveal infrastructure internals beyond minimal troubleshooting guidance.

## 6) Contributor Reliability Playbook (Phase 4)

When adding or changing reliability-sensitive behavior:

1. Reuse `utils/cache_policy.py` controls for new user-facing `st.cache_data` surfaces (tier TTLs, `compose_cache_key`, `runtime_cache_scope`, and freshness messages).
2. Keep Health Diagnostics (`pages/128_Health_Diagnostics.py`) aligned with runtime reality using non-sensitive checks only.
3. Keep docs synchronized in one pass: `README.md`, `docs/architecture.md`, `docs/design-system.md`, this contract, and `docs/streamlit-performance-audit.md`.
4. Validate with targeted tests (cache-policy and affected page tests) before release.

## Related Docs

- Architecture boundaries: `docs/architecture.md`
- Azure AI opt-in setup/privacy: `docs/azure-ai-setup.md`
- Release validation flow: `docs/release-checklist.md`
