# Block Cave — Variant P (Lapis + persistent ore veins) Independent QA Review

**Verdict: PASS WITH FINDINGS** (no blocking defect; the mechanic, tail, split and
isolation claims are confirmed, but the **RTP-band feasibility claim is NOT
robust** on a fresh disjoint sample).

| | |
| --- | --- |
| Role | Independent QA agent (not the implementer) |
| Date | 2026-11-18 |
| Scope | Read-only on `math/`. No implementation file was modified. |
| Target | `math/games/block_cave/candidate_lapis_persistent_config.py` (Variant P), `game_override.py`, `gamestate.py`, `game_config.py`, `calibrate.py`, `BONUS_VARIANT_REPORT.md` |
| Report under review | `math/games/block_cave/BONUS_VARIANT_REPORT.md` |

---

## 1. Summary

Variant P layers a **persistent-ore-vein** free-spin mechanic on the Lapis Lazuli
base and replaces the paytable with a **merged, small-cluster-reduced** table, in
an attempt to reach a **≥100× natural round tail ≈ 1 in 10,000** (acceptable
1:5,000–1:20,000) while holding natural RTP inside the **96.0–96.7%** band.

I verified the mechanic by code review, re-ran the full check suite, confirmed
config reproducibility and off-limits integrity, and independently re-measured
the config on **three fresh, disjoint seed ranges** (70M/80M/90M) that were never
used by the author.

**Confirmed:**
- The mechanic is gated behind `config.ore_vein_persist_freespins` (defaults
  **OFF**); no existing config changes.
- Persistent veins accumulate within a free-spin series, keep their wild +
  neighbour-upgrade function, are reset at series start (no cross-round
  leakage), and the whole series is one reproducible book.
- The 1,000× cap is authoritative (`payoutMultiplier = min(base+free,1000)×100`).
- Config reproducibility (strips, SHAs, merged 5-tier, gate ON), 25/25 tests,
  13/13 `win_calculations`, `pip check` clean.
- **≥100× tail** and its **split** (all with-free-spins, 0 base-only).
- **Isolation** (persistence is the tail driver; persistence OFF → 0 ≥100×).
- **No new SDK event type** is introduced by the persistent-vein mechanic.

**Not robust / not confirmed:**
- **F1 (HIGH):** the claim that Variant P "sits inside the RTP band" is a
  range-dependent point estimate. On fresh disjoint ranges the pooled natural
  RTP is **0.9757 (above the 0.967 upper edge)**, and one range (90M) measured
  **1.0110 (above 100%)**.
- **F2 (MEDIUM):** `build_config()` does **not** set `ore_vein_persist_max`
  (it is `None`/unbounded). Only the measurement helpers set it to 7. The report
  §1 claims `config.ore_vein_persist_max = 7`.

---

## 2. Checks run (commands + results)

All commands run from the repo root using `math\.venv\Scripts\python.exe`
(Python 3.13.2).

| Check | Command | Result |
| --- | --- | --- |
| Config self-check | `python math/games/block_cave/candidate_lapis_persistent_config.py` | base SHA `00af3ba5…8181`, free SHA `bc15b4fb…4c47`, "Variant P config reproducible" |
| Block Cave suite | `python math/games/block_cave/test_block_cave.py` | **25/25 passed** (incl. `test_variant_p_config_reproducible`, `test_variant_p_gate_default_off`, `test_variant_p_cap_bounds_set`, `test_variant_p_inject_places_veins`, `test_variant_p_vein_explodes_but_position_persists`) |
| Upstream wins | `python -m pytest math/tests/win_calculations -q` | **13 passed in 0.07s** |
| Deps | `python -m pip check` | No broken requirements found |
| Baseline strips | `build_strip(20261117/…, BASE/FREE_COUNTS)` | base `7d04c138…b2451`, free `f7f48c53…d89754`, both length 200 |
| Off-limits SHAs | `Get-FileHash -Algorithm SHA256 <6 configs>` | all 6 match report §7 exactly (see §4) |

---

## 3. Mechanic verification (code review)

The mechanic is implemented in `math/games/block_cave/game_override.py` and the
flow is driven from `math/games/block_cave/gamestate.py`.

### 3.1 Gate (DEFAULTS OFF)

- `game_config.py` line 147: `self.ore_vein_persist_freespins = False` (default).
- `game_override.py:41-43` `_persist_enabled()` reads
  `bool(getattr(config, "ore_vein_persist_freespins", False))`.
- `candidate_lapis_persistent_config.py:202` sets it `True` for Variant P.

Verified: `test_variant_p_gate_default_off` passes; when the gate is off,
`persistent_veins` stays empty and no existing config or the §3.1 game changes.

### 3.2 Persistence + accumulation (within series only)

- `reset_book()` (`game_override.py:28-32`) clears `persistent_veins` at the
  start of every paid-round spin attempt (`run_spin` → `gamestate.py:12`).
- `reset_fs_spin()` (`game_override.py:34-36`) clears `persistent_veins` at the
  start of each free-spin **series** (`run_freespin` → `gamestate.py:40`).
- Within a series, `run_freespin` does **not** call `reset_book`, so the set
  carries across free spins and retriggers.
- `draw_board` (`game_override.py:120-140`) injects the recorded positions
  (`_inject_persistent_ore_veins`, lines 84-98) before the reveal, then
  rescans so every vein on the board becomes persistent.
- `tumble_board` (`game_override.py:142-155`) rescans after each cascade.

**Conclusion: no cross-round leakage.** `persistent_veins` is reset at both the
paid-round boundary (`reset_book`) and the series boundary (`reset_fs_spin`), so
no state transfers to a later paid round. Confirmed by code and by the isolation
measurement (persist OFF → 0 ≥100×).

### 3.3 1,000× cap is authoritative

`calibrate.py:148` enforces
`payoutMultiplier = int(round(min(baseGameWins+freeGameWins, 1000.0) * 100, 0))`,
and the `check_book` consistency check validates it. This is the same
sum-then-cap confirmed in `win_manager.py` (`basegame_wins`/`freegame_wins`
accumulated per gametype, then `evaluate_finalwin`/`update_final_win` does the
sum-then-cap). The report's ≥100× definition (total win of a paid base round
including all triggered free spins) is **correct**.

### 3.4 No invented SDK event type

The persistent-vein mechanic modifies engine-internal board state before
`reveal_event` and emits standard `reveal_event` / `fs_trigger_event` /
`tumbleBoard` events. **No new event type is introduced.** (The
`oreVeinUpgrade` event is a separate, pre-existing Stage-2 item from the
`create-cluster` rule, already documented as needing a frontend union member in
Stages 5–6; it is not created by the persistent-vein mechanic.)

---

## 4. Config reproducibility & off-limits integrity

### 4.1 Variant P self-check

`python math/games/block_cave/candidate_lapis_persistent_config.py`:
- base strip SHA `00af3ba544dba0ee523b6d4e85304d0622dd740a5c76dc13651e254a22558181`
- free strip SHA `bc15b4fb96319e90f35024fe8b751b3ee3534731a56aa0f9939a7a8034db4c47`
- asserts: length 200, counts match, no `silver`, gate ON, `create-cluster` →
  `diamond`, all 5–7 cluster pays ≥ 0.10×.

I independently confirmed: `cfg.ore_vein_persist_freespins is True`,
`ore_vein_rule == "create-cluster"`, `ore_vein_target == "diamond"`, no 5–7
cluster value < 0.10×, and `VARIANT_PAY_RANGES == [(5,7),(8,10),(11,14),(15,19),(20,30)]`
(5 merged tiers).

### 4.2 Baseline strips

`build_strip(20261117, BASE_COUNTS)` → `7d04c1381709f4ba…859bfb2451`
`build_strip(20261118, FREE_COUNTS)` → `f7f48c53b017f2e7…95d89754`
Both length 200; counts match the weight tables. Unchanged.

### 4.3 Off-limits configs (byte-identical)

Recomputed SHA-256 and matched report §7 **exactly** (all 6):

| file | SHA-256 (first 8 / last 5) |
| --- | --- |
| `candidate_a_config.py` | `DE49BE20…D31A4` |
| `candidate_b_config.py` | `5073ACB4…4A6D3` |
| `candidate2_config.py` | `10F1DC1D…65F3C` |
| `candidate_lapis_config.py` | `DC343889…69F4347` |
| `variant_config.py` | `DDD4DBD1…1990D72` |
| `game_config.py` | `9642B207…659B6421` |

---

## 5. Independent fresh-range measurement (disjoint from the author's ranges)

The author measured on **40M/50M/60M**. To avoid any tuning-range contamination I
measured on the **fresh, disjoint** ranges **70M/80M/90M** using the same helper
and configuration:

```
python .runtime/block_cave/measure_variant_cap.py 7 20000 10000 \
  .runtime/block_cave/qa_vp_70m.json 70000000 --compare-lapis
python .runtime/block_cave/measure_variant_cap.py 7 20000 10000 \
  .runtime/block_cave/qa_vp_80m.json 80000000 --compare-lapis
python .runtime/block_cave/measure_variant_cap.py 7 20000 10000 \
  .runtime/block_cave/qa_vp_90m.json 90000000 --compare-lapis
```

### 5.1 Variant P natural (n = 20,000 per range)

| Range | RTP | base RTP | feat RTP | hit | full | entry | feat mean | feat dur | max round | ≥100× (k) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 70M | 0.9622 | 0.7634 | 0.1988 | 0.6980 | 0.2464 | 0.0068 | 29.23 | 8.68 | 108.41 | 4 |
| 80M | 0.9538 | 0.7752 | 0.1786 | 0.7005 | 0.2501 | 0.0066 | 27.07 | 8.64 | 101.31 | 1 |
| 90M | **1.0110** | 0.7600 | 0.2509 | 0.7013 | 0.2523 | 0.0093 | 27.13 | 8.76 | 173.78 | 3 |
| **Pooled** | **0.9757** | 0.7662 | 0.2095 | 0.6999 | 0.2496 | 0.00755 | 27.81 | 8.69 | 127.83 | **8** |

Pooled fresh 95% CI for RTP: **[0.9493, 1.0021]** (straddles both band edges and
includes 1.0); pooled std ≈ 3.30, se ≈ 0.0135.

Fresh Lapis reference pooled RTP = **0.9741**; ≥100× = **0/60,000**.

### 5.2 ≥100× split (fresh, deterministic replay)

`qa_vp_split.json` — 8 total natural ≥100× rounds, **all with-free-spins, 0
base-only** (base-only share 0.000). This **confirms** the report's §3.3 finding
(that the tail is free-spin driven), reproduced on fresh ranges with 8 events.

### 5.3 Isolation (same merged paytable, persistence ON vs OFF; forced freegame, n=5,000/range)

`qa_vp_isolation.json`:

| forced freegame (merged paytable) | persist ON | persist OFF |
| --- | --- | --- |
| ≥100× | **150/15000 = 0.01000** | **0/15000 = 0.000** |
| feature payout mean | 24.35 | 6.95 |
| feature payout max (avg of range maxes) | 297.1 | 35.9 |
| feature duration mean | 8.32 | 8.47 |

This **confirms** the report's §5 claim: persistence is the dominant tail driver.
With the same merged paytable, turning persistence off collapses the feature mean
(~24.3× → ~6.9×) and eliminates every ≥100× forced freegame.

---

## 6. Findings

### F1 (HIGH) — The RTP-band feasibility claim is not robust; the fresh pooled RTP is above the band

**Location:** `BONUS_VARIANT_REPORT.md` §3.2, §5, §6 (and the open-decision
framing in `docs/STATUS.md`).

**Claim:** §6 — "Variant P at cap=7, common-scale=1.10 meets the tail objective
and **sits inside the RTP band** (as a pooled point estimate)." §3.2/§5 —
"the net lands Variant P **inside** the 96.0–96.7% band while the Lapis reference
sits at ~0.9716 (above the 0.967 upper edge)."

**Reproduction:** Independent fresh measurement on disjoint ranges (70M/80M/90M,
n=20,000 each):

| Sample | Variant P pooled RTP | ≥100× | In band? | Lapis pooled RTP |
| --- | --- | --- | --- | --- |
| Author (40M/50M/60M) | 0.9651 | 6/60000 | Yes | 0.9716 (above) |
| **QA fresh (70M/80M/90M)** | **0.9757** | 8/60000 | **No (above 0.967)** | 0.9741 (above) |

- Fresh pooled RTP **0.9757** is **above the 0.967 upper edge** (and the 95% CI
  [0.9493, 1.0021] straddles the whole band and includes 1.0).
- **90M range alone = 1.0110**, **above 100%** (the 95% CI upper for that range
  is 1.0616).
- The two pooled point estimates (0.9651 vs 0.9757) differ by **+1.06 pp** — larger
  than the 0.7 pp band — and the 90M point estimate is above 100%.

**Why it matters:** The §3.2/§5/§6 "in band" conclusion is a range-dependent
point estimate, not a robust confirmation. On a fresh sample the config is
**out of band on the high side**, and on one fresh range it exceeds 100%. This
directly affects the product decision (whether Variant P's tail is worth the RTP
volatility). §8 does acknowledge per-range seed-sensitivity, but only frames it
as "per-range estimates straddle both edges"; it does **not** report that a fresh
**pooled** sample lands above the band.

**Recommendation:** Reword §6/§3.2/§5 to "the pooled point estimate on the
author's ranges is in band, but this is not robust: a fresh disjoint sample
measures 0.9757 (above 0.967) and one range exceeds 100%." Present the RTP band
as **not robustly met** and add the fresh pooled value to §8 Limitations.

### F2 (MEDIUM) — `build_config()` does not set `ore_vein_persist_max` (cap unbounded)

**Location:** `candidate_lapis_persistent_config.py:179-203` (`build_config`),
`game_override.py:64` (`_rescan_persistent_veins`), report §1.

**Claim:** report §1 — "Persistent gate — `config.ore_vein_persist_freespins =
True`, `config.ore_vein_persist_max = 7`."

**Reproduction:** I ran
`cfg = candidate_lapis_persistent_config.build_config()` and inspected the
attributes. `cfg.ore_vein_persist_freespins is True`, but
`getattr(cfg, "ore_vein_persist_max", "MISSING")` returns **`MISSING`** —
`build_config()` **never sets** `ore_vein_persist_max`. The cap is only set by
the measurement/helper scripts (`measure_variant_cap.py:75`,
`qa_isolate_vp.py`, `split_vp100x.py`), not by the config builder.

**Consequence:** `_rescan_persistent_veins` (`game_override.py:64`) does
`cap = getattr(self.config, "ore_vein_persist_max", None)`, and when the config is
built by `build_config()` alone, `cap` is `None` → the `if cap is not None …`
clamp is **skipped**, so `persistent_veins` is **unbounded** across a long
series. The cap was added precisely to prevent the set growing without bound (the
runaway that a locked-vein prototype showed). The measured numbers used cap=7
(via the helper), so they are valid, but the config **as documented** does not
actually bound the set.

**Recommendation:** Either set `config.ore_vein_persist_max = 7` inside
`build_config()` (so the config is self-contained and matches report §1), or
correct report §1 to state that the cap is set by the measurement helper and is
`None` (unbounded) from `build_config()`.

### F3 (LOW) — §3.1 50M feature payout mean over-stated by 0.01

**Location:** `BONUS_VARIANT_REPORT.md` §3.1 table, 50M Variant P row.

Report lists **27.07**; the author's own `final_50m_cs110.json`
`feat_pay_mean = 27.0645833…` rounds to **27.06**. A 0.01 transcription slip
(non-material). The 40M (26.41) and 60M (24.30) values transcribe correctly.

### F4 (LOW) — §4 "feature duration max 35" is a rounded mean-of-maxes; observed max is 36

**Location:** `BONUS_VARIANT_REPORT.md` §4 table.

Report lists **35**; the author's `bonus_variant_pooled.json` has
`feat_dur_max = 34.6666…` (mean of per-range maxes 32/36/36 = 34.67), which rounds
to 35. The **observed max** across the three ranges was **36**. Recommend labeling
it "mean of range maxes (34.67), observed max 36."

### F5 (INFO) — §5 persistence-ON isolation numbers are not in a checked-in JSON

**Location:** `BONUS_VARIANT_REPORT.md` §5 table (persist ON row) vs
`bonus_variant_isolation.json`.

`bonus_variant_isolation.json` contains **only the persistence-OFF arm** (0/15000,
feat_mean 6.94, feat_max_avg 44.85). The **ON** arm figures in the report table
(137/15000 = 0.00913, feat_mean 24.33, feat_max_avg 287.0) are **not** backed by
a checked-in artifact. I independently reproduced the ON arm on fresh ranges
(150/15000 = 0.01000, feat_mean 24.35, feat_max_avg 297.1), which directionally
confirms the claim, but the specific ON numbers in §5 are not reproducible from
the committed JSON. Recommend adding the ON-arm JSON.

### F6 (INFO) — Persistent-vein injection can overwrite a scatter on the new board

**Location:** `game_override.py:93-95` (`_inject_persistent_ore_veins`).

A recorded persistent-vein position may coincide with a cell that the current
free spin drew as a `pickaxe` (scatter). `self.board[reel][row] = self.create_symbol("ore_vein")`
overwrites it. The code does recompute `get_special_symbols_on_board()` and
`_recompute_anticipation()` (lines 96-97), so the scatter count/anticipation are
re-derived — but that free spin's **retrigger** count is reduced by the overwritten
scatter. This is a subtle, by-design-looking interaction (the persistent wild
takes priority), but it is worth an explicit note so it is not mistaken for a bug
in retrigger accounting.

### F7 (INFO) — Persistent veins are engine-internal; no frontend marker distinguishes them

**Location:** `game_override.py:84-98`; report §8.

Because the veins are injected before the reveal and emit no new event type, the
frontend cannot distinguish a **persistent** ore vein from a normally-landed one
(no glow/marker in the payload). There is **no SDK event-contract clash** (good),
but if the design intends a visual "persistent vein" affordance, that information
is not currently available to the frontend. Confirms report §8; flags the
frontend implication for Stages 5–6.

### F8 (INFO) — `_rescan_persistent_veins` iterates Python sets

**Location:** `game_override.py:67-82`.

`_rescan_persistent_veins` builds and iterates a Python `set` of `(reel,row)`
int-tuples. For int-tuples the iteration order is deterministic in CPython (int
and tuple-of-int hashing is not randomized), so the cap-trimming result is
reproducible across runs. However the order is **hash order, not insertion/scan
order**, so when the cap binds, which veins are kept is not the "scan order"
that the comment implies. Not a correctness bug for int-tuples; note for clarity.

### F9 (INFO) — Visual / Playwright QA is not applicable

No Block Cave frontend exists yet (frontend is Stages 5–6). There is no Pixi
canvas, no Action button and no example round to verify, so the visual-qa check
cannot be run. This is not a finding against the math; it is a limitation of the
current stage.

---

## 7. Verdict

**PASS WITH FINDINGS.** The persistent-ore-vein mechanic is correctly gated
(default OFF), the config is reproducible (strips + SHAs + merged 5-tier + gate
ON), off-limits files are byte-identical, the 25/25 and 13/13 suites pass,
`pip check` is clean, the 1,000× cap is authoritative, and **no new SDK event
type** is introduced. The ≥100× tail, its base-only/with-fs split (all
with-free-spins), and the persistence isolation (persistence is the tail driver)
are all **confirmed on fresh disjoint ranges**.

The one material issue is **F1**: the report's conclusion that Variant P "sits
inside the RTP band" is **not robust**. On a fresh disjoint sample the pooled
natural RTP is **0.9757 (above the 0.967 upper edge)** and one range (90M) is
**1.0110 (above 100%)**. The report should present the RTP band as **not robustly
met** and surface the fresh pooled value.

F2 (the cap not set by `build_config()`) is a latent implementation/documentation
mismatch that should be fixed so the shipped config matches its documented
cap=7 behavior.

---

## 8. Limitations

- All figures are **DEV measurements** on an unpublished prototype; **no
  production RTP claim** is made by this review.
- The ≥100× tail is rare (8 events in 60,000 fresh rounds) and the Wilson 95%
  interval is wide: **[6.76e-5, 2.63e-4] = [1:14,801, 1:3,801]**, so the 1:7,500
  point estimate is not a firm tail certification. It is nonetheless **within**
  the acceptable 1:5,000–1:20,000 band.
- No ≥500× or ≥1000× round was observed and no `wincap` bind occurred in the
  fresh samples, so the 1,000× cap is a safety valve that this config does not
  reach.
- The forced-freegame books are deliberately generated and used only for the
  feature's internal distribution, not for round RTP or entry rate.
- The "Δ vs Lapis" comparison bundles both the merged paytable and the
  persistent-vein mechanic; §5 isolation is the direct test of the persistence
  effect and confirms it is the dominant driver.
- The measured RTP std at n=20k/range (~2.9–3.7) is much wider than the 0.7 pp
  band, so any single-range point estimate (including the 90M 1.0110) is not a
  robust band statement.

## 9. Evidence artifacts

| Artifact | Purpose |
| --- | --- |
| `.runtime/block_cave/qa_vp_70m.json` / `qa_vp_80m.json` / `qa_vp_90m.json` | QA fresh-range measurement (Variant P + Lapis reference) |
| `.runtime/block_cave/qa_vp_pooled.json` | QA pooled aggregation (incl. Wilson CIs) |
| `.runtime/block_cave/qa_vp_split.json` | QA ≥100× base-only vs with-free-spins split |
| `.runtime/block_cave/qa_vp_isolation.json` | QA persistence ON vs OFF isolation |
| `.runtime/block_cave/qa_aggregate_vp.py`, `qa_split_vp.py`, `qa_isolate_vp.py` | QA helpers (read-only) |

No credentials are embedded in this report. Only this QA report was written; no
implementation file was modified.
