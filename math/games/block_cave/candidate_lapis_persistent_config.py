"""Block Cave Variant P — Lapis Lazuli + persistent ore veins (DEV, unpublished).

This is a SEPARATE, clearly-labelled DEV config. It does NOT modify the
validated §3.1 baseline in `game_config.py`, nor `candidate_a_config.py`,
`candidate_b_config.py`, `candidate2_config.py`, `variant_config.py` nor
`candidate_lapis_config.py`; all of those remain reproducible and unchanged.

PURPOSE (Variant P):
    Build on the Lapis Lazuli config (`candidate_lapis_config.py`) and gate the
    **persistent-ore-vein** mechanic behind `config.ore_vein_persist_freespins`
    (a config attribute that DEFAULTS OFF in `game_config.py`). When ON, every
    ore vein that lands on a free-spin board becomes persistent (locked, never
    explodes) and its position carries forward to subsequent free spins in the
    SAME series. The whole free-spin series is one reproducible game book; the
    persistent set is reset at the series start so no state transfers to a later
    paid round. There is no bonus multiplier in Variant P.

CALIBRATION:
    To hold the natural RTP inside the 96.0-96.7% band while the persistent
    veins lift the tail, the paytable merges the §3.1 tiers 5-7 and 8-10 into
    two tiers (so 9 tiers -> 5 tiers) and reduces the small-cluster pay values
    (a winning 5-7 cluster still pays >= 0.10x). The reel strips and symbol
    counts are the Lapis Lazuli ones (identical to `candidate_lapis_config.py`).

DEV measurement only - NOT a production RTP claim. Nothing here is published or
deployed. All numbers are DEV measurements on the current prototype.
"""

from __future__ import annotations

import hashlib
import random

from game_config import GameConfig, sha256_strip

# ---------------------------------------------------------------------------
# Variant identity
# ---------------------------------------------------------------------------

VARIANT_NAME = "Block Cave Variant P (Lapis + persistent ore veins)"
VARIANT_DESCRIPTION = (
    "Lapis Lazuli strips with the persistent-ore-vein free-spin mechanic "
    "(ore_vein_persist_freespins=True) and a merged, small-cluster-reduced "
    "paytable (tiers 5-7 and 8-10 merged). DEV measurement only."
)

# ---------------------------------------------------------------------------
# Strips (identical to Lapis Lazuli: same counts, same seeds, lapis in place of
# silver at the same NONCOMMON_ORDER position)
# ---------------------------------------------------------------------------

LAPIS_COMMON_ORDER = ["earth", "stone", "timber", "copper"]
LAPIS_NONCOMMON_ORDER = ["lapis", "gold", "emerald", "diamond", "ingot", "ore_vein", "pickaxe"]

BASE_COUNTS = {
    "earth": 36, "stone": 33, "timber": 31, "copper": 30,
    "lapis": 16, "gold": 14, "emerald": 12, "diamond": 8,
    "ingot": 9, "ore_vein": 8, "pickaxe": 3,
}

FREE_COUNTS = {
    "earth": 42, "stone": 40, "timber": 38, "copper": 36,
    "lapis": 8, "gold": 9, "emerald": 8, "diamond": 6,
    "ingot": 5, "ore_vein": 5, "pickaxe": 3,
}

BASE_SEED = 20261117
FREE_SEED = 20261118

# Ore-vein upgrade (DEV rule, same as Lapis / Candidate A).
ORE_VEIN_RULE = "create-cluster"
ORE_VEIN_TARGET = "diamond"

# Persistent-vein cap: the maximum number of ore veins recorded as persistent
# within a free-spin series. `game_override._rescan_persistent_veins` clamps
# the set to this many (when set), so the set cannot grow without bound across
# a long series. Kept in `build_config()` so the shipped config is
# self-contained and matches report §1 (`config.ore_vein_persist_max = 7`).
ORE_VEIN_PERSIST_MAX = 7

# ---------------------------------------------------------------------------
# Merged, small-cluster-reduced paytable (9 tiers -> 5 tiers)
# ---------------------------------------------------------------------------

# Merged cluster-size ranges, ascending. Tiers 5-7 and 8-10 are merged from the
# §3.1 PAY_RANGES; tiers 11-14, 15-19 and 20-30 are unchanged.
VARIANT_PAY_RANGES = [(5, 7), (8, 10), (11, 14), (15, 19), (20, 30)]

# Paytable values (multiples of the play amount) per symbol, one entry per
# VARIANT_PAY_RANGES index. Small-cluster values (index 0 = tiers 5-7) are
# reduced relative to the §3.1 5-cluster values (a winning 5-7 cluster still
# pays >= 0.10x). The high tiers (11-14, 15-19, 20-30) are retained at the
# §3.1 low end so the persistent-vein tail can express itself.
#
# CALIBRATION: the common symbols are uniformly scaled by ~1.10 (the
# `--common-scale` lever from `.runtime/block_cave/calib_paytable.py`). This is
# the calibration lever that lifts the base RTP (common symbols dominate the
# base RTP while premium/ingot drive the tail). The values below are the baked
# result at cap=7, common-scale=1.10; premium and ingot are left unscaled so the
# persistent-vein tail is unchanged. Rounded to 2 decimals. The 1.10 value
# centres the pooled out-of-sample RTP in the 96.0-96.7% band (1.11 gave a
# pooled point estimate ~0.970, slightly above the 0.967 upper edge).
_P_COMMON_PAYS = {
    "earth": [0.20, 0.81, 3.04, 5.06, 8.09],
    "stone": [0.24, 1.01, 3.64, 6.06, 10.11],
    "timber": [0.29, 1.21, 4.65, 7.69, 12.13],
    "copper": [0.32, 1.42, 5.67, 9.10, 15.17],
}
_P_PREMIUM_PAYS = {
    "lapis": [0.55, 2.39, 9.19, 14.71, 23.90],
    "gold": [0.92, 3.68, 14.71, 23.90, 36.77],
    "emerald": [1.47, 6.43, 23.90, 36.77, 58.82],
    "diamond": [2.21, 10.11, 36.77, 58.82, 91.91],
}
_P_INGOT_PAYS = {
    "ingot": [5.51, 23.90, 91.91, 147.06, 229.78],
}


def build_lapis_strip(seed, counts):
    """Return a length-200 strip whose symbol counts equal `counts`.

    Byte-for-byte mirror of `candidate_lapis_config.build_lapis_strip` (and
    `game_config.build_strip` with lapis in place of silver). The RNG sequence
    is identical, so the strip arrangement equals Candidate A's strip after
    renaming `silver` -> `lapis`.
    """
    rng = random.Random(seed)

    runs = []
    for sym in LAPIS_COMMON_ORDER:
        c = counts[sym]
        runs.extend([[sym, sym]] * (c // 2))
        if c % 2 == 1:
            runs.append([sym])

    singles = []
    for sym in LAPIS_NONCOMMON_ORDER:
        singles.extend([sym] * counts[sym])

    buckets = [[] for _ in range(len(runs) + 1)]
    for s in singles:
        buckets[rng.randrange(len(buckets))].append(s)

    order = list(range(len(runs)))
    rng.shuffle(order)

    strip = []
    for idx in order:
        strip.extend(runs[idx])
        strip.extend(buckets[idx])
    strip.extend(buckets[len(runs)])
    return strip


def build_pay_group():
    """Return a `pay_group` dict with the merged VARIANT_PAY_RANGES.

    `lapis` replaces `silver` (same values as the Lapis silver row). Each
    merged range maps to a single pay value per symbol.
    """
    pay_group = {}
    all_pays = {}
    all_pays.update(_P_COMMON_PAYS)
    all_pays.update(_P_PREMIUM_PAYS)
    all_pays.update(_P_INGOT_PAYS)
    for symbol, values in all_pays.items():
        for rng, value in zip(VARIANT_PAY_RANGES, values):
            pay_group[(rng, symbol)] = value
    return pay_group


def build_lapis_strips():
    """Return (base_strip, free_strip) for the Variant P config."""
    base = build_lapis_strip(BASE_SEED, BASE_COUNTS)
    free = build_lapis_strip(FREE_SEED, FREE_COUNTS)
    return base, free


def sha256():
    """Return (base_sha, free_sha) for the Variant P strips."""
    base, free = build_lapis_strips()
    return sha256_strip(base), sha256_strip(free)


def build_config() -> GameConfig:
    """Return a fresh GameConfig for Variant P.

    Reuses the §3.1 baseline bet modes, wincap, triggers; replaces the reel
    strips with the lapis strips (identical to `candidate_lapis_config`), the
    paytable with the merged small-cluster-reduced paytable, sets the DEV
    `create-cluster` -> `diamond` ore-vein rule, and gates the persistent-ore-
    vein mechanic ON. This does NOT change `game_config.py` nor any existing
    candidate config.
    """
    from calibrate import make_config  # DEV harness; resets the singleton

    config = make_config(1.0)
    # Replace the paytable with the merged, small-cluster-reduced version.
    config.paytable = config.convert_range_table(build_pay_group())
    base, free = build_lapis_strips()
    config.reels = {
        "BR0": [base] * config.num_reels,
        "FR0": [free] * config.num_reels,
    }
    config.ore_vein_rule = ORE_VEIN_RULE
    config.ore_vein_target = ORE_VEIN_TARGET
    # Gate the Variant P persistent-ore-vein mechanic ON, and bound the
    # persistent-vein set so it cannot grow without bound across a long series.
    config.ore_vein_persist_freespins = True
    config.ore_vein_persist_max = ORE_VEIN_PERSIST_MAX
    return config


# SHA-256 fingerprints of the generated strips (deterministic; identical to the
# Lapis Lazuli strips, since the strips/counts are unchanged).
BASE_SHA = "00af3ba544dba0ee523b6d4e85304d0622dd740a5c76dc13651e254a22558181"
FREE_SHA = "bc15b4fb96319e90f35024fe8b751b3ee3534731a56aa0f9939a7a8034db4c47"


if __name__ == "__main__":
    base, free = build_lapis_strips()
    bs, fs = sha256()
    assert len(base) == 200 and len(free) == 200
    assert all(base.count(s) == c for s, c in BASE_COUNTS.items())
    assert all(free.count(s) == c for s, c in FREE_COUNTS.items())
    assert "silver" not in base and "silver" not in free, "silver must be fully removed"
    assert bs == BASE_SHA, bs
    assert fs == FREE_SHA, fs
    # Paytable sanity: 5 merged ranges, all 5-7 cluster values >= 0.10x.
    cfg = build_config()
    assert cfg.ore_vein_persist_freespins is True, "persistent gate must be ON"
    assert cfg.ore_vein_persist_max == ORE_VEIN_PERSIST_MAX, (
        "persistent-vein cap must be set to match report §1"
    )
    assert cfg.ore_vein_rule == "create-cluster"
    assert cfg.ore_vein_target == "diamond"
    for size, sym in cfg.paytable:
        if 5 <= size <= 7:
            assert cfg.paytable[(size, sym)] >= 0.10, f"{sym} 5-7 pay < 0.10x"
    print(f"base strip sha256: {bs}")
    print(f"free strip sha256: {fs}")
    print("Variant P config reproducible (strips + SHAs + merged paytable + "
          "persistent-ore-vein gate ON)")
