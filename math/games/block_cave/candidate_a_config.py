"""Block Cave Stage-3 Candidate A configuration (DEV, unpublished).

This is a SEPARATE, clearly-labelled DEV candidate config. It does NOT modify
the validated §3.1 baseline in `game_config.py`, nor the Stage-3 variant in
`variant_config.py`; both remain reproducible and unchanged.

Candidate A design (see MATH_DESIGN.md and CANDIDATES_REPORT.md):
  * Base strip **E4**: keeps the §3.1 pickaxe=3 (so the natural 3+ pickaxe
    free-spin ENTRY rate stays ≈0.67%) and the same count of the `ore_vein`
    wild (8) that drives the cascade/wild RTP step function, but shifts the
    premium distribution (diamond 10→8, ingot 7→9) so the base contributes a
    slightly lower share. This is what pulls the natural RTP back into the
    96.0-96.7% Engine band after switching to a positive ore-vein rule.
  * Ore-vein upgrade uses the DEV `create-cluster` rule (target `diamond`) so
    that the upgrade makes a POSITIVE RTP contribution (the §3.1 baseline rule
    is negative, ≈-1.2 pp). The rule is applied via `config.ore_vein_rule` /
    `config.ore_vein_target`; the shipped `game_config.py` default stays
    `baseline`/`diamond`.
  * Free-spin strip **G6** is tuned so that the free-spin feature payout mean
    lands ≈8.3x (inside the 8-12x band) while keeping short free spins
    (8/12/16/16, retrigger cap 60) and a high visible hit (≈70%).
  * PRIORITY is HIGH visible hit (≈70%) and LOW dry streaks; the 45% hit /
    15% full-return §3.3 targets are explicitly relaxed. The natural free-spin
    ENTRY rate is ≈0.67% (the 1% target is not reachable with integer pickaxe
    counts: pick=3 gives ≈0.67%, pick=4 gives ≈1.5-1.7%).

DEV measurement only - NOT a production RTP claim. Nothing here is published or
deployed. All numbers are DEV measurements on the current prototype.
"""

from __future__ import annotations

from game_config import GameConfig, build_strip, sha256_strip

# ---------------------------------------------------------------------------
# Candidate A identity
# ---------------------------------------------------------------------------

VARIANT_NAME = "Block Cave Stage-3 Candidate A (create-cluster / high-hit)"
VARIANT_DESCRIPTION = (
    "Positive create-cluster ore-vein rule (target diamond) with an E4 base "
    "strip and a G6 free-spin strip, tuned for a high visible hit (≈70%), low "
    "dry streaks and a natural RTP inside the 96.0-96.7% Engine band."
)

# ---------------------------------------------------------------------------
# Strips (deterministic; see build_strip in game_config.py)
# ---------------------------------------------------------------------------

# Base strip (E4): pickaxe=3 and ore_vein=8 (unchanged from §3.1) so the
# cascade/wild RTP step function and the ≈0.67% entry rate are preserved. The
# premium distribution is rebalanced (diamond 10->8, ingot 7->9) so the base
# contributes a slightly lower share once the positive ore-vein rule is applied.
BASE_COUNTS = {
    "earth": 36, "stone": 33, "timber": 31, "copper": 30,
    "silver": 16, "gold": 14, "emerald": 12, "diamond": 8,
    "ingot": 9, "ore_vein": 8, "pickaxe": 3,
}

# Free strip (G6): heavily common-weighted with a low ore_vein count. Because
# `create-cluster` upgrades ore_vein -> diamond, a low free-strip ore_vein count
# is the main lever to bring the feature payout down to ≈8.3x (8-12x band).
FREE_COUNTS = {
    "earth": 42, "stone": 40, "timber": 38, "copper": 36,
    "silver": 8, "gold": 9, "emerald": 8, "diamond": 6,
    "ingot": 5, "ore_vein": 5, "pickaxe": 3,
}

BASE_SEED = 20261117
FREE_SEED = 20261118

# Ore-vein upgrade (DEV rule; default in game_config.py stays `baseline`).
ORE_VEIN_RULE = "create-cluster"
ORE_VEIN_TARGET = "diamond"

# Payout scale is 1.0 (the §3.1 calibrated paytable, unchanged).
PAY_SCALE = 1.0

# SHA-256 fingerprints of the generated strips (deterministic).
BASE_SHA = "33e6f349c3e968cba7f5e0839196bfc165cafc8f894ba8e5e188ea3b17a463c5"
FREE_SHA = "12096d9f52e6c60286e3d2842e06de8e79e0b2771ce5db6ec4e452e06c440687"


def build_strips():
    """Return (base_strip, free_strip) for Candidate A."""
    base = build_strip(BASE_SEED, BASE_COUNTS)
    free = build_strip(FREE_SEED, FREE_COUNTS)
    return base, free


def sha256():
    """Return (base_sha, free_sha) for the Candidate A strips."""
    base, free = build_strips()
    return sha256_strip(base), sha256_strip(free)


def build_config() -> GameConfig:
    """Return a fresh GameConfig for Candidate A.

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
    print("Candidate A strips reproducible (length 200, counts + SHA-256 match)")
