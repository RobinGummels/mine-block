# Block Cave art templates

Original prototype art for the 6×5 board. The editable SVG fallback uses a
64×64 logical pixel grid and transparent 512×512 PNG exports. The current
preview uses separate transparent 1254×1254 3D raster symbols. These assets
were made for this project from the written brief and contain no third-party
textures, characters or downloaded assets. They are not final production art
or approved platform assets.

| Asset ID | SVG fallback | Pixel PNG | Current 3D PNG | Visual |
| --- | --- | --- | --- | --- |
| `earth` | `earth.svg` | `earth.png` | `earth_3d.png` | wet soil with grassy top |
| `stone` | `stone.svg` | `stone.png` | `stone_3d.png` | layered textured rock |
| `timber` | `timber.svg` | `timber.png` | `timber_3d.png` | dark bark, light cut surface |
| `copper_ore` | `copper_ore.svg` | `copper_ore.png` | `copper_ore_3d.png` | broad orange plates |
| `lapis_ore` | `lapis_ore.svg` | `lapis_ore.png` | `lapis_ore_3d.png` | deep cobalt pools |
| `gold_ore` | `gold_ore.svg` | `gold_ore.png` | `gold_ore_3d.png` | yellow cubical nuggets |
| `emerald_ore` | `emerald_ore.svg` | `emerald_ore.png` | `emerald_ore_3d.png` | vertical green prisms |
| `diamond_ore` | `diamond_ore.svg` | `diamond_ore.png` | `diamond_ore_3d.png` | cyan kite-shaped gems |
| `fantasy_alloy_ingot` | `fantasy_alloy_ingot.svg` | `fantasy_alloy_ingot.png` | `fantasy_alloy_ingot_3d.png` | near-black alloy **block**, restrained violet seams |
| `ore_vein_wild` | `ore_vein_wild.svg` | `ore_vein_wild.png` | `ore_vein_wild_3d.png` | cyan/violet four-arm junction, no text |
| `pickaxe_scatter` | `pickaxe_scatter.svg` | `pickaxe_scatter.png` | `pickaxe_scatter_3d.png` | cyan pickaxe, magenta plaque, SCATTER label |

The math symbol ID `lapis` maps to art asset ID `lapis_ore`. The rare
alloy keeps its current `fantasy_alloy_ingot` asset ID for compatibility,
although its revised visual is a block. Any ID change must be coordinated
with math and frontend.

## 3D symbol provenance

All eleven current symbol PNGs are 1254×1254 RGBA with transparent corners,
generated for this project with the built-in image-generation tool on
2026-11-18. Each prompt used its matching pixel PNG as a semantic reference,
the 3D cave/character as lighting and material references, and a consistent
three-quarter orthographic cube angle, amber left light, cyan right rim, crisp
voxel geometry and transparent cutout. The ore prompts required differently
shaped mineral inclusions **inside** the same stone cube. Wild and scatter
were prompted as different silhouettes; the exact SCATTER label was added in
a targeted edit. The 3D PNGs are raster sources, not exports of the SVGs.

| 3D asset | Built-in generation output ID |
| --- | --- |
| `earth_3d.png` | `exec-07e8890e-dca0-4abe-85f7-a76cc9fb288b.png` |
| `stone_3d.png` | `exec-507b7d3f-6c29-4b80-b7ca-f249901476b9.png` |
| `timber_3d.png` | `exec-b51b3aec-aa3a-48db-af5c-8b7f10c72351.png` |
| `copper_ore_3d.png` | `exec-57c23347-96f4-402f-94f9-2a171e97ffd4.png` |
| `lapis_ore_3d.png` | `exec-7b3399db-918d-4e5f-a418-ebbbe3cd1c11.png` |
| `gold_ore_3d.png` | `exec-a1fbf490-061d-4410-a2dd-9c68f88ef736.png` |
| `emerald_ore_3d.png` | `exec-fc356747-c6e1-477d-aa91-d0b84f715757.png` |
| `diamond_ore_3d.png` | `exec-dbc32fdc-a4e4-4601-af75-4679b83fe595.png` |
| `fantasy_alloy_ingot_3d.png` | `exec-a7003f2b-8df8-487e-b528-4de801cf1922.png` |
| `ore_vein_wild_3d.png` | `exec-2aed7ed7-3961-4458-83ad-bc9fd37f5fc0.png` |
| `pickaxe_scatter_3d.png` | `exec-3e9b859f-915b-4ef0-a2ee-1fb548089705.png` |

## Wild visual options

| Option | SVG / PNG | Distinguishing shape |
| --- | --- | --- |
| Default cyan | `ore_vein_wild.svg` / `ore_vein_wild.png` | crystal cross |
| Violet rune | `ore_vein_wild_violet.svg` / `ore_vein_wild_violet.png` | mirrored rune stones |
| Chromatic nexus | `ore_vein_wild_nexus.svg` / `ore_vein_wild_nexus.png` | multicolor junction |

All three variants are dark purple stone, intentionally different from
yellow gold ore and the dark alloy's narrow violet seams. Only the default
file is the current game symbol; alternatives are for design selection.

## Scene assets

| Asset ID | SVG source | PNG export | Size and alpha |
| --- | --- | --- | --- |
| `cave_background` | `cave_background.svg` | `cave_background.png` | 1920×1080, opaque |
| `cave_background_3d` | — | `cave_background_3d.png` | 1672×941, opaque |
| `cave_explorer` | `cave_explorer.svg` | `cave_explorer.png` | 512×768, transparent |
| `cave_explorer_3d` | — | `cave_explorer_3d.png` | 1024×1536, transparent |

The 3D cave background was generated for this project from the user's block-cave
brief (local generation output `exec-60904c94-e8ec-4221-8317-0982e8021dcd.png`,
2026-11-18). It is a raster prototype with cave depth, torchlight and lava.
`preview.html` uses it behind the board. The editable pixel-art
`cave_background.svg` and its PNG remain as fallback. The 3D PNG is a separate
source asset; neither regeneration command above overwrites it. The side
explorer in the current preview is a separate original 3D raster prototype.
It was made with the built-in image-generation tool on 2026-11-18 and revised
after independent visual review (`exec-e13ea87c-5e69-49c8-9bce-a25d4b276b31.png`).
Revision prompt: keep the original adult three-quarter mining pose and raised
cyan-accented pickaxe, aubergine workcoat, ochre hood/scarf, copper goggles and
charcoal boots; rebuild the head, face, torso, arms, hands and legs from
visible cubes and rectangular prisms with hard right-angle edges and a
transparent background. The supplied adventurer image guided the action
silhouette only. The original editable
`cave_explorer.svg` and its PNG remain untouched as a fallback. The 3D PNG is
not generated or overwritten by the regeneration commands below.

## Regeneration and review

From this directory:

```powershell
python .\generate_templates.py
node .\export_png.mjs
```

The Python source uses only the standard library. PNG export reuses the
project's installed Playwright package in `qa/node_modules` and local Chrome;
no new package is installed. These commands regenerate pixel-art SVG/PNG
fallbacks and preview PNGs; they do not replace the 3D raster sources.
`preview.html` and `preview.png` show the
asset sheet plus 400×225 and 1200×675 example board layouts. The isolated
`preview-mini.png` and `preview-desktop.png` are easier to inspect at
their actual sizes.

The current 3D Wild is identified by its cross-shaped silhouette; the
SCATTER lettering is tiny at 400×225 and cannot carry the meaning alone.
The final frontend should explain both special symbols in the paytable and
accessible text. The preview does not test
actual Pixi integration, animation or platform approval.
