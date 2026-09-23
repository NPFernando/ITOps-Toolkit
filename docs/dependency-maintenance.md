# Dependency and Security Maintenance

This note records the dependency review boundary for ITOps Toolkit. The
application intentionally avoids speculative upgrades: a newer package is
only adopted after compatibility tests, lint, dependency consistency checks,
and the repository's CI security checks pass.

## Current policy

- Keep direct runtime dependencies declared in `requirements.txt`.
- Keep development and CI tooling in `requirements-dev.txt`.
- Run `make dependency-check` before release; it covers `pip check` and Ruff.
- Run the full test matrix in `.github/workflows/qa.yml` for Python 3.11 and
  3.12 before merging dependency changes.
- Treat Socket Security results and any future vulnerability scanner findings
  as release evidence, not as a reason to upgrade blindly.
- Do not copy secrets, tokens, private keys, or user payloads into issue,
  release, or test evidence.

## Review record

The current environment reports newer versions for several transitive and
direct packages, including Streamlit, OpenAI, Plotly, Starlette,
Cryptography, PyJWT, and SQLparse. These are review candidates only; no
version was changed in this maintenance pass because each requires a
compatibility decision and focused regression run.

The current Streamlit compatibility decision is documented in
`docs/streamlit-performance-audit.md`. The pinned runtime remains
`streamlit==1.61.0`.

## Upgrade procedure

1. Select one bounded package update or compatible update group.
2. Review release notes and security impact.
3. Update the direct requirement intentionally.
4. Run `make dependency-check`, focused affected tests, and the full suite.
5. Confirm both Python CI matrix jobs and Socket Security checks pass.
6. Record the resulting pin and any compatibility exception in this document.

## Current follow-up

The current release keeps the existing runtime pins, including
`streamlit==1.61.0`, because no dependency upgrade is required to close the
validated UI and reliability scope. Re-run `make dependency-check` before
each release and review upstream advisories separately; do not convert an
available-version report into an upgrade without compatibility tests and a
documented reason.
