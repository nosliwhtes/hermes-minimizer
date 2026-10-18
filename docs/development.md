# Development and verification

[README](../README.md) · [Contributing contract](../CONTRIBUTING.md) · [Changelog](../CHANGELOG.md)

## Official locked environment

From the plugin repository root, use the official Hermes source and lockfile. Python 3.14 is the native integration environment; the standalone examples need only stdlib Python 3.10+.

```bash
git clone https://github.com/NousResearch/hermes-agent.git ../hermes-agent
git -C ../hermes-agent checkout e06df9c2eae6901f4c88f464e0ae6e753c0428b8
uv sync --project ../hermes-agent --locked --python 3.14 --group dev

HERMES_SOURCE="$(cd ../hermes-agent && pwd)" \
  uv run --project ../hermes-agent pytest tests -q
uv run --project ../hermes-agent hermes plugins doctor . --ci
uv run --project ../hermes-agent hermes plugins validate .
```

Native integration has also been execution-tested against official commit `548091836760a67e331b8f5643be8e5c08fae1e6`. To reproduce against that revision, check it out in the Hermes clone, repeat the locked sync, and rerun the same commands. No model call is required by this suite.

The tests use Hermes' real plugin manager, native section renderer, and system-prompt assembly. They require `HERMES_SOURCE` pointing to an official source tree and an interpreter with that tree's locked dependencies. Do not substitute a mocked plugin API for compatibility evidence. Doctor and catalog validation do not establish model effectiveness.

## Runnable documentation fixtures

```bash
python examples/check.py
```

This standalone verifier runs both authored before/after pairs against explicit expected behavior and returns nonzero if a check fails. It resolves files relative to its own path, so an absolute script invocation works from another directory. It uses stdlib `unittest`, not pytest or Hermes.

- `ordered_dedup`: stable first-occurrence deduplication for lists of strings. Preserve input, fresh output, case/Unicode/empty strings, empty lists, and type errors.
- `single_renderer`: only `render_message(name, *, style="plain")` is the public API. Preserve output, trimming, Unicode, keyword-only style, blank-name/type errors, and unsupported-style error precedence. The fixture's internal factory and renderer classes are not a compatibility surface.

`tests/test_examples.py` also exercises the contracts and runs the verifier as a subprocess. It checks root/absolute invocation, nonzero failure on a deliberately broken fixture, and consistent counting of imports, comments, and blank lines in disposable copies. CI's existing `pytest tests -q` command includes these tests.

Counts use `len(source.splitlines())` for the four fixture source files only. A trailing newline terminates the last line; it does not create an extra blank line. Counts exclude the verifier and tests. The before versions contain no padding added to inflate the difference. These are illustrative simplifications, not a model benchmark, performance measurement, or promised savings.

## Release contract

Version 0.1.1 changes onboarding, metadata, documentation, and executable examples; `__init__.py` and `policy.md` retain their 0.1.0 bytes. The plugin still registers one static native section and fails visibly without the required API. Examples are never imported by the runtime.

Keep test-first evidence for executable changes. Run the native suite, standalone verifier, doctor, and catalog validator before requesting review. Follow [CONTRIBUTING.md](../CONTRIBUTING.md) for constraints, licensing, and private-data exclusions.

The README's poster, MP4, and GIF illustrate verified fixture checks. They must remain labeled as a scripted walkthrough, not live model output. A static poster is the reduced-motion alternative. Catalog installation follows the catalog's reviewed SHA; a repository release alone does not update it.
