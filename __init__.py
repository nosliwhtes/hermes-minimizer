"""Native Hermes plugin that contributes Minimizer guidance to the system prompt."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

SECTION_ID = "minimizer.guidance"
SECTION_POSITION = "after_memory"
MAX_SECTION_CHARS = 4_000
SHARED_BUDGET_CHARS = 8_000
DEFAULT_PRESET = "standard"

_POLICY_FILES = {
    "standard": "policy.md",
    "compact": "policy-compact.md",
}
_RESERVED_MARKERS = (
    "<!-- hermes-plugin-sections:start -->",
    "<!-- hermes-plugin-sections:end -->",
)
_EXTRA_HEADING = "\n\n## Additional guidance\n\n"
_TRUNCATION_SUFFIX = "..."

_ADVISORY_REVIEW_PROMPT = """\
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
report findings, missing evidence, or blockers."""


def _load_policies() -> dict[str, str]:
    root = Path(__file__).resolve().parent
    return {
        name: (root / filename).read_text(encoding="utf-8").strip()
        for name, filename in _POLICY_FILES.items()
    }


def _read_settings(ctx: Any) -> tuple[str, str]:
    get_config = getattr(ctx, "get_config", None)
    if not callable(get_config):
        return DEFAULT_PRESET, ""

    raw_preset = get_config("preset", DEFAULT_PRESET)
    preset = raw_preset.strip().lower() if isinstance(raw_preset, str) else DEFAULT_PRESET
    if preset not in _POLICY_FILES:
        preset = DEFAULT_PRESET

    raw_extra = get_config("extra_guidance", "")
    extra = raw_extra.strip() if isinstance(raw_extra, str) else ""
    return preset, extra


def _sanitize_extra(extra: str) -> str:
    for marker in _RESERVED_MARKERS:
        # Keep a separator so removing a marker cannot join two halves of another.
        extra = extra.replace(marker, "\n")
    # Hermes also scans for length frames inside the persisted section body.
    return extra.replace("<!-- hermes-plugin-section-chars:", "&lt;!-- hermes-plugin-section-chars:").strip()


def _render_policy(policies: Mapping[str, str], preset: str, extra: str) -> str:
    base = policies.get(preset, policies[DEFAULT_PRESET])
    cleaned_extra = _sanitize_extra(extra)
    if not cleaned_extra:
        return base

    available = MAX_SECTION_CHARS - len(base) - len(_EXTRA_HEADING)
    if available <= 0:
        return base

    if len(cleaned_extra) > available:
        if available > len(_TRUNCATION_SUFFIX):
            cleaned_extra = cleaned_extra[: available - len(_TRUNCATION_SUFFIX)].rstrip() + _TRUNCATION_SUFFIX
        else:
            cleaned_extra = cleaned_extra[:available]

    return f"{base}{_EXTRA_HEADING}{cleaned_extra}"


def register(ctx: Any) -> None:
    register_section = getattr(ctx, "register_system_prompt_section", None)
    if not callable(register_section):
        raise RuntimeError(
            "hermes-minimizer requires Hermes >=0.22.0 and "
            "PluginContext.register_system_prompt_section; upgrade Hermes before enabling it"
        )

    policies = _load_policies()

    def _current_guidance(_session_info: Mapping[str, Any] | None = None) -> str:
        preset, extra = _read_settings(ctx)
        return _render_policy(policies, preset, extra)

    register_section(SECTION_ID, _current_guidance, position=SECTION_POSITION)

    register_command = getattr(ctx, "register_command", None)
    if callable(register_command):
        def _handle_minimizer(raw_args: str = "") -> str:
            sub = (raw_args or "").strip().lower()
            preset, extra = _read_settings(ctx)
            rendered = _render_policy(policies, preset, extra)
            if sub in ("", "status"):
                extra_state = "set" if _sanitize_extra(extra) else "none"
                return (
                    f"hermes-minimizer ({SECTION_ID})\n"
                    f"- preset: {preset} (choices: standard, compact)\n"
                    f"- extra_guidance: {extra_state}\n"
                    f"- rendered size: {len(rendered)}/{MAX_SECTION_CHARS} chars "
                    f"(shared plugin budget: {SHARED_BUDGET_CHARS} chars)\n"
                    "- note: settings apply to new sessions; resumed sessions keep frozen prompt bytes.\n"
                    "- subcommands: /minimizer [status|policy|review]"
                )
            if sub == "policy":
                return rendered
            if sub == "review":
                return _ADVISORY_REVIEW_PROMPT
            return "Usage: /minimizer [status|policy|review]"

        register_command(
            "minimizer",
            _handle_minimizer,
            description="Show Minimizer status, active policy, or advisory review prompt",
            args_hint="[status|policy|review]",
        )
