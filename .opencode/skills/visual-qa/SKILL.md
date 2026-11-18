---
name: visual-qa
description: Verify actual rendered Storybook gameplay, interactions and browser errors with Playwright.
---
Install qa/ dependencies using scripts/setup.ps1 and run npm test from qa/.
Inspect the resulting screenshots. Verify a visible canvas, an enabled Action
button, a completed example round and responsive layout. Inspect console,
failed requests and HTTP errors. Test at 1200x675 and 400x225. Keep failure
screenshots and traces in .runtime; never include API keys. A successful server
start or a visible loading screen does not satisfy the check. If tools are
blocked, report the missing check rather than asserting visual correctness.
