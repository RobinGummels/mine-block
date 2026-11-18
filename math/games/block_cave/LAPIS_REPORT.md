# Block Cave — Lapis Lazuli Config & RTP-vs-Tail Calibration

**Status:** DEV measurement only. **This is NOT a production certification and
makes no RTP claim for a published game.** All figures are measured on the
current (unpublished) Block Cave prototype. Owner: Math agent.

Two deliverables are documented here:

1. **Part 1 — a mathematically-neutral `lapis` config** that replaces the
   `silver` symbol with a new `lapis` symbol, derived from Candidate A
   (`candidate_a_config.py`) with identical counts, paytable values and strip
   arrangement. It is a SEPARATE, clearly-labelled DEV config and does **not**
   modify `game_config.py`, `candidate_a_config.py`, `candidate_b_config.py` or
   `ore_vein_rules.py`.
2. **Part 2 — a bounded, reproducible calibration** that attempts to raise the
   ≥100× tail probability toward ≈1e-4 while keeping the natural RTP inside the
   **96.0–96.7%** Engine band, the visible hit ≈70%, a **positive** ore-vein
   contribution, short free spins (8/12/16/16, retrigger cap 60) and the 1,000×
   cap. The trade-off and the feasibility conclusion are reported openly.

---

## Part 1 — Mathematically-neutral `lapis` config

### 1.1 Why a rename

Candidate A is the recommended Stage-3 config (see `CANDIDATES_REPORT.md`). The
product direction proposes a **Lapis Lazuli** branding instead of a silver-based
one, so the `silver` symbol is renamed to `lapis`. The rename must be
**mathematically neutral**: the symbol counts, the paytable values (the
`silver` row becomes the `lapis` row with the SAME values) and the strip
*arrangement* must be identical. The ONLY difference in the generated strips is
the literal string `silver` → `lapis`.

Because `game_config.build_strip` consumes randomness only via
`rng.randrange`/`rng.shuffle` (which operate on integer indices, not on symbol
names), replacing `silver` with `lapis` at the SAME position in the non-common
order yields a strip whose pattern is byte-identical after the silver→lapis
rename. The lapis config reproduces this self-contained so `game_config.py` is
not touched.

### 1.2 Config file

`math/games/block_cave/candidate_lapis_config.py` (self-contained):

- `build_lapis_strip(seed, counts)` — byte-for-byte mirror of
  `game_config.build_strip` with `lapis` in place of `silver`.
- `build_lapis_pay_group()` — the §3.1 paytable with `lapis` in place of
  `silver`.
- `build_config()` — a fresh `GameConfig` with the lapis strips, the lapis
  paytable and the DEV `create-cluster` → `diamond` ore-vein rule.
- `BASE_COUNTS` / `FREE_COUNTS` — identical to Candidate A's counts, with
  `lapis` replacing `silver`.
- Seeds: base `20261117`, free `20261118` (same as Candidate A).

### 1.3 Reproducibility

Generated strips are frozen by SHA-256:

| | SHA-256 |
|---|---|
| Lapis base strip | `00af3ba544dba0ee523b6d4e85304d0622dd740a5c76dc13651e254a22558181` |
| Lapis free strip | `bc15b4fb96319e90f35024fe8b751b3ee3534731a56aa0f9939a7a8034db4c47` |

For reference, Candidate A's strips (unchanged) are:

| | SHA-256 |
|---|---|
| Candidate A base strip | `33e6f349c3e968cba7f5e0839196bfc165cafc8f894ba8e5e188ea3b17a463c5` |
| Candidate A free strip | `12096d9f52e6c60286e3d2842e06de8e79e0b2771ce5db6ec4e452e06c440687` |

The §3.1 baseline strips (unchanged) are:

| | SHA-256 |
|---|---|
| Baseline base strip | `7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451` |
| Baseline free strip | `f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754` |

### 1.4 Rename-neutrality proof

`test_lapis_config_reproducible` in `math/games/block_cave/test_block_cave.py`
verifies, for both the base and the free strip:

- length 200, counts match the lapis count table, SHA-256 matches;
- `[s.replace("lapis","silver") for s in lapis_strip] == candidate_a_strip`
  (position-by-position equality after the rename);
- every position is either equal, or is `(lapis, silver)`;
- no `silver` remains in the lapis strips, and the lapis count equals A's
  silver count;
- the paytable gives `lapis` exactly Candidate A's `silver` row and every other
  symbol's pay values are identical;
- the baseline strips/SHAs are byte-identical after building the lapis config.

### 1.5 Seed-matched equivalence

At a small seed-matched sample the lapis config produces identical metrics to
Candidate A (RTP, hit, full, feature entry/payout/duration, max round,
≥100× probability, ore-vein Δ), confirming the rename is behaviourally neutral.
(DEV smoke, n=2000, `lapis_smoke_lapis.json` / `lapis_smoke_candA.json`.)

---

## Part 2 — RTP-vs-tail calibration (P(≥100×) toward ≈1e-4)

### 2.1 Objective

Raise the natural round probability of a ≥100× win toward ≈1e-4 (≈1 in 10,000
rounds) from the Candidate-A baseline (≈1e-5), while keeping:

- natural RTP inside the **96.0–96.7%** band;
- visible hit ≈**70%**;
- a **positive** ore-vein contribution (Δ > 0 pp);
- **short** free spins (8/12/16/16, retrigger cap 60);
- the **1,000×** round cap;
- `game_config.py`, `candidate_a_config.py`, `candidate_b_config.py` and
  `ore_vein_rules.py` unchanged.

### 2.2 Method

The natural lever for producing very large rounds is the **frequency of the
high-value symbols** `diamond` and `ingot` (the only symbols whose pay rows can
approach/exceed 100× on a single line; ingot's top row is 229.78×, diamond's top
row is 91.91×). The calibration therefore varies the **base-strip counts** of
`diamond` and `ingot` (compensated by reducing `lapis` to keep each strip length
exactly 200) and, in one arm, the **free-strip** counts. The paytable is
**unchanged** (§3.1 calibrated, scale 1.0) and the ore-vein rule stays the DEV
`create-cluster` → `diamond`. Every arm is built with the lapis strip builder
+ lapis paytable (Part 1) and measured on a **fresh out-of-sample range**
(`start_seed ≥ 20_000_000`), disjoint from the tuning range used for Candidate A.

**Screening (n=30k).** Five arms are screened at n=30,000 natural rounds +
20,000 forced freegame rounds using `screen_lapis_tail.py` with the
`--enabled-only` flag (the ore-vein-disabled natural pass is skipped for speed,
so `ore_vein_delta_pp` is not computed at screen size). At n=30k the tail is far
too rare to measure — **zero** ≥100× events occur in every arm — so `max_round`
is used only as a **coarse tail proxy** at screen size. The screen's purpose is
to reject arms that leave the RTP band or collapse the profile; the tail is
validated separately at large n.

Arms (each base and free strip sums to 200; free strip is the unchanged lapis
`G6` unless noted):

| Arm | base diamond | base ingot | base lapis | free change |
|---|---|---|---|---|
| `lapis_base` | 8 | 9 | 16 | — (reference = Candidate A) |
| `d10_i10` | 10 | 10 | 13 | — |
| `d12_i10` | 12 | 10 | 11 | — |
| `d12_i11` | 12 | 11 | 10 | — |
| `free_d8_i7` | 8 | 9 | 16 | free diamond 6→8, ingot 5→7, lapis 8→6, gold 9→7 |

### 2.3 Screening results

Measured on the OOS range `start_seed = 20_000_000`, n=30,000 natural + 20,000
forced freegame, `--enabled-only`. (The RTP 95% CI at n=30k is ±~2%, so band
membership here is indicative, not firm.)

| Arm | natural RTP | base RTP | feat RTP | hit | max_round | forced max_round |
|---|---|---|---|---|---|---|
| `lapis_base` | 0.9584 | 0.8954 | 0.0630 | 0.6981 | 26.75 | 53.86 |
| `d10_i10` | 0.9736 | 0.9106 | 0.0630 | 0.6987 | 32.35 | 55.30 |
| `d12_i10` | 0.9941 | 0.9311 | 0.0630 | 0.7000 | 44.10 | 55.30 |
| `d12_i11` | **1.0099** | 0.9469 | 0.0630 | 0.6994 | 42.95 | 64.46 |
| `free_d8_i7` | 0.9582 | 0.8954 | 0.0628 | 0.6981 | 26.75 | 53.86 |

Two observations drive the feasibility conclusion:

1. **Base-premium boosts push RTP out of band.** Because the base-modified arms
   (`d10_i10`, `d12_i10`, `d12_i11`) keep the same free strip, their feature RTP
   is **constant** (0.0630) and their feature payout/duration are identical to
   `lapis_base` (mean 8.288×, dur mean 8.649, max 24). Natural RTP therefore
   tracks base RTP directly: `natural ≈ base + 0.0630`. Even the mildest boost
   (`d10_i10`: diamond 8→10, ingot 9→10) raises base RTP by ≈1.5 pp (0.8954 →
   0.9106), taking natural RTP to 0.9736 — **above the 0.967 upper band edge**.
   The stronger boosts overshoot far more (0.9941, and `d12_i11` is **>1.00**).
   Since the band is only 0.7 pp wide, any premium boost that moves the tail by a
   measurable amount exceeds the band.

2. **The ≥100× tail is structurally out of reach.** Even **forced** freegames
   (every round enters the feature) reach a max of only **53.86×** for
   `lapis_base`, and at most **64.46×** for the most aggressive boost
   (`d12_i11`), over 20k forced rounds — all well below 100×. The feature's mean
   payout is ~8.3×, so to reach P(≥100×) ≈ 1e-4 (≈1.5% of feature rounds paying
   ≥100×) the feature would need extreme variance that the fixed paytable and
   strip composition cannot produce without also raising the mean (and hence
   RTP).

`free_d8_i7` (free-strip boost only, base unchanged) keeps RTP in band (0.9582)
but does **not** lift the tail — its `max_round` (26.75 natural, 53.86 forced)
is identical to `lapis_base`, and its feature mean actually drops slightly
(8.288× → 8.265×). It therefore does not advance the objective.

### 2.4 Out-of-sample validation

The screen's two most informative arms — `lapis_base` (the in-band reference)
and `d10_i10` (the **mildest** premium boost that begins to move the tail) —
were validated at **n=200,000 natural rounds + 20,000 forced freegame** on the
same OOS range `start_seed = 20_000_000`, in **full** mode (ore-vein enabled +
disabled + forced), using `screen_lapis_tail.py` (newer reproducible format).

| Arm | natural RTP | 95% CI | base RTP | ore-vein Δ (pp) | hit | entry | feat_pay mean | feat_dur mean | max_round | P(≥100×) |
|---|---|---|---|---|---|---|---|---|---|---|
| `lapis_base` | **0.9641** | [0.9572, 0.9710] | 0.9022 | **+0.0887** | 0.6999 | 0.00727 | 8.518 | 8.732 | 65.36 | 0 (Wilson ≤ 1.92e-5) |
| `d10_i10` | **0.9814** | [0.9741, 0.9886] | 0.9194 | +0.2047 | 0.7004 | 0.00727 | 8.518 | 8.732 | 80.04 | 0 (Wilson ≤ 1.92e-5) |

Both arms have **0 consistency violations**, max zero-run 9, short free spins
(mean 8.73, max 32) and a feature mean of 8.52× (inside the 8–12× band). The
ore-vein contribution is **positive** for both (the `create-cluster` → `diamond`
rule), stronger for `d10_i10` (+0.20 pp vs +0.09 pp) because there are more
diamonds to cluster.

The decisive contrast is the **RTP**:

- `lapis_base` natural RTP **0.9641** is inside the 96.0–96.7% band (point
  estimate; the CI straddles both edges, consistent with the known
  seed-sensitivity — see Limitations).
- `d10_i10` natural RTP **0.9814** is **above** the band, and its **entire** 95%
  CI `[0.9741, 0.9886]` lies **above the 0.967 upper edge**. The mildest
  premium-boost costs **≈1.7 pp** of RTP (0.9814 − 0.9641) against a band that
  is only **0.7 pp** wide.

The tail target is not reached by either arm at this sample size: **zero**
≥100× rounds occurred in 200k for both (max_round 65.36× / 80.04×), and the
Wilson 95% upper bound on P(≥100×) is **1.92e-5** — an order of magnitude below
the ≈1e-4 objective.

### 2.5 Feasibility conclusion

**The calibration objective is infeasible: P(≥100×) cannot be raised from ≈1e-5
toward ≈1e-4 while keeping the natural RTP inside the 96.0–96.7% band.**

Three independent observations support this:

1. **The tail is driven by high-value symbol frequency, which is the same lever
   that raises RTP.** To produce very large rounds the game needs more frequent
   `diamond`/`ingot` matches. Because the base-modified arms keep the same free
   strip, their feature RTP is **fixed** (0.0619), so `natural RTP = base RTP +
   0.062`. Every premium boost raises `base RTP` directly: the mildest (`d10_i10`,
   diamond 8→10, ingot 9→10) adds ≈1.7 pp, and the band is only 0.7 pp wide.
   The stronger boosts (`d12_i10` ≈0.994, `d12_i11` ≈1.01) overshoot far more.

2. **The boost does not even reach the tail.** At n=200k, `d10_i10` produced
   **zero** ≥100× rounds (max_round 80.04×) and `lapis_base` also zero (65.36×);
   the Wilson 95% upper bound on P(≥100×) is 1.92e-5 for both. Even **forced**
   freegames (every round in the feature) max at 45–53× with a mean ≈8.3×. There
   is no mechanism in the fixed §3.1 paytable + strip composition to make ≈1.5%
   of feature rounds pay ≥100× (the rate needed for P(≥100×)≈1e-4) without also
   inflating the mean and hence RTP.

3. **The one in-band alternative does not lift the tail.** `free_d8_i7` (free-strip
   boost only, base unchanged) stays in band (0.9582 at n=30k) but its `max_round`
   (26.75 natural / 53.86 forced) is identical to `lapis_base`, and its feature
   mean drops slightly (8.27× vs 8.29×). It does not advance the objective.

**Recommendation:** keep **`lapis_base`** (the mathematically-neutral rename of
Candidate A) as the Stage-3 config. On the fresh OOS range it is in band (point
estimate 0.9641), has a **positive** ore-vein contribution (+0.0887 pp), visible
hit ≈0.70, a feature mean of 8.52× (8–12× band), short free spins (mean 8.73,
max 32), low dry streaks (max zero-run 9) and **0** consistency violations. Its
≥100× tail is present in principle but too rare to measure at feasible n (0
events in 200k; Wilson upper bound 1.92e-5). No separate
`candidate_lapis_tail_config.py` is created, because no in-band tail boost was
found.

---

## Reproducibility

- Helpers: `.runtime/block_cave/screen_lapis_tail.py` (adds `--enabled-only`),
  `.runtime/block_cave/measure_config_module.py`.
- Config self-checks: `python math/games/block_cave/candidate_lapis_config.py`.
- Tests: `python math/games/block_cave/test_block_cave.py` (19/19, incl.
  `test_lapis_config_reproducible`).
- `pip check` clean; upstream `math/tests/win_calculations` 13/13.
- Calibration outputs (reproducible, newer format with start_seed + Wilson CIs):
  - Screen (n=30k, `--enabled-only`, start_seed 20M):
    `.runtime/block_cave/screen_oos_tail_30k.json`.
  - Validation (n=200k, full ore-vein, start_seed 20M):
    `.runtime/block_cave/screen_oos_validate_200k.json`.
- Arm definitions: `.runtime/block_cave/arms_oos_tail.json`,
  `.runtime/block_cave/arms_oos_validate.json`.

## Limitations

- Not a production certification; no published RTP claim; nothing deployed.
- The RTP 95% CI at feasible n (std ≈1.7–1.8) straddles the 96.0% lower edge
  for all in-band point estimates, so "in band" is a point-estimate statement,
  not a robust certification.
- P(≥100×) is extremely rare and **highly seed-sensitive**: Candidate A
  (identical to `lapis_base`) measured max_round 424.9× / P(≥100×)=1e-5 on the
  `start_seed=1M` range, but **zero** ≥100× events / max_round 65.36× on the
  `start_seed=20M` range (both n=200k). A single ultra-rare event can dominate
  the point estimate, so the tail is reported via the round-max and the ≥100×
  point estimate with a Wilson 95% CI, and no single range is a firm tail
  certification.
- The feasibility conclusion relies on the **relative** RTP cost of a premium
  boost (≈1.7 pp for `d10_i10`) vs the **0.7 pp** band width, which is robust
  across seeds, rather than on absolute band membership (which is
  seed-sensitive).
