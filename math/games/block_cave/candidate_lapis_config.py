"""Block Cave Stage-3 Lapis Lazuli configuration (DEV, unpublished).

This is a SEPARATE, clearly-labelled DEV candidate config. It does NOT modify
the validated §3.1 baseline in `game_config.py`, nor `candidate_a_config.py`,
nor `candidate_b_config.py`; all of those remain reproducible and unchanged.

PURPOSE (Part 1 — mathematically neutral rename):
    This config replaces the `silver` symbol with a new `lapis` symbol,
    derived from **Candidate A** (base E4 / free G6, `create-cluster` ->
    `diamond`, pay scale 1.0). It is **mathematically neutral**: the symbol
    counts, the paytable values (the `silver` row becomes the `lapis` row with
    the SAME values) and the strip ARRANGEMENT are identical. The ONLY
    difference in the generated strips is the literal string ``silver`` ->
    ``lapis``.

Because `game_config.build_strip` consumes randomness only via
``rng.randrange``/``rng.shuffle`` (which operate on integer indices, not on
symbol names), replacing ``silver`` with ``lapis`` at the SAME position in the
non-common order yields a strip whose pattern is byte-identical after the
silver->lapis rename. This module reproduces that procedure self-contained so
`game_config.py` is not touched.

DEV measurement only - NOT a production RTP claim. Nothing here is published or
deployed. All numbers are DEV measurements on the current prototype.
"""

from __future__ import annotations

import hashlib
import random

from game_config import GameConfig, PAY_RANGES, sha256_strip

# ---------------------------------------------------------------------------
# Lapis identity
# ---------------------------------------------------------------------------

VARIANT_NAME = "Block Cave Stage-3 Lapis Lazuli (create-cluster / high-hit)"
VARIANT_DESCRIPTION = (
    "Mathematically-neutral rename of Candidate A: `silver` -> `lapis` with "
    "identical counts, paytable values and strip arrangement. Uses the same "
    "positive create-cluster ore-vein rule (target diamond), pay scale 1.0, "
    "base seed 20261117 and free seed 20261118."
)

# ---------------------------------------------------------------------------
# Strips (deterministic; mirrors game_config.build_strip with lapis in place
# of silver at the same NONCOMMON_ORDER position)
# ---------------------------------------------------------------------------

# Same symbol orders as game_config, but `lapis` replaces `silver` at the same
# index. This keeps the RNG consumption sequence identical.
LAPIS_COMMON_ORDER = ["earth", "stone", "timber", "copper"]
LAPIS_NONCOMMON_ORDER = ["lapis", "gold", "emerald", "diamond", "ingot", "ore_vein", "pickaxe"]

# Base strip (E4): identical counts to Candidate A, silver -> lapis.
BASE_COUNTS = {
    "earth": 36, "stone": 33, "timber": 31, "copper": 30,
    "lapis": 16, "gold": 14, "emerald": 12, "diamond": 8,
    "ingot": 9, "ore_vein": 8, "pickaxe": 3,
}

# Free strip (G6): identical counts to Candidate A, silver -> lapis.
FREE_COUNTS = {
    "earth": 42, "stone": 40, "timber": 38, "copper": 36,
    "lapis": 8, "gold": 9, "emerald": 8, "diamond": 6,
    "ingot": 5, "ore_vein": 5, "pickaxe": 3,
}

BASE_SEED = 20261117
FREE_SEED = 20261118

# Ore-vein upgrade (DEV rule; default in game_config.py stays `baseline`).
ORE_VEIN_RULE = "create-cluster"
ORE_VEIN_TARGET = "diamond"

# Payout scale is 1.0 (the §3.1 calibrated paytable, unchanged).
PAY_SCALE = 1.0


def build_lapis_strip(seed, counts):
    """Return a length-200 strip whose symbol counts equal `counts`.

    Byte-for-byte mirror of `game_config.build_strip`, but the non-common order
    uses `lapis` in place of `silver`. The RNG sequence is identical, so the
    resulting strip arrangement equals Candidate A's strip after renaming
    `silver` -> `lapis`.
    """
    rng = random.Random(seed)

    # 1. Common symbols -> runs of 2, one single if the count is odd.
    runs = []
    for sym in LAPIS_COMMON_ORDER:
        c = counts[sym]
        runs.extend([[sym, sym]] * (c // 2))
        if c % 2 == 1:
            runs.append([sym])

    # 2. Non-common symbols -> individual singles, in LAPIS_NONCOMMON_ORDER.
    singles = []
    for sym in LAPIS_NONCOMMON_ORDER:
        singles.extend([sym] * counts[sym])

    # 3. len(runs)+1 gap buckets; place each single into a uniform bucket.
    buckets = [[] for _ in range(len(runs) + 1)]
    for s in singles:
        buckets[rng.randrange(len(buckets))].append(s)

    # 4. Shuffle the run order.
    order = list(range(len(runs)))
    rng.shuffle(order)

    # 5. Concatenate.
    strip = []
    for idx in order:
        strip.extend(runs[idx])
        strip.extend(buckets[idx])
    strip.extend(buckets[len(runs)])
    return strip


# ---------------------------------------------------------------------------
# Paytable (the `silver` row becomes the `lapis` row, same values)
# ---------------------------------------------------------------------------

_LAPIS_COMMON_PAYS = {
    "earth": [0.18, 0.28, 0.46, 0.74, 1.10, 1.65, 2.76, 4.60, 7.35],
    "stone": [0.22, 0.33, 0.55, 0.92, 1.38, 2.02, 3.31, 5.51, 9.19],
    "timber": [0.26, 0.40, 0.66, 1.10, 1.65, 2.57, 4.23, 6.99, 11.03],
    "copper": [0.29, 0.48, 0.77, 1.29, 2.02, 3.13, 5.15, 8.27, 13.79],
}
# `lapis` has EXACTLY Candidate A's `silver` pay row.
_LAPIS_PREMIUM_PAYS = {
    "lapis": [0.55, 0.92, 1.47, 2.39, 3.68, 5.51, 9.19, 14.71, 23.90],
    "gold": [0.92, 1.47, 2.39, 3.68, 5.88, 9.19, 14.71, 23.90, 36.77],
    "emerald": [1.47, 2.39, 4.04, 6.43, 10.11, 14.71, 23.90, 36.77, 58.82],
    "diamond": [2.21, 3.68, 6.43, 10.11, 15.63, 22.98, 36.77, 58.82, 91.91],
}
_LAPIS_INGOT_PAYS = {
    "ingot": [5.51, 9.19, 14.71, 23.90, 36.77, 55.15, 91.91, 147.06, 229.78],
}


def build_lapis_pay_group():
    """Return a `pay_group` dict with `lapis` in place of `silver`."""
    pay_group = {}
    all_pays = {}
    all_pays.update(_LAPIS_COMMON_PAYS)
    all_pays.update(_LAPIS_PREMIUM_PAYS)
    all_pays.update(_LAPIS_INGOT_PAYS)
    for symbol, values in all_pays.items():
        for rng, value in zip(PAY_RANGES, values):
            pay_group[(rng, symbol)] = value
    return pay_group


# ---------------------------------------------------------------------------
# Reproducibility helpers
# ---------------------------------------------------------------------------

def build_lapis_strips():
    """Return (base_strip, free_strip) for the Lapis config."""
    base = build_lapis_strip(BASE_SEED, BASE_COUNTS)
    free = build_lapis_strip(FREE_SEED, FREE_COUNTS)
    return base, free


def sha256():
    """Return (base_sha, free_sha) for the Lapis strips."""
    base, free = build_lapis_strips()
    return sha256_strip(base), sha256_strip(free)


def build_config() -> GameConfig:
    """Return a fresh GameConfig for the Lapis config.

    Reuses the §3.1 baseline bet modes, wincap, triggers; replaces the reel
    strips with the lapis strips and the paytable with the lapis paytable
    (silver -> lapis). The ore-vein rule/target are set to the DEV
    `create-cluster` / `diamond`. This does NOT change `game_config.py`.
    """
    from calibrate import make_config  # DEV harness; resets the singleton

    config = make_config(PAY_SCALE)
    # Rename `silver` -> `lapis` in the paytable (same values).
    config.paytable = {
        (size, ("lapis" if sym == "silver" else sym)): val
        for (size, sym), val in config.paytable.items()
    }
    base, free = build_lapis_strips()
    config.reels = {
        "BR0": [base] * config.num_reels,
        "FR0": [free] * config.num_reels,
    }
    config.ore_vein_rule = ORE_VEIN_RULE
    config.ore_vein_target = ORE_VEIN_TARGET
    return config


# SHA-256 fingerprints of the generated strips (deterministic). Computed by
# running this module; see __main__ below.
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
    print(f"base strip sha256: {bs}")
    print(f"free strip sha256: {fs}")
    print("Lapis strips reproducible (length 200, counts + SHA-256 match)")
