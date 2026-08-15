# Generated Assets Strategy

This directory is the single source of truth for generated visual assets used by the app and documentation.

## Starter Pack Index

For the initial generated icon/poster pack and recommended placement, see:

- `docs/assets/INDEX.md`

## Directory Layout

```text
docs/assets/
  icons/
    source/      # Editable masters (SVG/Figma exports)
    exported/    # App-ready optimized assets
  posters/
    source/      # Editable poster masters
    exported/    # Final PNG/WebP/JPG outputs
  illustrations/
    source/      # Editable vector/raster masters
    exported/    # App/docs-ready optimized outputs
```

## Naming Convention

Use lowercase kebab-case and semantic prefixes:

`<type>-<context>-<subject>-<variant>-<w>x<h>-v<NN>.<ext>`

Examples:
- `icon-tool-dns-outline-24x24-v01.svg`
- `poster-release-v1-landscape-2400x1350-v02.webp`
- `illustration-home-hero-light-1600x900-v01.webp`

Rules:
- `type` must be one of: `icon`, `poster`, `illustration`
- Include dimensions in exported filenames
- Increment version when pixels/paths change
- Never use spaces, uppercase, or ambiguous names like `final2`

## Source vs Exported Formats

- `source/`: editable masters only (`.svg`, `.fig`, `.ai`, `.psd`)
- `exported/`: delivery-ready assets only
  - Icons: prefer `.svg`; use `.png` only when raster is required
  - Posters: `.webp` primary, `.png` fallback, `.jpg` for broad compatibility
  - Illustrations: `.webp` primary, `.png` fallback; `.svg` if fully vector-safe

Do not hand-edit exported files as source of truth; regenerate from `source/`.

## Target Dimensions and Aspect Ratios

- Icons:
  - 16x16, 20x20, 24x24 (1:1)
  - Optional high-density PNG: 32x32, 48x48
- Posters:
  - Social/preview landscape: 2400x1350 (16:9)
  - Doc cover portrait: 1080x1350 (4:5)
  - Slide/announcement: 1920x1080 (16:9)
- Illustrations:
  - App hero/supporting artwork: 1600x900 (16:9)
  - Inline doc illustration: 1200x675 (16:9)
  - Square callout art: 1200x1200 (1:1)

## Optimization Rules

- Icons (SVG):
  - Remove editor metadata
  - Flatten transforms when safe
  - Keep viewBox; avoid hardcoded fill unless required
- Raster exports:
  - Prefer WebP quality 75–85 for posters/illustrations
  - Use PNG only for transparency-critical assets
  - Keep exported file sizes practical:
    - Icons PNG: <= 50 KB
    - Illustrations: <= 350 KB
    - Posters: <= 600 KB

## Placement Map (App + Docs)

- `icons/exported/`
  - App UI symbols (tool visuals, future compact UI glyphs)
  - Docs callouts and capability badges
- `posters/exported/`
  - Release notes visuals and documentation banners
  - README/community announcement media
- `illustrations/exported/`
  - App home/feature explanatory artwork
  - Architecture or workflow support images in `docs/`

Keep runtime app usage limited to optimized assets from `exported/`.

## Quality and Accessibility Constraints

- Provide meaningful alt text for every non-decorative image used in docs/app.
- Ensure icon and text contrast meets WCAG AA where applicable.
- Avoid embedding tiny unreadable text inside posters/illustrations.
- Keep visual style consistent with `docs/design-system.md` (color direction and tone).
- Do not include customer data, logs, tokens, or internal hostnames in generated imagery.
