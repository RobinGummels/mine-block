# Block Cave — Variant P natural RTP: precision measurement

**Status:** DEV measurement only. **This is NOT a production certification and
makes no RTP claim for a published game.** All figures are measured on the
current (unpublished) Block Cave prototype. Owner: Math agent.

This report measures the **actual natural RTP** of the Variant P config
(`candidate_lapis_persistent_config.py`, cap = 7, common-scale = 1.10) to a
**pre-determined precision** (95% CI half-width ≤ 0.50 pp) and re-checks the
**≥100× natural round tail** against the acceptable band (1:5,000–1:20,000).
It supersedes the noisy, range-dependent point estimates in the prior report
(`BONUS_VARIANT_REPORT.md`), which were based on n = 20,000/range and whose
per-range RTP CI (±0.05–0.07) was far wider than the 0.7 pp band.

---

## 1. Config (what is measured)

`math/games/block_cave/candidate_lapis_persistent_config.py` — the cap = 7,
common-scale = 1.10 Variant P config, built with
`build_config()` (`ore_vein_persist_max = 7`, ore-vein upgrade **enabled**).
Identical to the config measured in `BONUS_VARIANT_REPORT.md` §1:

- **Strips** — byte-identical to the Lapis Lazuli strips. Base SHA
  `00af3ba5…258181`, free SHA `bc15b4fb…4db4c47`.
- **Paytable** — merged 5-tier `VARIANT_PAY_RANGES = [(5,7),(8,10),(11,14),(15,19),(20,30)]`,
  small-cluster (5–7) reduced, premium/ingot unscaled, common-scale ≈ 1.10.
  No bonus multiplier.
- **Ore-vein rule** — `create-cluster` → `diamond`.
- **Persistent gate** — `config.ore_vein_persist_freespins = True`,
  `config.ore_vein_persist_max = 7`.

**Verification.** The config self-check passes (`python
math/games/block_cave/candidate_lapis_persistent_config.py` prints the two strip
SHAs and "Variant P config reproducible"), `test_block_cave.py` is 25/25
(incl. `test_variant_p_config_reproducible` and the 5 persistent-vein mechanic
tests), `pip check` is clean, and upstream `math/tests/win_calculations` is
13/13. The config was confirmed byte-identical to the author's: a fresh 40M run
reproduces `final_40m_cs110.json` exactly (rtp = 0.9593, feat = 0.1994,
entry = 0.00755, P100x = 3/20000, feat_pay_mean = 26.412, max = 218.57).

---

## 2. Method — pre-determined precision

- **Precision target.** 95% CI half-width ≤ **0.50 pp** (0.005), z = 1.96.
- **Measured per-round std.** Pilot: **3.1771** (50,000 natural rounds @ seed
  100M; rtp = 0.95014, CI [0.9223, 0.9780], throughput = 2,726 r/s). The pooled
  large-sample std is **3.0754**.
- **Required sample size.** n_required = (1.96 × 3.1771 / 0.005)² =
  **1,551,096** rounds.
- **Sample used.** **1,800,000** natural rounds across **six fresh, disjoint**
  seed ranges (110M, 120M, 130M, 140M, 150M, 160M) × 300,000 each — all
  **previously unused**, so this is a single independent out-of-sample sample.
  All rounds are natural (`criteria=basegame`, no forcing), which is the only
  basis for round RTP, hit, full return, entry rate and the round ≥100× tail.
- **Aggregation.** All per-round payouts are **pooled across ranges into ONE
  independent sample** — no per-range "seed RTPs" are reported as separate
  results. The pooled 95% CI half-width is **0.00449 (0.45 pp)**, which meets
  the ≤ 0.50 pp target.
- **≥100× split.** The natural runs are replayed (deterministic) and each ≥100×
  round is inspected for its `baseGameWins` vs `freeGameWins` to report the
  base-only vs with-free-spins split.

Helper: `.runtime/block_cave/measure_rtp_precision.py` →
`.runtime/block_cave/vp_current_pooled.json` (BOM-free). Pilot helper:
`.runtime/block_cave/pilot_variant_rtp.py` →
`.runtime/block_cave/vp_pilot_100m.json`.

---

## 3. Result — pooled natural RTP (N = 1,800,000)

| metric | value |
|---|---|
| **Natural RTP** | **0.94624** |
| 95% CI | **[0.94175, 0.95074]** |
| CI half-width | **0.00449 (0.45 pp)** — meets ≤ 0.50 pp |
| per-round std | 3.07537 |
| base RTP | 0.76009 |
| feature RTP | 0.18615 |
| visible hit | 0.69863 |
| full return (≥1.0×) | 0.24834 |
| feature entry | 0.007189 (0.719%) [0.007066, 0.007313] |
| feature payout mean / med / p90 / p99 / max | 25.892 / 20.78 / 48.54 / 108.06 / 337.07 |
| feature duration mean / med / max | 8.587 / 8.0 / 32.0 |
| round win max | 337.07 |
| wincap bind rate | 0 |
| consistency violations | 0 |
| throughput | 2,716 r/s |

**The measured natural RTP is 0.9462**, comfortably **below** the 96.0–96.7%
engine band. The per-range estimates on the six fresh ranges are tightly
clustered (0.9428–0.9495), so the pooled 0.9462 is **robust** and is **not** a
seed-range artifact. (The earlier author pooled 0.9651 and QA fresh pooled
0.9757 were noisy small samples at n = 20k; the 1.8M sample is the authoritative
measurement.)

---

## 4. Result — ≥100× natural round tail

| metric | value |
|---|---|
| **≥100× natural** | **168 / 1,800,000** |
| point estimate | **9.333e-5 (≈ 1:10,714)** |
| Wilson 95% | **[8.0247e-5, 1.0855e-4]** (≈ 1:12,461 to 1:9,212) |
| ≥100× split — base-only | 0 |
| ≥100× split — with-free-spins | 168 |
| base-only share | 0.000 |
| ≥500× natural | 0 / 1,800,000 (Wilson upper 2.13e-6) |
| ≥1000× natural | 0 / 1,800,000 (Wilson upper 2.13e-6) |
| wincap bind | 0 |

**The ≥100× tail is 1:10,714**, at the centre of the acceptable band
(1:5,000–1:20,000), and the **Wilson 95% interval lies entirely inside** the
band (lower ≈ 1:12,461, upper ≈ 1:9,212) — so the tail target is robustly met.
**Every** one of the 168 hits is with-free-spins; **no base round reaches ≥100×
on its own** (base-only share = 0.000). The tail is a persistent-vein /
free-spin phenomenon, as designed. No ≥500× or ≥1000× round was observed, and
the 1,000× cap never engaged.

---

## 5. Calibration decision — **NO calibration performed**

The task's calibration condition was to perform a **bounded calibration-down**
only if the natural RTP were **confidently above 96.7%** (while keeping the
≥100× tail ≥ ~1:20,000).

The measured natural RTP is **0.9462** — **below** the entire 96.0–96.7% band,
and certainly **not** above 96.7%. Therefore the calibration-down condition is
**not met**, and **no calibration was performed**: the config was left exactly as
it is, and **no calibrated candidate config file was created**. No lever
(premium/high-tier paytable, common-scale, persistent-vein cap) was changed.
(Helper `.runtime/block_cave/measure_variant_param.py` was built for a bounded
calibration sweep but was **not used**, since no calibration was needed.)

**Consequence / caveat.** The measured RTP is **below** the engine band, i.e.
this config **under-returns** relative to the 96.0–96.7% band, rather than
over-returning. The tail target is met (1:10,714, Wilson inside band), but the
**RTP is not in the 96.0–96.7% band**. Because the RTP is below band (not above),
this is **not** a calibration-down scenario; it is a finding that the config
under-returns. See Limitations.

---

## 6. Reproducibility

- **Config self-check:** `python math/games/block_cave/candidate_lapis_persistent_config.py`
  (prints the two strip SHAs + "reproducible").
- **Tests:** `python math/games/block_cave/test_block_cave.py` (25/25). Also
  `python -m pytest math/tests/win_calculations -q` (13/13).
- **Pilot:** `.runtime/block_cave/pilot_variant_rtp.py` →
  `.runtime/block_cave/vp_pilot_100m.json` (std 3.1771, n_required 1,551,096).
- **Measurement:** `.runtime/block_cave/measure_rtp_precision.py
  candidate_lapis_persistent_config 300000 .runtime/block_cave/vp_current_pooled.json
  110000000 120000000 130000000 140000000 150000000 160000000`.
- **Outputs:** `vp_pilot_100m.json`, `vp_current_pooled.json`,
  `vp_verify_40m.json` — all UTF-8, **BOM-free**, LF.
- **Off-limits configs verified byte-identical** (SHA-256, unchanged; matches
  `BONUS_VARIANT_REPORT.md` §7):
  `candidate_a_config.py` `DE49BE20…D31A4`, `candidate_b_config.py`
  `5073ACB4…4A6D3`, `candidate2_config.py` `10F1DC1D…65F3C`,
  `candidate_lapis_config.py` `DC343889…69F4347`, `variant_config.py`
  `DDD4DBD1…1990D72`, `game_config.py` `9642B207…659B6421`.

---

## 7. Limitations

- **Not a production certification; no published RTP claim; nothing deployed.**
  This is a DEV measurement on the unpublished prototype. **The math is NOT
  locked** and no config is promoted as a production configuration.
- **The natural RTP is below the engine band.** Measured **0.9462**
  [0.9418, 0.9507] — below the 96.0% lower edge. This is a robust measurement
  (1.8M rounds, ±0.45 pp, per-range 0.9428–0.9495), but it means the config
  **does not currently meet** the 96.0–96.7% band. Whether this is acceptable
  (or whether a bounded calibration-**up** should be considered) is an open
  product decision, **not** settled here. Because the RTP is below band, the
  task's calibration-**down** condition does not apply.
- **The ≥100× tail is rare and seed-sensitive.** 168 events in 1.8M spins. The
  Wilson 95% interval [8.02e-5, 1.09e-4] is still relatively wide, so the
  point estimate (1:10,714) is not a firm tail certification, though the whole
  interval sits inside the acceptable 1:5,000–1:20,000 band. The tail is
  **entirely free-spin / persistent-vein driven** (168/168 with-free-spins,
  0 base-only).
- **No ≥500× or ≥1000× round observed; the 1,000× cap never engaged.** The cap
  is a safety valve this config does not reach in 1.8M natural rounds. The
  persistent-vein cap (7) bounds the board set and prevents the runaway that a
  locked-vein prototype showed.
- **Forced-freegame books are not used here.** This report measures only natural
  rounds (the correct basis for round RTP, entry rate and the round ≥100× tail).
  The feature's *internal* distribution is reported from the natural free-spin
  rounds that occurred (12,941 features), not from separately forced books.
- **No frontend/event-contract change.** The mechanic emits standard
  `reveal_event` / `fs_trigger_event` / `tumbleBoard` events; persistent veins
  are engine-internal board state, not a new event type.
- **The persistent-vein injection can overwrite a `pickaxe` (scatter)** on a new
  free-spin board, reducing that spin's retrigger count (by design — the
  persistent wild takes priority; scatter count and anticipation are re-derived
  immediately after injection). This is unchanged from the prior report and does
  not affect the natural-round RTP / tail measurement above.
- **Not committed, no off-limits file modified.** All changes are in
  `.runtime/block_cave/` (helpers + JSONs). No off-limits config was modified;
  no commit was made; `docs/STATUS.md` and `BONUS_VARIANT_REPORT.md` were left
  untouched.
