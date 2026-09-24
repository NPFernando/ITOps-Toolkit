# Contributor release playbook

Use the release branch workflow for changes that affect the public Streamlit
application. Direct pushes to `main` are not part of the supported process.

## Local preflight

```bash
make release-evidence
make pre-merge
```

For a complete confidence run, use:

```bash
make pre-release
```

## Pull request handoff

Include the user-visible change, affected tool pages, focused test command,
release-gate result, and any external-provider limitations. Do not describe an
unauthenticated redirect as production UI verification.

## Merge and deployment

After maintainer approval, merge the PR through repository controls. Confirm
the deployed revision, app startup, Home discovery, one network-backed tool,
one text/data tool, empty/error states, and safe-data guidance. If startup or
provider behavior regresses, stop validation and follow the rollback notes in
`docs/release-operations.md`.
