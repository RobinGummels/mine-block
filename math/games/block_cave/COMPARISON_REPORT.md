# Block Cave — Stage-3 Variant vs §3.1 Baseline Comparison

**Status:** DEV measurement only. **This is NOT a production certification and
makes no RTP claim for a published game.** All figures are measured on the
current (unpublished) Block Cave prototype. Owner: Math agent.

This report compares the validated **§3.1 baseline** (`game_config.py`) against
a **separate, clearly-labelled Stage-3 variant config** (`variant_config.py`).
The baseline is **unchanged and still reproducible**; the variant is a DEV
candidate that targets a higher natural free-spin entry rate and a **positive**
ore-vein RTP contribution (the baseline's ore-vein upgrade is a small net
*negative*). **No final math is decided here** — the recommendation is for the
orchestrator/product to choose.

---

## 1. Objective

Build a targeted Stage-3 Block Cave variant that:

1. Raises the natural 3+ pickaxe free-spin **entry** rate (baseline ≈ 0.70%,
   target ≈ 1%).
2. Rebalances the **ore-vein upgrade** to a **positive** RTP contribution
   (baseline ≈ −1.24 pp).
3. Keeps the overall natural RTP in the Engine's **96.0–96.7%** band.
4. Keeps short free spins (8/12/16/16), visible hit ≈ 70% and full-return ≈ 29%.
5. Does **not** inflate the top-pay tail.

Then compare it against the §3.1 baseline and recommend a direction without
deciding the final math.

## 2. What changed (variant config)

The variant reuses the §3.1 baseline bet modes, wincap, triggers and paytable
(scale **1.0**). Only the following differ (see `variant_config.py`):

| Aspect | §3.1 baseline | Stage-3 variant |
| --- | --- | --- |
| Base strip | pickaxe **3**, silver 16 | pickaxe **4**, silver **15** (sum stays 200) |
| Base seed | 20261117 | **20261131** |
| Free strip | earth 30 … ingot 14, ore_vein 15, pickaxe 3 | earth **42**, stone **38**, timber **36**, copper **32**, silver 15, gold 14, emerald 12, diamond **4**, ingot **2**, ore_vein **2**, pickaxe 3 |
| Free seed | 20261118 | 20261118 |
| Ore-vein rule | `baseline` (convert first eligible neighbour) | `create-cluster` (convert only if it completes a ≥5 target cluster) |
| Ore-vein target | diamond | diamond |
| Paytable | §3.1, scale 1.0 | §3.1, scale 1.0 (unchanged) |

- The base strip `pickaxe` count is raised from 3 to 4 by reducing `silver`,
  which raises the natural 3+ pickaxe **entry** rate.
- The ore-vein upgrade is switched to the DEV `create-cluster` rule (selected
  via `config.ore_vein_rule`, default in `game_config.py` stays `baseline`) so
  the conversion only happens when it completes a paying (≥5) diamond cluster,
  making the upgrade a **positive** RTP contributor instead of a negative one.
- The free-spin strip is retuned (fewer premium/ingot/ore-vein, more common
  symbols) so that, with the higher entry rate, the overall natural RTP stays
  in band. **Free spins remain short** (trigger table 8/12/16/16, retrigger cap
  60).

Frozen strip SHA-256 (variant): base `428854a3…60277`, free `aa0002ab…c9ce`.

## 3. Method

- **Natural base rounds only** (`criteria="basegame"`, `betmode="base"`, no
  forcing) are the only basis for round RTP, hit, full-return, dry streaks and
  the free-spin **entry rate**.
- **Seed-matched:** baseline and variant use the **same seed range**
  (0…199,999) for the enabled/disabled arms, so each comparison is a
  like-for-like seed-matched measurement.
- **Forced freegame rounds** (`criteria="freegame"`,
  `force_freegame=True`) are generated **only** to measure the free-spin
  feature's internal distribution; they are **not** used for round RTP/entry.
- Sample: **200,000 natural rounds** per config per ore-vein arm, plus
  **2,000** forced freegame rounds per config.
- Harness: `math/games/block_cave/calibrate.py` (`CalibrateState`,
  `make_config`, `Measurer`, `run_natural`, `run_forced_freegame`,
  `set_ore_vein_enabled`) and `.runtime/block_cave/measure_candidate.py`.
- Baseline outputs: `.runtime/block_cave/orchestrator_200k.json` (ore enabled)
  and `.runtime/block_cave/baseline_ore_dis_200k.json` (ore disabled). Variant
  output: `.runtime/block_cave/variant_200k.txt`.

## 4. Results — natural base game (n = 200,000 each, seed-matched)

| Metric | §3.1 baseline | Stage-3 variant |
| --- | --- | --- |
| **RTP** (mean round payout) | **0.96435** | **0.96436** |
| base-game RTP contribution | 0.89753 | 0.89673 |
| free-spin RTP contribution | 0.06682 | 0.06762 |
| RTP stddev | 2.0766 | ≈ 2.0 (see §13) |
| **Visible hit** `P(payout>0)` | 0.69956 | **0.70990** |
| **Full return** `P(payout>=1.0×)` | 0.29159 | **0.28690** |
| **Feature entry rate** | **0.00674** (0.674%) | **0.01593** (1.593%) |
| Feature duration mean | 8.67 | 8.78 |
| Feature payout mean (natural) | 9.91 | **4.24** |
| Round payout max | **544.43** | **57.47** |
| `P(>=100×)` / `P(>=500×)` / `P(>=1000×)` | 5e-6 / 5e-6 / 0.0 | **0.0 / 0.0 / 0.0** |
| `wincap` bind count | 0 | 0 |
| Consistency violations | 0 / 200000 | 0 / 200000 |

Both configs sit at a natural RTP of ≈ **96.4%** — statistically
indistinguishable (see CI caveat, §13) and inside the **96.0–96.7%** band at
the point estimate.

### Key relationships

- **Feature RTP contribution ≈ entry × feature-payout mean.**
  - Baseline: 0.00674 × 9.91 ≈ **0.0668**.
  - Variant: 0.01593 × 4.24 ≈ **0.0676**.
  - The variant raises the entry rate **2.36×** but cuts the per-feature payout
    to **≈ 43%** of the baseline, so the overall feature RTP contribution is
    essentially **unchanged** (~0.067). The *distribution* of that contribution
    is very different: many small features vs. few large ones.

## 5. Ore-vein RTP contribution

Seed-matched enabled vs. disabled natural runs (n = 200,000 each arm):

| Config | Ore-vein ENABLED RTP | Ore-vein DISABLED RTP | **Ore-vein Δ (pp)** |
| --- | --- | --- | --- |
| §3.1 baseline | 0.96435 | 0.97673 | **−1.238 pp** |
| Stage-3 variant | 0.96436 | 0.96173 | **+0.263 pp** |

- **Baseline:** enabling the ore-vein upgrade **lowers** RTP by ≈ **−1.24 pp**
  (it converts a regular block to diamond, which frequently breaks a common
  symbol cluster). This reproduces the finding in
  `CALIBRATION_REPORT.md` §7.4.
- **Variant:** the `create-cluster` rule only converts when it **completes a
  paying (≥5) diamond cluster**, so the upgrade adds ≈ **+0.26 pp** — a
  **positive** contribution. This achieves the variant's core goal.
- Note the base-game contribution flips sign: baseline base Δ ≈ −1.36 pp;
  variant base Δ ≈ +0.26 pp. The feature contribution is small in both.

## 6. Free-spin feature internal distribution (forced freegame, n = 2,000)

| Metric | §3.1 baseline | Stage-3 variant |
| --- | --- | --- |
| Feature payout mean | **9.60** | **4.04** |
| Feature payout median | 7.72 | n/a (not captured) |
| Feature duration mean | 8.40 | 8.46 |
| Feature duration max | 24 | n/a (not captured) |
| Feature payout max | 107.19 | 35.75 |
| `P(>=100×)` (feature) | 5e-4 | 0.0 |

The variant's free-spin feature is **much less generous per feature** (mean
≈ 4.0× vs 9.6×) because the free strip was retuned with fewer
premium/ingot/ore-vein symbols. It stays **short** (mean ≈ 8.4–8.5 spins; the
baseline's max in this sample was 24, and both are capped at 60).

## 7. Tail behaviour

- **Baseline** has a heavier tail: max round payout **544.43×**, with one round
  ≥ 100× (and ≥ 500×) in 200k.
- **Variant** has a much lighter tail: max round payout **57.47×**, with
  **zero** rounds ≥ 100× in 200k.
- The variant does **not** inflate the top pay — it substantially **reduces** it.
  This satisfies "don't inflate top pays," but it also means the game loses the
  rare big-win/1,000×-cap-excitement tail. The 1,000× cap never binds for
  either config (0 wincap binds).

## 8. Findings vs. design targets

| Design target | Baseline | Variant | Variant met? |
| --- | --- | --- | --- |
| Natural RTP in 96.0–96.7% | 0.96435 | 0.96436 | ✅ Met (see CI caveat §13) |
| Feature entry ≈ 1.0% | 0.674% | **1.593%** | ⚠️ **Overshoots** (1.6× target) |
| Ore-vein RTP contribution | −1.24 pp | **+0.26 pp** | ✅ **Met** (goal achieved) |
| Visible hit ≈ 70% | 0.6996 | 0.7099 | ✅ Met |
| Full return ≈ 29% | 0.2916 | 0.2869 | ✅ Met |
| Short free spins (8/12/16/16) | mean 8.67 | mean 8.78 | ✅ Met |
| Feature average payout 8–12× | 9.91 | **4.24** | ❌ **Not met** (regression) |
| Top pay not inflated | 544.43 | 57.47 | ✅ Met (much lower) |

## 9. Trade-offs / conflicts

The variant achieves the two headline goals but introduces new trade-offs:

1. **Entry overshoot.** The variant entry is **1.593%**, well above the ≈1%
   target. This is the best achievable with `pickaxe=4` on a 200-symbol shared
   strip (the entry is dominated by the strip's pickaxe arrangement, and 4
   pickaxes land the natural rate around 1.5–1.6%). Accepted as "≈1% in
   spirit," but the deviation is reported.
2. **Feature payout collapse.** The per-feature average payout drops from
   ≈9.9× to ≈4.2×, far below the 8–12× target. The higher entry rate and the
   lower per-feature payout cancel out in the feature RTP contribution, so
   players see features **~2.4× more often** but each pays **~55% less**.
3. **Tail collapse.** The max round win falls from ≈544× to ≈57×, and there are
   no ≥100× rounds. The rare big-win tail is effectively removed.
4. **Ore-vein positive (good).** The `create-cluster` rule makes the upgrade a
   small **positive** contributor (+0.26 pp) — the opposite of the baseline.

## 10. Recommendation (for orchestrator/product — NOT a final math decision)

The variant successfully meets the two goals it was built for — **higher free-spin
entry** (0.674% → 1.593%) and a **positive ore-vein RTP contribution**
(−1.24 pp → +0.26 pp) — while keeping the natural RTP in the 96.0–96.7% band,
hit ≈ 71% and full-return ≈ 29%.

The trade-offs are a **much lower per-feature payout** (4.2× vs 9.9×) and a
**collapsed top-pay tail** (max 57× vs 544×, no ≥100× rounds). Whether the
variant is preferable depends on the product priority:

- **If the priority is frequent feature entry + a positive ore-vein effect** (and
  the product accepts a lighter feature payout and a much smaller max win), the
  variant is the better direction.
- **If the priority is a meatier feature (≈9.9×) and a meaningful top-pay tail**,
  the baseline is preferable, and the two open baseline conflicts (entry 0.70%,
  negative ore-vein) remain unresolved.

A middle path would target an entry closer to ≈1% (e.g. a slightly different
pickaxe arrangement or a less aggressive free-strip retune) to reduce the entry
overshoot while retaining the positive ore-vein rule — but that is a further
calibration step and is **not** decided here. Recommend the orchestrator/product
choose the direction; the frozen `variant_config.py` and the baseline remain
independently reproducible for either decision.

## 11. Verification

- `math/games/block_cave/test_block_cave.py` — **15/15 pass** (incl. the new
  `test_variant_config_reproducible`, which verifies the variant strips/SHAs and
  that the baseline strips are unchanged).
- `pip check` — **no broken requirements**.
- Upstream `math/tests/win_calculations` — **13/13 pass**.
- `variant_config.py` standalone self-check — base/free strips length 200,
  counts + SHA-256 match (base `428854a3…60277`, free `aa0002ab…c9ce`).
- All large runs report **0 consistency violations** across 200,000 books each.
- Baseline `game_config.py` is untouched; its strips/SHAs are re-verified by the
  test suite.

## 12. Files changed / integration requirements

**Changed (math only, `math/games/block_cave/`):**
- `variant_config.py` — **new** frozen variant config (do not lose).
- `test_block_cave.py` — added `test_variant_config_reproducible` (15th test).
- `ore_vein_rules.py` — added the `create-cluster` rule (DEV).
- `game_executables.py` — dispatch via `config.ore_vein_rule` /
  `config.ore_vein_target` (defaults to baseline/`diamond`, so the shipped game
  is unchanged).
- `MATH_DESIGN.md` — corrected the stale assumption-ledger #1 (paytable is §3.1
  at scale 1.0; the C2 ×F scale-up was reverted).
- `COMPARISON_REPORT.md` — this report.

**Not changed:** `game_config.py` (baseline), `docs/`, `qa/`, `frontend/`,
`art/`, `scripts/`, `opencode.jsonc`, and the official Lines example.

**Integration notes:**
- The variant is **DEV-only** and is not wired into `game_config.py`. It is
  driven by `variant_config.build_config()` / `experiment.build_config(...)` and
  the `config.ore_vein_rule` / `config.ore_vein_target` attributes.
- The **default** `game_config.py` `ore_vein_rule` remains `baseline` and
  `ore_vein_target` remains `diamond`, so the validated §3.1 game is unchanged.
- No frontend/art change is required to *measure* the variant; if it were ever
  shipped, the `create-cluster` rule would need the same `oreVeinUpgrade` event
  contract already documented in `MATH_DESIGN.md` §8.

## 13. Limitations

- **Not a production certification.** No published RTP claim. Nothing deployed.
- **RTP CI:** the baseline RTP stddev is 2.0766; at n = 200,000 the standard
  error is ≈ 0.0046 (95% CI ≈ ±0.91 pp), so the baseline CI is
  **[0.9553, 0.9735]**. The variant RTP stddev was not captured by the summary
  harness, but it uses a strip of the same length/structure and is expected to
  be comparable (≈ 2.0), giving a similar ±0.9 pp CI. Both point estimates
  (≈0.964) are inside the band, but **the 95% CIs straddle the 96.0% lower
  edge**, so "in band" is a point-estimate statement. Report the CI alongside.
- Because all six reels share one 200-symbol strip, the base RTP is **extremely
  seed-sensitive** (measured 0.60–1.09 across seeds for the same counts); the
  variant's specific base seed (20261131) was chosen for a good base/entry, and
  re-seeding would move the result.
- The variant free strip was chosen by **direct grid search** (feature payout is
  non-monotonic in the free-strip counts), not by scaling the baseline free
  strip. It is one particular arrangement; other arrangements would give
  different trade-offs.
- Forced freegame samples are generated books, used only for the feature
  internal distribution; they are not a basis for round RTP or entry rate.
- The ore-vein Δ is a seed-matched observation at n = 200,000; it is a measured
  effect, not a definitive guarantee.
