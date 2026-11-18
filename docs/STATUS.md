# Setup status — 2026-11-17

The prepared setup has been applied to the original project at
`C:\Users\robin\Documents\stake\stake-game-ai`. Local installation and
verification are complete. The user subsequently reported that UniGPT works
in their PowerShell session. The custom game's specification and first art
templates are in progress; no custom math or frontend code has been started.

## Verified in the original project

- `scripts/setup.ps1 -Rust` installed all 36 frontend workspaces from the
  frozen lockfile, the isolated math environment, QA dependencies and Chromium;
  `cargo check --locked` passed. A second frozen pnpm install passed after the
  Storybook package update without downloading anything.
- The isolated Python environment passed `pip check`, the upstream Lines
  pytest suite (13 tests), and `scripts/math_smoke.py` (100 conditional rounds,
  seeded replay, free spins and zstd round-trip). The smoke books SHA256 is
  `3b1208d33fe7e2fb3e53cc5974e7c166a6baf0ba567687c017711c77eba2f97f`.
- Storybook starts on Windows. Playwright passed the official Lines example at
  1200 × 675 and 400 × 225: the canvas rendered and the Action completed at
  both sizes. Screenshots and the HTML report are in `.runtime`.
- OpenCode 2.3.0 parses the project config, discovers all five agents and lists
  `unigpt/DeepSeek-V4-Flash`. This is configuration validation, not an
  authenticated model call.
- The transfer preserved the two pre-existing frontend edits in
  `.setup-backup\20261117-154701-510` and did not replace the user's lockfile.

## Limits and remaining input

- A cold Storybook run spent over 20 minutes on Vite transforms and timed out.
  The completed, cached browser run passed both viewports in 16.8 minutes.
  Allow a long first load on this machine; a permanent spinner is not accepted.
- The optional Adobe Typekit font reported `Web font load inactive` on localhost.
  The SDK resolves this as a fallback; the browser test excludes only that
  exact message from console failures. Other console, JavaScript, HTTP and
  request errors still fail the test. The stock example's translation test
  overlay clips at 400 × 225.
- A temporary pytest cache with sandbox-only permissions was removed; the
  final pytest run passed without warnings. Cargo passed with warnings in
  upstream optimizer code.
- UniGPT works according to the user's 2026-11-17 report. An authenticated
  model tool call was not independently rerun in this Codex session; its
  `UNIGPT_API_KEY` environment variable is absent. Context7 remains disabled
  and untested.
- The math smoke is a conditional development check, not an RTP estimate or
  production certification. `docs/GAME_SPEC.md` now contains the user's 6×5
  cave-game direction; its RTP and hit-frequency targets are unmeasured.

## Custom game planning

- `docs/GAME_SPEC.md` records the selected mechanics and 1,000× round cap.
  `docs/PROJECT_PLAN.md` defines staged math, art, frontend and independent
  QA handoffs. `docs/DESIGN_SYSTEM.md` records the draft visual direction.
- `art/templates/` now contains 11 editable symbol SVGs, one cave background
  SVG and one original side-explorer SVG, with generator, manifest and a
  400×225 contact preview. An independent QA agent checked all 13 SVGs for
  XML structure, viewBox, titles and external references; all passed. The
  mini preview shows all 30 board symbols without overlap from the explorer.
  `W`/`FS` badges and some ore colors still need real-UI small-size checks.
- No custom game's RTP, hit rate, feature rate, or bonus payout has been
  simulated or verified. The sample Storybook proves only the SDK example.
- The official Engine approval guidelines prohibit gamble features and
  continuation. The requested player-selected bonus-risk upgrade is therefore
  excluded. An automatic in-book upgrade would need platform confirmation.

## Stage 1 — Math design and QA review (2026-11-17)

- The math agent produced `math/games/block_cave/MATH_DESIGN.md` (single file,
  no code, no reels, no frontend). It proposes the 6×5 orthogonal-cluster win
  rule, paytable, base and free-spin strip weights, an ore-vein wild +
  adjacent-upgrade rule, a 3-pickaxe scatter trigger with short free spins,
  the sum-then-cap 1,000× round cap, and a provisional event schema. Every
  non-simulated number is marked ASSUMPTION and collected in a 17-item ledger.
- The independent QA agent reviewed it and wrote
  `qa/reports/block_cave_stage1_math_review.md`. **Verdict: not ready for
  Stage 2.** Key findings: the natural scatter rate is mis-stated (design
  claims 0.8% / 1-in-125; independent binomial gives ≈1.01% / 1-in-98.7); the
  reel-strip symbol *arrangement* is unspecified so RTP/hit/feature claims are
  not reproducible (QA's simulations spanned ≈11% → ≈3626% RTP by arrangement
  alone); the ore-vein→`ingot` upgrade inflates RTP by ≈ +14pp (to ≈110%) in a
  faithful simulation, contradicting the "low activation" mitigation premise
  (≈0.575 activations/round, 34.7% of rounds); the 1,000× cap is effectively
  unreachable in the base game (max observed ≈205.78×, P(≥500×)=0%); the
  event-ordering table does not match the real engine emission sequence and
  `oreVeinUpgrade` is a genuinely new SDK event type needing math/frontend
  agreement; and implementing "initial-board-only" scatter counting requires
  overriding engine `draw_board`/`check_fs_condition`.
- **Stage 1 blockers for Stage 2:** specify the strip arrangement; correct the
  scatter arithmetic; re-bound the vein-upgrade RTP inflation; ratify the
  `oreVeinUpgrade` event contract and correct event ordering; and acknowledge
  the engine-code touchpoints for natural triggering. No game logic or
  frontend was implemented in this step. No measured RTP, hit rate or feature
  rate is claimed for Block Cave.

### Stage 1 resolution (2026-11-17) — READY FOR STAGE 2

The math agent revised `math/games/block_cave/MATH_DESIGN.md` to address all
10 findings (F1–F10). An independent second QA review
(`qa/reports/block_cave_stage1_math_review2.md`) confirmed **9 of 10 resolved**
and the frontend agent reviewed the `oreVeinUpgrade` contract as a draft
(AGREE WITH CORRECTIONS: (A) vein/upgrade cardinality, (B) in-cluster target,
(C) `wincap` union+handler requirement). The only remaining critical blocker
was F2 (strip reproducibility).

The math agent then documented an authoritative, executable generator
`build_strip(seed, counts)` (base seed `20261117`, free-spin seed `20261118`)
and embedded the exact 200-symbol lists plus SHA-256 for each strip. An
independent QA re-verification (`qa/reports/block_cave_stage1_f2_reverify.md`)
extracted the code from the file, executed it, and confirmed both strips
regenerate byte-for-byte, length 200, counts match the weight tables, and the
SHA-256 values match
(`7d04c138…2451` base / `f7f48c53…9754` free-spin). **F2 RESOLVED.**

**Verdict: Stage 1 is READY FOR STAGE 2.** All 10 findings resolved; frontend
contract corrections A/B/C confirmed. Remaining items are product decisions,
not blockers (see the open-decisions list in the design and the final report
to the user). No measured RTP/hit/feature rate is claimed; all figures are
ASSUMPTION/ILLUSTRATION pending Stage 2/3 simulation on the exact strips.

See `TEST_REPORT.md` for the command-level evidence and `SETUP.md` for usage.

## Stage 2 — Math prototype (in progress)

### Mechanics-framing correction (2026-11-17) — VERIFIED

The math agent corrected a framing error in `math/games/block_cave/MATH_DESIGN.md`:
the ore-vein upgrade is a **normal in-round mechanic**, not a free-spin "bonus
upgrade", and it is distinct from the deferred free-spin bonus-tier upgrade. The
correction was applied in four places (§1 stateless bullet, §9 open decision,
Assumptions ledger row #20, and a new "Revision history" entry C1). The framing
is a pure wording change: no numeric value, rule, event ordering or payload
changed.

An independent QA review (`qa/reports/block_cave_stage2_framing_correction.md`)
checked the file against `docs/GAME_SPEC.md` and `docs/PROJECT_PLAN.md`, grepped
all `upgrade`/conflation terms, and returned **PASS**: no residual conflation and
no mechanics contradiction. No implementation file was modified.

The math implementation (books, run.py, override logic, test script) was
completed. An independent QA pass
(`qa/reports/block_cave_stage2_math_review.md`) re-verified the six mechanics
against the real emitted events (win, tumble, ore-vein with/without target,
three-pickaxe trigger, retrigger clamp, 1000× cap), re-derived both strips
(byte-for-byte, matching the documented SHA-256 values), checked book structure,
and confirmed off-limits file integrity. **Verdict: PASS WITH FINDINGS** (no
blocking defect). The strips are deterministic; the prototype books are
structurally valid (60 books, contiguous event indexes, `payoutMultiplier` in
`[0,100000]`, correct cascade ordering); `run.py` completes without hanging and
its output is labeled DEV observation only.

Findings: **F1 (MEDIUM, latent)** the `wincap` bet-mode criteria distribution
can never converge (`force_wincap` is never consumed; `win_criteria=1000.0` is
unreachable on the strips), a footgun for any downstream `create_books` run;
**F2 (LOW, theoretical)** `process_ore_vein_upgrades` runs after
`evaluate_wincap` so an `oreVeinUpgrade` could follow `wincap` without a
`tumbleBoard` (by-design per §8 ordering, not observed); **F3 (INFO)** the DEV
disclaimer is in `run.py` stdout but not embedded in the JSONL; **F4 (INFO,
Stages 5–6)** `oreVeinUpgrade` and `wincap` need frontend `BookEvent` union members
+ handlers (no Block Cave frontend exists yet); **F5 (INFO)** no measured
RTP/hit rate (correctly disclaimed). No measured RTP, hit frequency, feature
rate or volatility is claimed for Block Cave.

F1 fix (remove the non-convergent `wincap` criteria distribution) is in
progress; the author re-runs the affected checks and QA re-verifies.

### Stage 2 resolution (2026-11-17) — PASS

The math author addressed **F1** by removing the non-convergent `wincap`
criteria distribution from `math/games/block_cave/game_config.py` (the
`criteria="wincap"`, `win_criteria=1000.0`, `force_wincap=True` distribution)
and re-normalizing the surviving quotas to `0.6316 / 0.2105 / 0.1579`
(sum = 1.0, preserving the original 0.6:0.2:0.15 ratio), with a comment
explaining why. `run.py`'s docstring was updated accordingly. The `wincap` cap
**mechanism** (event, `evaluate_wincap`, 100,000-unit clamp) is unchanged and
still exercised deterministically by `test_wincap`.

An independent QA re-verification (addendum to
`qa/reports/block_cave_stage2_math_review.md`) re-ran the test suite (**10/10**,
including `test_wincap`), `run.py` (completes without hanging, byte-identical
output), and inspected the live config: no `wincap` criteria remains, quotas sum
to 1.0, `win_criteria=[None,None,0.0]`, no Block Cave code path can hang on a
`wincap` criteria. No regression to the surviving distributions, the cap
mechanism, or off-limits files. **F1 RESOLVED — final Stage 2 verdict: PASS.**

Remaining non-blocking items (unchanged): **F2** `process_ore_vein_upgrades` can
run after `evaluate_wincap` (by-design per §8 ordering, not observed); **F3** the
DEV disclaimer is in `run.py` stdout but not embedded in the JSONL; **F4** (Stages
5–6) `oreVeinUpgrade` and `wincap` need frontend `BookEvent` union members +
handlers (no Block Cave frontend exists yet); **F5** no measured RTP/hit rate
(correctly disclaimed).

**Limitations:** No measured RTP, hit frequency, feature rate or volatility is
claimed for Block Cave — all such figures are design targets or DEV
observations. The `wincap`/1,000× path is only proven via a constructed board,
not by natural simulation (the cap is essentially unreachable on the design
strips per §7). The prototype books are deterministic; `run.py` is a seeded DEV
run, not an RTP estimate. Visual/Playwright QA is not applicable until the
Block Cave frontend exists (Stage 6). The next stage in `PROJECT_PLAN.md` is
Stage 3 math calibration; the frontend contract and app follow in Stages 5–6.

## Stage 3 — Math calibration (in progress)

### Calibration result (2026-11-17) — RTP target MET, several targets NOT met

The math agent calibrated the paytable and produced
`math/games/block_cave/CALIBRATION_REPORT.md` plus `MATH_DESIGN.md` revision
**C3**. The conclusion is that the **MATH_DESIGN §3.1 paytable at scale 1.0** is
the calibrated table (the earlier ×F scale-up, revision C2, was reverted). The
reel strips, weights/counts, `wincap=1000.0` and seeds (20261117 / 20261118) are
unchanged.

The orchestrator independently re-measured the checked-in config (not trusting
the report) and reproduced the result:

| Metric | Orchestrator independent (200k natural) | Report (500k) |
| --- | --- | --- |
| Natural base-game RTP | **0.9643** | 0.9648 |
| base contribution | 0.8975 | 0.8945 |
| feature contribution | 0.0668 | 0.0703 |
| RTP stddev | 2.077 | 1.94 |
| Visible hit `P(payout>0)` | 0.6996 | 0.6985 |
| Full return `P(payout>=1.0×)` | 0.2916 | 0.2910 |
| Feature entry rate | 0.0067 (1348/200000) | 0.00704 |
| Feature duration mean / max | 8.67 / 28 | 8.73 / 36 |
| Feature payout mean / median | 9.91 / 7.87 | 9.98 / 7.86 |
| Round max observed | 544.43 | 544.43 |
| `wincap` binds | 0 | 0 |
| Consistency violations | 0 / 200000 | 0 |

Additional independent checks by the orchestrator:
- **Strip SHA-256 reproduced:** base `7d04c138…b2451`, free `f7f48c53…d89754`
  (seed 20261117 / 20261118), length 200, counts match the weight tables.
- **Paytable equals §3.1** (e.g. `earth` = [0.18,0.28,0.46,…]); the config is
  **not** the ×F scaled version.
- **Scatter entry (board-draw) `P(>=3 pickaxes)` = 0.00702** over 200k boards,
  matching the measured feature-entry rate (~0.7%).
- **Ore-vein upgrade contribution:** 150k enabled RTP 0.9640 vs 150k disabled
  RTP 0.9764 ⇒ the upgrade **lowers** base-game RTP by ≈ **−1.24pp** on this
  strip (report §7.4). Reproduced.
- **Tests:** `test_block_cave.py` 11/11 pass (incl.
  `test_wincap_ore_vein_upgrade`), `pip check` clean, upstream
  `math/tests/win_calculations` 13/13 pass.

**Verdict:** the RTP band target (96.0–96.7%) is **MET** (point estimate ≈
96.4%). Frequent small wins and short free spins are preserved; top pays were
**not** raised to reach 1,000× (round max ≈ 544×, the 1,000× cap never binds in
the base game). An independent QA agent pass is running
(`qa/reports/block_cave_stage3_calibration_review.md`).

### Candidate 2 — refined direction (2026-11-18)

Following the user's refinement direction (target ≈1% entry, 8–12× feature
payout, short free spins, positive ore-vein, ≈45% visible hit, ≈15% full return,
preserved rare-big-win tail), the math agent produced a **separate DEV Candidate
2** (`math/games/block_cave/candidate2_config.py`, base seed 20261103 / free seed
20261118, `create-cluster`→`diamond`, §3.1 paytable scale 1.0) and a three-way
comparison (`CANDIDATE2_REPORT.md`) vs the §3.1 baseline and the Stage-3 variant.
`game_config.py`, `variant_config.py`, `ore_vein_rules.py` and
`game_executables.py` were **not** modified; the shipped default remains
`baseline`/`diamond`.

Three-way results (n=200k natural, seed-matched; forced freegame for feature):

| Metric | §3.1 baseline | Stage-3 variant | **Candidate 2** |
| --- | --- | --- | --- |
| Natural RTP | 0.96435 | 0.96436 | **0.95087** (CI [0.9377, 0.9640]) |
| Visible hit | 0.6996 | 0.7099 | **0.4652** |
| Full return | 0.2916 | 0.2869 | **0.1840** |
| Feature entry | 0.674% | 1.593% | 1.617% |
| Feature payout mean | 9.91× | 4.24× | **10.78×** |
| Feature duration mean | 8.67 | 8.78 | 8.90 |
| Ore-vein Δ | −1.24 pp | +0.26 pp | **+0.27 pp** |
| Max round | 544.43× | 57.47× | **184.55×** |
| P(≥100×) | 5e-6 | 0 | 2.5e-05 |
| Consistency violations | 0 | 0 | 0 |

Candidate 2 uniquely reaches the §3.3 player-experience targets (visible hit
≈46%, full return ≈18%), a meaty 10.78× feature, short free spins (mean 8.9, max
44), a **positive** ore-vein (+0.27 pp) and a meaningful tail (max 184.6×,
≥100× ≈1-in-40k) — **but its natural RTP is not robustly in the 96.0–96.7%
band.** It measured **0.9656 (in band) at n=100k** and **0.95087 (below band) at
n=200k**; the two point estimates differ by ~1.5 pp with overlapping CIs, so the
RTP is genuinely borderline and highly seed-sensitive (RTP stddev ≈3.0).

The orchestrator independently re-measured Candidate 2 at n=100k: **RTP 0.9656**
(base 0.7871, feature 0.1785, hit 0.4677, full 0.1852, entry 0.0167, feature
payout 10.71×, ore-vein Δ +0.289 pp, 0 violations) — **reproducing the math
agent's 100k number exactly** and corroborating the hit/full/feature/tail profile
and the seed-sensitivity.

**QA verdict (independent): PASS WITH FINDINGS**
(`qa/reports/block_cave_stage3_candidate2_review.md`). QA reproduced the
Candidate 2 strips/SHAs, the 16/16 test suite, `pip check`, upstream
`win_calculations` 13/13, confirmed off-limits files unchanged, and reproduced
the 200k natural numbers **byte-for-byte**. No config defect, no blocker.

- **F1 (MEDIUM)** — the report's claim that the §3.3 hit/full targets and the RTP
  band are "not simultaneously achievable" is **stronger than the evidence
  supports**. The arithmetic (base ≈0.777 + feature ≈0.174 ≈ 0.951, CI straddling
  96.0%) is confirmed, but the CI straddles 96.0%, the config is extremely
  seed-sensitive, and only ≈0.9 pp more base contribution is needed to reach
  96.0%. QA recommends rewording to "this seed/strip arrangement falls below the
  band" and **exploring a different base seed** before concluding the two target
  sets are irreconcilable.
- **F2 (LOW)** — console summary prints natural `P(≥100×)` as `0.0000`; the JSON
  value is `2.5e-05` (the report table shows the correct value).
- **F3 (INFO)** — visual/Playwright QA not applicable (no Block Cave frontend
  exists yet; frontend is Stages 5–6).
- **F4 (INFO)** — the baseline/variant comparison arms were spot-checked, not
  re-run independently.

**Tests:** `test_block_cave.py` 16/16 (incl. `test_candidate2_config_reproducible`),
`pip check` clean, upstream `win_calculations` 13/13.

### Candidate 2 — bounded base-seed search (out-of-sample) (2026-11-18)

Per the user's direction (keep the §3.1 paytable, do **not** relax the 96.0–96.7%
RTP band, keep the §3.3 profile), the math agent ran a **bounded base-strip-seed
search** and validated the promising seeds **out-of-sample** on a fresh,
previously-unused spin range. Helpers: `.runtime/block_cave/screen_c2_base.py`
(screen) and `.runtime/block_cave/measure_c2_seed.py` (OOS). `game_config.py`,
`variant_config.py`, `ore_vein_rules.py`, `game_executables.py` and
`candidate2_config.py` were **not** modified; no new winning seed config was
created.

- **Screening:** 21 base seeds (reference 20261103 + systematic block
  20265001–20265020) at n=50k on the tuning range (`start_seed=0`). Seeds with
  inflated entry or RTP far out of band were rejected as §3.3 violations.
- **OOS validation:** 5 seeds at n=200k per ore-vein arm + 20k forced freegame on
  `start_seed=1_000_000` (disjoint from the tuning range 0–199,999). All 0
  consistency violations.
- **Result:** the reference seed **20261103** is the best fit. The math agent's
  OOS reading (range 1M, n=200k): RTP **0.9604** (CI [0.9468, 0.9740], std 3.10),
  hit 0.4641, full 0.1847, entry 0.01597, feature payout 11.07×, max round
  210.46×, P(≥100×) 6.5e-05, **ore-vein Δ +0.325 pp**, 0 violations. The other
  validated seeds overshoot (20265001 ≈1.015) or fall short (20265006 0.917,
  20265010 0.869, 20265011 0.756) of the band.
- **Independent OOS cross-checks (different fresh ranges) — the band is NOT
  robust.** Two independent agents re-measured seed 20261103 on ranges disjoint
  from both 0 and 1,000,000:
  - Orchestrator (`start_seed=5_000_000`, n=100k): RTP **0.9512** (CI
    [0.9329, 0.9696]), below band.
  - QA (`start_seed=5_000_000`, n=200k): RTP **0.9576** (CI [0.9446, 0.9706]),
    below band.
  - Point estimates across ranges: 0.9509 (range 0, 200k), 0.9656 (range 0,
    100k), 0.9604 (range 1M, 200k), 0.9512 (range 5M, 100k), 0.9576 (range 5M,
    200k) — centered ≈0.955–0.96, **straddling the 96.0% lower edge**. The §3.3
    profile is robustly met across all ranges; the RTP band is **not robustly**
    met.

**QA verdict (independent): PASS WITH FINDINGS**
(`qa/reports/block_cave_stage3_candidate2_seed_search_review.md`). QA reproduced
the OOS result, confirmed methodology sound, §3.3 profile robust, off-limits
files unchanged, tests 16/16 + 13/13 + `pip check`. Findings: **F1 (MEDIUM)** §11
OOS table lists `P(≥100×)=0.0` for the four non-reference seeds but their JSONs
report 2.5e-05/2.5e-05/5.0e-06/3.0e-05; **F2 (MEDIUM)** the fresh-range
reproduction gives RTP **0.9576 (below band)**, so the "satisfies the RTP band"
conclusion is a **range-dependent point estimate, not a robust confirmation**;
**F3/F4/F5 (LOW)** §12 cites stale tuning-range tail metrics (184.6× vs OOS
210.46×), §8 still shows a stale "below band" verdict, and full-return 18.5% is
labelled "(≈15%)/Met" though above the 12–16% band.

### Open conflicts / product decisions (must be resolved before frontend work)

These are real target conflicts, not passing results. They need a product
decision:

1. **Visible hit ≈ 69.9% vs the ≈45% target.** The common-symbol weight (≈65%)
   makes sub-1.0× cluster wins so frequent that the visible hit is far above
   target. Lowering it trades off the "frequent visible small wins" product
   goal. **Open.**
2. **Full return ≈ 29.2% vs the 12–16% target.** The tumble cascade frequently
   sums several small wins past 1.0×. Same trade-off as (1). **Open.**
3. **Feature entry ≈ 0.7% vs the ≈1.0% target.** The strip-based 3+ pickaxe rate
   is below the binomial approximation (≈1.01%). Raising `pickaxe` weight would
   increase entry but change the base strip arrangement. **Open.**
4. **Ore-vein upgrade RTP contribution ≈ −1.24pp** (counterintuitive — the
   conversion to `diamond` occasionally breaks a frequent common-symbol cluster).
   It does not push RTP out of band and is a small effect. Retained for the
   mechanic, not for a measurable RTP boost. **Note.**
5. **`wincap` / `oreVeinUpgrade` event contract** is validated by
   `test_wincap_ore_vein_upgrade`; the frontend still needs the `wincap` and
   `oreVeinUpgrade` `BookEvent` union members + handlers (Stages 5–6).
6. **Candidate 2 RTP vs the §3.3 hit/full targets (new).** Candidate 2 meets the
   §3.3 hit/full/feature/tail targets and a positive ore-vein, but its natural
   RTP is **not robustly in the 96.0–96.7% band**. A bounded base-seed search
   (paytable unchanged, band not relaxed) with out-of-sample validation found no
   seed that robustly satisfies BOTH; the reference seed 20261103 is the best fit
   but its RTP point estimate is range-dependent (0.9509 / 0.9512 / 0.9576 /
   0.9604 / 0.9656 across disjoint ranges), straddling the 96.0% lower edge with
   std ≈3.0. **Open — needs the product decision on which constraint is harder
   (relax the §3.3 hit/full targets to get in-band RTP, or accept the borderline
   RTP for the §3.3 profile), or a deeper structural change.**

**Limitations:** no production RTP claim is made; all figures are DEV
measurements on the unpublished prototype. The 95% CI for the §3.1 RTP at 500k
rounds is [0.9594, 0.9702], which slightly straddles the 96.0% lower edge, so
the point estimate is in band but the CI is not entirely within it. The forced
freegame samples are deliberately generated books (feature internal distribution
only), not a basis for round RTP or entry rate.

### Lapis Lazuli + ≥100× calibration (2026-11-18) — lapis neutral, tail boost INFEASIBLE

Following the user's direction (keep Candidate A as the base, add a distinct
Lapis Lazuli ore block replacing Silver, then bounded ≥100× calibration), the
math agent produced `math/games/block_cave/candidate_lapis_config.py` and
`math/games/block_cave/LAPIS_REPORT.md`.

- **Lapis rename is mathematically neutral.** `candidate_lapis_config.py`
  replaces `silver` with `lapis` (identical counts, paytable values, and
  position-by-position strip arrangement). It is self-contained (its own
  `build_lapis_strip`/`build_lapis_pay_group`), so `game_config.py` is
  untouched. Baseline SHAs byte-identical (`7d04c138…2451` / `f7f48c53…9754`);
  Candidate A/B unchanged. Lapis SHAs `00af3ba5…8181` / `bc15b4fb…4c47`.
- **≥100× calibration is INFEASIBLE within the levers explored.** Every
  premium-count boost (diamond/ingot) that grows the tail raises natural base
  RTP ~1.7–2.0 pp against a band only 0.7 pp wide. The mildest boost
  (`d10_i10`) put the entire 95% CI above the 0.967 edge (≈0.974–0.989) yet
  still produced **zero** ≥100× events in 200k rounds (max 68–80×). No in-band
  tail boost exists; no `candidate_lapis_tail_config.py` was created.
- **QA verdict (independent): PASS WITH FINDINGS**
  (`qa/reports/block_cave_stage3_lapis_review.md`). QA re-derived the lapis
  SHAs, confirmed rename-neutrality position-by-position, confirmed off-limits
  files unchanged (mtimes), verified the Wilson CI (`proportion_ci(0,200000)`
  upper = 1.92076e-5), reproduced the screen/validation tables exactly, and ran
  the suites. On a fresh disjoint range (30M): `lapis_base` RTP 0.9619 (CI
  [0.9550, 0.9688], straddles both edges), hit 0.699, ore-vein Δ +0.0985 pp;
  `d10_i10` RTP 0.9823 (CI [0.9750, 0.9896], above band); zero ≥100× events in
  200k (max 49×/68×). **Infeasibility independently supported** (boost cost
  +2.04 pp at 30M / +1.73 pp at 20M vs a 0.7 pp band).
- **Findings (non-blocking):** F1 (LOW) §2.5 forced max/feature RTP are
  single-range figures — label "measured at 20M"; F2 (LOW) soften "infeasible"
  → "infeasible within the levers explored" (premium-count boosts on the fixed
  §3.1 paytable + fixed `create-cluster` rule); F3 (INFO) Wilson uses z=1.96
  (conservative); F4 (INFO) §2.3 vs §2.4 feature RTP differ by sample size.
- **Open product decision:** the ≥100× tail target (≈1e-4) is not achievable
  while holding the 96.0–96.7% band and the fixed §3.1 paytable / `create-cluster`
  rule. Options: keep `lapis_base` (neutral, in-band, tail stays ~1e-5), or
  relax a constraint (band / paytable / ore-vein rule / hit) to pursue the
  tail. **Not locked yet.**

**Tests:** `test_block_cave.py` 19/19, `pip check` clean, upstream
`win_calculations` 13/13.

### New direction: persistent-ore-vein bonus variant (2026-11-18) — math NOT locked

The user does NOT want to finalise the Block Cave math yet. New directive:
develop and test a **bonus variant** on the current Lapis Lazuli config, with a
**≥100× target of ≈1 round win per 10,000 paid rounds** (acceptable
≈1:5,000–1:20,000).

**≥100× definition — CONFIRMED.** A ≥100× hit is the total win of a paid base
round including all free spins that round triggers. Verified in
`math/src/wins/win_manager.py` (`basegame_wins`/`freegame_wins` accumulated per
gametype, then `evaluate_finalwin`/`update_final_win` does the sum-then-cap) and
in `calibrate.py`'s `check_book`
(`payoutMultiplier = min(baseGameWins+freeGameWins, 1000) × 100`). So
`payoutMultiplier/100` already captures the triggered free-spin series. Future
reporting must also **split whether ≥100× came from the base game alone or with
free spins**.

**Mechanic to test (Variant P):** ore veins persist within the triggered
free-spin series and **accumulate across free spins**, keeping their wild +
neighbour-upgrade function. Behaviour during cascades, new ore veins and
re-triggers must be precisely defined; the whole series must be one reproducible
game book (no state transfer to later paid rounds); the 1,000× cap must be
respected; the Stake engine + event contract for replay/frontend must be
checked. No bonus multiplier in Variant P. **Variant M** (bounded stacking bonus
multiplier) is a separately-measurable fallback only if P cannot reach ≥100×.

**Calibration:** permitted to merge pay tiers 5–7 and 8–10 and reduce small
cluster wins (a winning 5–7 cluster ≥0.10×). Frequent small hits desired; a
somewhat lower visible hit is acceptable; free spins stay short & relatively
frequent. RTP platform boundary 96.0–96.7% (the general 95–97% product wish
does not replace the platform boundary). No forced results, no seed cherry-picking.

**Measurement:** report for both variants natural round results with multiple
independent samples + CIs: RTP, ≥100× frequency (base-only vs with free spins),
bonus entry, bonus win distribution, visible hit, full return, free-spin
duration, round win max — compared against the previous Lapis config.

**Gate:** an independent QA agent (not the implementer) must check math, event
replay and conclusions. Existing candidates stay unchanged. Present results + a
recommendation to the user before the final config is written or the frontend is
implemented.

### Variant P: precise natural RTP measurement (2026-11-18) — math NOT locked

Ran a pre-determined-precision large sample on the actual Variant P config
(`candidate_lapis_persistent_config.build_config()`, cap=7, common-scale=1.10,
ore-vein upgrade on). Precision target 95% CI half-width ≤0.50 pp; pilot std
3.1771 → n_required 1,551,096. **Sample used 1,800,000 natural rounds**, pooled
as ONE sample across six fresh disjoint ranges (110M–160M × 300k; these ranges
are now consumed). Measured half-width 0.45 pp → target met.

- **Pooled natural RTP 0.94624**, 95% CI [0.94175, 0.95074]; per-range
  0.9428–0.9495 (robust, not a seed-range artifact). base RTP 0.76009, feature
  RTP 0.18615, visible hit 0.69863, full return 0.24834, feature entry 0.00719,
  feature mean 25.89 / max 337.07, round max 337.07, 0 wincap binds, 0 violations.
- **≥100× tail 168 / 1,800,000 = 1:10,714**, Wilson 95% [8.02e-5, 1.09e-4]
  (≈1:12,461–1:9,212), entirely inside the acceptable 1:5,000–1:20,000 band;
  split base-only 0 / with-free-spins 168. No ≥500× / ≥1000×.
- **Key result:** the config **under-returns** — natural RTP 0.9462 is BELOW the
  96.0–96.7% band, the opposite of the earlier noisy 20k-block estimates
  (author 0.9651 / QA 0.9757 were n=20k noise). No calibration-down was performed
  (condition not met). See `BONUS_VARIANT_RTP_REPORT.md` and artifacts
  `vp_pilot_100m.json`, `vp_current_pooled.json`, `vp_verify_40m.json`.

### Variant P: books → base-LUT → optimized-LUT path traced; preliminary weighted mode (2026-11-18)

**User directive:** the published mode RTP is NOT the natural/measured RTP — it
arises from the **final book weights** in the optimized lookup table the Rust
optimizer produces. So do not discard Variant P for its natural RTP (0.9462),
and do not blindly re-tune the raw config up to a 96.3% natural RTP. Trace the
books → base-LUT → optimized-LUT path and build a **preliminary weighted mode
around 96.3%**, computing metrics from EXACTLY the final weights; only if a
sensible weighting cannot preserve the play profiles should a bounded payout
increase be tested. Preserve Variant P and prior candidates byte-identical.

**Path verified (orchestrator + explore agent):**
- Base LUT `library/lookup_tables/lookUpTable_<mode>.csv` = one row per book
  `bookId,1,payoutMultiplier`; `payoutMultiplier = round(min(base+free,1000)*100)`;
  the optimizer reads `win = payoutMultiplier/100` (bet units). Every weight is 1,
  so base-LUT RTP = Σ(win)/N = the natural RTP.
- Optimized LUT `library/publish_files/lookUpTable_<mode>_0.csv` =
  `bookId, weight, rounded_win`; **published RTP = Σ(weight·win)/Σ(weight)**
  (`optimization_program/src/exes.rs:172-174`, `main.rs:338-343`).
- The Rust optimizer re-weights **by win value/band** and distributes weight
  uniformly within a band (`main.rs:312-328`); band edges are exactly
  `[0,0.1) [0.1,1) [1,2) [2,3) [3,5) [5,10) [10,20) [20,50) [50,100) [100,200) [200,500) [500,1000) [1000,2000) [2000,3000) [3000,5001)`.

**Preliminary weighted mode built (math agent), `BONUS_VARIANT_WEIGHTED_MODE_REPORT.md`:**
- Sample: 1,800,000 natural rounds on six fresh disjoint ranges 170M–220M × 300k
  (all ≥170M, never used). Throughput 2,341 r/s; runtime 768.9 s; 0 consistency
  violations.
- Natural (base-LUT) RTP 0.94571 (base 0.76158, feature 0.18413), ≥100× 182/1.8M
  = 1:9,890, base-only 1 / with-fs 181. Round win max 428.36.
- **Weighting:** minimum-KL (exponential tilt `q_b ∝ p_b·exp(λ·m_b)`, λ =
  0.00179466 by bisection), then uniform within band (`w_i = q_band/count_band`).
  Max band boost **1.59×** on [200,500); KL 1.58e-5; only [0,0.1) & [0.1,1)
  trimmed (≤0.17%). Bands ≥[500,1000) are empty on this sample.
- **Published RTP 0.96300** (target 0.963, error +2e-16; integer-encoded
  −8.8e-11). Weighted hit 0.69900, full return 0.24979, free-spin entry 0.007417
  (0.742%), feature payout mean 26.77 / median 21.15, duration mean 8.66 / max 32.
- **Weighted ≥100× 1.286e-4 (1:7,776)**, Wilson 95% [1.130e-4, 1.462e-4]
  (≈1:8,848–1:6,839), entirely inside 1:5,000–1:20,000; base-only share 0.69%.
  No ≥500× / ≥1000×; cap never engages.
- **Verdict: SENSIBLE** — a min-KL weighting hits 96.3% published RTP, keeps ≥100×
  in-band, and preserves hit / entry / full-return (distortion tiny). **No
  paytable / small-payout bump needed** *for the re-weighting target*.

**Independent QA (not the implementer): ACCEPT WITH FINDINGS**
(`qa/reports/block_cave_variant_p_weighted_mode_qa.md`). Re-derived all numbers
from raw artifacts (not the implementer's helpers); 63/63 checks passed, no FAILs.
Min-KL solve re-implemented from scratch; independent fresh 5,000-book run on a
disjoint seed (230M) corroborated `check_book`. Findings are NOTE-level:
1. "No paytable bump needed" is true **only for optimizer re-weighting**; the
   underlying game still returns **0.9457** until the weighting is actually applied.
2. Wilson input nitpick (displayed `k=231, n=1799940` vs `k_eff=231.409,
   n_eff=1799940.79`) — cosmetic; interval correct.
3. Config docstring claims RTP in 96.0–96.7% but natural measures 0.9457
   (~1.4 pp short) — reconcile the config's own claim.
4. No ≥500× tail in 1.8M spins; the weighting cannot create one — the
   persistent-vein "tail lift" intent is not realized in-band.
5. The Kish effective-sample-size Wilson interval is a legitimate design-effect
   approximation for the natural-sample sampling variability, but is **not** a
   sampling CI for a fixed published distribution.
6. Repo is not a git repo, so "untouched" beyond listed SHAs/mtimes cannot be
   byte-verified against a baseline.

**Feasibility of the real Rust optimizer for Block Cave (explore agent): NOT
currently wireable; feasible with a dedicated wiring + math-design task.** The
engine is SDK-compatible and the production `GameState` accumulates books via
`create_books` (only the measurement-only `CalibrateState` overrides
`imprint_wins`). Missing pieces: (1) no `game_optimization.py`/`OptimizationSetup`
→ `opt_params` unset → empty `math_config.json` → Rust panics (`betmode index
not found`); (2) `run.py` is a prototype, not the `create_books`/`generate_configs`/
`OptimizationExecution` flow; (3) `library/` is empty (needs `force_record_*`,
`math_config.json`, `lookUpTable_*`); (4) Rust binary not built (cargo 1.100.0
available; `cargo run --release` would build it). **Crux blocker:** the
reference games define a `wincap` fence, and the Rust binary panics for a
win-type fence whose `avg_win` (= Block Cave's `get_wincap()` = 1000.0) is not in
the base LUT — Block Cave cannot naturally reach 1000×, and the engine never
consumes `force_wincap`. Paths: (i) omit the `wincap` fence and redistribute RTP
across `basegame`/`freegame`/`0`, or (ii) add a `force_wincap` mechanism + a
`wincap` distribution (larger, sequenced change). Until then, the weighted mode
above is a **model of the optimizer's RTP targeting**, not its actual output.

**Open issues / not locked:**
- Not a production claim; all DEV. Natural RTP (0.9457) is below the 96.0–96.7%
  band; the weighting lifts the *published* RTP to 0.963 but the underlying game
  still under-returns.
- ≥100× (1:7,776 weighted) and ≥500× are point estimates on one 1.8M sample, not
  tail certifications; rare & seed-sensitive.
- The min-KL weights are not the Rust optimizer's output (extra constraints:
  win-range fences, `distribution_bias`, `score_type`). Run the real optimizer
  after wiring before treating these weights as authoritative.
- No frontend/event-contract change (a lookup-table weight change only).
- No math lock. `BONUS_VARIANT_REPORT.md`, `BONUS_VARIANT_RTP_REPORT.md` and all
  prior candidates unchanged.

## Art templates v2 — 2026-11-18

- `art/templates/` now contains original pixel-art SVG sources and 512×512
  transparent PNG exports for the 6×5 game's symbols. `silver_ore` was replaced
  with `lapis_ore` (math ID `lapis`); the dark alloy visual is now a block while
  retaining the `fantasy_alloy_ingot` asset ID. Grass/earth, log, ore textures,
  pickaxe scatter, cave tunnel and lava were revised. Three ore-vein WILD
  concepts are available; the cyan-cross version is the current default.
- The background exports at 1920×1080. `preview-mini.png` and
  `preview-desktop.png` show illustrative 400×225 and 1200×675 layouts, not
  actual frontend playback. The existing explorer SVG was retained.
- Independent QA: `qa/reports/block_cave_art_v2_review.md` — **PASS with
  nonblocking findings**. All 15 SVGs parsed, all 15 PNGs passed size/alpha
  checks, and isolated regeneration produced byte-identical outputs. WILD and
  SCATTER labels are not reliably readable at 400×225; the future frontend
  must explain these symbols through the paytable and accessible text. The
  `lapis` → `lapis_ore` map needs an integration test. No Pixi or platform
  approval claim is made.

## Art reference revision — 2026-11-18

- The pickaxe scatter now has an original horizontal turquoise pixel head and
  angled brown handle, based on the user's visual direction; its magenta field
  and SCATTER label remain. The new separate 3D cave plate
  `art/templates/cave_background_3d.png` (1672×941) follows the warm dripstone
  direction of reference 5, with peripheral torches, rock and lava. The art
  preview uses it behind the 6×5 board at 400×225 and 1200×675. The previous
  pixel-art background remains a fallback.
- Independent QA: `qa/reports/block_cave_art_v3_review.md` — **PASS with
  nonblocking presentation findings**. Targeted pickaxe regeneration and PNG
  re-export were checked in isolated copies; the new raster asset and fallback
  remained untouched. Both previews were pixel-identical on regeneration and
  showed no clipping. The small SCATTER label needs explanation in the eventual
  UI, and the 3D background versus pixel-symbol style needs a real-game review.
  Pixi playback was not tested.

## Character art revision — 2026-11-18

- `art/templates/cave_explorer_3d.png` is a new 1024×1536 transparent raster
  prototype. The user's reference guided its dynamic three-quarter pose,
  raised pickaxe and block-built anatomy; aubergine/ochre workwear, goggles
  and cyan tool accents distinguish this original miner. The mini and desktop
  previews now use it. The prior editable `cave_explorer.svg` and PNG remain
  available as fallbacks.
- Independent QA: `qa/reports/block_cave_art_v4_review.md` — **PASS after one
  visual revision**. The first draft's rounded anatomy was rejected; the
  revised cubic head and limbs resolved that finding. The isolated exporter
  passed, all 78 preview images loaded, both 400×225 and 1200×675 previews
  showed no board overlap or clipping, and the 3D raster and fallback files
  were unchanged by export. The character remains a prototype pending visual
  acceptance and actual Pixi integration; the 3D figure and pixel symbols
  have different rendering styles.

## Variant P — complete local DEV math package (2026-11-18) — DEV only, math NOT locked

Produced a complete local DEV math package for Variant P (Block Cave Lapis +
persistent ore veins) under `math/games/block_cave/library/`: compressed JSONL
books, weighted base/optimized lookup tables and `index.json`. No upload, no
math lock. DEV-only — this is NOT a production RTP claim or release.

### Configuration and sample
- Config = `candidate_lapis_persistent_config.build_config()` (cap=7,
  common-scale=1.10, ore-vein persist ON); strips = Lapis SHAs
  `00af3ba5…8181` / `bc15b4fb…4c47`.
- 1,800,000 books generated on six fresh disjoint ranges 170M–220M × 300k each
  (all ≥170M, never used). Generation: 942 r/s, 1961.3 s total, 0 consistency
  violations. RNG seed = `start_seed + i + 1`; `book['id']` overridden to the
  global 0-based index.
- Weighting = minimum-KL exponential tilt (λ = 0.0017946579216578254 by
  bisection, target published RTP 0.963), then uniform within band;
  `weight_int = round(w·2^50)`. This is a MODEL of the Rust optimizer's RTP
  targeting, not its output (the real optimizer is not wireable for Block Cave:
  no `game_optimization.py`, empty library, `wincap` fence `avg_win` absent
  from the base LUT). See the open issues below.

### Package contents and sizes
- `books/books_base.jsonl` 4,715,025,550 bytes (2,619 B/book).
- `publish_files/books_base.jsonl.zst` 420,175,702 bytes (233 B/book).
- `publish_files/lookUpTable_base_0.csv` 36,607,144 bytes.
- `lookup_tables/lookUpTable_base.csv` 22,207,144 bytes.
- `publish_files/index.json` = `{"modes":[{"name":"base","cost":1.0,
  "events":"books_base.jsonl.zst","weights":"lookUpTable_base_0.csv"}]}`.
- Platform compressed-file size limit: **not findable locally or online**;
  reported honestly as UNVERIFIED (≈0.42 GB observed).

### Orchestrator verification (all PASS)
- Byte-identity of the generated CSVs to the references:
  `lookUpTable_base.csv` SHA256 `2662d122…e282b` == `vp_weighted_base_lut.csv`;
  `lookUpTable_base_0.csv` SHA256 `ed086fa5…c27094c` ==
  `vp_weighted_optimized_lut.csv`.
- zstd round-trip: decompressed 4,715,025,550 bytes == jsonl; streaming sha256
  `7ba38e97…6ef2f`.
- Full streaming cross-check (`vp_full_crosscheck.py`): 1,800,000 rows, 0 CSV
  `payoutMultiplier` mismatches, 0 id mismatches, 0 `check_book` violations →
  PASS.
- index.json shape OK; book id == row index; `payoutMultiplier` ==
  `round(min(base+free,1000)*100)`.

### Metrics
- Natural (base-LUT, all weights=1): RTP 0.9457134111 (base 0.7615848, feature
  0.1841286), visible hit 0.6984872, full return 0.2488556, feature entry
  0.0070867 (12,756), feature duration mean 8.617 / max 32, round max 428.36,
  ≥100× 182/1.8M (base-only 1 / with free-spins 181). No ≥500× / ≥1000×.
- Weighted published: RTP 0.9630000000 (integer cross-check 0.9629999999,
  error −8.8e-11), visible hit 0.6990031, full return 0.2497911, feature entry
  0.0074175, ≥100× 1.2856e-4 (1:7,776; base-only 8.82e-7 / with-fs 1.2768e-4),
  λ = 0.00179466, KL = 1.58009e-5, max band boost 1.587×.
- ≥100× definition: total win of a paid base round including all free spins it
  triggers (`payoutMultiplier/100 >= 100`).

### Independent QA (not the implementer): PASS WITH FINDINGS
`qa/reports/block_cave_variant_p_dev_package_qa.md`. All 8 checks pass; no
implementation or library file modified; 44/44 metrics recomputed; Min-KL
re-derived exactly (λ matches, KL 1.58009e-5, max boost 1.587×, 0 LUT
`weight_int` mismatch); `win_calculations` 13/13, `test_block_cave.py` 25/25;
200 books regenerate byte-equal; off-limits SHAs 8/8 match. Findings are
claim-reconciliation / notes, NOT package defects:
- **F1 (MEDIUM, claim reconciliation):** the config docstring claims natural RTP
  in the 96.0–96.7% band, but natural measures 0.9457 (~1.4 pp below). The
  weighting lifts only the *published* RTP to 0.963; the underlying game still
  under-returns.
- **F2 (NOTE):** the min-KL weights are a model of the Rust optimizer's targeting,
  not its actual output (not wireable here).
- **F3 (NOTE):** the repo is not a git repo, so "untouched" beyond listed
  SHAs/mtimes cannot be byte-verified against a baseline.
- **F4 (NOTE):** no ≥500×/≥1000× tail in 1.8M spins (round max 428.36); the
  weighting cannot create one.
- **F5/F6 (INFO):** weighted ≥100× = 1.286e-4 is a point estimate, not a tail
  certification; no frontend change and visual QA not applicable.

### Could not be verified
- Real Rust optimizer output; git-baseline "untouched"; exact per-value
  `common-scale=1.10` multiplier semantics; whether a ≥500× tail exists at
  larger sample sizes; the platform compressed-file size limit.

### Open issues / not locked
- DEV only; not a production RTP claim or release.
- Natural RTP 0.9457 is below the 96.0–96.7% band; the weighting lifts only the
  published RTP to 0.963. Reconcile the config's band claim (F1).
- ≥100× (1:7,776 weighted) and ≥500× are point estimates on one 1.8M sample.
- The min-KL weights are not the Rust optimizer's output; run the real optimizer
  after wiring before treating them as authoritative.
- No frontend / event-contract change (a lookup-table weight change only).
- No math lock. Prior candidates and `BONUS_VARIANT_*` reports unchanged.

## 3D symbol art revision — 2026-11-18

- The eleven current board symbols now have separate 1254×1254 transparent
  `art/templates/*_3d.png` sources. Earth, stone and timber use distinct cubic
  materials; five ores embed differently shaped minerals in a shared stone
  cube; the rare alloy is a dark block; ore vein is a cyan/violet junction; and
  the pickaxe is framed in magenta with SCATTER text. The preview uses these
  assets with the existing 3D cave and explorer. The SVG/PNG pixel assets remain
  fallbacks and the art IDs and math contract are unchanged.
- Independent QA: `qa/reports/block_cave_art_v5_review.md` — **PASS as prototype
  art**. All eleven rasters have real alpha; isolated export regenerated three
  pixel-identical previews without changing source/fallback assets; Chrome
  loaded all 78 images without console, page, network or HTTP errors. Both
  400×225 and 1200×675 previews show the full board without overlap. At mini
  size the SCATTER word is too small to read, so the final UI needs paytable
  and accessible explanations. The eleven sources total about 16.5 MiB;
  frontend atlas/downsampling and real Pixi performance remain untested.
