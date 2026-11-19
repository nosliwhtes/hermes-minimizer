# Changelog

## 0.2.0 — 2026-11-19

- Expand `policy.md` with proportional-process and trust-boundary runtime-parser verification guidance, and add `policy-compact.md` (~1,490 chars) for tighter shared prompt budgets.
- Declare native `config_schema` (`preset`: `standard`/`compact`, `extra_guidance`: bounded team/repo addendum) so Desktop **Settings -> Plugins** renders a form automatically.
- Sanitize reserved persistence markers and enforce Hermes' 4,000-character section cap on `extra_guidance` so malformed settings cannot cause Hermes to skip the section.
- Register the read-only `/minimizer [status|policy|review]` slash command via `ctx.register_command`.
- Verify compatibility with `plugins.isolation: host`, pin `actions/checkout` in CI to a full commit SHA, update the CI matrix to Hermes `v0.22.0` and `v0.23.2`, and prevent lazy PM re-syncs inside isolated test homes.

No tools, hooks, middleware, network calls, telemetry, or runtime dependencies were added. Model effectiveness remains unmeasured.

## 0.1.1 — 2026-10-18

- Rework onboarding around a reviewed catalog install, a first useful review prompt, verification, lifecycle guidance, and explicit limits.
- Add ordinary-language build/review workflows without registering another skill or command; move detailed development setup to its own page.
- Add two authored, executable before/after examples with behavior contracts, a stdlib verifier, physical-line counts, and pytest integration.
- Add fixture-walkthrough media links with a static alternative and explicit non-benchmark labeling.
- Improve discovery metadata for code review, refactoring, reuse, and over-engineering; document execution-tested official Hermes revisions.

Runtime and policy are unchanged from 0.1.0: one static native system-prompt section, no additional tools, hooks, telemetry, or runtime dependencies. Model effectiveness and usage impact remain unmeasured.

## 0.1.0

- Initial native plugin with static simplest-complete-system guidance and real Hermes integration tests.
