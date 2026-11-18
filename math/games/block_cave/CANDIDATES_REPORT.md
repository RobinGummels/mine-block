# Block Cave — Stage-3 Candidates A & B vs §3.1 Baseline

**Status:** DEV measurement only. **This is NOT a production certification and
makes no RTP claim for a published game.** All figures are measured on the
current (unpublished) Block Cave prototype. Owner: Math agent.

This report compares three independently-reproducible configs on a **single,
like-for-like out-of-sample (OOS) range**:

1. the validated **§3.1 baseline** (`game_config.py`, ore-vein rule `baseline`),
2. **Candidate A** (`candidate_a_config.py`, ore-vein rule `create-cluster`),
3. **Candidate B** (`candidate_b_config.py`, ore-vein rule `create-cluster`).

Candidates A and B are SEPARATE, clearly-labelled DEV configs. They do **not**
modify `game_config.py`, `variant_config.py` or `candidate2_config.py`. Both
remain unchanged and independently reproducible. **No final math is decided
here** — the recommendation is for the orchestrator/product to choose.

---

## 1. Objective (from the orchestrator)

Build up to TWO baseline-derived Block Cave candidates that:

1. Keep the **96.0–96.7% RTP band** as the HARD target (do NOT relax).
2. Use the §3.1 baseline as the starting point.
3. Switch the ore-vein rule to a **positive `create-cluster`** (target
   `diamond`), and if it overshoots, compensate via the free strip / weights
   **without distorting the paytable** (paytable = §3.1 calibrated, scale 1.0).
4. **Prioritise HIGH visible hit (≈70%) and LOW dry streaks.** The §3.3 targets
   of 45% hit / 15% full-return are **explicitly relaxed**.
5. Calibrate the free-spin ENTRY rate as close to **1%** as possible, and
   document the integer-count constraint.
6. Keep feature payout in the **8–12×** band and **short free spins**
   (8/12/16/16, retrigger cap 60).
7. At most **TWO** new DEV config files; do **not** modify `game_config.py`.
8. Optionally remove Silver Ore; if removed, rebalance to sum 200 and document
   the effect.

---

## 2. Configs under test

| | Base strip | Free strip | Ore-vein rule | Base seed | Free seed | Pay scale |
|---|---|---|---|---|---|---|
| §3.1 baseline | `game_config.py` base | `game_config.py` free | `baseline` | 20261117 | 20261118 | 1.0 |
| **Candidate A** | **E4** | **G6** | `create-cluster` → diamond | 20261117 | 20261118 | 1.0 |
| **Candidate B** | **S6** (silver removed) | **G6** (same as A) | `create-cluster` → diamond | 20261117 | 20261118 | 1.0 |

Base/free counts (sum 200 each):

- **E4 (A base):** earth 36, stone 33, timber 31, copper 30, silver 16,
  gold 14, emerald 12, diamond 8, ingot 9, ore_vein 8, pickaxe 3.
- **S6 (B base):** earth 37, stone 32, timber 30, copper 29, silver **0**,
  gold 20, emerald 16, diamond 14, ingot 13, ore_vein 6, pickaxe 3.
- **G6 (A & B free):** earth 42, stone 40, timber 38, copper 36, silver 8,
  gold 9, emerald 8, diamond 6, ingot 5, ore_vein 5, pickaxe 3.

All strips are deterministic (`build_strip` in `game_config.py`) and frozen by
SHA-256 (see §7).

---

## 3. Measurement method

All three configs were measured on the **same fresh, disjoint OOS range** so the
comparison is like-for-like:

- `start_seed = 1_000_000`, `n = 200_000` natural base rounds per ore-vein arm,
  `freegame_n = 20_000` forced freegame rounds.
- Ore-vein **enabled** arm (natural RTP), ore-vein **disabled** arm (isolates
  the ore-vein RTP contribution), and **forced freegame** arm (feature internal
  distribution only).
- Paytable is the §3.1 calibrated table at scale 1.0 (unchanged for all three).
- Helper: `.runtime/block_cave/measure_cand_general.py`
  (accepts optional `start_seed`).

---

## 4. Results (OOS, start_seed = 1_000_000, n = 200k + 20k forced)

### 4.1 Natural RTP

| Config | Natural RTP | 95% CI | std | Base RTP | Feature RTP |
|---|---|---|---|---|---|
| §3.1 baseline | **0.96462** | [0.9566, 0.9727] | 1.834 | 0.89791 | 0.06670 |
| **Candidate A** | **0.96245** | [0.9544, 0.9705] | 1.837 | 0.90434 | 0.05811 |
| **Candidate B** | **0.96425** | [0.9567, 0.9718] | 1.732 | 0.90480 | 0.05945 |

All three point estimates fall **inside** the 96.0–96.7% hard band. **The 95% CI
straddles the 96.0% lower edge for all three** (std ≈1.7–1.8), so "in band" is a
**point-estimate** statement, not a robust certification — consistent with the
Candidate 2 framing in `CANDIDATE2_REPORT.md` §11/§15 (a certification-scale
sample ≥500k–1M rounds is needed for a firm in/out-of-band claim).

### 4.2 Ore-vein RTP contribution (enabled − disabled)

| Config | Disabled RTP | Ore-vein Δ (pp) | Sign |
|---|---|---|---|
| §3.1 baseline | 0.97683 | **−1.2215** | ❌ negative |
| **Candidate A** | 0.96151 | **+0.0943** | ✅ positive |
| **Candidate B** | 0.96149 | **+0.2760** | ✅ positive (stronger) |

Switching to the `create-cluster` rule makes the ore-vein upgrade **positive**
for both candidates. Candidate B (silver removed) gives the **stronger** positive
Δ (+0.2760 pp vs +0.0943 pp). The §3.1 baseline rule is **negative** (−1.2215 pp).

### 4.3 Profile (hit / full / entry)

| Config | Visible hit | Full return | Free-spin entry | Entry 95% CI |
|---|---|---|---|---|
| §3.1 baseline | 0.69856 | 0.29087 | 0.00676 | [0.0064, 0.0071] |
| **Candidate A** | **0.69784** | 0.29417 | 0.00676 | [0.0064, 0.0071] |
| **Candidate B** | 0.67919 | 0.28158 | 0.00686 | [0.0065, 0.0072] |

- **Candidate A** holds a high visible hit ≈**0.70** (≈70%), matching the
  baseline (0.6986).
- **Candidate B** is slightly lower (≈0.68) — the silver removal trades ~2 pp of
  visible hit for a stronger positive ore-vein Δ.
- Entry ≈**0.68%** for all three (pickaxe = 3). **Exactly 1% is not reachable**
  with integer pickaxe counts (see §6).

### 4.4 Feature payout & duration

| Config | feat_pay mean (natural) | feat_pay mean (forced) | feat_pay median (forced) | dur mean | dur max |
|---|---|---|---|---|---|
| §3.1 baseline | 9.8676 | 9.6135 | 7.48 | 8.787 | 24 |
| **Candidate A** | **8.5960** | **8.3208** | 7.52 | 8.846 | 28 |
| **Candidate B** | **8.6605** | **8.3303** | 7.54 | 8.874 | 32 |

Both candidates keep the feature payout inside the **8–12×** band (≈8.3×
forced). The baseline is also in band but nearer the top (≈9.6×). Free-spin
durations are short (mean ≈8.8, max 24–32, well under the 60 retrigger cap).

### 4.5 Tail / risk (max_round, P(≥100×))

| Config | max_round | P(≥100×) | P(≥500×) | P(≥100×) forced |
|---|---|---|---|---|
| §3.1 baseline | 286.89 | 1.50e-05 | 0.0 | 3.00e-04 |
| **Candidate A** | **424.90** | 1.00e-05 | 0.0 | 5.00e-05 |
| **Candidate B** | 59.31 | **0.0** | 0.0 | 0.0 |

- **Candidate A** has a **meaningful tail** (max 424.9×, P(≥100×) ≈1e-05 ≈1 in
  100k) — comparable to or slightly larger than the baseline max (286.9×).
- **Candidate B has NO ≥100× tail** (max 59.31×, P(≥100×)=0). This is the main
  cost of the silver removal.

### 4.6 Dry streaks / consistency

| Config | P(zero-run ≥10) | P(zero-run ≥20) | max_zero_run | violations |
|---|---|---|---|---|
| §3.1 baseline | 1.00e-05 | 0.0 | 10 | 0 |
| **Candidate A** | 1.00e-05 | 0.0 | 10 | 0 |
| **Candidate B** | 1.00e-05 | 0.0 | 11 | 0 |

All three have **low dry streaks** (max zero-run ≈10–11) and **0 consistency
violations**.

---

## 5. Which candidate satisfies all constraints?

| Constraint | §3.1 baseline | **Candidate A** | Candidate B |
|---|---|---|---|
| 96.0–96.7% RTP band (HARD) | ✅ 0.9646 | ✅ 0.9624 | ✅ 0.9643 |
| Positive `create-cluster` ore-vein | ❌ −1.22 pp | ✅ +0.09 pp | ✅ +0.28 pp |
| High visible hit ≈70% | ✅ 0.699 | ✅ 0.698 | ⚠️ 0.679 |
| Low dry streaks (max_zero ≤11) | ✅ 10 | ✅ 10 | ✅ 11 |
| Feature payout 8–12× | ✅ 9.6× | ✅ 8.3× | ✅ 8.3× |
| Short free spins (≤60 cap) | ✅ | ✅ | ✅ |
| Meaningful tail (≥100×) | ✅ 286.9× | ✅ 424.9× | ❌ 59.3× |
| ≤2 new DEV config files | — | ✅ | ✅ |
| `game_config.py` unchanged | — | ✅ | ✅ |

**Recommendation: Candidate A satisfies ALL constraints.** It keeps the RTP in
band, makes the ore-vein upgrade positive, holds a high visible hit (≈0.70), low
dry streaks, an 8–12× feature, short free spins, **and** a meaningful tail
(max 424.9×).

**Candidate B is a valid alternative but weaker on the priority axes.** It
delivers a stronger positive ore-vein Δ (+0.28 pp) but costs ~2 pp of visible
hit (0.679) and **removes the ≥100× tail entirely** (max 59.31×). It does land in
the RTP band on this OOS range, but it is a **strictly worse** profile than
Candidate A on the stated priorities (hit + tail), so Candidate A is preferred.

---

## 6. Unachievable combinations (documented openly)

- **Exact 1% free-spin entry is NOT reachable with integer pickaxe counts.**
  The natural 3+ pickaxe entry is a discrete function of the number of pickaxes
  on the strip: pick=3 gives ≈**0.67–0.68%**, pick=4 gives ≈**1.5–1.7%**. There is
  no integer pickaxe count that yields exactly ≈1.0%. Both candidates keep
  pick=3 to preserve the high-hit priority (entry ≈0.68%).
- **Silver removal trades hit and tail for ore-vein Δ (Candidate B).** Removing
  Silver Ore yields a stronger positive `create-cluster` contribution but lowers
  the visible hit (0.68 vs 0.70) and removes the ≥100× tail. It is **achievable**
  and lands in the RTP band on this OOS range, but it is not a strict
  improvement — it is a profile trade.
- **Silver-removal base RTP is high-variance / bimodal.** Under the positive
  `create-cluster` rule, small premium/ore_vein rebalances swing the silver-
  removed base RTP sharply (screening saw ≈0.79–1.16 across nearby
  compositions). Candidate B (S6) is the composition that lands in band OOS; it
  is **not** robust to re-seeding / small rebalances.

---

## 7. Reproducibility

Config files are frozen by SHA-256 of the generated strips:

- `candidate_a_config.py`: BASE_SHA `33e6f349…a463c5`, FREE_SHA `12096d9f…440687`.
- `candidate_b_config.py`: BASE_SHA `2295935d…763f27`, FREE_SHA `12096d9f…440687`.
- The §3.1 baseline strips are unchanged (verified by `test_block_cave.py`).

Both configs pass `python math/games/block_cave/candidate_a_config.py` /
`candidate_b_config.py` self-checks (length 200, counts + SHA-256 match), and
`test_block_cave.py` includes `test_candidate_a_config_reproducible` and
`test_candidate_b_config_reproducible`.

---

## 8. Limitations

- **Not a production certification.** No published RTP claim. Nothing deployed.
- **RTP CI (variance limit, not a hard wall):** all three RTP CIs straddle the
  96.0% lower edge (std ≈1.7–1.8). A certification-scale sample (≥500k–1M rounds
  or a multi-range aggregate) is required before a firm in/out-of-band claim.
- **Single OOS range.** Results are for one fresh range (start_seed=1_000_000).
  A second disjoint range (as QA did for Candidate 2) would move each point
  estimate by several tenths of a percent.
- **All six reels share one 200-symbol strip**, so the base RTP is
  seed-sensitive. Candidate A/B base seeds were chosen for a good
  base/entry/hit/tail balance.
