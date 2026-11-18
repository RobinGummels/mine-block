# Windows setup

Prepared on 2026-11-17 for OpenCode 2.3.0, Node 22.23.5, pnpm 10.5.0 and
Python 3.13.2. Read STATUS.md for actual completed checks and blockers.

## Entry points

From the project directory in PowerShell:

```powershell
.\scripts\setup.ps1
.\scripts\test-setup.ps1 -Browser -Rust
.\scripts\start-storybook.ps1
```

Setup installs frontend dependencies from the existing frozen lockfile,
creates math/.venv, installs the checked-out math package and its requirements,
then installs the separate qa/ Playwright dependencies and Chromium. Use
`setup.ps1 -Rust` to check the optimization crate too. It needs registry
access and the Windows Rust build prerequisites. No global Python removal,
Node upgrade or Make installation is required. Tools use the .venv interpreter
directly; activation is optional.

The SDK requirements file includes an editable remote Git dependency. The
new requirements-local.txt retains the listed dependencies while setup
installs the existing checkout itself, preventing a second SDK checkout.
The upstream unpinned toml and matplotlib requirements are retained.

## Storybook

Open http://127.0.0.1:6001/?path=/story/mode-base-book--random and select
MODE_BASE / book / random. Wait for the scene and the Action button to become
enabled, then click Action. The action must finish and the scene must render.
Some component stories intentionally display the loading screen.

The Lines start script uses cross-env for Windows. The preview exports an
object literal around the shared preview configuration so Storybook can parse
it. `@storybook/addon-svelte-csf` is updated from 5.0.5 to 5.0.9. The large
official base-book fixture is served as static JSON, and Lines asset paths
point to the files in `static/`. A cold Vite load exceeded twenty minutes on
this machine; the cached browser test passed. The automated check allows up
to 45 minutes per viewport for a cold cache. Wait for Vite transforms to
finish before treating the first spinner as a permanent failure.

The automated browser test also checks a visible, nonzero canvas, finishes
the Action, captures screenshots and fails on JavaScript, console, HTTP or
network errors except the SDK's exact `Web font load inactive` message. The
optional Adobe Typekit font falls back on localhost. Inspect screenshots in
.runtime/playwright-results and the HTML report in .runtime/playwright-report.
It checks desktop and mini; the stock translation overlay clips at mini size.
qa/package-lock.json is created during the first successful install; retain it.

## Math

```powershell
.\math\.venv\Scripts\python.exe -m pytest .\math\tests -q
.\math\.venv\Scripts\python.exe .\scripts\math_smoke.py
```

Prefer test-setup.ps1 because it sets the correct working directory for the
upstream test suite. The smoke uses the official Lines logic for one hundred
conditional rounds, repeats the seeds and checks compressed books. It writes
only to .runtime/math-smoke and does not alter production books. It does not
measure RTP and does not launch the repository's large optimization defaults.

## OpenCode and a new UniGPT key

```powershell
.\scripts\test-unigpt.ps1
.\scripts\start-agent.ps1
```

Both scripts request a NEW key using hidden input. The connection check sends
only GET /models and verifies the configured model ID, without generation.
The launcher uses a private server (--standalone), passes the key to the child
process and restores the previous
environment afterward; it does not save the key to a file. For a key you have
deliberately set in UNIGPT_API_KEY, use start-agent.ps1 -UseEnvironmentKey.
Alternatively use OpenCode /connect to store a fresh key in its local auth
store. Revoke the previously exposed key in UniGPT; it was not reused here.

OpenCode 2.3.0 uses providers/package/settings, agents/ Markdown files, and
mcp.servers. Do not replace them with OpenCode V1 provider/npm/options or
singular agent syntax. The project model is unigpt/DeepSeek-V4-Flash. Its
context/output limits retain the prior 128000/8000 values and need provider
confirmation. Image input is not advertised until verified.

The five agents are orchestrator, math, frontend, art and qa. They receive
disjoint file ownership in AGENTS.md; this is coordination guidance, not an
OS sandbox. No blanket auto-approval flag was added. The four project skills
are locally authored workflows, not installations in the ChatGPT skills UI.

Context7 is configured but disabled until its connection can be checked.
To enable it, set mcp.servers.context7.disabled to false, then run
`opencode mcp list --standalone`. If the public server requires a key, configure
it through an environment reference. Playwright runs locally through qa/;
there is no unverified browser MCP startup dependency. Superpowers was not
installed: it adds no necessary capability to this prepared workflow.

The reported UniGPT limits (four concurrent requests, thirty requests/minute,
one million tokens/minute, five credits/four hours and fifty/week) have not
been verified through an authenticated portal. The orchestrator starts with
at most two concurrent requests. This is not an enforced API rate limiter.

## References

- https://github.com/engineio/web-sdk
- https://github.com/engineio/math-sdk
- https://opencode.ai/docs/config/
- https://opencode.ai/docs/providers/
- https://opencode.ai/docs/agents/
- https://opencode.ai/docs/skills/
- https://opencode.ai/docs/mcp-servers/
- https://github.com/microsoft/playwright/releases/tag/v1.56.1
