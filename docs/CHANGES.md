# Applied setup changes

The prepared files below were transferred into the original project. The
existing frontend and math Git repositories were preserved. Two pre-existing
frontend edits were backed up in `.setup-backup`. The existing lockfile was
preserved during transfer, then updated for the tested Storybook addon version.

| File | Change |
| --- | --- |
| .gitignore | Add |
| .opencode/agents/art.md | Add |
| .opencode/agents/frontend.md | Add |
| .opencode/agents/math.md | Add |
| .opencode/agents/orchestrator.md | Add |
| .opencode/agents/qa.md | Add |
| .opencode/skills/frontend-design/SKILL.md | Add |
| .opencode/skills/stake-engine-validation/SKILL.md | Add |
| .opencode/skills/visual-qa/SKILL.md | Add |
| .opencode/skills/web-design-guidelines/SKILL.md | Add |
| AGENTS.md | Add |
| docs/DESIGN_SYSTEM.md | Add |
| docs/ENGINE_CONTRACT.md | Add |
| docs/GAME_SPEC.md | Add |
| docs/SETUP.md | Add |
| docs/STATUS.md | Add |
| docs/TEST_REPORT.md | Add |
| frontend/apps/lines/.storybook/preview.ts | Modify |
| frontend/apps/lines/package.json | Modify |
| math/requirements-local.txt | Add |
| opencode.jsonc | Add |
| qa/package.json | Add |
| qa/playwright.config.mjs | Add |
| qa/tests/lines.spec.mjs | Add |
| scripts/math_smoke.py | Add |
| scripts/setup.ps1 | Add |
| scripts/start-agent.ps1 | Add |
| scripts/start-storybook.ps1 | Add |
| scripts/test-setup.ps1 | Add |
| scripts/test-unigpt.ps1 | Add |
| docs/CHANGES.md | Add |

## Fixes made during installation and browser validation

| File | Change |
| --- | --- |
| scripts/setup.ps1 | Set CI during frozen pnpm install to avoid an interactive prompt on repeat setup |
| qa/playwright.config.mjs | Start PowerShell with `-ExecutionPolicy Bypass` and allow the observed slow cold Vite load |
| qa/tests/lines.spec.mjs | Keep all browser error checks, except the SDK's exact nonblocking Typekit fallback message |
| frontend/apps/lines/package.json | Update `@storybook/addon-svelte-csf` to 5.0.9 |
| frontend/packages/config-storybook/package.json | Match addon version 5.0.9 |
| frontend/pnpm-lock.yaml | Update dependency resolutions for the addon version |
| frontend/apps/lines/src/stories/data/base_books.ts | Move the 10,000 official example books out of the Vite source bundle |
| frontend/apps/lines/static/story-data/base_books.json | Serve those unchanged books as static data |
| frontend/apps/lines/src/stories/ModeBaseBook.stories.svelte | Load the books when Action is clicked |
| frontend/apps/lines/src/game/assets.ts | Use the verified `/assets/` URLs for static resources |
| frontend/apps/lines/src/routes/+layout.svelte | Use static URLs for the existing loader GIFs |
| qa/package-lock.json | Record the installed Playwright QA dependencies |
