"""Block Cave Stage-3 Candidate 2 configuration (DEV, unpublished).

This is a SEPARATE, clearly-labelled DEV candidate config. It does NOT modify
the validated §3.1 baseline in `game_config.py`, nor the Stage-3 variant in
`variant_config.py`; both remain reproducible and unchanged.

Candidate 2 design (see MATH_DESIGN.md and CANDIDATE2_REPORT.md):
  * Base strip **H4** with pickaxe=4 (baseline 3) so the natural 3+ pickaxe
    free-spin ENTRY rate lands ≈1.5-1.7% (the 1% target is not reachable with
    integer pickaxe counts: pick=3 gives ≈0.7%, pick=4 gives ≈1.5-1.7%).
  * Ore-vein upgrade uses the DEV `create-cluster` rule (target `diamond`) so
    that the upgrade makes a POSITIVE RTP contribution (the §3.1 baseline rule
    is negative, ≈-1.2 pp). The rule is applied via `config.ore_vein_rule` /
    `config.ore_vein_target`; the shipped `game_config.py` default stays
    `baseline`/`diamond`.
  * Free-spin strip **F5** is tuned so that, combined with the higher entry
    rate, the overall natural RTP lands inside the 96.0-96.7% Engine band while
    keeping short free spins (8/12/16/16, retrigger cap 60), visible hit ≈45%,
    full-return ≈15-19% and a meaningful tail (occasional ≥100x, top win well
    above common pays).

DEV measurement only - NOT a production RTP claim. Nothing here is published or
deployed. All numbers are DEV measurements on the current prototype.
"""

from __future__ import annotations

from game_config import GameConfig, build_strip, sha256_strip

# ---------------------------------------------------------------------------
# Candidate 2 identity
# ---------------------------------------------------------------------------

VARIANT_NAME = "Block Cave Stage-3 Candidate 2 (pick=4 / create-cluster)"
VARIANT_DESCRIPTION = (
    "pick=4 free-spin entry boost + create-cluster ore-vein rule (positive "
    "ore-vein RTP contribution) with an F5-tuned free-spin strip."
)

# ---------------------------------------------------------------------------
# Strips (deterministic; see build_strip in game_config.py)
# ---------------------------------------------------------------------------

# Base strip (H4): pickaxe 4 (baseline 3) so natural entry ≈1.5-1.7%. The count
# is redistributed across commons/premiums so the strip still sums to 200 and
# holds visible hit ≈45% and full-return ≈15-19%.
BASE_COUNTS = {
    "earth": 28, "stone": 26, "timber": 24, "copper": 22,
    "silver": 20, "gold": 20, "emerald": 19, "diamond": 17,
    "ingot": 11, "ore_vein": 9, "pickaxe": 4,
}

# Free strip (F5): a small premium boost over the baseline FREE_COUNTS so the
# forced free-game payout mean lands ≈10.0-10.7x (inside the 8-12x band) while
# total natural RTP stays in band.
FREE_COUNTS = {
    "earth": 29, "stone": 27, "timber": 25, "copper": 23,
    "silver": 18, "gold": 18, "emerald": 14, "diamond": 13,
    "ingot": 15, "ore_vein": 15, "pickaxe": 3,
}

BASE_SEED = 20261103
FREE_SEED = 20261118

# Ore-vein upgrade (DEV rule; default in game_config.py stays `baseline`).
ORE_VEIN_RULE = "create-cluster"
ORE_VEIN_TARGET = "diamond"

# Payout scale is 1.0 (the §3.1 calibrated paytable, unchanged).
PAY_SCALE = 1.0

# SHA-256 fingerprints of the generated strips (deterministic).
BASE_SHA = "7a9fe8ec9e9c1f9f05a59de5ce1149e21b1ba5dab34fa794a147ad6f1f83d425"
FREE_SHA = "48e1ea8cb7de20454be0fc1b5cf2064da5cf4709b878d06783c5dfb1c7015096"


def build_strips():
    """Return (base_strip, free_strip) for Candidate 2."""
    base = build_strip(BASE_SEED, BASE_COUNTS)
    free = build_strip(FREE_SEED, FREE_COUNTS)
    return base, free


def sha256():
    """Return (base_sha, free_sha) for the Candidate 2 strips."""
    base, free = build_strips()
    return sha256_strip(base), sha256_strip(free)


def build_config() -> GameConfig:
    """Return a fresh GameConfig for Candidate 2.

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
    print("Candidate 2 strips reproducible (length 200, counts + SHA-256 match)")
