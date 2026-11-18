"""Regenerate original pixel-art SVG sources; no third-party art or packages."""

from pathlib import Path
from random import Random
from sys import argv
from xml.etree import ElementTree


HERE = Path(__file__).parent
INK = "#0b0f1c"


def rect(x, y, w, h, color):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>'


def poly(points, color):
    return f'<polygon points="{points}" fill="{color}"/>'


def svg(title, body, width=512, height=512, grid_width=64, grid_height=64):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {grid_width} {grid_height}" shape-rendering="crispEdges" role="img">'
        f'<title>{title}</title>{body}</svg>\n'
    )


def texture(seed, colors, count=85):
    rng = Random(seed)
    return "".join(
        rect(rng.randrange(7, 57), rng.randrange(11, 57),
             rng.choice((1, 1, 2, 3)), rng.choice((1, 1, 2)), rng.choice(colors))
        for _ in range(count)
    )


FONT = {
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
}


def pixel_text(label, x, y, color):
    return "".join(
        rect(x + i * 6 + col, y + row, 1, 1, color)
        for i, letter in enumerate(label)
        for row, bits in enumerate(FONT[letter])
        for col, bit in enumerate(bits)
        if bit == "1"
    )


def cube(title, seed, left="#344255", right="#405169", top="#65758a",
         left_art="", right_art="", top_art="", badge="", texture_colors=None):
    texture_colors = texture_colors or ("#263345", "#58677b", "#728397")
    definitions = (
        '<defs>'
        '<clipPath id="left"><polygon points="7,16 32,28 32,58 7,46"/></clipPath>'
        '<clipPath id="right"><polygon points="32,28 57,16 57,46 32,58"/></clipPath>'
        '<clipPath id="top"><polygon points="7,16 32,4 57,16 32,28"/></clipPath>'
        '</defs>'
    )
    body = (
        definitions
        + poly("5,15 32,2 59,15 59,47 32,61 5,47", INK)
        + poly("7,16 32,4 57,16 32,28", top)
        + poly("7,16 32,28 32,58 7,46", left)
        + poly("32,28 57,16 57,46 32,58", right)
        + f'<g clip-path="url(#left)">{texture(seed, texture_colors, 48)}{left_art}</g>'
        + f'<g clip-path="url(#right)">{texture(seed + 17, texture_colors, 48)}{right_art}</g>'
        + f'<g clip-path="url(#top)">{texture(seed + 33, ("#8695a4", "#435269"), 22)}{top_art}</g>'
        + poly("6,15 32,3 58,15 57,18 32,6 7,18", "#1c2739")
        + poly("31,27 33,27 33,58 31,58", "#0e1728")
        + badge
    )
    return svg(title, body)


def ore(title, seed, color, highlight, kind):
    # Mineral silhouettes are deliberate: nodules, pools, nuggets, columns, gems.
    if kind == "copper":
        left = (poly("11,30 16,28 16,25 22,25 22,29 26,29 26,35 20,35 20,38 13,36", color)
                + rect(14, 28, 5, 2, highlight) + rect(24, 43, 5, 4, color))
        right = (poly("37,31 41,27 46,27 46,24 52,24 52,31 49,31 49,36 42,36 42,40 37,38", color)
                 + rect(40, 29, 7, 2, highlight) + rect(47, 42, 5, 4, color))
    elif kind == "lapis":
        left = (poly("11,29 17,23 24,26 27,33 23,39 17,40 12,36", "#133f9b")
                + rect(16, 27, 6, 5, color) + rect(20, 34, 4, 3, highlight)
                + rect(11, 42, 3, 2, color))
        right = (poly("37,31 43,24 51,25 54,32 50,38 42,41 37,37", "#133f9b")
                 + rect(42, 29, 8, 6, color) + rect(45, 27, 4, 2, highlight)
                 + rect(51, 42, 3, 2, color))
    elif kind == "gold":
        left = (rect(13, 28, 5, 5, color) + rect(16, 25, 6, 7, color)
                + rect(22, 32, 5, 6, color) + rect(15, 26, 4, 2, highlight)
                + rect(23, 43, 5, 4, color))
        right = (rect(39, 29, 7, 6, color) + rect(43, 25, 7, 6, color)
                 + rect(48, 34, 5, 7, color) + rect(43, 26, 5, 2, highlight)
                 + rect(36, 42, 5, 4, color))
    elif kind == "emerald":
        left = (poly("13,27 18,23 23,26 23,36 19,41 13,38", color)
                + rect(16, 26, 3, 10, highlight)
                + poly("24,41 27,39 29,41 29,48 25,49", color))
        right = (poly("40,29 46,21 52,25 52,37 47,43 40,39", color)
                 + rect(44, 26, 3, 12, highlight)
                 + poly("36,44 39,41 43,44 42,50 38,52", color))
    else:  # diamond
        left = (poly("12,29 19,23 26,29 19,39", color)
                + poly("19,23 26,29 19,31", highlight)
                + poly("22,42 27,38 30,43 26,49", color))
        right = (poly("39,30 47,22 54,29 47,41", color)
                 + poly("47,22 54,29 47,31", highlight)
                 + poly("35,44 40,40 44,45 40,51", color))
    top_art = rect(28, 12, 3, 2, color) + rect(35, 14, 2, 2, highlight)
    return cube(title, seed, left_art=left, right_art=right, top_art=top_art)


def wild_variant(title, seed, primary, secondary, pattern):
    if pattern == "rune":
        art = (
            poly("11,34 17,27 23,30 27,24 31,30 32,42 27,47 20,43 14,48", primary)
            + poly("37,31 43,25 48,30 54,25 54,39 48,43 42,39 38,47", primary)
            + rect(18, 32, 4, 8, secondary) + rect(46, 32, 4, 8, secondary)
            + rect(24, 43, 4, 3, secondary)
        )
    elif pattern == "cross":
        art = (
            poly("16,29 21,24 25,29 21,35", primary)
            + poly("37,32 44,26 47,19 52,24 50,31 56,34 48,39 45,48 40,43 37,39 33,37", primary)
            + rect(44, 29, 4, 13, secondary) + rect(39, 34, 13, 4, secondary)
        )
    else:
        art = (
            poly("13,29 18,24 23,29 20,34 25,39 19,44 14,40 17,35", primary)
            + poly("39,31 44,24 49,29 54,26 52,35 56,40 49,45 43,41 39,47 35,40", secondary)
            + rect(23, 42, 5, 4, "#59d4b6") + rect(47, 31, 4, 4, "#f7cc65")
        )
    badge = (rect(13, 48, 38, 12, INK)
             + rect(15, 49, 34, 1, primary)
             + pixel_text("WILD", 21, 51, "#f5f1e8"))
    return cube(title, seed, left="#2a2247", right="#352951", top="#554068",
                left_art=art, right_art=art, top_art=rect(28, 13, 7, 4, primary),
                badge=badge, texture_colors=("#191b3b", "#51436a", "#71528b"))


symbols = {
    "earth.svg": cube(
        "Wet grass earth block", 1, "#5c3a36", "#6e483d", "#618349",
        left_art=(rect(9, 24, 5, 4, "#342b30") + rect(19, 34, 7, 3, "#80604c")
                  + rect(11, 42, 7, 3, "#2e2a30") + rect(26, 48, 4, 5, "#aa7451")
                  + rect(10, 18, 3, 7, "#4b703d") + rect(18, 21, 4, 5, "#779e56")),
        right_art=(rect(36, 27, 6, 3, "#2e2a30") + rect(45, 38, 7, 4, "#96684c")
                   + rect(40, 47, 5, 3, "#2e2a30") + rect(51, 17, 3, 8, "#83a95b")),
        top_art=(rect(15, 15, 8, 3, "#8dae5b") + rect(29, 8, 6, 3, "#a4b96a")
                 + rect(39, 15, 7, 2, "#386b42")),
        texture_colors=("#342b30", "#86614c", "#a17458"),
    ),
    "stone.svg": cube(
        "Layered rock block", 4,
        left_art=(poly("9,32 16,35 16,38 22,38 22,42 29,45 29,48 23,46 20,43 14,43 14,39 9,37", "#1c293c")
                  + rect(14, 27, 7, 2, "#9ba9b2")),
        right_art=(poly("36,36 42,33 42,29 48,26 55,29 55,32 48,30 45,35 39,38", "#172437")
                   + rect(38, 44, 11, 2, "#91a1af")),
        texture_colors=("#253346", "#596c7e", "#8594a4"),
    ),
    "timber.svg": cube(
        "Dark bark log block", 8, "#47332d", "#58402f", "#c79d65",
        left_art=(rect(10, 22, 2, 25, "#231e24") + rect(17, 27, 3, 24, "#2b2024")
                  + rect(25, 30, 2, 24, "#281f24") + rect(14, 34, 8, 2, "#9b6a46")
                  + rect(23, 44, 6, 2, "#9b6a46")),
        right_art=(rect(37, 25, 3, 26, "#291f23") + rect(46, 21, 2, 25, "#281e21")
                   + rect(53, 19, 2, 26, "#2a2023") + rect(40, 37, 11, 2, "#9b6a46")),
        top_art=(poly("16,16 32,8 49,16 32,24", "#e3b87b")
                 + poly("22,16 32,11 42,16 32,21", "#a8734a")
                 + poly("27,16 32,13 38,16 32,19", "#e9c992")),
        texture_colors=("#2d2526", "#6e503b", "#8c6241"),
    ),
    "copper_ore.svg": ore("Copper nodules in stone", 11, "#d86d3d", "#ffc087", "copper"),
    "lapis_ore.svg": ore("Cobalt lapis pockets in stone", 12, "#2575df", "#8bc7ff", "lapis"),
    "gold_ore.svg": ore("Gold nuggets in stone", 13, "#f1b932", "#fff1a0", "gold"),
    "emerald_ore.svg": ore("Emerald prisms in stone", 14, "#36bd7f", "#b7ffe1", "emerald"),
    "diamond_ore.svg": ore("Cut blue gems in stone", 15, "#43cdf1", "#e8fcff", "diamond"),
    "fantasy_alloy_ingot.svg": cube(
        "Dark fantasy alloy block", 16, "#1a1b28", "#262333", "#353243",
        left_art=(poly("10,28 18,25 22,31 29,32 29,36 23,36 18,33 13,35", "#704c93")
                  + rect(17, 27, 4, 2, "#d6a0f0") + rect(13, 43, 7, 5, "#4b365c")
                  + rect(24, 47, 4, 3, "#a66cc1")),
        right_art=(poly("37,31 43,26 48,28 54,24 54,31 49,34 43,33 39,39", "#8c59ad")
                   + rect(43, 28, 5, 2, "#e6b5fb") + rect(40, 45, 10, 4, "#533c70")
                   + rect(51, 38, 3, 6, "#bd83dc")),
        top_art=(rect(29, 9, 8, 3, "#8c59ad") + rect(37, 14, 5, 2, "#bd83dc")),
        texture_colors=("#0c1019", "#383349", "#4e435c"),
    ),
    "ore_vein_wild.svg": wild_variant("Cyan crystal cross WILD", 18, "#51e4ed", "#c6ffff", "cross"),
    "pickaxe_scatter.svg": svg(
        "Pickaxe free spin SCATTER",
        rect(4, 4, 56, 56, INK)
        + rect(6, 6, 52, 52, "#701e70")
        + rect(8, 8, 48, 41, "#af337e")
        + rect(9, 31, 3, 3, "#ffe0a3")
        + rect(49, 37, 4, 3, "#ffe0a3")
        + poly("26,20 33,22 23,48 16,45", INK)
        + poly("28,22 31,23 21,45 18,44", "#a3653e")
        + rect(19, 39, 4, 2, "#d69a59")
        + poly("10,19 15,14 24,12 39,12 49,15 56,19 54,24 48,21 40,20 26,20 18,22 13,26", INK)
        + poly("13,19 17,16 25,14 39,14 48,17 53,20 51,22 47,19 39,18 26,18 18,20 15,23", "#31cbd5")
        + rect(24, 14, 18, 2, "#b8fcff")
        + poly("13,19 17,16 20,17 16,22 15,23", "#168b9c")
        + poly("48,17 53,20 51,22 47,19", "#168b9c")
        + rect(27, 19, 5, 3, "#7beaf0")
        + rect(8, 49, 48, 11, INK)
        + rect(9, 49, 46, 1, "#ffe0a3")
        + pixel_text("SCATTER", 11, 51, "#fff8db"),
    ),
}

alternatives = {
    "ore_vein_wild_violet.svg": wild_variant(
        "Violet rune vein WILD", 17, "#bd62eb", "#f7c5ff", "rune"),
    "ore_vein_wild_nexus.svg": wild_variant(
        "Chromatic vein nexus WILD", 19, "#f16bce", "#69e6ef", "nexus"),
}

background = svg(
    "Original pixel-art lava tunnel",
    rect(0, 0, 480, 270, "#0b1020")
    + poly("0,0 480,0 335,73 145,73", "#1f273b")
    + poly("0,0 145,73 145,193 0,270", "#2c3544")
    + poly("480,0 335,73 335,193 480,270", "#263144")
    + poly("0,270 145,193 335,193 480,270", "#202637")
    + poly("145,73 335,73 335,193 145,193", "#131a2b")
    + poly("181,98 299,98 299,190 181,190", "#0a1224")
    + poly("191,168 289,168 302,210 177,210", "#482735")
    + poly("190,188 289,188 311,220 171,220", "#e75c2c")
    + poly("201,191 253,190 279,208 185,208", "#ffc04b")
    + poly("240,205 299,198 315,218 222,218", "#ff8b2f")
    + poly("0,29 109,29 145,73 145,193 90,220 0,220", "#354050")
    + poly("480,29 371,29 335,73 335,193 390,220 480,220", "#303d51")
    + poly("0,0 80,0 143,72 110,72", "#4b5262")
    + poly("480,0 400,0 337,72 370,72", "#475162")
    + poly("0,218 86,218 145,193 178,220 0,270", "#414455")
    + poly("480,218 394,218 335,193 302,220 480,270", "#3a4051")
    + "".join(rect(x, 0, 5, 220, "#182235") for x in (19, 94, 383, 456))
    + "".join(rect(x, 35, 2, 161, "#657083") for x in (113, 365))
    + rect(0, 220, 480, 50, "#222838")
    + poly("0,222 90,223 145,199 170,219 0,250", "#505260")
    + poly("480,222 390,223 335,199 310,219 480,250", "#4b4f60")
    + rect(83, 76, 10, 61, "#6f4d37") + rect(387, 76, 10, 61, "#6f4d37")
    + poly("79,77 86,50 91,65 97,46 102,76", "#f1a437")
    + poly("383,77 390,50 395,65 401,46 406,76", "#f1a437")
    + rect(86, 64, 6, 13, "#ffe09b") + rect(390, 64, 6, 13, "#ffe09b")
    + rect(92, 113, 4, 4, "#cf9b54") + rect(384, 103, 4, 4, "#cf9b54")
    + rect(98, 32, 284, 194, "#111929")
    + rect(101, 35, 278, 188, "#162033")
    + rect(101, 35, 278, 4, "#4a5669")
    + rect(101, 219, 278, 4, "#4a5669")
    + rect(101, 35, 4, 188, "#4a5669")
    + rect(375, 35, 4, 188, "#4a5669")
    + poly("154,233 326,233 354,250 126,250", "#41212e")
    + poly("163,236 317,236 337,248 143,248", "#e85827")
    + poly("185,237 259,237 279,243 174,243", "#ffd15a")
    + rect(271, 243, 47, 3, "#ff9b36")
    + poly("110,0 370,0 312,34 168,34", "#2a3448")
    + poly("150,0 330,0 285,32 195,32", "#151e30")
    + poly("195,0 285,0 266,30 214,30", "#0a1222")
    + poly("0,13 111,16 170,32 166,34 101,24 0,23", "#697287")
    + poly("480,13 369,16 310,32 314,34 379,24 480,23", "#697287")
    + rect(223, 25, 34, 7, "#5b2c34")
    + rect(229, 27, 22, 4, "#f08135")
    + rect(233, 28, 12, 2, "#ffd66e"),
    1920, 1080, 480, 270,
)

assets = {**symbols, **alternatives, "cave_background.svg": background}
requested = argv[1] if len(argv) > 1 else None
if requested and requested not in assets:
    raise SystemExit(f"Unknown asset: {requested}")
for filename, contents in assets.items():
    if requested and filename != requested:
        continue
    ElementTree.fromstring(contents)
    (HERE / filename).write_text(contents, encoding="utf-8")

assert len(symbols) == 11 and len(alternatives) == 2
ElementTree.parse(HERE / "cave_explorer.svg")
print(f"Generated {requested or 'all assets'}.")
