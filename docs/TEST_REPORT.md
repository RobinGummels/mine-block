# Test report — original project

Date: 2026-11-17. Project:
`C:\Users\robin\Documents\stake\stake-game-ai`.

| Check | Result |
| --- | --- |
| `scripts/setup.ps1 -Rust` | Passed: 36 pnpm workspaces, isolated math venv, QA npm packages, Chromium, and locked Cargo check |
| `scripts/setup.ps1 -SkipMath -SkipBrowser` after package update | Passed: frozen lockfile, no downloads |
| Isolated Python dependency check | `pip check` passed with SDK pins NumPy 2.2.5 and zstandard 0.23.0 |
| Upstream Lines pytest suite | 13 passed; no warnings in the final run |
| Official Lines math smoke | 100 conditional rounds, free-spin events, seeded replay and zstd round-trip passed |
| Locked optimizer `cargo check` | Passed; upstream compiler warnings remain |
| Storybook Windows startup | Passed on `http://127.0.0.1:6001` |
| Playwright desktop | Passed at 1200 × 675: visible canvas, Action resolved, screenshots captured |
| Playwright mini | Passed at 400 × 225: visible canvas, Action resolved, screenshots captured |
| OpenCode config and agents | Parsed under OpenCode 2.3.0; five agents and `unigpt/DeepSeek-V4-Flash` discovered |
| UniGPT authentication/model tool call | Pending a new user-held API key; no old key used |
| Context7 | Disabled; connection not claimed |

The final Playwright run passed **2/2 tests in 16.8 minutes** with a warm Vite
cache. The first cold desktop attempt timed out after 20 minutes at the
Storybook spinner while Vite compiled and re-optimized dependencies. After
that compilation completed, both viewports loaded and the Action finished.
Artifacts are under `.runtime/playwright-results` and
`.runtime/playwright-report`. The inspected images show the existing Lines
example, not a newly developed game.

The optional Adobe Typekit font reported `Web font load inactive` on localhost.
The SDK treats this as a fallback and continues. QA excludes only this exact
console message; every other console error, JavaScript exception, failed
request and HTTP error remains a failure. The stock example's translation
test overlay clips at the 400 × 225 embed size.

The math smoke books SHA256 is
`3b1208d33fe7e2fb3e53cc5974e7c166a6baf0ba567687c017711c77eba2f97f`.
It is a conditional development sample, not an RTP estimate. No large
optimizer simulation or production certification was run. A static Storybook
production build was started but stopped during the slow Vite transform; the
validated path is the Storybook development server and browser QA.
