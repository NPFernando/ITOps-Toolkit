# Release Notes

## ITOps Toolkit UI and reliability readiness

### User-facing improvements

- Added first-run guidance and quick-start troubleshooting workflows.
- Added profession, category, search, navigation, sorting, and reset controls
  to Home discovery.
- Search results now prioritize exact and title matches before broader
  description matches.
- Improved shared empty, status, warning, failure, accessibility, and mobile
  interaction patterns across the tool catalog.

### Reliability and privacy

- HTTP checks now expose structured, public-safe failure metadata for
  operators and tests: error code, failure mode, attempt count, and retryable
  state.
- Sanitized upstream exception details and closed response bodies in network
  adapters.
- Added catalog, alias, guided-workflow, and representative cross-page
  regression contracts.

### Release and operations

- Added repeatable release evidence and dependency consistency checks.
- Added operator deployment, smoke-test, rollback, and dependency-maintenance
  guidance.
- Production sign-off still requires authenticated live smoke validation after
  merge; unauthenticated redirects are not treated as proof of UI health.
