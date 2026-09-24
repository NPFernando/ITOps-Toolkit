# Release Operations Handoff

This is the operator-facing release checklist for ITOps Toolkit. Use
synthetic or public-safe inputs only. Never include credentials, tokens,
private keys, customer data, or copied production logs in evidence.

## Before release

1. Confirm the working tree is clean and the intended commit is based on the
   current `origin/main`.
2. Run `make release-evidence`.
3. Run the full suite with `.venv/bin/python -m pytest -q`.
4. Review `docs/ui-ux-audit-inventory.json` for new parse errors, direct
   notices, or unexpected pattern gaps.
5. Review dependency health with `make dependency-check`.

## Deployment monitoring

After the deployment starts, monitor:

- App startup and authentication redirect behavior.
- Dependency/import errors in the deployment logs.
- External lookup failures, timeouts, rate limits, and provider outages.
- Streamlit exceptions triggered by Home filters, tool forms, downloads, or
  sidebar interactions.
- Readability of warning, empty, and failure states on desktop and mobile.
- Structured adapter metadata such as `error_code`, `failure_mode`,
  `attempts`, and `retryable` when reviewing sanitized diagnostics.

Do not treat a successful unauthenticated redirect as proof that the toolkit
UI is healthy. Production closeout requires an authenticated browser session.

## Authenticated smoke checklist

Record only pass/fail status and sanitized notes:

- Home renders after login.
- Search, profession, category, navigation, and reset controls work.
- A representative network/security tool succeeds with synthetic input.
- A representative text/data tool succeeds with synthetic input.
- A no-result or validation-error state is readable and actionable.
- Sidebar search and at least one related-tool handoff work.
- No user input is persisted or exposed in the evidence.

## Failure and rollback

If startup errors, repeated tool failures, broken navigation, or unsafe copy
appears:

1. Stop the release closeout and record the sanitized symptom.
2. Keep production status blocked.
3. Compare the deployed commit with the last known-good commit.
4. Revert or redeploy using the hosting platform's normal rollback process.
5. Re-run the local release gates before attempting deployment again.

## Maintainer communication

Use `docs/pr-188-maintainer-handoff.md` for the review checklist and
`docs/release-notes.md` for the concise change summary. Keep production
evidence sanitized and record only pass/fail status plus actionable notes.
