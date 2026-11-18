# Block Cave art v5: independent symbol review

Date: 2026-11-18. Scope: the eleven current `art/templates/*_3d.png` board symbols, `preview.html`, `README.md`, and the three preview PNGs. This review did not edit art implementation files.

## Verdict

**PASS as prototype art. No blocking findings.** The 3D symbols match the agreed 6×5 block-cave direction, retain the symbol meanings from the SVG fallbacks, and remain distinguishable in both preview layouts.

## Visual findings

- Earth has wet grass over brown soil; stone has a visibly layered rock texture; timber has dark vertical bark and a bright cut top. All read as cubes.
- Copper, lapis, gold, emerald and diamond appear as differently colored and shaped inclusions within the same gray stone cube: broad orange plates, cobalt pools, small yellow cubes, tall green prisms and cyan kite crystals. This shared host stone and matching amber-left/cyan-right lighting make a consistent set. At 400×225 the ore colors remain distinguishable, though the fine inclusion shapes are less clear.
- The rare alloy reads as a near-black block with thin violet seams. It is distinct from plain stone and gold in the mini preview.
- Wild is a glowing cyan/violet four-arm junction; scatter is a cyan pickaxe on a magenta square. They are distinct from each other, from gold, and from the cyan diamond ore by silhouette/background. The scatter image visibly spells **SCATTER** exactly at full size and desktop size. At 400×225 the word is too small to read; the pickaxe and magenta frame still identify the symbol. The final paytable and accessible label should supply its meaning.
- The 400×225 and 1200×675 previews show all 30 board cells and the side character without board overlap or visible clipping. The warm cave, block geometry and lighting are coherent. No obvious copied Minecraft texture, character, logo or other recognizable third-party material appeared in this visual inspection; that is not a license/provenance audit.

## Technical evidence

- Exactly eleven new symbol files are present. Each opens as **1254×1254 RGBA**, has alpha range 0–255 and transparent corners; each contains hundreds of thousands of fully transparent pixels. Two images have a corner alpha of 1 at one bottom corner, visually negligible.
- In an isolated temporary copy under `art/`, `node export_png.mjs` exited 0 and rendered the expected fifteen SVG-derived PNGs plus `preview.png`, `preview-mini.png` and `preview-desktop.png`. The regenerated previews were pixel-identical to the checked-in versions: 1400×1715, 400×225 and 1200×675 respectively.
- SHA-256 before/after the isolated export found no changes to all thirteen 3D rasters (eleven symbols plus cave and explorer), all fifteen SVGs, or all fifteen fallback PNGs.
- Local headless Chrome loaded `preview.html`: **78/78 images** were complete with positive natural dimensions. No console errors, page errors, failed requests or HTTP 4xx/5xx responses were observed.
- `README.md` maps all eleven art IDs to fallback/current files and records how the raster set was generated. The math `lapis` to art `lapis_ore` mapping is documented.

## Integration notes

The eleven source PNGs total about **16.5 MiB**. Before frontend use at roughly 32 px per mini-cell symbol, make appropriately sized runtime variants/atlases and verify performance in the real canvas. The mini preview cannot establish text legibility or interaction behavior. Actual frontend loading, animation, accessibility and game math were outside this art review.
