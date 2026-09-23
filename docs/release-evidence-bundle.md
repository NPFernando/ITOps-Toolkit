# Release Evidence Bundle

This document is the sanitized handoff record for the current ITOps Toolkit
release-readiness cycle. It contains no user-entered domains, URLs, logs,
tokens, credentials, or production payloads.

## Local implementation scope

- Home quick-start workflows for domain, TLS/security, auth, and incident/log
  troubleshooting.
- Home first-run guidance explaining the safe path from browsing to a result.
- Profession, category, search, and navigation-mode controls with one-click
  reset behavior.
- Search relevance ranking that prioritizes exact and title matches.
- Shared UI shell, notices, empty states, accessibility patterns, and
  responsive card behavior.
- Structured, public-safe HTTP failure metadata for retry and operator
  diagnostics.
- Maintainer handoff, release notes, dependency follow-up, and deployment
  communication guidance.

## Local validation

Run from the repository root:

```bash
.venv/bin/python -m pytest -q tests/test_app_page.py
.venv/bin/python -m pytest -q
```

The focused AppTest suite is the minimum gate for Home onboarding and discovery
changes. The full suite is required before release integration.

## UI inventory and release gates

```bash
make audit-ui
make release-gates
make release-evidence
make dependency-check
```

The generated inventory is stored at
`docs/ui-ux-audit-inventory.json`. Any new direct notice or page-local shell
pattern should be reviewed against `docs/design-system.md`.

`make release-evidence` is the repeatable combined gate for refreshing the
inventory, running release gates, and checking dependency/lint health before
branch integration. `docs/release-operations.md` contains the deployment
monitoring, authenticated smoke, and rollback checklist.

## Branch integration status

The validated release commits are published on
`release/itops-ui-release-readiness`, with pull request #188 open against
`main`. All Python 3.11/3.12 and Socket Security checks passed. The pull
request remains blocked only by the repository's required maintainer review;
automatic merge is disabled. The working tree for the release branch is clean.

After approval, merge PR #188 through the repository workflow and monitor the
deployment against the resulting commit. Do not bypass the review requirement
with an administrator merge.

## Production verification blocker

Authenticated production verification is still pending. The live Streamlit
deployment redirects unauthenticated requests to its login flow from this
environment. A redirect is not evidence that the deployed toolkit UI works.

Closeout requires a logged-in browser session and a sanitized smoke result
covering:

1. Home renders after authentication.
2. Search, profession, category, and reset controls work.
3. One representative network/security tool accepts synthetic input and
   renders a result.
4. One text/data tool renders a result without persisting the input.
5. Empty/error states remain readable and actionable.
6. No sensitive data is entered or recorded.

Until that checklist is completed, production status remains **blocked**.

## Maintenance references

- `docs/dependency-maintenance.md` records the dependency review and upgrade
  procedure.
- `docs/streamlit-performance-audit.md` records the current Streamlit pin and
  performance decisions.
