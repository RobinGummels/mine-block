# Block Cave — Stage-3 Candidates A & B: Independent Fresh-Range Verification

**Reviewer:** Independent QA (engine-validation skill). **Date:** 2026-11-18.
**Scope:** Independently verify the math agent's `CANDIDATES_REPORT.md` and the two DEV
candidate configs (`candidate_a_config.py`, `candidate_b_config.py`), confirm the
paytable/baseline is undistorted, and reproduce both candidates' measurements on a
**FRESH, DISJOINT** spin-RNG range (`start_seed = 10_000_000`), disjoint from the
tuning range (0), the math-agent OOS range (1_000_000) and the orchestrator's
cross-check range (5_000_000).

**Access:** READ-ONLY on `math/games/block_cave/`. Only scratch outputs written under
`.runtime/block_cave/` with the distinct `qa_candAB_*` prefix. No implementation file
was edited. This is a DEV measurement only — **no production RTP claim is made or
endorsed here.**

---

## Verdict: PASS WITH FINDINGS

The two candidate configs are **independently reproducible** (SHA-256 matches), the
§3.1 paytable is **undistorted** (scale 1.0), the baseline/off-limits files are
**unchanged**, the report's §4 figures transcribe **correctly** from the source JSONs,
and **both candidates reproduce an in-band RTP point estimate on the fresh 10M range**.
However, the report's **tail comparison** ("Candidate A has a meaningful tail /
Candidate B has NO ≥100× tail"), which is a key justification for preferring
Candidate A, is **not robust** — on an independent disjoint range the tail metrics
**flip** (A: max 39.71×, no ≥100×; B: max 140.81×, P(≥100×)=2e-05). The RTP band
membership is confirmed only as a **point-estimate statement** (all CIs straddle the
96.0% lower edge), consistent with the report's own caveat.

| Check | Result |
| --- | --- |
| 1. Config identity & reproducibility (SHAs) | PASS (A base `33e6f349…`, B base `2295935d…`, A/B free `12096d9f…`) |
| 2. Baseline integrity / paytable undistorted | PASS |
| 3. Report §4 transcription | PASS (no factual errors in §4) |
| 4. Independent fresh-range reproduction (10M) | PASS (both reproduce in-band point estimates) |
| 5. Off-limits integrity | PASS |
| 6. Tests (18/18, 13/13, pip check) | PASS |
| 7. Recommendation "A over B" | PARTIAL (hit axis robust; tail justification NOT robust) |

---

## Findings

| # | Severity | Finding |
| --- | --- | --- |
| F1 | **MEDIUM** | The **tail comparison** in §4.5 and §5 ("Candidate A has a meaningful tail: max 424.9×, P(≥100×)≈1e-05; Candidate B has NO ≥100× tail: max 59.31×, P(≥100×)=0") is a **single-range observation, not a robust property**. On an independent fresh range (`start_seed=10_000_000`, n=200k) the tail flips: **Candidate A** = max 39.71×, **P(≥100×)=0.0**; **Candidate B** = max 140.81×, **P(≥100×)=2e-05**. The §5 "Meaningful tail (≥100×)" axis (A ✅ / B ❌) and the MATH_DESIGN statement "Candidate B removes the ≥100× tail entirely" are **not robustly supported** — the tail is a high-variance rare-event statistic and the direction is range-dependent. This does not invalidate the RTP/profile reproduction, but it **weakens** the "Candidate A is strictly better on the tail" rationale. |
| F2 | **LOW** | §4.4 column header `dur mean \| dur max` is **unlabeled as natural-vs-forced**. The values shown (8.787/24, 8.846/28, 8.874/32) are the **natural-enabled** arm; the **forced-freegame** durations are 8.47/40, 8.49/36, 8.50/44. The report's text "max 24–32" therefore **understates** the actual free-spin max (up to 40/36/44), though "well under the 60 retrigger cap" still holds for both. |
| F3 | **LOW** | §6 screening claim "screening saw ≈0.79–1.16 across nearby compositions" could **not be independently verified**: the silver-removed composition count JSONs exist (`base_cands_B*.json`, `base_cands_Bgen.json`), but the measured RTP screening output for those compositions was not found in `.runtime/block_cave/`. Treat the §6 variance range as an unconfirmed supporting claim, not a verified number. |
| F4 | **INFO** | The §5 "96.0–96.7% RTP band (HARD)" row is labelled `✅` for all three configs, but the band membership is a **point-estimate statement** (all three CIs straddle the 96.0% lower edge; the report's own §4.1/§8 caveat is accurate). This is the same variance/precision limit flagged for Candidate 2; it is honestly caveated, so this is informational, not a defect. |
| F5 | **INFO** | `MATH_DESIGN.md` revision note spells "Candidate B (**s6**)" (lowercase) while the config/report use "**S6**". Cosmetic. |

No BLOCKER findings. The RTP and profile conclusions reproduce; the tail-differentiator
claim (F1) is the only finding that affects the headline recommendation, and it does so
only on the non-robust tail axis.

---

## 1. Methodology soundness — PASS

- **Helper:** `.runtime/block_cave/measure_cand_general.py` takes explicit
  `base_counts_json`, `base_seed`, `free_counts_json`, `free_seed`, `rule`, `target`,
  `n`, `freegame_n`, `out_json` and optional `start_seed`. It builds the config via
  `experiment.build_config(...)` and measures three seed-matched arms on the same
  range: natural (ore-vein **enabled**), natural (ore-vein **disabled**), and forced
  freegame. ✓
- **Disjoint ranges:** tuning = 0; math-agent OOS = 1,000,000; orchestrator = 5,000,000;
  **QA fresh range = 10,000,000**. All mutually disjoint. ✓
- **Ore-vein isolation is clean:** `set_ore_vein_enabled(False)` swaps
  `GameExecutables.process_ore_vein_upgrades` for a no-op, so the disabled arm isolates
  the upgrade contribution; both arms use the same config and the same `start_seed`
  (seed-matched). ✓
- **Run mechanics:** `run_natural` drives `state.run_spin(start_seed + i)` with
  `criteria="basegame"`; `run_forced_freegame` uses `criteria="freegame"` at
  `start_seed + n`. RNG range is exactly `[start_seed, start_seed+n)`. ✓
- **Paytable not distorted:** `make_config(PAY_SCALE=1.0)` restores
  `gc.build_pay_group = _ORIG_BUILD_PAY_GROUP` (the §3.1 table); no scale factor is
  applied for either candidate. ✓
- **Counts validated by the helper:** `sum(base_counts)==200`, `sum(free_counts)==200`
  asserted before each run. ✓

## 2. Config identity & reproducibility — PASS

Ran each config's `__main__` self-check directly (`math/.venv/Scripts/python.exe
candidate_a_config.py` / `candidate_b_config.py` from `math/games/block_cave/`):

| Config | Base SHA (computed) | Matches constant? | Free SHA (computed) | Matches constant? |
| --- | --- | --- | --- | --- |
| Candidate A | `33e6f349c3e968cba7f5e0839196bfc165cafc8f894ba8e5e188ea3b17a463c5` | ✅ | `12096d9f52e6c60286e3d2842e06de8e79e0b2771ce5db6ec4e452e06c440687` | ✅ |
| Candidate B | `2295935d58a132ae6fc56d5569b4dcd5742379d3be597d84034999826f763f27` | ✅ | `12096d9f52e6c60286e3d2842e06de8e79e0b2771ce5db6ec4e452e06c440687` | ✅ |

- Both strips build to **length 200**; counts sum to **200** and match the constants.
- Both configs print "strips reproducible (length 200, counts + SHA-256 match)".
- A and B share the **G6 free strip** (same `12096d9f…`), as documented.
- **Answer:** **Candidate A is reproducible (SHAs match). Candidate B is reproducible
  (SHAs match).**

## 3. Baseline integrity / paytable undistorted — PASS

Recomputed strip SHAs via the modules (not read from constants):

| Config | Base SHA | Free SHA | Length | Sum |
| --- | --- | --- | --- | --- |
| `game_config.py` (baseline) | `7d04c138…bfb2451` | `f7f48c53…d89754` | 200 | 200 |
| `variant_config.py` | `428854a3…d60277` | `aa0002ab…96cc9ce` | 200 | 200 |
| `candidate2_config.py` | `7a9fe8ec…f83d425` | `48e1ea8c…c7015096` | 200 | 200 |

- Baseline SHAs match the documented `7d04c138…2451` / `f7f48c53…9754`; variant and
  Candidate 2 SHAs match their own constants. ✓
- **Paytable equals §3.1 at scale 1.0** (cross-checked against `MATH_DESIGN.md` §3.1):
  `earth` [0.18, 0.28, 0.46, 0.74, 1.10, 1.65, 2.76, 4.60, 7.35], `stone`
  [0.22, 0.33, 0.55, 0.92, 1.38, 2.02, 3.31, 5.51, 9.19], `timber`
  [0.26, 0.40, 0.66, 1.10, 1.65, 2.57, 4.23, 6.99, 11.03], `copper`
  [0.29, 0.48, 0.77, 1.29, 2.02, 3.13, 5.15, 8.27, 13.79], `silver`
  [0.55, 0.92, 1.47, 2.39, 3.68, 5.51, 9.19, 14.71, 23.90], `gold`
  [0.92, 1.47, 2.39, 3.68, 5.88, 9.19, 14.71, 23.90, 36.77], `emerald`
  [1.47, 2.39, 4.04, 6.43, 10.11, 14.71, 23.90, 36.77, 58.82], `diamond`
  [2.21, 3.68, 6.43, 10.11, 15.63, 22.98, 36.77, 58.82, 91.91], `ingot`
  [5.51, 9.19, 14.71, 23.90, 36.77, 55.15, 91.91, 147.06, 229.78]. ✓
- Both candidates call `make_config(PAY_SCALE=1.0)` → `_ORIG_BUILD_PAY_GROUP` (no scale).
- **Answer:** **The paytable is undistorted; the baseline is unchanged.**

## 4. Independent fresh-range reproduction (start_seed = 10,000,000) — PASS

Commands (scratch output under `.runtime/block_cave/`):

```
math\.venv\Scripts\python.exe .runtime\block_cave\measure_cand_general.py \
  .runtime\block_cave\candA_base_oos.json 20261117 \
  .runtime\block_cave\candA_free_oos.json 20261118 \
  create-cluster diamond 200000 20000 .runtime\block_cave\qa_candAB_A_10m.json 10000000

math\.venv\Scripts\python.exe .runtime\block_cave\measure_cand_general.py \
  .runtime\block_cave\qa_candAB_B_base.json 20261117 \
  .runtime\block_cave\qa_candAB_B_free.json 20261118 \
  create-cluster diamond 200000 20000 .runtime\block_cave\qa_candAB_B_10m.json 10000000
```

For Candidate B, the count JSONs were written with Python `json.dump` (no BOM) from
`candidate_b_config.py` (`qa_candAB_B_base.json` / `qa_candAB_B_free.json`), read back
cleanly, and both sum to 200.

### 4a. Candidate A — report OOS (1M) vs QA fresh range (10M)

| Metric (natural, ore-vein enabled) | Math-agent OOS (1M) | **QA fresh (10M)** |
| --- | --- | --- |
| RTP (point) | 0.96245 | **0.96303** |
| RTP 95% CI | [0.9544, 0.9705] | **[0.95619, 0.96987]** |
| RTP std | 1.837 | **1.561** |
| Base RTP | 0.90434 | **0.90293** |
| Feature RTP | 0.05811 | **0.06010** |
| Visible hit | 0.69784 | **0.69807** |
| Full return | 0.29417 | **0.29515** |
| Feature entry | 0.00676 | **0.00708** |
| Feature payout mean (natural) | 8.5960 | **8.4883** |
| Feature duration mean / max | 8.846 / 28 | **8.819 / 28** |
| Max round | 424.90 | **39.71** |
| P(≥100×) | 1e-05 | **0.0** |
| P(≥500×) | 0.0 | **0.0** |
| P(≥10 zero-run) / max zero-run | 1e-05 / 10 | **0.0 / 9** |
| Consistency violations | 0 | **0** |
| Ore-vein Δ (enabled − disabled) | +0.0943 pp | **+0.1043 pp** |
| Forced feat_pay_mean | 8.3208 | **8.3127** |

### 4b. Candidate B — report OOS (1M) vs QA fresh range (10M)

| Metric (natural, ore-vein enabled) | Math-agent OOS (1M) | **QA fresh (10M)** |
| --- | --- | --- |
| RTP (point) | 0.96425 | **0.96740** |
| RTP 95% CI | [0.9567, 0.9718] | **[0.95914, 0.97565]** |
| RTP std | 1.732 | **1.884** |
| Base RTP | 0.90480 | **0.90744** |
| Feature RTP | 0.05945 | **0.05996** |
| Visible hit | 0.67919 | **0.68078** |
| Full return | 0.28158 | **0.28231** |
| Feature entry | 0.00686 | **0.00689** |
| Feature payout mean (natural) | 8.6605 | **8.7089** |
| Feature duration mean / max | 8.874 / 32 | **8.767 / 24** |
| Max round | 59.31 | **140.81** |
| P(≥100×) | 0.0 | **2e-05** |
| P(≥500×) | 0.0 | **0.0** |
| P(≥10 zero-run) / max zero-run | 1e-05 / 11 | **0.0 / 9** |
| Consistency violations | 0 | **0** |
| Ore-vein Δ (enabled − disabled) | +0.2760 pp | **+0.3067 pp** |
| Forced feat_pay_mean | 8.3303 | **8.2937** |

### 4c. Interpretation

- **Deterministic/low-variance metrics reproduce well** across the two disjoint ranges for
  both candidates: base/feature RTP, visible hit, full return, entry, feature payout mean,
  feature duration, dry streaks and the ore-vein Δ all agree within a few basis points. Both
  candidates keep the feature payout in the **8–12×** band (≈8.3× forced) and short free spins.
- **RTP point estimates both reproduce IN BAND on the fresh range:**
  Candidate A **0.96303** (96.3%) and Candidate B **0.96740** (96.7%). Both CIs
  **straddle the 96.0% lower edge** (A [0.9562, 0.9699]; B [0.9591, 0.9757]), so "in band"
  is a point-estimate statement, not a robust certification — exactly as the report's own
  §4.1/§8 caveat states.
- **High-variance tail metrics FLIP (F1):** Candidate A had a 424.9× max and P(≥100×)=1e-05
  at 1M, but only a **39.71×** max and **P(≥100×)=0.0** at 10M. Candidate B had a 59.31× max
  and P(≥100×)=0.0 at 1M, but a **140.81×** max and **P(≥100×)=2e-05** at 10M. This is the
  expected rare-event variance (≈2–4 occurrences per 200k), but it means the report's
  A-has-a-tail / B-has-no-tail framing is **range-dependent** and not a stable property.

## 5. Off-limits integrity — PASS

- **No extra candidate config file was created.** Recursive search for `candidate*` found
  only `candidate2_config.py` (pre-existing), `candidate_a_config.py` (new, allowed),
  `candidate_b_config.py` (new, allowed), plus their `__pycache__` `.pyc` files and the two
  report markdown files. No `candidate*_*.py` beyond the two allowed DEV files.
- **`game_config.py`, `variant_config.py`, `candidate2_config.py`, `ore_vein_rules.py`,
  `game_executables.py` unchanged** (verified by strip-SHA recomputation and mtimes):
  - `game_config.py` 17.11 23:41, `variant_config.py` 18.11 01:54, `candidate2_config.py`
    18.11 02:49, `ore_vein_rules.py` 18.11 00:32, `game_executables.py` 18.11 00:31 — all
    **predate** `candidate_a_config.py` (10:42) and `candidate_b_config.py` (10:51).
  - The `create-cluster` rule is present in `ore_vein_rules.py` (`rule_create_cluster`,
    registered under `"create-cluster"`); `game_executables.py` retains
    `process_ore_vein_upgrades`. ✓
- QA scratch files are confined to `.runtime/block_cave/qa_candAB_*`; no `math/`, `docs/`
  or shipped config was edited.

## 6. Report transcription check — PASS (no factual errors in §4)

Cross-checked every §4 number against the three source JSONs
(`candA_oos_200k.json`, `candB_oos_200k.json`, `baseline_oos_200k.json`):

- §4.1 Natural RTP / CI / std / base / feature — all match to 4 dp.
- §4.2 Ore-vein disabled RTP and Δ (baseline −1.2215, A +0.0943, B +0.2760) — match.
- §4.3 Visible hit / full return / entry / entry CI — match.
- §4.4 Feature payout mean (natural & forced), median, duration mean/max — match.
- §4.5 max_round, P(≥100×), P(≥500×), P(≥100×) forced — match (no `P(≥100×)` transcription
  error like the earlier Candidate-2 §11 issue).
- §4.6 Dry streaks (P(zero≥10), P(zero≥20), max_zero_run, violations) — match.

**Answer:** **No factual transcription errors found in `CANDIDATES_REPORT.md` §4.** The
only issues are the §4.4 column-labeling ambiguity (F2) and the unverifiable §6 screening
range (F3).

## 7. Tests — PASS

| Check | Result |
| --- | --- |
| `math\games\block_cave\test_block_cave.py` | **18/18 pass** (incl. `test_candidate_a_config_reproducible`, `test_candidate_b_config_reproducible`) |
| `python -m pip check` | **No broken requirements found** |
| `python -m pytest math\tests\win_calculations -q` | **13 passed** |

## 8. Conclusion — explicit answers

- **Is Candidate A reproducible (SHAs match)?** **YES.** Base `33e6f349…a463c5`, free
  `12096d9f…440687`, length 200, counts sum 200.
- **Is Candidate B reproducible?** **YES.** Base `2295935d…763f27`, free `12096d9f…440687`,
  length 200, counts sum 200.
- **Is the paytable undistorted / baseline unchanged?** **YES.** Baseline/variant/Candidate-2
  strip SHAs match the documented constants; paytable equals §3.1 at scale 1.0 (verified
  value-by-value); candidates use `make_config(1.0)` → no scaling.
- **Does an independent fresh-range (10M) reproduce Candidate A's in-band RTP point estimate,
  or fall outside the band?** **REPRODUCES — 0.96303, in band (96.3%).** CI **[0.95619,
  0.96987] straddles 96.0%** (lower edge inside the CI). So the point estimate is in band,
  but it is not a robust in-band certification (same variance limit the report flags).
- **Does Candidate B reproduce?** **YES — 0.96740, in band (96.7%),** CI [0.95914, 0.97565]
  straddling 96.0% (upper edge above 96.7%).
- **Is "Candidate A preferred over Candidate B" supported?** **PARTIALLY.** On the stated
  priority (HIGH visible hit ≈70%), Candidate A is robustly better (0.698 vs 0.681 across
  both ranges), and both candidates have low dry streaks and an in-band RTP point estimate.
  **However**, the report's tail-based justification ("A has a meaningful tail / B removes the
  ≥100× tail entirely") is **NOT robustly supported** (F1): on the fresh 10M range the tail
  flips (A max 39.71×, no ≥100×; B max 140.81×, P(≥100×)=2e-05). The "A is strictly better"
  framing should be softened to "A is better on the hit axis; the tail axis is a
  range-dependent rare-event statistic, not a stable differentiator."
- **Any factual transcription errors in `CANDIDATES_REPORT.md`?** **No factual errors in §4.**
  Minor labeling ambiguity (§4.4 dur column, F2) and an unverifiable §6 screening claim (F3).
- **Overall verdict:** **PASS WITH FINDINGS** — the configs reproduce, the paytable is
  undistorted, both candidates land in-band as point estimates, tests and off-limits integrity
  pass, and the §4 report is accurate. The one MEDIUM finding (F1) is that the headline tail
  comparison and the resulting "strictly better" recommendation are range-dependent and should
  be reworded; it does not change the core RTP/profile reproduction.

---

## Checks not performed / limitations

- **Visual / Playwright QA: NOT APPLICABLE.** No Block Cave frontend exists (frontend is
  Stages 5–6 per `docs/STATUS.md`), so there is no Pixi canvas, Action, or rendered gameplay
  to verify. This review is purely math/engine validation.
- **Baseline not independently re-measured on the fresh range.** The task scope required
  re-measuring only Candidate A and Candidate B at `start_seed=10_000_000`. The §3.1 baseline
  was cross-checked for transcription against `baseline_oos_200k.json` (1M) but not re-run at
  10M. Its tail (max 286.89× at 1M) is likewise a single-range observation.
- **Independent reproduction is a single fresh range (10M) at n=200k + 20k** — a point
  measurement, not a multi-range aggregate; the variance caveat applies to it equally.
- **No git history** (directory is not a git repo), so off-limits integrity was verified via
  SHA recomputation, absence of extra `candidate*_*.py`, and file mtimes relative to the
  candidate work, rather than a diff against a prior commit.
- **§6 screening claim (F3) not independently verified** — the silver-removed composition RTP
  screening output was not located; only the composition count JSONs were confirmed.
- **RTP band membership is a point-estimate statement**, not a robust certification, for all
  three configs; a ≥500k–1M round (or multi-range aggregate) sample is needed for a firm
  in/out-of-band claim, as the report itself states.
- No production RTP is claimed. All figures are DEV measurements on the unpublished prototype.
