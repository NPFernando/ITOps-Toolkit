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
  - Home navigation mode switch: Quick access (personalized sections) and All tools (full catalog).
  - Quick access sections may include Your Favorites, Recently Used (or Popular to Start), Shared Favorites, and New & Noteworthy.
  - All tools mode supports search + profession filtering + sort controls.
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
  - Primary top-level links are Home and Roadmap & Feedback, followed by grouped tool links.
  - Quick-search input and grouped navigation should keep strong contrast and clear spacing so scanning still works in long tool lists.
  - Active navigation state uses the blue gradient treatment.
  - Keep Streamlit's collapse and expand controls visible; hide native page navigation and deploy/tool chrome without hiding `stExpandSidebarButton`.
  - Add new tools by extending the `TOOLS` metadata in `utils/ui.py`.
  - Keep the command palette (`Ctrl/Cmd+K`) aligned with the same `TOOLS` metadata and page-link navigation behavior.
- Tool cards:
  - Use the central tool title, description, icon text, accent color, and Streamlit page link.
  - Show category metadata inside each card for faster visual scanning on the home grid.
  - Buttons should navigate through Streamlit page links.
- Page headers:
  - Use `render_page_header` instead of page-local `st.title` and `st.caption` combinations.
  - Keep the small uppercase overline (`<category> Tool`) above the title to reinforce page context.
  - Header illustrations are optional and category-driven; keep them low-clutter and decorative so titles/descriptions remain primary.
  - Use the warning parameter for sensitive-data reminders.
- Tool page panels:
  - Wrap the primary input workflow in `tool_form_panel` and introduce it with `render_form_intro`.
  - Use `render_empty_state` before first submission so blank pages explain what will appear; optional generated illustrations should remain secondary.
  - Use `render_section_heading` for results, headers, recommendations, and downloads; maintain eyebrow + heading + optional description hierarchy.
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
- Generated assets:
  - Runtime visual hooks are centralized in `utils/ui.py`:
    - `HOME_HERO_ILLUSTRATION`
    - `TOOL_CARD_ICON_ASSETS`
    - `TOOL_HEADER_ILLUSTRATION_BY_CATEGORY`
    - `EMPTY_STATE_ILLUSTRATIONS`
    - `ROADMAP_BADGE_ICONS`
  - Use exported outputs under `docs/assets/icons/exported/` and `docs/assets/illustrations/exported/` for runtime/documentation visuals.
  - Keep editable originals under `docs/assets/*/source` and regenerate exports instead of editing exported files directly.

## Generated Visuals Policy

- Generated SVGs are enhancement-only UI media; they must never be required for tool execution, validation, or results.
- Keep visual mappings semantic by context (network/security/data/etc.) and source all runtime mappings from `utils/ui.py`, not page-local constants.
- Prefer lightweight SVG exports for runtime hooks; reserve posters for documentation/release surfaces.
- Every generated visual used in runtime must have a graceful fallback path.

## Decorative vs Semantic Usage

- Runtime UI-generated images (hero, card icons, page-header illustrations, empty-state illustrations, roadmap badge icons) are decorative and rendered with empty alt plus `aria-hidden`/presentation semantics.
- Meaningful user-facing text (tool titles, category labels, status words like Planned/In Progress/Complete, source labels like Seed/GitHub) must remain in adjacent text, not only in imagery.
- Documentation images may be semantic; in docs, provide concise alt text when an image carries meaning.

## Fallback Rules

- Asset load boundary: `_svg_data_uri` returns `None` when an SVG is missing or invalid path/extension; callers must degrade safely.
- Home hero: falls back to the built-in CSS hero visual when the generated hero SVG is unavailable.
- Tool cards: fall back to text icon abbreviations from `ToolMeta.icon` when mapped SVGs are unavailable.
- Page headers and empty states: omit the illustration slot when no mapped SVG resolves; keep title/description primary.
- Roadmap badges: fall back to compact text glyphs when SVG badges are unavailable.

## Responsive Rules

- The sidebar remains Streamlit-native so users can collapse it on narrow screens.
- Home hero content stacks naturally on mobile.
- Generated hero visual reduces minimum height at smaller breakpoints (`<=1100px`, `<=720px`) to keep above-the-fold content readable.
- Touch targets for pills/buttons should stay at least ~2.3rem tall so filter/sort controls remain usable on phones.
- Quick-access and All-tools sections should wrap naturally; avoid fixed card widths that break mixed sections (favorites/recents/shared/new).
- Feature strips collapse from five columns to two columns and then one column.
- Tool cards should not rely on fixed text widths; long labels must wrap cleanly.
- Tool-page action buttons (submit/download) should wrap label text and expand full-width on narrow screens.
- Tool page headers with illustrations switch from side-by-side to stacked layout on narrow screens; illustration width becomes full-width below mobile breakpoint.
- Roadmap columns may scroll vertically on desktop, then stack naturally on narrow screens.

## Accessibility Rules

- Keep visible `:focus-visible` styles across links, buttons, and form controls in the shared shell CSS.
- Prefer semantic notice containers (`role="note"`) for shared warning/info blocks (home notice, roadmap notices).
- Preserve keyboard accessibility for sidebar quick search, pills (mode/filter/sort), and command palette triggers.
- Keep roadmap card/body text sizes readable after styling changes; avoid shrinking below body-readable sizes.

## Maintenance Rules

- Do not duplicate tool titles, descriptions, paths, or accent colors outside `utils/ui.py`.
- Do not add a separate navigation library unless Streamlit page links no longer support the required behavior.
- Do not log or persist user-entered domains, URLs, logs, JWTs, JSON, or encoded text.
- Do not store roadmap feedback in Streamlit. New ideas should leave the app through GitHub Issues; curated defaults belong in `data/roadmap_seed.json`.
- Any new user-facing page should call `apply_app_shell` immediately after `st.set_page_config`.
- Any new preloader, spinner, skeleton, or transition styling must use the light blue/white work area and dark sidebar tokens. Avoid default gray loading surfaces.
- Any material change to the shell, home layout, or tool navigation should update this file and `docs/architecture.md` when boundaries change.
