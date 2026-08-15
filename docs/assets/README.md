# Generated Assets Strategy

This directory is the source of truth for generated visual assets used by runtime UI hooks and documentation media.

## Runtime mappings (phase2)

Defined in `utils/ui.py`:

- `HOME_HERO_ILLUSTRATION` → home hero visual
- `TOOL_CARD_ICON_ASSETS` → selected tool-card icon mappings by tool slug
- `TOOL_HEADER_ILLUSTRATION_BY_CATEGORY` → tool header illustration by category
- `EMPTY_STATE_ILLUSTRATIONS` → empty-state illustration variants (`ready`, `network`, `security`)
- `ROADMAP_BADGE_ICONS` → roadmap status/source badges

If a mapped SVG is missing, runtime uses graceful fallbacks (CSS hero, text icon/badge fallback, or no illustration slot).

## Directory layout

```text
docs/assets/
  icons/
    source/      # Editable masters
    exported/    # Runtime/docs SVG badge + icon assets
  posters/
    source/      # Editable poster masters
    exported/    # Docs/release poster exports
  illustrations/
    source/      # Editable illustration masters
    exported/    # Runtime/docs illustration exports
```

## Usage guidance

- Runtime UI should reference exported files only via `utils/ui.py` constants.
- Treat runtime visuals as decorative enhancements; do not depend on them for core meaning or workflows.
- Keep semantic text in UI copy (titles, statuses, source labels), not only in imagery.
- In documentation, use concise alt text when an image carries meaning.

## Authoring rules

- Naming: `<type>-<context>-<subject>-<variant>-<w>x<h>-v<NN>.<ext>`
- Keep editable originals in `source/`; do not hand-edit `exported/` outputs.
- Current runtime hooks expect SVG files.
- For full inventory and placement guidance, use `docs/assets/INDEX.md`.
