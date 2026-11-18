# Block Cave art v3 — independent QA

Date: 2026-11-18  
Reviewer: independent QA agent; no art implementation edits  
Verdict: **PASS with nonblocking presentation findings** for the art prototypes.

## Scope

Reviewed the revised `pickaxe_scatter.svg`/`.png`, `generate_templates.py`,
`export_png.mjs`, the new `cave_background_3d.png`, both retained fallback
background files, `preview.html`, `preview-mini.png`, `preview-desktop.png`,
and `README.md`. Checks ran against isolated temporary copies; the files in
`art/templates/` were read only.

## Technical checks

- `pickaxe_scatter.svg` parses as SVG XML, has a title, 64×64 logical viewBox
  and 512×512 export dimensions, and contains no external image/script. The
  512×512 PNG has a transparent outer corner. Visually it has the requested
  broad turquoise horizontal pixel pickaxe head and brown diagonal handle.
- `cave_background_3d.png` opens as 1672×941. Its sampled corners and center
  are opaque. The 400×225 and 1200×675 preview files have the stated sizes.
- The targeted command `python generate_templates.py pickaxe_scatter.svg`
  succeeded in a temporary copy. The resulting pickaxe SVG matched the
  checked-in source byte-for-byte. Hashes and modification times of
  `cave_background.svg`, `cave_background.png`, `cave_background_3d.png`,
  `cave_explorer.svg`, and a sentinel file were unchanged. The generator's
  selected-file filter is at `generate_templates.py:283-291` and rejects
  unknown names before writing.
- A separate isolated **full generator** run left all input/output file
  contents byte-identical, including the fallback SVG/PNG and the 3D PNG.
  It rewrites its own SVG outputs, so their modification times can change.
- The PNG exporter ran successfully in a separate temporary copy. It wrote
  the expected 15 SVG-derived PNGs and three previews, and did not change the
  separate 3D background. The fallback `cave_background.png` export remained
  byte-identical to the checked-in file. All three previews were
  **pixel-identical** to the checked-in previews. The full contact sheet
  `preview.png` differed as a PNG byte stream despite identical pixels,
  so screenshot byte hashes are not a suitable acceptance criterion here.
- `preview.html:44,50` uses the new 3D PNG for both embed-size examples. The
  fallback SVG/PNG remain separate assets. `export_png.mjs` only writes PNGs
  derived from the 15 SVG names plus three preview PNGs; it has no output
  path for `cave_background_3d.png`.

## Visual check

- The background is a warmer, deep block cave with rock formations,
  torchlight, crystals and visible lava. The dark 6×5 board panel keeps all
  30 symbols readable over it at both preview sizes. No board symbol,
  pickaxe, side explorer or foreground frame is visibly clipped.
- The scatter's magenta square and turquoise horizontal head separate it
  clearly from cubic ores, gold, alloy and WILD. The requested pickaxe shape
  is recognizable at 400×225. The `SCATTER` letters at that size remain too
  small to carry the meaning alone, consistent with the README.
- At 1200×675 the photographic 3D cave and pixel-art symbols/explorer have a
  noticeable style difference. This is a visual choice to review in the
  eventual game UI, not a broken asset. The mini preview retains good board
  contrast despite the detailed cave behind it.

No blocking defect was found. This review does not test Pixi rendering,
animation, user-interface controls, or platform acceptance.
