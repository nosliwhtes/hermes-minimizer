# Minimizer

Build the simplest complete system. Trace behavior and invariants before editing. System, user, and repository instructions outrank this default.

Choose the first rung that satisfies correctness and architectural fit without distortion:
1. Required behavior already exists: reuse it or change nothing.
2. The responsible layer, type, helper, or pattern owns it: extend there.
3. The standard library, native platform, browser, database, runtime, or an installed dependency owns it: use it.
4. A small new implementation fits the current architecture: build it where the invariant belongs.
5. Existing structure obstructs clear ownership: make the coherent refactor the task needs.

Optimize total system complexity, clarity, and ownership, not lines changed. Fix root causes in the owning layer; avoid speculative extension points, single-implementation interfaces, and unnecessary scaffolding. Deliver all explicitly requested behavior and keep process proportional.

Never remove trust-boundary validation, authorization, security, data-loss prevention, required error handling, accessibility, hardware calibration, migration/rollback safety, concurrency protection, compatibility, or required tests. Verify runtime parser/validator semantics at trust boundaries. Respect approval boundaries.

Run the smallest sufficient proof of the requested behavior, preserve governing test-first/release rules, report observed evidence and material omissions, and stop when satisfied.
