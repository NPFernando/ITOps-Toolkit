# GPT Visual Generation Spec (Clean-Enterprise)

This spec defines the default prompt, review, and export process for GPT-generated visuals used in `docs/assets/`.

## 1) Reusable Prompt Templates

Use this base style prefix in every prompt:

`Clean enterprise product illustration style, modern SaaS, minimal composition, calm confidence, high contrast, soft depth, crisp edges, no visual noise, white or very light neutral background, brand-safe blue/teal accents, readable at small sizes.`

### A. Icons (tool/workflow symbols)

Template:

`{base style}. Create a single {subject} icon for {context}. Vector-like flat style, 1:1 composition, centered, clear silhouette, 2–3 accent colors max, no text, no gradients unless extremely subtle.`

Example:

`Clean enterprise product illustration style... Create a single DNS lookup icon for ITOps diagnostics. Vector-like flat style, 1:1 composition, centered, clear silhouette, 2–3 accent colors max, no text.`

### B. Hero visuals

Template:

`{base style}. Create a 16:9 hero visual for {theme}. Include one dominant focal concept and 2–4 supporting elements showing flow, reliability, and clarity. Keep large negative space for overlay text. No embedded words.`

### C. Roadmap badges

Template:

`{base style}. Create a compact badge-style visual for roadmap item {item}. Shape-first design, strong semantic metaphor, 1:1 ratio, no text, high legibility at 24px and 32px.`

### D. Tool-header illustrations

Template:

`{base style}. Create a horizontal tool-header illustration for {tool_name}. 16:9 crop-safe composition, one central workflow metaphor, light background, low clutter, no tiny details, no text.`

### E. Empty-state illustrations

Template:

`{base style}. Create an empty-state illustration for {screen/purpose}. Communicate "ready to start" with a positive neutral tone, single clear action metaphor, sparse composition, no text.`

### F. Posters

Template:

`{base style}. Create a poster-style visual for {campaign/use_case}. Cinematic but clean enterprise tone, high-clarity focal subject, subtle depth layers, 16:9 or 4:5 layout, no logos, no text.`

## 2) Negative Prompt Set (append to all prompts)

`No watermark, no signature, no logo, no brand names, no text, no letters, no UI screenshot style, no photoreal humans, no hands with artifacts, no clutter, no busy background, no heavy gradients, no low contrast, no blur, no compression artifacts, no noisy textures, no distorted geometry, no duplicate objects, no cropped focal object.`

## 3) Acceptance Checklist

Asset is accepted only if all pass:

- Readability: concept remains clear at target display size (icons at 24px; badges at 24px/32px).
- Contrast: focal shape separation is strong on light backgrounds.
- Semantic clarity: visual metaphor matches intended tool/feature meaning.
- No clutter: composition has clear hierarchy and sufficient negative space.
- No watermark-like artifacts: no hidden text, gibberish marks, ghost logos, or signature traces.

## 4) Naming + Versioning Rules (aligned to docs/assets)

Use existing naming pattern:

`<type>-<context>-<subject>-<variant>-<w>x<h>-v<NN>.<ext>`

- `type`: keep existing allowed values: `icon`, `illustration`, `poster`
- Map new asset classes:
  - hero visuals → `illustration-...-hero-...`
  - roadmap badges → `icon-roadmap-...`
  - tool-header illustrations → `illustration-tool-...-header-...`
  - empty-state illustrations → `illustration-empty-state-...`
- `vNN` starts at `v01`; increment on any pixel/path/composition change.
- Place editable masters in `source/`, delivery assets in `exported/`.

## 5) Export + Optimization Rules

- Icons:
  - Primary: SVG (`icons/exported/`)
  - Optional PNG: 24x24, 32x32 for raster-only surfaces
  - Target size: SVG lean; PNG <= 50 KB
- Hero/tool-header/empty-state illustrations:
  - Primary: WebP (`illustrations/exported/`), quality 75–85
  - PNG fallback for transparency-critical usage
  - Target size: <= 350 KB each
- Posters:
  - Primary: WebP (`posters/exported/`), quality 75–85
  - PNG fallback, JPG only for broad compatibility
  - Target size: <= 600 KB
- Preserve target dimensions from `docs/assets/README.md`.

## 6) Quality Review Workflow (Human Gate Required)

1. Generate 3–5 candidates per asset prompt.
2. Discard candidates failing negative-prompt constraints.
3. Run acceptance checklist.
4. Export best candidate(s) to `source/` and `exported/` with compliant names.
5. **Human gate (required):** reviewer validates semantic fit, readability at intended size, and artifact-free output.
6. Integrate into docs/app only after reviewer approval.

Minimum reviewer note format (in PR description or comment):

`Reviewed by: <name> | Asset: <filename> | Checks: readability/contrast/semantic/no-clutter/no-artifacts = pass`
