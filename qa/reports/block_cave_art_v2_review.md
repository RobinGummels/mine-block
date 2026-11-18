# Block Cave art v2 — independent QA

Date: 2026-11-18  
Reviewer: independent QA agent; no art implementation edits  
Verdict: **PASS with nonblocking visual findings** for editable prototypes.

## Scope and evidence

Reviewed `art/templates/README.md`, `generate_templates.py`, `export_png.mjs`,
all 15 SVG/PNG asset pairs, `preview.html`, `preview-mini.png` (400×225),
`preview-desktop.png` (1200×675), and the contact sheet. This is an art-source
review, not a Pixi, math, platform-approval, or legal clearance test.

- Independently parsed all **15 SVGs** with Python `xml.etree.ElementTree`.
  Each has the SVG namespace and a title; no external `href`, embedded image,
  `script`, or `foreignObject` was found. The 13 symbol sources have 64×64
  logical viewBoxes and 512×512 exports; the background is 480×270 to
  1920×1080; the retained explorer is 512×768.
- Independently opened all **15 PNGs** with Pillow. Every size matches its
  export contract; the top-left alpha is 0 for symbols/explorer and 255 for
  the opaque cave background. Both isolated preview PNG sizes match their
  names. This checks the exported pixel alpha, not every pixel's alpha.
- Ran `generate_templates.py` in a temporary directory containing a copy of
  the generator and the retained explorer. Its **14 generated SVGs** match the
  originals byte-for-byte. A sentinel file and `cave_explorer.svg` remained
  unchanged. Source inspection shows writes only to the 11 defined symbols,
  two wild alternatives, and `cave_background.svg`; it does not delete files.
- Ran `export_png.mjs` in a separate temporary directory with copies of the
  15 SVGs and preview HTML. It exited 0, wrote exactly the expected **15 asset
  PNGs and three previews**, and all 18 PNGs matched the repository files
  byte-for-byte. Neither isolated run wrote to `art/templates/`.
- No `silver_ore` file or text reference remains in `art/templates/`. The
  README maps math ID `lapis` to art ID `lapis_ore`; both SVG and PNG exist.
  The rare alloy retains the `fantasy_alloy_ingot` asset ID while its visual
  changes to a block. Math/frontend must use that explicit mapping.

## Visual review

- **User-requested motifs present:** wet earth has a green grass top and muddy
  sides; timber has dark bark and a lighter cut top; the fantasy alloy is a
  dark cubic block with violet seams; copper/lapis/gold/emerald/diamond are
  embedded in separately textured stone cubes. The tunnel has converging
  geometry, torches and a lava pool below the board. The adult explorer has a
  helmet, beard, amber scarf and work clothes.
- At 400×225 and 1200×675, all 30 board symbols remain inside the preview
  area. The side explorer does not cover the board. The current cyan-cross
  WILD is distinguishable from the dark alloy and yellow gold by shape and
  bright cyan; the magenta square pickaxe SCATTER is distinct from all cubes.
  At desktop size the labels are visible. No clipping was seen in either
  isolated preview.
- The generic pixel cubes, tools and cave evoke the requested block-game
  genre, but no recognizable Minecraft logo, Steve likeness, or copied
  texture was apparent in the reviewed output. This visual inspection cannot
  establish legal IP clearance or platform approval.

## Nonblocking findings for production art/frontend

1. **Small-size labels:** WILD and SCATTER text is not reliably readable at
   400×225 (`preview-mini.png`; `README.md`, final paragraph). Preserve their
   distinct shapes and explain their meaning through rules, paytable and
   accessible text in the frontend. Verify on the real Pixi canvas.
2. **Alternative wild:** the violet-rune option is closer in color and cubic
   silhouette to the fantasy alloy than the current cyan-cross option
   (`preview.png`). Keep the cyan-cross default unless a small-size comparison
   demonstrates equal clarity.
3. **Integration ID:** `lapis` → `lapis_ore` is documented only in the art
   manifest. The final math/frontend asset map needs an explicit test for this
   translation; the art review alone does not prove integration.

No blocking art-source defect was found. The templates remain prototypes;
production export, controls, animation, color/contrast in the actual game,
and jurisdiction wording were outside this check.
