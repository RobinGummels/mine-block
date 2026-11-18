# Block Cave — staged implementation plan

Status: planning baseline, 2026-11-17. Read `GAME_SPEC.md`,
`DESIGN_SYSTEM.md`, `ENGINE_CONTRACT.md`, `AGENTS.md` and `STATUS.md` first.
The working title and provisional math target are subject to review.

## Product and approval gates

The release candidate is a 6×5 original cave slot with orthogonal clusters
of five or more, tumbles, an ore-vein wild that upgrades adjacent regular
blocks, and three pickaxe scatters that start short free spins. Target
frequent visible small payouts; report visible hits separately from payouts
that return at least the play amount. The maximum round payout is 1,000×.
No result probabilities have been established by the current setup tests.

Stake Engine rules govern the design. In particular, games are stateless;
jackpots, gamble features, continuation and early cashout are prohibited.
Therefore do not build Le Outlaw's player-selected bonus gamble. A future
bonus mode needs its own complete outcome distribution and clear price/rules;
an automatic free-spin bonus-tier upgrade needs platform confirmation before
implementation. The ordinary ore-vein symbol conversion is already part of
the approved game concept and is assessed with the other in-round mechanics.
For `social=true`, apply Stake.us terminology across all visible text,
including rules, loading and replay: `play` instead of `bet`, `get bonus`
instead of `buy bonus`, `coins` instead of `cash`, and no `$` for XSC/XGC.
Check context-dependent wording against the official matrix. Follow the
current official approval,
math, communication and jurisdiction documents:

- https://stake-engine.com/docs/approval-guidelines#key-restrictions
- https://stake-engine.com/docs/approval-guidelines/math-verification
- https://stake-engine.com/docs/approval-guidelines/front-end-communication
- https://stake-engine.com/docs/approval-guidelines/jurisdiction-requirements
- https://stake-engine.com/docs/approval-guidelines/game-replay-requirements

## Stages and handoffs

| Stage | Owner | Deliverable | Independent verifier gate |
| --- | --- | --- | --- |
| 0. Concept lock | Orchestrator + user | `GAME_SPEC.md`, visual direction, open decisions | QA checks traceability to user decisions and official constraints |
| 1. Math proposal | Math agent | paytable, weighted symbols, vein timing, 3-pickaxe trigger, free-spin count/retrigger, 1,000× cap, provisional event schema | QA reviews calculations and states unproven assumptions |
| 2. Math prototype | Math agent | separate game under `math/games/`, deterministic seed, base and free-spin books | QA checks no-win/win/vein/scatter/cap books and reproducibility |
| 3. Math calibration | Math agent | simulation report per mode: RTP, standard deviation, visible hit, full-return hit, dry-streak distribution, feature entry/length, tails | QA reruns independent samples and checks published books/lookup/index consistency |
| 4. Art source | Art agent | original symbols, cave background, optional explorer and source manifest | QA checks originality, asset dimensions, small-size legibility and provenance |
| 5. Frontend contract | Orchestrator with math/frontend | agreed IDs, event sequence, units, replay/resume fixtures | QA checks fixtures against actual generated books |
| 6. Frontend game | Frontend agent | separate app, responsive 6×5 presentation, controls, sounds/motion settings, rules, social wording | QA tests action completion and console/network at desktop, mini, expanded mini |
| 7. Integration | Orchestrator | math/frontend ID and payout agreement, Storybook fixtures, error handling, docs | QA verifies every scenario and replay/resume from real books |
| 8. Release review | Orchestrator | submission package and evidence after explicit release instruction | Independent QA checks current Engine criteria; no automatic publication |

The orchestrator gives each implementation task one owner and a separate QA
reviewer. Code authors do not certify their own work. Keep agent file scopes
disjoint; at most two concurrent model requests at first. The next task is
Stage 2: implement a separate math prototype from the independently reviewed
Stage 1 design, then have QA challenge its books and reproducibility. Stage 4
art prototypes may proceed in parallel because they do not set payouts.

## Decisions before production sign-off

- Treat the reviewed Stage 1 paytable, feature rate, starting free spins,
  retrigger cap and vein behavior as prototype inputs. Revise them after
  Stage 2/3 simulations show the actual tradeoffs; obtain product approval
  before the final game rules and frontend are locked.
- Choose the final original title and fantasy-alloy name before production
  art and public copy.
- The separately priced bonus mode is deferred beyond the first release.
- Obtain platform clarification before considering an automatic free-spin
  bonus-tier upgrade. This is separate from the ore-vein symbol's in-round
  block conversion. A small guaranteed win is a product preference, not an
  approved exception to the no-gamble rule.

## OpenCode Stage 1 task (completed)

Run `scripts/start-agent.ps1` in the original project, then give the
orchestrator this task: "Read AGENTS.md and docs/GAME_SPEC.md,
docs/PROJECT_PLAN.md, docs/ENGINE_CONTRACT.md. Assign Stage 1 to the math
agent, with scope limited to `math/games/block_cave/MATH_DESIGN.md`.
Have the independent QA agent review the proposal and report findings.
Resolve the scatter and vein timing questions in the math design.
Do not implement the game, use third-party art, or add a gamble/continuation
feature yet. Report all unmeasured values as assumptions."
