# Block Cave — Stage 3 Math Calibration Review (independent QA)

**Reviewer:** Independent QA agent (stake-engine-validation)
**Date:** 2026-11-17
**Scope:** `math/games/block_cave/CALIBRATION_REPORT.md` + the checked-in Stage 3
math (paytable calibration to scale 1.0, revision C3)
**Files reviewed (read-only):**
- `math/games/block_cave/CALIBRATION_REPORT.md`
- `math/games/block_cave/MATH_DESIGN.md` (§3.1 paytable, revision C3)
- `math/games/block_cave/game_config.py`
- `math/games/block_cave/calibrate.py`
- `math/games/block_cave/test_block_cave.py`
- `math/games/block_cave/run.py`
- Measurement corpus under `.runtime/block_cave/*.json`

> **Read-only constraint.** No `math/` source file was edited, patched or
> reformatted during this review. The only generated artifact touched is
> `math/.runtime/block_cave/prototype_books.jsonl`, which is the normal output of
> `run.py` (a DEV observation file, not an implementation file). QA scripts were
> placed under `.runtime/block_cave/` and this report under `qa/reports/`.

---

## Verdict: **PASS WITH FINDINGS**

Every claim in `CALIBRATION_REPORT.md` was independently reproduced. The
calibration result (the `MATH_DESIGN.md` §3.1 paytable at scale 1.0 gives a
natural base-game RTP ≈ 0.965, inside the 96.0–96.7% band) is **confirmed and
not an artifact of the report's own harness**. No blocking defect was found.
All four findings below are **minor / informational** and none changes the
conclusion.

| Check | Result |
| --- | --- |
| Task 1 — Strip reproducibility | **PASS** |
| Task 2 — Paytable == §3.1 (scale 1.0, not ×F) | **PASS** |
| Task 3 — Independent measurement (100k / 5k) | **PASS** |
| Task 4 — Book / lookup invariants | **PASS** |
| Task 5 — `test_block_cave` (11/11, incl. wincap + ore-vein) | **PASS** |
| Task 6 — `pip check` + upstream pytest | **PASS** |
| Task 7 — Report consistency vs `.runtime` corpus | **PASS** |

---

## 1. Task 1 — Strip reproducibility — PASS

Command:

```powershell
python .runtime/block_cave/qa_stage3_strip_pay.py
```

`build_strip(20261117, BASE_COUNTS)` / `build_strip(20261118, FREE_COUNTS)` were
called directly from `game_config.py` and re-executed.

| Check | Value |
| --- | --- |
| Base strip SHA-256 | `7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451` |
| Free strip SHA-256 | `f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754` |
| Length (both) | 200 |
| Base counts vs `BASE_COUNTS` | match |
| Free counts vs `FREE_COUNTS` | match |
| Deterministic (re-run == first) | true for both |

Both SHA-256 values match the documented values in `MATH_DESIGN.md` §4.1/§4.2
and in the report header. **PASS.**

## 2. Task 2 — Paytable == §3.1 — PASS

Same script, second section. All **9 symbols × 9 cluster-size values** were
compared against the `MATH_DESIGN.md` §3.1 tables.

- `_COMMON_PAYS` (`earth/stone/timber/copper`), `_PREMIUM_PAYS`
  (`silver/gold/emerald/diamond`) and `_INGOT_PAYS` (`ingot`) match §3.1 exactly
  (e.g. `earth` = `[0.18, 0.28, 0.46, 0.74, 1.10, 1.65, 2.76, 4.60, 7.35]`).
- The config is **NOT** the ×F-scaled version. `F = 1.8382663803148458` would
  make `earth` = `[0.33, 0.51, 0.85, 1.36, 2.02, 3.03, 5.07, 8.46, 13.51]`;
  the config value is `[0.18, 0.28, 0.46, 0.74, 1.10, 1.65, 2.76, 4.60, 7.35]`.
  `config is xF-scaled? False`.
- `build_pay_group()` produces **81** `(range, symbol)` source keys; the
  expanded `convert_range_table` paytable has **234** keys (report §5 is
  consistent).
- `PAY_RANGES` = `[(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,14),(15,19),(20,30)]`
  → 26 cluster sizes. All pay_group values numeric.

**PASS.**

## 3. Task 3 — Independent measurement (100k natural + 5k forced freegame) — PASS

Command:

```powershell
python math/games/block_cave/calibrate.py --natural 100000 --freegame 5000 --label qa_stage3 --out .runtime/block_cave/qa_stage3.json --no-progress
```

Independent run (not trusting the report). Output: `.runtime/block_cave/qa_stage3.json`.

| Metric | QA independent (100k) | Orchestrator (200k) | Report (500k) |
| --- | --- | --- | --- |
| Natural base-game RTP | **0.96195** | 0.96435 | 0.96480 |
| base contribution | 0.89808 | 0.89753 | 0.89453 |
| feature contribution | 0.06388 | 0.06682 | 0.07027 |
| RTP std | 2.3869 | 2.0766 | 1.9402 |
| Visible hit `P(payout>0)` | 0.69861 | 0.69956 | 0.69849 |
| Full return `P(payout>=1.0×)` | 0.29146 | 0.29159 | 0.29104 |
| Feature entry rate | 0.00660 (660/100000) | 0.00674 (1348/200000) | 0.00704 (3521/500000) |
| Feature duration mean / median / max | 8.55 / 8.0 / 24 | 8.67 / 8.0 / 28 | 8.73 / 8.0 / 36 |
| Feature payout mean / median | 9.68 / 7.63 | 9.91 / 7.87 | 9.98 / 7.86 |
| Round max observed | 544.43 | 544.43 | 544.43 |
| `P(>=100×)` / `P(>=500×)` / `P(>=1000×)` | 1e-5 / 1e-5 / 0 | 5e-6 / 5e-6 / 0 | 6e-6 / 2e-6 / 0 |
| `wincap` binds | 0 | 0 | 0 |
| Consistency violations | 0 / 100000 | 0 / 200000 | 0 / 500000 |

The QA point estimate **0.96195** is inside the 96.0–96.7% band and within the
normal sampling error of both the orchestrator (0.96435) and the report
(0.96480). All tail, feature and consistency metrics agree within noise. The
100k RTP 95% CI is `[0.9472, 0.97675]`, which straddles the 96.0% lower edge —
the same behaviour the report itself flags for the 500k run (`[0.9594, 0.9702]`).
This is an honest property of a heavy-tailed distribution, not a defect.

**PASS.** The report's central claim (≈0.965 in band) is reproducible.

## 4. Task 4 — Book / lookup invariants — PASS

`run.py` was executed (writes `math/.runtime/block_cave/prototype_books.jsonl`).
The invariant checker `.runtime/block_cave/qa_stage3_book.py` loaded all **60**
books:

```
Loaded 60 books ...
NO violations across 60 books
```

Checked invariants (all held):
- `payoutMultiplier` is an `int` in `[0, 100000]`.
- Event `index` values are contiguous from 0.
- First event is `reveal`.
- `finalWin` amount == `payoutMultiplier`.
- `int(round(min(base + free, 1000.0) * 100, 0))` == `payoutMultiplier`
  (base+free sum-then-cap).
- `baseGameWins` / `freeGameWins` non-negative.

Observed event types: `reveal, winInfo, setWin, setTotalWin, updateTumbleWin,
tumbleBoard, oreVeinUpgrade, freeSpinTrigger, updateFreeSpin, freeSpinEnd,
finalWin`. **PASS.**

## 5. Task 5 — `test_block_cave` 11/11 incl. wincap + ore-vein — PASS

Command:

```powershell
python math/games/block_cave/test_block_cave.py
```

Result: **`11/11 tests passed`**.

`test_wincap_ore_vein_upgrade` (lines 422–503) was inspected directly and
asserts:
- Event order `updateTumbleWin < wincap < oreVeinUpgrade` (line 466).
- `wincap` amount `== WINCAP_UNITS` (`100000`) (line 471).
- `veinPositions == [{"reel": 1, "row": 1}]` and `upgrades ==
  [{"reel": 1, "row": 2, "symbol": "diamond"}]` (lines 478–479).
- The cascade **stops** after wincap (`"tumbleBoard" not in types`, line 483).
- `setTotalWin` / `finalWin` / `payoutMultiplier` all `== WINCAP_UNITS` (lines
  497–499), and book invariants still hold (line 501).

This confirms the report §5 claim and the event-ordering contract. **PASS.**

## 6. Task 6 — `pip check` + upstream pytest — PASS

```powershell
python -m pip check          # -> No broken requirements found.
python -m pytest tests\win_calculations -q   # -> 13 passed in 0.06s
```

**PASS.**

## 7. Task 7 — Report consistency vs `.runtime` corpus — PASS

Cross-checked the report's numbers against the actual measurement JSON files:

- **§4.2 Post-calibration** (RTP 0.9648, visible 0.6985, full return 0.2910,
  entry 0.00704, feature duration 8.73/max 36, feature payout 9.98/7.86/max
  105.82, `P(>=100×)=6e-6`, `P(>=500×)=2e-6`, `wincap` 0, violations 0) matches
  `calib_md_post.json` (500k natural + 20k forced).
- **§8 Post run** (RTP 0.9590, base 0.8970, feature 0.0620, visible 0.6982, full
  0.2883, entry 0.0063, max 544.43, wincap 0, violations 0) matches
  `calib_post.json` (50k natural + 5k forced).
- **§4.1 Pre-calibration** (RTP 1.7577, base 1.6538, feature 0.1039, visible
  0.6954, full 0.4474, entry 0.00583, feature payout 17.81/14.32, round
  p50/p90/max 0.85/4.52/1000.0, wincap bind 1) matches `calib_confirm.json`
  (30k natural + 3k forced, ×F baked table).
- **§7.4 Ore-vein contribution** (enabled 0.9640 vs disabled 0.9764, Δ ≈
  −1.24pp) matches `calib_ore_enabled.json` / `calib_ore_disabled.json` (150k
  each).
- **§5** `make_config(1.0)` reproduces the §3.1 paytable (234 expanded keys).

**PASS.**

---

## Independent confirmation beyond the listed tasks

To avoid only re-running the author's own harness, two extra checks were done.

### A. Ore-vein upgrade contribution (seed-matched, 150k enabled/disabled)

```
python math/games/block_cave/calibrate.py --natural 150000 --freegame 0 --label qa_ore_enabled  --out .runtime/block_cave/qa_ore_enabled.json  --no-progress
python math/games/block_cave/calibrate.py --natural 150000 --freegame 0 --label qa_ore_disabled --out .runtime/block_cave/qa_ore_disabled.json --no-progress --disable-ore-vein
```

| Metric | Enabled (150k) | Disabled (150k) |
| --- | --- | --- |
| Natural base-game RTP | 0.96398 | 0.97636 |
| base contribution | 0.89739 | 0.91079 |
| feature contribution | 0.06658 | 0.06557 |
| Visible hit | 0.69895 | 0.69895 |
| Feature entry | 0.006747 (1012/150000) | 0.006747 (1012/150000) |

Δ = 0.97636 − 0.96398 = **−1.24pp**, exactly the report §7.4 claim. The two runs
are **seed-matched** (identical 1012 feature entries, identical visible hit),
confirming the comparison is like-for-like. **Confirmed.**

### B. Board-draw scatter entry `P(>=3 pickaxes)` over 200k boards

`python .runtime/block_cave/qa_stage3_scatter.py` drew 200,000 boards directly
(`draw_board` + `count_special_symbols("scatter")`):

```
Boards drawn: 200000
P(>=3 pickaxes) = 0.006875  (1375/200000)
Binomial approx P(Binomial(30, 0.015)>=3) = 0.010127
```

The empirical per-board scatter rate **0.006875** is close to the measured
feature-entry rate (≈0.0066–0.0070) and below the binomial approximation
0.010127 — consistent with the report §7.3 (open conflict #3). **Confirmed.**

### C. Determinism

Two identical `--natural 2000 --freegame 200` runs (`.runtime/block_cave/qa_det_a.json`,
`qa_det_b.json`) produced numerically identical output (RTP 0.88087, base
0.83599, feature 0.04488, visible 0.697, full 0.2735, entry k=8, max 30.47),
differing only in `runtime_seconds`. **Confirmed.** *(Minor: both files carry the
label `qa_det_a`; the `--label` for the second run was not updated. Cosmetic only.)*

---

## Findings

All findings are **minor / informational**. None blocks the calibration result.

### F1 (INFO) — RTP standard deviation is heavy-tail sensitive
The sample std is noisy at finite n and is driven by the single largest round.
My 100k std = **2.3869**, orchestrator 200k = **2.0766**, report 500k = **1.9402**.
The largest observed round (544.43×) appears in every sample and inflates the
estimate more at smaller n. Consequently the report's CI
(`SE = std / √n`, giving `[0.9594, 0.9702]` at 500k) is a normal-approximation
that uses a heavy-tail sample std as its input, so the CI width is itself only
approximate. The report already discloses the CI caveat (§9) and does not
overstate the result, so this is informational.

### F2 (INFO) — `calib_ore_test.json` is an orphan artifact
`.runtime/block_cave/calib_ore_test.json` reports `ore_vein_enabled=False`,
`n=3000`, **RTP 0.48932**, max 16.57. This is inconsistent with
`calib_ore_disabled.json` (RTP 0.97636 at 150k) and appears to have been
produced against the pre-revert, lower paytable. It is **not referenced** by
`CALIBRATION_REPORT.md`. Recommend deleting it (or clearly relabelling it) to
avoid it being mistaken for a §7.4 measurement.

### F3 (INFO) — report §3 rounds `calib_pre` slightly
Report §3 states `measured_pre_rtp = 0.524`; `calib_pre.json` actually records
**RTP 0.52527** (500k natural). Minor rounding; the conclusion (a 0.52 RTP is
implausible and must not be used as a scale factor) is unaffected.

### F4 (INFO) — natural vs forced feature statistics are implicit
Report §4.2 lists feature duration mean 8.73 / max 36 and feature payout mean
9.98 / median 7.86 / max 105.82. These are the **natural** features (3,521
entries) in `calib_md_post.json`; the **forced** freegame sample (20,000) shows
duration mean 8.50 / max 44 and payout mean 9.69 / max 120.42. The report
correctly separates natural and forced in its method (§2), but the table does not
label which sample produced the feature row. The distinction is implicit, not
explicit; the natural numbers are the correct ones for feature internal
statistics, so this is a clarity note only.

### F5 (INFO) — determinism artifacts share a label
`qa_det_a.json` / `qa_det_b.json` both have `label: "qa_det_a"`. Cosmetic; does
not affect the determinism conclusion (numeric fields identical).

---

## Reproduction steps (summary)

```powershell
# Task 1/2 — strip + paytable
python .runtime/block_cave/qa_stage3_strip_pay.py

# Task 3 — independent 100k/5k measurement
python math/games/block_cave/calibrate.py --natural 100000 --freegame 5000 --label qa_stage3 --out .runtime/block_cave/qa_stage3.json --no-progress

# Task 4 — books + invariants
python math/games/block_cave/run.py
python .runtime/block_cave/qa_stage3_book.py

# Task 5 — tests
python math/games/block_cave/test_block_cave.py

# Task 6 — pip + pytest
python -m pip check
python -m pytest tests\win_calculations -q

# Extra: ore-vein contribution (seed-matched)
python math/games/block_cave/calibrate.py --natural 150000 --freegame 0 --label qa_ore_enabled  --out .runtime/block_cave/qa_ore_enabled.json  --no-progress
python math/games/block_cave/calibrate.py --natural 150000 --freegame 0 --label qa_ore_disabled --out .runtime/block_cave/qa_ore_disabled.json --no-progress --disable-ore-vein

# Extra: scatter board-draw rate
python .runtime/block_cave/qa_stage3_scatter.py
```

## Evidence artifacts

- `.runtime/block_cave/qa_stage3.json` — independent 100k/5k measurement
- `.runtime/block_cave/qa_ore_enabled.json`, `qa_ore_disabled.json` — ore-vein
  seed-matched 150k comparison
- `.runtime/block_cave/qa_det_a.json`, `qa_det_b.json` — determinism runs
- `.runtime/block_cave/qa_stage3_strip_pay.py`, `qa_stage3_book.py`,
  `qa_stage3_scatter.py` — QA verification scripts
- `math/.runtime/block_cave/prototype_books.jsonl` — 60-book `run.py` output
- Reference corpus: `calib_md_post.json`, `calib_post.json`,
  `calib_confirm.json`, `calib_ore_enabled.json`, `calib_ore_disabled.json`,
  `orchestrator_200k.json`

## Limitations

- All figures are **DEV measurements** on the unpublished prototype. This review
  makes **no production RTP claim** and does not certify the game.
- The RTP "in band" result is a **point estimate**. Both the report's 500k CI
  `[0.9594, 0.9702]` and this review's 100k CI `[0.9472, 0.97675]` straddle the
  96.0% lower edge; this is documented, not hidden.
- The report's ore-vein SE claim ("≈2.3 SE at 150k") was not independently
  re-derived from per-round data; only the direction and magnitude (−1.24pp) were
  confirmed.
- Visual/Playwright QA is **not applicable** here: no Block Cave frontend exists
  yet (Stage 6). This review is purely math/engine validation.
