"""Native Hermes plugin that contributes Minimizer guidance to the system prompt."""

from pathlib import Path


def register(ctx) -> None:
    register_section = getattr(ctx, "register_system_prompt_section", None)
    if not callable(register_section):
        raise RuntimeError(
            "hermes-minimizer requires Hermes >=0.22.0 and "
            "PluginContext.register_system_prompt_section; upgrade Hermes before enabling it"
        )

    policy = Path(__file__).with_name("policy.md").read_text(encoding="utf-8").strip()
    register_section("minimizer.guidance", policy, position="after_memory")
