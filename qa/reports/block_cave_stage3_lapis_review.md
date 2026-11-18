# Block Cave — Stage-3 Lapis Config & RTP-vs-Tail Calibration: Independent Fresh-Range Review

**Reviewer:** Independent QA (stake-engine-validation skill). **Date:** 2026-11-18.
**Scope:** Independently verify the math agent's Part-1 `lapis` config
(`candidate_lapis_config.py`) and Part-2 calibration / infeasibility conclusion
(`LAPIS_REPORT.md`), confirm the Wilson CI in `calibrate.py`, run
`test_lapis_config_reproducible`, and reproduce both validated arms on a **FRESH,
DISJOINT** spin-RNG range (`start_seed = 30_000_000`), disjoint from the tuning range
(0), the math-agent OOS ranges (1M, 20M), the orchestrator cross-check (5M) and the
prior QA candidates range (10M).

**Access:** READ-ONLY on `math/games/block_cave/`. Only scratch outputs written under
`.runtime/block_cave/` with the distinct `qa_lapis_*` prefix. No implementation file
was edited. This is a DEV measurement only — **no production RTP claim is made or
endorsed here.**

---

## Verdict: PASS WITH FINDINGS

The Part-1 `lapis` config is **independently reproducible** (both strip SHAs match),
the **rename is mathematically neutral** (position-by-position equality after
`lapis`→`silver`, no `silver` residue, identical paytable row, deterministic), the
baseline / Candidate A / Candidate B / `ore_vein_rules.py` files are **unchanged**,
the Wilson CI in `calibrate.py` is **correct**, the report's §2.3 and §2.4 figures
**transcribe correctly** from the source JSONs, and the test suite passes
(19/19, 13/13, `pip check` clean).

The Part-2 **infeasibility conclusion is independently supported on a fresh disjoint
range.** At `start_seed = 30_000_000` (n=200k + 20k forced), `lapis_base` stays in
band as a **point estimate (0.9619 / 96.2%)** with high hit, a **positive** ore-vein
contribution (+0.0985 pp) and 0 consistency violations; the mildest premium boost
`d10_i10` **overshoots the band (0.9823 / 98.2%)** with its **entire** 95% CI
`[0.9750, 0.9896]` above the 0.967 upper edge; and **neither arm produced a single
≥100× round** (max 49.13× / 68.24×; Wilson 95% upper bound 1.92e-5), confirming that
the premium-count lever that raises the tail is the same lever that pushes RTP out of
the 0.7 pp-wide band. The findings below are **nuance only** — none affects the
headline RTP/profile reproduction or the infeasibility conclusion.

| Check | Result |
| --- | --- |
| 1. Config identity & reproducibility (SHAs) | PASS (base `00af3ba5…`, free `bc15b4fb…`) |
| 2. Rename-neutrality (Part 1) | PASS |
| 3. Baseline / Candidate A / B / ore-vein integrity | PASS (unchanged) |
| 4. Report transcription (§2.3, §2.4, §1.3) | PASS |
| 5. Wilson CI correctness (`calibrate.py`) | PASS |
| 6. Independent fresh-range reproduction (30M) | PASS (conclusion confirmed) |
| 7. Tests (19/19, 13/13, pip check) | PASS |
| 8. Infeasibility conclusion | SUPPORTED (robust across 20M & 30M) |

---

## Findings

| # | Severity | Finding |
| --- | --- | --- |
| F1 | **LOW** | §2.5 presents the **forced-freegame max** ("45–53×") and the **feature RTP** ("fixed 0.0619") as if they were stable properties. On the fresh disjoint 30M range the forced max is **85.28×** for both arms and the feature RTP is **0.0607**. Both are still well below 100× / ≈0.06, so the §2.5 conclusion holds, but the specific figures are **single-range point estimates**, not constants. Recommend describing them as "measured at the 20M range" (the report's own §Limitations already flags tail seed-sensitivity; this just extends it to the forced-max figure). |
| F2 | **LOW** | The word **"infeasible"** in §2.5 is a strong absolute claim. The report's evidence is scoped to the levers explored — premium-count boosts on the fixed §3.1 paytable with the fixed `create-cluster` → `diamond` rule. Recommend wording it as **"infeasible within the levers explored"** (or "no in-band tail boost was found among these levers") so it is not read as a general impossibility. The report's own recommendation ("No separate `candidate_lapis_tail_config.py` is created, because no in-band tail boost was found") already reads this way; the headline sentence should match. |
| F3 | **INFO** | `calibrate.proportion_ci` uses **z = 1.96** for the 95% Wilson interval, slightly wider than the exact two-sided 1.95996. This makes the reported Wilson upper bound (1.92e-5) **marginally conservative** (the exact-z bound would be ≈1.920e-5 vs ≈1.921e-5). Not a defect — it errs on the safe side; noted for transparency. |
| F4 | **INFO** | Internal feature-RTP figure differs between §2.3 (**0.0630**, n=30k) and §2.4/§2.5 (**0.0619**, n=200k). Both are accurate for their sample sizes; the feature RTP is constant across the base-modified arms *within* a range (shared free strip) but varies slightly *across* ranges (0.0630 → 0.0619 → 0.0607) because the entry rate is sampled. Cosmetic / consistency nuance only. |

No BLOCKER findings. The RTP/profile reproduction, the rename neutrality and the
infeasibility conclusion all hold independently.

---

## 1. Methodology soundness — PASS

- **Helper:** `.runtime/block_cave/screen_lapis_tail.py` takes an `arms_json` (list of
  `{name, base, free}` count dicts), `n`, `freegame_n`, `out_json` and optional
  `start_seed`. It asserts `sum(base)==200` and `sum(free)==200`, builds each arm via
  the lapis strip builder + lapis paytable, and measures three seed-matched passes:
  natural (ore-vein **enabled**), natural (ore-vein **disabled**), and forced freegame.
  ✓
- **Disjoint ranges:** tuning = 0; math-agent candidate OOS = 1M; orchestrator = 5M;
  prior QA candidates = 10M; lapis report screen/validation = 20M; **QA fresh =
  30,000,000**. All mutually disjoint. ✓
- **Ore-vein isolation is clean:** `set_ore_vein_enabled(False)` swaps
  `process_ore_vein_upgrades` for a no-op; both arms use the same config and the same
  `start_seed`, so the Δ isolates the upgrade contribution. ✓
- **RNG range:** `run_natural` drives `run_spin(start_seed + i)`; `run_forced_freegame`
  uses `start_seed + n`. Range is exactly `[start_seed, start_seed+n)`. ✓
- **Wilson CI in `calibrate.py`:** `proportion_ci(k, n)` computes the Wilson score
  interval (centre/half with `z=1.96`), and `Measurer.summary` attaches
  `p_ge_100x_ci` via `proportion_ci(int((pay>=100).sum()), n)`. ✓

## 2. Config identity & reproducibility — PASS

Ran the config self-check directly (`math/.venv/Scripts/python.exe
candidate_lapis_config.py` from `math/games/block_cave/`):

| Config | Base SHA (computed) | Matches constant? | Free SHA (computed) | Matches constant? |
| --- | --- | --- | --- | --- |
| `candidate_lapis_config.py` | `00af3ba544dba0ee523b6d4e85304d0622dd740a5c76dc13651e254a22558181` | ✅ | `bc15b4fb96319e90f35024fe8b751b3ee3534731a56aa0f9939a7a8034db4c47` | ✅ |

- Both strips build to **length 200**; counts sum to **200** and match the constants.
- **Answer:** **The `lapis` config is reproducible (both SHAs match).**

## 3. Rename-neutrality (Part 1) — PASS

Independently verified (not by trusting the report):

- **Position-by-position equality after rename:** for both the base and free strip,
  `[s.replace("lapis","silver") for s in lapis_strip] == candidate_a_strip` → **True**.
- **No `silver` residue:** a full walk of the lapis strips and config found **0** hits
  for `silver`; the lapis count equals Candidate A's silver count (base 16 / free 8).
- **Paytable row equality:** the `lapis` row in the lapis paytable equals the `silver`
  row in the §3.1 paytable, and every other symbol's pay values are **identical**.
- **Determinism:** rebuilding the config twice yields identical strips (SHA-stable).
- **Behavioral neutrality (DEV smoke, n=2000, seed 0):**
  `lapis_smoke_lapis.json` and `lapis_smoke_candA.json` are **identical**
  (RTP 0.878400, ore-vein Δ +0.130500 pp, n=2000).
- **Answer:** **The rename is mathematically neutral.** Candidate A
  (`33e6f349…` / `12096d9f…`) and Candidate B (`2295935d…` / `12096d9f…`) SHAs were
  also re-confirmed and match their constants.

## 4. Baseline / off-limits integrity — PASS

- **No extra config file created:** a recursive search found only the allowed
  `candidate_lapis_config.py` plus the pre-existing candidates; no
  `candidate_lapis_tail_config.py` was created (the report states none was, because no
  in-band tail boost was found — confirmed).
- **`game_config.py`, `candidate_a_config.py`, `candidate_b_config.py`,
  `ore_vein_rules.py` unchanged** (verified by mtimes relative to the lapis work):
  `game_config.py` 17.11 23:41, `ore_vein_rules.py` 18.11 00:32,
  `candidate_a_config.py` 18.11 10:42, `candidate_b_config.py` 18.11 10:51 — all
  **predate** `candidate_lapis_config.py` (11:51), `calibrate.py` (11:53) and
  `test_block_cave.py` (11:54). The `create-cluster` → `diamond` rule is present and
  registered. ✓
- QA scratch files are confined to `.runtime/block_cave/qa_lapis_*`; no `math/`,
  `docs/` or shipped config was edited. All inspected JSONs are **BOM-free**
  (written via Python `json.dump`, no `Set-Content`).
- **Answer:** **The off-limits files are unchanged; the baseline is undistorted.**

## 5. Report transcription check — PASS (no factual errors)

- **§1.3 SHAs** match the computed values exactly.
- **§2.3 screen table (n=30k, `--enabled-only`, start_seed 20M)** cross-checked against
  `screen_oos_tail_30k.json` — every arm matches to 4 dp:
  `lapis_base` 0.9584/0.8954/0.0630/0.6981/26.75/53.86; `d10_i10` 0.9736/0.9106/0.0630/
  0.6987/32.35/55.30; `d12_i10` 0.9941/0.9311/0.0630/0.7000/44.10/55.30; `d12_i11`
  1.0099/0.9469/0.0630/0.6994/42.95/64.46; `free_d8_i7` 0.9582/0.8954/0.0628/0.6981/
  26.75/53.86.
- **§2.4 validation table (n=200k, full ore-vein, start_seed 20M)** cross-checked
  against `screen_oos_validate_200k.json` — all figures match, including the Wilson
  upper bound **1.92e-5** for both arms.
- **Answer:** **No factual transcription errors found in `LAPIS_REPORT.md`.**

## 6. Wilson CI verification — PASS

Independently recomputed `proportion_ci(0, 200000)`:

- `p = 0`, `z = 1.96`, `denom = 1 + z²/n`, `centre = (z²/2n)/denom`,
  `half = z·sqrt(z²/4n²)/denom` → **upper = 1.92076e-5** (matches the report's 1.92e-5).
- The formula is the standard Wilson score interval; the `k=0` lower bound is 0. ✓
- **Answer:** **The Wilson CI is implemented correctly.** (F3: z=1.96 is marginally
  wider than the exact 1.95996 — INFO only.)

## 7. Tests — PASS

| Check | Result |
| --- | --- |
| `math\games\block_cave\test_block_cave.py` | **19/19 pass** (incl. `test_lapis_config_reproducible`) |
| `python -m pip check` | **No broken requirements found** |
| `python -m pytest math\tests\win_calculations -q` | **13 passed** |

## 8. Independent fresh-range reproduction (start_seed = 30,000,000) — PASS

Command (scratch output under `.runtime/block_cave/`):

```
math\.venv\Scripts\python.exe .runtime\block_cave\screen_lapis_tail.py ^
  .runtime\block_cave\arms_oos_validate.json 200000 20000 ^
  .runtime\block_cave\qa_lapis_30m_200k.json 30000000
```

(n=200,000 natural + 20,000 forced freegame, **full** ore-vein mode, both arms
`lapis_base` and `d10_i10`.)

### 8a. `lapis_base` — report OOS (20M) vs QA fresh (30M)

| Metric (natural, ore-vein enabled) | Math-agent OOS (20M) | **QA fresh (30M)** |
| --- | --- | --- |
| RTP (point) | 0.9641 | **0.9619** |
| RTP 95% CI | [0.9572, 0.9710] | **[0.9550, 0.9688]** |
| RTP std | 1.5689 | **1.5686** |
| Base RTP | 0.9022 | **0.9012** |
| Feature RTP | 0.0619 | **0.0607** |
| Visible hit | 0.6999 | **0.6992** |
| Full return | 0.2949 | **0.2951** |
| Feature entry | 0.00727 | **0.00707** |
| Feature payout mean | 8.518 | **8.591** |
| Feature duration mean / max | 8.732 / 32 | **8.778 / 28** |
| Max round | 65.36 | **49.13** |
| P(≥100×) | 0.0 | **0.0** |
| P(≥100×) Wilson upper | 1.92e-5 | **1.92e-5** |
| P(zero≥10) / max zero-run | 0.0 / 9 | **5e-6 / 10** |
| Consistency violations | 0 | **0** |
| Ore-vein Δ (enabled − disabled) | +0.0887 pp | **+0.0985 pp** |
| Forced feat_pay_mean | 8.307 | **8.322** |
| Forced max_round | 45.10 | **85.28** |

### 8b. `d10_i10` — report OOS (20M) vs QA fresh (30M)

| Metric (natural, ore-vein enabled) | Math-agent OOS (20M) | **QA fresh (30M)** |
| --- | --- | --- |
| RTP (point) | 0.9814 | **0.9823** |
| RTP 95% CI | [0.9741, 0.9886] | **[0.9750, 0.9896]** |
| RTP std | 1.6565 | **1.6648** |
| Base RTP | 0.9194 | **0.9216** |
| Feature RTP | 0.0619 | **0.0607** |
| Visible hit | 0.7004 | **0.6996** |
| Full return | 0.2958 | **0.2962** |
| Feature entry | 0.00727 | **0.00707** |
| Feature payout mean | 8.518 | **8.591** |
| Feature duration mean / max | 8.732 / 32 | **8.778 / 28** |
| Max round | 80.04 | **68.24** |
| P(≥100×) | 0.0 | **0.0** |
| P(≥100×) Wilson upper | 1.92e-5 | **1.92e-5** |
| P(zero≥10) / max zero-run | 0.0 / 9 | **5e-6 / 10** |
| Consistency violations | 0 | **0** |
| Ore-vein Δ (enabled − disabled) | +0.2047 pp | **+0.2107 pp** |
| Forced feat_pay_mean | 8.307 | **8.322** |
| Forced max_round | 52.85 | **85.28** |

### 8c. Interpretation

- **Deterministic / low-variance metrics reproduce well** across the two disjoint
  ranges for both arms: base/feature RTP, visible hit, full return, feature payout
  mean, feature duration and the ore-vein Δ all agree within a few basis points. Both
  arms keep the feature payout in the **8–12×** band (≈8.3× forced) and short free
  spins (natural max 28, forced max 40, both under the 60 retrigger cap).
- **`lapis_base` RTP point estimate is IN BAND on the fresh range: 0.9619 (96.2%).**
  Its CI `[0.9550, 0.9688]` **straddles both edges** (lower edge 96.0% inside; upper
  edge 96.7% inside), so "in band" is a **point-estimate statement**, exactly as the
  report's §Limitations states.
- **`d10_i10` RTP point estimate is ABOVE the band: 0.9823 (98.2%),** and its
  **entire** 95% CI `[0.9750, 0.9896]` lies **above the 0.967 upper edge**. This
  reproduces the report's §2.4 finding that the mildest premium boost overshoots the
  band.
- **The tail is still unreached on the fresh range:** both arms produced **zero**
  ≥100× rounds in 200k (max 49.13× / 68.24×), with a Wilson 95% upper bound of
  **1.92e-5** — an order of magnitude below the ≈1e-4 objective. This **supports** the
  infeasibility conclusion.
- **The relative RTP cost of the boost is robust:** the `lapis_base`→`d10_i10` RTP gap
  is **+2.04 pp at 30M** (0.9823 − 0.9619) and **+1.73 pp at 20M** — both far larger
  than the **0.7 pp** band width. The report's §2.5 reasoning, which leans on this
  **relative** cost rather than absolute band membership, is therefore robust across
  seeds.
- **Ore-vein Δ is positive and stronger for the boosted arm** (+0.0985 vs +0.2107 pp),
  consistent with more diamonds to cluster — reproduced at 30M.
- **0 consistency violations** for both arms on the fresh range; max zero-run 10 (one
  zero-run ≥10 in 200k, `p_zero10 = 5e-6`), slightly above the 20M range's 9 but within
  variance.

## 9. Conclusion — explicit answers

- **Is the Part-1 `lapis` config reproducible (SHAs match)?** **YES.** Base
  `00af3ba5…58181`, free `bc15b4fb…4c47`, length 200, counts sum 200.
- **Is the rename mathematically neutral?** **YES.** Position-by-position equality
  after `lapis`→`silver` (base + free), no `silver` residue, identical paytable row,
  deterministic, and behaviorally identical to Candidate A in a seed-matched smoke
  test.
- **Is the baseline / Candidate A / Candidate B / `ore_vein_rules.py` unchanged?**
  **YES.** Verified by SHA recomputation and mtimes predating the lapis work.
- **Is the Wilson CI in `calibrate.py` correct?** **YES.** `proportion_ci(0, 200000)`
  gives an upper bound of 1.92076e-5, matching the report (F3: z=1.96 is marginally
  conservative — INFO).
- **Does an independent fresh range (30M) reproduce the report's conclusions?**
  **YES.**
  - `lapis_base` reproduces an **in-band point estimate** (0.9619, 96.2%); CI
    straddles both edges → point-estimate statement, not a robust certification.
  - `d10_i10` reproduces **out-of-band** (0.9823, 98.2%); entire CI above 0.967.
  - **Neither reaches the ≥100× tail** (0 events; Wilson upper 1.92e-5) — the
    infeasibility conclusion is **supported**.
- **Are the report's figures transcribed correctly?** **YES.** §1.3 SHAs, §2.3 screen
  table and §2.4 validation table all match their source JSONs exactly.
- **Is "infeasible" fully supported?** **SUPPORTED within the levers explored.** The
  premium-count boost raises RTP out of the 0.7 pp band before it reaches the tail,
  and the one in-band alternative (`free_d8_i7`) does not lift the tail. Recommend
  softening the headline wording (F2) to "infeasible within the levers explored".
- **Overall verdict:** **PASS WITH FINDINGS** — the config reproduces, the rename is
  neutral, the report is accurate, the Wilson CI is correct, tests pass, and the
  infeasibility conclusion is independently confirmed on a fresh disjoint range. The
  only findings are LOW (range-dependent figures in §2.5; "infeasible" wording) and
  INFO (z=1.96; §2.3-vs-§2.4 feature-RTP figure), none of which change the core
  results.

---

## Checks not performed / limitations

- **Visual / Playwright QA: NOT APPLICABLE.** No Block Cave frontend exists yet
  (frontend is Stages 5–6 per `docs/STATUS.md`), so there is no Pixi canvas, no
  resolved Action, and no rendered gameplay to verify. This review is purely
  math/engine validation; it does not substitute for the Stage 5–6 frontend QA pass.
- **Independent reproduction is a single fresh range (30M) at n=200k + 20k** — a point
  measurement, not a multi-range aggregate; the variance caveat applies to it equally.
  The tail (max 49.13× / 68.24×, 0 ≥100×) is a single-range observation; the report
  itself flags that Candidate A measured a 424.9× max / P(≥100×)=1e-5 on the 1M range.
- **RTP band membership is a point-estimate statement**, not a robust certification, for
  both arms; a larger or multi-range aggregate sample is needed for a firm in/out-of-band
  claim, as the report states.
- **No git history** (directory is not a git repo), so off-limits integrity was verified
  via SHA recomputation, absence of extra `candidate*_*.py`, and file mtimes relative to
  the lapis work, rather than a diff against a prior commit.
- No production RTP is claimed. All figures are DEV measurements on the unpublished
  prototype.
