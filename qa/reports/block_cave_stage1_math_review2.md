# QA Re-review — Stage 1 Block Cave math design (revised)

**Reviewer:** Independent QA agent (not the design author)
**Date:** 2026-11-17
**File under review:** `math/games/block_cave/MATH_DESIGN.md` (NOT modified by QA)
**Prior review:** `qa/reports/block_cave_stage1_math_review.md` (kept intact)
**Method:** Independent re-review of the revised design against the engine facts
(`math/src/state/books.py`, `math/src/events/events.py`,
`math/src/events/event_constants.py`, `math/src/executables/executables.py`,
`math/src/calculations/tumble.py`, `math/src/calculations/board.py`), the docs
(`GAME_SPEC.md`, `PROJECT_PLAN.md`, `ENGINE_CONTRACT.md`), and the frontend
contract (`frontend/apps/cluster/src/game/typesBookEvent.ts`,
`bookEventHandlerMap.ts`, `types.ts`). Independent scripts were written to
re-derive the §4.1/§4.2 strips from the documented seed + algorithm, to recompute
the scatter rate, and to estimate the vein RTP contribution. No implementation
files were modified; the design file was not touched.

---

## Verdict

**NOT READY FOR STAGE 2** — but only by a narrow, single-item margin.

Every original critical finding is resolved *except* **F2's reproducibility
guarantee**: the design now pins the strip down with an explicit ordered
200-symbol list (good) **and** a deterministic generation rule (seed 20261117 /
20261118). The declared lists are length-200 and their symbol counts match the
weight tables exactly, **but the documented generation rule does NOT reproduce the
declared ordered lists under any faithful reading or any seed I searched**. Per
the review criteria, an unreproducible strip is a critical blocker. This is a
small, mechanical fix (correct the algorithm/seed, or drop the false
"re-derivable exactly as follows" claim and state the explicit list is the sole
source). Once fixed, the design is otherwise ready for Stage 2.

The frontend-contract corrections (A)/(B)/(C) are present and coherent, and the
event ordering, vein bound, hard-cap labelling, joint-calibration wording,
statelessness affirmation, and engine touchpoints are all correctly addressed.

---

## Original findings (F1–F10)

| # | Finding (prior review) | Status | Evidence |
| --- | --- | --- | --- |
| F1 | Scatter arithmetic error (0.8% vs 1.01%) | **RESOLVED** | §4.1 now states **≈1.01% (1 in ~98.7)** with the binomial caveat. Independent recompute: P(X=0)=63.5458%, P(X=1)=29.0311%, P(X=2)=6.4104%, **P(X≥3)=1.0127% (1 in 98.7)**. Matches. |
| F2 | Reel-strip arrangement unspecified; all numbers unverifiable | **PARTIALLY RESOLVED** | The arrangement is now explicit (full 200-symbol ordered lists in §4.1/§4.2, counts verified exact). **However the documented deterministic generation rule (seed 20261117/20261118) does NOT reproduce the declared ordered lists** — see the reproducibility check below. Counts/length PASS; order re-derivation FAIL. |
| F3 | Ore-vein→`ingot` upgrade is dominant RTP-inflation risk; mitigations insufficient | **RESOLVED** | §5.3 changes target to **`diamond`** (mid-premium, top 50×, not `ingot` 125×), **cap reduced to 1**, and the invalid "low activation frequency" mitigation premise is removed; the RTP contribution is now described as measured-and-compensated. My ILLUSTRATION Monte Carlo on the exact §4.1 strip gives a vein inflation of ≈ **0 pp** (not the prior +14 pp), confirming the inflation lever is bounded. See below. |
| F4 | 1,000× cap effectively unreachable / unstated frequency | **RESOLVED** | §7 restates the cap as a **hard safety upper bound, not a target**; "No top pay in the paytable was raised to reach it"; the max-win frequency (205.78×, P(≥100×)≈0.005%, P(≥500×)=0%, P(≥1000×)=0%) is explicitly labelled **ILLUSTRATION, not measured** and marked arrangement-dependent. |
| F5 | Event-ordering table did not match the engine sequence | **RESOLVED** | §8 table now mirrors the engine: per-cascade `winInfo` → `updateTumbleWin` → [`wincap`] → [`oreVeinUpgrade`] → `tumbleBoard`, then `setWin` → `setTotalWin`. Verified against `executables.py` (`emit_tumble_win_events` = win_info → update_tumble_win → evaluate_wincap; `tumble_game_board` = tumble → tumble_board_event) and `tumble.py` (`set_end_tumble_event` = set_win → set_total). `wincap` correctly placed mid-cascade. |
| F6 | `oreVeinUpgrade` is a genuinely new event type; contract must be agreed | **RESOLVED** | §8 provides a concrete implementable draft (type string `"oreVeinUpgrade"`, payload `veinPositions`/`upgrades` with `{reel,row,symbol}`), coordinate convention, ordering, and the A/B corrections. Confirmed `oreVeinUpgrade` is absent from `typesBookEvent.ts` `BookEvent` union and `event_constants.py`, so it is genuinely new. |
| F7 | Design's initial-board-only scatter rule conflicts with engine default | **RESOLVED** | §6.2a explicitly names both engine touchpoints: **(a)** remove/relax the `draw_board` re-draw suppression loop in `math/src/calculations/board.py` (~lines 201–205) and **(b)** override/adapt `check_fs_condition` in `math/src/executables/executables.py` (lines 43–49) for initial-board counting. Both verified in source. |
| F8 | Hit/RTP described as consequences of the weights | **RESOLVED** | §3.2/§3.3 now state hit-rate, full-return and RTP are **coupled and must be jointly calibrated** via simulation on the exact strip, not consequences of the weights. |
| F9 | Statelessness not explicitly addressed | **RESOLVED** | §1 now has an explicit **"Stateless (F9)"** statement; no player-selected wager/gamble/continuation/cashout; the automatic in-book upgrade is flagged as needing platform confirmation. |
| F10 | "Per-segment capping is NOT used" technically inaccurate | **RESOLVED** | §7 reworded to "individual wins are below the cap in practice; only the cumulative round total is clamped to 1,000×", consistent with `win_info_event`/`set_win_event`/`set_total_event` `min(win, wincap)*100` clamps. |

---

## Frontend contract corrections (A) / (B) / (C)

| Correction | Status | Evidence |
| --- | --- | --- |
| **(A)** `upgrades` vs `veinPositions` cardinality | **Confirmed** | §5.3 and §8 state `upgrades` holds only blocks actually converted, so `upgrades.length <= veinPositions.length`; an activating vein that converts nothing is still listed in `veinPositions`; the frontend must not assume equal lengths. Coherent and correct. |
| **(B)** Upgrade target inside OR outside the winning cluster | **Confirmed** | §5.3/§5.4 state an in-cluster target is swapped to `diamond` immediately before the cluster explodes with **no double-scoring** (winInfo already scored it at the original symbol); out-of-cluster targets remain and are scored next tumble. Coherent. |
| **(C)** `wincap` frontend handler requirement | **Confirmed** | §8 correctly identifies that `wincap` is **absent** from the cluster `BookEvent` union (`typesBookEvent.ts`) and has **no branch** in `bookEventHandlerMap.ts`, and that because the handler map is a `Record` (not exhaustive) the missing branch is a **runtime silent-skip**. The design requires a `wincap` union member + handler branch (chosen over dropping the event). Verified directly in the frontend sources. |

The frontend agent's three corrections are faithfully incorporated.

---

## Independent strip-reproducibility check (F2)

A standalone Python script was written (QA-only, in the session temp dir) to
re-derive each strip from the documented 5-step algorithm + seed, assert length
200, and assert the symbol counts match the declared weight tables.

**Output:**

```
===== BASE STRIP (seed 20261117) =====
declared length: 200
declared length 200: OK
derived length: 200
derived length 200: OK
ORDERED LIST MATCH: FAIL (first divergence at index 2)
  derived[2] = ore_vein
  declared[2] = timber
counts match weight tables: PASS
total expected symbols: 200 (should be 200)

===== FREE-SPIN STRIP (seed 20261118) =====
declared length: 200
declared length 200: OK
derived length: 200
derived length 200: OK
ORDERED LIST MATCH: FAIL (first divergence at index 2)
  derived[2] = gold
  declared[2] = ore_vein
counts match weight tables: PASS
total expected symbols: 200 (should be 200)

base run count: 66 (design says 66)
  pairs=64 singles=2 common symbols=130
```

**Result: FAIL (re-derivation).** Both declared strips are exactly 200 symbols and
their counts match the weight tables, and the run decomposition is structurally
consistent (66 runs = 64 pairs + 2 singles, 130 common + 70 non-common). But the
documented seed + algorithm **does not** reproduce the declared ordered lists.

To be fair and rule out an ambiguous reading of the algorithm, I tested multiple
faithful interpretations (gap-after-run, gap-before-run, shuffle-before-gap,
original-index gap, no-shuffle) and **none** matched. I also brute-force searched
seeds 0–500,000 for the literal documented model and 0–200,000 for two variants:
**no seed reproduced the declared list.** This indicates the declared lists were
not generated by the documented procedure at all — the generation rule is a
post-hoc rationalisation that does not match its own artifact.

**Implication for Stage 2/3:** The explicit ordered list is present and correct, so
a simulation *can* run on it by hardcoding the list. But the design makes a false
claim ("it can be re-derived exactly as follows"), and anyone following the
documented rule would silently generate a **different** strip and produce
non-reproducible, off-spec results. This is the remaining critical blocker.

---

## Scatter-rate recompute (F1)

Independent computation of `P(Binomial(30, 0.015) >= 3)`:

| Quantity | Value |
| --- | --- |
| P(X=0) | 63.5458% |
| P(X=1) | 29.0311% |
| P(X=2) | 6.4104% |
| **P(X ≥ 3)** | **1.0127% (1 in 98.7)** |

Matches the design's corrected ≈1.01% / 1-in-98.7. **RESOLVED.**

---

## Vein RTP contribution (F3) — ILLUSTRATION

I ran a small Monte Carlo on the exact declared §4.1 base strip (200 symbols,
sample 200,000, seed 20261117, 6 reels × 5 rows, orthogonal 5+ clusters,
ore_vein as wild, vein activates when a winning-cluster member, converts 1
adjacent block to `diamond`, consumed on activation; tumble preserves surviving
cells). **This is labelled ILLUSTRATION**: it is an independent QA estimate, not
the official Block Cave measurement (which requires the real engine + full book
path). Full reproducibility parameters (strip, seed, sample) are given above so
the number is checkable.

**Output:**

```
[ILLUSTRATION] RTP without vein upgrade : 45.55%
[ILLUSTRATION] RTP with vein upgrade    : 44.76%
[ILLUSTRATION] vein inflation (pp)      : -0.79 pp (-1.74% relative)
vein activations/round (upgrade run)    : 1.013  (fraction of rounds with activation: 57.30%)
```

**Interpretation:** The vein upgrade's RTP contribution is now **≈ 0 pp** (slightly
negative in this model), a dramatic change from the prior **+14.24 pp** inflation
with the old `ingot`/cap-3 rule. The diamond/cap-1 change successfully removes the
dominant inflation lever, so the upgrade no longer threatens to push the game out
of the 96.0–96.7% band on its own. This supports the design's decision to bound the
per-activation effect and then measure/compensate the residual rather than rely on
a presumed low activation frequency.

Two caveats worth recording (not blockers):
- My ILLUSTRATION found **~1.01 activations/round** and **~57.3% of rounds** with at
  least one activation on the declared strip — **higher** than the ~0.58/round and
  ~35% figure the design cites from the prior reference QA (which was on a different,
  "moderate" strip). This does not reintroduce the RTP risk (per-activation effect is
  bounded to 1 diamond), but the design should not cite the old activation frequency
  as if it were the declared strip's.
- The absolute base RTP (~45.6% in this model, no free spins) is **not** a Block Cave
  measurement and is model-sensitive; it is far below the 84–88% base-game figure the
  design implies is needed. This only reinforces that Stage 3 must calibrate RTP on the
  exact strip; it is not a Stage-2 blocker because the design already defers RTP to
  Stage 3.

---

## Measurement-honesty scan (user directive)

Scanned the whole document for any number presented as "measured" without a full
reproducible run (strip + seed + sample + executable check path). Result:

- The 205.78× / P(≥100×)≈0.005% / P(≥500×)=0% / P(≥1000×)=0% figures in §7 are
  explicitly labelled **ILLUSTRATION, not measured** and attributed to the prior QA
  simulation of a "comparable moderate strip," with a note that they are
  arrangement-dependent. **No unlabelled "result" claim.** PASS.
- The ~0.58 activations/round / ~35% figure in §5.3 is attributed to "the reference QA
  simulation" (i.e. the prior review, on a different strip). It is contextualised as a
  rationale, not a Block Cave measurement, but it is **not** accompanied by a
  reproducible strip/seed in the design; flagged as a minor honesty/attribution note.
- All RTP/hit/feature/payout numbers carry **ASSUMPTION** / "not measured" / "to be
  verified by simulation." The reproducibility note in §4.2 correctly states no
  simulation has been run on the exact strips. PASS.
- No number is presented as a measured Block Cave result. **PASS overall**, with the
  single minor attribution note above.

---

## New findings

| # | Severity | Finding | Location |
| --- | --- | --- | --- |
| N1 | **CRITICAL** | The documented deterministic generation rule (seed 20261117 / 20261118) does **not** reproduce the declared §4.1/§4.2 ordered strips. Counts and length are correct, but the re-derived order diverges at index 2, and no seed in a searched range reproduces the list under any faithful reading. The design's claim "it can be re-derived exactly as follows" is false. | §4.1, §4.2 |
| N2 | Minor (informational) | The design cites the prior QA's ~0.58 activations/round / ~35% as a rationale in §5.3, but that was measured on a different "moderate" strip; my ILLUSTRATION on the declared §4.1 strip found ~1.01/round and ~57.3%. Not a blocker (per-activation effect is now bounded), but the citation is not representative. | §5.3 |
| N3 | Minor (informational) | If the declared strip's base RTP is anywhere near my model's ~45.6% (no free spins), the base game is well short of the ~84–88% the design implies is needed to reach 96.3%. This is deferred to Stage 3 by the design, so not a blocker, but the strip may be too low-value to hit targets without re-weighting. | §4.1 / §3.3 |

---

## Remaining Stage-2 blockers

1. **N1 (critical):** Fix the §4.1/§4.2 generation rule so that the documented seed
   + algorithm actually reproduces the declared ordered strips, **or** remove the false
   "re-derivable exactly as follows" claim and state that the explicit ordered list is
   the sole authoritative source for Stage 2/3. Until then the strip is not reliably
   reproducible and the design's own reproducibility guarantee is broken.

No other Stage-2 blockers remain. All other original critical/major findings
(F1, F3, F4, F5, F6, F7) are resolved, the frontend contract corrections (A)/(B)/(C)
are confirmed, and the measurement-honesty directive is satisfied.

---

*QA deliverable only. No implementation files were modified. The design file
`math/games/block_cave/MATH_DESIGN.md` was not touched.*
