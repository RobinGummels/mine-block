# Block Cave Variant P — DEV package independent QA

**Verdict: PASS WITH FINDINGS** — all 8 package checks pass; no BLOCKER or
MEDIUM defect in the generated package. Findings are design/limitation notes.

**Object under test (DEV only):** the generated DEV math package for Variant P
(Block Cave Lapis Lazuli + persistent ore veins) at
`math/games/block_cave/library/`:

| Artifact | Bytes |
| --- | ---: |
| `library/books/books_base.jsonl` | 4,715,025,550 |
| `library/lookup_tables/lookUpTable_base.csv` | 22,207,144 |
| `library/publish_files/books_base.jsonl.zst` | 420,175,702 |
| `library/publish_files/lookUpTable_base_0.csv` | 36,607,144 |
| `library/publish_files/index.json` | 106 |

`index.json` content (exact):
`{"modes":[{"name":"base","cost":1.0,"events":"books_base.jsonl.zst","weights":"lookUpTable_base_0.csv"}]}`

**This is NOT a production RTP claim and NOT a production release.** The package
is a measurement/DEV artifact. The weights are a minimum-KL re-weighting of the
natural book distribution to a target published RTP — **not** the Rust
optimizer's full fence/search output.

---

## Summary of checks

| # | Check | Result |
| --- | --- | --- |
| 1 | CSV byte-identity (base + optimized LUT vs reference) | **PASS** |
| 2 | zstd round-trip (decompress == jsonl) | **PASS** |
| 3 | Line counts (books + both LUTs) | **PASS** |
| 4 | Book/CSV consistency + `check_book` (full 1.8M scan) | **PASS** |
| 5 | npz cross-check (reference `vp_weighted_180m.npz` vs books) | **PASS** |
| 6 | Metrics recompute (natural + weighted, independent) | **PASS** (44/44) |
| 6b | Min-KL band-weighting re-derivation (independent) | **PASS** |
| 7 | Off-limits files unchanged (SHA-256) | **PASS** (8/8) |
| 8 | Official/format tests | **PASS** (13/13 + 25/25) |
| — | Reproducibility (config → books) | **PASS** |

---

## Per-check detail

### Check 1 — CSV byte-identity — PASS

Re-hashed from scratch; both generated files are byte-identical to the reference
copies in `.runtime/block_cave/`.

- `library/lookup_tables/lookUpTable_base.csv`
  sha256 `2662d122d760d17bce32eed9bfdc5feeb250ddca04ee726e042517f1298e282b`
  (22,207,144 B) == reference `vp_weighted_base_lut.csv`.
- `library/publish_files/lookUpTable_base_0.csv`
  sha256 `ed086fa57cf5281f76036af9919aa7580e01ee8d1dd2c49ab03efc84bc27094c`
  (36,607,144 B) == reference `vp_weighted_optimized_lut.csv`.

### Check 2 — zstd round-trip — PASS

Streamed decompression of `books_base.jsonl.zst` (420,175,702 B) produced
**4,715,025,550** bytes, exactly the raw `books_base.jsonl` size. Chunk-for-chunk
byte-identical to the raw jsonl. `sha256(jsonl) == sha256(decompressed) ==
7ba38e97aa0f91475baec1d3c82cc065bbd0939e8710b488f39c6a393bb6ef2f`.

### Check 3 — line counts — PASS

- `books_base.jsonl`: 1,800,000 lines.
- `lookUpTable_base.csv`: 1,800,000 lines.
- `lookUpTable_base_0.csv`: 1,800,000 lines.

No header row. First line `0,1,333`; last line `1799999,1,0` (base LUT) and
`1799999,624429725,0` (optimized LUT). No newline-only trailing artifact.

### Check 4 — book/CSV consistency + `check_book` — PASS (full scan)

Streamed all **1,800,000** books in lockstep with both LUTs (219.7 s, 8,193
books/s). Results over the full set:

- base-LUT row mismatches: **0**
- optimized-LUT row mismatches: **0**
- `calibrate.check_book(book)` violations: **0**
- `payoutMultiplier` recompute
  (`int(round(min(base+free,1000)*100))`) mismatches: **0**

`check_book` validates: `payoutMultiplier` int in `[0,100000]`, contiguous event
indexes, first event `reveal`, `finalWin.amount == payoutMultiplier`,
`int(round(min(base+free,1000)*100)) == payoutMultiplier`, non-negative wins.

### Check 5 — npz cross-check — PASS (full 1.8M)

Reference `vp_weighted_180m.npz` compared against QA arrays collected directly
from the books jsonl — **all 1,800,000 entries** (not a sample). `pm`, `base`,
`free`, `hit`, `feat`, `fspins` all **0 mismatch**. Also confirmed reference npz
`pm == round(min(base+free,1000)*100)` for all entries (0 mismatch).

### Check 6 — metrics recompute — PASS (44/44)

Recomputed independently from the books + optimized-LUT `weight_int`, compared
against `vp_package_vp_full.summary.json` and `vp_weighted_180m_an.json`.
**All 44 comparisons match** (natural values exact; weighted values agree to
≤ 8.8e-11, attributable to float-vs-integer weight encoding).

**Natural (base-LUT, all weights = 1):**

| Metric | Value |
| --- | --- |
| RTP | 0.9457134111111112 |
| base RTP | 0.7615848388888895 |
| feature RTP | 0.18412857222222206 |
| visible hit | 0.6984872222222223 |
| full return | 0.24885555555555555 |
| feature entry | 0.0070866666666666665 (k=12,756) |
| feature duration mean / max | 8.617121354656632 / 32 |
| max win | 428.36 |
| P(≥100×) | 0.00010111111111111112 (k=182; base-only 1 / with-fs 181) |
| P(≥500×) | 0 |
| P(≥1000×) | 0 |

**Weighted (optimized-LUT `weight_int`):**

| Metric | Value |
| --- | --- |
| published RTP | 0.9629999999120095 (error −8.8e-11 vs 0.963) |
| visible hit | 0.6990031071174377 |
| full return | 0.24979113496259292 |
| feature entry | 0.00741748827476671 |
| P(≥100×) | 0.00012856470701416836 (base-only 8.8e-07 / with-fs 1.2768e-04) |
| P(≥500×) | 0 |
| P(≥1000×) | 0 |
| max single-book weight (int) | 992,966,420 |

### Check 6b — min-KL band-weighting re-derivation — PASS

Re-implemented the exponential-tilt solve from scratch (no import of the
implementer's helper). **λ = 0.0017946579216578254** matches the summary
exactly; bisection converged. Band table `count/p_b/m_b/q_b/ratio` all match;
**KL = 1.5800928909953444e-05**; max band boost ratio **1.5874764225375428**.
Optimized-LUT integer weights equal
`round((q_b/count_b normalized)*2^50)` with **0 mismatch**. Only `[0,0.1)` and
`[0.1,1)` are reduced (≤0.17%); the max boost (1.587×) is on `[200,500)`.
Published RTP from the derived weights = 0.9629999999120095.

### Check 7 — off-limits files unchanged — PASS (8/8)

All 8 files match their recorded SHA-256 (and mtimes are recorded):

| File | SHA-256 (first 8 hex) |
| --- | --- |
| `game_config.py` | 9642B207… |
| `variant_config.py` | DDD4DBD1… |
| `ore_vein_rules.py` | AB161BFF… |
| `game_executables.py` | 2B1D167B… |
| `candidate2_config.py` | 10F1DC1D… |
| `candidate_lapis_config.py` | DC343889… |
| `candidate_lapis_persistent_config.py` | 27ECE240… |
| `calibrate.py` | 816796E3… |

### Check 8 — official/format tests — PASS

- `math/tests/win_calculations`: **13/13** passed.
- `math/games/block_cave/test_block_cave.py`: **25/25** passed.

### Reproducibility — PASS

Regenerated the first 200 books from
`candidate_lapis_persistent_config.build_config()` + `CalibrateState` /
`run_spin(170000000 + i)`; book dicts are byte-equal to the jsonl. Config
confirmed: `ore_vein_persist_freespins=True`, `ore_vein_persist_max=7`,
`ore_vein_rule='create-cluster'`, `ore_vein_target='diamond'`. Regenerated
books also pass `check_book`.

---

## Findings

- **F1 (MEDIUM — claim reconciliation, not a package defect).** The config
  docstring says it is calibrated "to hold the natural RTP inside the 96.0–96.7%
  band," but the natural (base-LUT) RTP measures **0.9457**, ~1.4 pp **below**
  the band. The min-KL weighting lifts only the *published* RTP to 0.963; the
  underlying game still under-returns until that weighting is actually applied.
  The user directive treats published-mode RTP as the operative metric, so this
  is expected, but the config's own claim should be reconciled.
- **F2 (NOTE).** The min-KL weights are a **model** of the Rust optimizer's RTP
  targeting, **not** the actual optimizer output. The real Rust optimizer is not
  currently wireable for Block Cave (no `game_optimization.py`/`OptimizationSetup`
  → `opt_params` unset; the `wincap` fence's `avg_win` = 1000.0 is not in the
  base LUT; the Rust binary is not built). These weights are therefore not
  authoritative.
- **F3 (NOTE).** The repo is **not a git repo**, so "untouched" beyond the listed
  SHAs/mtimes cannot be byte-verified against a baseline. The 8 off-limits files
  match their recorded SHAs and mtimes, which is the strongest available check.
- **F4 (NOTE).** No ≥500× or ≥1000× tail exists in 1.8M spins (P(≥500×)=0,
  P(≥1000×)=0; round max 428.36). The persistent-vein "tail lift" intent is not
  realized in-band, and the weighting cannot create a tail that is absent from
  the natural distribution.
- **F5 (INFO).** Weighted P(≥100×) = 1.286e-4 (≈1:7,776), inside the acceptable
  1:5,000–1:20,000 band, but this is a point estimate on one 1.8M sample, not a
  tail certification (rare & seed-sensitive).
- **F6 (INFO).** No frontend/event-contract change is involved (a lookup-table
  weight change only). Visual/Playwright QA is **not applicable** — no Block Cave
  frontend exists yet (Stages 5–6).

---

## What could NOT be verified

- **Real Rust optimizer output** for Block Cave — not wireable in this
  environment; the weighted mode is a model, not the optimizer's output.
- **"Untouched" beyond the listed SHAs/mtimes** — no git baseline exists to diff
  against.
- **Exact `common-scale=1.10` multiplier semantics** on each pay value — the
  scale is baked into `_P_COMMON_PAYS` and was not independently re-derived as a
  per-value multiplier; only config reproducibility and measured RTP agreement
  were verified.
- **Whether a ≥500× tail exists at larger sample sizes** — 0 observed in 1.8M
  spins; not tested beyond that.

---

## Evidence

QA scratch scripts (QA files) in `.runtime/block_cave/`:
`qa_vp_check1_csv_identity.py`, `qa_vp_check2_zstd_roundtrip.py`,
`qa_vp_check4_consistency.py`, `qa_vp_check5_npz.py`,
`qa_vp_check6_metrics.py`, `qa_vp_check6b_minkl.py`, `qa_vp_repro.py`.
QA arrays collected from the books: `.runtime/block_cave/qa_vp_arrays.npz`.
References: `.runtime/block_cave/vp_weighted_base_lut.csv`,
`vp_weighted_optimized_lut.csv`, `vp_weighted_180m.npz`,
`vp_weighted_180m_an.json`, `vp_package_vp_full.summary.json`.

**Environment:** `math/.venv/Scripts/python.exe` (Python 3.13.2, numpy 2.2.5,
zstandard 0.23.0), Windows/PowerShell.

## Conclusion

The generated Variant P DEV package is internally consistent, complete and
reproducible: all books/LUTs agree, `check_book` passes on every book, the
reference npz matches, metrics recompute exactly, off-limits files are
unchanged, and the official/format test suites pass. **No implementation or
library file was modified by this QA pass.** The package is a DEV artifact, not a
production release or a production RTP claim.
