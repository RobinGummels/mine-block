# Block Cave — Variant P (Lapis + persistent ore veins) Measurement Report

**Status:** DEV measurement only. **This is NOT a production certification and
makes no RTP claim for a published game.** All figures are measured on the
current (unpublished) Block Cave prototype. Owner: Math agent.

Variant P is a DEV experiment that layers a **persistent-ore-vein** free-spin
mechanic on the Lapis Lazuli base (`candidate_lapis_config.py`) and replaces the
paytable with a **merged, small-cluster-reduced** table, in an attempt to reach a
**≥100× natural round tail ≈ 1 in 10,000** (acceptable band 1:5,000–1:20,000)
while holding the natural RTP inside the **96.0–96.7%** engine band. The
mechanic is gated behind `config.ore_vein_persist_freespins` (**DEFAULTS OFF**),
so no existing config or the §3.1 game changes.

This is the **cap = 7, common-scale = 1.10** calibration (the final point chosen
after cs=1.11 pushed the pooled out-of-sample RTP to ~0.970, above the 0.967
upper edge).

---

## 1. Config (what Variant P is)

`math/games/block_cave/candidate_lapis_persistent_config.py` (self-contained DEV
config; does **not** modify `game_config.py`, `candidate_*_config.py`,
`variant_config.py` or `ore_vein_rules.py`):

- **Strips** — byte-identical to the Lapis Lazuli strips (same counts, same
  seeds, same SHAs; lapis replaces silver). Base SHA
  `00af3ba5…258181`, free SHA `bc15b4fb…4db4c47`.
- **Paytable** — the §3.1 9 tiers are merged into **5 tiers**
  `VARIANT_PAY_RANGES = [(5,7),(8,10),(11,14),(15,19),(20,30)]`. The small-cluster
  tier (5–7) pays are **reduced** (a winning 5–7 cluster still pays ≥ 0.10×); the
  high tiers (11–14, 15–19, 20–30) retain the §3.1 low-end values so the
  premium/ingot tail can express itself. The **common** symbols (`earth`, `stone`,
  `timber`, `copper`) are baked at **common-scale ≈ 1.10** relative to the merged
  Lapis values; **premium** (`lapis`, `gold`, `emerald`, `diamond`) and **ingot**
  are **unscaled**. There is **no bonus multiplier** in Variant P.
- **Ore-vein rule** — the DEV `create-cluster` → `diamond` rule (same as Lapis /
  Candidate A).
- **Persistent gate** — `config.ore_vein_persist_freespins = True`,
  `config.ore_vein_persist_max = 7`.

### 1.1 The persistent-ore-vein mechanic

`game_override.py` implements it (gated, DEFAULTS OFF). When ON and a free-spin
board is drawn, every ore vein that lands is recorded as **persistent**
(`persistent_veins`, a set of `(reel,row)` positions). The recorded positions are
**re-injected** at the start of each subsequent free spin in the **same series**,
so a vein that explodes during a cascade is removed from the board but
**regenerates at its recorded position** on the next free spin. The whole series
is one reproducible book; `persistent_veins` is reset at the series start, so no
state transfers to a later paid round. The set is bounded by
`ore_vein_persist_max` (here 7) so it cannot grow across a long series.

Crucially the persistent veins are **NOT locked**: during a cascade they behave
like normal ore veins and **can explode**. (An earlier prototype that locked the
veins created a positive-feedback loop — a wild that never leaves the board feeds
the cascade and lands new veins that also never leave — saturating the board and
running to the 1000× cap. The can-explode variant breaks that feedback.)

**Noted interaction (by design):** when a recorded persistent-vein position
coincides with a cell that the current free spin drew as a `pickaxe` (scatter),
the injection overwrites that scatter with the persistent wild. The scatter count
and anticipation are re-derived immediately after injection
(`_recompute_anticipation`), but that spin's **retrigger** count is reduced by the
overwritten scatter. The persistent wild takes priority, so this is intentional
and is not a retrigger-accounting bug.

---

## 2. Measurement method

- **Config built:** `candidate_lapis_persistent_config.build_config()` with
  `ore_vein_persist_max = 7`. Ore-vein upgrade **enabled**
  (`set_ore_vein_enabled(True)`).
- **Seed ranges:** three **fresh, disjoint** out-of-sample ranges —
  `start_seed = 40_000_000`, `50_000_000`, `60_000_000`.
- **Natural:** n = 20,000 base rounds per range (criteria `basegame`, no forcing)
  — the only basis for round RTP, hit, full return, entry rate and the round
  ≥100× tail.
- **Forced freegame:** n = 10,000 per range (`criteria=freegame`,
  `force_freegame=True`) — used **only** for the feature's *internal*
  distribution (duration/payout/tails), NOT for round RTP or entry rate.
- **Lapis reference:** the same ranges were run with
  `candidate_lapis_config.build_config()` (identical strips, §3.1 9-tier
  paytable, no persistence) for the Δ comparison.

Helper: `.runtime/block_cave/measure_variant_cap.py 7 20000 10000 <out> <seed>
--compare-lapis`. Outputs: `final_40m_cs110.json`, `final_50m_cs110.json`,
`final_60m_cs110.json`.

---

## 3. Results — natural rounds (n = 20,000 per range)

### 3.1 Per-range

| Range | arm | RTP (95% CI) | base RTP | feat RTP | hit | full | entry | feat mean | feat dur | max round | ≥100× (Wilson) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 40M | **Variant P** | 0.9593 [0.9120, 1.0066] | 0.7599 | 0.1994 | 0.7020 | 0.2488 | 0.00755 | 26.41 | 8.69 | 218.57 | 3/20000 [5.1e-5, 4.4e-4] |
| 40M | Lapis | 0.9616 [0.9402, 0.9830] | 0.9023 | 0.0593 | 0.7020 | 0.2980 | 0.00755 | 7.86 | 8.87 | 42.91 | 0 |
| 50M | **Variant P** | 0.9654 [0.9230, 1.0078] | 0.7705 | 0.1949 | 0.6954 | 0.2485 | 0.00720 | 27.06 | 8.64 | 109.20 | 1/20000 [8.8e-6, 2.8e-4] |
| 50M | Lapis | 0.9729 [0.9509, 0.9949] | 0.9079 | 0.0650 | 0.6954 | 0.2912 | 0.00720 | 9.03 | 8.75 | 28.44 | 0 |
| 60M | **Variant P** | 0.9705 [0.9283, 1.0127] | 0.7640 | 0.2065 | 0.6980 | 0.2525 | 0.00850 | 24.30 | 8.49 | 148.42 | 2/20000 [2.7e-5, 3.6e-4] |
| 60M | Lapis | 0.9802 [0.9582, 1.0021] | 0.9079 | 0.0723 | 0.6980 | 0.2994 | 0.00850 | 8.50 | 8.78 | 22.08 | 0 |

### 3.2 Pooled (60,000 natural rounds total)

| metric | Variant P | Lapis | Δ (Variant P − Lapis) |
|---|---|---|---|
| RTP | **0.9651** | 0.9716 | −0.0065 |
| base RTP | 0.7648 | 0.9060 | −0.1412 |
| feature RTP | 0.2003 | 0.0655 | +0.1348 |
| visible hit | 0.6985 | 0.6985 | 0.0000 |
| full return (≥1.0×) | 0.2499 | 0.2962 | −0.0463 |
| feature entry | 0.00775 | 0.00775 | 0.00000 |
| feature payout mean | 25.92 | 8.46 | +17.46 |
| feature payout median | 20.61 | 7.79 | +12.83 |
| feature payout p90 | 48.32 | 14.07 | +34.24 |
| feature payout p99 | 100.81 | 19.88 | +80.94 |
| feature payout max | 158.62 | 23.80 | +134.82 |
| feature duration mean | 8.61 | 8.80 | −0.19 |
| max round (mean of range maxes) | 158.73 | 31.14 | +127.59 |
| **≥100× natural** | **6/60000** (1:10,000) | 0/60000 | +6 |
| ≥100× Wilson 95% | [4.6e-5, 2.18e-4] | [0, 6.4e-5] | — |
| ≥500× natural | 0 | 0 | 0 |
| ≥1000× natural | 0 | 0 | 0 |
| wincap bind rate | 0 | 0 | 0 |
| consistency violations | 0 | 0 | 0 |

**Natural RTP.** The pooled point estimate on the author's 40M/50M/60M ranges is
**0.9651**, which sits **inside** the 96.0–96.7% band. This is a
**range-dependent point estimate, NOT a robust band certification**: an
independent re-measurement on **fresh, disjoint ranges** (70M/80M/90M, n=20,000
each; see the QA report and `qa_vp_70m.json`/`qa_vp_80m.json`/`qa_vp_90m.json`/
`qa_vp_pooled.json`) measures a pooled natural RTP of **0.9757** — **above the
0.967 upper edge** — and one range (90M) measured **1.0110 (above 100%)**. The
two pooled point estimates differ by **+1.06 pp** (0.9651 vs 0.9757), larger than
the 0.7 pp band. The per-range estimates on the author's ranges
(0.9593 / 0.9654 / 0.9705) and on the fresh ranges (0.9622 / 0.9538 / 1.0110)
straddle both band edges — the seed-range variance (±0.007, from the 1.5–3.7 RTP
std at n=20k) is **wider than the 0.7 pp band**, so the RTP band should be
treated as **not robustly met** (see Limitations).

**≥100× natural tail.** The pooled point estimate is **6/60,000 = 1:10,000**,
which sits at the centre of the acceptable **1:5,000–1:20,000** band. The Wilson
95% interval is **[4.6e-5, 2.18e-4]** (i.e. ≈1:21,700 to ≈1:4,600), so the
interval straddles the band edges and is consistent with the 1:5,000–1:20,000
target. **No** ≥500× or ≥1000× round was observed, and **no** wincap bind (the
1,000× cap never engaged) in 60,000 natural rounds.

### 3.3 ≥100× hit — base-only vs with-free-spins split

The ≥100× hit is defined as the **total win of a paid base round including any
triggered free spins** (`payoutMultiplier = min(baseGameWins+freeGameWins,1000)×100`).
To report the split, the natural runs were replayed (deterministic) and each
≥100× round inspected for its `baseGameWins` vs `freeGameWins`. Helper:
`.runtime/block_cave/split_vp100x.py` → `bonus_variant_split.json`.

| Range | ≥100× rounds | base-only ≥100× | with-free-spins ≥100× |
|---|---|---|---|
| 40M | 3 | 0 | 3 |
| 50M | 1 | 0 | 1 |
| 60M | 2 | 0 | 2 |
| **Pooled** | **6** | **0** | **6** |

Every natural ≥100× hit came from a base round that **triggered free spins**, and
the **free spins alone** produced the ≥100× total. **No base round reached ≥100×
on its own** in 60,000 natural rounds (base-only share = 0.000). The six hits
and their splits:

| range | round idx | total | base | free |
|---|---|---|---|---|
| 40M | 3603 | 218.57× | 0.00× | 218.57× |
| 40M | 8061 | 115.81× | 1.50× | 114.31× |
| 40M | 10917 | 125.04× | 0.00× | 125.04× |
| 50M | 1235 | 109.20× | 0.32× | 108.88× |
| 60M | 14737 | 148.42× | 0.00× | 148.42× |
| 60M | 16542 | 121.53× | 0.00× | 121.53× |

This confirms the design expectation: **the ≥100× tail is a free-spin /
persistent-vein phenomenon**, not a base-game one.

---

## 4. Results — forced freegame (feature internal distribution, n = 10,000/range)

| metric | Variant P (pooled) | Lapis (pooled) |
|---|---|---|
| feature payout mean | 24.36 | 8.31 |
| feature payout median | 19.78 | 7.53 |
| feature payout p90 | 45.16 | 13.78 |
| feature payout p99 | 99.06 | 22.34 |
| feature payout max | 345.73 | 184.47 |
| feature duration mean | 8.33 | 8.48 |
| feature duration max | mean of range maxes (34.67), observed max 36 | mean of range maxes (34.67), observed max 36 |
| **≥100× (forced)** | **286/30000 = 0.00953** [0.0085, 0.0107] | 2/30000 = 6.7e-5 [1.8e-5, 2.4e-4] |
| ≥500× (forced) | 0 | 0 |
| ≥1000× (forced) | 0 | 0 |
| consistency violations | 0 | 0 |

At **forced** freegame entry, Variant P's feature pays ≥100× in **~0.95%** of
entries (Wilson [0.85%, 1.07%]) vs Lapis ~0.007%. Because the natural entry rate
is ~0.775%, this gives a natural round ≥100× probability of
≈0.00775 × 0.00953 ≈ **7.4e-5** — consistent with the directly-measured
**6/60,000 = 1.0e-4** (the direct measurement is authoritative). The forced runs
confirm the persistence lifts the feature tail by ~two orders of magnitude.

---

## 5. Ore-vein Δ vs Lapis

The Lapis reference and Variant P share the same strips, scatter entry and
ore-vein `create-cluster` rule; they differ in **(a)** the merged, reduced
small-cluster paytable and **(b)** the persistent-ore-vein mechanic. The **Δ vs
Lapis** (pooled natural) is in §3.2. The dominant effects:

- **Base RTP drops −14.1 pp** (0.7648 vs 0.9060): the merged table's reduced
  5–7 cluster pays lower the base-game contribution, and the +1.10 common-scale
  only partially compensates.
- **Feature RTP rises +13.5 pp** (0.2003 vs 0.0655) and the **feature payout mean
  rises +17.5×** (25.9 vs 8.5): the persistent veins compound across a free-spin
  series.
- **Net RTP −0.65 pp** (0.9651 vs 0.9716): the two effects nearly offset, and
  on the author's 40M/50M/60M ranges the net point estimate (0.9651) sits
  **inside** the 96.0–96.7% band while the Lapis reference sits at ~0.9716
  (above the 0.967 upper edge). This "in band" conclusion is **range-dependent
  and NOT robust**: an independent re-measurement on fresh, disjoint ranges
  (70M/80M/90M) gives a pooled natural RTP of **0.9757 (above 0.967)** and one
  range (90M) is **1.0110 (above 100%)**. See §6 and Limitations.
- **≥100× natural** goes from **0/60,000** (Lapis) to **6/60,000** (Variant P).
- **≥100× forced** goes from **2/30,000** (Lapis) to **286/30,000** (Variant P).
- **Round max** goes from **31.1** (Lapis, mean of range maxes) to **158.7**
  (Variant P); the largest single observed round is **218.57×** (40M range).

The persistence is the **dominant** tail driver. This was confirmed directly with
an **isolation measurement** (same merged paytable, cap=7; both arms are now
checked-in and reproducible): persistence **OFF** via
`.runtime/block_cave/isolate_persist_off.py` → `bonus_variant_isolation.json`,
and persistence **ON** via `.runtime/block_cave/isolate_persist_on.py` →
`bonus_variant_isolation_on.json` (forced freegame n = 5,000/range on the
author's 40M/50M/60M ranges, `start_seed + 20000`):

| forced freegame (same merged paytable) | persist **ON** | persist **OFF** |
|---|---|---|
| ≥100× | 137/15000 = 0.00913 | **0/15000 = 0.000** |
| feature payout mean | 24.33 | **6.94** |
| feature payout max (avg of range maxes) | 287.0 | **44.9** |
| feature duration mean | 8.33 | 8.50 |

With the **same** merged paytable, turning persistence **off** collapses the
feature mean from ~24.3× to ~6.9× and eliminates every ≥100× forced freegame
(0/15,000), while turning it **on** produces ~0.9% ≥100× forced freegames. The
≥100× tail therefore comes from the **persistent-vein compounding** across the
free-spin series, not from the merged paytable. (The persistence-OFF feature mean
of ~6.9× is also *below* Lapis's ~8.3×, confirming the merged paytable alone
*lowers* the feature rather than lifting it.)

Both arms are reproducible from the checked-in JSONs: the ON arm
(`bonus_variant_isolation_on.json`) reproduces the figures in the table above
(137/15,000 = 0.00913, feat mean 24.33, feat max avg 287.0) and the OFF arm
(`bonus_variant_isolation.json`) reproduces 0/15,000, feat mean 6.94, feat max
avg 44.9.

---

## 6. Conclusion / feasibility

**Variant P at cap=7, common-scale=1.10 meets the tail objective, but the RTP
band is NOT robustly met.** On the author's 40M/50M/60M ranges the pooled natural
RTP point estimate is **0.9651**, which sits **inside** the 96.0–96.7% band, but
this is a **range-dependent point estimate, not a robust certification**: an
independent re-measurement on **fresh, disjoint ranges** (70M/80M/90M, n=20,000
each) gives a pooled natural RTP of **0.9757 (above the 0.967 upper edge)** and
one range (90M) measures **1.0110 (above 100%)**. The two pooled point estimates
differ by **+1.06 pp**, larger than the 0.7 pp band. See the QA report and
Limitations.

- **≥100× natural = 6/60,000 = 1:10,000** — at the centre of the acceptable
  1:5,000–1:20,000 band (Wilson [1:21,700, 1:4,600]). On the fresh disjoint ranges
  the equivalent figure is **8/60,000 ≈ 1:7,500** (Wilson [1:14,801, 1:3,801]),
  consistent with the same band.
- **Natural RTP = 0.9651** pooled on the author's ranges — a **point estimate in
  band, but NOT robust**: the fresh pooled value is **0.9757 (above 0.967)** and
  the 90M range is **1.0110 (above 100%)** (per-range estimates straddle the
  edges; see Limitations).
- **Visible hit ≈ 0.70**, **feature entry ≈ 0.78%**, **short** free spins (mean
  8.6, max 28), **0** consistency violations, **0** wincap binds, **no** ≥500× /
  ≥1000× rounds.
- **The ≥100× tail is free-spin driven**: all 6 natural hits are with-free-spins
  (0 base-only); the fresh ranges reproduce this (8/8 with-free-spins).

Compared to the Lapis reference, Variant P buys the tail at the cost of a **lower
base RTP** (−14 pp) and a **lower full-return** (−4.6 pp, i.e. fewer ≥1.0× base
rounds) but a **much higher feature payout** (+17.5× mean), netting to an RTP
that is ~0.65 pp below Lapis on the author's ranges. The **RTP band is NOT
robustly met**: the pooled point estimate is in band on the author's ranges, but
a fresh disjoint sample measures **above** the band (0.9757) and one range
exceeds 100% (90M = 1.0110).

---

## 7. Reproducibility

- **Config self-check:** `python math/games/block_cave/candidate_lapis_persistent_config.py`
  (prints the two strip SHAs + "reproducible").
- **Tests:** `python math/games/block_cave/test_block_cave.py` (25/25, incl.
  `test_variant_p_config_reproducible` and the 5 persistent-vein mechanic tests).
  Also `python -m pytest games/block_cave/test_block_cave.py -q`.
- **Measurement:** `python .runtime/block_cave/measure_variant_cap.py 7 20000 10000
  <out_json> <start_seed> --compare-lapis` for each of
  `start_seed = 40000000 / 50000000 / 60000000`.
- **Aggregation:** `.runtime/block_cave/aggregate_vp.py` →
  `.runtime/block_cave/bonus_variant_pooled.json`.
- **≥100× split:** `.runtime/block_cave/split_vp100x.py` →
  `.runtime/block_cave/bonus_variant_split.json`.
- **Persistence isolation:** `.runtime/block_cave/isolate_persist_off.py` →
  `.runtime/block_cave/bonus_variant_isolation.json` (persistence OFF) and
  `.runtime/block_cave/isolate_persist_on.py` →
  `.runtime/block_cave/bonus_variant_isolation_on.json` (persistence ON), both on
  the same merged paytable, forced freegame n = 5,000/range.
- **Outputs:** `final_40m_cs110.json`, `final_50m_cs110.json`,
  `final_60m_cs110.json` (per-range, with lapis comparison), plus the pooled /
  split JSONs above (all UTF-8, **BOM-free**, LF).
- **Off-limits configs verified byte-identical** (SHA-256, unchanged):
  `candidate_a_config.py` `DE49BE20…D31A4`, `candidate_b_config.py`
  `5073ACB4…4A6D3`, `candidate2_config.py` `10F1DC1D…65F3C`,
  `candidate_lapis_config.py` `DC343889…69F4347`, `variant_config.py`
  `DDD4DBD1…1990D72`, `game_config.py` `9642B207…659B6421`.
- `pip check` clean; upstream `math/tests/win_calculations` 13/13.

## 8. Limitations

- **Not a production certification; no published RTP claim; nothing deployed.**
- The RTP 95% CI at n=20k/range (std 1.5–3.7) is ~±0.05–0.07, far wider than the
  0.7 pp band, so a single range is **not** a robust band statement. The pooled
  point estimate on the author's ranges (0.9651) is in band, but the per-range
  estimates straddle both edges. **An independent re-measurement on fresh,
  disjoint ranges (70M/80M/90M, n=20,000 each — see the QA report
  `qa/reports/block_cave_stage3_variant_p_review.md` and the QA artifacts
  `.runtime/block_cave/qa_vp_70m.json`, `qa_vp_80m.json`, `qa_vp_90m.json`,
  `qa_vp_pooled.json`) measures a pooled natural RTP of 0.9757 (above the 0.967
  upper edge; 95% CI [0.9493, 1.0021], which straddles the whole band and
  includes 1.0), and one range (90M) measures 1.0110 (above 100%).** The two
  pooled point estimates differ by +1.06 pp — larger than the 0.7 pp band — so
  the RTP band is **not robustly met**.
- The ≥100× tail is **rare and highly seed-sensitive**: 6 events in 60,000 spins.
  The Wilson 95% interval [4.6e-5, 2.18e-4] is wide, so the **point estimate**
  (1:10,000) is not a firm tail certification; the acceptable band
  (1:5,000–1:20,000) is consistent with the measured 1:10,000.
- The 1,000× cap never engaged (0 wincap binds) and no ≥500× / ≥1000× round was
  observed, so the cap is a safety valve that the calibrated config does not
  reach in these samples. The persistent-vein cap (7) bounds the board set and
  prevents the runaway that a locked-vein prototype showed.
- The "Δ vs Lapis" bundles **both** the merged paytable and the persistent-vein
  mechanic. §5 isolates the two directly (persistence OFF on the same merged
  paytable) and shows the persistence is the dominant tail driver: persistence
  OFF collapses the forced feature mean to ~6.9× and yields **0** ≥100× forced
  freegames (0/15,000), versus **137/15,000** (0.00913) with persistence ON.
- The forced-freegame books are **deliberately generated** and are used only for
  the feature's internal distribution, not for round RTP or entry rate.
- No frontend/event-contract change: the mechanic emits standard
  `reveal_event` / `fs_trigger_event` / `tumbleBoard` (with `explodingSymbols`)
  events. The persistent veins are an **engine-internal** board state, not a new
  event type, so there is no SDK event-contract clash.
- **Persistent-vein injection can overwrite a `pickaxe` (scatter)** on a new
  free-spin board, reducing that spin's retrigger count (by design — the
  persistent wild takes priority; the scatter count and anticipation are
  re-derived immediately after injection, but the overwritten scatter is not
  counted for retrigger). See §1.1.
