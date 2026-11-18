# QA Review — Stage 1 Block Cave Math Design

**Reviewer:** Independent QA agent (not the design author)
**Date:** 2026-11-17
**File under review:** `math/games/block_cave/MATH_DESIGN.md` (NOT modified by QA)
**Scope:** Challenge the Stage 1 math proposal before Stage 2. Verify traceability, constraint compliance, Stage-2 question determinism, math sanity, assumption marking, completeness, and RTP risks. No implementation files were touched.
**Method:** Static review of the design against `docs/GAME_SPEC.md`, `docs/PROJECT_PLAN.md`, `docs/ENGINE_CONTRACT.md`, the reference engine `math/games/0_0_cluster/`, `math/src/events/events.py`, `math/src/events/event_constants.py`, `math/src/calculations/board.py`, `math/src/calculations/cluster.py`, `math/src/calculations/tumble.py`, `math/src/executables/executables.py`, `math/src/state/books.py`, and the frontend SDK types (`frontend/apps/cluster/src/game/typesBookEvent.ts`, `bookEventHandlerMap.ts`, real books in `stories/data/`). Independent Monte Carlo simulations were run to reproduce the design's claims.

---

## Verdict

**STAGE 1 MATH DESIGN IS NOT READY FOR STAGE 2.** It is a well-structured, honest proposal with strong traceability and good assumption hygiene, but it contains a **confirmed arithmetic error** in the scatter rate, an **under-specified reel-strip arrangement** that makes every RTP/hit/feature claim unverifiable, an **RTP-inflation risk in the ore-vein upgrade that my simulation shows is far larger than the design's mitigations can contain**, and an **event-ordering table that does not match the actual engine emission sequence**. These are resolvable before Stage 2, but several are genuine blockers as written.

---

## Summary per check area

| # | Check area | Verdict | Key reason |
| --- | --- | --- | --- |
| 1 | Traceability to GAME_SPEC | **PASS** | 6×5, 5+ orthogonal clusters, wild+upgrade vein, 3-pickaxe trigger, 1,000× cap, 96.3% target, frequent small wins all present and quoted. |
| 2 | Constraint compliance | **PASS (caveats)** | No gamble/continuation/player upgrade; stateless in practice but not stated explicitly; frontend-must-not-invent stated; 100-units serialization correct. |
| 3 | Stage-2 question determinism | **PARTIAL** | Pickaxe rule is unambiguous and good; vein rule is precise, but the engine's default scatter/trigger behaviour conflicts with the design's initial-board rule and is not flagged. |
| 4 | Math sanity | **FAIL** | Scatter arithmetic is wrong (0.8% vs 1.01%); base RTP/hit are entirely strip-arrangement dependent and span 11%→3626%; vein upgrade inflates RTP ~+14pp in simulation; 1,000× effectively unreachable in base game. |
| 5 | Assumption marking | **PARTIAL** | Mostly good; the "0.8%" scatter number is presented as a computed result, not an assumption, and is wrong. |
| 6 | Completeness for Stage 1 | **PASS (gap)** | All Stage 1 deliverables covered; missing the reel-strip *arrangement* (only counts given), which is critical. |
| 7 | Risk flags | **FAIL** | Ore-vein→`ingot` upgrade is confirmed as the dominant RTP risk; proposed mitigations (cap 3, "low activation") are insufficient per simulation. |

---

## Numbered findings

### F1 — [Critical] Confirmed arithmetic error in the natural scatter rate
**Location:** `MATH_DESIGN.md` §4.1 (lines 186–188), also §3.3/§6.5 and assumption ledger #5.
The design states: *"pickaxe ≈ 1.5% → natural 3+ scatter rate ≈ 0.8% (roughly 1 in 125 base spins), computed as P(Binomial(30, 0.015) >= 3)."*
Independent computation of exactly that formula:
- P(X=0) = 63.5458%, P(X=1) = 29.0311%, P(X=2) = 6.4104%
- **P(X ≥ 3) = 1.0127% → 1 in 98.7**, not 0.8% (1 in 125).

This confirms the orchestrator's earlier quick check (≈1.01%, 1 in ~98.7) and **refutes** the design's 0.8%. The design presents a wrong computed value as fact rather than an assumption.
**Recommendation:** Correct the value to ≈1.01% (1 in 98.7) under the stated binomial model, and add a note that the binomial is itself only an approximation because the board is drawn from correlated 5-symbol reel windows (see F2).

### F2 — [Critical] Reel-strip arrangement is unspecified; all RTP/hit/feature numbers are unverifiable
**Location:** `MATH_DESIGN.md` §4.1 (lines 164–179), §4.2 (lines 202–215).
Only symbol *counts* (length-200 strip) are given; the *ordering* of symbols on the strip is never specified. This is the single largest gap. My independent Monte Carlo simulation (6 independent 5-symbol windows over a 200-strip, orthogonal 5+ clusters, ore-vein as wild, proposed paytable, tumble cascades) produces wildly different results purely from arrangement:
| Strip arrangement | Base RTP (no vein) | Visible hit | Full return (≥1.0×) | Max single-round win |
| --- | --- | --- | --- | --- |
| Shuffled (max dispersion) | 11.36% | 25.8% | 2.27% | 11.42× |
| Moderate (runs of 2) | 95.65% | 66.4% | 24.0% | 205.78× |
| Grouped (contiguous) | 3626% | 99.7% | 97.7% | (cascades) |
The design targets base RTP ≈84–88%, hit ≈45%, full-return ≈12–16%. These are *achievable in principle* with a tuned arrangement between "shuffle" and "moderate," but the proposed counts alone pin down **nothing**. The design's §3.3 claim that the ≈45% hit target is "driven by the high combined weight of the four common symbols plus tumbles" is not established by the numbers as given.
**Recommendation:** Add the reel-strip symbol arrangement (or a generated-strip spec / per-reel strip layout) to the Stage 1 design, and list it in §9 open decisions. Without it, Stage 2/3 simulation is not reproducible and the RTP target is not a testable claim.

### F3 — [Critical] Ore-vein→`ingot` upgrade is the dominant RTP-inflation risk; mitigations are insufficient
**Location:** `MATH_DESIGN.md` §5.3 (lines 267–273), §9 (lines 465–467).
The design correctly self-identifies this as "the highest-RTP-risk part of the design," but proposes to bound it with "the cap of 3 per vein and the low vein activation frequency." My simulation (moderate strip, faithful implementation of §5.2–§5.5: activate on win membership, convert up to 3 orthogonal regular blocks to `ingot`, consumed on activation, survive outside cluster, scan-order, no chaining) shows:
- Base RTP **without** vein: 95.65%
- Base RTP **with** vein: 109.89%
- **Vein inflation: +14.24 percentage points (≈ +14.9% relative)**
- Vein activations: **0.575 per round**; **34.7% of rounds** have at least one vein activation; **29.3% of win events** involve a vein.

The "low activation frequency" premise is contradicted: at ~1.2 vein cells per board and a moderate hit rate, veins land in winning clusters often. The +14pp inflation pushes the game far outside the 96.0–96.7% band before free spins are even added.
**Recommendation:** Before Stage 2, either (a) upgrade to a *mid/lower* premium (e.g. `diamond`/`emerald`) rather than the top `ingot`, (b) reduce the cap to 1, (c) gate activation much harder (e.g. only when the vein is in a cluster of a *specific* symbol, or require ≥6 symbols), or (d) quantify the actual activation/RTP impact in a Stage 2 simulation and calibrate the paytable/weights downward to compensate. The current "cap 3 / low activation" story is not a sufficient bound.

### F4 — [Major] 1,000× round cap is effectively unreachable in the base game
**Location:** `MATH_DESIGN.md` §7 (lines 376–402), §3.1 ingot row (line 122).
Largest single cluster pay is `ingot` 20–30 = 125×. My simulation found max single-round win ≈ **205.78×** (moderate strip, 40k rounds), with **P(≥100×) = 0.005%**, **P(≥500×) = 0%**, **P(≥1000×) = 0%**. To reach 1,000× the round must sum base wins plus a free-spin feature; with feature average only 8–12× and a long tail, a 1,000× round is extraordinarily rare. This is not necessarily a defect (a cap can be a hard upper bound), but the design does not state an expected max-win frequency, which the official math-verification guidelines require. The design should either (a) confirm the cap is intended as a rarely/never-reached hard bound, or (b) reconsider whether the paytable can realistically produce a 1,000× round (e.g. via a much larger vein-driven `ingot` cluster, or a higher top pay). As written, the cap is essentially decoration.
**Recommendation:** Report the estimated maximum-win frequency and, if the cap is meant to be hit, add a mechanism (e.g. a bigger top-tier cluster, or a free-spin multiplier) that can plausibly reach it; otherwise state that 1,000× is a safety upper bound that is not expected to bind.

### F5 — [Major] Event-ordering table does not match the actual engine emission sequence
**Location:** `MATH_DESIGN.md` §8 (lines 417–430) vs. `math/src/executables/executables.py` and `math/src/calculations/tumble.py`.
The engine's real per-cascade order is: `reveal` → `winInfo` → `updateTumbleWin` → `tumbleBoard` → (repeat) → `setWin` → `setTotalWin` → [`freeSpinTrigger`] → [`freeSpinRetrigger`] → `finalWin`, with `wincap` emitted *in the middle* of a cascade when `running_bet_win` first crosses the cap (see `emit_tumble_win_events` → `evaluate_wincap`, and `set_end_tumble_event` in `tumble.py`). The design's table places `updateTumbleWin`/`setTumbleWin` at position 5, *after* `tumbleBoard` (position 4), which is inverted; it omits `setWin` entirely; and it places `wincap` at the end (position 12), whereas the engine emits it during the cascade. The proposed insertion of `oreVeinUpgrade` between `winInfo` and `tumbleBoard` is consistent with §5.5 ("scored at original size before upgrade," upgrade applied before the cluster explodes), which is good.
**Recommendation:** Rewrite §8's event table to mirror the real engine sequence (including `setWin`, and `updateTumbleWin` before `tumbleBoard`), and place `oreVeinUpgrade` between `winInfo`/`updateTumbleWin` and `tumbleBoard`. Confirm `wincap` emission timing.

### F6 — [Major] `oreVeinUpgrade` is a genuinely new event type not present in the SDK; contract must be agreed before any implementation
**Location:** `MATH_DESIGN.md` §8 (lines 432–449).
`oreVeinUpgrade` does **not** exist anywhere in the frontend SDK. `frontend/apps/cluster/src/game/typesBookEvent.ts` defines `reveal`, `winInfo`, `updateTumbleWin`, `setTotalWin`, `freeSpinTrigger`, `updateFreeSpin`, `updateGlobalMult`, `freeSpinEnd`, `tumbleBoard`, `finalWin`, `setWin`, `updateGrid`, `freeSpinRetrigger`, `createBonusSnapshot` — no `oreVeinUpgrade`. The design correctly flags this as requiring math/frontend agreement, but it is a genuine contract change: the frontend would need a new event-handler branch (to visually convert adjacent blocks) and a new TS type, plus the payload shape (`veinPositions`, `upgrades[]` with `{reel,row,symbol}`) must be ratified. The payload uses row/column coordinates consistent with `Position` in the cluster types.
**Recommendation:** Route the `oreVeinUpgrade` contract through the orchestrator's Stage-5 frontend-contract step *before* any book is generated; agree the type string, payload field names, and position coordinate convention (with/without padding offset) with the frontend agent.

### F7 — [Major] Design's "initial-board-only" scatter rule conflicts with the engine's default trigger behaviour
**Location:** `MATH_DESIGN.md` §6.1–§6.2 (lines 321–334) vs. `math/src/executables/executables.py` `check_fs_condition` (lines 43–49) and `math/src/calculations/tumble.py` (line 48).
The engine's `check_fs_condition` calls `count_special_symbols("scatter")`, which reads `special_syms_on_board`; that list is refreshed by `get_special_symbols_on_board()` inside `tumble_board()` on every cascade. So the engine counts scatters on the **post-tumble** board, not the initial board. The design's rule ("count only on the initial board; no accumulation across tumbles") is unambiguous as a *rule*, but implementing it requires **overriding** `check_fs_condition` (or capturing the initial-board scatter count before any cascade), which the design does not mention. The `readme.txt` note about "scatter symbols tumbling onto the board during basegame criteria" is exactly the behaviour the design is trying to remove.
**Recommendation:** Add an explicit note that natural triggering requires (a) removing the `draw_board` re-draw suppression loop in `src/calculations/board.py` (lines 201–205) and (b) overriding `check_fs_condition` to evaluate the initial board. This is a real engine-code touchpoint the design should surface.

### F8 — [Minor] Base-game RTP feasibility is plausible but only within an unspecified strip arrangement
**Location:** `MATH_DESIGN.md` §3.3 (lines 141–153), §3.2.
The design's arithmetic on the free-spin contribution is correct: feature rate 0.8–1.0% × feature average 8–12× ⇒ free-spin RTP contribution **6.4%–12.0%**, so the base game must supply **84.3%–89.9%** RTP. My simulation shows a tuned strip can reach this (moderate ≈95.7%, shuffle ≈11%), so 84–88% is reachable *in principle*. However, the design's stated targets (45% hit, 12–16% full-return) require the average winning round to be ≈1.9× while also claiming "many sub-1.0× wins"; that is only self-consistent if the ≥1.0× tail is heavy. This is a plausible-but-unproven assertion, correctly marked ASSUMPTION, but it should be reworded to avoid implying the 45% target is a consequence of the weights (F2). The design should not present "intended RTP contribution" as an established fact.
**Recommendation:** Soften "driven by" causation in §3.3 and §3.2; state that hit-rate and RTP must be jointly calibrated via simulation.

### F9 — [Minor] Design does not explicitly address statelessness
**Location:** `MATH_DESIGN.md` §1, §9.
The design implies stateless mechanics but never states the engine's stateless requirement (per `PROJECT_PLAN.md`: "games are stateless; jackpots, gamble, continuation and early cashout are prohibited"). It does exclude gamble/continuation (good), but the stateless property itself should be affirmed. The "automatic in-book upgrade" is correctly flagged as requiring platform confirmation.
**Recommendation:** Add one sentence affirming the game is stateless and that no player-selected wager/upgrade exists.

### F10 — [Minor] "Per-segment capping is NOT used" is technically inaccurate
**Location:** `MATH_DESIGN.md` §7 (lines 388–391).
The engine *does* clamp individual win amounts to `wincap` in `win_info_event` (`min(win, wincap) * 100`), `set_win_event`, and `set_total_event`. For Block Cave, since no individual win can reach 1,000× (max cluster 125×), this clamping never binds, so the design's *intent* is correct. But the statement that per-segment capping is not used is misleading.
**Recommendation:** Rephrase to "individual wins are below the cap in practice; only the cumulative round total is clamped to 1,000×."

---

## Numbers independently recomputed (design vs. QA)

| Quantity | Design value | QA independent result | Status |
| --- | --- | --- | --- |
| P(Binomial(30, 0.015) ≥ 3) | 0.8% (1 in 125) | **1.0127% (1 in 98.7)** | **CONFIRMED ERROR** |
| P(X=0)/P(X=1)/P(X=2) (n=30,p=.015) | not stated | 63.55% / 29.03% / 6.41% | — |
| Strip-based scatter 3+ rate (shuffle) | 0.8% | 0.67–0.70% | differs |
| Strip-based scatter 3+ rate (moderate) | 0.8% | 2.39% | differs |
| Strip-based scatter 3+ rate (grouped) | 0.8% | 9.08% | differs |
| 100 units per multiplier (1,000× → 100,000) | 100,000 units | 100,000 units | correct |
| Reference game `wincap` | 5000.0 (per game_config.py) | 5000.0 | correct |
| Max single `ingot` cluster pay | 125× | 125× (from paytable) | correct |
| Free-spin RTP contribution | (implied 6.4–12%) | 6.4%–12.0% (0.8–1.0% × 8–12×) | consistent |
| Base RTP needed for 96.3% | not stated | 84.3%–89.9% | — |
| Base RTP (no vein), shuffled | ≈45% hit implied | 11.36% RTP, 25.8% hit | far below target |
| Base RTP (no vein), moderate | target 84–88% | 95.65% RTP, 66.4% hit | above target |
| Base RTP (with vein), moderate | target 84–88% | **109.89% RTP** | **over target** |
| Vein RTP inflation (moderate) | "bounded by cap 3 / low activation" | **+14.24 pp (≈ +14.9% rel.)** | **mitigation insufficient** |
| Vein activation frequency (moderate) | "low activation" | **0.575/round, 34.7% of rounds** | **contradicts premise** |
| Max single-round base win (moderate) | cap 1,000× | 205.78× (P≥500×=0%) | cap effectively unreachable |

Simulation parameters: 6 reels × 5 rows = 30 cells; each reel = independent 5-symbol window on a shared 200-length strip; orthogonal 5+ clusters; `ore_vein` substitutes as wild (`wild_key="wild"`); paytable from §3.1; tumble scrolls each reel window back by the number of exploding cells (mirrors `tumble.py`); 40k–300k rounds per run; vein upgrade implemented per §5.2–§5.5. The exact values are **arrangement-dependent** (F2) and are presented to bound the plausible range, not as a production RTP.

---

## Blockers for Stage 2

1. **Reel-strip arrangement is unspecified** (F2). Without it, the paytable+weights produce anywhere from 11% to 3626% RTP; Stage 2 cannot be calibrated or reproduced. This is the primary blocker.
2. **Scatter-rate arithmetic error** (F1). The 0.8% figure is wrong and is used to justify the feature-rate target; it must be corrected and re-grounded.
3. **Ore-vein upgrade RTP inflation** (F3). The +14pp inflation pushes the game to ~110% RTP with the current mitigations; the upgrade target/cap/activation must be re-bounded or the paytable re-weighted before Stage 2.
4. **Event contract for `oreVeinUpgrade`** (F6) and the **event-ordering mismatch** (F5). These must be ratified with the frontend and corrected to match the real engine sequence before any books are generated.
5. **Engine code touchpoints for natural triggering** (F7). The design must acknowledge that implementing "initial-board-only" scatter counting and natural triggering requires overriding `draw_board` and `check_fs_condition`.

## Not a blocker (informational)

- Traceability, constraint compliance (no gamble/continuation), pickaxe-rule clarity, vein-rule determinism, assumption hygiene (mostly), and Stage 1 completeness are all in good shape. The design is honest that nothing is measured and correctly defers RTP/hit/feature measurement to Stage 3.
- The 1,000× cap value and unit conversion are correct; the concern is reachability (F4), not correctness.

---

*QA deliverable only. No implementation files were modified. The design file `math/games/block_cave/MATH_DESIGN.md` was not touched.*
