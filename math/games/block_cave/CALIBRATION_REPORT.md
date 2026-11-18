# Block Cave — Stage 3 Math Calibration Report

**Status:** DEV measurement only. **This is NOT a production certification and
makes no RTP claim for a published game.** All figures below are measured on
the current (unpublished) Block Cave prototype with the deterministic reel
strips in `MATH_DESIGN.md` §4.1/§4.2. Owner: Math agent.

## 1. Objective

Calibrate the Block Cave paytable so the **natural base-game RTP** falls inside
the Engine's **96.0–96.7%** band near the **96.3%** target, add a
`wincap` + `oreVeinUpgrade` QA regression test, and document the calibration.

## 2. Method

- **Natural rounds only** (`criteria="basegame"`, `betmode="base"`, no
  forcing) are the **only** basis for round RTP, RTP standard deviation,
  visible hit, full return, dry-streak behaviour and the free-spin **entry
  rate**.
- **Forced freegame rounds** (`criteria="freegame"`,
  `force_freegame=True`) are generated **only** to measure the free-spin
  feature's *internal* distribution (duration, payout, tails) with many
  samples. They are explicitly labelled and are **not** used for round RTP or
  entry rate.
- **Deterministic:** reel strips are built from seeds **20261117** (base) and
  **20261118** (free), SHA-256
  `7d04c138…b2451` / `f7f48c53…d89754`. Same seed range ⇒ identical output.
- Harness: `math/games/block_cave/calibrate.py` (`CalibrateState`,
  `make_config`, `Measurer`), plus a temp paytable-scale sweep helper
  (`calib_sweep.py`) used to probe scale factors. The sweep helper hand-builds
  the `MATH_DESIGN.md` §3.1 paytable and overrides `gc.build_pay_group`; it is
  independent of the checked-in `game_config.py`.
- Measurement outputs live under `.runtime/block_cave/`.

## 3. Key finding — the previous paytable scale-up was wrong

- The prior Stage-3 revision (**C2**) multiplied the §3.1 paytable by a uniform
  factor `F = 1.8382663803148458`, derived from `0.963 / measured_pre_rtp`,
  where `measured_pre_rtp = 0.524` (`calib_pre`).
- **`calib_pre` (0.524) is unreliable/erroneous.** A 0.524 RTP implies a ~48%
  house edge, which is implausible for a product targeting 96.3%. It was
  measured on a different / lower paytable, so it is **not** a valid basis for
  a scale factor.
- **Measuring the actual game code** with the ×F paytable baked into
  `game_config.py` gives a natural base-game RTP of **≈ 1.76** (`calib_confirm`,
  30k natural) — far **above** the band (over-paying).
- **Measuring the exact `MATH_DESIGN.md` §3.1 paytable** (scale 1.0, no
  scaling) gives a natural base-game RTP of **≈ 0.964** — already **inside** the
  96.0–96.7% band, statistically indistinguishable from the 96.3% target.
- **Conclusion:** the calibrated paytable is the §3.1 table itself. The ×F
  scale-up must be **reverted**; no paytable scale factor is applied.

## 4. Pre / Post calibration metrics

### 4.1 Pre-calibration (×F baked paytable)

Measured on the previous `game_config.py` (all §3.1 values × `F`, rounded to
2 dp). Sample: **30,000 natural base rounds** (`calib_confirm.json`).

| Metric | Value |
| --- | --- |
| Natural base-game RTP | **1.7577** (CI [1.6845, 1.8309]) |
| base-game RTP contribution | 1.6538 |
| free-spin RTP contribution | 0.1039 |
| Visible hit `P(payout>0)` | 0.6954 |
| Full return `P(payout>=1.0×)` | 0.4474 |
| Feature entry rate | 0.00583 (0.583%) |
| Feature duration (mean) | 8.59 |
| Feature payout (mean / median) | 17.81 / 14.32 |
| Round payout p50 / p90 / max | 0.85 / 4.52 / 1000.0 |
| `wincap` bind count | 1 |

### 4.2 Post-calibration (§3.1 paytable, scale 1.0)

Measured on the corrected `game_config.py` (exact §3.1 values). Sample:
**500,000 natural base rounds** + 20,000 forced freegame rounds
(`calib_md_post.json`).

| Metric | Value |
| --- | --- |
| Natural base-game RTP | **0.9648** (CI [0.9594, 0.9702]) |
| base-game RTP contribution | 0.8945 |
| free-spin RTP contribution | 0.0703 |
| Visible hit `P(payout>0)` | 0.6985 (CI [0.6972, 0.6998]) |
| Full return `P(payout>=1.0×)` | 0.2910 (CI [0.2898, 0.2923]) |
| Feature entry rate | 0.00704 (0.704%), 3521/500000 |
| Feature duration (mean / median / max) | 8.73 / 8.0 / 36 |
| Feature payout (mean / median / max) | 9.98 / 7.86 / 105.82 |
| Round payout p50 / p90 / p99 / max | 0.46 / 2.5 / 6.99 / 544.43 |
| `P(>=100×)` / `P(>=500×)` / `P(>=1000×)` | 6e-6 / 2e-6 / 0.0 |
| `wincap` bind count | 0 |
| Consistency violations | 0 |

## 5. Change log

- **`math/games/block_cave/game_config.py`** — reverted `_COMMON_PAYS`,
  `_PREMIUM_PAYS` and `_INGOT_PAYS` from the ×F baked values to the
  `MATH_DESIGN.md` §3.1 values (81 source entries, 234 expanded
  `convert_range_table` keys). The reel strips, symbol weights/counts,
  `wincap=1000.0`, `rtp` design field and seeds (20261117 / 20261118) are
  **unchanged** (base strip SHA-256 `7d04c138…b2451`, free strip
  `f7f48c53…d89754`).
- **`math/games/block_cave/MATH_DESIGN.md`** — added revision **C3** (paytable
  reverted to §3.1, strips unchanged); corrected the §3.3 measured-outcome
  rationale (the full-return overshoot comes from the tumble cascade summing
  many small wins, **not** from a paytable scale-up); reconciled the §3.1 note
  to state these are the calibrated values.
- **`math/games/block_cave/test_block_cave.py`** — already contains
  `test_wincap_ore_vein_upgrade` (asserts event order
  `updateTumbleWin → wincap → oreVeinUpgrade`, `wincap` amount `100000`,
  expected `veinPositions`/`upgrades`, and that the cascade **stops** after
  `wincap_triggered`). No change required; **11/11 pass**.
- No changes to `frontend/`, `art/`, `docs/`, `qa/`, `scripts/` or other games.

## 6. Targets met / not met

| Design target | Measured (§3.1) | Met? |
| --- | --- | --- |
| Natural base-game RTP in 96.0–96.7% band | 0.9648 | ✅ **Met** (point estimate inside band; see §9 CI caveat) |
| Visible hit ≈ 45% | 0.6985 | ❌ **Not met** (≈69.9%) |
| Full return ≈ 12–16% | 0.2910 | ❌ **Not met** (≈29.1%) |
| Feature entry ≈ 1.0% | 0.00704 | ❌ **Not met** (≈0.704%) |
| Feature average payout ≈ 8–12× | 9.98 | ✅ Met |
| Feature median payout ≈ 5–7× | 7.86 | ⚠️ Slightly above (≈7.9×) |
| Feature duration short (8–16, cap 60) | mean 8.73, max 36 | ✅ Met |
| 1,000× cap as safety ceiling | max 544.43, `wincap` binds 0 | ✅ Met (cap never binds in base game) |
| No top pay raised to reach 1,000× | true | ✅ Met |

## 7. Conflicts / open decisions

1. **Visible hit ≈ 69.9% vs the ≈45% target.** The common-symbol weight
   (≈65%) makes sub-1.0× cluster wins so frequent that the visible hit is far
   above target. Lowering the common weight would trade off the
   "frequent visible small wins" product goal. **Open** for product/orchestrator.
2. **Full return ≈ 29.1% vs the 12–16% target.** The tumble cascade frequently
   sums several small wins past 1.0×. Same trade-off as (1).
3. **Feature entry ≈ 0.704% vs the ≈1.0% target.** The strip-based 3+ pickaxe
   rate is below the binomial approximation (≈1.01%). Raising the `pickaxe`
   weight would increase entry but also change the base strip arrangement.
4. **Ore-vein upgrade RTP contribution.** A seed-matched comparison on the §3.1
   paytable (`calib_ore_enabled.json` vs `calib_ore_disabled.json`, 150k each)
   shows the upgrade contributes **≈ −1.24%** of RTP (enabled 0.9640 vs
   disabled 0.9764), i.e. enabling the upgrade slightly **lowers** base-game
   RTP on this strip. This is counterintuitive (the upgrade converts a regular
   block to a higher-paying `diamond`) and is likely because the conversion
   occasionally breaks a frequent common-symbol cluster. It does **not** push
   RTP out of band and is a small effect (≈2.3 SE at 150k). **Open:** confirm
   whether the intended "vein reveals rich ore" value is being realised; the
   upgrade is retained for the mechanic, not for a measurable RTP boost.
5. **`wincap` / `oreVeinUpgrade` event contract.** Validated by
   `test_wincap_ore_vein_upgrade` (order `updateTumbleWin → wincap →
   oreVeinUpgrade`). The frontend still needs a `wincap` union member + handler
   branch and the `oreVeinUpgrade` handler (per `MATH_DESIGN.md` §8), which is
   outside the math scope.

## 8. Verification

- `test_block_cave.py` — **11/11 pass** (incl. `test_wincap_ore_vein_upgrade`).
- `pip check` — **no broken requirements**.
- Upstream `math/tests/win_calculations` — **13/13 pass**.
- **Determinism:** two identical 5,000-round runs produced identical output;
  single-spin wins match the paytable exactly (e.g. `copper` 5-cluster = 0.29×).
- Reverted `game_config.py` paytable verified equal to §3.1 (81 source / 234
  expanded keys, 0 mismatches); `make_config(1.0)` reproduces §3.1.
- **Official post run** (`calibrate.py --natural 50000 --freegame 5000` on the
  reverted `game_config.py`, `calib_post.json`): RTP **0.9590** (CI
  [0.9332, 0.9847], consistent with the 500k 0.9648), base 0.8970, feature
  0.0620, visible hit 0.6982, full return 0.2883, entry 0.0063, max 544.43,
  `wincap` binds 0, consistency violations 0.

## 9. Limitations

- **Not a production certification.** No published RTP claim.
- RTP standard deviation for the §3.1 paytable is ≈ 1.94; at 500,000 rounds the
  standard error is ≈ 0.00274 (95% CI ≈ ±0.0054), i.e. the CI is
  **[0.9594, 0.9702]**. The point estimate 0.9648 is inside the band, but the CI
  slightly straddles the 96.0% lower edge (lower bound 0.9594 < 0.960), so a 95%
  confidence interval is not entirely within the band. Report the point
  estimate together with the CI.
- Forced freegame samples are generated books, used only for the feature
  internal distribution; they are **not** a basis for round RTP or entry rate.
- The ore-vein contribution in §7.4 is a seed-matched 150k comparison and is a
  measured observation, not a definitive effect.
