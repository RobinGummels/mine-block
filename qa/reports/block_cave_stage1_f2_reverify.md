# QA Re-verification — Block Cave F2 (reproducible reel strips) — after math-agent fix

**Reviewer:** Independent QA agent (not the design author; did not write the fix)
**Date:** 2026-11-17
**File under review:** `math/games/block_cave/MATH_DESIGN.md` (**NOT modified by QA**)
**Prior verdict:** `qa/reports/block_cave_stage1_math_review2.md` — **NOT READY FOR STAGE 2**,
solely because **F2** (reproducible reel-strip arrangement) was broken: the documented
seed + algorithm did not reproduce the embedded ordered strip lists (divergence at index 2;
seeds 0–500,000 brute-forced with no match).

**Scope of this pass:** Independently re-verify F2 on the finalized design. This pass is
limited to the strip-reproducibility claim and any new blocker introduced in §4. It does
**not** re-run the full F1–F10 / A/B/C review (those were already resolved in the prior
pass and are unaffected by this change).

---

## F2 verdict: **RESOLVED**

The documented deterministic generation rule now reproduces the embedded ordered strips
byte-for-byte, for both the base and the free-spin strip. The declared SHA-256 values, the
embedded lists, the `build_strip` code and the step-by-step summary all agree.

---

## Method (non-circular)

A standalone script was written (QA-only, in the session temp dir,
`opencode\blockcave_f2_verify\verify_f2.py`) and run with the isolated math venv
(`math\.venv\Scripts\python.exe`, Python 3.13.2). It:

1. **Reads the design file programmatically** and extracts, without hand-copying:
   - the two fenced 200-symbol ordered lists (attributed to §4.1 base / §4.2 free-spin by
     section boundaries),
   - the single ```python `build_strip` / `sha256_strip` code block (and `BASE_COUNTS`,
     `FREE_COUNTS`, `COMMON_ORDER`, `NONCOMMON_ORDER`),
   - the declared SHA-256 values from the prose.
2. **`exec`s the extracted `build_strip` code** to obtain the functions/constants.
3. **Regenerates** each strip purely from its documented seed + counts
   (`build_strip(20261117, BASE_COUNTS)` and `build_strip(20261118, FREE_COUNTS)`),
   independently of the embedded list.
4. **Compares** the regenerated strip to the embedded list read from the file, asserts
   length 200, asserts symbol counts match the weight tables, and asserts
   `sha256_strip(regenerated)` equals the declared SHA-256.

The regeneration uses only the documented rule + seed + counts (independent of the embedded
list), and the embedded list is read from the file and actually compared. This is not
circular.

---

## Script output (evidence)

```
[section] 4.1 @ 10519, 4.2 @ 18323, ##5 @ 22061
[extract] symbol-strip candidates found: 2
[extract] base strip length      = 200
[extract] free-spin strip length = 200
[extract] declared base SHA      = 7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451
[extract] declared free SHA      = f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754
[code] COMMON_ORDER    = ['earth', 'stone', 'timber', 'copper']
[code] NONCOMMON_ORDER = ['silver', 'gold', 'emerald', 'diamond', 'ingot', 'ore_vein', 'pickaxe']

===== COUNTS CROSS-CHECK (code block vs design weight tables) =====
BASE_COUNTS  == design 4.1 table: PASS
FREE_COUNTS  == design 4.2 table: PASS
BASE_COUNTS  sum = 200
FREE_COUNTS  sum = 200

===== BASE STRIP (build_strip(20261117, BASE_COUNTS)) =====
seed used                      = 20261117
regenerated length             = 200
embedded length                = 200
length == 200                  : PASS (and embedded 200)
ORDERED LIST MATCH             : PASS (element-by-element, len=200)
counts == weight table         : PASS
sha256(regenerated)            = 7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451
sha256(embedded)               = 7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451
declared SHA-256               = 7d04c1381709f4bad9811c1f8bf1b7d53d9ee11562a5e33326ef4b859bfb2451
sha256(regenerated) == declared: PASS
sha256(regenerated) == embedded: PASS

===== FREE-SPIN STRIP (build_strip(20261118, FREE_COUNTS)) =====
seed used                      = 20261118
regenerated length             = 200
embedded length                = 200
length == 200                  : PASS (and embedded 200)
ORDERED LIST MATCH             : PASS (element-by-element, len=200)
counts == weight table         : PASS
sha256(regenerated)            = f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754
sha256(embedded)               = f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754
declared SHA-256               = f7f48c53b017f2e74599fd2d71a775bcc6ba1dc5617505c1815e6dd995d89754
sha256(regenerated) == declared: PASS
sha256(regenerated) == embedded: PASS

===== SUMMARY =====
base strip fully reproducible   : PASS
free-spin strip fully reproducible: PASS
OVERALL F2 VERDICT              : PASS / RESOLVED
EXITCODE=0
```

---

## Assertions

| Assertion | Result |
| --- | --- |
| Regenerated base strip == embedded base list (element-by-element) | **PASS** |
| Regenerated free-spin strip == embedded free-spin list (element-by-element) | **PASS** |
| Both strips length == 200 | **PASS** (regenerated and embedded both 200) |
| Base symbol counts == §4.1 weight table | **PASS** |
| Free-spin symbol counts == §4.2 weight table | **PASS** |
| `sha256_strip(regenerated base)` == declared base SHA | **PASS** |
| `sha256_strip(regenerated free)` == declared free SHA | **PASS** |

Counts checked: base `earth36 stone33 timber31 copper30 silver16 gold14 emerald12
diamond10 ingot7 ore_vein8 pickaxe3` (sum 200); free-spin `earth30 stone28 timber26
copper24 silver18 gold16 emerald14 diamond12 ingot14 ore_vein15 pickaxe3` (sum 200).
Both match the weight tables exactly.

---

## Consistency of the F2 reproducibility claim (§4.1 / §4.2)

- **Embedded lists** — present, length 200, valid symbol tokens only.
- **Code block** — a single authoritative ```python block; deterministic (a fresh
  `random.Random(seed)` is the only RNG); uses `BASE_COUNTS` / `FREE_COUNTS`.
- **SHA-256** — the declared base `7d04c1…2451` and free `f7f48c…9754` are exactly the
  hashes of the regenerated strips.
- **Step-by-step summary arithmetic** — confirmed against the executed code:
  64 pairs + 2 singles = **66 runs**, 130 common symbols; 70 non-common singles;
  `len(runs)+1` = **67** gap buckets; 130 + 70 = **200**. The prose summary matches.
- **Seeds** — `20261117` (base, §4.1) and `20261118` (free-spin, §4.2) are documented in
  the file and reproduce the strips.

All four elements (prose, code, SHA-256, step-by-step summary) now agree.

---

## New-blocker scan (§4 only)

No new blocker was introduced in §4. The change is self-consistent: the generation rule is
deterministic, uses a single seeded RNG, reproduces both strips, and the counts/weights are
unchanged and correct. The §4.1 usage note ("6 reels read a consecutive 5-symbol window from
this single strip, per-reel random offset, `strip[(reel_pos + row) % 200]`") is a Stage-2
consumption description, not part of the reproducibility guarantee, and is consistent with
the strip being a shared 200-symbol reel strip. No contradictions introduced.

---

## Remaining Stage-2 blocker related to the strip

**None.** The only prior critical blocker (N1 / F2, unreproducible strip) is now resolved.

---

## Conclusion

F2 is **RESOLVED**. With the single prior blocker cleared and no new blocker introduced in
§4, the design is now **ready for a final READY verdict** for Stage 2. This pass did not
re-open the other resolved findings (F1, F3–F10, A/B/C), which were confirmed in the prior
review and are unaffected by this change.

---

*QA deliverable only. No implementation files were modified. The design file
`math/games/block_cave/MATH_DESIGN.md` was not touched. Verification script and output are
in `C:\Users\robin\AppData\Local\Temp\opencode\blockcave_f2_verify\verify_f2.py`.*
