# Design system — Block Cave (draft)

Status: visual direction for review, not final production art. The current
3D raster symbols and the pixel-art SVG/PNG fallbacks in `art/templates/` are
original prototypes.

## Scene and layout

- 6×5 board in the center; a clearly separate control and information zone.
  Keep symbol silhouettes distinguishable at 400×225, 800×450 and 1200×675.
- Original cubic cave architecture, a tunnel with visible depth, lava below
  the board and warm torchlight. The current 3D raster prototype
  `art/templates/cave_background_3d.png` follows the warm dripstone mood of
  the user's fifth reference; the older pixel-art cave remains a fallback. An
  original adult explorer may react at the side without hiding symbols,
  controls, win text or rules. No Minecraft/Roblox textures or recognizable
  character likenesses. The current `cave_explorer_3d.png` prototype uses a
  cubic head and limbs, a raised pickaxe, and distinct aubergine/ochre miner
  clothing; the earlier vector explorer remains a fallback.
- Reserve room for play amount, win, free spins remaining, sound, settings,
  rules and an obvious primary play control. Use semantic HTML for controls
  and Pixi for the game scene.

## Initial visual tokens

| Role | Draft color | Use |
| --- | --- | --- |
| Deep cave | `#151a29` | background |
| Rock | `#344255` | blocks and panel |
| Torch amber | `#f4b64f` | focus and active highlights |
| Copper | `#ca744a` | common ore |
| Lapis | `#2575df` | premium ore |
| Emerald | `#46bc85` | premium ore |
| Diamond | `#76cde1` | premium ore |
| Alloy | `#1b1929` / `#8b5cae` | rare dark block with violet seams |
| Wild cyan | `#51e4ed` | crystal cross, separate from gold and alloy |
| Scatter magenta | `#a52274` | pickaxe background |
| Text | `#f5f1e8` | primary information |

These are prototype values. Text, controls and symbols need contrast checks
in all embed sizes. Do not rely on ore color alone: each ore needs its own
inclusion pattern and recognizable silhouette. Use a legible sans font with
system fallback; font choice and rights are open.

## Symbols and motion

- Regular symbols: muddy grass block, stone, bark-covered timber, copper,
  lapis, gold, emerald and diamond embedded in cubic stone, plus an original
  dark fantasy-alloy block. The math ID `lapis` maps to art ID `lapis_ore`;
  the rare block retains the `fantasy_alloy_ingot` asset ID for now.
- Current 3D ore vein: cyan/violet four-arm crystal junction; the older SVG
  variants retain WILD badges. Pickaxe: distinct large silhouette on a magenta
  field with SCATTER text. Explain both in the frontend rules and accessible
  text because the label is too small at 400×225.
- Motion follows the ordered server book. Cluster, tumble, ore-vein upgrade
  and free-spin entry animations must follow the event order agreed in Stage
  1; their current listing is not a rule. Provide a reduced-motion
  presentation with the same result and readable win information.
- No rapid flashing or essential information available only through audio.
  Audio control defaults and sound design remain open.

## Asset contract

Keep the 1254×1254 transparent 3D raster sources, editable SVG/PNG fallbacks
and a manifest with symbol ID, dimensions, transparency and provenance.
Production atlas format follows the frontend's measured Pixi requirements.
The templates are design references, not verified Pixi assets. Do not use the
Le Outlaw screenshots as distributable assets.
