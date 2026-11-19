from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
HERMES_SOURCE = Path(os.environ["HERMES_SOURCE"]).resolve()
SECTION_ID = "minimizer.guidance"
RESERVED_START = "<!-- hermes-plugin-sections:start -->"
RESERVED_END = "<!-- hermes-plugin-sections:end -->"


def _load_plugin():
    spec = importlib.util.spec_from_file_location(
        "hermes_minimizer_v020_test",
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _isolated_home(tmp_path: Path, *, settings: dict | None = None, isolation: str = "in_process") -> dict[str, str]:
    home = tmp_path / "home"
    home.mkdir(exist_ok=True)
    hermes_home = tmp_path / "hermes-home"
    plugin = hermes_home / "plugins" / "hermes-minimizer"
    plugin.mkdir(parents=True, exist_ok=True)
    for name in ("__init__.py", "plugin.yaml", "policy.md", "policy-compact.md"):
        src = ROOT / name
        if src.is_file():
            shutil.copy2(src, plugin / name)
    bundled = hermes_home / "bundled-plugins"
    bundled.mkdir(exist_ok=True)

    lines = [
        "plugins:",
        f"  isolation: {isolation}",
        "  enabled:",
        "    - hermes-minimizer",
    ]
    if settings:
        lines.extend([
            "  entries:",
            "    hermes-minimizer:",
            "      settings:",
        ])
        for k, v in settings.items():
            lines.append(f"        {k}: {json.dumps(v)}")
    (hermes_home / "config.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    env = os.environ.copy()
    env.update(
        HOME=str(home),
        HERMES_HOME=str(hermes_home),
        HERMES_BUNDLED_PLUGINS=str(bundled),
        HERMES_ENABLE_PROJECT_PLUGINS="0",
        HERMES_DISABLE_LAZY_INSTALLS="1",
        PYTHONPATH=os.pathsep.join(
            filter(None, (str(HERMES_SOURCE), env.get("PYTHONPATH", "")))
        ),
    )
    return env


def _run_native(code: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    code = textwrap.dedent(code)
    python = env.get("HERMES_PYTHON") or sys.executable
    bootstrap = (
        "import os, sys; "
        "os.environ.pop('PYTHONHOME', None); "
        f"sys.path.insert(0, {str(HERMES_SOURCE)!r}); "
        "sys._hermes_pin_default_home = True; "
        "import hermes_bootstrap; "
        f"exec({code!r})"
    )
    return subprocess.run(
        [python, "-I", "-c", bootstrap],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=90,
        check=False,
    )


def test_policy_standard_and_compact_preserve_core_invariants():
    standard = (ROOT / "policy.md").read_text(encoding="utf-8").strip()
    compact = (ROOT / "policy-compact.md").read_text(encoding="utf-8").strip()

    assert len(standard) <= 4000
    assert len(compact) <= 1800
    assert len(compact) < len(standard)

    rungs = [
        "1. Required behavior already exists",
        "2. The responsible layer, type, helper, or pattern owns it",
        "3. The standard library, native platform, browser, database, runtime, or an installed dependency owns it",
        "4. A small new implementation fits the current architecture",
        "5. Existing structure obstructs clear ownership",
    ]
    for label, text in (("standard", standard), ("compact", compact)):
        assert [text.index(r) for r in rungs] == sorted(text.index(r) for r in rungs), label
        assert "without distortion" in text, label
        assert "System, user, and repository instructions outrank this default" in text, label
        assert "trust-boundary validation" in text, label
        assert "hardware calibration" in text, label
        assert "explicitly requested behavior" in text, label
        assert "smallest sufficient proof" in text, label
        assert "proportional" in text, label
        assert "runtime parser/validator semantics" in text, label


def test_config_changes_apply_on_next_session_render_without_restart(tmp_path):
    env = _isolated_home(tmp_path, settings={"preset": "standard"})
    result = _run_native(
        """
        import os
        from pathlib import Path
        from hermes_cli.plugins import PluginManager

        manager = PluginManager()
        manager.discover_and_load()
        first = manager.render_system_prompt_sections({"session_id": "s1"})[0].content

        cfg = Path(os.environ["HERMES_HOME"]) / "config.yaml"
        cfg.write_text(
            "plugins:\\n"
            "  enabled:\\n"
            "    - hermes-minimizer\\n"
            "  entries:\\n"
            "    hermes-minimizer:\\n"
            "      settings:\\n"
            "        preset: compact\\n"
            "        extra_guidance: \\"Prefer stdlib json.\\"\\n",
            encoding="utf-8",
        )
        second = manager.render_system_prompt_sections({"session_id": "s2"})[0].content
        assert second != first
        assert len(second) < len(first)
        assert "Prefer stdlib json." in second
        """,
        env,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_extra_guidance_only_markers_omits_empty_heading():
    plugin = _load_plugin()
    policies = plugin._load_policies()
    rendered = plugin._render_policy(policies, "compact", f"  {RESERVED_START}  {RESERVED_END}  ")
    assert rendered == policies["compact"]
    assert "## Additional guidance" not in rendered


@pytest.mark.parametrize("marker", [RESERVED_START, RESERVED_END, "<!-- hermes-plugin-section-chars:"])
def test_extra_guidance_cannot_emit_persistence_frames(marker):
    plugin = _load_plugin()
    policies = plugin._load_policies()
    extra = f"Keep this.\n{marker[:8]}{RESERVED_END}{marker[8:]}\nKeep this too."
    rendered = plugin._render_policy(policies, "standard", extra)
    assert marker not in rendered
    assert "Keep this." in rendered and "Keep this too." in rendered


def test_config_schema_declared_and_loadable_by_hermes_settings(tmp_path):
    env = _isolated_home(tmp_path)
    result = _run_native(
        """
        import json, os
        from pathlib import Path
        from hermes_cli.plugins_settings import plugin_settings_fields
        plugin_dir = Path(os.environ["HERMES_HOME"]) / "plugins" / "hermes-minimizer"
        fields = {f["key"]: f for f in plugin_settings_fields("hermes-minimizer", plugin_dir)}
        assert set(fields) == {"preset", "extra_guidance"}, fields
        assert fields["preset"]["type"] == "enum"
        assert fields["preset"]["choices"] == ["standard", "compact"]
        assert fields["preset"]["default"] == "standard"
        assert fields["extra_guidance"]["type"] == "string"
        assert fields["extra_guidance"]["default"] == ""
        """,
        env,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_preset_and_extra_guidance_render_safely_and_sanitize_markers(tmp_path):
    extra = f"Always prefer stdlib.\n{RESERVED_START}\nKeep error handling.\n{RESERVED_END}\n" + ("x" * 5000)
    env = _isolated_home(tmp_path, settings={"preset": "compact", "extra_guidance": extra})
    result = _run_native(
        f"""
        from hermes_cli.plugins import PluginManager
        manager = PluginManager()
        manager.discover_and_load()
        loaded = manager._plugins["hermes-minimizer"]
        assert loaded.enabled and not loaded.error
        sections = manager.render_system_prompt_sections({{"session_id": "s1"}})
        assert len(sections) == 1
        content = sections[0].content
        assert len(content) <= 4000
        assert {RESERVED_START!r} not in content
        assert {RESERVED_END!r} not in content
        assert "Always prefer stdlib." in content
        assert "Keep error handling." in content
        assert "## Additional guidance" in content
        """,
        env,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_unknown_or_non_string_settings_fall_back_safely():
    plugin = _load_plugin()
    registered = {}

    class FakeCtx:
        def get_config(self, key, default=None):
            return {"preset": "nonexistent", "extra_guidance": 12345}.get(key, default)

        def register_system_prompt_section(self, section_id, content, *, position="after_memory"):
            registered["section"] = (section_id, content, position)

        def register_command(self, name, handler, description="", args_hint=""):
            registered["command"] = (name, handler, description, args_hint)

    plugin.register(FakeCtx())
    section_id, content_fn, position = registered["section"]
    assert section_id == SECTION_ID
    assert position == "after_memory"
    rendered = content_fn({}) if callable(content_fn) else content_fn
    assert rendered == (ROOT / "policy.md").read_text(encoding="utf-8").strip()


def test_minimizer_slash_command_handles_status_policy_review_and_unknown(tmp_path):
    env = _isolated_home(tmp_path, settings={"preset": "compact", "extra_guidance": "Prefer SQLite over Redis."})
    result = _run_native(
        """
        from hermes_cli import plugins

        handler = plugins.get_plugin_command_handler("minimizer")
        assert callable(handler)

        status_out = handler("")
        assert "preset: compact" in status_out
        assert "4000" in status_out
        assert "extra_guidance: set" in status_out

        policy_out = handler("policy")
        assert "Build the simplest complete system" in policy_out
        assert "Prefer SQLite over Redis." in policy_out

        review_out = handler("review")
        assert "ADVISORY ONLY" in review_out
        assert "file:line" in review_out

        help_out = handler("bogus")
        assert "Usage: /minimizer" in help_out
        """,
        env,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("isolation", ["in_process", "host"])
def test_plugin_works_under_both_in_process_and_host_isolation(tmp_path, isolation):
    env = _isolated_home(tmp_path, settings={"preset": "compact"}, isolation=isolation)
    result = _run_native(
        f"""
        from hermes_cli.plugins import PluginManager
        manager = PluginManager()
        manager.discover_and_load()
        host = getattr(manager, "_plugin_host_instance", None)
        try:
            loaded = manager._plugins["hermes-minimizer"]
            assert loaded.enabled and not loaded.error, loaded.error
            assert bool(host and host.alive) == ({isolation!r} == "host")
            sections = manager.render_system_prompt_sections({{"session_id": "iso-1"}})
            assert len(sections) == 1
            assert sections[0].id == {SECTION_ID!r}
            assert len(sections[0].content) < 2000
            cmd = manager._plugin_commands["minimizer"]["handler"]
            assert "preset: compact" in cmd("")
        finally:
            manager.unload()
            if host is not None:
                host.shutdown()
        """,
        env,
    )
    assert result.returncode == 0, result.stdout + result.stderr
