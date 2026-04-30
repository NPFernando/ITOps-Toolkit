# Screenshot Guide

Use this guide for local release QA screenshots. Screenshots are temporary QA artifacts and should be saved outside the repository, for example `/tmp/itops-screenshots`.

## Storage

Create a temporary screenshot directory:

```bash
mkdir -p /tmp/itops-screenshots
```

Do not save screenshots under the project directory unless a future release explicitly adds tracked documentation images.

## Required Captures

Capture these views before release:

- Home desktop: `1440x1000`.
- Home mobile: `390x900`.
- DNS Record Checker: `1280x900`.
- Domain Health Checker empty form: `1280x900`.
- Log Troubleshooting Assistant with Azure unavailable state: `1280x900`.
- Roadmap & Feedback desktop: `1440x1000`.
- Roadmap & Feedback mobile: `390x900`.

Optional captures when local Azure secrets are available:

- Log Troubleshooting Assistant with Azure available state.
- Log Troubleshooting Assistant after an unchecked submit.
- Log Troubleshooting Assistant after a checked submit with a synthetic sanitized log.

## Visual Acceptance

Home page:

- Dark sidebar and light workspace are visible before and after app load.
- Hero, search input, trust chips, tool cards, feature strip, and notice match the shared design system.
- No native Streamlit navigation list or deploy toolbar appears.

Tool pages:

- Shared page header, form panel, empty state, and result panel are consistent.
- Form labels and buttons are not clipped.
- Text-heavy pages have no horizontal scroll or overlapping content.

Roadmap & Feedback:

- Board summary cards, search, filters, four columns, and submit-idea links are visible.
- GitHub feedback links open outside Streamlit, live public issue cards link back to GitHub, and no in-app persistence UI is implied.
- If GitHub is unavailable or rate-limited, the seed-only fallback note is subdued and does not look like a failure.
- Static AI Recommended items are clearly labeled as curated recommendations, not live AI output.

Log Troubleshooting Assistant:

- Azure unavailable state is clear when secrets are missing.
- Azure available state says summaries are optional and sanitized.
- Skipped and error AI states do not look like full-page failures when rule-based results succeeded.
- Optional AI summary panel uses the shared light-blue status note treatment.

Mobile:

- Sidebar can collapse cleanly.
- Search, cards, forms, checkboxes, buttons, and status notes remain readable.
- No text overlaps or extends outside its container.

## Manual Capture Notes

If using Playwright locally, keep outputs in `/tmp/itops-screenshots`. Browser automation is not part of CI because local WSL browser dependencies can vary by machine.

For Azure AI screenshots, use synthetic sanitized logs only:

```text
2026-04-30T10:15:00Z ERROR certificate verify failed for https://example.internal
2026-04-30T10:15:01Z WARN upstream returned status 502
```

Never include real customer logs, secrets, tokens, keys, or internal hostnames in screenshots.
