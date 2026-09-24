# Production sign-off template

Copy this template into the release handoff after the pull request is merged.
Use synthetic, public-safe inputs only.

## Release identity

- Deployed commit:
- Deployment timestamp:
- Reviewer:
- PR:

## Authenticated smoke

- [ ] Home renders after login.
- [ ] Search, profession, category, navigation, and reset controls work.
- [ ] Representative network/security tool returns a readable result.
- [ ] Representative text/data tool returns a readable result.
- [ ] Empty, validation, and provider-error states are actionable.
- [ ] Sidebar and related-tool navigation work.
- [ ] No sensitive data was entered or captured.

## Operational checks

- [ ] Startup/import health is normal.
- [ ] Health Diagnostics shows no unexpected failures.
- [ ] Provider retry/rate-limit behavior is readable.
- [ ] Rollback commit and operator contact are known.

## Decision

- Status: `PASS` / `BLOCKED` / `ROLLBACK`
- Evidence location:
- Follow-up owner:
