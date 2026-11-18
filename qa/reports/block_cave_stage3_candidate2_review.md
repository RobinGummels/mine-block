# Block Cave — Stage-3 Candidate 2 Independent QA Review

**Reviewer:** Independent QA subagent (read-only on `math/`).
**Date:** 2026-11-18.
**Scope:** `math/games/block_cave/candidate2_config.py` (Stage-3 Candidate 2, DEV)
and the three-way comparison in `math/games/block_cave/CANDIDATE2_REPORT.md`
(§3.1 baseline / Stage-3 variant / Candidate 2).

**Verdict: PASS WITH FINDINGS**

No blocking defect. The Candidate 2 config is reproducible, the test suite
passes, the off-limits files are intact, and an independent 200k natural
measurement reproduces the math agent's reported numbers **byte-for-byte**
(`qa_c2_200k.json` is identical to `c2_f5_200k.json`). The arithmetic behind
the central "RTP-band conflict" claim is confirmed. The one substantive
finding is that the report frames the conflict as **inherent / not
simultaneously achievable**, which is stronger than the evidence supports
(demonstrated for this seed arrangement specifically; the config is highly
seed-sensitive and the CI straddles 96.0%). See **F1 (MEDIUM)**.

---

## 1. Checks performed

### Check 1 — Config reproducibility — PASS

`math\.venv\Scripts\python.exe math\games\block_cave\candidate2_config.py`
printed:

```
base strip sha256: 7a9fe8ec9e9c1f9f05a59de5ce1149e21b1ba5dab34fa794a147ad6f1f83d425
free strip sha256: 48e1ea8cb7de20454be0fc1b5cf2064da5cf4709b878d06783c5dfb1c7015096
Candidate 2 strips reproducible (length 200, counts + SHA-256 match)
```

Both SHAs match the frozen values exactly. Both strips are length 200, and
`BASE_COUNTS`/`FREE_COUNTS` match (each sums to 200). `build_config()` sets the
`create-cluster` rule / `diamond` target and the H4/F5 strips.

### Check 2 — Test suite — PASS

| Check | Result |
| --- | --- |
| `test_block_cave.py` | **16/16 pass** |
| `python -m pip check` | **No broken requirements found** |
| `python -m pytest math\tests\win_calculations -q` | **13 passed** |

The 16th test (`test_candidate2_config_reproducible`) is present and passes; it
also re-checks that the baseline strips are unchanged.

### Check 3 — Off-limits integrity — PASS

The four off-limits files (`game_config.py`, `variant_config.py`,
`ore_vein_rules.py`, `game_executables.py`) were **not** modified by the
Candidate 2 work:

- **§3.1 baseline** re-derived independently: base
  `7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451` (…2451),
  free `f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754`
  (…9754) — both match the documented values; length 200; counts match.
- **Stage-3 variant** re-derived independently: base
  `428854a3b18ff3683bfb0b14126672f173f3520a762564f098a305fed4d60277` (…60277),
  free `aa0002abdcdfda251db2dbe363b1b2d98c5badbbd946a039961af130f96cc9ce`
  (…c9ce) — both match; length 200; counts match.
- No `candidate2` reference exists in any of the four off-limits files
  (grep returned no matches). `candidate2_config` is referenced only by its own
  report, the test suite, and the `MATH_DESIGN.md` revision note.
- The shipped `game_config.py` default ore-vein behaviour is unchanged: it does
  **not** set `ore_vein_rule`/`ore_vein_target` attributes, and the executable
  resolves them via `getattr(..., "baseline")` / `getattr(..., "diamond")`.
  Confirmed `_ore_target(GameConfig()) == "diamond"` and
  `getattr(config, "ore_vein_rule", "baseline") == "baseline"`.
- Candidate 2 is **not** wired into any shipped entry point
  (`run.py`, `game_calculations.py`, `game_events.py`, `gamestate.py`,
  `game_config.py` all contain no `candidate2` reference).

### Check 4 — Independent measurement — PASS (exact reproduction)

Built the Candidate 2 config independently (counts JSON written from
`candidate2_config.BASE_COUNTS`/`FREE_COUNTS`, seeds 20261103/20261118,
`create-cluster`→`diamond` rule, §3.1 paytable scale 1.0) and ran:

```
math\.venv\Scripts\python.exe .runtime\block_cave\measure_c2.py \
  .runtime\block_cave\qa_c2_base.json 20261103 \
  .runtime\block_cave\qa_c2_free.json 20261118 \
  200000 20000 .runtime\block_cave\qa_c2_200k.json
```

n = 200,000 natural base rounds per ore-vein arm (seed-matched) + 20,000 forced
freegame rounds. Runtime ≈ 206 s. **0 consistency violations.**

The output `qa_c2_200k.json` is **byte-for-byte identical** to the math agent's
`c2_f5_200k.json` (verified by `json.load` equality).

| Metric (natural, n=200k, ore-vein enabled) | **QA independent** | Report | Match |
| --- | --- | --- | --- |
| RTP (mean round payout) | **0.95087** | 0.95087 | ✅ |
| RTP 95% CI | **[0.9377, 0.9640]** | [0.9377, 0.9640] | ✅ |
| base-game RTP contribution | **0.77657** | 0.77657 | ✅ |
| free-spin RTP contribution | **0.17430** | 0.17430 | ✅ |
| Visible hit `P(payout>0)` | **0.46519** | 0.46519 | ✅ |
| Full return `P(payout>=1.0x)` | **0.18403** | 0.18403 | ✅ |
| Feature entry rate | **0.016165** | 0.01617 | ✅ |
| Feature payout mean (natural) | **10.7825** | 10.78 | ✅ |
| Feature duration mean | **8.9007** | 8.90 | ✅ |
| Round payout max | **184.55** | 184.55 | ✅ |
| Ore-vein Δ (enabled−disabled, pp) | **+0.2693** | +0.269 | ✅ |
| Consistency violations | **0 / 200000** | 0 | ✅ |

Additional (forced freegame, n=20,000): feature payout mean **10.6223**
(report 10.62), median **7.635**, duration mean **8.496** (report 8.50), max
**44**, payout max **187.04**, `P(>=100x)` **0.00095** — all match.

Note: `P(>=100x)` in the natural round is `2.5e-05` (1 round in 40,000), not
0 — the console summary prints it rounded to `0.0000`.

### Check 5 — RTP-band conflict claim — CONFIRMED (arithmetic), with caveat

The core arithmetic is confirmed by my measurement:

- base contribution ≈ **0.777** (measured 0.77657).
- feature contribution ≈ **0.174** (measured 0.17430).
- total ≈ **0.951** (0.77657 + 0.17430 = 0.95087), **below** the 96.0% band.
- The 95% CI **[0.9377, 0.9640]** **straddles** 96.0% (0.9377 < 0.96 < 0.9640),
  so "below band" is a **point-estimate** statement, not a CI-supported one.
- The identity `entry × feature-payout-mean` holds: 0.016165 × 10.7825 =
  0.17430.
- To reach 96.0% with the feature contribution held at 0.1743, base would need
  to be **≈0.7857** (0.96 − 0.1743). The report's stated "≈0.785" is correct.
- CI-implied RTP stddev ≈ 2.997, consistent with the report's "≈3.0".

The **characterization of an inherent conflict** is only partially supported.
The numbers confirm a real, large trade-off for **this seed arrangement
(20261103)**: a sparser strip that hits the §3.3 targets (hit 46.5%, full
18.4%) lowers the base contribution to ~0.777, and even a strong feature
(0.174) does not close the gap to 96.0%. That is a genuine tension.

However, the report's stronger wording — "the §3.3 hit-rate/full-return targets
and the 96.0–96.7% RTP band are **not simultaneously achievable**" (§9) and
"cannot both be met with the current engine/paytable" (§11) — is not fully
established by the data:

1. **The CI straddles 96.0%.** The point estimate is below band but the 95% CI
   includes values in band.
2. **Extreme seed-sensitivity.** The report itself (§10) states base RTP for the
   same counts varies ≈0.37–1.04 across strip-build seeds, and that this same
   Candidate 2 config measured **0.9656 (in band)** at n=100k over a different
   seed range. This shows the "hit/full → base-RTP" mapping is not a fixed
   curve but depends heavily on arrangement, so a different base-seed or a
   modest strip tweak could plausibly land in band at similar hit/full.
3. **The gap is small.** Base needs only ~0.9pp more (0.777 → 0.786, i.e.
   average win-per-hit 1.670 → 1.690) to hit 96.0% at the current feature
   contribution.

The report is careful in §10 and §14 (it does flag the seed-sensitivity and the
straddling CI), but the headline conclusion in §9/§11 reads as a proven
impossibility. The finding below captures this.

### Check 6 — No production claims — PASS

- `candidate2_config.py` docstring: "DEV measurement only - NOT a production RTP
  claim. Nothing here is published or deployed. All numbers are DEV measurements
  on the current prototype."
- `CANDIDATE2_REPORT.md` header: "Status: DEV measurement only. This is NOT a
  production certification and makes no RTP claim for a published game." §14
  repeats this.
- `MATH_DESIGN.md` revision note: Candidate 2 is "**DEV measurement only** — no
  production RTP claim."
- The shipped `game_config.py` `rtp = 0.963` is labelled "design target; do NOT
  claim as measured"; Candidate 2 does not override it.
- Candidate 2 is a separate module, not wired into `game_config.py`; the
  default shipped game remains `baseline`/`diamond`.

---

## 2. Findings

| # | Severity | Finding |
| --- | --- | --- |
| **F1** | **MEDIUM** | The report's §9/§11 conclusion that the §3.3 hit/full targets and the 96.0–96.7% RTP band are **"not simultaneously achievable"** is stronger than the evidence supports. The arithmetic (base ≈0.777, feature ≈0.174, total ≈0.951, CI [0.9377, 0.9640] straddling 96.0%) is fully confirmed, and there is a real trade-off for seed **20261103**. But (a) the 95% CI straddles 96.0%, so "below band" is only a point-estimate; (b) the report itself documents extreme base-RTP seed-sensitivity (≈0.37–1.04 for the same counts, and an in-band 0.9656 for this config at n=100k); and (c) the required base increase to reach 96.0% is only ≈0.9pp. A different base-seed or modest strip tweak may reach the band at similar hit/full. **Recommendation:** reword the conclusion to "this Candidate 2 seed/strip arrangement falls below the band," and treat the shortfall as an arrangement problem to be explored before concluding the two target sets are fundamentally irreconcilable. |
| F2 | LOW | The console summary (`measure_c2.py`) prints `P(>=100x)` for the natural round as `0.0000`, which could be mis-read as zero; the JSON value is `2.5e-05` (1 in 40,000). Informational; the report's §4 table correctly shows `2.5e-05`. |
| F3 | INFO | Visual/Playwright QA was **not applicable** to this task. There is no Block Cave frontend (per `docs/STATUS.md`, frontend is Stages 5–6), so there is no loaded Pixi canvas or Action to verify. This review is math-config validation only. |
| F4 | INFO | The baseline/variant comparison arms in the three-way table were spot-checked against their own output files and match the report (`orchestrator_200k.json`: RTP 0.96435, base 0.89753, hit 0.69956, full 0.29159, entry 0.00674; `variant_200k.txt`: RTP 0.96436, base 0.89673, hit 0.70990, full 0.28690, entry 0.01593, ore-vein Δ +0.2630 pp). I did not independently re-run those two arms. |

---

## 3. Confirmation / contradiction of the math agent's key claims

| Claim | Status |
| --- | --- |
| Candidate 2 strips reproducible (length 200, counts + SHA match) | ✅ **Confirmed** |
| Base SHA `7a9fe8ec…d425`, free SHA `48e1ea8c…5096` | ✅ **Confirmed** |
| 16/16 tests pass | ✅ **Confirmed** |
| `pip check` clean; `win_calculations` 13/13 | ✅ **Confirmed** |
| Off-limits files (`game_config.py`, `variant_config.py`, `ore_vein_rules.py`, `game_executables.py`) unmodified; baseline/variant strips/SHAs unchanged | ✅ **Confirmed** |
| RTP 0.95087 (CI [0.9377, 0.9640]) | ✅ **Confirmed** |
| Visible hit 0.46519 | ✅ **Confirmed** |
| Full return 0.18403 | ✅ **Confirmed** |
| Entry 0.01617 | ✅ **Confirmed** |
| Feature payout mean 10.78 | ✅ **Confirmed** |
| Feature duration mean 8.90 | ✅ **Confirmed** |
| Max round 184.55 | ✅ **Confirmed** |
| Ore-vein Δ +0.269 pp | ✅ **Confirmed** |
| 0 consistency violations | ✅ **Confirmed** |
| Base contribution ≈0.777, feature ≈0.174, total ≈0.951 (below band) | ✅ **Confirmed** |
| CI straddles 96.0% | ✅ **Confirmed** |
| **"Inherent conflict" — §3.3 targets and RTP band not simultaneously achievable** | ⚠️ **Partially supported** (arithmetic confirmed; the "not achievable" framing is overstated; see F1) |
| Config/report clearly DEV, no published-RTP claim | ✅ **Confirmed** |

---

## 4. Evidence / artifacts

- `math/games/block_cave/candidate2_config.py` — self-check output (base/free
  SHA, length 200, counts match).
- `math/games/block_cave/test_block_cave.py` — 16/16 pass.
- `math\.venv\Scripts\python.exe -m pip check` — clean.
- `math\.venv\Scripts\python.exe -m pytest math\tests\win_calculations -q` —
  13 passed.
- `.runtime/block_cave/qa_c2_base.json`, `.runtime/block_cave/qa_c2_free.json`
  — Candidate 2 counts (each sum 200).
- `.runtime/block_cave/qa_c2_200k.json` — independent 200k natural + 20k forced
  freegame measurement (identical to `c2_f5_200k.json`).
- `.runtime/block_cave/qa_c2_timing.json` — small harness smoke (n=2000).
- Off-limits integrity re-derivation (baseline + variant strip SHAs/counts,
  `candidate2` grep) — inline in §1.

## 5. Limitations

- I did **not** re-run the 200k measurement for the baseline and variant
  comparison arms; I relied on their checked-in output files, which match the
  report. (These arms were independently QA-verified in earlier stages per
  `docs/STATUS.md`.)
- I did **not** independently re-derive the exact per-round RTP standard
  deviation from the raw payouts (the qa_c2 JSON stores aggregates only). The
  ≈3.0 stddev is instead corroborated from the CI width (CI-implied stddev
  ≈ 2.997).
- I did **not** run any visual/Playwright browser check — not applicable (no
  Block Cave frontend exists; see F3).
