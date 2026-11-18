# Game specification — Block Cave (working title)

Status: product direction agreed on 2026-11-17; math implementation is pending
the detailed paytable and simulation. Block Cave is a placeholder name.

## Product intent

- Original, adult-oriented block-cave world with unique textures, names and
  character. Six columns and five visible rows, readable at 1200×675 and
  400×225.
- Frequent visible small wins, including payouts below the play amount;
  shorter, more frequent free-spin rounds. No claim of frequent profit or
  streak-free play.
- Maximum payout per round: **1,000× the base play amount**. Apply the cap
  consistently to base and any future priced mode; confirm exact Engine units.
- Use `math/games/0_0_cluster` and `frontend/apps/cluster` as references,
  preserving both official examples and creating a separate game.

## Draft round flow

1. The Python math engine selects the entire outcome book. The frontend
   animates its ordered events and never invents a payout or symbol outcome.
2. Five or more orthogonally connected identical regular symbols form a
   winning cluster on a 6×5 board. Winning blocks disappear and new blocks
   fall in; repeat until no cluster remains.
3. An **ore-vein** symbol is a wild for regular cluster matching. When its
   agreed activation condition is met, it upgrades orthogonally adjacent
   regular blocks. The engine records positions and upgraded symbol IDs in
   the book. Exact activation timing, targets and multiple-vein behavior
   require math/frontend contract design.
4. **Three pickaxe symbols** trigger a short free-spin round. Initial spin
   count, retrigger and frequency are to be proposed and simulated, with an
   explicit cap on bonus length. The pickaxe is a scatter, not the wild.
5. A preselected, separately priced bonus mode is deferred beyond the first
   version, per the user's long-term preference. If added later, it needs
   its own costs, RTP, max win, confirmation UI and complete rules.
6. The user likes a free-spin bonus upgrade that retains a small guaranteed win. Current
   Engine approval guidelines prohibit gamble features and continuation, so
   no player-selected wager/upgrade is in this implementation. An automatic,
   predetermined bonus-tier upgrade within a single book remains a research
   item until Engine confirms its acceptability. This is separate from the
   ore-vein symbol converting a neighboring block during an ordinary round.

## Symbol hierarchy

| Class | Draft symbols | Purpose |
| --- | --- | --- |
| Common | earth, stone, timber, copper-bearing stone | frequent smaller cluster pays |
| Premium | lapis-bearing stone, gold-bearing stone, emerald-bearing stone, diamond-bearing stone | larger, less frequent pays |
| Rare top symbol | original dark fantasy-alloy block; final name pending | highest regular-symbol pay |
| Special | ore vein; pickaxe | wild and adjacent upgrade; free-spin scatter |

Every ore is a cubic stone block with the material embedded in its face.
The rare symbol uses math ID `ingot` and art ID `fantasy_alloy_ingot` but is
drawn as an original dark alloy block. No Minecraft or Roblox names, character
likenesses, textures or assets may be used.

## Math targets and evidence

Provisional RTP target: **96.3% for each mode**, within the Engine's current
96.0–96.7% band. This is a design target, not a measured result. The current
official math page also requires the cheapest mode at 1.0× cost and standard
deviation at least 0.6 for 1.0× modes:
https://stake-engine.com/docs/approval-guidelines/math-verification

Before coding, the math agent must propose the paytable, symbols/reel
weights, free-spin count and rate, retrigger cap and ore-vein event rules.
The orchestrator and QA must verify the resulting weighted distributions:

- `P(payout > 0)` (visible hit) and `P(payout >= play amount)` (full return),
  reported separately.
- Zero-win streak frequencies at 10 and 20 rounds. Even a high hit rate
  cannot guarantee that a 20-round dry streak never occurs.
- Free-spin entry frequency, length, average and median payout.
- RTP, standard deviation, payout percentiles, maximum-win frequency and
  consistency between book events and serialized payout multiplier.

No actual hit frequency or bonus frequency has been claimed yet.

## Engine, approval and communication contract

- Python owns all random selection and payouts. Agree any new book-event
  type, order, units and resume behavior with TypeScript before parallel
  implementation. See `ENGINE_CONTRACT.md`.
- Publication math requires matching compressed result books, integer
  payout lookup tables and index. Source:
  https://github.com/engineio/docs/blob/main/src/routes/faq/math/what-files-are-required/%2Bpage.svx
- Storybook acceptance cases: normal win, no win, tumble, vein activation,
  free-spin trigger/end, replay/resume, win cap and errors using real generated
  books. Test desktop, mini and expanded mini, including console/network.
- Social-mode wording must be correct across UI, rules, loader and replay.
  Mode names must match across math/UI/replay. Source:
  https://stake-engine.com/docs/approval-guidelines/jurisdiction-requirements
  For `social=true`, replace gambling terms in visible copy: e.g. `bet` →
  `play`, `buy bonus` → `get bonus`, `cash` → `coins`, and use `win` in place
  of `pay` where it describes a result. Do not show dollar signs for XSC/XGC.
  Check the current jurisdiction matrix before drafting final copy; other
  contexts and locales need their own review.
- A mode costing over 2× base requires a confirmation step and clearly
  presented cost, RTP, max win and trigger rules. Source:
  https://stake-engine.com/docs/approval-guidelines/front-end-communication
- No third-party IP or visuals particularly appealing to minors. Sources:
  https://stake-engine.com/docs/approval-guidelines and
  https://www.minecraft.net/en-us/usage-guidelines

## Remaining product decisions

- Final game and fantasy-alloy names.
- Exact paytable and relative symbol frequencies, free-spin length/rate,
  retrigger cap and vein activation rules, to be proposed from simulations.
- A separately priced bonus mode is deferred beyond the first release.
- Any automatic free-spin bonus-tier upgrade needs a clear book contract and
  platform confirmation; the player-selected gamble version is excluded.
