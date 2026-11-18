# Block Cave art v4: independent character review

Date: 2026-11-18. Scope: new `art/templates/cave_explorer_3d.png`, both board previews, `preview.html`, `README.md`, and `export_png.mjs`. The art implementation was not edited during this review.

## Verdict

**Technical checks pass; visual direction needs one revision before character acceptance.** The new miner is original and visually active, but the head and limbs read as a conventional rounded 3D cartoon person rather than the requested blocky 3D character. This is a visual-brief blocker, not a file or layout defect.

## Findings

1. **Blocking visual brief mismatch — character silhouette.** The supplied reference has a square, cuboid head and rectangular limbs. The new miner has a smooth oval face and nose, rounded ears and fingers, tapered upper arms and legs. The coat, boots, pickaxe, goggles and some rock surfaces are faceted, but they do not make the body read as a block character. At 400×225 the figure is too small for those facets to carry the requested style. Revise the character with an unmistakably cubic head, planar face, and clearly cuboid arms and legs while retaining its distinct workwear palette, equipment, proportions and facial design. Do not reproduce the reference character's turquoise shirt, blue trousers, brown hair/beard or facial layout.
2. **Nonblocking cutout note.** `cave_explorer_3d.png` is a real RGBA image, 1024×1536. Corners have alpha 0; 711,027 pixels are fully transparent and 861,837 have partial alpha (maximum alpha 254). The warm/cyan glow reaches the image bounds, so the nonzero-alpha bounding box spans the entire canvas. This looks intentional in both previews; a tighter cutout may make later animation/layering easier.

## Checks performed

- **Reference and layout inspection:** Visually compared the supplied reference image with the current character raster and viewed `preview-mini.png` at 400×225 and `preview-desktop.png` at 1200×675. The raised pickaxe gives an active pose. The miner sits to the right of the 6×5 board in both layouts, with no board overlap or visible clipping. On the mini layout, the character is recognizable as a pickaxe-bearing miner, but facial detail is not discernible at final size.
- **Assets load:** Opened an isolated copy of `preview.html` in local headless Chrome. Every `<img>` returned `complete: true` and a positive natural width/height, including the new character and 3D background.
- **Isolated exporter:** Copied the template directory to a verified temporary directory under `art/` and ran `node export_png.mjs` there. It exited 0 and exported the expected 15 SVG PNGs plus three previews. The regenerated `preview.png`, `preview-mini.png` and `preview-desktop.png` matched the checked-in images pixel for pixel. SHA-256 checks before/after confirmed that `cave_explorer_3d.png`, `cave_background_3d.png`, `cave_explorer.svg` and the fallback `cave_explorer.png` were unchanged. The temporary copy was removed after checks.
- **Documentation:** `README.md` records the 1024×1536 transparent raster, its generation provenance, fallback assets and preview/export workflow. The fallback SVG/PNG are present.

The visual comparison is an art-direction judgment, not legal IP clearance. No frontend integration, animation or game math was tested in this art review.

## Re-review addendum — 2026-11-18, revised character

**Final QA verdict: technical PASS; the cubic-silhouette blocker above is resolved.** The current `cave_explorer_3d.png` has an unmistakably box-shaped head with a planar pixel-like face, cuboid hands and arms, and rectangular legs and boots. The body and raised pickaxe now read as a dynamic voxel miner in both board previews. At 400×225, the character is small but its angular silhouette and raised tool remain visible. At 1200×675, the figure is fully visible to the right of the board. Neither preview shows board overlap or clipping.

The figure is visually distinct from the supplied reference: aubergine workcoat, ochre hood/scarf, goggles, cyan-accented tool and a different face. **Product-direction follow-up:** the hooded, stylized figure can read more feminine or androgynous than the reference's simple masculine adventurer. Its resemblance to the user's Steve-like intent now comes mainly from its cubic anatomy and mining tool, not clothing or character identity. The user should review that interpretation before treating this raster as final character art; it does not block use as a prototype.

Affected technical checks were rerun on the revised asset. It is 1024×1536 RGBA with transparent corners and alpha range 0–254 (716,461 fully transparent pixels). In an isolated copy, `node export_png.mjs` again exited 0, regenerated 15 SVG-derived PNGs and three previews, and produced preview pixels identical to the checked-in files. All 78 `<img>` elements in `preview.html` loaded in Chrome (`complete` and positive natural width). SHA-256 before/after confirmed that the new 3D character, 3D background and original SVG/PNG explorer fallback were not overwritten. The revised generation prompt/provenance is recorded in `README.md`.
