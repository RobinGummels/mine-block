"""Block Cave Stage-3 variant configuration (DEV, unpublished).

This is a SEPARATE, clearly-labelled variant config. It does NOT modify the
validated §3.1 baseline in `game_config.py`; the baseline remains reproducible
and unchanged.

Stage-3 variant design (see MATH_DESIGN.md and COMPARISON_REPORT.md):
  * pickaxe=4 (baseline 3) by reducing `silver` (BASE_COUNTS sum stays 200),
    which raises the natural 3+ pickaxe free-spin ENTRY rate.
  * Ore-vein upgrade uses the DEV `create-cluster` rule (target `diamond`) so
    that the upgrade makes a POSITIVE RTP contribution (the §3.1 baseline rule
    is negative, ~-1.2pp). The rule is applied via `config.ore_vein_rule` /
    `config.ore_vein_target`; the shipped `game_config.py` default stays
    `baseline`/`diamond`.
  * The free-spin strip is retuned (lower premium / ore-vein counts) so that,
    combined with the higher entry rate, the overall natural RTP lands inside
    the 96.0-96.7% Engine band while keeping short free spins (8/12/16/16),
    visible hit ~70% and full-return ~29%.

DEV measurement only - NOT a production RTP claim. Nothing here is published or
deployed. All numbers are DEV measurements on the current prototype.
"""

from __future__ import annotations

from game_config import GameConfig, build_strip, sha256_strip

# ---------------------------------------------------------------------------
# Variant identity
# ---------------------------------------------------------------------------

VARIANT_NAME = "Block Cave Stage-3 variant (pick=4 / create-cluster)"
VARIANT_DESCRIPTION = (
    "pick=4 free-spin entry boost + create-cluster ore-vein rule (positive "
    "ore-vein RTP contribution) with a retuned free-spin strip."
)

# ---------------------------------------------------------------------------
# Strips (deterministic; see build_strip in game_config.py)
# ---------------------------------------------------------------------------

# Base strip: pickaxe 4 (baseline 3), reducing `silver` to keep length 200.
BASE_COUNTS = {
    "earth": 36, "stone": 33, "timber": 31, "copper": 30,
    "silver": 15, "gold": 14, "emerald": 12, "diamond": 10,
    "ingot": 7, "ore_vein": 8, "pickaxe": 4,
}

# Free-spin strip: retuned so the feature payout + entry gives RTP in band.
FREE_COUNTS = {
    "earth": 42, "stone": 38, "timber": 36, "copper": 32,
    "silver": 15, "gold": 14, "emerald": 12, "diamond": 4,
    "ingot": 2, "ore_vein": 2, "pickaxe": 3,
}

BASE_SEED = 20261131
FREE_SEED = 20261118

# Ore-vein upgrade (DEV rule; default in game_config.py stays `baseline`).
ORE_VEIN_RULE = "create-cluster"
ORE_VEIN_TARGET = "diamond"

# Payout scale is 1.0 (the §3.1 calibrated paytable, unchanged).
PAY_SCALE = 1.0

# SHA-256 fingerprints of the generated strips (deterministic).
BASE_SHA = "428854a3b18ff3683bfb0b14126672f173f3520a762564f098a305fed4d60277"
FREE_SHA = "aa0002abdcdfda251db2dbe363b1b2d98c5badbbd946a039961af130f96cc9ce"


def build_strips():
    """Return (base_strip, free_strip) for the variant."""
    base = build_strip(BASE_SEED, BASE_COUNTS)
    free = build_strip(FREE_SEED, FREE_COUNTS)
    return base, free


def sha256():
    """Return (base_sha, free_sha) for the variant strips."""
    base, free = build_strips()
    return sha256_strip(base), sha256_strip(free)


def build_config() -> GameConfig:
    """Return a fresh GameConfig for the variant.

    Reuses the §3.1 baseline bet modes, wincap, triggers and paytable; only the
    reel strips and the ore-vein rule/target are replaced. The GameConfig
    singleton is reset so each call returns an independent config. This does NOT
    change `game_config.py`.
    """
    from calibrate import make_config  # DEV harness; resets the singleton

    config = make_config(PAY_SCALE)
    base, free = build_strips()
    config.reels = {
        "BR0": [base] * config.num_reels,
        "FR0": [free] * config.num_reels,
    }
    config.ore_vein_rule = ORE_VEIN_RULE
    config.ore_vein_target = ORE_VEIN_TARGET
    return config


if __name__ == "__main__":
    base, free = build_strips()
    bs, fs = sha256()
    assert len(base) == 200 and len(free) == 200
    assert all(base.count(s) == c for s, c in BASE_COUNTS.items())
    assert all(free.count(s) == c for s, c in FREE_COUNTS.items())
    assert bs == BASE_SHA, bs
    assert fs == FREE_SHA, fs
    print(f"base strip sha256: {bs}")
    print(f"free strip sha256: {fs}")
    print("variant strips reproducible (length 200, counts + SHA-256 match)")
