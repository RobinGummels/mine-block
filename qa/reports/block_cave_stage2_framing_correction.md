# QA report — Block Cave Stage 2 mechanics-framing correction

**File under review:** `math/games/block_cave/MATH_DESIGN.md`
**Reviewer:** Independent QA subagent (not the file's author)
**Date:** 2026-11-17
**Scope:** Framing/wording correction only. The ore-vein conversion of an adjacent
regular block is a **normal in-round mechanic**, **NOT** a "bonus upgrade" and
**NOT** the deferred free-spin bonus-tier upgrade. No mechanics, numeric or rule
content was expected to change.

**Authoritative external references used to judge the correction:**
- `docs/GAME_SPEC.md` lines ~37–42: "An automatic, predetermined bonus-tier
  upgrade within a single book remains a research item until Engine confirms its
  acceptability. **This is separate from the ore-vein symbol converting a
  neighboring block during an ordinary round.**"
- `docs/PROJECT_PLAN.md` lines ~20–22 and ~67: "an automatic free-spin
  bonus-tier upgrade needs platform confirmation before implementation. **The
  ordinary ore-vein symbol conversion is already part of the approved game
  concept and is assessed with the other in-round mechanics.**"

---

## Verdict: **PASS**

All three required locations are corrected consistently, the new top-level
revision-history entry is present and correctly labeled, no residual conflation
remains, and the correction does not contradict any mechanic in §5, §6 or §8.
It is a pure framing/wording fix with no change to any numeric or rule content.

---

## 1. The four required corrections — all present

### 1a. §1 "Scope and status" stateless bullet (lines 74–82)

The bullet is correctly reworded:

> "The ore-vein upgrade is a **normal in-round mechanic**, not a player choice
> and not a continuation: when a vein activates it converts an adjacent regular
> block as a fixed rule. It is **not** a "bonus upgrade" and is **not** the
> deferred free-spin bonus-tier upgrade (see §9); it is assessed with the other
> in-round mechanics like the wild and the scatter."

Stateless (F9) wording is retained and the ore-vein upgrade is explicitly
separated from the deferred free-spin bonus-tier upgrade. **Correct.**

### 1b. §9 "Open decisions / open questions" (lines 867–878)

The open-decision entry is correctly reworded:

> "**The ore-vein upgrade is a normal in-round mechanic, not a free-spin bonus
> upgrade (corrected).** … It is automatic, predetermined and stateless (no
> player-selected wager/upgrade, F9). It is **not** a "bonus upgrade" and is
> **not** the deferred free-spin bonus-tier upgrade. The separate product
> preference for a "free-spin bonus upgrade that retains a small guaranteed
> win" remains a **distinct, deferred research item** that still needs platform
> confirmation before any implementation (per `GAME_SPEC.md` and
> `PROJECT_PLAN.md`). By contrast, the ore-vein conversion is already part of
> the approved game concept and is assessed with the other in-round mechanics."

This matches the authoritative statements exactly. **Correct.**

### 1c. Assumptions ledger row #20 (line 936)

> "| 20 | The game is stateless with no player-selected wager/upgrade (F9); the
> ore-vein upgrade is a normal in-round mechanic, not a free-spin bonus
> upgrade. | No player-choice state in the game. Platform confirmation applies
> only to the separate, deferred free-spin bonus-tier upgrade, not to the
> ore-vein conversion. |"

The "How it is verified" cell correctly scopes platform confirmation to the
separate free-spin bonus-tier upgrade only. **Correct.**

### 1d. New "Revision history" entry at the top (lines 15–28)

The top entry is present and labeled **"Revision history (2026-11-17 — Stage 2
mechanics-framing correction)"**. It states that the change removes a framing
error (not a mechanics change), and defines **C1 (this revision)**:

> "the ore-vein conversion of an adjacent regular block is a **normal in-round
> mechanic**, like the wild and the tumble. It is automatic, predetermined and
> stateless. It is **not** a bonus upgrade and is **not** the deferred
> free-spin bonus-tier upgrade. Only the separate free-spin bonus-tier upgrade
> still needs platform confirmation; the ore-vein conversion is part of the
> approved game concept and is assessed with the other in-round mechanics (see
> §1 and §9). Game logic is unchanged."

This entry is correctly placed as the first (most recent) revision block, above
the prior "QA-response revision" entry (lines 30–65). **Correct.**

---

## 2. Whole-file residual-conflation search — none found

Searched the entire file for the following terms (case-insensitive):
`bonus upgrade`, `bonus-tier`, `bonus tier`, `in-book`, `in book`,
`platform confirmation`, `platform confirm`, `needs platform`, `platform`,
and reviewed every `upgrade` occurrence (76 matches).

Every occurrence of the conflation terms is in one of two legitimate contexts:

1. **The corrected framing itself**, explicitly negating the conflation (e.g.
   "It is **not** a "bonus upgrade"", "**not** the deferred free-spin
   bonus-tier upgrade").
2. **The separate, deferred free-spin bonus-tier upgrade** (a distinct product
   preference that genuinely still needs platform confirmation) — never applied
   to the ore-vein conversion.

Notes on specific matches that were checked and ruled **not** residual
conflation:
- **Line 18/20** — inside the new revision-history entry describing the error
  that was removed; correctly framed as the *old* (now-corrected) wording.
- **Line 844 (`createBonusSnapshot`)** — this is a list of existing frontend
  `BookEvent` union members, unrelated to the ore-vein framing; it is a factual
  list of current event types and does not call the ore-vein upgrade a bonus.
- **Line 864 (separately priced bonus mode)** — a distinct open decision about a
  separately priced bonus mode, separate from the ore-vein upgrade. Not
  conflation.
- **§5 / §6 / §8 mechanics** — describe the ore-vein upgrade purely as an
  in-round mechanic/event; no "bonus upgrade" or "platform confirmation"
  language is attached to the ore-vein conversion.

No residual text in `MATH_DESIGN.md` calls the ore-vein upgrade a "bonus
upgrade", an "in-book upgrade", or a "bonus-tier upgrade", and none implies the
ore-vein conversion needs platform confirmation.

---

## 3. No mechanics contradiction — purely a framing fix

Confirmed the correction is consistent with the actual mechanics and does not
change any numeric or rule content:

- **§5 (lines 473–598) — Ore-vein (wild + upgrade) rules.** Activation is
  automatic (a vein activates when it is a member of a winning cluster, §5.2);
  it converts **1** adjacent regular block to `diamond` (§5.3); it is consumed
  on activation (§5.4); multiple veins process in deterministic scan order
  (§5.5). All of this is consistent with a "normal in-round mechanic,
  automatic, predetermined and stateless" framing. No framing-related wording
  contradicts these rules, and no numeric/rule value was altered by the
  correction (the F3 `ingot`→`diamond`, cap 3→1 changes are from the prior
  "QA-response revision" block, not this framing fix).
- **§6 (lines 600–687) — Pickaxe scatter + free spins.** Describes the
  scatter trigger and free-spin feature. No mention of the ore-vein upgrade as
  a bonus, and no contradiction with the corrected framing. The separate
  free-spin bonus-tier upgrade is not presented as an implemented mechanic
  here; this section only describes the pickaxe-triggered free spins.
- **§8 (lines 735–856) — Provisional event schema.** The `oreVeinUpgrade` event
  is described as a normal event in the cascade group
  (`updateTumbleWin` → `wincap`/`oreVeinUpgrade` → `tumbleBoard`), consistent
  with an in-round mechanic. No "bonus" or "platform confirmation" framing is
  attached to the ore-vein event.

The correction is therefore a **pure framing/wording fix** — it changes no
numeric value, no rule, no event ordering and no event payload. The mechanics in
§5, §6 and §8 are unchanged and consistent with the corrected framing.

---

## 4. Evidence of the diff reviewed

- Full file read: `math/games/block_cave/MATH_DESIGN.md` (lines 1–942).
- Whole-file grep for conflation terms and all `upgrade` occurrences
  (76 matches) — all reviewed.
- Compared against authoritative statements in `docs/GAME_SPEC.md` (lines
  37–42) and `docs/PROJECT_PLAN.md` (lines 20–22, 67).

---

## Conclusion

**PASS.** The ore-vein framing correction is applied consistently across the
file: §1 stateless bullet, §9 open decision, assumptions-ledger row #20, and the
new top "Stage 2 mechanics-framing correction" revision-history entry are all
correct. No residual conflation with the free-spin bonus-tier upgrade or
"bonus/in-book upgrade" language remains, and no mechanic in §5, §6 or §8 is
contradicted. No further changes to `MATH_DESIGN.md` are required for this
framing correction. (QA does not modify implementation files; this is a
findings-only report.)
