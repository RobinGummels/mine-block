"""Block Cave game configuration file/setup.

Implements the deterministic reel strips defined in MATH_DESIGN.md §4.1/§4.2
(the authoritative Python block there) and the paytable from §3.1.
"""

import hashlib
import random

from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode

# ---------------------------------------------------------------------------
# Deterministic strip generation (MATH_DESIGN.md §4.1, authoritative code block)
# ---------------------------------------------------------------------------

# Fixed symbol orders (make the procedure unambiguous).
COMMON_ORDER = ["earth", "stone", "timber", "copper"]
NONCOMMON_ORDER = ["silver", "gold", "emerald", "diamond", "ingot", "ore_vein", "pickaxe"]

# Weight-table counts (Section 4.1 base and Section 4.2 free-spin).
BASE_COUNTS = {
    "earth": 36, "stone": 33, "timber": 31, "copper": 30,
    "silver": 16, "gold": 14, "emerald": 12, "diamond": 10,
    "ingot": 7, "ore_vein": 8, "pickaxe": 3,
}
FREE_COUNTS = {
    "earth": 30, "stone": 28, "timber": 26, "copper": 24,
    "silver": 18, "gold": 16, "emerald": 14, "diamond": 12,
    "ingot": 14, "ore_vein": 15, "pickaxe": 3,
}


def build_strip(seed, counts):
    """Return a length-200 strip whose symbol counts equal `counts`.

    Deterministic: every call with the same (seed, counts) returns the same
    list. `random.Random(seed)` is the only source of randomness.
    """
    rng = random.Random(seed)

    # 1. Common symbols -> runs of 2, one single if the count is odd, in
    #    COMMON_ORDER. (64 pairs + 2 singles = 66 runs for the base counts.)
    runs = []
    for sym in COMMON_ORDER:
        c = counts[sym]
        runs.extend([[sym, sym]] * (c // 2))
        if c % 2 == 1:
            runs.append([sym])

    # 2. Non-common symbols -> individual singles, in NONCOMMON_ORDER.
    singles = []
    for sym in NONCOMMON_ORDER:
        singles.extend([sym] * counts[sym])

    # 3. len(runs)+1 gap buckets; place each single, in NONCOMMON_ORDER, into
    #    a uniformly random bucket index.
    buckets = [[] for _ in range(len(runs) + 1)]
    for s in singles:
        buckets[rng.randrange(len(buckets))].append(s)

    # 4. Shuffle the run order (shuffle a list of indices, then index).
    order = list(range(len(runs)))
    rng.shuffle(order)

    # 5. Concatenate: for each run in shuffled order, the run then the singles
    #    in that run's gap bucket; then the last bucket's singles.
    strip = []
    for idx in order:
        strip.extend(runs[idx])
        strip.extend(buckets[idx])
    strip.extend(buckets[len(runs)])
    return strip


def sha256_strip(strip):
    return hashlib.sha256(",".join(strip).encode("utf-8")).hexdigest()


# Cluster-size ranges, in ascending order (MATH_DESIGN.md §3.1).
PAY_RANGES = [(5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10), (11, 14), (15, 19), (20, 30)]

# Paytable values (multiples of the play amount) per symbol, one entry per
# PAY_RANGES index. Rows follow the design tables in §3.1. These are the
# MATH_DESIGN §3.1 values at scale 1.0 — the calibrated paytable.
#
# Stage 3 calibration (C3): the earlier Stage-3 revision (C2) scaled every value
# by `F = 1.8382663803148458` (derived from a stale `calib_pre` RTP of 0.524).
# That scale-up is WRONG and was REVERTED here: the MATH_DESIGN §3.1 paytable
# at scale 1.0 measures a natural base-game RTP of ~0.964, already inside the
# 96.0–96.7% Engine band, whereas the ×F scale-up over-pays at ~1.76. See
# CALIBRATION_REPORT.md. The reel strips, symbol weights/counts and the
# ore-vein rule are unchanged (their SHA-256 fingerprints and seeds are
# identical to the Stage 2 revision).
_COMMON_PAYS = {
    "earth": [0.18, 0.28, 0.46, 0.74, 1.10, 1.65, 2.76, 4.60, 7.35],
    "stone": [0.22, 0.33, 0.55, 0.92, 1.38, 2.02, 3.31, 5.51, 9.19],
    "timber": [0.26, 0.40, 0.66, 1.10, 1.65, 2.57, 4.23, 6.99, 11.03],
    "copper": [0.29, 0.48, 0.77, 1.29, 2.02, 3.13, 5.15, 8.27, 13.79],
}
_PREMIUM_PAYS = {
    "silver": [0.55, 0.92, 1.47, 2.39, 3.68, 5.51, 9.19, 14.71, 23.90],
    "gold": [0.92, 1.47, 2.39, 3.68, 5.88, 9.19, 14.71, 23.90, 36.77],
    "emerald": [1.47, 2.39, 4.04, 6.43, 10.11, 14.71, 23.90, 36.77, 58.82],
    "diamond": [2.21, 3.68, 6.43, 10.11, 15.63, 22.98, 36.77, 58.82, 91.91],
}
_INGOT_PAYS = {
    "ingot": [5.51, 9.19, 14.71, 23.90, 36.77, 55.15, 91.91, 147.06, 229.78],
}


def build_pay_group():
    """Return a `pay_group` dict suitable for `Config.convert_range_table`."""
    pay_group = {}
    all_pays = {}
    all_pays.update(_COMMON_PAYS)
    all_pays.update(_PREMIUM_PAYS)
    all_pays.update(_INGOT_PAYS)
    for symbol, values in all_pays.items():
        for rng, value in zip(PAY_RANGES, values):
            pay_group[(rng, symbol)] = value
    return pay_group


class GameConfig(Config):
    """Singleton Block Cave game configuration class."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "block_cave"
        self.provider_number = 0
        self.working_name = "Block Cave"
        self.wincap = 1000.0
        self.win_type = "cluster"
        self.rtp = 0.963  # design target; do NOT claim as measured
        # Variant P gate: when True (set by a DEV variant config), ore veins
        # persist across a free-spin series. DEFAULTS OFF so the validated
        # §3.1 game, and every existing config, behaves exactly as before.
        self.ore_vein_persist_freespins = False
        self.construct_paths()

        # Game dimensions
        self.num_reels = 6
        self.num_rows = [5] * self.num_reels
        self.include_padding = True

        self.special_symbols = {"wild": ["ore_vein"], "scatter": ["pickaxe"]}

        # Paytable (MATH_DESIGN.md §3.1)
        self.paytable = self.convert_range_table(build_pay_group())

        # Free-spin trigger scaling (MATH_DESIGN.md §6.3): 3/4/5/6+ -> 8/12/16/16
        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 12, 5: 16, 6: 16},
            self.freegame_type: {3: 8, 4: 12, 5: 16, 6: 16},
        }
        self.anticipation_triggers = {
            self.basegame_type: 2,
            self.freegame_type: 2,
        }

        # Reels: a single shared strip read across all 6 reels.
        base_strip = build_strip(20261117, BASE_COUNTS)
        free_strip = build_strip(20261118, FREE_COUNTS)
        self.reels = {
            "BR0": [base_strip] * self.num_reels,
            "FR0": [free_strip] * self.num_reels,
        }

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=1000,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    # NOTE: the `wincap` criteria distribution was removed. It
                    # set win_criteria=1000.0, which is essentially unreachable
                    # on the design strips (MATH_DESIGN.md §7), and `force_wincap`
                    # is never consumed by the engine's repeat-until-criteria loop
                    # (`check_repeat` only checks `win_criteria`/`force_freegame`).
                    # Any harness driving it through `create_books` would loop
                    # forever. The 1,000x cap mechanism itself is unchanged and is
                    # exercised deterministically in `test_block_cave.py`.
                    #
                    # Quotas are relative weights: the engine normalizes them by
                    # their sum at runtime (`run_sims.py`). The surviving quotas
                    # below are re-normalized to sum to 1.0 so they read as a
                    # proper distribution, preserving the original 0.6:0.2:0.15
                    # ratio among the remaining criteria (the removed wincap
                    # 5% share was redistributed proportionally).
                    Distribution(
                        criteria="basegame",
                        quota=0.6316,
                        win_criteria=None,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.2105,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {3: 10},
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.1579,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
        ]
