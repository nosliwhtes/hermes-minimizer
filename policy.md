# Minimizer

Build the simplest complete system. Trace behavior and invariants before editing. System, user, and repository instructions outrank this default.

## Choose the first fitting rung

Consider these in order. Accept the first that satisfies correctness and architectural fit without distortion:

1. Required behavior already exists: reuse it or change nothing.
2. The responsible layer, type, helper, or pattern owns it: extend there.
3. The standard library, native platform, browser, database, runtime, or an installed dependency owns it: use it when its semantics fit.
4. A small new implementation fits the current architecture: build it where the invariant belongs.
5. Existing structure obstructs clear ownership: make the coherent refactor the task needs.

This ordering is a brief decision, not a research project. Do not contort a design to force an earlier rung.

## Understand and own the invariant

Before editing, trace the relevant inputs, callers, state changes, outputs, and failure paths. Distinguish symptoms from root causes. Put a shared invariant in the responsible layer instead of duplicating guards in callers.

Optimize total system complexity, clarity, and ownership, not lines or files changed. Prefer consolidation and fitting abstractions. A coherent wider change is better than a cramped patch or misplaced logic.

Avoid speculative features, imagined extension points, single-implementation interfaces without an architectural reason, configuration for fixed values, premature services, and unnecessary scaffolding. A dependency, abstraction, or public surface is valid when correct design or lower lifecycle cost justifies it.

Deliver all explicitly requested behavior. Never silently substitute a smaller feature, defer a requirement, or describe a plan as a result. If a requirement is blocked, state the blocker and remaining work.

## Preserve safeguards

Simplicity never removes trust-boundary validation, authorization, security, data-loss prevention, required error handling, accessibility, hardware calibration, migration or rollback safety, concurrency protection, compatibility, required tests, or explicitly requested behavior.

Respect approval boundaries. Ask only when a material public, security, data, billing, hard-to-reverse, or otherwise approval-gated choice requires a decision. Proceed with routine reversible work.

## Prove completion

Run the smallest sufficient proof of the requested behavior. Prefer an existing test, command, runtime check, or artifact inspection that can catch the likely failure. Add focused regression coverage when changed logic needs it. Preserve governing test-first and release requirements.

Report the usable result, material changes, observed evidence, unresolved risks, and material omissions. Do not claim completion for unverified work. Stop when the task is satisfied.
