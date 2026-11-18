"""Block Cave Stage 3 variant experiments (DEV measurement only).

Small, reproducible experiments used to choose the variant's strip counts,
seed, and ore-vein target BEFORE a large run. Nothing here is a production
claim. This module does not modify `game_config.py`; it builds throwaway
configs on the fly.

Run from anywhere, e.g.:

    & "C:\\Users\\robin\\Documents\\stake\\stake-game-ai\\math\\.venv\\Scripts\\python.exe" \
        math\\games\\block_cave\\experiment.py scatter
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MATH_DIR = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(MATH_DIR))

import game_config as gc                                    # noqa: E402
from game_config import build_strip, sha256_strip           # noqa: E402
from gamestate import GameState                             # noqa: E402
from calibrate import CalibrateState, set_ore_vein_enabled, run_natural, Measurer  # noqa: E402


# ---------------------------------------------------------------------------
# Config builder for arbitrary counts/seeds (does not touch game_config.py)
# ---------------------------------------------------------------------------

def build_config(base_counts, base_seed, free_counts, free_seed, pay_scale=1.0,
                 ore_rule="baseline", ore_target="diamond"):
    """Return a fresh GameConfig with the given strips and paytable scale.

    Reuses the baseline triggers, wincap and bet modes; only the paytable
    (optionally scaled by `pay_scale`) and the reel strips are replaced. The
    GameConfig singleton is reset so each call returns an independent config.
    `ore_rule`/`ore_target` set the ore-vein behaviour (defaults to the §3.1
    baseline).
    """
    from calibrate import make_config
    config = make_config(pay_scale)
    config.reels = {
        "BR0": [build_strip(base_seed, base_counts)] * config.num_reels,
        "FR0": [build_strip(free_seed, free_counts)] * config.num_reels,
    }
    config.ore_vein_rule = ore_rule
    config.ore_vein_target = ore_target
    return config


def make_counts(pickaxe: int, reduce_from: str = "earth") -> dict:
    """Base counts with a different pickaxe count, keeping total 200.

    `reduce_from` is the symbol whose count is reduced by the pickaxe delta so
    the strip stays length 200.
    """
    counts = dict(gc.BASE_COUNTS)
    delta = pickaxe - counts["pickaxe"]
    counts["pickaxe"] = pickaxe
    counts[reduce_from] = counts[reduce_from] - delta
    assert sum(counts.values()) == 200, sum(counts.values())
    assert counts[reduce_from] >= 0, counts
    return counts


# ---------------------------------------------------------------------------
# Scatter-rate measurement
# ---------------------------------------------------------------------------

def scatter_rate(config, n, start_seed, label):
    """Draw `n` natural base boards and measure the 3+ pickaxe fraction.

    Mirrors the engine's initial-board scatter count (draw_board +
    count_special_symbols) WITHOUT running the cascade, so it is fast. This is
    the free-spin ENTRY rate for the natural base game.
    """
    state = GameState(config)
    state.betmode = "base"
    state.criteria = "basegame"
    hits = 0
    for i in range(n):
        state.run_spin(start_seed + i)
        b = state.book.to_json()
        if any(e.get("type") == "freeSpinTrigger" for e in b["events"]):
            hits += 1
    p = hits / n
    se = math.sqrt(p * (1 - p) / n) if n else 0.0
    return {
        "label": label,
        "n": n,
        "entries": hits,
        "entry_rate": p,
        "se": se,
        "ci95": [p - 1.96 * se, p + 1.96 * se],
    }


def scatter_sweep():
    """Sweep pickaxe count (reducing earth) and measure entry rate."""
    n = 40000
    print(f"Sweeping pickaxe count, {n} natural base spins each "
          f"(reducing `earth` to keep length 200).\n")
    print(f"{'pick':>5} {'earth':>6} {'entry%':>9} {'CI':>24} {'k':>6}")
    for pick in range(3, 8):
        counts = make_counts(pick, reduce_from="earth")
        config = build_config(counts, 20261117, gc.FREE_COUNTS, 20261118)
        r = scatter_rate(config, n, 0, f"pick{pick}")
        ci = r["ci95"]
        print(f"{pick:>5} {counts['earth']:>6} {r['entry_rate']*100:>8.3f} "
              f"[{ci[0]*100:.3f},{ci[1]*100:.3f}] {r['entries']:>6}")


def scatter_seed_sweep(pick, reduce_from="earth", n=20000, seeds=range(20261100, 20261140)):
    """For a fixed pickaxe count, sweep seeds to find one landing near ~1%."""
    print(f"Seed sweep for pickaxe={pick} (reducing {reduce_from}), "
          f"{n} natural base spins each.\n")
    print(f"{'seed':>10} {'entry%':>9} {'k':>6}")
    results = []
    for seed in seeds:
        counts = make_counts(pick, reduce_from=reduce_from)
        config = build_config(counts, seed, gc.FREE_COUNTS, 20261118)
        r = scatter_rate(config, n, 0, f"seed{seed}")
        results.append((r["entry_rate"], seed, r["entries"]))
        print(f"{seed:>10} {r['entry_rate']*100:>8.3f} {r['entries']:>6}")
    results.sort()
    best = results[0]
    print(f"\nLowest entry: seed {best[1]} -> {best[0]*100:.3f}% ({best[2]})")
    print("Seeds near 1.0%:")
    for rate, seed, k in results:
        if 0.009 <= rate <= 0.013:
            print(f"  seed {seed} -> {rate*100:.3f}% ({k})")


def scatter_grid():
    """Grid over pickaxe count and reduce-from symbol at a few seeds."""
    n = 15000
    seeds = [20261117, 20261131, 20261102, 20261116]
    reduces = ["earth", "stone", "timber", "copper", "silver", "gold", "emerald"]
    print(f"Grid: pickaxe x reduce_from x seed, {n} natural base spins each.\n")
    for pick in (3, 4, 5):
        print(f"--- pickaxe = {pick} ---")
        print(f"{'reduce':>8} {'seed':>10} {'entry%':>9}")
        for red in reduces:
            best = None
            for seed in seeds:
                counts = make_counts(pick, reduce_from=red)
                config = build_config(counts, seed, gc.FREE_COUNTS, 20261118)
                r = scatter_rate(config, n, 0, f"{red}{seed}")
                if best is None or r["entry_rate"] < best[0]:
                    best = (r["entry_rate"], seed)
            print(f"{red:>8} {best[1]:>10} {best[0]*100:>8.3f}")


# ---------------------------------------------------------------------------
# Ore-vein target sweep (enabled vs disabled contribution)
# ---------------------------------------------------------------------------

def measure_rtp(config, n, start_seed, ore_enabled, label):
    """Run `n` natural base rounds with the ore-vein step on/off.

    Returns the round RTP (mean payout multiplier) and its std. Uses the same
    seed range for enabled/disabled so the comparison is seed-matched.
    """
    set_ore_vein_enabled(ore_enabled)
    state = CalibrateState(config)
    state.betmode = "base"
    m = run_natural(state, n, start_seed, label, progress=False)
    return m


def ore_target_sweep(pick, reduce_from, base_seed, n=30000):
    """Measure the ore-vein RTP contribution for each candidate target symbol.

    Uses the given base strip (pickaxe count / reduce_from / base_seed) and the
    baseline free strip. For each target symbol, runs seed-matched enabled and
    disabled natural rounds and reports the RTP delta.
    """
    base_counts = make_counts(pick, reduce_from=reduce_from)
    targets = ["diamond", "silver", "gold", "emerald", "ingot"]
    print(f"Ore-vein target sweep: pick={pick} reduce={reduce_from} "
          f"base_seed={base_seed}, {n} natural rounds per arm.\n")
    print(f"{'target':>8} {'RTP_en':>9} {'RTP_dis':>9} {'delta(pp)':>10} {'hit_en':>8} {'hit_dis':>8}")
    for target in targets:
        config = build_config(base_counts, base_seed, gc.FREE_COUNTS, 20261118)
        config.ore_vein_target = target
        en = measure_rtp(config, n, 0, True, f"en_{target}")
        di = measure_rtp(config, n, 0, False, f"dis_{target}")
        delta_pp = (en.payouts and di.payouts and
                    (sum(en.payouts) / len(en.payouts) - sum(di.payouts) / len(di.payouts)) * 100)
        en_rtp = sum(en.payouts) / len(en.payouts)
        di_rtp = sum(di.payouts) / len(di.payouts)
        hit_en = sum(en.hit) / len(en.hit)
        hit_dis = sum(di.hit) / len(di.hit)
        print(f"{target:>8} {en_rtp:>9.4f} {di_rtp:>9.4f} {delta_pp:>+10.2f} {hit_en:>8.4f} {hit_dis:>8.4f}")

def rule_sweep(pick, reduce_from, base_seed, target="diamond", n=30000, rules=("baseline", "create-cluster", "isolated", "convert-all", "out-of-cluster")):
    """Measure the ore-vein RTP contribution for each candidate rule.

    Seed-matched enabled vs disabled natural rounds on the given strip. The
    `disabled` arm is identical for every rule (it is just the ore-vein step
    off), so each rule's delta isolates its own contribution.
    """
    base_counts = make_counts(pick, reduce_from=reduce_from)
    print(f"Ore-vein rule sweep: pick={pick} reduce={reduce_from} base_seed={base_seed} "
          f"target={target}, {n} natural rounds per arm.\n")
    print(f"{'rule':>14} {'RTP_en':>9} {'RTP_dis':>9} {'delta(pp)':>10} {'hit_en':>8}")
    for rule in rules:
        config = build_config(base_counts, base_seed, gc.FREE_COUNTS, 20261118)
        config.ore_vein_target = target
        config.ore_vein_rule = rule
        en = measure_rtp(config, n, 0, True, f"en_{rule}")
        di = measure_rtp(config, n, 0, False, f"dis_{rule}")
        en_rtp = sum(en.payouts) / len(en.payouts)
        di_rtp = sum(di.payouts) / len(di.payouts)
        delta_pp = (en_rtp - di_rtp) * 100
        hit_en = sum(en.hit) / len(en.hit)
        print(f"{rule:>14} {en_rtp:>9.4f} {di_rtp:>9.4f} {delta_pp:>+10.2f} {hit_en:>8.4f}")


def measure_variant(pick, reduce_from, base_seed, free_seed, target, rule, natural, freegame, start_seed=0, label="variant", pay_scale=1.0, free_counts=None):
    """Build a variant config and run natural + forced freegame rounds.

    Prints the human report for the DEV measurement of one candidate variant.
    `freegame` rounds are deliberately generated (criteria=freegame) and are
    used only for the feature internal distribution, not for round RTP.
    `free_counts` overrides the free strip symbol counts (defaults to the
    baseline §4.2 FREE_COUNTS).
    """
    from calibrate import build_report, human_report, run_forced_freegame
    base_counts = make_counts(pick, reduce_from=reduce_from)
    f_counts = free_counts if free_counts is not None else gc.FREE_COUNTS
    config = build_config(base_counts, base_seed, f_counts, free_seed,
                          pay_scale=pay_scale, ore_rule=rule, ore_target=target)
    set_ore_vein_enabled(True)
    state = CalibrateState(config)
    state.betmode = "base"
    print(f"Variant: pick={pick} reduce={reduce_from} base_seed={base_seed} "
          f"free_seed={free_seed} target={target} rule={rule} pay_scale={pay_scale}\n")
    natural_m = run_natural(state, natural, start_seed, label, progress=False)
    forced_m = run_forced_freegame(state, freegame, start_seed + natural, label, progress=False)
    report = build_report(label, pay_scale, natural_m, forced_m, 0.0, ore_vein_enabled=True)
    print(human_report(report))
    return report


def main():
    ap = argparse.ArgumentParser(description="Block Cave variant experiments (DEV).")
    ap.add_argument("cmd", choices=["scatter", "scatter-seed", "scatter-grid", "ore", "rule", "measure"], default="scatter", nargs="?")
    ap.add_argument("--pick", type=int, default=4, help="pickaxe count for the seed sweep")
    ap.add_argument("--n", type=int, default=20000, help="spins per seed in the seed sweep")
    ap.add_argument("--reduce", default="silver", help="symbol reduced to make room for pickaxes")
    ap.add_argument("--base-seed", type=int, default=20261117, help="base strip seed")
    ap.add_argument("--ore-n", type=int, default=30000, help="natural rounds per arm in the ore sweep")
    ap.add_argument("--target", default="diamond", help="ore-vein upgrade target symbol")
    ap.add_argument("--rules", default="baseline,create-cluster,isolated,convert-all,out-of-cluster",
                    help="comma-separated ore-vein rule names for the rule sweep")
    ap.add_argument("--free-seed", type=int, default=20261118, help="free strip seed")
    ap.add_argument("--rule", default="create-cluster", help="ore-vein rule for the measure command")
    ap.add_argument("--natural", type=int, default=20000, help="natural rounds for the measure command")
    ap.add_argument("--freegame", type=int, default=20000, help="forced freegame rounds for the measure command")
    ap.add_argument("--label", default="variant", help="measure label")
    ap.add_argument("--pay-scale", type=float, default=1.0, help="paytable scale factor for the measure command")
    ap.add_argument("--free-counts", default=None,
                    help="JSON dict overriding the free strip symbol counts, e.g. "
                         '{"earth":34,"stone":31,"timber":29,"copper":27,"silver":16,'
                         '"gold":14,"emerald":12,"diamond":10,"ingot":10,"ore_vein":11,"pickaxe":3}')
    args = ap.parse_args()
    if args.cmd == "scatter":
        scatter_sweep()
    elif args.cmd == "scatter-seed":
        scatter_seed_sweep(args.pick, n=args.n)
    elif args.cmd == "scatter-grid":
        scatter_grid()
    elif args.cmd == "ore":
        ore_target_sweep(args.pick, args.reduce, args.base_seed, n=args.ore_n)
    elif args.cmd == "rule":
        rule_sweep(args.pick, args.reduce, args.base_seed, target=args.target,
                   n=args.ore_n, rules=tuple(r.strip() for r in args.rules.split(",")))
    elif args.cmd == "measure":
        free_counts = None
        if args.free_counts:
            free_counts = json.loads(args.free_counts)
        measure_variant(args.pick, args.reduce, args.base_seed, args.free_seed,
                        args.target, args.rule, args.natural, args.freegame,
                        label=args.label, pay_scale=args.pay_scale, free_counts=free_counts)


if __name__ == "__main__":
    main()
