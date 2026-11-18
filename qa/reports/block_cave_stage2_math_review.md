# Block Cave — Stage 2 Math Prototype: Independent QA Review

**Reviewer:** Independent QA agent (not the math author)
**Date:** 2026-11-17
**Scope:** `math/games/block_cave/` Stage 2 math prototype
**Verdict:** **PASS WITH FINDINGS** — all six mechanics, strip reproducibility, prototype books, config/rules and off-limits integrity verified; two LOW/MEDIUM findings and scoping notes; no blocking defect in the Stage 2 prototype.

---

## 1. Scope and method

This is an **independent** QA pass over the Stage 2 math prototype for the
Block Cave game. It does not trust the author's own test assertions; mechanics
were re-verified by dumping actual generated book events and the design
algorithm was re-implemented from scratch rather than by importing the author's
`game_config.py`.

**No implementation file was modified.** Only `qa/reports/block_cave_stage2_math_review.md`
(the report) was written. The author's `math/games/block_cave/`, `math/src/`,
`math/games/0_0_cluster/`, `docs/`, `frontend/`, `qa/`, `opencode.jsonc` and
`frontend/pnpm-lock.yaml` were left untouched.

Verification used the project venv interpreter and was run from the repo root:

- Python: `C:\Users\robin\Documents\stake\stake-game-ai\math\.venv\Scripts\python.exe`
- `PYTHONPATH=math\games\block_cave;math` for scripts that import the game modules.

Independent re-verification scripts were kept outside the repo (temp dir,
reusable evidence):
`bc_verify_strips.py`, `bc_verify_mechanics.py`, `bc_verify_books.py`,
`bc_verify_config.py`, `bc_verify_natural.py`.

> **Visual QA is NOT applicable at this stage.** There is no Block Cave
> frontend yet — a recursive search under `frontend/` found no `block_cave`
> directory or file. The "loaded Pixi canvas / completed Action" visual check
> is a **Stage 3** concern once the frontend replay exists. Nothing was
> asserted about a canvas here.

---

## 2. Environment and commands run (with outputs)

### 2.1 Author's test suite

```
& "...\math\.venv\Scripts\python.exe" math\games\block_cave\test_block_cave.py
```

```
  [ok] strips reproduce documented SHA-256 + counts
  [PASS] test_strip_shas
  [ok] book invariants across 9 spins (basegame/freegame/0)
  [PASS] test_book_invariants
  [ok] win emits winInfo -> setWin -> setTotalWin (earth 6-cluster)
  [PASS] test_win_event_sequence
  [ok] tumble: 2 winInfo with tumbleBoard between (seed 3)
  [PASS] test_tumble_between_wins
  [ok] ore-vein upgrade converts 1 eligible adjacent block to diamond
  [PASS] test_ore_vein_upgrade_with_target
  [ok] ore-vein activation with no eligible target => veinPositions only
  [PASS] test_ore_vein_upgrade_no_target
  [ok] 3 pickaxes trigger freeSpinTrigger totalFs=8, 8 free reveals on FR0
  [PASS] test_three_pickaxe_trigger
  [ok] natural trigger at basegame seed 236, totalFs=8
  [PASS] test_natural_trigger
  [ok] retrigger clamps total free spins to 60
  [PASS] test_retrigger_clamp
  [ok] 1000x cap clamps setTotalWin/finalWin/payoutMultiplier to 100000
  [PASS] test_wincap

10/10 tests passed.
```

### 2.2 Prototype run (`run.py`)

```
$env:PYTHONPATH = "math\games\block_cave;math"
& "...\python.exe" math\games\block_cave\run.py
```

```
Rounds: 60
Total payoutMultiplier units: 7735 (mean 128.92)
baseGameWins: 19.28, freeGameWins: 58.07
Hit (payoutMultiplier > 0): 34 (56.7%)
Max payoutMultiplier: 2132
Free-spin trigger rounds: 10
DEV observation only - NOT a measured RTP and NOT a confirmed hit frequency.
Wrote books to C:\Users\robin\Documents\stake\stake-game-ai\math\.runtime\block_cave\prototype_books.jsonl
```

The run **completed without hanging** and wrote the 60-book JSONL. The
`DEV observation only` disclaimer is correctly printed. Note the disclaimer
appears in `run.py` stdout but **not** inside the JSONL file (see finding F3).

### 2.3 Independent verification scripts

All scripts re-ran cleanly; full outputs are quoted inline in §3 and §4.

---

## 3. Requirement verification

### 3.1 Strip reproducibility — **PASS**

The design's `build_strip(seed, counts)` algorithm was **re-implemented
independently** (not imported from `game_config.py`) and executed.

```
base length: 200      base SHA: 7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451
free length: 200      free SHA: f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754
base MATCH: True      free MATCH: True
base deterministic: True   free deterministic: True
```

Counts match §4.1 / §4.2 weight tables exactly (base `earth 36 … pickaxe 3`,
free `earth 30 … pickaxe 3`), each total 200. **F2 (strip reproducibility)
remains resolved.**

### 3.2 Six mechanics — all **GENUINELY** verified (real event data)

These were verified by inspecting actual emitted events, not by trusting the
test's assertions.

**Mechanic 1 — Win (`winInfo → updateTumbleWin → setWin → setTotalWin`).**
Earth 6-cluster, win 15:
```
reveal → winInfo → updateTumbleWin(15) → oreVeinUpgrade → tumbleBoard → setWin(15) → setTotalWin(15) → finalWin(15)
payoutMultiplier 15, baseGameWins 0.15
```
`winInfo.totalWin=15`, `payoutMultiplier=15`, `setWin/setTotalWin/finalWin=15`.

**Mechanic 2 — Tumble (≥2 `winInfo` with `tumbleBoard` between).** Seed 3:
```
reveal → winInfo → updateTumbleWin(42) → oreVeinUpgrade → tumbleBoard → winInfo → updateTumbleWin(54) → oreVeinUpgrade → tumbleBoard → setWin(54) → setTotalWin(54) → finalWin(54)
```
Two `winInfo` events with `tumbleBoard` between; `tumbleBoard` removed 7 then 5
symbols. Tumble is real and re-scores the post-fall board.

**Mechanic 3a — Ore-vein upgrade WITH target.**
```
reveal → winInfo → updateTumbleWin(15) → oreVeinUpgrade
oreVeinUpgrade: {"veinPositions":[{"reel":1,"row":1}], "upgrades":[{"reel":1,"row":2,"symbol":"diamond"}]}
board[1][1].name after: diamond
```
A winning vein at `(reel 1, row 1)` converted an eligible orthogonal neighbour
`(reel 1, row 2)` to `diamond`. Placement is between `updateTumbleWin` and
`tumbleBoard`, per design §8.

**Mechanic 3b — Ore-vein upgrade NO target.**
```
oreVeinUpgrade: {"veinPositions":[{"reel":1,"row":2}], "upgrades":[]}
```
The vein is still recorded, with an empty `upgrades` list when no eligible
target exists. Matches the "always recorded, even if nothing converted" rule.

**Mechanic 4 — Three-pickaxe trigger.** `freeSpinTrigger.totalFs=8`,
`positions` = the 3 initial pickaxes, followed by exactly **8** `reveal` events
with `gameType: freegame` (on FR0), then `freeSpinEnd(amount 614, winLevel 3)`
and `finalWin`. Trigger fires naturally at basegame seed 236 (see 3.3).

**Mechanic 5 — Retrigger clamp (§6.4).**
- 55 + 3-pickaxe retrigger ⇒ `tot_fs = 60` (clamped).
- 50 + 8-pickaxe (count clamped to 6 → +16) ⇒ `tot_fs = 60`.
- `freeSpinRetrigger` emitted with `totalFs: 60`.

**Mechanic 6 — 1,000× cap.** `wincap` triggered mid-cascade:
```
reveal → winInfo → updateTumbleWin(12500) → wincap(100000) → setTotalWin(100000) → finalWin(100000)
payoutMultiplier: 100000
```
`setTotalWin`, `finalWin` and `payoutMultiplier` all clamp to `100000`
(= 1000× × 100 units). The `wincap` event is emitted between
`updateTumbleWin` and `setTotalWin`, matching design §8 (not at the end).

### 3.3 Natural triggering + initial-board-only counting — **PASS**

Natural trigger found at basegame seed **236**: the initial reveal already has
3 pickaxes; `freeSpinTrigger.totalFs=8` positions exactly equal the initial
reveal pickaxe positions; `force_freegame` is `False` for the basegame
distribution.

Initial-board-only counting confirmed with a constructed board that had
**0** initial pickaxes but **1** pickaxe tumbled in later:
```
initial_scatter_count before cascade: 0
special_syms_on_board scatter after cascade: 1
initial_scatter_count still: 0
check_fs_condition: False
check_freespin_entry: False
```
Scatter counting is evaluated on the **initial** board only (§6.1/§6.2).

`check_repeat` confirmed **not** forcing a non-zero win for non-`"0"` criteria:
a zero-win basegame round leaves `repeat = False`.

### 3.4 Prototype books — **PASS**

`math\.runtime\block_cave\prototype_books.jsonl` (329,115 bytes, 60 lines):
- **60 books** — 40 `basegame`, 10 `freegame`, 10 `"0"` (criteria counts
  `Counter({'basegame': 40, 'freegame': 10, '0': 10})`).
- Event indexes contiguous from 0; first event `reveal`; book id 0..59.
- `payoutMultiplier` is an `int` in `[0, 100000]` and equals `finalWin`.
- Cascade order per design §8:
  `winInfo → updateTumbleWin → [wincap] → oreVeinUpgrade → tumbleBoard`
  then `setWin → setTotalWin`.
- Free-spin group repeats; closes with `freeSpinEnd → finalWin`.
- `oreVeinUpgrade` payload `{index,type,veinPositions:[{reel,row}],
  upgrades:[{reel,row,symbol}]}` with padded `row` (+1) and
  `len(upgrades) <= len(veinPositions)`.
- `oreVeinUpgrade` events total **103**; `wincap` events total **0**.
- `max payoutMultiplier = 2132` (21.32×), `min 0`, **34** books with payout > 0.
- Independent `bc_verify_books.py` reported **`ISSUES: none`**.

First book (id 0) `reveal` board shows 6 reels × 7 board rows (visible rows
1–5 + padding rows 0 and 6), `paddingPositions` present, `include_padding=True`,
consistent with design §8.

### 3.5 Config and rules — **PASS**

`bc_verify_config.py`:
```
game_id: block_cave    num_reels: 6    num_rows: [5,5,5,5,5,5]    include_padding: True
win_type: cluster    wincap: 1000.0    rtp: 0.963
special_symbols: {'wild': ['ore_vein'], 'scatter': ['pickaxe']}
freespin_triggers: {'basegame': {3:8,4:12,5:16,6:16}, 'freegame': {3:8,4:12,5:16,6:16}}
anticipation_triggers: {'basegame': 2, 'freegame': 2}
reels keys: ['BR0', 'FR0']     BR0/FR0: 6 reels each length 200
PAYTABLE ERRORS: none
```
11 symbols; no paying entries for `ore_vein`/`pickaxe`. Paytable matches §3.1
(small-cluster→large-cluster values, `ingot` top row 125.00). `rtp=0.963` is a
design target only — **not claimed as measured**.

### 3.6 Off-limits integrity — **PASS** (timestamp-based; no git repo)

The repo is **not a git repository**, so no byte-level baseline/diff exists.
The check is **timestamp-based** plus the `.setup-backup` snapshot (which holds
only frontend). Evidence:

| Path | LastWriteTime | Assessment |
|---|---|---|
| `math/src/` source files | 14:45:09 (setup) | unchanged during Stage 2 |
| `math/src/**/__pycache__/*.pyc` | 15:53:43 (setup smoke) | compiled during setup, pre-Stage-2 |
| `math/games/0_0_cluster/` | all 14:45:09 | unchanged |
| `opencode.jsonc` | 16:08:50 | unchanged |
| `frontend/pnpm-lock.yaml` | 17:15:32 | unchanged |
| `docs/ENGINE_CONTRACT.md` | 15:21:08 | earlier |
| `docs/SETUP.md`, `docs/CHANGES.md`, `docs/TEST_REPORT.md` | 18:48–18:52 | earlier |
| `docs/DESIGN_SYSTEM.md` | 20:50:10 | earlier |
| `docs/GAME_SPEC.md`, `docs/PROJECT_PLAN.md` | 22:31:00 / 22:31:47 | planning docs (pre-implementation) |
| `docs/STATUS.md` | 22:38:08 | orchestrator-owned status note (expected) |
| `math/games/block_cave/*.py` implementation | 22:38–22:43 | the Stage 2 work |

All off-limits implementation/shared files predate the Stage 2 implementation
(22:36–22:43). `math/src/` source files were **not** modified during Stage 2.
`docs/` updates are planning/status docs, not engine or shared-lockfile
changes. **Limitation:** without git, this is timestamp inference, not a
byte-diff, for `math/src/`, `0_0_cluster/` and `docs/`.

---

## 4. Author-flagged risks — assessment

The math author flagged three risks; all three are **confirmed and acceptable
for the Stage 2 prototype**, with caveats.

**(a) `wincap` criteria never converges → `run.py` uses a manual deterministic loop.**
**CONFIRMED.** The config's `wincap` distribution sets `criteria="wincap"`,
`win_criteria=1000.0`, `force_wincap=True`, `force_freegame=True`. A grep shows
`force_wincap` is **never consumed by any runtime engine logic** (it appears only
in `game_config.py` files, `docs`, and `src/config/distributions.py` as a default
— never in `state.py`/`executables.py`/`board.py`). `check_repeat` compares
`final_win` to `win_criteria` (1000.0), which is essentially unreachable on the
design strips (max observed 21.32×); `check_current_repeat_count` only *warns*
every 1000 repeats and does not terminate. **Running `criteria="wincap"` through
the normal repeat-until-criteria loop would loop indefinitely.**
`run.py` correctly avoids the `wincap` criteria (it runs only `basegame`,
`freegame`, `"0"`), and the cap is exercised deterministically by
`test_wincap` (constructing the board directly). **Acceptable for the prototype,
but see finding F1.**

**(b) `force_freegame` branch preserved in `draw_board`.**
**CONFIRMED** and **legitimate.** `game_override.draw_board` keeps the
`force_freegame` re-draw/force-special branch (lines 34–39) used by criteria
that require a specific scatter count (the `freegame` and `wincap`
distributions set `force_freegame=True`). The base-game threshold re-draw
suppression loop was removed, enabling natural triggering. The forced-freegame
branch is exercised by `run.py`'s `freegame` seeds.

**(c) Books written to `math\.runtime\block_cave\`.**
**CONFIRMED.** `run.py` writes to `ROOT / ".runtime" / "block_cave"` where
`ROOT = Path(__file__).resolve().parents[2]` = `math/`, i.e.
`math\.runtime\block_cave\prototype_books.jsonl` (confirmed by the printed path).
This is a development-only runtime location, not a published book store.

---

## 5. Findings

### F1 — `wincap` bet-mode distribution can never converge (MEDIUM, latent)
- **Severity:** MEDIUM (latent hazard for downstream tooling; not triggered by
  the prototype's own `run.py`).
- **Location:** `math/games/block_cave/game_config.py` lines 213–226 (`wincap`
  distribution: `criteria="wincap"`, `win_criteria=1000.0`, `force_wincap=True`).
- **Reproduction:** Any consumer that iterates `GameConfig.bet_modes`
  distributions and runs the `wincap` criteria through the normal
  repeat-until-criteria loop will re-draw forever. `force_wincap` is not
  consumed by engine logic, so nothing forces the win; `check_repeat` keeps
  `repeat=True` because `final_win != 1000.0`; `check_current_repeat_count`
  only warns at 1000/2000/… and never breaks.
- **Evidence:** `grep force_wincap` shows consumption nowhere in runtime code;
  `run.py` docstring and the design §7/F4/F18 acknowledge it; `run.py` excludes
  the criteria.
- **Recommendation:** Keep it out of `run.py` (already done), but either remove
  the `wincap` distribution from `bet_modes` until the cap is reachable, or add
  a guard so downstream tooling never tries to converge on it. Document that a
  full simulation/optimization run must exclude the `wincap` criteria.

### F2 — `oreVeinUpgrade` could be emitted after `wincap` with no following `tumbleBoard` (LOW, theoretical)
- **Severity:** LOW (theoretical; unreachable in practice).
- **Location:** `math/games/block_cave/game_executables.py` lines 27–31
  (`emit_tumble_win_events` calls `process_ore_vein_upgrades()` unconditionally
  after `evaluate_wincap()`).
- **Reproduction:** If a cascade crosses the cap, `evaluate_wincap()` sets
  `wincap_triggered` and the cascade stops (no `tumbleBoard`), yet
  `process_ore_vein_upgrades()` still runs and could emit an `oreVeinUpgrade`
  after the `wincap` event, producing `updateTumbleWin → wincap → oreVeinUpgrade`
  with no subsequent `tumbleBoard`.
- **Evidence:** Not observed — the generated books contain **0** `wincap` events
  (cap unreachable naturally; max 21.32×). The `test_wincap` board had no
  eligible vein on the winning cascade, so no `oreVeinUpgrade` was emitted there.
- **Recommendation:** Guard `process_ore_vein_upgrades()` behind
  `if not wincap_triggered` for strict §8 ordering, or explicitly document the
  allowed `wincap → oreVeinUpgrade` (no `tumbleBoard`) sequence in §8.

### F3 — Books JSONL does not carry the "DEV observation" label (INFO)
- **Severity:** INFO (cosmetic / traceability).
- **Location:** `math/.runtime/block_cave/prototype_books.jsonl`.
- **Details:** The "DEV observation only - NOT a measured RTP..." disclaimer
  appears in `run.py` stdout but is not embedded in the JSONL. A downstream
  reader of the file alone cannot tell it is a dev sample.
- **Recommendation:** (Optional) add a top-level `note`/`devOnly` field to each
  book or a manifest line, so the file is self-describing.

### F4 — `oreVeinUpgrade` and `wincap` are new event types for the frontend (INFO, Stage 3)
- **Severity:** INFO (forward-looking; not a Stage 2 blocker).
- **Location:** `math/games/block_cave/game_executables.py` /
  `game_events.py` (emit `oreVeinUpgrade`), design §8, and the cluster
  `frontend/apps/lines/src/game/bookEventHandlerMap.ts` / `typesBookEvent.ts`.
- **Details:** `oreVeinUpgrade` and `wincap` are **not** in the cluster
  `BookEvent` union / handler map. The frontend must add both a union member and
  a handler branch (already AGREED WITH CORRECTIONS by the frontend agent:
  A/B/C). Since no Block Cave frontend exists yet, this is correctly deferred to
  Stage 3. **No frontend union/handler change is present now** (expected).

### F5 — No measured RTP / hit rate (INFO, correctly disclaimed)
- **Severity:** INFO.
- **Details:** `run.py` reports a dev-sample mean (128.92 units) and 56.7% hit
  from 60 seeded rounds. This is a **conditional development sample**, not a
  measured RTP or hit frequency, and is correctly disclaimed both in code and in
  `docs/STATUS.md`. `rtp=0.963` in config is a design target only.

---

## 6. Verdict

**PASS WITH FINDINGS.**

- All **six mechanics** are genuinely verified against real emitted events, not
  test assertions: win, tumble, ore-vein upgrade (with and without target),
  three-pickaxe trigger, retrigger clamp, and the 1,000× cap.
- **Strip reproducibility** is confirmed (independent re-implementation; both
  SHA-256 values and all counts match §4.1/§4.2).
- **Prototype books** (60) are structurally valid, ordered, in-bounds, and
  reproduce the design cascade sequence; the cap is correctly never hit
  naturally (0 `wincap` events, max 21.32×).
- **Config & rules** match the design (6×5 cluster, wincap 1000, paytable,
  special symbols, trigger scaling, anticipation).
- **Off-limits integrity** is clean (no modification of `math/src/`,
  `0_0_cluster/`, `opencode.jsonc`, `frontend/pnpm-lock.yaml` during Stage 2).
- All three author-flagged risks are confirmed and handled for the prototype.

No blocking defect prevents the Stage 2 prototype from being accepted. **F1**
(the never-converging `wincap` distribution) should be resolved or explicitly
excluded from any downstream optimization/production run before Stage 3. **F2**
and **F3** are LOW/INFO. **F4** is the expected Stage 3 math/frontend contract
work; **F5** is correctly disclosed.

### Limitations of this review
- No git repo ⇒ off-limits check for `math/src/`, `0_0_cluster/`, `docs/` is
  timestamp-based, not a byte-diff.
- The 60-round prototype is a deterministic dev sample; it does **not** measure
  RTP, hit frequency, feature rate or bonus payout. Those remain unclaimed.
- Visual QA (Pixi canvas + completed Action) is **not applicable** — no Block
  Cave frontend exists yet.

---

# Addendum — F1 fix re-verification (2026-11-17)

**Re-reviewer:** Independent QA agent (not the math author)
**Trigger:** The math author addressed finding **F1** (non-convergent `wincap`
bet-mode criteria distribution) by modifying `math/games/block_cave/game_config.py`
(removed the `wincap` distribution, re-normalized quotas) and
`math/games/block_cave/run.py` (docstring only). This addendum re-runs the
affected checks. **No implementation file was modified by QA; only this report.**

## Commands run and outputs

### 1. Test suite — **10/10 PASS**

```
& "C:\Users\robin\Documents\stake\stake-game-ai\math\.venv\Scripts\python.exe" math\games\block_cave\test_block_cave.py
```

```
  [ok] strips reproduce documented SHA-256 + counts
  [PASS] test_strip_shas
  [ok] book invariants across 9 spins (basegame/freegame/0)
  [PASS] test_book_invariants
  [ok] win emits winInfo -> setWin -> setTotalWin (earth 6-cluster)
  [PASS] test_win_event_sequence
  [ok] tumble: 2 winInfo with tumbleBoard between (seed 3)
  [PASS] test_tumble_between_wins
  [ok] ore-vein upgrade converts 1 eligible adjacent block to diamond
  [PASS] test_ore_vein_upgrade_with_target
  [ok] ore-vein activation with no eligible target => veinPositions only
  [PASS] test_ore_vein_upgrade_no_target
  [ok] 3 pickaxes trigger freeSpinTrigger totalFs=8, 8 free reveals on FR0
  [PASS] test_three_pickaxe_trigger
  [ok] natural trigger at basegame seed 236, totalFs=8
  [PASS] test_natural_trigger
  [ok] retrigger clamps total free spins to 60
  [PASS] test_retrigger_clamp
  [ok] 1000x cap clamps setTotalWin/finalWin/payoutMultiplier to 100000
  [PASS] test_wincap

10/10 tests passed.
```

`test_wincap` still passes, i.e. the 1,000× cap path is still exercised
deterministically via a constructed board.

### 2. `run.py` — **completes without hanging, writes books**

```
$env:PYTHONPATH = "math\games\block_cave;math"
& "...\python.exe" math\games\block_cave\run.py
```

```
Rounds: 60
Total payoutMultiplier units: 7735 (mean 128.92)
baseGameWins: 19.28, freeGameWins: 58.07
Hit (payoutMultiplier > 0): 34 (56.7%)
Max payoutMultiplier: 2132
Free-spin trigger rounds: 10
DEV observation only - NOT a measured RTP and NOT a confirmed hit frequency.
Wrote books to C:\Users\robin\Documents\stake\stake-game-ai\math\.runtime\block_cave\prototype_books.jsonl
```

Identical output to the pre-fix run; completed without hanging.

### 3. F1 footgun — **REMOVED (resolved)**

Inspection of the live config (`GameConfig().bet_modes[0].get_distributions()`):

```
num distributions: 3
  criteria=basegame   quota=0.6316 win_criteria=None  reel_weights {'basegame':{'BR0':1},'freegame':{'FR0':1}}  scatter None  force_wincap False  force_freegame False
  criteria=freegame   quota=0.2105 win_criteria=None  reel_weights {'basegame':{'BR0':1},'freegame':{'FR0':1}}  scatter {3:10}       force_wincap False  force_freegame True
  criteria=0          quota=0.1579 win_criteria=0.0   reel_weights {'basegame':{'BR0':1},'freegame':{'FR0':1}}  scatter None  force_wincap False  force_freegame False
criteria list: ['basegame', 'freegame', '0']
quota sum: 1.000000
win_criteria list: [None, None, 0.0]
wincap config value: 1000.0
```

- **No** distribution with `criteria="wincap"` or `win_criteria=1000.0` remains.
  A repo-wide grep of `math/games/block_cave/` for `criteria="wincap"` /
  `win_criteria = 1000` found only `test_block_cave.py` (the `test_wincap`
  assertion) and the explanatory comment in `game_config.py` line 175.
- Surviving criteria are exactly `['basegame','freegame','0']`.
- Quotas sum to **1.000000**; no deviation to document. The re-normalized values
  preserve the original 0.6 : 0.2 : 0.15 ratio among the surviving criteria
  (0.6/0.95 = 0.6316, 0.2/0.95 = 0.2105, 0.15/0.95 = 0.1579).
- `win_criteria` is `[None, None, 0.0]`.
- `force_wincap: False` on all three; `force_freegame`: basegame False, freegame
  True, "0" False.
- **No code path in `block_cave/` can hang on a `wincap` criteria** now: there is
  no such distribution, `run.py` iterates only `basegame`/`freegame`/`0`, and
  `test_wincap` constructs a board directly rather than driving the
  repeat-until-criteria loop. The engine's `check_current_repeat_count` (which
  only warns, never terminates) is no longer reachable via a `wincap` criteria.

The author's comment that "the engine normalizes [quotas] by their sum at
runtime (`run_sims.py`)" is **accurate**: `run_sims.py` uses `random.choices(…,
criteria_weights)` (weights are normalized by sum) and, in the `set_sim_amount`
path, explicitly divides by `total_quota` (`d.get_quota() / total_quota`). With
the quotas now summing to exactly 1.0, `get_sim_splits`' `num_sims * d._quota`
allocation is also exact, so no rounding drift.

### 4. Config/rules — **NO REGRESSION**

The surviving three distributions match MATH_DESIGN.md:
- `reel_weights` = `{'basegame':{'BR0':1},'freegame':{'FR0':1}}` on all three.
- `scatter_triggers {3:10}` on the `freegame` distribution only.
- `force_freegame`: basegame False, freegame True, "0" False (unchanged).
- `force_wincap: False` on all three.
- `wincap = 1000.0`, `win_type = "cluster"`, `rtp = 0.963`, 6 reels × 5 rows,
  `include_padding=True`, `special_symbols`, paytable and free-spin trigger
  scaling all unchanged from the original review.

### 5. `wincap` cap mechanism — **RETAINED (unchanged)**

- `math/games/block_cave/game_executables.py` (LastWriteTime 22:38:55, unchanged)
  still calls `self.evaluate_wincap()` then `self.process_ore_vein_upgrades()`
  inside `emit_tumble_win_events`.
- `math/games/block_cave/gamestate.py` (22:39:42, unchanged) still guards the
  cascade loop with `while self.win_data["totalWin"] > 0 and not
  (self.wincap_triggered)` and retains `wincap_triggered`.
- `math/games/block_cave/test_block_cave.py` (22:43:39, unchanged) still asserts
  `state.wincap_triggered`, uses `WINCAP_UNITS = 100000`, and checks
  `int(round(min(total_mult, 1000.0) * 100, 0)) == b["payoutMultiplier"]` —
  the 100,000-unit clamp.
- The engine `wincap` mechanism lives in `math/src/state/state.py`
  (`min(self.win_manager.running_bet_win, self.config.wincap)`, etc.); all of
  `math/src/` is unchanged (14:45:09).

### 6. Off-limits cleanliness — **AUTHOR CHANGED ONLY `game_config.py` + `run.py`**

| Path | LastWriteTime | Assessment |
|---|---|---|
| `math/games/block_cave/game_config.py` | 22:56:11 | **the F1 fix** (removed `wincap` dist; re-normalized quotas; NOTE comment) |
| `math/games/block_cave/run.py` | 22:56:14 | **docstring only** (lines 7–14) |
| `math/games/block_cave/*.py` (other) | 22:38–22:43 | unchanged |
| `math/games/block_cave/MATH_DESIGN.md` | 22:36:02 | unchanged |
| `math/src/` source + pyc | 14:45:09 / 15:53:43 | unchanged |
| `math/games/0_0_cluster/` | 14:45:09 | unchanged |
| `opencode.jsonc` | 16:08:50 | unchanged |
| `frontend/pnpm-lock.yaml` | 17:15:32 | unchanged |
| `docs/GAME_SPEC.md`, `docs/PROJECT_PLAN.md` | 22:31:00 / 22:31:47 | unchanged |
| `docs/STATUS.md` | 22:55:45 | **orchestrator-owned** status note (see note below) |

**Observation (not an author violation):** `docs/STATUS.md` changed to 22:55:45.
Its content records this QA verdict and states "F1 fix ... is in progress; the
author re-runs the affected checks and QA re-verifies." STATUS.md is
orchestrator-owned; this is the expected orchestrator status update, not a math
implementation change. All other `docs/` files are unchanged.

## Re-verification verdict

**F1 is RESOLVED.** The non-convergent `wincap` bet-mode criteria distribution
is gone; the surviving criteria are `['basegame','freegame','0']` with quotas
summing to 1.0, `win_criteria [None, None, 0.0]`, and `force_wincap: False`
throughout. No code path in `block_cave/` can hang on a `wincap` criteria.

**No new issue was introduced by the fix.** `test_block_cave.py` still passes
10/10 (including `test_wincap`), `run.py` completes without hanging and writes
the same 60 books, the re-generated books still satisfy all invariants
(`bc_verify_books.py`: 60 books, 0 `wincap` events, 103 `oreVeinUpgrade` events,
`ISSUES: none`, max `payoutMultiplier` 2132), config/rules match the design, and
the `wincap` cap mechanism (engine + `game_executables` + `gamestate` +
`test_wincap`) is retained and unchanged. Off-limits integrity holds (author
touched only `game_config.py` and `run.py`).

**Final verdict on the Stage 2 prototype after the fix: PASS.**
The previously-reported F1 is resolved and all affected checks re-verify clean.
The remaining items (F2 LOW/theoretical, F3 INFO, F4 Stage-3 frontend contract,
F5 INFO/disclosed) are unchanged and non-blocking. No measured RTP, hit
frequency, feature rate or volatility is claimed for Block Cave.
