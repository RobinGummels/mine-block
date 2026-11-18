# Block Cave — Stage-3 VARIANT Independent QA Review

**Reviewer:** QA agent (independent of the math agent that authored the variant)
**Date:** 2026-11-18
**Scope:** Independent verification of the math agent's Stage-3 variant work
(`math/games/block_cave/variant_config.py`, the `create-cluster` ore-vein rule,
and `COMPARISON_REPORT.md`) against the validated §3.1 baseline
(`math/games/block_cave/game_config.py`).
**Mode:** READ-ONLY on all `math/` files. No `math/` file was edited, patched,
or reformatted. Only `qa/reports/block_cave_stage3_variant_review.md` was
written, plus a QA helper under `.runtime/block_cave/` (not under `math/`).

---

## Verdict: **PASS WITH FINDINGS**

The variant config is reproducible, the baseline `game_config.py` is unchanged,
the `create-cluster` rule behaves as documented, the event contract is
preserved, and the report's headline numbers are internally consistent with the
measurement artifacts. Three non-blocking findings (F1 LOW, F2/F3 INFO) are
recorded below. No implementation defect that changes the reported math was
found. Visual QA (visual-qa skill) is **N/A** for this review: no Block Cave
frontend exists yet (Stage 6); this is a math-only variant review.

---

## 1. Method

All checks were run by the reviewer from the repo root using
`math\.venv\Scripts\python.exe` (Python 3.13.2). The report's claims were
re-derived independently rather than taken on trust. The baseline `game_config.py`
was verified unchanged; the variant was verified reproducible; the variant and
baseline were both re-measured independently; the rule/event code was reviewed.

Visual QA is not applicable: there is no rendered Block Cave canvas or frontend
Action to exercise at this stage. No browser/Playwright run was performed
because there is no frontend. This is a math/contract validation only.

---

## 2. Checks run (exact commands and results)

| # | Command | Result |
| --- | --- | --- |
| 1 | `python variant_config.py` (standalone self-check) | base SHA `428854a3…60277`, free SHA `aa0002ab…c9ce`; "variant strips reproducible (length 200, counts + SHA-256 match)" |
| 2 | `python -m pytest math\games\block_cave\test_block_cave.py -q` | **15 passed** in 0.34s |
| 3 | `python -m pip check` | No broken requirements found |
| 4 | `python -m pytest math\tests\win_calculations -q` | **13 passed** in 0.09s |
| 5 | Inline baseline `game_config.py` verification | see §3 |
| 6 | `python .runtime\block_cave\measure_candidate.py 20261131 50000 2000 .runtime\block_cave\qa_variant.json` | independent variant measurement, see §4 |
| 7 | Inline baseline ore-vein Δ (50k enabled + 50k disabled, seed-matched) | enabled 0.95896, disabled 0.97078, **Δ = −1.18 pp** |
| 8 | Inline variant consistency check (20,000 natural variant rounds) | **0 violations / 20000**, wincap_bind 0, rtp_std 1.6123, max 42.49, p_ge_100x 0.0 |
| 9 | Inline variant consistency check (2,000 natural variant rounds) | **0 violations / 2000**, wincap_bind 0 |

---

## 3. Baseline `game_config.py` unchanged (verified)

Confirmed the §3.1 baseline is untouched and reproducible:

- **Paytable** `earth` = `[0.18, 0.28, 0.46, 0.74, 1.1, 1.65, 2.76, 4.6, 7.35]`
  (matches MATH_DESIGN §3.1; `_COMMON_PAYS['earth']` in `game_config.py` line 97).
  `PAY_RANGES = [(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,14),(15,19),(20,30)]`.
- **Base strip** seed `20261117`, SHA-256 `7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451`, length 200.
- **Free strip** seed `20261118`, SHA-256 `f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754`, length 200.
- **Counts sum to 200** for both base and free.
- `BASE_COUNTS`: silver **16**, pickaxe **3** (differs from the variant's silver 15 / pickaxe 4).
- `wincap = 1000.0`.
- **No `ore_vein_rule` / `ore_vein_target` attribute exists** in `game_config.py`
  (`hasattr(GameConfig(), 'ore_vein_rule') == False`; neither string present in the
  module source). So `game_executables.py` defaults to `baseline` / `diamond`,
  and the shipped §3.1 game is unchanged.

---

## 4. Independent variant measurement (50k natural + 2k forced)

Command: `python .runtime\block_cave\measure_candidate.py 20261131 50000 2000 .runtime\block_cave\qa_variant.json`

**Ore-vein ENABLED natural:**
| Metric | Reviewer (50k) | Report (200k) |
| --- | --- | --- |
| RTP | 0.9618188 | 0.96436 |
| base-game RTP | 0.8959416 | 0.89673 |
| feature RTP | 0.0658772 | 0.06762 |
| visible hit | 0.70896 | 0.70990 |
| full return | 0.28590 | 0.28690 |
| feature entry | 0.01564 (1.564%) | 0.01593 (1.593%) |
| feature payout mean | 4.2121 | 4.24496 |
| feature duration mean | 8.8593 | 8.7822 |
| round payout max | 43.46 | 57.47 |
| P(≥100×) | 0.0 | 0.0 |

**Ore-vein DISABLED (seed-matched):** RTP 0.9587892.
**Ore-vein Δ (enabled − disabled):** **+0.3030 pp** (report: +0.263 pp; within CI).

**Forced freegame (feature internal, n=2000):** feature payout mean 4.1237,
duration mean 8.514, max 39.21, P(≥100×) 0.0.

All reviewer point estimates are within sampling CI of the report's 200k values.
The variant's entry rate (~1.56–1.59%) is clearly above the baseline (~0.67%)
and in the ~1.5–1.6% region, confirming the report's "entry overshoot" trade-off.

---

## 5. Ore-vein rule Δ — independent sign check

- **Baseline** (50k each, `calibrate.py`): enabled 0.95896, disabled 0.97078 →
  **Δ = −1.18 pp** (negative). Matches the report's −1.238 pp within CI.
- **Variant** (50k each, seed-matched): enabled 0.9618188, disabled 0.9587892 →
  **Δ = +0.30 pp** (positive). Matches the report's +0.263 pp within CI.

The variant's core goal (positive ore-vein RTP contribution) is confirmed, and
the baseline's negative contribution is reproduced.

---

## 6. `create-cluster` rule code review (`ore_vein_rules.py`)

- `_MIN_PAY_CLUSTER = 5` (line 21), matching the first paying `PAY_RANGES` entry `(5,5)`.
- `rule_create_cluster` (lines 155–175): for each activated vein (an `ore_vein`
  in the winning cluster), it converts the **first** eligible neighbour only when
  `_cluster_size_if_converted(...) >= _MIN_PAY_CLUSTER` (line 172). Otherwise it
  does **not** convert and only records the activation in `veinPositions`.
- `_cluster_size_if_converted` (lines 59–109): returns 0 if the candidate cell is
  in the winning cluster (so in-cluster cells are never converted); otherwise it
  BFS-counts the converted cell plus connected surviving `target`/`ore_vein`
  (wild) cells. The converted cell counts as +1.
- Behavior confirmed by `test_create_cluster_rule_converts_when_paying_cluster`
  (converts a stone that completes a ≥5 diamond cluster) and
  `test_create_cluster_rule_no_convert_without_cluster` (no conversion when no
  ≥5 cluster results, but vein activation still recorded).
- `get_rule` registry (lines 248–259): `"create-cluster"` → `rule_create_cluster`;
  unknown names fall back to `rule_baseline`.

---

## 7. Dispatch & event contract

- `game_executables.py` `_ore_target(config)` (lines 14–15) defaults to `"diamond"`
  when `ore_vein_target` is absent; `process_ore_vein_upgrades` (lines 40–62) reads
  `ore_vein_rule` via `getattr(..., "baseline")` and dispatches through `get_rule`.
  Baseline path is unchanged.
- Event emission order in `emit_tumble_win_events` (lines 28–38):
  `winInfo -> updateTumbleWin -> [wincap] -> [oreVeinUpgrade] -> tumbleBoard`
  (MATH_DESIGN §8). `test_wincap_ore_vein_upgrade` asserts
  `updateTumbleWin < wincap < oreVeinUpgrade` and that the cascade stops after the
  wincap (no `tumbleBoard`). Passed.
- `ore_vein_upgrade_event` (`game_events.py` lines 15–29) emits event type
  `oreVeinUpgrade` with `veinPositions` and `upgrades`; rows use the padded
  `row + 1` convention. Verified in the passing tests.

---

## 8. Report ↔ artifact consistency

The report's headline figures match the persisted artifacts exactly:

| Report claim | Artifact | Match |
| --- | --- | --- |
| Baseline RTP 0.96435 | `orchestrator_200k.json` rtp 0.9643496 | ✅ |
| Variant RTP 0.96436 | `variant_200k.txt` rtp 0.96435665 | ✅ |
| Baseline ore-vein Δ −1.238 pp | (0.9643496 − 0.9767308)×100 = −1.2381 | ✅ |
| Variant ore-vein Δ +0.263 pp | (0.96435665 − 0.96172665)×100 = +0.263 | ✅ |
| Baseline entry 0.00674 / variant 0.01593 | both artifacts | ✅ |
| Baseline hit 0.69956 / variant 0.70990 | 0.699555 / 0.709895 | ✅ |
| Baseline full 0.29159 / variant 0.28690 | 0.29159 / 0.286895 | ✅ |
| Baseline feature pay mean 9.91 / variant 4.24 | 9.9134 / 4.24496 | ✅ |
| Baseline max 544.43 / variant max 57.47 | both artifacts | ✅ |
| Forced freegame feature mean 9.60 / 4.04 | 9.600045 / 4.042885 | ✅ |
| Forced freegame max 107.19 / 35.75 | both artifacts | ✅ |

The report correctly labels the variant as DEV-only, makes no production RTP
claim, and discloses the seed-sensitivity and CI caveats in §13.

---

## 9. Findings

### F1 — LOW (evidence/reporting gap): variant's 200k artifact does not persist `consistency`, `wincap_bind_count`, `rtp_std`, `p_ge_500x`/`p_ge_1000x`

**Evidence.** `COMPARISON_REPORT.md` §11 states "All large runs report **0
consistency violations** across 200,000 books each." The baseline artifacts
(`orchestrator_200k.json` lines 135–139, `baseline_ore_dis_200k.json` lines
135–139) carry a `consistency` block (0/200000) and a `wincap_bind_count` (0),
but the variant's own artifact `.runtime/block_cave/variant_200k.txt`
(lines 5–29) contains **no** `consistency`, `wincap_bind_count`, `rtp_std`, or
`p_ge_500x`/`p_ge_1000x` fields. `measure_candidate.py` `summarize()` (lines
34–48) only extracts a subset of keys and drops those.

**Independent confirmation of the underlying result.** The reviewer ran the
variant config through `run_natural` and read the full `Measurer.summary`:
- 20,000 natural rounds: **0 violations / 20000**, wincap_bind_count **0**,
  rtp_std 1.6123, max 42.49, P(≥100×) 0.0.
- 2,000 natural rounds: **0 violations / 2000**, wincap_bind_count **0**.

So the "0 consistency violations" claim for the variant is supported by the
harness, but **not evidenced at the 200k scale in the variant's own artifact**.
Non-blocking; recommend the variant output also surface `consistency`,
`wincap_bind_count`, `rtp_std`, and the tail probabilities if this report is
used for a future decision.

**File locations.** `.runtime/block_cave/variant_200k.txt`; `.runtime/block_cave/measure_candidate.py` (lines 34–48).

### F2 — INFO: variant RTP stddev is an inference, not a measurement

**Evidence.** `COMPARISON_REPORT.md` §4 line 87 lists the variant RTP stddev as
"≈ 2.0 (see §13)" and §13 (lines 257–262) infers a comparable ±0.9 pp CI from
"a strip of the same length/structure." The variant's 200k run did not persist
`rtp_std`. The reviewer's 20k variant sample measured `rtp_std = 1.6123`, which
is **lower** than the baseline's 2.0766. So the assumed ≈2.0 / ±0.9 pp is a
conservative upper bound; the actual appears smaller. This does not change the
point-estimate conclusion ("in band" at the point estimate) but means the
reported CI for the variant is an inference rather than a measured quantity.

**File locations.** `COMPARISON_REPORT.md` §4 line 87, §13 lines 257–262.

### F3 — INFO: variant base RTP is seed-sensitive; "in band" holds for the chosen seed only

**Evidence.** The variant base seed is `20261131` (`variant_config.py` line 56),
chosen for a good base/entry result. The report's §13 (lines 263–266) discloses
that, because all six reels share one 200-symbol strip, the base RTP is
"extremely seed-sensitive (measured 0.60–1.09 across seeds for the same counts)."
This is disclosed and is not a defect, but it means the "in-band RTP" conclusion
for the variant is not robust to re-seeding. A reviewer's 20k sample at a
different seed start produced RTP 0.96895, and the 50k seed-20261131 sample
produced 0.9618188 — both inside the band, but both subject to sampling/seed
variance.

**File locations.** `variant_config.py` line 56; `COMPARISON_REPORT.md` §13 lines 263–266.

---

## 10. Non-findings / confirmed-correct items

- Variant reproducibility: base/free strips length 200, counts match, SHAs match
  (`test_variant_config_reproducible` + standalone self-check).
- Baseline unchanged (paytable §3.1, strips/SHAs, no ore-vein override).
- `create-cluster` only converts when it completes a ≥5 paying cluster.
- `oreVeinUpgrade` event contract (`veinPositions`/`upgrades`, padded row+1) and
  the `wincap`/`oreVeinUpgrade` ordering are preserved and tested.
- Report numbers are internally consistent with the artifacts.
- Report correctly labels the work DEV-only and makes no production RTP claim.
- MATH_DESIGN.md assumption ledger #1 correction (scale 1.0, C2 ×F reverted) is
  consistent with the reverted `game_config.py` comment (lines 88–95).

---

## 11. Limitations of this review

- The variant's 200k-scale consistency claim was not re-verified at full 200k by
  the reviewer (only at 20k / 2k). The harness code path is identical and the
  baseline's 200k artifacts show 0 violations, so the residual risk is low.
- Visual/browser QA was not performed because no Block Cave frontend exists yet.
- The reviewer did not re-run the full 200k measurement for either arm; the
  reviewer's point estimates are from 50k (variant) and 50k (baseline ore-vein)
  samples, which are within CI of the report's 200k values.

---

## 12. Recommendation

Accept the variant work as **PASS WITH FINDINGS**. No change to any `math/`
implementation file is required. The three findings are non-blocking; F1 is the
only one worth acting on (surface the variant's `consistency` / `wincap_bind_count`
/ `rtp_std` / tail-probability fields in its output artifact so the §11 claim is
directly evidenced). F2 and F3 are documented limitations already disclosed in
the report.
