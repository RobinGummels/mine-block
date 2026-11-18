# Block Cave — Stage-3 Candidate 2: Base-Strip-Seed Search & Out-of-Sample (OOS) Review

**Reviewer:** Independent QA (engine-validation skill). **Date:** 2026-11-18.
**Scope:** Independently verify the math agent's bounded base-strip-seed search and its OOS
conclusion for Candidate 2 (`candidate2_config.py`, base seed `20261103`), and the associated
docs changes (`CANDIDATE2_REPORT.md` §11 + `MATH_DESIGN.md` revision note).

**Access:** READ-ONLY on `math/games/block_cave/`. Only scratch outputs written under
`.runtime/block_cave/` with the distinct `qa_c2s_*` prefix. No implementation file was edited.

---

## Verdict: PASS WITH FINDINGS

The methodology, off-limits integrity and the test suite are sound, and the §3.3 **profile**
claim for seed `20261103` is robustly confirmed by an independent fresh-range reproduction.
However, the **RTP-band** conclusion is **not** robustly supported: an independent run on a
second fresh, disjoint range gives a point estimate **below** the 96.0% lower edge, and both
CIs straddle 96.0%. The math agent's *own* caveat (variance/precision limit; certification-scale
needed) is validated, but the headline "0.9604 (in band)" is a range-dependent point estimate,
not a stable property.

| Check | Result |
| --- | --- |
| 1. Methodology soundness | PASS |
| 2. Independent OOS reproduction (seed 20261103) | PASS (reproducible within noise; point estimate below band) |
| 3. §3.3 profile confirmation | PASS (robustly confirmed) |
| 4. Off-limits integrity | PASS |
| 5. Docs review (§11 + MATH_DESIGN note) | FINDINGS (see below) |
| 6. Tests (16/16, 13/13, pip check) | PASS |

---

## Findings

| # | Severity | Finding |
| --- | --- | --- |
| F1 | **MEDIUM** | §11 OOS table reports `P(≥100×) = 0.0` for the four non-reference seeds (20265001/06/10/11), but the underlying OOS JSONs report non-zero values (`2.5e-05`, `2.5e-05`, `5.0e-06`, `3.0e-05`). The reference seed's `6.5e-05` is correct, but the four other rows are factually wrong vs their source JSON. |
| F2 | **MEDIUM** | Independent fresh-range reproduction gives **RTP 0.9576 (below the 96.0% band)**, CI [0.9446, 0.9706] straddling 96.0% — see §2. This corroborates the math agent's variance caveat but means "seed 20261103 satisfies the band OOS" is a range-dependent point estimate, not a robust confirmation. |
| F3 | **LOW** | §12 recommendation still cites the *tuning-range* tail metrics (`max 184.6×`, `≥100× ≈1 in 40k`) while quoting the OOS RTP 0.9604 in the same paragraph. The OOS tail is `max 210.46×`, `P(≥100×) 6.5e-05` (≈1 in 15.4k). Mixed range references. |
| F4 | **LOW** | §8 "Findings vs design targets" table still shows Candidate 2 RTP `0.95087` / `❌ Below band` without an inline pointer to the §11 revision. §9 has a revision note, but a reader scanning §8 sees a stale "below band" verdict. |
| F5 | **LOW** | Full-return is reported as `(≈15%)` / `✅ Met`, but the measured full return is **0.1847 (≈18.5%)**, which is **above** the §3.3 `12–16%` band. The table value is accurate; only the parenthetical and "Met" label are imprecise. (Persists from the earlier Candidate-2 review.) |

No BLOCKER findings. None of F1–F5 change the overall profile conclusion for the reference seed.

---

## 1. Methodology soundness — PASS

- **`measure_c2_seed.py`** uses an explicit `start_seed` argument (not 0) for OOS, and its
  `BASE_COUNTS`/`FREE_COUNTS`/`FREE_SEED` match `candidate2_config.py` exactly (verified by
  direct comparison):
  - H4 base: earth 28 / stone 26 / timber 24 / copper 22 / silver 20 / gold 20 / emerald 19 /
    diamond 17 / ingot 11 / ore_vein 9 / pickaxe 4 (sum 200).
  - F5 free: earth 29 / stone 27 / timber 25 / copper 23 / silver 18 / gold 18 / emerald 14 /
    diamond 13 / ingot 15 / ore_vein 15 / pickaxe 3 (sum 200); FREE_SEED 20261118.
- **Disjoint ranges:** tuning = 0–199,999 (`start_seed=0`, up to n=200k); math-agent OOS =
  1,000,000–1,199,999; QA fresh range = 5,000,000–5,199,999. All disjoint. ✓
- **Ore-vein delta is clean:** `set_ore_vein_enabled(False)` swaps
  `GameExecutables.process_ore_vein_upgrades` for a no-op, so the disabled arm isolates the
  upgrade contribution; both arms use the same config and same `start_seed` (seed-matched). ✓
- **Run mechanics:** `run_natural`/`run_forced_freegame` drive `state.run_spin(start_seed + i)`,
  so the RNG range is exactly `[start_seed, start_seed+n)`. ✓
- **Bounded/documented search:** the screen helper screens 21 seeds (20261103 + 20265001–20265020)
  at n=50k on `start_seed=0`; five are carried forward to OOS. The seed set and selection criteria
  are documented in §11. The 21-row screening output (`c2_screen.json`) matches the §11 screening
  table exactly (spot-checked 20261103/20265001/20265015/20265016). ✓
- **No selection-bias concern for the reference:** `20261103` is the *original* config seed, not
  a seed newly chosen from the screen, so the "no new seed needed" conclusion is not an artifact of
  cherry-picking. ✓

## 2. Independent OOS reproduction of seed 20261103 (fresh range 5,000,000) — PASS (reproducible within noise)

Command run (READ-ONLY on `math/`; scratch output under `.runtime/block_cave/`):

```
math\.venv\Scripts\python.exe .runtime\block_cave\measure_c2_seed.py 20261103 5000000 200000 20000 .runtime\block_cave\qa_c2s_200k_5m.json
```

Natural `n=200,000` per ore-vein arm + `20,000` forced freegame, `start_seed=5,000,000`.

| Metric (natural, ore-vein enabled) | Math agent OOS (range 1,000,000) | **QA independent (range 5,000,000)** |
| --- | --- | --- |
| RTP (point) | 0.9604 | **0.9576** |
| RTP 95% CI | [0.9468, 0.9740] | **[0.9446, 0.9706]** |
| RTP std | 3.10 | **2.96** |
| Base RTP | 0.7837 | **0.7840** |
| Feature RTP | 0.1768 | **0.1736** |
| Visible hit | 0.4641 | **0.4648** |
| Full return | 0.1847 | **0.1854** |
| Feature entry | 0.01597 | **0.01586** |
| Feature payout mean | 11.07× | **10.95×** |
| Feature payout median | 8.00× | **7.93×** |
| Feature duration mean / max | 8.86 / 32 | **8.84 / 28** |
| Max round | 210.46× | **115.75×** |
| P(≥100×) | 6.5e-05 | **2.5e-05** |
| P(10 consecutive zero) | 0.0021 | **0.0022** |
| Max zero-run | 18 | **19** |
| Consistency violations | 0 | **0** |
| Ore-vein Δ (enabled − disabled) | +0.325 pp | **+0.241 pp** |

**Interpretation.** The deterministic metrics — base RTP, feature RTP, hit, full, entry, feature
payout mean/median, feature duration, zero-run — are stable to within a few basis points across
the two fresh ranges. The high-variance tail metrics (max round, P(≥100×)) differ substantially
(210.46× vs 115.75×; 6.5e-05 vs 2.5e-05), as expected for rare events (the ≥100× events count
is only ~5–13 in 200k). The two RTP point estimates differ by 0.0028, which is ~0.42 standard
errors (SE ≈ 0.0066), i.e. fully consistent within noise.

**Band question (as required by the task).**
- **Is the QA point estimate in the 96.0–96.7% band?** **No — it is 0.9576, just *below* the
  96.0% lower edge.** (The math agent's OOS point estimate 0.9604 was just *above* it.)
- **Does the QA CI straddle 96.0%?** **Yes** — [0.9446, 0.9706] contains 96.0%.

So a second fresh, disjoint range does **not** reproduce an in-band point estimate; it lands
just below the band. This is exactly the variance/precision behaviour the math agent flagged
("a single 200k run can move the point estimate by several tenths of a percent"), and it means
the RTP-band conclusion is a *point-estimate statement*, not a robust in-band confirmation.

## 3. §3.3 profile confirmation for seed 20261103 — PASS

Using the independent measurement (range 5,000,000):

| §3.3 target | Measured (QA) | Met? |
| --- | --- | --- |
| Visible hit ≈ 45% (≈40–55%) | 0.4648 | ✅ |
| Full return ≈ 15% (design band 12–16%) | 0.1854 (18.5%) | ⚠️ above 16% band (see F5) |
| Feature payout 8–12× | 10.95× | ✅ |
| Short free spins | mean 8.84, max 28 | ✅ |
| Positive ore-vein contribution | +0.241 pp | ✅ |
| Meaningful tail | max 115.75×, P(≥100×) 2.5e-05 | ✅ |

The profile is stable and robustly confirmed. The only caveat is the full-return value
(≈18.5%) sitting above the 12–16% target band (F5).

## 4. Off-limits integrity — PASS

- **SHAs recompute correctly** (recomputed via the modules, not just read from constants):
  - Baseline (`game_config.py`) base `7d04c138…2451`, free `f7f48c53…9754` — match
    `MATH_DESIGN.md` §4.1/§4.2.
  - Variant (`variant_config.py`) base `428854a3…60277`, free `aa0002ab…c9ce`.
  - Candidate 2 (`candidate2_config.py`) base `7a9fe8ec…d425`, free `48e1ea8c…5096` (recomputed
    from `build_strips()` matches the constants).
- **No `candidate2_seed_<n>.py` was created** — recursive search over `math/` and `.runtime/`
  returned nothing.
- **No paytable/count change:** `game_config.py` `_COMMON_PAYS`/`_PREMIUM_PAYS`/`_INGOT_PAYS`
  still match §3.1 (scale 1.0); `candidate2_config.py` uses `make_config(PAY_SCALE=1.0)`.
- **mtimes:** `game_config.py` (17.11 23:41), `variant_config.py` (18.11 01:54),
  `ore_vein_rules.py` (18.11 00:32), `game_executables.py` (18.11 00:31), `candidate2_config.py`
  (18.11 02:49) all predate the docs update (`CANDIDATE2_REPORT.md` 18.11 08:47,
  `MATH_DESIGN.md` 18.11 08:46), consistent with the seed search touching only the docs and
  `.runtime` helpers.

## 5. Docs review — FINDINGS

- **§11 OOS table (F1).** Reference seed row (0.9604, CI [0.9468, 0.9740], hit 0.4641,
  full 0.1847, entry 0.0160, pay 11.07, dur 8.86, max 210.46, **P(≥100×) 6.5e-05**, zero-run 18,
  Δ +0.325) matches `oos_c2_20261103.json` exactly. **But** the four non-reference rows list
  `P(≥100×) = 0.0`, whereas their JSONs (`oos_c2_20265001/06/10/11.json`) report 2.5e-05,
  2.5e-05, 5.0e-06 and 3.0e-05 respectively. Factual transcription error (small values, but
  incorrect). The forced-freegame internal-distribution numbers (mean 10.57×, median 7.70×,
  dur 8.49/36, max 149.45×, P(≥100×) 0.00105) match the JSON. ✓
- **F1 (earlier finding) addressed?** Yes. §9 now carries a revision note that the
  "not simultaneously achievable" conclusion is **revised** to a variance/precision limit
  (CI straddles 96.0%, std ≈3.1), and that Candidate 2 *does* satisfy both on OOS but needs a
  certification-scale sample to confirm. This directly resolves the earlier overstated framing.
- **RTP framing honest?** Yes. §11, §12 and §15 all state the point estimate (0.9604), the
  straddling CI [0.9468, 0.9740], the ≈3.1 std, and the certification-scale (≥500k–1M) caveat.
  `MATH_DESIGN.md`'s new revision note is consistent (RTP 0.9604 in band, CI straddles,
  variance/precision limit). Honest.
- **P(≥100×) consistency:** reference seed `6.5e-05` is consistent across §11, `MATH_DESIGN.md`
  and the JSON. Non-reference seeds are inconsistent (F1).
- **§12 tail (F3):** stale tuning-range tail metrics mixed with OOS RTP.
- **§8 (F4):** stale "below band" table row without an inline pointer to §11.
- **§3.3 full-return label (F5):** `(≈15%)`/`Met` imprecise for an 18.5% value.

## 6. Tests — PASS

| Check | Result |
| --- | --- |
| `math\games\block_cave\test_block_cave.py` | **16/16 pass** (incl. `test_candidate2_config_reproducible`) |
| `python -m pip check` | **No broken requirements found** |
| `python -m pytest math\tests\win_calculations -q` | **13 passed** |

---

## Conclusion on the math agent's conclusion

The math agent concluded: **seed 20261103 already satisfies BOTH the 96.0–96.7% RTP band and
the §3.3 profile out-of-sample, so no new seed is needed.**

- **§3.3 profile — SUPPORTED.** Independent fresh-range reproduction confirms hit ≈46.5%, full
  ≈18.5%, feature payout ≈11× (8–12×), short free spins, a positive ore-vein Δ, and a meaningful
  tail, stable across two disjoint fresh ranges.
- **RTP band — NOT ROBUSTLY SUPPORTED (but honestly caveated).** An independent run on a second
  fresh range (5,000,000) gives RTP **0.9576**, which is **below** the 96.0% lower edge; the CI
  [0.9446, 0.9706] straddles 96.0%. The two fresh-range point estimates (0.9604 vs 0.9576) agree
  within ~0.4 standard errors, so they are consistent, but the point estimate itself is not stable
  enough to assert "in band" as a property. This is precisely the variance/precision limit the math
  agent described, and the report's caveat (CI straddles, std ≈3.1, certification-scale sample
  needed) is accurate and appropriately qualified.
- **"No new seed needed" — SUPPORTED** for the *profile* dimension; the search is bounded and
  documented, the reference seed is the only one of 21 that holds the profile, and the alternatives
  clearly overshoot (1.0151) or fall short (0.7555–0.9171) of the band. The "no new seed" framing
  remains valid; what is *not* robust is calling the reference seed's band membership a settled fact.

**Net:** the math agent's conclusion is supported as a **qualified point-estimate statement**,
with the caveat that a second fresh range does **not** reproduce an in-band point estimate. The
report's honest framing (variance/precision limit; certification-scale needed) is validated. The
two MEDIUM findings (F1 transcription error; F2 range-dependent band) and the LOW documentation
issues should be corrected before the report is treated as final.

---

## Checks not performed / limitations

- **Visual / Playwright QA: NOT APPLICABLE.** No Block Cave frontend exists (frontend is Stages
  5–6 per `docs/STATUS.md`), so there is no Pixi canvas, Action, or rendered gameplay to verify.
  This review is purely math/engine validation.
- **Independent reproduction used a single fresh range (5,000,000) at n=200k + 20k.** It is a
  point measurement, not a multi-range aggregate; the variance caveat applies to it equally.
- **No git history** (directory is not a git repo), so off-limits integrity was verified via SHA
  recomputation, absence of `candidate2_seed_*.py`, and file mtimes relative to the docs update,
  rather than a diff against a prior commit.
- The four non-reference OOS seeds were cross-checked against their JSONs (F1) but not
  independently re-simulated.
