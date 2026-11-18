# Eigenes Stake.com Game

Prepare and later implement a Stake Engine game using the official SDKs. Read
docs/GAME_SPEC.md, docs/ENGINE_CONTRACT.md and docs/STATUS.md before editing.
The product direction is recorded in docs/GAME_SPEC.md. Treat its open math
values and branding as proposals until the user approves them. Do not claim a
measured RTP or a production release. Keep the official Lines example intact.

## Ownership and integration

The orchestrator owns opencode.jsonc, scripts/, qa/, docs/ and integration.
Delegate frontend/ to the frontend agent, math/ to the math agent, art/ to the
art agent. QA reports findings and owns test reports, not implementation files.
Every code change needs an independent QA pass by an agent other than its
author before the orchestrator accepts it. The author fixes reported issues;
QA reruns the affected checks.
Before delegating, assign specific files. Never give two running agents the
same file or a shared lockfile. Sequence shared changes through the orchestrator.
Use at most two simultaneous model requests initially. The reported UniGPT key
limits are four concurrent requests and thirty per minute; verify in the portal.
Stop and report rate limits rather than retrying without a bound.

## Development

- Windows and PowerShell are the primary environment. Use scripts/ entry points.
- Keep Node 22 and pnpm 10.5.0; preserve frontend/pnpm-lock.yaml.
- Keep game rules and payouts in Python. Replay server results in the frontend.
- Read the actual SDK types and examples before changing event contracts.
- Use a small reproducible simulation before large runs or optimisation.
- Run relevant checks and update docs/STATUS.md with evidence and limitations.
- Read command exit codes. Starting a server is not proof of a working game.
- Browser checks must include loaded canvas, resolved Action, console/network
  errors and desktop/mini screenshots. A loader is not a passing result.
- Never print or commit credentials. Use UNIGPT_API_KEY or OpenCode /connect.
- Never publish, deploy, upload production books or perform real-money actions
  as part of routine development. Ask for explicit release instructions.
- Preserve existing local changes. Do not commit generated libraries or caches.

## Local checks

PowerShell from this directory:

```powershell
.\scripts\setup.ps1
.\scripts\test-setup.ps1 -Browser -Rust
.\scripts\start-storybook.ps1
.\scripts\start-agent.ps1
```

Use the project skills for design, interface review, engine validation and
visual QA. Context7 is optional and disabled until its connection is verified.
