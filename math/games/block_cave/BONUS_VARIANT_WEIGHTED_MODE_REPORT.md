# Block Cave — Variant P: preliminary weighted mode (DEV, unpublished)

**Status:** DEV-only preliminary exploration. **This is NOT a production
certification and makes NO published RTP claim.** Owner: Math agent. Scope:
build a *preliminary weighted mode* for Variant P (persistent-ore-vein bonus)
that targets a published RTP of **~96.3%** and report the play profiles computed
from exactly those final weights. Nothing here is deployed, published or
qualified as a production distribution. The Rust optimizer has not been run for
this game (see §11 Feasibility).

---

## 0. Executive summary

A **minimum-KL re-weighting** of the natural Variant P book distribution to a
published RTP of **0.963** is **sensible** and achieves all target play profiles
at the same time:

| metric | natural (base LUT) | weighted (published) |
|---|---|---|
| **RTP** | 0.9457 | **0.9630** (target 0.963) |
| visible hit | 0.6985 | 0.6990 |
| full return (≥1.0×) | 0.2489 | 0.2498 |
| free-spin entry | 0.00709 | 0.00742 |
| **≥100× rate** | 1.011e-4 (1:9,890) | **1.286e-4 (1:7,776)** |
| ≥100× Wilson 95% | [8.75e-5, 1.169e-4] | [1.130e-4, 1.462e-4] |
| ≥500× / ≥1000× | 0 / 0 | 0 / 0 |
| max band boost | — | **1.59×** ([200,500) band) |
| KL divergence | — | 1.58e-5 |

The weighted ≥100× interval lies entirely inside the acceptable band
(1:5,000–1:20,000). Distortion is tiny (max band boost 1.59×, KL 1.58e-5), and
hit / full-return / entry are essentially preserved (hit up 0.0005, entry up
4.7%). **No production RTP is claimed** — this is a DEV weighting of a natural
sample to a design target.

---

## 1. Config measured (what this is)

`math/games/block_cave/candidate_lapis_persistent_config.py` — the Variant P
config, built with `build_config()` (self-contained, sets
`ore_vein_persist_max = 7`) and the ore-vein upgrade enabled via
`calibrate.set_ore_vein_enabled(True)`.

- **Strips** — byte-identical to the Lapis Lazuli strips. Base SHA
  `00af3ba5…258181`, free SHA `bc15b4fb…4db4c47`.
- **Paytable** — merged 5-tier `VARIANT_PAY_RANGES = [(5,7),(8,10),(11,14),(15,19),(20,30)]`,
  small-cluster (5–7) reduced, premium/ingot unscaled, common-scale ≈ 1.10.
  No bonus multiplier.
- **Ore-vein rule** — `create-cluster` → `diamond`.
- **Persistent gate** — `config.ore_vein_persist_freespins = True`,
  `config.ore_vein_persist_max = 7`.

This config is identical to the one measured in `BONUS_VARIANT_RTP_REPORT.md`.
Only the *weights* are changed here (a DEV re-weighting); the game rules,
payouts and strips are untouched.

---

## 2. Method — books → base LUT → optimized LUT

### 2.1 The published pipeline (as given, not re-derived)

The **natural / base** LUT is one row per simulated book:
`library/lookup_tables/lookUpTable_<mode>.csv`, rows `bookId,1,payoutMultiplier`
where `payoutMultiplier` is the integer `round(min(baseGameWins+freeGameWins,1000)*100)`.
The optimizer reads `win = payoutMultiplier/100.0` (bet units). Because every
book has weight 1, base-LUT RTP = Σ(win)/N = the **natural** RTP.

The **optimized** LUT is `library/publish_files/lookUpTable_<mode>_0.csv`, rows
`bookId, weight, rounded_win` with `rounded_win = win*100`. The Rust optimizer
re-weights by WIN VALUE / band and distributes weight **uniformly** across all
books in a band. **Published RTP = Σ(weight·win) / Σ(weight)**.

The Rust band edges (`optimization_program/src/main.rs` `get_win_ranges`,
lines 392–408) are exactly:
`[0,0.1) [0.1,1) [1,2) [2,3) [3,5) [5,10) [10,20) [20,50) [50,100) [100,200) [200,500) [500,1000) [1000,2000) [2000,3000) [3000,5001)`.

### 2.2 This report's weighting

Because the Rust optimizer is not runnable for Block Cave today (see §11), this
report reproduces its **RTP-targeting model** on the natural books:

1. Partition the N books into the 15 bands above.
2. Natural band probability `p_b = count_b / N`, band mean win `m_b`.
3. Solve for band weights `q_b ≥ 0`, `Σ q_b = 1`, `Σ q_b·m_b = 0.963`,
   **minimising KL divergence** `Σ q_b·log(q_b/p_b)`. The exact minimum-KL
   solution is the exponential tilt `q_b ∝ p_b · exp(λ·m_b)`; λ was found by
   bisection (monotonic in λ). This mirrors the optimizer's RTP targeting with
   the **smallest possible distortion** from the natural distribution.
4. Within each band distribute weight uniformly: `w_i = q_band(i) / count_band(i)`,
   so `Σ w_i = 1`.
5. Verify published RTP `Σ(w_i·win_i) / Σ(w_i) ≈ 0.963`.

**Solver:** a convex closed-form tilt (1-D root-find on λ). No scipy needed
(scipy is not installed in `math/.venv`); implemented with numpy `logaddexp`
for numerical stability. This is the KL method the task requested (not
sum-of-squares / max-ratio).

---

## 3. Sample & reproducibility

- **Config module:** `candidate_lapis_persistent_config`.
- **Rounds:** 1,800,000 natural base rounds (`criteria=basegame`, no forcing),
  the only correct basis for round RTP, hit, full-return, entry rate and the
  round ≥100× tail.
- **Fresh, disjoint, never-used seed ranges:** 170M, 180M, 190M, 200M, 210M,
  220M × 300,000 each. All start at ≥170M (prior work used 0–160M).
- **Throughput:** 2,341 r/s pooled (range-wise 2,150–2,442 r/s).
- **Runtime:** 768.9 s (~12.8 min) total.

Per-range values (pooled into ONE independent sample, not reported as separate
"seed RTPs"):

| range | RTP | std | ≥100× | r/s |
|---|---|---|---|---|
| 170M | 0.9497 | 3.079 | 22 | 2,267 |
| 180M | 0.9519 | 3.201 | 37 | 2,150 |
| 190M | 0.9426 | 3.076 | 27 | 2,405 |
| 200M | 0.9380 | 2.975 | 26 | 2,432 |
| 210M | 0.9440 | 3.093 | 30 | 2,380 |
| 220M | 0.9482 | 3.153 | 40 | 2,442 |
| **pooled** | **0.9457** | ~3.09 | **182** | **2,341** |

The pooled per-range RTPs are tightly clustered (0.9380–0.9519), so the pooled
0.9457 is robust and not a seed-range artifact.

---

## 4. Natural (base LUT) results — N = 1,800,000

| metric | value |
|---|---|
| **Natural RTP** (base-LUT RTP) | **0.94571** |
| base RTP contribution | 0.76158 |
| feature RTP contribution | 0.18413 |
| visible hit P(payout>0) | 0.69849 |
| full return P(≥1.0×) | 0.24886 |
| feature entry rate | 0.007087 (12,756 features) |
| feature payout mean / median / max | 25.98 / 20.68 / 332.56 |
| feature duration mean / median / max | 8.62 / 8.0 / 32 |
| round win max | 428.36 |
| **≥100×** | **182 / 1,800,000 = 1.011e-4 (1:9,890)** |
| ≥100× Wilson 95% | [8.745e-5, 1.169e-4] ≈ 1:11,435 to 1:8,554 |
| ≥100× split — base-only / with-fs | 1 / 181 (base-only share 0.55%) |
| ≥500× / ≥1000× | 0 / 0 |
| wincap bind | 0 |
| consistency violations | 0 |

The natural RTP (0.9457) is **below** the 96.0–96.7% engine band, consistent
with the prior 1.8M measurement (0.9462). This is the *reason* a weighting is
needed to reach a published ~96.3%.

---

## 5. Band model & final weights

### 5.1 Band statistics and solved weights

Solved with λ = **0.00179466** (KL minimiser, converged). Achievable weighted
mean range over non-empty bands is [0, 258.47].

| band (bet units) | count | p_b | m_b | q_b | ratio q_b/p_b | verdict |
|---|---|---|---|---|---|---|
| [0, 0.1) | 542,723 | 0.301513 | 0.000 | 0.300997 | 0.9983 | reduced |
| [0.1, 1) | 809,337 | 0.449632 | 0.434 | 0.449212 | 0.9991 | reduced |
| [1, 2) | 286,823 | 0.159346 | 1.409 | 0.159476 | 1.0008 | boosted |
| [2, 3) | 54,834 | 0.030463 | 2.383 | 0.030542 | 1.0026 | boosted |
| [3, 5) | 51,652 | 0.028696 | 3.839 | 0.028845 | 1.0052 | boosted |
| [5, 10) | 41,776 | 0.023209 | 6.405 | 0.023437 | 1.0098 | boosted |
| [10, 20) | 5,954 | 0.003308 | 13.94 | 0.003386 | 1.0236 | boosted |
| [20, 50) | 5,639 | 0.003133 | 30.55 | 0.003304 | 1.0546 | boosted |
| [50, 100) | 1,080 | 0.000600 | 65.65 | 0.000674 | 1.1231 | boosted |
| [100, 200) | 172 | 9.556e-5 | 126.69 | 1.197e-4 | 1.2531 | boosted |
| [200, 500) | 10 | 5.556e-6 | 258.47 | 8.819e-6 | 1.5875 | boosted |
| [500, 1000) | 0 | 0 | 0 | 0 | 0 | empty |
| [1000, 2000) | 0 | 0 | 0 | 0 | 0 | empty |
| [2000, 3000) | 0 | 0 | 0 | 0 | 0 | empty |
| [3000, 5001) | 0 | 0 | 0 | 0 | 0 | empty |

**Interpretation.** The min-KL tilt is **gentle and monotone in win value**:
it trims the two lowest bands ([0,0.1), [0.1,1)) by ≤0.17% and boosts every band
from [1,2) upward, with the boost growing with win value. The largest boost is
the [200,500) band (1.59×), which is also the largest-mean populated band. No
band is boosted more than 1.59× — far below the 5× "unreasonable" threshold.

Because the bands above [200,500) are empty on this sample (the design caps the
round win below 500 in 1.8M natural rounds; max observed 428.36), the weighting
cannot push weight onto ≥500× — so ≥500× / ≥1000× remain at 0 after weighting.

---

## 6. Published (weighted) metrics — from the FINAL weights

Computed from `w_i` (sum = 1). Published RTP `Σ(w_i·win_i)`.

| metric | value |
|---|---|
| **Published RTP** | **0.96300** (error +2e-16) |
| published RTP from integer-encoded weights | 0.96300 (error −8.8e-11) |
| weighted visible hit | 0.69900 |
| weighted full return | 0.24979 |
| weighted free-spin entry | 0.007417 (0.742%) |
| feature weight mass | 0.007417 |
| weighted feature payout mean / median | 26.77 / 21.15 |
| weighted feature duration mean / median / max | 8.66 / 8.0 / 32 |
| **weighted ≥100×** | **1.286e-4 (1:7,776)** |
| weighted ≥100× Wilson 95% | [1.130e-4, 1.462e-4] ≈ 1:8,848 to 1:6,839 |
| weighted ≥100× split — base-only / with-fs | 8.82e-7 / 1.277e-4 (share base 0.69%) |
| weighted ≥500× | 0 (Wilson upper 2.13e-6) |
| weighted ≥1000× | 0 (Wilson upper 2.13e-6) |
| Kish effective sample size | 1,799,940 |
| max / min-nonzero book weight | 8.82e-7 / 5.55e-7 |

**≥100× note.** The weighted ≥100× is **1:7,776** and its Wilson interval
[1:8,848, 1:6,839] lies **entirely inside** the acceptable 1:5,000–1:20,000
band. The tail remains **free-spin / persistent-vein driven**: 181 of 182
≥100× rounds need free spins; only 1 is base-only (weighted base-only share
0.69%). No ≥500× or ≥1000× round exists after weighting, and the 1,000× cap
never engages.

**Wilson CI method for a weighted proportion.** The weights are deterministic,
so I used the Kish effective sample size `n_eff = (Σw)² / Σ(w²) = 1/Σ(w²)` and
`k_eff = p̂·n_eff`, then applied the standard Wilson interval to `(k_eff, n_eff)`.
For near-uniform weights this reduces to the ordinary binomial Wilson interval;
here `n_eff ≈ 1.80M` (weights are near-uniform, so the CIs are effectively the
binomial ones). Documented for transparency.

---

## 7. Natural vs weighted comparison

| metric | natural | weighted | Δ |
|---|---|---|---|
| RTP | 0.9457 | 0.9630 | +0.0173 |
| visible hit | 0.69849 | 0.69900 | +0.00051 (ratio 1.0007) |
| full return | 0.24886 | 0.24979 | +0.00093 |
| free-spin entry | 0.007087 | 0.007417 | +0.00033 (ratio 1.047) |
| ≥100× rate | 1.011e-4 | 1.286e-4 | ×1.27 |
| ≥100× (1-in-X) | 1:9,890 | 1:7,776 | — |
| ≥500× / ≥1000× | 0 / 0 | 0 / 0 | 0 / 0 |
| feature payout mean | 25.98 | 26.77 | +0.79 |
| feature duration mean | 8.62 | 8.66 | +0.04 |

The weighting raises RTP by +1.73 pp while leaving the hit, full-return,
free-spin entry and feature profiles essentially unchanged (hit +0.07% relative,
entry +4.7% relative, feature payout mean +3%). The ≥100× rate rises 27% but
stays inside the band.

---

## 8. Sensibility assessment

The task's concern: can a **sensible** weighting hit 96.3% while keeping ≥100×
in 1:5,000–1:20,000, and preserving hit / entry?

**Verdict: SENSIBLE — yes.**

- **(a) Hits 0.963 published RTP.** `Σ(w·win)/Σ(w) = 0.96300` (and
  0.96300 from the integer-encoded weights). ✔
- **(b) ≥100× stays in band.** Weighted 1:7,776, Wilson [1:8,848, 1:6,839],
  entirely inside 1:5,000–1:20,000. ✔
- **(c) Play profiles preserved.** Hit 0.6990 (natural 0.6985, +0.07% rel),
  free-spin entry 0.00742 (natural 0.00709, +4.7% rel), full return 0.2498.
  ✔
- **Distortion is small.** Max band boost **1.59×** (the [200,500) band), far
  below the 5× threshold; KL divergence **1.58e-5**; only the two lowest bands
  are trimmed (each by ≤0.17%). No band collapses, hit does not drop, and the
  ≥100× rate does not leave the band.

So a **sensible weighting alone can hit 96.3%** for Variant P while keeping all
target play profiles — no paytable change / small-payout bump is needed for the
RTP target. (The fallback described in the task — a bounded increase of
small/medium payouts — is **not** required for this config.)

**Caveat on the ≥100× tail.** The tail is rare (182 natural hits; ~231 weighted
"effective" hits). Even though the Wilson interval sits inside the band, the
point estimate (1:7,776) is not a firm tail certification; it is a DEV
measurement on one 1.8M sample.

---

## 9. Book / lookup consistency

- **0 consistency violations** across all 1,800,000 books (via `calibrate.check_book`).
- **Base-LUT RTP = natural RTP:** `Σ(payoutMultiplier)/100/N = 0.9457134`
  computed directly from the CSV, matching the natural mean. ✔
- **Book→LUT cross-check:** `payoutMultiplier == round(min(base+free,1000)*100)`
  for all 1.8M books (0 mismatches); `round(win*100) == payoutMultiplier` for
  all books (0 mismatches).
- **Weighted RTP = target:** `Σ(w·win)/Σ(w) = 0.96300`; integer-encoded
  cross-check `0.96300` (error −8.8e-11).
- **Off-limits configs verified byte-identical** (SHA-256 unchanged, matches
  `BONUS_VARIANT_RTP_REPORT.md` §6):
  `candidate_a_config.py DE49BE20…`, `candidate_b_config.py 5073ACB4…`,
  `candidate2_config.py 10F1DC1D…`, `candidate_lapis_config.py DC343889…`,
  `variant_config.py DDD4DBD1…`, `game_config.py 9642B207…`,
  `gamestate.py ADFF2DC4…`, `game_override.py D9778C19…`,
  `ore_vein_rules.py AB161BFF…`, `game_executables.py 2B1D167B…`,
  `game_events.py 14948ACD…`, `game_calculations.py 5CC9CF2D…`,
  `calibrate.py 816796E3…`, `run.py A3455311…`, `test_block_cave.py 92D13B29…`,
  `candidate_lapis_persistent_config.py 27ECE240…`.

---

## 10. Artifacts (all new, `.runtime/block_cave/`, `vp_weighted_*`)

| file | contents |
|---|---|
| `vp_weighted_collect.py` | helper: run natural rounds, store per-book arrays |
| `vp_weighted_analyze.py` | helper: build base LUT, solve min-KL weights, compute metrics |
| `vp_weighted_180m.npz` | per-book arrays (pm, base, free, hit, feat, fspins) |
| `vp_weighted_180m.summary.json` | per-range + pooled natural summary |
| `vp_weighted_180m_an.json` | full weighting / metrics report (BOM-free) |
| `vp_weighted_base_lut.csv` | base LUT `bookId,1,payoutMultiplier` (1.8M rows) |
| `vp_weighted_optimized_lut.csv` | optimized LUT `bookId,weight,rounded_win` (1.8M rows) |
| `vp_weighted_smoke.npz/.summary.json/_an.json` | small smoke test (2k rounds, sanity only) |
| `vp_weighted_base_lut.csv`, `vp_weighted_optimized_lut.csv` | regenerated by the analysis run |

No existing `vp_*` or `final_*` files were overwritten. **No new files were
written into `math/games/block_cave/library/`** (the shared library remains
untouched; the collection uses `CalibrateState`, a no-op `imprint_wins`).

### Commands used

```powershell
# collection (1.8M natural rounds, fresh ranges)
& "math\.venv\Scripts\python.exe" .runtime\block_cave\vp_weighted_collect.py 300000 .runtime\block_cave\vp_weighted_180m 170000000 180000000 190000000 200000000 210000000 220000000

# weighting + metrics
& "math\.venv\Scripts\python.exe" .runtime\block_cave\vp_weighted_analyze.py .runtime\block_cave\vp_weighted_180m.npz .runtime\block_cave\vp_weighted_180m_an 0.963
```

---

## 11. Feasibility — is Block Cave wireable into the real Rust optimizer?

**Verdict: currently BLOCKED; feasible with a dedicated wiring task.** The Rust
binary itself is general and present (`math/optimization_program`), but the
Python-side entry path and the config/fence alignment are missing.

### 11.1 What the real path needs (from the reference `0_0_cluster/run.py`)

The standard path is:
`OptimizationSetup(config)` → `create_books(...)` (writes `library/lookup_tables/lookUpTable_<mode>.csv`
+ books) → `generate_configs(gamestate)` (writes `library/configs/math_config.json`)
→ `OptimizationExecution().run_all_modes(config, target_modes, rust_threads)`
→ `generate_configs` again → `create_stat_sheet` / `execute_all_tests`.

`run_opt_single_mode` reads `config.opt_params[mode]["parameters"]`, writes a
TOML setup, and runs `cargo run --release`. The Rust `main.rs` reads the base
LUT via `read_look_up_table(game_name, bet_type, path_to_games)` and the fences
from `library/configs/math_config.json`; it writes the optimized LUT to
`library/publish_files/lookUpTable_<mode>_0.csv`.

### 11.2 What is missing for Block Cave

1. **No `game_optimization.py`.** Block Cave has no `OptimizationSetup`, so
   `config.opt_params` is never set. `run_opt_single_mode` does
   `opt_config = game_config.opt_params` and then `params = obj["parameters"]`
   for the target mode — it would fail (no `opt_params`, no `parameters`).
2. **`run.py` is only a small prototype.** It runs a handful of seeded spins and
   writes books to a temp JSONL. It does **not** call `create_books`,
   `generate_configs`, `OptimizationExecution`, `create_stat_sheet` or
   `execute_all_tests`. So there is no base LUT and no `math_config.json` for the
   Rust binary to read.
3. **Single bet mode / no `bonus`.** Block Cave has one bet mode `base` (the
   separately priced bonus is deferred). The reference `0_0_cluster` targets
   `["base","bonus"]`. A single-mode run may work, but the `OptimizationSetup`
   must be authored for `base` only.
4. **`wincap` criteria absent.** Block Cave's `base` bet mode deliberately
   removed the `wincap` criteria distribution (documented in `game_config.py`:
   driving it through `create_books` would loop forever because the engine's
   `check_repeat` never consumes `force_wincap`). The reference optimizer's fence
   model includes a `wincap` fence (`ConstructConditions(rtp=0.001,
   av_win=wincap, search_conditions=wincap)`). Block Cave's optimization config
   would therefore need fences that exactly match its present criteria
   (`basegame`, `freegame`, `0`). Whether the Rust `exit_if_fence_has_no_books`
   / win-range logic tolerates a missing `wincap` fence is **unverified**.
5. **Design parameters not authored.** `OptimizationSetup` needs Block-Cave-specific
   `conditions` (rtp / hr / av_win / search_conditions per criteria),
   `scaling` bands, `parameters` (`num_show`, `num_per_fence`, `min_m2m`,
   `max_m2m`, `pmb_rtp`, `sim_trials`, `test_spins`, `test_weights`,
   `score_type`) and `distribution_bias`. These are a math-design decision, not
   just wiring, and would change the RTP/tail outcome.

### 11.3 Conclusion

The bottleneck is **not** the Rust code (it reads the standard base LUT +
`math_config.json` and writes the standard optimized LUT). It is the
**Python-side `OptimizationSetup` + a real driver `run.py`** and the
**config/fence alignment** (the removed `wincap` criteria vs. the optimizer's
fence expectations, and a single-mode target). I assess this as **blocked for
now, feasible with a dedicated wiring + math-design task**. Until then, the
weighted mode reported here is the *model* of the optimizer's RTP targeting
(min-KL band re-weighting), not its actual output.

---

## 12. Open issues

- **Not a production claim.** All numbers are DEV measurements / a DEV weighting.
  No published RTP is claimed; nothing is deployed.
- **Natural RTP below band.** The natural Variant P RTP is 0.9457 — below the
  96.0–96.7% band. The weighting lifts the *published* RTP to 0.963, but the
  **underlying game** still under-returns; this is a design decision, not settled
  here.
- **≥100× is rare and seed-sensitive.** 182 natural hits (231 weighted effective)
  in 1.8M spins. The point estimate (1:7,776) is not a firm tail certification;
  the Wilson interval [1:8,848, 1:6,839] sits inside the band but is still
  relatively wide.
- **The min-KL weighting is not the Rust optimizer's output.** It is the exact
  minimum-distortion solution to the *RTP constraint* the optimizer targets, but
  the real optimizer runs a pig/fence search with extra constraints (win-range
  fences, `distribution_bias`, `score_type`) that can change the outcome. Run the
  real optimizer (after §11 wiring) before treating these weights as authoritative.
- **Empty top bands.** No ≥500× round occurred in 1.8M natural spins; the [500,1000)
  and higher bands are empty, so no weight can be assigned there and ≥500×/≥1000×
  are 0. The 1,000× cap never engaged. If a ≥500× tail is desired, the paytable /
  persistent-vein cap would need to change — out of scope here.
- **No frontend/event-contract change.** The weighting is a lookup-table weight
  change only; book event types, ordering and `payoutMultiplier` are unchanged.
- **Not committed.** No off-limits config modified; `docs/STATUS.md` and all
  existing `BONUS_VARIANT_*` reports left untouched.
