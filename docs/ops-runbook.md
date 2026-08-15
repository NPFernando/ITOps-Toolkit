# Operations Runbook

This runbook is for maintainers operating ITOps Toolkit releases.

## 1. Health Diagnostics Interpretation

Use `Health Diagnostics` (`pages/128_Health_Diagnostics.py`) as the first operational checkpoint.
The page now includes a **Runbook guidance** panel with a public-safe link back to this runbook (`docs/ops-runbook.md`).

- **Pass**: safe to continue release checks.
- **Warn**: optional integrations or non-critical configuration gaps.
- **Fail**: resolve before release.

Priority checks:
1. Configured GitHub repo
2. Roadmap seed parse
3. Cache probe
4. Adapter capabilities

## 2. Incident Triage Sequence

1. Identify the affected surface (Domain Health, DNS, SSL, HTTP, Roadmap, AI summary).
2. Classify failure mode:
   - `input_invalid`
   - `timeout`
   - `connectivity`
   - `upstream_unavailable`
   - `upstream_response_invalid`
   - `policy_blocked`
   - `internal_error`
3. Confirm user-facing error message stays sanitized and actionable.
4. Reproduce with local deterministic tests first (no live-network assumptions).

## 3. Reliability Troubleshooting Paths

### External adapter issues

- Validate timeout/retry defaults against `docs/reliability-contract.md`.
- Check for retry exhaustion messaging on adapters and pages.
- Confirm no secret values are surfaced in diagnostics or error text.

### Cache behavior issues

- Review `utils/cache_policy.py` usage and cache key composition.
- Confirm stale/freshness messaging appears on cached surfaces.
- Use test-isolated cache scopes in pytest scenarios.

### Streamlit behavior issues

- Check `docs/streamlit-performance-audit.md` for current pin and compatibility decisions.
- Verify rerun-sensitive paths with targeted page tests.

## 4. Release Commands

Fast release confidence gate:

```bash
make release-gates
```

Full release gate:

```bash
make qa
```

## 5. Escalation Rule

If a failure cannot be reproduced deterministically with local tests, treat it as environment-specific, capture sanitized context only, and avoid broad speculative fixes.
