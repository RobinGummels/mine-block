"""Block Cave Stage 3 math calibration harness (DEV measurement only).

This module runs the Block Cave engine over:

* **Natural base rounds**  (`criteria="basegame"`, `betmode="base"`, no forcing)
  — the ONLY basis for round RTP, standard deviation, visible hit, full
  return, dry-streak behaviour and the free-spin **entry rate**.
* **Deliberately-generated freegame rounds** (`criteria="freegame"` with
  `force_freegame=True`) — used ONLY to measure the free-spin feature's
  *internal* distribution (duration, payout, tails) with many samples. These
  are explicitly labelled as generated books and are NOT used for round RTP or
  entry rate.

It reports the Stage 3 metrics in a machine-readable JSON report and a
human-readable summary. It is deterministic: the same seed range always
produces the same numbers.

This is **NOT a production certification** and makes **no RTP claim** for a
published game. All output is DEV measurement on the current (unpublished)
Block Cave prototype.

Run from anywhere, e.g.:

    & "C:\\Users\\robin\\Documents\\stake\\stake-game-ai\\math\\.venv\\Scripts\\python.exe" \
        math\\games\\block_cave\\calibrate.py --natural 1000 --freegame 1000 --out .runtime\\block_cave\\calib.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent          # math/games/block_cave
MATH_DIR = HERE.parents[1]                       # math
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(MATH_DIR))

import game_config as gc                        # noqa: E402
from game_config import GameConfig, BASE_COUNTS, FREE_COUNTS, build_strip, sha256_strip  # noqa: E402
from gamestate import GameState                 # noqa: E402
from game_executables import GameExecutables    # noqa: E402

WINCAP_MULT = 1000.0
WINCAP_UNITS = 100000

_ORIG_BUILD_PAY_GROUP = gc.build_pay_group
_ORIG_ORE_VEIN = GameExecutables.process_ore_vein_upgrades


def set_ore_vein_enabled(enabled: bool) -> None:
    """Enable/disable the ore-vein upgrade step (measurement only).

    When disabled, `process_ore_vein_upgrades` is replaced with a no-op so a
    comparison run can isolate the RTP contribution of the ore-vein upgrade.
    This is a DEV measurement hook only; it does not change `game_config.py` or
    the shipped engine.
    """
    if enabled:
        GameExecutables.process_ore_vein_upgrades = _ORIG_ORE_VEIN
    else:
        def _noop(self):
            pass
        GameExecutables.process_ore_vein_upgrades = _noop


class CalibrateState(GameState):
    """Measurement subclass that skips in-memory library accumulation.

    `imprint_wins` is a no-op so that running hundreds of thousands of spins
    does not grow the in-memory library (which would otherwise hold one JSON
    string per book). The authoritative book is still built and read directly
    via `state.book.to_json()` after each spin.
    """

    def imprint_wins(self):
        pass


def make_config(pay_scale: float = 1.0) -> GameConfig:
    """Build a fresh GameConfig, optionally scaling the paytable.

    `pay_scale` multiplies every paytable value and rounds to 2 decimal
    places. It is used only for calibration experiments (finding the scale
    factor); the checked-in `game_config.py` holds the final values.
    """
    gc.GameConfig._instance = None
    if abs(pay_scale - 1.0) < 1e-12:
        gc.build_pay_group = _ORIG_BUILD_PAY_GROUP
    else:
        orig = _ORIG_BUILD_PAY_GROUP

        def scaled_build():
            pg = orig()
            return {k: round(v * pay_scale, 2) for k, v in pg.items()}

        gc.build_pay_group = scaled_build
    return gc.GameConfig()


# ---------------------------------------------------------------------------
# Book-level consistency checks
# ---------------------------------------------------------------------------

def check_book(book: dict) -> list:
    """Return a list of consistency-violation strings for one book.

    Checks (MATH_DESIGN.md §7 / ENGINE_CONTRACT.md):
    - `payoutMultiplier` is an integer in [0, 100000].
    - event `index` values are contiguous starting at 0.
    - the first event is `reveal`.
    - `finalWin.amount == payoutMultiplier`.
    - `int(round(min(baseGameWins+freeGameWins, 1000.0)*100, 0)) == payoutMultiplier`.
    - `baseGameWins` / `freeGameWins` are non-negative.
    """
    violations = []
    pm = book.get("payoutMultiplier")
    if not isinstance(pm, int):
        violations.append(f"payoutMultiplier not int: {pm!r}")
    elif not (0 <= pm <= WINCAP_UNITS):
        violations.append(f"payoutMultiplier out of [0,100000]: {pm}")

    events = book.get("events", [])
    for i, e in enumerate(events):
        if e.get("index") != i:
            violations.append(f"event index not contiguous at {i}: {e.get('index')}")
            break
    if not events:
        violations.append("no events")
    elif events[0].get("type") != "reveal":
        violations.append(f"first event not reveal: {events[0].get('type')}")

    final_amt = [e.get("amount") for e in events if e.get("type") == "finalWin"]
    if not final_amt:
        violations.append("no finalWin event")
    elif final_amt[-1] != pm:
        violations.append(f"finalWin {final_amt[-1]} != payoutMultiplier {pm}")

    base = book.get("baseGameWins", 0.0)
    free = book.get("freeGameWins", 0.0)
    if base < 0 or free < 0:
        violations.append(f"negative wins base={base} free={free}")
    expected = int(round(min(base + free, WINCAP_MULT) * 100, 0))
    if expected != pm:
        violations.append(
            f"base+free sum-then-cap {expected} != payoutMultiplier {pm} "
            f"(base={base}, free={free})"
        )
    return violations


# ---------------------------------------------------------------------------
# Dry-streak statistics
# ---------------------------------------------------------------------------

def dry_streak_stats(hit: np.ndarray, hit_rate: float) -> dict:
    """Run-length statistics on the zero/one payout sequence.

    `hit[i]` is 1 if round i pays > 0, else 0.
    Returns the observed fraction of all-zero sliding windows of length 10 and
    20, the theoretical `(1-hit_rate)^L`, the maximal zero-run length, and the
    count of maximal zero-runs of length >= 10 and >= 20.
    """
    n = len(hit)
    p_zero = 1.0 - hit_rate

    def window_zero_fraction(length: int) -> float:
        if n < length:
            return 0.0
        csum = np.concatenate(([0], np.cumsum(hit)))
        # count windows whose sum is 0
        zero_windows = 0
        for i in range(n - length + 1):
            if csum[i + length] - csum[i] == 0:
                zero_windows += 1
        return zero_windows / (n - length + 1)

    # Maximal zero-run length distribution
    runs = []
    cur = 0
    for h in hit:
        if h == 0:
            cur += 1
        else:
            if cur:
                runs.append(cur)
                cur = 0
    if cur:
        runs.append(cur)

    runs_arr = np.array(runs, dtype=np.int64) if runs else np.array([], dtype=np.int64)
    max_run = int(runs_arr.max()) if runs_arr.size else 0
    count_ge_10 = int((runs_arr >= 10).sum()) if runs_arr.size else 0
    count_ge_20 = int((runs_arr >= 20).sum()) if runs_arr.size else 0

    return {
        "sample_size": n,
        "hit_rate": hit_rate,
        "p_zero_single": p_zero,
        "obs_zero_window_10": window_zero_fraction(10),
        "obs_zero_window_20": window_zero_fraction(20),
        "theoretical_zero_window_10": p_zero ** 10,
        "theoretical_zero_window_20": p_zero ** 20,
        "max_zero_run": max_run,
        "num_zero_runs_ge_10": count_ge_10,
        "num_zero_runs_ge_20": count_ge_20,
        "num_zero_runs_total": int(runs_arr.size),
        # run-length histogram: length -> count (most common first)
        "zero_run_length_histogram": {
            str(int(k)): int(v)
            for k, v in sorted(
                zip(*np.unique(runs_arr, return_counts=True)), key=lambda kv: -kv[1]
            )
        },
    }


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def mean_ci(values: np.ndarray) -> dict:
    """Mean and a 95% normal-approximation CI of a sample."""
    n = values.size
    if n == 0:
        return {"mean": None, "se": None, "ci95": [None, None], "n": 0}
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(n)) if n > 1 else 0.0
    return {
        "mean": mean,
        "se": se,
        "ci95": [mean - 1.96 * se, mean + 1.96 * se],
        "n": int(n),
    }


def proportion_ci(k: int, n: int) -> dict:
    """Proportion with 95% CI (normal approx + Wilson)."""
    if n == 0:
        return {"p": None, "se": None, "ci95": [None, None], "wilson95": [None, None], "k": 0, "n": 0}
    p = k / n
    se = math.sqrt(p * (1 - p) / n)
    z = 1.96
    # Wilson score interval
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt((p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return {
        "p": p,
        "se": se,
        "ci95": [p - z * se, p + z * se],
        "wilson95": [centre - half, centre + half],
        "k": int(k),
        "n": int(n),
    }


def percentile_summary(values: np.ndarray) -> dict:
    """Payout percentile summary in multiplier units (not ×100)."""
    if values.size == 0:
        return {}
    out = {}
    for p in (50, 90, 99, 99.9):
        out[f"p{p}"] = float(np.percentile(values, p))
    out["max"] = float(values.max())
    out["mean"] = float(values.mean())
    out["median"] = float(np.median(values))
    return out


# ---------------------------------------------------------------------------
# Measurement run
# ---------------------------------------------------------------------------

class Measurer:
    """Streaming accumulator that processes books one at a time.

    Keeps only the numeric arrays needed for the metrics, plus small counters,
    so that 500k+ rounds do not blow up memory. Each book is still fully
    consistency-checked as it is processed.
    """

    def __init__(self, label: str):
        self.label = label
        self.payouts = []        # round payout multiplier (e.g. 0.49)
        self.base_wins = []      # baseGameWins (multiplier units)
        self.free_wins = []      # freeGameWins (multiplier units)
        self.hit = []            # 1 if payout>0 else 0
        self.feature_flags = []  # 1 if round had a freeSpinTrigger else 0
        self.feature_spins = []  # free-spin count per feature (only when feature)
        self.feature_payout = []  # freeGameWins per feature (only when feature)
        self.wincap_binds = 0
        self.consistency_violations = 0
        self.violation_examples = []
        self.n = 0

    def process(self, book: dict):
        self.n += 1
        viols = check_book(book)
        if viols:
            self.consistency_violations += 1
            if len(self.violation_examples) < 5:
                self.violation_examples.append({
                    "id": book.get("id"),
                    "criteria": book.get("criteria"),
                    "violations": viols,
                })

        pm = book["payoutMultiplier"]
        mult = pm / 100.0
        self.payouts.append(mult)
        self.base_wins.append(book["baseGameWins"])
        self.free_wins.append(book["freeGameWins"])
        self.hit.append(1 if pm > 0 else 0)

        events = book.get("events", [])
        has_feature = any(e.get("type") == "freeSpinTrigger" for e in events)
        self.feature_flags.append(1 if has_feature else 0)
        if has_feature:
            fs_count = sum(1 for e in events if e.get("type") == "updateFreeSpin")
            self.feature_spins.append(fs_count)
            self.feature_payout.append(book["freeGameWins"])
        if any(e.get("type") == "wincap" for e in events) or pm >= WINCAP_UNITS:
            self.wincap_binds += 1

    def summary(self, mode: str) -> dict:
        pay = np.array(self.payouts, dtype=np.float64)
        base = np.array(self.base_wins, dtype=np.float64)
        free = np.array(self.free_wins, dtype=np.float64)
        hit = np.array(self.hit, dtype=np.int64)
        n = self.n

        rtp = float(pay.mean()) if n else None
        std = float(pay.std(ddof=1)) if n > 1 else None
        hit_rate = float(hit.mean()) if n else None
        full_return = float((pay >= 1.0).mean()) if n else None
        base_rtp = float(base.mean()) if n else None
        feature_rtp = float(free.mean()) if n else None

        feature_flags = np.array(self.feature_flags, dtype=np.int64)
        entry_rate = proportion_ci(int(feature_flags.sum()), n) if n else None

        feature_spins = np.array(self.feature_spins, dtype=np.float64)
        feature_payout = np.array(self.feature_payout, dtype=np.float64)

        # Win tails (round payout multiplier)
        tails = percentile_summary(pay)
        tails["p_ge_100x"] = float((pay >= 100.0).mean()) if n else None
        tails["p_ge_500x"] = float((pay >= 500.0).mean()) if n else None
        tails["p_ge_1000x"] = float((pay >= 1000.0).mean()) if n else None
        # Proportion with BOTH a normal-approximation and a Wilson 95% CI.
        # `p_ge_100x` etc. are rare (≈1e-4), so the Wilson interval is the
        # honest uncertainty bound (the normal approx is poor near the tails).
        tails["p_ge_100x_ci"] = proportion_ci(int((pay >= 100.0).sum()), n) if n else None
        tails["p_ge_500x_ci"] = proportion_ci(int((pay >= 500.0).sum()), n) if n else None
        tails["p_ge_1000x_ci"] = proportion_ci(int((pay >= 1000.0).sum()), n) if n else None
        tails["wincap_bind_rate"] = (self.wincap_binds / n) if n else None
        tails["wincap_bind_count"] = self.wincap_binds

        summary = {
            "mode": mode,
            "label": self.label,
            "sample_size": n,
            "rtp": rtp,
            "rtp_std": std,
            "rtp_std_ci": mean_ci(pay)["ci95"],
            "base_rtp": base_rtp,
            "feature_rtp": feature_rtp,
            "visible_hit": hit_rate,
            "visible_hit_ci": proportion_ci(int((hit == 1).sum()), n)["ci95"],
            "full_return": full_return,
            "full_return_ci": proportion_ci(int((pay >= 1.0).sum()), n)["ci95"],
            "dry_streaks": dry_streak_stats(hit, hit_rate) if n else {},
            "feature_entry": entry_rate,
            "feature_duration": (
                {
                    "n_features": int(feature_spins.size),
                    "mean": float(feature_spins.mean()) if feature_spins.size else None,
                    "median": float(np.median(feature_spins)) if feature_spins.size else None,
                    "min": float(feature_spins.min()) if feature_spins.size else None,
                    "max": float(feature_spins.max()) if feature_spins.size else None,
                    "std": float(feature_spins.std(ddof=1)) if feature_spins.size > 1 else None,
                }
                if feature_spins.size
                else {}
            ),
            "feature_payout": (
                {
                    "n_features": int(feature_payout.size),
                    "mean": float(feature_payout.mean()) if feature_payout.size else None,
                    "median": float(np.median(feature_payout)) if feature_payout.size else None,
                    "std": float(feature_payout.std(ddof=1)) if feature_payout.size > 1 else None,
                    "min": float(feature_payout.min()) if feature_payout.size else None,
                    "max": float(feature_payout.max()) if feature_payout.size else None,
                    "p10": float(np.percentile(feature_payout, 10)) if feature_payout.size else None,
                    "p25": float(np.percentile(feature_payout, 25)) if feature_payout.size else None,
                    "p75": float(np.percentile(feature_payout, 75)) if feature_payout.size else None,
                    "p90": float(np.percentile(feature_payout, 90)) if feature_payout.size else None,
                    "p99": float(np.percentile(feature_payout, 99)) if feature_payout.size else None,
                }
                if feature_payout.size
                else {}
            ),
            "win_tails": tails,
            "consistency": {
                "books_checked": n,
                "violations": self.consistency_violations,
                "examples": self.violation_examples,
            },
        }
        return summary


def run_natural(state: CalibrateState, n: int, start_seed: int, label: str,
                progress: bool = True) -> Measurer:
    """Run `n` natural base rounds (criteria="basegame")."""
    m = Measurer(label)
    t0 = time.time()
    state.criteria = "basegame"
    for i in range(n):
        state.run_spin(start_seed + i)
        m.process(state.book.to_json())
        if progress and (i + 1) % 20000 == 0:
            print(f"    natural: {i+1}/{n} ({time.time()-t0:.1f}s)", flush=True)
    m.runtime_seconds = time.time() - t0
    return m


def run_forced_freegame(state: CalibrateState, n: int, start_seed: int, label: str,
                        progress: bool = True) -> Measurer:
    """Run `n` deliberately-generated freegame rounds (criteria="freegame")."""
    m = Measurer(label)
    t0 = time.time()
    state.criteria = "freegame"
    for i in range(n):
        state.run_spin(start_seed + i)
        m.process(state.book.to_json())
        if progress and (i + 1) % 10000 == 0:
            print(f"    freegame: {i+1}/{n} ({time.time()-t0:.1f}s)", flush=True)
    m.runtime_seconds = time.time() - t0
    return m


# ---------------------------------------------------------------------------
# Report writers
# ---------------------------------------------------------------------------

def strip_info() -> dict:
    base = build_strip(20261117, BASE_COUNTS)
    free = build_strip(20261118, FREE_COUNTS)
    return {
        "base_strip_seed": 20261117,
        "free_strip_seed": 20261118,
        "base_strip_sha256": sha256_strip(base),
        "free_strip_sha256": sha256_strip(free),
        "base_counts": BASE_COUNTS,
        "free_counts": FREE_COUNTS,
    }


def build_report(label: str, pay_scale: float, natural: Measurer, forced: Measurer,
                 runtime_seconds: float, ore_vein_enabled: bool = True) -> dict:
    return {
        "label": label,
        "pay_scale_applied": pay_scale,
        "ore_vein_enabled": ore_vein_enabled,
        "wincap_mult": WINCAP_MULT,
        "wincap_units": WINCAP_UNITS,
        "strip_info": strip_info(),
        "natural_base": natural.summary("natural_base"),
        "forced_freegame": forced.summary("forced_freegame"),
        "runtime_seconds": runtime_seconds,
        "note": (
            "DEV measurement only. This is NOT a production certification and "
            "makes no RTP claim for a published game. Natural rounds are the "
            "only basis for round RTP, hit, full-return, dry streaks and the "
            "feature entry rate; forced freegame rounds are deliberately "
            "generated and are used only for the feature internal distribution."
        ),
    }


def human_report(report: dict) -> str:
    lines = []
    lines.append("=" * 78)
    lines.append(f"Block Cave calibration report — {report['label']}")
    lines.append("=" * 78)
    lines.append(f"pay_scale_applied: {report['pay_scale_applied']}")
    lines.append(f"ore_vein_enabled : {report.get('ore_vein_enabled', True)}")
    lines.append(f"wincap: {report['wincap_mult']}x ({report['wincap_units']} units)")
    lines.append(f"base strip sha256: {report['strip_info']['base_strip_sha256']}")
    lines.append(f"free strip sha256: {report['strip_info']['free_strip_sha256']}")
    lines.append(f"runtime: {report['runtime_seconds']:.1f}s")
    lines.append("")

    for key in ("natural_base", "forced_freegame"):
        s = report[key]
        lines.append("-" * 78)
        lines.append(f"{key}  (sample {s['sample_size']}, label {s['label']})")
        lines.append("-" * 78)
        if key == "natural_base":
            lines.append(f"RTP (mean round payout)          : {fmt(s['rtp'])}")
            lines.append(f"  base RTP contribution          : {fmt(s['base_rtp'])}")
            lines.append(f"  feature RTP contribution       : {fmt(s['feature_rtp'])}")
            lines.append(f"RTP stddev                       : {fmt(s['rtp_std'])}")
            lines.append(f"Visible hit P(payout>0)          : {fmt(s['visible_hit'])}  CI {fmt_ci(s['visible_hit_ci'])}")
            lines.append(f"Full return P(payout>=1.0x)      : {fmt(s['full_return'])}  CI {fmt_ci(s['full_return_ci'])}")
            ds = s.get("dry_streaks", {})
            if ds:
                lines.append(f"Dry streak: obs 10-zero window    : {fmt(ds.get('obs_zero_window_10'))}  (theo {fmt(ds.get('theoretical_zero_window_10'))})")
                lines.append(f"Dry streak: obs 20-zero window    : {fmt(ds.get('obs_zero_window_20'))}  (theo {fmt(ds.get('theoretical_zero_window_20'))})")
                lines.append(f"Dry streak: max zero run         : {ds.get('max_zero_run')}  (#runs>=10: {ds.get('num_zero_runs_ge_10')}, >=20: {ds.get('num_zero_runs_ge_20')})")
            fe = s.get("feature_entry", {})
            if fe.get("p") is not None:
                lines.append(f"Feature entry rate               : {fmt(fe['p'])}  CI {fmt_ci(fe['ci95'])}  ({fe['k']}/{fe['n']})")
        fd = s.get("feature_duration", {})
        if fd:
            lines.append(f"Feature duration (spins)         : mean {fmt(fd.get('mean'))} median {fmt(fd.get('median'))} min {fmt(fd.get('min'))} max {fmt(fd.get('max'))} (n={fd.get('n_features')})")
        fp = s.get("feature_payout", {})
        if fp:
            lines.append(f"Feature payout (multiplier)      : mean {fmt(fp.get('mean'))} median {fmt(fp.get('median'))} max {fmt(fp.get('max'))} (n={fp.get('n_features')})")
            lines.append(f"  percentiles: p10 {fmt(fp.get('p10'))} p25 {fmt(fp.get('p25'))} p50 {fmt(fp.get('median'))} p75 {fmt(fp.get('p75'))} p90 {fmt(fp.get('p90'))} p99 {fmt(fp.get('p99'))}")
        wt = s.get("win_tails", {})
        if wt:
            lines.append(f"Round payout p50/p90/p99/p99.9   : {fmt(wt.get('p50'))} / {fmt(wt.get('p90'))} / {fmt(wt.get('p99'))} / {fmt(wt.get('p99.9'))}")
            lines.append(f"Round payout max observed        : {fmt(wt.get('max'))}")
            lines.append(f"P(>=100x) / P(>=500x) / P(>=1000x): {fmt(wt.get('p_ge_100x'))} / {fmt(wt.get('p_ge_500x'))} / {fmt(wt.get('p_ge_1000x'))}")
            for label, key in (("P(>=100x)", "p_ge_100x"), ("P(>=500x)", "p_ge_500x"), ("P(>=1000x)", "p_ge_1000x")):
                ci = wt.get(f"{key}_ci")
                if ci and ci.get("p") is not None:
                    lines.append(f"  {label} 95% CI: normal [{fmt(ci['ci95'][0])}, {fmt(ci['ci95'][1])}]"
                                 f"  Wilson [{fmt(ci['wilson95'][0])}, {fmt(ci['wilson95'][1])}]"
                                 f"  ({ci['k']}/{ci['n']})")
            lines.append(f"wincap bind rate                 : {fmt(wt.get('wincap_bind_rate'))} ({wt.get('wincap_bind_count')})")
        cons = s.get("consistency", {})
        lines.append(f"Consistency violations           : {cons.get('violations')} / {cons.get('books_checked')}")
        if cons.get("examples"):
            lines.append(f"  examples: {json.dumps(cons['examples'])[:400]}")
        lines.append("")

    lines.append("=" * 78)
    lines.append(report["note"])
    lines.append("=" * 78)
    return "\n".join(lines)


def fmt(v):
    return "n/a" if v is None else f"{v:.4f}"


def fmt_ci(ci):
    if ci is None or ci[0] is None:
        return "n/a"
    return f"[{ci[0]:.4f}, {ci[1]:.4f}]"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Block Cave Stage 3 calibration harness (DEV).")
    ap.add_argument("--natural", type=int, default=1000, help="natural base rounds to run")
    ap.add_argument("--freegame", type=int, default=1000, help="forced freegame rounds to run")
    ap.add_argument("--start-seed", type=int, default=0, help="first simulation seed")
    ap.add_argument("--paytable-scale", type=float, default=1.0,
                    help="multiply the paytable by this factor (calibration experiment)")
    ap.add_argument("--label", default="run", help="report label (e.g. pre/post calibration)")
    ap.add_argument("--out", default=None, help="write JSON report to this path")
    ap.add_argument("--no-progress", action="store_true", help="suppress progress prints")
    ap.add_argument("--disable-ore-vein", action="store_true",
                    help="disable the ore-vein upgrade step (measure the upgrade's RTP contribution)")
    args = ap.parse_args()

    config = make_config(args.paytable_scale)
    set_ore_vein_enabled(not args.disable_ore_vein)
    state = CalibrateState(config)
    state.betmode = "base"

    t0 = time.time()
    print(f"Running {args.natural} natural base rounds "
          f"(criteria=basegame, pay_scale={args.paytable_scale})...", flush=True)
    natural = run_natural(state, args.natural, args.start_seed, args.label,
                          progress=not args.no_progress)
    print(f"Running {args.freegame} forced freegame rounds "
          f"(criteria=freegame, force_freegame=True)...", flush=True)
    forced = run_forced_freegame(state, args.freegame, args.start_seed + args.natural,
                                 args.label, progress=not args.no_progress)
    total_runtime = time.time() - t0

    report = build_report(args.label, args.paytable_scale, natural, forced, total_runtime,
                          ore_vein_enabled=not args.disable_ore_vein)
    print(human_report(report))

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nWrote JSON report to {out}")


if __name__ == "__main__":
    main()
