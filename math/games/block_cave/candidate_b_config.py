"""Block Cave Stage-3 Candidate B configuration (DEV, unpublished).

This is a SEPARATE, clearly-labelled DEV candidate config. It does NOT modify
the validated §3.1 baseline in `game_config.py`, nor the Stage-3 variant in
`variant_config.py`; both remain reproducible and unchanged.

Candidate B design (see MATH_DESIGN.md and CANDIDATES_REPORT.md):
  * Base strip **S6** with Silver Ore REMOVED (silver=0). The 16 silver count is
    redistributed (mostly into gold/emerald/diamond/ingot premiums plus a small
    earth bump) so the strip still sums to 200. This evaluates whether removing
    the low-RTP silver symbol helps the design.
  * Ore-vein upgrade uses the DEV `create-cluster` rule (target `diamond`),
    applied via `config.ore_vein_rule` / `config.ore_vein_target`.
  * Free-spin strip **G6** is UNCHANGED from Candidate A so the base-strip
    silver-removal effect is isolated for comparison.
  * PRIORITY is HIGH visible hit (≈70%) and LOW dry streaks; the 45% hit /
    15% full-return §3.3 targets are explicitly relaxed.

SILVER-REMOVAL NOTICE: Under the positive `create-cluster` rule, removing Silver
Ore makes the base RTP bimodal/chaotic (the `ore_vein` wild count and the premium
composition drive a sharp RTP step function). Small nearby rebalances swing the
silver-removed base RTP from ≈0.79 to ≈1.16. Candidate B (S6) is the composition
that lands INSIDE the 96.0-96.7% Engine band on a fresh out-of-sample range
(RTP ≈0.964), but at a slightly LOWER visible hit (≈0.68 vs ≈0.70 for Candidate
A) and with NO meaningful ≥100× tail (max ≈59×, P(≥100×)=0 vs Candidate A max
≈425×). Silver removal is therefore achievable but is a PROFILE TRADE (stronger
positive ore-vein Δ ≈+0.28 pp, but less hit and no tail), not a strict
improvement. See CANDIDATES_REPORT.md.

DEV measurement only - NOT a production RTP claim. Nothing here is published or
deployed. All numbers are DEV measurements on the current prototype.
"""

from __future__ import annotations

from game_config import GameConfig, build_strip, sha256_strip

# ---------------------------------------------------------------------------
# Candidate B identity
# ---------------------------------------------------------------------------

VARIANT_NAME = "Block Cave Stage-3 Candidate B (silver-removed / create-cluster)"
VARIANT_DESCRIPTION = (
    "Silver-removed base strip (S6) + positive create-cluster ore-vein rule "
    "(target diamond) with the Candidate A G6 free-spin strip. Evaluates the "
    "silver-removal effect: lands in the RTP band OOS but trades hit/tail for a "
    "stronger positive ore-vein contribution."
)

# ---------------------------------------------------------------------------
# Strips (deterministic; see build_strip in game_config.py)
# ---------------------------------------------------------------------------

# Base strip (S6): silver removed (0) and redistributed across premiums + a
# small earth bump, summing to 200. ore_vein=6 to keep the wild-driven RTP from
# overshooting above 1.0, though the base RTP is chaotic under create-cluster.
BASE_COUNTS = {
    "earth": 37, "stone": 32, "timber": 30, "copper": 29,
    "silver": 0, "gold": 20, "emerald": 16, "diamond": 14,
    "ingot": 13, "ore_vein": 6, "pickaxe": 3,
}

# Free strip (G6): identical to Candidate A so the silver-removal effect on the
# base strip is isolated in the comparison.
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
BASE_SHA = "2295935d58a132ae6fc56d5569b4dcd5742379d3be597d84034999826f763f27"
FREE_SHA = "12096d9f52e6c60286e3d2842e06de8e79e0b2771ce5db6ec4e452e06c440687"


def build_strips():
    """Return (base_strip, free_strip) for Candidate B."""
    base = build_strip(BASE_SEED, BASE_COUNTS)
    free = build_strip(FREE_SEED, FREE_COUNTS)
    return base, free


def sha256():
    """Return (base_sha, free_sha) for the Candidate B strips."""
    base, free = build_strips()
    return sha256_strip(base), sha256_strip(free)


def build_config() -> GameConfig:
    """Return a fresh GameConfig for Candidate B.

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
    print("Candidate B strips reproducible (length 200, counts + SHA-256 match)")
