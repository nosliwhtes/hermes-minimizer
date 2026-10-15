# Hermes Minimizer

A native Hermes Python plugin that adds simplest-complete-system guidance through `PluginContext.register_system_prompt_section`.

The plugin contributes static guidance. It does not intercept tools, edit conversation history, make network requests, add dependencies, or enforce outcomes.

## Requirements

- Hermes Agent 0.22.0 or newer
- The native `register_system_prompt_section` plugin API

Older or incompatible Hermes versions fail plugin registration with an upgrade message. There is no monkeypatch fallback.

## Install

```bash
hermes plugins install nosliwhtes/hermes-minimizer --enable
```

Start a new Hermes session or process after enabling. Existing persisted prompts can retain the section bytes with which they were created.

## Verify

```bash
hermes plugins doctor hermes-minimizer --ci
hermes plugins list --enabled --plain
```

Doctor exercises Hermes' real manifest discovery, import, and registration contracts. The test suite additionally verifies native rendering and actual system-prompt assembly.

## Disable or remove

```bash
hermes plugins disable hermes-minimizer
# Start a new Hermes process/session to remove the guidance from new prompts.

hermes plugins remove hermes-minimizer
```

Disabling is config-only in a running process. A prompt already persisted for a session may retain its frozen plugin section.

## Upgrade and compatibility

```bash
hermes plugins update hermes-minimizer
```

Version 0.1.0 is tested against Hermes source commit `e06df9c2eae6901f4c88f464e0ae6e753c0428b8`. Compatibility is capability-based as well as version-gated: registration requires the native prompt-section method and fails visibly if it is absent.

## Limits

- Guidance influences model behavior but does not guarantee simplicity, correctness, safety, or test coverage.
- It is not a sandbox, authorization layer, policy enforcement engine, or test runner.
- System, user, and repository instructions remain higher priority.
- Static guidance is deterministic, but model responses are not.
- Changes take effect at Hermes' normal plugin/session lifecycle boundaries, not retroactively inside persisted prompts.

## Development

Use the official Hermes source and lockfile as the test environment:

```bash
git clone https://github.com/NousResearch/hermes-agent.git ../hermes-agent
git -C ../hermes-agent checkout e06df9c2eae6901f4c88f464e0ae6e753c0428b8
uv sync --project ../hermes-agent --locked --python 3.14 --group dev

HERMES_SOURCE="$(cd ../hermes-agent && pwd)" \
  uv run --project ../hermes-agent pytest tests -q
uv run --project ../hermes-agent hermes plugins doctor . --ci
uv run --project ../hermes-agent hermes plugins validate .
```

See `CONTRIBUTING.md` for the change contract and `THIRD_PARTY_NOTICES.md` for provenance.

## License

MIT. Copyright (c) 2026 Seth Wilson.
