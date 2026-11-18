# Block Cave — Stage 1 Math Design Proposal

Working title: **Block Cave** (final name pending).
Owner: Math agent. Status: **Stage 1 proposal only.** No game code exists yet.
Every numeric value below that is not derived from an actual simulation is
marked **ASSUMPTION**. No measured RTP, hit-rate or feature-rate is claimed.
This file is a proposal for the orchestrator and QA to review before Stage 2.

The design is constrained by `docs/GAME_SPEC.md`, `docs/PROJECT_PLAN.md`,
`docs/ENGINE_CONTRACT.md` and the engine conventions read from
`math/games/0_0_cluster/` and `math/src/state/books.py`. Payouts, symbol
weights and event ordering are proposed in Python-owned terms and must be
replayed verbatim by the frontend.

## Revision note (2026-11-18 — Candidate 2 base-seed search & out-of-sample validation)

Following the seed-sensitivity caveat, a **bounded base-strip-seed search** was
run for Candidate 2: 21 base-strip seeds (the reference 20261103 plus a
systematic block 20265001–20265020) were screened at n=50k, and the five most
promising were re-measured **out-of-sample** on a fresh spin-RNG range
(`start_seed = 1_000_000`, disjoint from the tuning range 0–199,999) at n=200k
natural + 20k forced freegame. The paytable (§3.1, scale 1.0), the H4 base
counts, the F5 free strip (free seed 20261118), the ore-vein rule/target
(`create-cluster` → diamond) and the short-free-spin structure were **fixed**;
only the base-strip seed and the spin-RNG `start_seed` varied.

**Key outcome:** no new seed is needed. The existing Candidate 2 reference seed
**20261103** is the only one of the 21 screened that satisfies **both** the
96.0–96.7% RTP band **and** the §3.3 profile. On the fresh out-of-sample range
it measures **RTP 0.9604 (in band)**, visible hit 0.4641 (≈45%), full return
0.1847 (≈15%), feature entry 1.60%, feature payout 11.07× (8–12×), short free
spins (mean 8.86, max 32), a **positive** ore-vein Δ (+0.325 pp) and a
meaningful tail (max 210.46×, P(≥100×) ≈6.5e-05), with 0 consistency violations.

This **revises** the earlier "below band" framing in `CANDIDATE2_REPORT.md` §9/§10:
the 0.9509 point estimate was on the *tuning* range; the same config measures
**0.9604** on a fresh range. The 95% CI **[0.9468, 0.9740] still straddles the
96.0% lower edge** and the RTP stddev is ≈3.1, so the RTP-band question is a
**variance/precision limit of a single 200k sample**, not a hard design wall.
A certification-scale measurement (≥500k–1M rounds or a multi-range aggregate)
is required to narrow the CI and confirm the band. Candidate 2's config
(`candidate2_config.py`, seed 20261103) is **unchanged**; no new
`candidate2_seed_<n>.py` was created. Full table in `CANDIDATE2_REPORT.md` §11.

## Revision note (2026-11-18 — Stage-3 Candidates A & B, baseline-derived DEV configs)

Two further **baseline-derived** DEV candidates were built to explore a different
design point: keep the §3.1 **pickaxe=3** (so the natural 3+ pickaxe free-spin
ENTRY rate stays ≈0.67%), switch the ore-vein rule to the positive
**`create-cluster`** (target `diamond`) rule, and **prioritise HIGH visible hit
(≈70%) and LOW dry streaks**. The §3.3 targets of 45% hit / 15% full-return are
**explicitly relaxed**. The paytable is the §3.1 calibrated table at scale 1.0
(unchanged); only the reel strips and the ore-vein rule differ. Both configs are
**DEV-only** and do **not** modify `game_config.py`, `variant_config.py` or
`candidate2_config.py`.

* **Candidate A** (`candidate_a_config.py`): base strip **E4** (keeps §3.1
  earth/stone/timber/copper/silver/ore_vein=8/pickaxe=3, but diamond 10→8 and
  ingot 7→9) + free strip **G6** (heavy commons, ore_vein=5) + `create-cluster`.
  This lands the natural RTP inside the 96.0–96.7% band with a high hit and a
  positive ore-vein contribution.
* **Candidate B** (`candidate_b_config.py`): base strip **S6** with **Silver Ore
  REMOVED** (silver=0, redistributed across premiums + a small earth bump, sum
  200) + the same **G6** free strip + `create-cluster`. This isolates the
  silver-removal effect.

**Key finding — silver removal is high-variance and trades hit/tail for a positive
ore-vein effect.** Under the positive `create-cluster` rule, removing silver makes
the base RTP **bimodal/chaotic** (the `ore_vein` wild count and the premium
composition drive a sharp RTP step function): at small sample sizes nearby
silver-removed compositions either **overshoot** the band (RTP >1.0) or
**undershoot** it (RTP ≈0.79–0.93). **Candidate B (s6)** is the composition that
lands **inside** the 96.0–96.7% band on a fresh out-of-sample range (RTP 0.9643),
but at a **slightly lower visible hit (≈0.68 vs ≈0.70 for Candidate A)** and with
**no meaningful ≥100× tail** (max 59.3×, P(≥100×)=0 vs Candidate A max 424.9×,
P(≥100×)=1e-05). Silver removal is therefore **achievable but not a strict
improvement**: it gives a stronger positive ore-vein Δ (+0.28 pp vs +0.09 pp) at
the cost of hit and tail. Full metrics and the unachievable-combination statement
are in `CANDIDATES_REPORT.md`.

**Entry-rate note:** with pickaxe=3 the natural entry is ≈0.67% (pickaxe=4 gives
≈1.5–1.7%). An exact **1.0%** entry is **not reachable** with integer pickaxe
counts; Candidate A keeps pickaxe=3 to preserve the high-hit priority.


## Revision note (2026-11-18 — Stage-3 Candidate 2, separate DEV config)

A second Stage-3 DEV candidate, **Candidate 2**, is added as a **separate**
config module (`candidate2_config.py`). It does **not** modify this design or
`game_config.py`; the §3.1 baseline and the Stage-3 variant
(`variant_config.py`) remain unchanged and independently reproducible.

Candidate 2 targets the §3.3 hit-rate/full-return design targets that the
baseline misses (visible hit ≈45%, full return ≈15%), a **positive** ore-vein
contribution (via the DEV `create-cluster` rule), a feature payout in the 8–12×
band, and short free spins (8/12/16/16, retrigger cap 60). It is **DEV
measurement only** — no production RTP claim. See `CANDIDATE2_REPORT.md` for
the full three-way comparison (baseline / Stage-3 variant / Candidate 2).

**Key measured outcome (n = 200,000 natural rounds, seed-matched):** Candidate 2
reaches the hit (~46.5%) and full-return (~18.4%) design targets and a positive
ore-vein Δ (+0.27 pp), but its natural RTP point estimate is **0.9509 — below
the 96.0–96.7% Engine band** (95% CI [0.9377, 0.9640], which straddles the 96.0%
lower edge). This surfaces a real conflict between the §3.3 hit/full targets and
the RTP band: lowering the visible hit to ≈45% also lowers the base-game RTP
contribution enough that, combined with the entry/feature structure, the total
does not robustly reach 96.0%. This is reported rather than silently "fixed" by
distorting the paytable.

## Revision history (2026-11-17 — Stage 3 calibration correction)

This revision **reverts the Stage-3 C2 paytable scale-up**. The prior revision
multiplied the §3.1 paytable by `F = 1.8382663803148458` (derived from a stale
`calib_pre` RTP of 0.524) and baked the result into `game_config.py`. That
scale-up is **wrong**: the exact MATH_DESIGN §3.1 paytable at **scale 1.0**
already measures a natural base-game RTP of **≈ 0.964**, inside the
**96.0–96.7%** Engine band near the 96.3% target, whereas the ×F paytable
over-pays at **≈ 1.76**. The `calib_pre` 0.524 figure was measured on a
different/lower paytable (a ~48% house edge, implausible) and is **not** a
valid basis for a scale factor.

- **C3 (this revision) — paytable reverted to §3.1, strips unchanged.**
  `_COMMON_PAYS`, `_PREMIUM_PAYS` and `_INGOT_PAYS` in `game_config.py` were
  restored to the MATH_DESIGN §3.1 values (scale 1.0), removing the ×F
  multiplication. The base and free-spin strip seeds (20261117 / 20261118) and
  counts are untouched, so the strip SHA-256 values are unchanged. The
  calibrated paytable is the §3.1 table itself; **no paytable scale factor is
  applied**.
- **Measured (Stage 3), not assumed:** with the §3.1 paytable, the natural
  base-game RTP measured on 500,000 rounds is reported in
  `CALIBRATION_REPORT.md`. It is **not** a production certification. Several
  design targets were **not** met and are surfaced as **open conflicts** in
  §3.3 and the report (visible hit ≈ 69% vs the 45% target, full-return ≈ 29%
  vs the 12–16% target, feature entry ≈ 0.70% vs the ≈1.0% target). These are
  **not** silently "fixed" by distorting the paytable.

## Revision history (2026-11-17 — Stage 2 mechanics-framing correction)

This revision removes a **framing error** (not a mechanics change): the
ore-vein upgrade was described as a "bonus upgrade" requiring platform
confirmation, conflating it with the **separate, deferred** free-spin
bonus-tier upgrade (a small-guaranteed-win product preference). It is not.

- **C1 (this revision)** — the ore-vein conversion of an adjacent regular block
  is a **normal in-round mechanic**, like the wild and the tumble. It is
  automatic, predetermined and stateless. It is **not** a bonus upgrade and is
  **not** the deferred free-spin bonus-tier upgrade. Only the separate
  free-spin bonus-tier upgrade still needs platform confirmation; the ore-vein
  conversion is part of the approved game concept and is assessed with the
  other in-round mechanics (see §1 and §9). Game logic is unchanged.

## Revision history (2026-11-17 — QA-response revision)

This revision resolves the independent QA findings in
`qa/reports/block_cave_stage1_math_review.md`. Changes made:

- **F1** — corrected the natural 3+ scatter rate from 0.8% (1 in 125) to
  **≈1.01% (1 in ~98.7)** and added the binomial-approximation caveat.
- **F2** — defined the exact base and free-spin reel-strip arrangements
  (deterministic seed + algorithm + full ordered 200-symbol lists) in §4.1/§4.2.
- **F3** — bounded the ore-vein upgrade: target changed from `ingot` to the
  mid-premium `diamond`, per-activation cap reduced from 3 to **1** adjacent
  block, and the now-invalid "low activation frequency" mitigation premise was
  removed. The vein's RTP contribution is now a measured-and-compensated
  target, not a presumed bound.
- **F4** — the 1,000× cap is restated as a hard safety upper bound, not a
  target; no top pays were raised to reach it. An expected max-win frequency
  is given as **ILLUSTRATION**.
- **F5** — the event table now mirrors the real engine emission sequence
  (adds `setWin`, places `updateTumbleWin` before `tumbleBoard`, places
  `wincap` during the cascade, and inserts `oreVeinUpgrade` between
  `updateTumbleWin` and `tumbleBoard`).
- **F6** — added a concrete, implementable `oreVeinUpgrade` event-contract
  draft (type string, payload field names/types, coordinate convention).
- **F7** — named the two engine touchpoints needed for natural triggering
  (`draw_board` re-draw suppression; `check_fs_condition` initial-board
  counting) in §6.
- **F8** — §3.2/§3.3 reworded so hit-rate and RTP are described as needing
  joint calibration, not as consequences of the weights.
- **F9** — statelessness explicitly affirmed; no player-selected wager/upgrade.
- **F10** — §7 reworded: individual wins are below the cap in practice; only
  the cumulative round total is clamped to 1,000×.
- **Frontend contract review (AGREE WITH CORRECTIONS)** — the frontend agent
  verified the `oreVeinUpgrade` coordinate convention and placement, and this
  revision applies its three corrections: (A) `upgrades` vs `veinPositions`
  cardinality, (B) in-cluster vs out-of-cluster upgrade targets, and (C) the
  `wincap` frontend-handler requirement. See §5.3/§5.4, §8 and §9.

---

## 1. Scope and status

- **Stage 1 deliverable.** This is a design proposal, not an implementation.
- No `run.py`, `game_config.py`, `gamestate.py`, reel CSVs or simulation
  exists yet. None of the values here have been validated by simulation.
- **Stateless (F9).** Block Cave is a **stateless** game: there is no
  player-selected wager, no gamble/continuation, no early cashout and no
  persistent per-player state. The full outcome of a round is determined by
  the Python engine and replayed by the frontend. The ore-vein upgrade is a
  **normal in-round mechanic**, not a player choice and not a continuation:
  when a vein activates it converts an adjacent regular block as a fixed rule.
  It is **not** a "bonus upgrade" and is **not** the deferred free-spin
  bonus-tier upgrade (see §9); it is assessed with the other in-round
  mechanics like the wild and the scatter.
- All "target" percentages are **design targets**, not measured results. The
  current product RTP target is **96.3%** per mode, within the Engine's
  **96.0–96.7%** band (see `GAME_SPEC.md`). The 1.0× mode must also satisfy
  the official cheapest-mode and standard-deviation guidelines.
- Board: **6 columns × 5 rows = 30 symbol positions**. Win rule: **5 or more
  orthogonally connected identical regular symbols** form a cluster; winning
  blocks are removed, new blocks tumble in, and the process repeats until no
  cluster remains.
- **ASSUMPTION**: the paytable, reel weights, free-spin length/rate, retrigger
  cap and ore-vein rules below are a self-consistent starting point. Stage 2/3
  simulation must verify and calibrate RTP, hit rate, dry-streak behaviour,
  feature rate and the max-win cap. Until then, none of the numbers should be
  treated as final.
- **Separate Stage-3 variant (DEV, unpublished).** A distinct candidate config
  is maintained separately in `variant_config.py` (pickaxe=4, `create-cluster`
  ore-vein rule, retuned free strip) and is measured against this baseline in
  `COMPARISON_REPORT.md`. It does **not** modify this design or `game_config.py`;
  the validated §3.1 baseline is unchanged and remains reproducible.

---

## 2. Symbol set and IDs

Stable symbol IDs. The display name is a presentation concern; the engine and
frontend agree on these IDs. IDs are lower-case, no spaces.

| ID | Display name (draft) | Class |
| --- | --- | --- |
| `earth` | Earth block | regular / paying |
| `stone` | Stone block | regular / paying |
| `timber` | Timber block | regular / paying |
| `copper` | Copper-bearing stone | regular / paying |
| `silver` | Silver-bearing stone | regular / paying |
| `gold` | Gold-bearing stone | regular / paying |
| `emerald` | Emerald-bearing stone | regular / paying |
| `diamond` | Diamond-bearing stone | regular / paying |
| `ingot` | Fantasy-alloy ingot (name pending) | regular / paying (rare top) |
| `ore_vein` | Ore vein | wild (regular cluster match + adjacent upgrade) |
| `pickaxe` | Pickaxe | scatter (free-spin trigger, NOT a wild) |

- **9 regular symbols pay** (earth, stone, timber, copper, silver, gold,
  emerald, diamond, ingot).
- `ore_vein` is a **wild** for regular cluster matching and performs an
  adjacent-block upgrade (Section 5). It is not a paying symbol.
- `pickaxe` is a **scatter** that triggers free spins. It is **not** a wild and
  pays nothing by itself (Section 6).
- No Minecraft/Roblox names, likenesses, textures or assets. The ingot is
  original fantasy material.

---

## 3. Paytable

Payouts are expressed as **multiples of the play amount** (e.g. 0.1× = 0.1 ×
play amount). The engine serializes `payoutMultiplier` as
`int(round(multiplier * 100, 0))` (see `math/src/state/books.py`), so 0.1× →
10 units, 1.0× → 100 units, 1,000× → 100,000 units.

### 3.1 Pay table structure

Cluster sizes are defined as **ranges** `(min, max)` that expand to exact
cluster-size keys, matching the engine's `convert_range_table` convention
(`(5,5)`, `(6,8)`, `(9,12)`, `(13,36)` style). A cluster that does not fall in
a paying range pays nothing. These values were a **Stage 1 ASSUMPTION**; in
Stage 3 they are the **calibrated paytable** (scale 1.0, no scaling factor —
see the revision history C3), and their natural base-game RTP is measured in
`CALIBRATION_REPORT.md`.

#### Common symbols — frequent small wins

| Cluster size | `earth` | `stone` | `timber` | `copper` |
| --- | --- | --- | --- | --- |
| 5 | 0.18 | 0.22 | 0.26 | 0.29 |
| 6 | 0.28 | 0.33 | 0.40 | 0.48 |
| 7 | 0.46 | 0.55 | 0.66 | 0.77 |
| 8 | 0.74 | 0.92 | 1.10 | 1.29 |
| 9 | 1.10 | 1.38 | 1.65 | 2.02 |
| 10 | 1.65 | 2.02 | 2.57 | 3.13 |
| 11–14 | 2.76 | 3.31 | 4.23 | 5.15 |
| 15–19 | 4.60 | 5.51 | 6.99 | 8.27 |
| 20–30 | 7.35 | 9.19 | 11.03 | 13.79 |

#### Premium symbols — larger, less frequent

| Cluster size | `silver` | `gold` | `emerald` | `diamond` |
| --- | --- | --- | --- | --- |
| 5 | 0.55 | 0.92 | 1.47 | 2.21 |
| 6 | 0.92 | 1.47 | 2.39 | 3.68 |
| 7 | 1.47 | 2.39 | 4.04 | 6.43 |
| 8 | 2.39 | 3.68 | 6.43 | 10.11 |
| 9 | 3.68 | 5.88 | 10.11 | 15.63 |
| 10 | 5.51 | 9.19 | 14.71 | 22.98 |
| 11–14 | 9.19 | 14.71 | 23.90 | 36.77 |
| 15–19 | 14.71 | 23.90 | 36.77 | 58.82 |
| 20–30 | 23.90 | 36.77 | 58.82 | 91.91 |

#### Rare top symbol — highest regular-symbol pay

| Cluster size | `ingot` |
| --- | --- |
| 5 | 5.51 |
| 6 | 9.19 |
| 7 | 14.71 |
| 8 | 23.90 |
| 9 | 36.77 |
| 10 | 55.15 |
| 11–14 | 91.91 |
| 15–19 | 147.06 |
| 20–30 | 229.78 |

### 3.2 Rationale and intended contribution

- **Ordering** is monotonic by rarity: common symbols pay least but are
  weighted to form clusters most often; premium pay more and form clusters
  less often; `ingot` pays most and is rarest. Within a class, ordering
  follows the draft hierarchy (earth < stone < timber < copper; silver < gold
  < emerald < diamond).
- **Frequent visible small wins**: common symbols are weighted so that 5- and
  6- clusters are the most common win event, paying 0.10×–0.26×, i.e.
  frequently **below the play amount**. This is the product's main goal.
- **Intended RTP contribution (ASSUMPTION)**: common symbols are expected to
  contribute the majority of the base-game RTP; premium and `ingot` contribute
  a smaller share but add variance and the tail that reaches the 1,000× cap.
  Free spins add a separate feature contribution (see 3.3).
- The exact split of RTP between common / premium / ingot / free-spin is **not
  determined by the weights alone**: it depends jointly on the reel-strip
  arrangement (§4.1), the paytable and the tumble/cascade behaviour, and it
  must be **measured together in Stage 3**. The numbers above are the starting
  hypothesis, not a consequence of the weights (F8).

### 3.3 Hit-rate design targets (ASSUMPTION, not measured)

- **`P(payout > 0)` (visible hit)** — target **≈ 45%** per base round,
  spanning roughly 40–55%. **ASSUMPTION** — this is a joint target to be
  reached by calibrating the strip arrangement (§4.1), the weights and the
  paytable together; it is **not** a direct consequence of the combined common
  weight alone. To be verified by simulation.
- **`P(payout >= 1.0×)` (full return, i.e. returns at least the play amount)**
  — target **≈ 12–16%** per base round. A round at or above the play amount
  requires at least a mid-size cluster or a tumble sequence that sums past
  1.0×. **ASSUMPTION** — to be verified by simulation.
- **Joint calibration (F8).** The hit rate, full-return rate and RTP are
  coupled: raising hit rate tends to raise RTP and full-return rate, and
  shifting the paytable/weights to one target moves the others. They must be
  tuned **together** in a Stage 2/3 simulation on the exact strip in §4.1,
  rather than each being treated as an independent consequence of a single
  weight.
- Zero-win dry streaks are expected; even a 45% hit rate leaves meaningful
  10- and 20-round dry-streak probability, which Stage 3 must report rather
  than assume away.

**Measured outcome (Stage 3, 500,000 natural base rounds — see
`CALIBRATION_REPORT.md`).** On the calibrated paytable (§3.1, scale 1.0) the
measured visible hit is **≈ 69.9%** and the measured full-return is **≈ 29.2%**.
Both are **above** the design targets (45% and 12–16% respectively). This is a
**real conflict**, not a passing result: the common-symbol weight (≈65%) makes
sub-1.0× cluster wins so frequent that the visible hit is far above target, and
the tumble cascade frequently **sums several of those small wins past 1.0×**,
which lifts the full-return well above the 12–16% target. Resolving it would
require lowering the common-symbol weight and/or rebalancing the paytable,
which trades off the "frequent visible small wins" product goal. The Stage 3
decision is to **preserve** the frequent-visible-small-win character and
surface this as an **open conflict** for the orchestrator/product, rather than
distort the paytable to force the hit-rate target. See the report's "Conflicts
/ open decisions" section.

---

## 4. Reel / symbol weights

Weights are expressed as **counts on a reel strip** shared by all 6 reels. A
single shared strip is proposed for simplicity and symmetric cluster
formation; per-reel strips are a Stage 2 option if simulation shows a need to
shape column variance. Per-cell probability = count / strip length.

### 4.1 Base-game strip (length 200, shared across 6 reels)

| Symbol | Count | Weight | Expected cells / 30-cell board |
| --- | --- | --- | --- |
| `earth` | 36 | 18.0% | 5.40 |
| `stone` | 33 | 16.5% | 4.95 |
| `timber` | 31 | 15.5% | 4.65 |
| `copper` | 30 | 15.0% | 4.50 |
| `silver` | 16 | 8.0% | 2.40 |
| `gold` | 14 | 7.0% | 2.10 |
| `emerald` | 12 | 6.0% | 1.80 |
| `diamond` | 10 | 5.0% | 1.50 |
| `ingot` | 7 | 3.5% | 1.05 |
| `ore_vein` | 8 | 4.0% | 1.20 |
| `pickaxe` | 3 | 1.5% | 0.45 |
| **Total** | **200** | **100%** | **30.00** |

**Exact base-strip arrangement (F2).** Counts alone do not determine the
RTP/hit/feature behaviour; the **ordering** does. To make every claim in this
document reproducible and testable in Stage 2, the base strip is defined
exactly as the following ordered, 200-symbol list. All 6 reels read a
consecutive 5-symbol window from this single strip (plus top/bottom padding),
starting at a per-reel random offset, exactly as the engine's
`create_board_reelstrips` does (`sym_id = strip[(reel_pos + row) % 200]`).

```
earth,earth,timber,timber,stone,copper,copper,diamond,ingot,timber,
timber,stone,stone,pickaxe,earth,earth,stone,stone,earth,earth,
ore_vein,stone,stone,timber,timber,silver,ingot,timber,timber,copper,
copper,silver,copper,copper,copper,copper,ore_vein,timber,timber,emerald,
stone,stone,gold,ore_vein,stone,stone,silver,pickaxe,earth,earth,
silver,ingot,earth,earth,earth,earth,gold,timber,timber,silver,
diamond,diamond,timber,timber,ingot,earth,earth,diamond,timber,timber,
silver,gold,emerald,earth,earth,gold,emerald,emerald,copper,copper,
gold,earth,earth,stone,stone,silver,silver,copper,copper,gold,
stone,stone,silver,earth,earth,gold,emerald,emerald,diamond,copper,
copper,ore_vein,stone,stone,gold,copper,copper,timber,timber,silver,
pickaxe,timber,timber,silver,ore_vein,earth,earth,earth,earth,stone,
stone,stone,stone,ingot,timber,timber,copper,copper,silver,copper,
copper,ore_vein,copper,copper,stone,stone,stone,stone,earth,earth,
gold,earth,earth,silver,timber,timber,timber,timber,ore_vein,timber,
timber,diamond,ore_vein,stone,stone,gold,emerald,diamond,diamond,earth,
earth,stone,stone,silver,diamond,earth,earth,emerald,copper,copper,
timber,ingot,earth,earth,gold,gold,emerald,stone,stone,diamond,
earth,earth,silver,timber,timber,silver,emerald,copper,copper,copper,
copper,gold,ingot,copper,copper,emerald,stone,stone,gold,emerald
```

**Deterministic generation rule (reproducible, seed 20261117).** The ordered
list in the fenced block above is generated by the following exact Python code.
This code is the **authoritative definition** of the generation rule. The list
is not hand-edited: it is the output of `build_strip(20261117, BASE_COUNTS)`,
and re-running that call reproduces it byte-for-byte.

**SHA-256 of the base strip:**
`7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451`
(hash of the comma-joined 200-symbol list, UTF-8).

```python
import hashlib
import random

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
```

**Step-by-step summary (equivalent to the code).** (1) Each common symbol, in
`COMMON_ORDER`, is split into consecutive runs of 2 — a single if the count is
odd — giving 66 runs (130 common symbols) for the base counts. (2) Each
non-common symbol, in `NONCOMMON_ORDER`, contributes its count as individual
singles → 70 singles. (3) There are `len(runs)+1` = 67 gap buckets; every
single is placed into a uniformly random bucket via
`rng.randrange(len(buckets))`, in `NONCOMMON_ORDER` order, using
`random.Random(20261117)`. (4) The list of run indices `range(len(runs))` is
shuffled with the same RNG. (5) The strip is the concatenation, in shuffled run
order, of each run immediately followed by the singles in that run's gap
bucket; the singles in the final (last-index) bucket are appended last. Length
= 130 + 70 = **200**.

**ASSUMPTION**:
- Combined common weight ≈ 65% is high, giving frequent common clusters. This
  is one input to the ≈45% visible-hit target and the many sub-1.0× wins, but
  it is **not** sufficient by itself (F8): the hit rate also depends on the
  strip arrangement and the tumble loop.
- `ore_vein` ≈ 4% → ~1.2 vein cells per board.
- **Scatter rate (F1, corrected).** `pickaxe` ≈ 1.5% gives a natural 3+ scatter
  rate of **≈ 1.01% (about 1 in ~98.7 base spins)** under the binomial
  approximation, computed as `P(Binomial(30, 0.015) >= 3)`:
  - P(X=0) ≈ 63.55%, P(X=1) ≈ 29.03%, P(X=2) ≈ 6.41% ⇒ P(X ≥ 3) ≈ **1.01%**.
  - **Caveat (F2):** the binomial is only an **approximation**. The board is
    not 30 independent cells — each reel draws a **correlated 5-symbol window**
    from a shared 200-symbol strip, and windows can overlap. The true
    strip-based 3+ scatter rate must be measured on the exact strip above in
    Stage 2/3. The value may differ from ≈1.01% in either direction.
  - This ≈1.01% is the design-target feature-entry rate. **ASSUMPTION** — must
    be verified and tuned in simulation.
- **Natural triggering is intended.** In the reference engine
  (`board.draw_board`, lines 202–205) the base-game branch re-draws the board
  until it does **not** reach the scatter threshold — the `while
  count_special_symbols(trigger_symbol) >= min(...)` loop keeps calling
  `create_board_reelstrips()` while the board has ≥ the trigger count, i.e. it
  suppresses boards that would naturally trigger free spins. That re-draw is a
  betmode-calibration tool, not a game rule. For Block Cave the scatter
  **should** trigger naturally (no threshold re-draw suppression in the base
  game) so that 3+ pickaxes actually start free spins. This requires an engine
  change, named in §6 (F7).

### 4.2 Free-spin strip (length 200, shared across 6 reels)

Used for every free spin. Premium, `ingot` and `ore_vein` are boosted relative
to base to make free spins higher-variance and more rewarding; common symbols
are reduced accordingly.

| Symbol | Count | Weight | Expected cells / 30-cell board |
| --- | --- | --- | --- |
| `earth` | 30 | 15.0% | 4.50 |
| `stone` | 28 | 14.0% | 4.20 |
| `timber` | 26 | 13.0% | 3.90 |
| `copper` | 24 | 12.0% | 3.60 |
| `silver` | 18 | 9.0% | 2.70 |
| `gold` | 16 | 8.0% | 2.40 |
| `emerald` | 14 | 7.0% | 2.10 |
| `diamond` | 12 | 6.0% | 1.80 |
| `ingot` | 14 | 7.0% | 2.10 |
| `ore_vein` | 15 | 7.5% | 2.25 |
| `pickaxe` | 3 | 1.5% | 0.45 |
| **Total** | **200** | **100%** | **30.00** |

**Exact free-spin strip arrangement (F2).** Same shared-strip model as §4.1,
defined exactly as the following ordered, 200-symbol list. It is generated by
the same `build_strip(seed, counts)` function and symbol orders defined in
§4.1, using the free-spin counts and seed **20261118**:
`build_strip(20261118, FREE_COUNTS)`. The exact ordered list is the
authoritative artifact, and is re-derivable byte-for-byte from that call.

**SHA-256 of the free-spin strip:**
`f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754`
(hash of the comma-joined 200-symbol list, UTF-8).

```
earth,earth,ore_vein,stone,stone,silver,ingot,ingot,timber,timber,
silver,ingot,earth,earth,gold,diamond,ingot,ore_vein,pickaxe,copper,
copper,earth,earth,silver,earth,earth,copper,copper,silver,ingot,
ingot,timber,timber,gold,timber,timber,diamond,earth,earth,silver,
silver,gold,gold,emerald,emerald,timber,timber,ore_vein,ore_vein,timber,
timber,silver,emerald,earth,earth,emerald,stone,stone,diamond,stone,
stone,timber,timber,gold,ore_vein,stone,stone,stone,stone,silver,
earth,earth,silver,diamond,pickaxe,stone,stone,silver,emerald,ore_vein,
stone,stone,gold,copper,copper,emerald,copper,copper,gold,ingot,
ore_vein,pickaxe,copper,copper,diamond,diamond,timber,timber,emerald,earth,
earth,gold,gold,copper,copper,silver,ingot,earth,earth,silver,
gold,emerald,copper,copper,diamond,ore_vein,timber,timber,emerald,ore_vein,
copper,copper,silver,diamond,ore_vein,copper,copper,ingot,copper,copper,
ore_vein,ore_vein,copper,copper,silver,copper,copper,silver,stone,stone,
emerald,timber,timber,ore_vein,earth,earth,gold,emerald,earth,earth,
silver,stone,stone,gold,diamond,earth,earth,gold,emerald,diamond,
earth,earth,ore_vein,timber,timber,earth,earth,stone,stone,diamond,
ingot,stone,stone,gold,ingot,ore_vein,earth,earth,silver,timber,
timber,gold,stone,stone,timber,timber,emerald,stone,stone,silver,
gold,diamond,ingot,stone,stone,timber,timber,ingot,ingot,emerald
```

**ASSUMPTION**:
- Free-spin `ingot` (7%) and `ore_vein` (7.5%) are roughly double the base
  weights, so free spins are more likely to produce premium/ingot wins and
  vein upgrades. This is what makes free spins "worth" a feature while staying
  short.
- Free-spin `pickaxe` ≈ 1.5% gives a retrigger rate of **≈ 1.01% per free spin**
  (about 1 in ~98.7 free spins) under the same binomial approximation (F1
  caveat applies: the strip-based rate must be measured on the exact strip).

**Reproducibility / calibration note (F2).** Every RTP, hit-rate, full-return
and feature-rate figure in this document is a **design target (ASSUMPTION)**,
**not a measured result** for the exact strips in §4.1/§4.2. No simulation has
yet been run on these exact strips. Stage 2/3 must calibrate the weights and
paytable against these exact strips so that the measured total RTP falls in the
96.0–96.7% band while the visible-hit, full-return and feature-rate targets
are also met. Until that calibration run, no number here is a measured RTP.

---

## 5. Ore-vein (wild + upgrade) rules

This is the key mechanic. The rules below are a **proposal**; the exact
timing, targets, multiple-vein behaviour and book serialization require
math/frontend contract agreement before implementation (Section 8).

### 5.1 Wild role (regular cluster matching)

- `ore_vein` substitutes for **any regular symbol** when forming a cluster.
  This uses the engine's standard wild handling (`Cluster.get_clusters` /
  `in_cluster` with `wild_key="wild"`), so a vein joins the cluster of whatever
  regular symbol it is orthogonally connected to.
- The vein does **not** have its own paytable entry; it contributes to the
  cluster of the regular symbol it wilds for.
- A vein is **not** a wild for `pickaxe` (scatter) and is **not** a scatter.

### 5.2 Activation condition

- **A `ore_vein` activates when it is a member of a winning cluster** — i.e.
  when it helped a regular-symbol cluster reach 5+ orthogonally connected
  symbols that resolves and pays.
- A vein that is merely on the board but not part of any winning cluster does
  **not** activate (no upgrade, and it is not removed by an activation).
- A vein that is part of a losing (fewer-than-5) cluster does not activate.

**ASSUMPTION** — this ties the upgrade to the wild's actual participation,
which keeps the upgrade from firing on every board that merely contains a vein.
The exact effect on RTP and feature frequency must be simulated.

### 5.3 Upgrade target and cap

- On activation, the vein converts **1** (not 3) of its **orthogonally
  adjacent regular blocks** into the **`diamond`** (mid-premium symbol).
- `ore_vein` and `pickaxe` are **not** eligible targets (a vein does not
  upgrade another vein or a pickaxe).
- Regular blocks that are **already `diamond`** are not re-converted (no-op).
- If no eligible adjacent regular block exists, the activation converts nothing
  (cap is a maximum, not a minimum).
- **Target may be inside or outside the winning cluster (B).** The eligible
  adjacent regular block does not have to lie outside the winning cluster; a
  block that is itself part of the winning cluster is a valid target. If it is
  converted, the visual swap to `diamond` happens **immediately before** the
  cluster explodes (see §5.4). There is **no double-scoring**: `winInfo` already
  scored the cluster at that block's **original** symbol, and the converted
  `diamond` is not re-scored in the same win event.
- **Activated-but-nothing-converted is still an activation (A).** When a vein
  activates (it is a member of a winning cluster) but has no eligible adjacent
  regular block, it still counts as an activation and is still listed in
  `veinPositions` in the book event, even though `upgrades` has no entry for it
  (§8).

**Bounding the vein's RTP impact (F3).** Upgrading to the top `ingot` with a
cap of 3 was the dominant RTP-inflation risk: it could fabricate large
`ingot` clusters far more often than the weights would allow, and the previous
"low activation frequency" mitigation was not sufficient (the reference QA
simulation found ~0.58 vein activations per round, with ~35% of rounds
containing at least one activation). This revision changes two things:

1. **Target is `diamond`, not `ingot`.** `diamond` is a mid-premium whose top
   cluster pay is **50×** (20–30 cluster) vs `ingot`'s **125×**. Fabricated
   `diamond` clusters therefore inject far less RTP per activation than the
   original `ingot` version.
2. **Cap is 1, not 3.** Each activation converts at most one adjacent block, so
   a single vein can add at most one premium block per activation; large
   fabricated clusters are far less likely than with the 3-block cap.

These two changes together bound the upgrade's RTP contribution to a small
share. **ASSUMPTION / TARGET** — the exact contribution is not claimed here; it
must be **measured in Stage 2/3** on the exact strip in §4.1, and if the total
RTP still exceeds the 96.0–96.7% band, the base paytable/weights are tuned
downward (or the target lowered further to `emerald`) to **compensate**. This
design does **not** rely on a presumed low activation frequency to hold RTP in
band; it bounds the per-activation effect and then measures/compensates the
residual.

**ASSUMPTION** — upgrading to `diamond` keeps the "vein reveals rich ore"
theme while removing the largest RTP-inflation lever. The `ingot` top symbol
remains reachable only by natural weight. The exact effect on RTP and feature
frequency must be simulated.

### 5.4 Consumption / persistence

- The vein is **consumed** when it activates: because it is a member of the
  winning cluster, it **explodes/removes** with that cluster and is not
  replaced by a vein in the same spot.
- Therefore a vein acts **at most once** per round. It does not persist to a
  later tumble after activation.
- **Upgraded blocks** behave as follows (B):
  - An upgraded block that is **inside** the winning cluster is converted to
    `diamond`, then **explodes with the cluster**. Because `winInfo` already
    scored it at its **original** symbol, the visual swap is applied **right
    before** the cluster explodes, and the converted `diamond` is **not**
    re-scored in the same win event (no double-scoring).
  - An upgraded block that is **outside** the winning cluster **remains on the
    board as a `diamond`** and may form a new cluster in the next tumble
    evaluation (scored on the next tumble only).

### 5.5 Multiple-vein interaction and order

- Veins are processed in **deterministic scan order**: reel index ascending,
  then row index ascending.
- Each vein independently evaluates its own eligible adjacent regular blocks.
- If two veins both want to convert the **same** regular block, the
  **first-processed** vein wins; the block is converted once and the later vein
  skips it (it is already `diamond`).
- Upgrades **do not chain**: a converted `diamond` is not a vein, so it cannot
  trigger further conversions.
- The upgrade is resolved **before** the winning cluster is exploded, so an
  upgraded block that is adjacent to the vein but outside the cluster can remain
  for the next evaluation.

**ASSUMPTION** — the exact ordering and re-evaluation step (whether the
enlarged cluster is re-scored in the same win event or only in the next tumble)
needs a math/frontend contract decision. The proposal here is: the cluster is
scored at its original size, then the upgrade is applied, then the cluster
explodes; upgraded blocks that survive are only scored on the next tumble
evaluation.

### 5.6 Book recording

The engine records vein positions and upgraded symbol IDs in the book via a
new event type (Section 8). Proposed payload fields:
- vein position(s) (`reel`, `row`),
- each upgraded position and its new symbol ID (`reel`, `row`, `symbol`).

---

## 6. Pickaxe scatter + free spins

### 6.1 What counts (resolved Stage-2 question)

- **Pickaxes count only on the initial board of each spin** (a base spin or a
  free spin). Pickaxes that **tumble in** during a cascade **do not** count
  toward the trigger.
- Rationale: deterministic and simple, avoids the "scatter tumbled in during a
  base-game cascade" ambiguity described in the `0_0_cluster` readme, and
  matches the intuitive "three pickaxes on the opening board start free spins."

### 6.2 Accumulation (resolved)

- Pickaxes **do not accumulate** across tumbles. They are evaluated **once**,
  on the initial board of a spin. A cascade that later brings new pickaxes does
  not re-trigger or increase the trigger count.

### 6.2a Engine touchpoints required for natural triggering (F7)

The design rule above ("count pickaxes only on the initial board; no
accumulation across tumbles") is unambiguous as a *rule*, but the default
engine does **not** behave this way. Implementing it requires **real
engine-code changes** in Stage 2:

- **(a) Remove/relax the `draw_board` re-draw suppression loop** in
  `math/src/calculations/board.py` (around lines 201–205). In the base-game
  branch, `draw_board` loops `create_board_reelstrips()` while
  `count_special_symbols(trigger_symbol) >= min(freespin_triggers)`, i.e. it
  keeps re-drawing the board until it has **fewer than** the trigger threshold.
  That suppresses natural scatter-triggered free spins. For Block Cave this
  loop must be removed (or disabled for the base game) so that a board drawn
  with 3+ pickaxes is revealed and can trigger free spins naturally.
- **(b) Override/adapt `check_fs_condition`** in
  `math/src/executables/executables.py` (lines 43–49). The default
  `check_fs_condition` calls `count_special_symbols("scatter")`, which reads
  `self.special_syms_on_board["scatter"]`; that list is refreshed by
  `get_special_symbols_on_board()` inside `tumble_board()` on **every cascade**.
  So the engine counts scatters on the **post-tumble** board, not the initial
  board. To implement "initial-board-only, no accumulation", Block Cave must
  override `check_fs_condition` (or capture the initial-board scatter count
  before any cascade) so that scatter counting evaluates only the **initial**
  board of each spin.
- The `0_0_cluster` `readme.txt` note about "scatter symbols tumbling onto the
  board during basegame criteria" is exactly the behaviour this design removes.

These are engine touchpoints, not game rules; they are listed here so Stage 2
knows the default behaviour must be changed.

### 6.3 Minimum trigger and scaling

- **3 pickaxes** is the trigger threshold.
- More pickaxes award more starting spins. Proposed table (**ASSUMPTION**):

| Pickaxes on initial board | Starting free spins |
| --- | --- |
| 3 | 8 |
| 4 | 12 |
| 5 | 16 |
| 6+ | 16 (capped) |

- A board with **fewer than 3** pickaxes does not trigger free spins.
- The pickaxe is **not** a wild and pays **nothing** by itself; it is purely a
  trigger. No scatter pay is awarded for 2 or fewer pickaxes.

### 6.4 Retrigger and cap

- During a free spin, **3+ pickaxes on that free spin's initial board** trigger
  a retrigger, adding the corresponding number of spins from the table above
  (8 / 12 / 16) to the remaining total.
- **Hard cap**: total free spins in one feature is capped at **60**. If a
  retrigger would exceed 60, it is clamped to 60 (no further retriggers once at
  the cap).
- **ASSUMPTION** — the starting-spin counts and the 60-spin cap are proposals;
  simulation must verify feature length, average/median payout and the cap's
  effect on the max-win tail.

### 6.5 Feature-rate and payout targets (ASSUMPTION)

- **Entry frequency** target: **≈ 1.0%** of base spins (≈ 1 in ~100), consistent
  with the corrected natural 3+ scatter rate in §4.1 (≈1.01% binomial
  approximation). **ASSUMPTION** — the exact strip-based entry rate must be
  measured on the exact strip; it may differ from the binomial value.
- **Expected free-spin average payout**: target **≈ 8–12×** the play amount per
  triggered feature, with **median** lower (≈ 5–7×) because the distribution is
  right-skewed toward the cap. **ASSUMPTION** — must be measured.
- The free-spin contribution to total RTP is intended to be a meaningful share
  (see 3.3) but the exact split is a Stage 3 measurement.

---

## 7. 1,000× round cap

- **Cap value (hard upper bound)**: **1,000×** the base play amount =
  **100,000** serialized units (`int(round(1000.0 * 100, 0))`). This is the
  **maximum** any single round may pay; it is a **safety ceiling**, not a
  design target (F4). **No top pay in the paytable was raised to reach it.**
- **Where applied**: the cap is applied to the book-level `payoutMultiplier`.
  The engine's `wincap` mechanism clamps the serialized `payoutMultiplier` to
  `wincap * 100` units. For Block Cave `wincap = 1000.0`.
- **Sum-then-cap (chosen behaviour)**: all wins in a round — base-cluster wins,
  tumble wins, and all free-spin wins — are **summed first**, and the total is
  then clamped to 1,000×. This matches the engine's `set_total_event` /
  `final_win_event` behaviour, which clamps `running_bet_win` (the cumulative
  round total) to `wincap`.
- **Per-segment capping (F10)**: the engine *does* clamp each individual win
  amount to `wincap` in `win_info_event` (`min(win, wincap) * 100`),
  `set_win_event` and `set_total_event`. For Block Cave, **individual wins are
  below the cap in practice** (the largest single cluster pay is `ingot`
  20–30 = 125×, and the vein upgrade now targets `diamond`, whose top pay is
  50×), so that per-segment clamp **never binds**. Only the **cumulative round
  total** is clamped to 1,000×. In short: individual wins are far below the cap;
  only the running round total can be clamped to 1,000×.
- **Expected max-win frequency (ILLUSTRATION, not measured)**: with a bounded
  `diamond` upgrade, short 8–16-spin free spins averaging ≈8–12×, and no
  mechanism to force large wins, the 1,000× cap is **expected to bind rarely or
  never** in the base game. As an **ILLUSTRATION** of the order of magnitude
  (not a measured result for Block Cave), the independent QA simulation of a
  comparable moderate strip reported a max single-round base win of
  **≈ 205.78×**, with **P(≥100×) ≈ 0.005%**, **P(≥500×) = 0%** and
  **P(≥1000×) = 0%**. These figures are **arrangement-dependent** and are shown
  only to illustrate that the cap is far above typical outcomes. Stage 2/3 must
  report the actual maximum-win frequency on the exact strip in §4.1.
- **Interaction with free spins**: the free-spin wins are added to the same
  running round total as the base win, and the combined total is clamped to
  1,000×. So a triggering base spin plus its free spins cannot exceed 1,000×.
- **Interaction with the ore-vein upgrade**: a `diamond` cluster produced by an
  upgrade can contribute to a larger round; the 1,000× clamp bounds the final
  payout regardless of how the win arose.
- **ASSUMPTION** — confirm the exact unit semantics against the SDK serializer
  (`int(round(multiplier * 100, 0))`) and the engine `wincap` path before
  implementation. The current reference (`game_config.py`, `wincap = 5000.0`)
  is a different game and is not a precedent for Block Cave's 1,000× value.

---

## 8. Provisional event schema

**PROVISIONAL.** Requires math/frontend agreement before implementation
(`ENGINE_CONTRACT.md`: custom event changes require explicit math/frontend
agreement). Event `type` strings and payload shapes below are proposals. The
frontend replays these in order and must never invent a payout or symbol
outcome. `payoutMultiplier` is serialized as an **integer at 100 units per
multiplier** (`books.py`).

Standard engine events (reused, exact shape from `src/events/events.py` and
`src/events/event_constants.py`):

**Emission order (F5).** The table below mirrors the real engine emission
sequence for Block Cave, which is a tumble game. The per-cascade group is
`reveal` → `winInfo` → `updateTumbleWin` → [`wincap`] → [`oreVeinUpgrade`] →
`tumbleBoard`, and the group repeats until no further win; then `setWin` →
`setTotalWin`; then the free-spin feature runs (per spin, `updateFreeSpin` →
`reveal` → the same cascade group → `setWin` → `setTotalWin`, with an optional
`freeSpinRetrigger`); the feature closes with `freeSpinEnd`; and the round
closes with `finalWin`. This matches the engine's
`executables.emit_tumble_win_events` (`win_info_event` → `update_tumble_win_event`
→ `evaluate_wincap`) followed by `tumble_game_board` (`tumble_board_event`),
then `tumble.set_end_tumble_event` (`set_win_event` → `set_total_event`), then
the freespin path and `evaluate_finalwin`.

| Order | `type` | Notes / payload |
| --- | --- | --- |
| 1 | `reveal` | Initial 6×5 board; `board`, `paddingPositions`, `gameType`, `anticipation`. |
| 2 (repeat per cascade) | `winInfo` | A cluster win; `totalWin`, `wins[]` (symbol, clusterSize, positions, meta). Emitted after cluster resolution. |
| 3 (per cascade) | `updateTumbleWin` | Running tumble-win banner `amount`. **Emitted right after `winInfo`, before `tumbleBoard`.** |
| 3a (per cascade) | `wincap` | Only when `running_bet_win` **first crosses** the 1,000× cap **during the cascade**, not at the end. **New frontend requirement (C):** `wincap` is absent from the cluster `BookEvent` union, so the frontend must add a `wincap` union member + handler branch (like `oreVeinUpgrade`), otherwise it is silently skipped. |
| 3b (per cascade) | `oreVeinUpgrade` | **NEW** — only when a vein activates. Placed **between `updateTumbleWin` and `tumbleBoard`**, consistent with "cluster scored at original size, then upgrade applied, then cluster explodes" (§5.5). |
| 4 (per cascade) | `tumbleBoard` | Removed/exploding symbols and the new symbols that fall in. |
| 5 | `setWin` | End-of-tumble `amount`, `winLevel` (omitted when the spin win is 0). **This event was missing from the earlier table.** |
| 6 | `setTotalWin` | Cumulative round total, clamped to 1,000× (100,000 units). |
| 7 | `freeSpinTrigger` | Base→feature entry; `totalFs`, `positions` (initial pickaxe positions). |
| 8 (repeat per free spin) | `updateFreeSpin` | Current free spin number and total. |
| 8a (repeat per free spin) | `reveal` | Free-spin board. |
| 8b (repeat cascade) | `winInfo` → `updateTumbleWin` → [`wincap`] → [`oreVeinUpgrade`] → `tumbleBoard` | Same cascade group as the base spin. |
| 8c (per free spin) | `setWin` → `setTotalWin` | End-of-tumble for that free spin. |
| 8d | `freeSpinRetrigger` | When 3+ initial pickaxes on that free spin; `totalFs`, `positions`. |
| 9 | `freeSpinEnd` | Feature end; total free-spin amount, `winLevel`. |
| 10 | `finalWin` | Final `amount` = round payout multiplier (clamped to 100,000 units). |

> `wincap` is **not** emitted at the end of the event list. It is emitted
> mid-cascade, inside `emit_tumble_win_events`, immediately after
> `updateTumbleWin`, when `running_bet_win` first reaches the cap.
>
> **Frontend handling (C).** `wincap` is **not** present in the cluster
> `BookEvent` union (`frontend/apps/cluster/src/game/typesBookEvent.ts`) and
> `bookEventHandlerMap.ts` has **no** `wincap` branch. Because that handler map
> is a `Record` (not an exhaustive mapped type), a missing branch is a **runtime
> silent-skip**, not a compile error. The frontend must therefore add a `wincap`
> union member + a handler branch (the same new-type requirement as
> `oreVeinUpgrade`) so the cap-crossing is not silently dropped. The payout
> total remains correct even if `wincap` were skipped, because `setTotalWin` and
> `finalWin` already carry the clamped cumulative total — but the mid-cascade
> cap signal is only surfaced if `wincap` is handled.

**New/proposed event for Block Cave** (`oreVeinUpgrade`) — **F6 contract draft**:

```json
{
  "index": 3,
  "type": "oreVeinUpgrade",
  "veinPositions": [{ "reel": 2, "row": 4 }],
  "upgrades": [
    { "reel": 1, "row": 4, "symbol": "diamond" }
  ]
}
```

**Contract definition (F6):**

- **`type` string:** `"oreVeinUpgrade"`.
- **Payload fields:**
  - `veinPositions: { reel: number; row: number }[]` — the position(s) of each
    vein that activated in this cascade step, in the deterministic scan order of
    §5.5 (reel ascending, then row ascending). Matches the `Position` type.
  - `upgrades: { reel: number; row: number; symbol: SymbolName }[]` — the
    position(s) of each block converted by an activation and the **new** symbol
    ID it becomes. For this design the symbol is always `diamond` (F3); the
    field is generic so the target could be re-parameterised. Only one entry per
    activation (cap = 1, §5.3).
- **Cardinality (A).** `upgrades` contains **only the blocks actually
  converted** — exactly one entry per real conversion — so
  **`upgrades.length <= veinPositions.length`**. A vein that activates but
  converts nothing is **still listed in `veinPositions`** (it activated; it just
  had no eligible adjacent regular block, §5.3), so `veinPositions` and
  `upgrades` are **not** the same length in general. The frontend must **not**
  assume `veinPositions.length === upgrades.length`.
- **Coordinate convention:** the same **padded row** convention used by
  `winInfo`, `tumbleBoard` and `freeSpinTrigger` positions. The engine's
  `win_info_event` and `tumble_board_event` add **+1 to `row`** when
  `include_padding=True`, so the serialized board shows the visible 5 rows at
  `row` 1–5 with padding at 0 and 6. The frontend `Position` type
  (`frontend/apps/cluster/src/game/types.ts`, `{ reel: number; row: number }`)
  consumes these coordinates directly, and the `reveal` board array is indexed
  in the same padded convention. `veinPositions` and `upgrades[].{reel,row}`
  therefore use **0-based `reel` and the padded (row+1) `row`**, matching the
  positions emitted in `winInfo`/`tumbleBoard`.
- **Position in the sequence:** between `updateTumbleWin` and `tumbleBoard`
  (order 3b above), so the cluster is scored at its original size, the upgrade
  is applied, then the cluster explodes.
- **This is a genuinely NEW SDK event type (F6).** It is **not** present in
  `frontend/apps/cluster/src/game/typesBookEvent.ts`, whose `BookEvent` union
  includes `reveal`, `winInfo`, `updateTumbleWin`, `setTotalWin`,
  `freeSpinTrigger`, `updateFreeSpin`, `updateGlobalMult`, `freeSpinEnd`,
  `tumbleBoard`, `finalWin`, `setWin`, `updateGrid`, `freeSpinRetrigger`,
  `createBonusSnapshot` — but **not** `oreVeinUpgrade`. Implementing it requires
  **both** sides to change:
  - **Python (math):** a new event constant/emitter (mirroring
    `game_events.update_grid_mult_event`) that writes `type: "oreVeinUpgrade"`.
  - **Frontend:** a new `BookEventOreVeinUpgrade` member in the `BookEvent`
    union in `typesBookEvent.ts` and a new handler branch in
    `bookEventHandlerMap.ts` (to visually convert the adjacent blocks).
  - This contract must be **agreed with the frontend agent next** and validated
    against a real generated book before any book is produced (Stage 5).

**ASSUMPTION** — the exact event type string, payload field names, coordinate
convention and ordering must be agreed with the frontend and validated against
real generated books before implementation.

---

## 9. Open decisions / open questions

- **Final game title** and **final fantasy-alloy name** (display name for
  `ingot`). These block production art and public copy.
- **Whether a separately priced bonus mode is in v1.** Out of scope for the
  Stage 1 base-game design; if added, it needs its own full outcome
  distribution, cost, RTP, max win and confirmation UI.
- **The ore-vein upgrade is a normal in-round mechanic, not a free-spin bonus
  upgrade (corrected).** The ore-vein symbol's conversion of an adjacent
  regular block is an **ordinary mechanic within the round**, like the wild
  matching and the tumble. It is automatic, predetermined and stateless (no
  player-selected wager/upgrade, F9). It is **not** a "bonus upgrade" and is
  **not** the deferred free-spin bonus-tier upgrade. The separate product
  preference for a "free-spin bonus upgrade that retains a small guaranteed
  win" remains a **distinct, deferred research item** that still needs
  platform confirmation before any implementation (per `GAME_SPEC.md` and
  `PROJECT_PLAN.md`). By contrast, the ore-vein conversion is already part of
  the approved game concept and is assessed with the other in-round
  mechanics.
- **Upgrade target/cap (revised, F3).** The current proposal is: upgrade to
  `diamond` (mid-premium) with a cap of **1** adjacent block per activation, to
  bound RTP inflation. **Open:** confirm the target symbol and cap with the
  product/orchestrator, and confirm the resulting RTP contribution after a
  Stage 2/3 measurement. **Fallback** if RTP still exceeds the 96.0–96.7% band:
  lower the target to `emerald`, or gate activation harder (e.g. require the
  activating cluster to be ≥6 symbols), or tune the base paytable/weights down.
- **Upgrade scoring timing.** Whether the enlarged cluster (after an upgrade) is
  re-scored in the same win event or only on the next tumble. The proposal is
  "next tumble only"; this must be confirmed with the frontend.
- **`oreVeinUpgrade` contract (F6, frontend-AGREE-with-corrections).** The
  contract is now clarified: **(A)** `upgrades` holds only the blocks actually
  converted, so `upgrades.length <= veinPositions.length`, and a vein that
  activates but converts nothing is still listed in `veinPositions` (the
  frontend must not assume the two arrays are the same length); **(B)** an
  upgrade target may be inside **or** outside the winning cluster, with an
  in-cluster target swapped to `diamond` immediately before the cluster explodes
  (no double-scoring); and **(C)** the frontend must add a `wincap` union member
  + handler branch. The exact event type string, payload field names, coordinate
  convention (padded row) and ordering still need final agreement with the
  frontend agent, plus a new `oreVeinUpgrade` handler branch + `BookEvent` union
  member. This is a Stage 5 gate before any book is produced.
- **Single vs. per-reel strips.** Proposed single shared strip; per-reel strips
  remain an option if simulation shows the need to shape column variance. The
  exact strips in §4.1/§4.2 are the reproducible baseline for Stage 2.
- **Engine changes for natural triggering (F7).** Confirming the removal of the
  `draw_board` re-draw suppression loop and the override of `check_fs_condition`
  (initial-board counting) as real engine-code changes in Stage 2.
- **Least-certain numbers**: free-spin average/median payout, feature rate,
  visible-hit rate and the RTP contribution of the ore-vein upgrade. All of
  these need Stage 3 simulation on the exact strips in §4.1/§4.2.

---

## 10. Assumptions ledger

| # | Assumption | How it is verified in Stage 2/3 |
| --- | --- | --- |
| 1 | Paytable values (Section 3) produce ≈ 96.3% RTP. | **Stage 3 (done):** the §3.1 paytable at **scale 1.0** — no scale factor is applied; the C2 ×`F=1.8332663803148458` scale-up was **reverted** as wrong. Measured natural base-game RTP ≈ **0.964** on 500,000 rounds (95% CI [0.959, 0.970]), inside the 96.0–96.7% band at the point estimate (see `CALIBRATION_REPORT.md`). |
| 2 | Visible hit `P(payout > 0)` ≈ 45%. | **Stage 3 (measured, NOT met):** ≈ 69.9% — above the 40–55% target. Surfaced as an open conflict; see §3.3. |
| 3 | Full-return `P(payout >= 1.0×)` ≈ 12–16%. | **Stage 3 (measured, NOT met):** ≈ 29.2% — above the 12–16% band. Surfaced as an open conflict; see §3.3. |
| 4 | Common-symbol weight ≈ 65% yields frequent small wins without inflating RTP. | Stage 3 simulation: tune weights **and the strip arrangement together** to hit the hit-rate and RTP targets (F8). |
| 5 | Base `pickaxe` weight 1.5% → natural 3+ scatter rate ≈ **1.01%** (binomial approximation, F1). | Stage 3 simulation: measure the **strip-based** entry frequency on the exact strip in §4.1; adjust weight or use a distribution quota. |
| 6 | Natural scatter triggering (no threshold re-draw suppression). | Stage 2: **remove/relax the `draw_board` re-draw suppression loop** (`board.py` ~201–205) and verify with a forced-scatter book (F7). |
| 7 | Free-spin strip boosts premium/ingot/ore-vein. | Stage 3 simulation: compare free-spin average/median vs. base. |
| 8 | Vein activation = "member of a winning cluster". | Stage 3 simulation: measure activation frequency and RTP contribution. |
| 9 | Vein upgrades **1** adjacent regular block to **`diamond`** (F3). | Stage 3 simulation: measure RTP impact; lower target to `emerald`, gate activation, or tune the paytable/weights down if over the 96.0–96.7% band. |
| 10 | Vein is consumed on activation; upgraded blocks may survive to next tumble. | Stage 2 book tests: verify consumption and surviving upgraded blocks. |
| 11 | Multiple veins process in scan order, first-processed wins shared blocks. | Stage 2 book test with a designed multi-vein board; confirm deterministic order. |
| 12 | Pickaxes count only on the initial board; no accumulation across tumbles. | Stage 2 book test with a designed cascade that introduces pickaxes mid-tumble; **requires overriding `check_fs_condition`** to evaluate the initial board (F7). |
| 13 | Trigger table 3/4/5 → 8/12/16 spins; 6+ capped at 16. | Stage 3 simulation: measure feature length; adjust if too long/short. |
| 14 | Retriggers during free spins; hard cap 60. | Stage 3 simulation: measure retrigger frequency and cap effect. |
| 15 | Free-spin average payout ≈ 8–12×, median ≈ 5–7×. | **Stage 3 (measured, see report):** on the calibrated paytable the forced-freegame feature payout mean ≈ 9.7× and median ≈ 7.6× — inside the target range. |
| 16 | Round cap applied sum-then-cap at 1,000× (100,000 units); individual wins are below the cap in practice (F10). | Stage 2/3: verify serialized `payoutMultiplier` never exceeds 100,000 and matches book events. |
| 17 | The exact strip arrangements in §4.1/§4.2 are reproducible (F2). | Re-derive both strips from the documented seed + algorithm; run Stage 2/3 simulation on them. |
| 18 | The 1,000× cap is a safety ceiling not expected to bind (F4). | **Stage 3 (measured):** max observed round win ≈ 544× and P(≥1000×) = 0 on 500,000 natural rounds, so the cap does not bind. |
| 19 | `oreVeinUpgrade` event type, payload and ordering (F6). | Math/frontend agreement; add the `BookEvent` union member + handler branch; validate against real generated books. |
| 20 | The game is stateless with no player-selected wager/upgrade (F9); the ore-vein upgrade is a normal in-round mechanic, not a free-spin bonus upgrade. | No player-choice state in the game. Platform confirmation applies only to the separate, deferred free-spin bonus-tier upgrade, not to the ore-vein conversion. |

---

*End of Stage 1 math design proposal. All numeric values are proposals marked
ASSUMPTION; no measured RTP or hit rate is claimed. This is not a production
distribution.*
