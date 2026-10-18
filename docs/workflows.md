# Minimizer workflows

[Quick start and limits](../README.md) · [Runnable evidence](../README.md#runnable-evidence)

These are prompts you can adapt, not registered commands. Enabling the plugin adds its static default guidance; none of these phrases activates a hidden mode.

## Build the smallest complete change

1. State the required behavior, public API, failure behavior, and safeguards.
2. Ask Hermes to trace the existing owner and reuse opportunities before editing.
3. Implement the first fitting approach, preserving repository instructions and approval boundaries.
4. Run the required tests and the smallest sufficient proof. Report observed results and unresolved work, not assumed completion.

Copyable prompt:

> Implement [requirement]. First trace the relevant callers, state changes, and failure paths. Reuse existing behavior or the responsible layer where it fits without distortion. Avoid speculative layers. Preserve all requirements and safeguards, follow this repository's test-first rules, and verify the result.

This is not a request to shorten code at any cost. A necessary abstraction or a coherent wider refactor can be the simpler complete design.

## Advisory over-engineering review

Use this when you want findings before edits:

```text
Review [files or diff] for over-engineering. ADVISORY ONLY: do not edit.
Trace behavior and invariants before suggesting a cut. Look for existing
behavior to reuse, one-implementation scaffolding without a real purpose,
and speculative extension points. Keep every requirement and safeguard.

For each actionable finding provide:
- file:line (use actual source locations)
- tag: reuse / unnecessary-layer / speculative-feature
- proposed cut or replacement, and why its semantics fit
- tests or invariants that must remain true, including failure paths

Do not invent line totals or claim tests ran when they did not.
If no safe cut exists, say so. Use "Lean already. Ship." only when the
review is complete, no actionable findings or unresolved requirements
remain, and the required verification has actually passed. Otherwise
report findings, missing evidence, or blockers.
```

Findings are proposals, not permission to bypass approval. Authorize edits separately when appropriate; then rerun the required checks against the actual change.

## Plugin vs. optional skills

This repository is a **native Python plugin**: one `minimizer.guidance` section registered through `PluginContext.register_system_prompt_section`. It does not install a skill, Journey kit, command, scanner, or auto-fixer. The [policy](../policy.md) is the packaged guidance source.

Skills can supply optional, task-specific procedures alongside that default. A separately installed skill also called Minimizer is not this plugin, and its presence or behavior is not verified by this repository. No Journey install is required. We do not bundle or register a second skill here.

[Ponytail](https://github.com/dietrichgebert/ponytail) informed some principles; [provenance and its MIT notice](../THIRD_PARTY_NOTICES.md) are included. That is not a claim that this plugin ships Ponytail executable code or the contents of an independently installed skill.

System, user, and repository requirements outrank the default guidance, with or without optional skills. Preserve authorization, trust-boundary validation, security, data-loss prevention, required error handling, accessibility, calibration, migration/rollback safety, concurrency protection, compatibility, and required tests.
