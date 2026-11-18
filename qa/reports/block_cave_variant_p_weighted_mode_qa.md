# Block Cave — Variant P Weighted-Mode Report — Independent QA

**QA report:** `qa/reports/block_cave_variant_p_weighted_mode_qa.md`
**QA agent:** independent (not the implementer). **Date:** 2026-11-18.
**Report under review:** `math/games/block_cave/BONUS_VARIANT_WEIGHTED_MODE_REPORT.md`
**Scope:** DEV-only verification. **No production RTP claim is made or endorsed here.**

**Method.** All numbers below were recomputed from the raw artifacts
(`vp_weighted_180m.npz`, `vp_weighted_base_lut.csv`,
`vp_weighted_optimized_lut.csv`, `vp_weighted_180m.summary.json`,
`vp_weighted_180m_an.json`) using the isolated interpreter
`math\.venv\Scripts\python.exe` (Python 3.13, numpy 2.2.5), via my own
scripts — **not** by importing or re-running the implementer's
`vp_weighted_analyze.py`/`vp_weighted_collect.py` (those were only read to
understand the stated method). The min-KL band solve was re-implemented
independently (exponential tilt + bisection on λ). A small fresh seed range
(5,000 books, seed 230,000,000 — disjoint from the 170M–220M sample) was also
run end-to-end through the engine to independently corroborate `check_book`.

---

## Checklist results

### 1. Natural RTP — **PASS**
- Natural RTP = mean(payoutMultiplier)/100 = **0.9457134** (claimed 0.94571). ✔
- Base / feature split: base **0.7615848**, feature **0.1841286** (claimed
  0.76158 / 0.18413). ✔
- Natural ≥100× = **182 / 1,800,000 = 1.011111e-4** (1:9,890). ✔
- max round win = 428.36; ≥500× = 0; ≥1000× = 0. ✔

### 2. Sample & ranges — **PASS**
- N = **1,800,000** books (npz and summary agree). ✔
- Six ranges 170M/180M/190M/200M/210M/220M × 300,000; all **≥ 170M** and
  **disjoint**. ✔ (Prior work was 0–160M, so these are fresh.)
- Pooled `consistency_violations` = **0**; per-range violations all **0**. ✔
- Independent fresh-range re-run (5,000 books, seed 230,000,000) also reported
  **0 `check_book` violations** and 0 `pm` vs `round(min(base+free,1000)*100)`
  mismatches. ✔ (direct cross-check, not just the stored counters)
- Summary pooled RTP (0.945713) == npz RTP (0.945713). ✔

### 3. Base-LUT ↔ book consistency — **PASS**
- `payoutMultiplier == round(min(base+free,1000)*100)` for all 1,800,000 books:
  **0 mismatches**. ✔
- `round(win*100) == payoutMultiplier` for all books: **0 mismatches**. ✔
- Base LUT CSV: **1,800,000 rows**, bookIds 0…1,799,999 in order, weight column
  all `1`. Base-LUT RTP from CSV = **0.9457134** == natural RTP. ✔
- 200,000-book random sample: CSV `payoutMultiplier` column == npz `pm`
  (0 mismatches). ✔

### 4. Min-KL weighting math — **PASS**
Re-implemented the exponential tilt `q_b ∝ p_b·exp(λ·m_b)` with bisection on λ:
- **λ = 0.00179465792** (reported 0.00179465792; match to <1e-10). ✔
- **Σ q_b = 1.000000000000**; **q_b ≥ 0** (min 0 on empty bands). ✔
- **Σ q_b·m_b = 0.963000000** (target 0.963). ✔
- All 15 band counts, `p_b`, `m_b`, `q_b` match the report table exactly. ✔
- **max q/p ratio = 1.587476** on **[200,500)** (reported 1.5875). ✔
- Only the two lowest bands trimmed: [0,0.1) ratio **0.99829**, [0.1,1) ratio
  **0.99907** (≤0.17% trim). All other populated bands boosted. ✔
- **KL divergence = 1.580093e-5** (reported 1.58e-5). ✔
- Achievable mean range over non-empty bands = **[0.0, 258.466]**; target 0.963
  is well inside. ✔

This is the exact closed-form minimum-KL solution for the mean constraint; the
report's characterization is correct.

### 5. Published RTP — **PASS**
- Float weights: `Σ(w·win)/Σ(w)` = **0.963000000000000** (error **+2.22e-16**;
  report says +2e-16). ✔
- From the optimized LUT integer weights (`w_int = round(w·2^50)`):
  `Σ(w_int·win)/Σ(w_int)` = **0.962999999912009** (error **−8.80e-11**;
  report says −8.8e-11). ✔
- Optimized LUT = 1,800,000 rows; `payoutMultiplier` column == base pm;
  integer-weight column == `round(w·2^50)` for all rows. ✔

### 6. Weighted metrics — **PASS**
From the final weights:
- Weighted visible hit = **0.699003** (claimed 0.6990). ✔
- Weighted full return = **0.249791** (claimed 0.2498). ✔
- Weighted free-spin entry = **0.00741749** (claimed 0.007417). ✔
- Weighted ≥100× = **1.285647e-4** = **1:7,776** (claimed 1.286e-4). ✔
- ≥100× split counts: **1 base-only / 181 with-free-spins**; weighted
  base-only **8.819e-7**, with-fs **1.27683e-4**, base-only share **0.686%**
  (claimed 0.69%). ✔
- ≥500× / ≥1000× = 0. ✔
- Kish **n_eff = 1,799,940.79** (claimed 1,799,940). ✔
- Weighted feature payout mean **26.7706** (claimed 26.77), duration mean
  **8.6599** (claimed 8.66), feature weight mass **0.0074175**. ✔
- ≥100× Wilson 95% = **[1.13033e-4, 1.46230e-4]** = 1:8,847 to 1:6,839
  (claimed [1.130e-4, 1.462e-4]). ✔
- ≥500× Wilson upper = **2.1343e-6** (claimed 2.13e-6). ✔
- Natural feature profile (from npz): entry k=12,756; payout mean 25.9824 /
  median 20.68 / max 332.56; duration mean 8.6171 / median 8.0 / max 32 —
  matches report §4. ✔

### 7. Wilson CI method — **NOTE (legitimate, but model-based)**
The report uses the Kish effective sample size `n_eff = (Σw)²/Σ(w²) = 1/Σ(w²)`
and `k_eff = p̂·n_eff`, then the standard Wilson interval. For a weighted mean of
i.i.d. Bernoulli indicators with **fixed** weights, the variance is
`p(1-p)·Σw²/(Σw)² = p(1-p)/n_eff`, so this is a **standard, legitimate
design-effect approximation** and reduces to the ordinary binomial Wilson
interval when weights are uniform (here n_eff ≈ 1.80M ≈ N).

Caveats I want on the record:
- The weights are **deterministic** and, more importantly, are **estimated from
  the same sample** (band `p_b`, `m_b` depend on the observed books). The
  interval is therefore a **model of the natural-sample sampling variability**,
  **not** a true sampling CI for a fixed, published distribution. The report
  explicitly discloses this ("the interval is a model"). ✔
- **Reporting nitpick:** the JSON reports `"k": 231, "n": 1799940`, but the
  interval is computed with the non-integer `k_eff = 231.409` and
  `n_eff = 1799940.79`. The interval values are correct (computed from the
  floats); the displayed `k`/`n` are just truncated integers and slightly
  misstate the inputs actually used. Minor, cosmetic.
- **Fairness of "inside 1:5,000–1:20,000":** point estimate 1:7,776 and
  interval [1:8,847, 1:6,839] are both strictly inside [1:20,000, 1:5,000]
  (rates 5e-5…2e-4). As a **DEV measurement** on one 1.8M sample this is a fair
  statement. It is **not** a tail certification, and the report says so. ✔

### 8. Sensibility verdict — **ACCEPT (design judgement), with the notes in §10**
- Hitting 0.963 requires a **max band boost of 1.59×** (the [200,500) band) and
  KL 1.58e-5; only the two zero/low bands are trimmed by ≤0.17%. This is a
  genuinely small distortion. The **1.59× < 5×** threshold is fair and not
  close to the limit.
- The boost is **monotone in win value** (gentle), which is the expected and
  sensible shape for an RTP-lifting tilt.
- ≥100× stays inside the band; hit and entry are essentially preserved
  (hit +0.07% relative, entry +4.7% relative).
- "**No paytable bump needed**" is supported **only in the optimizer
  re-weighting sense** — see §10 for the crucial caveat.

### 9. Off-limits integrity — **PASS (with a no-git limitation)**
- **All 16 SHA-256 prefixes** reported in §9 recomputed and **match exactly**
  (candidate_a DE49BE20, candidate_b 5073ACB4, candidate2 10F1DC1D,
  candidate_lapis DC343889, variant DDD4DBD1, game_config 9642B207, gamestate
  ADFF2DC4, game_override D9778C19, ore_vein_rules AB161BFF, game_executables
  2B1D167B, game_events 14948ACD, game_calculations 5CC9CF2D, calibrate
  816796E3, run A3455311, test_block_cave 92D13B29,
  candidate_lapis_persistent_config 27ECE240). ✔
- `math/games/block_cave/library/` contains **0 files** (all subdirs empty). ✔
- Config self-check: `build_config()` + `sha256()` succeed; base strip SHA
  `00af3ba5…`, free strip SHA `bc15b4fb…` (match report §1). ✔
- `docs/`, `scripts/`, `frontend/`, `art/`: **no files in scripts/, frontend/,
  art/ were modified on 2026-11-18** (all their mtimes are 17.11). `docs/STATUS.md`
  mtime is 18.11 14:29, **before** the weighted-mode work (~17:50–18:05), which
  is consistent with it being untouched by this task. ✔
- **Limitation:** the repo is **not a git repository**, so "untouched" beyond
  the listed SHAs / mtimes cannot be byte-verified against a baseline. The
  reported config SHAs do verify, and the report's own new artifacts are all
  confined to `.runtime/block_cave/vp_weighted_*` plus the report itself.

### 10. Overstated-claims review
Flagging anything presented as stronger than justified:
1. **"Sensible" vs "certified".** The report consistently uses "sensible /
   preliminary / DEV" and repeatedly disclaims a production RTP claim. This is
   **not** overstated. Good.
2. **"No paytable bump needed" — the main nuance.** This is true *only* in the
   sense that the optimizer's **re-weighting** of the book distribution reaches a
   published RTP of 0.963. The **underlying game's real RTP remains 0.9457**;
   the 0.963 is a re-weighted "published" figure that only materializes once the
   (currently un-run) Rust optimizer weighting is actually applied. The report
   discloses this in §11–§12, but the executive-summary phrasing ("no paytable
   change / small-payout bump is needed for the RTP target") is easy to read as
   "the game now returns 0.963," which is not yet the case. **Flag.**
3. **Natural RTP below the engine band.** 0.9457 is below 96.0–96.7%. The
   config docstring says it was calibrated to hold RTP in that band, but the
   measured natural RTP is 1.4 pp short. The report discloses the below-band
   status and calls it an unsettled design decision; it does not overclaim, but
   the config's own stated calibration target is not being met by the natural
   sample. **Flag as context.**
4. **Empty top bands.** No ≥500× occurred in 1.8M natural spins, so the
   weighting cannot create a ≥500× tail; ≥500×/≥1000× remain 0. Disclosed, but
   worth stating plainly: **this weighting does not and cannot produce a ≥500×
   tail** even though the persistent-vein mechanic was intended to lift the tail.
5. **Not the Rust optimizer's output.** Stated clearly and repeatedly. This is
   the exact minimum-distortion solution to the RTP constraint, not the result
   of the full pig/fence search (which has extra constraints and would change the
   outcome). **Correctly caveated.**
6. **≥100× "inside band" is a DEV measurement, not a tail certification.** The
   report states this. With 182 natural hits / ~231 effective, the point estimate
   1:7,776 is seed-sensitive. **Correctly caveated.**
7. **Kish CI presented as a Wilson interval.** It is a *weighted* design-effect
   Wilson interval; for near-uniform weights it is effectively the binomial one,
   but it is a model, not a true CI for a fixed distribution. The report discloses
   this in §6. **Correctly caveated** (see also the k/n truncation nitpick).

---

## Overall verdict: **ACCEPT WITH FINDINGS**

**No FAIL items.** Every numeric claim I recomputed reproduced exactly, the
min-KL solve and the published/weighted RTP are correct, the artifacts are
internally consistent, and all 16 off-limits config SHAs verify. The report is
honest about being DEV-only and about not being the Rust optimizer's output.

**Findings (all NOTE-level, no correction to the math is required):**
- **F1 (main):** "No paytable bump needed" is accurate only as a statement about
  optimizer re-weighting, not about the game's real RTP. The underlying game
  still returns 0.9457 until/unless the optimizer weighting is actually applied.
  The report discloses this, but the executive summary's wording invites
  over-reading. Recommend the exec summary add one clause: "(the underlying game
  RTP is unchanged at 0.9457 until the optimizer weighting is applied)."
- **F2:** The Wilson outputs display `k=231, n=1799940` but were computed with
  `k_eff=231.409, n_eff=1799940.79`. The interval is correct; the displayed
  integers are truncated and slightly misstate the inputs. Cosmetic.
- **F3 (context):** The config's stated calibration target (96.0–96.7%) is not
  met by the natural sample (0.9457). Disclosed by the report, but the config's
  own docstring claim should be reconciled.
- **F4 (context):** No ≥500× tail exists and none can be created by this
  weighting; the persistent-vein tail-lifting intent is not realized in-band.
- **F5 (verification limit):** Repo is not a git repo, so "untouched" for
  docs/scripts/qa/frontend/art beyond the listed SHAs and observed mtimes cannot
  be byte-verified against a baseline.

**Recommendation to orchestrator:** Accept the report's *mathematical*
correctness and its DEV framing. Treat the "sensible, no paytable bump needed"
conclusion as a **preliminary design result** that depends on the optimizer
re-weighting actually being applied; do not treat it as evidence that the game
itself returns 96.3%, and do not treat it as a tail certification. A paytable
bump (or a re-calibration to lift the natural RTP into the band) is still a live
question if a ≥500× tail or an in-band *natural* RTP is required.

**QA evidence files (temp, not in repo):**
`qa_vp_weighted_verify.py` (63/63 PASS), `qa_vp_weighted_supp.py`,
`qa_vp_crosscheck.py` (fresh 5k-book independent run).
