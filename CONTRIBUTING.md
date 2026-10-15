# Contributing

Keep the plugin bounded to one static native system-prompt section.

1. Trace the current Hermes discovery, registration, rendering, and prompt-assembly contracts before editing.
2. Write a failing behavior test first and preserve the RED result.
3. Keep `policy.md` as the single packaged policy source and below Hermes' 4,000-character default section limit.
4. Add no runtime dependency, network call, telemetry, hook, hidden state, core patch, or per-turn history edit.
5. Run the full commands in the README against the pinned official Hermes source before requesting review.

Public files must not contain private data, business context, credentials, transcripts, local absolute paths, or internal planning artifacts.

Changes to policy semantics must preserve instruction precedence, the five ordered decision rungs, no-distortion rule, responsible-layer/root-cause ownership, explicit requested behavior, safeguards, approval boundaries, sufficient proof, and truthful completion.

By contributing, you agree that your contribution is licensed under the MIT License in `LICENSE`.
