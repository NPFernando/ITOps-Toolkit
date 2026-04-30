# ITOps Toolkit Design System

This guide documents the UI direction used for the Streamlit dashboard and tool pages.

## Visual Direction

- Use a close match to the reference dashboard: dark left navigation, light work area, blue ITOps branding, and restrained security/operations visuals.
- Keep the interface practical for IT admins, MSP engineers, automation engineers, and DevOps users. The UI should feel fast, trustworthy, and work-focused.
- Preserve public-safe messaging near inputs that may receive domains, URLs, logs, JWTs, JSON, or encoded text.

## Layout

- Use the shared shell from `utils/ui.py` for global CSS, sidebar navigation, tool metadata, page headers, cards, and notices.
- Home page structure:
  - Hero section with product title, short value statement, search input, trust chips, and the IT/security visual.
  - Popular tool cards for primary workflows.
  - Feature strip for reliability, privacy, public-safe use, open source status, and mobile support.
  - Important notice band for sensitive-data handling.
- Roadmap & Feedback page structure:
  - Header with public roadmap context, Roadmap/Feedback tabs, and GitHub actions.
  - Board summary cards for public categories across seed and GitHub issue items.
  - Search and category filters above four roadmap columns: Planned, In Progress, Complete, and AI Recommended.
  - Seed vote-style numbers are curated display values; GitHub issue numbers use public reaction totals.
- Tool pages use a compact page header and keep the form-first workflow visible above results.
- Native Streamlit multipage navigation is disabled with `client.showSidebarNavigation = false`; use the shared sidebar shell instead.
- Streamlit native theme tokens in `.streamlit/config.toml` must stay aligned with the shared shell. They control the first loading frame before `utils/ui.py` CSS is injected, including sidebar color, app background, and toolbar visibility.
- Cards use an 8px radius, subtle borders, and no nested cards.

## Color And Typography

- Primary blue: `#126bff`.
- Dark sidebar: `#071a33` to `#061429`.
- Text ink: `#07142f`.
- Muted text: `#52637f`.
- Border line: `#d7e2f5`.
- Accent colors:
  - DNS/public-safe green: `#23b84d`.
  - SSL/JWT purple: `#7047e8`.
  - HTTP/open-source orange: `#ff6b13`.
  - JSON teal: `#11aab8`.
- Typography uses Manrope through the shared CSS. Keep letter spacing at `0`.

## Components

- Sidebar:
  - Brand block, navigation, safety card, and about card are required.
  - Active navigation state uses the blue gradient treatment.
  - Keep Streamlit's collapse and expand controls visible; hide native page navigation and deploy/tool chrome without hiding `stExpandSidebarButton`.
  - Add new tools by extending the `TOOLS` metadata in `utils/ui.py`.
- Tool cards:
  - Use the central tool title, description, icon text, accent color, and Streamlit page link.
  - Buttons should navigate through Streamlit page links.
- Page headers:
  - Use `render_page_header` instead of page-local `st.title` and `st.caption` combinations.
  - Use the warning parameter for sensitive-data reminders.
- Tool page panels:
  - Wrap the primary input workflow in `tool_form_panel` and introduce it with `render_form_intro`.
  - Use `render_empty_state` before first submission so blank pages explain what will appear.
  - Use `render_section_heading` for results, headers, recommendations, and downloads.
  - Use `tool_result_panel` and `tool_download_panel` for framed result and export areas.
  - Use `display_rows_frame` for mixed field/value result tables before passing them to `st.dataframe`.
  - Use `render_status_note` for compact success, info, warning, neutral, or optional AI state messages.
- Notices:
  - Use `render_important_notice` for the home-page sensitive-data message.
- Roadmap board:
  - Use `utils/roadmap.py` for seed loading, GitHub issue normalization, category counts, filtering, and GitHub feedback URLs.
  - Use `utils/github_issues.py` for read-only anonymous GitHub Issues API calls.
  - Label curated AI suggestions as static recommendations based on the toolkit direction. Do not call Azure/OpenAI from the roadmap page.
  - Keep feedback public-safe copy visible near submit links.
  - Show GitHub issue source badges and links for live public requests; show seed badges for curated local items.

## Responsive Rules

- The sidebar remains Streamlit-native so users can collapse it on narrow screens.
- Home hero content stacks naturally on mobile.
- Feature strips collapse from five columns to two columns and then one column.
- Tool cards should not rely on fixed text widths; long labels must wrap cleanly.
- Roadmap columns may scroll vertically on desktop, then stack naturally on narrow screens.

## Maintenance Rules

- Do not duplicate tool titles, descriptions, paths, or accent colors outside `utils/ui.py`.
- Do not add a separate navigation library unless Streamlit page links no longer support the required behavior.
- Do not log or persist user-entered domains, URLs, logs, JWTs, JSON, or encoded text.
- Do not store roadmap feedback in Streamlit. New ideas should leave the app through GitHub Issues; curated defaults belong in `data/roadmap_seed.json`.
- Any new user-facing page should call `apply_app_shell` immediately after `st.set_page_config`.
- Any new preloader, spinner, skeleton, or transition styling must use the light blue/white work area and dark sidebar tokens. Avoid default gray loading surfaces.
- Any material change to the shell, home layout, or tool navigation should update this file and `docs/architecture.md` when boundaries change.
