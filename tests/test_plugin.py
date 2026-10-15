from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]
HERMES_SOURCE = Path(os.environ["HERMES_SOURCE"])
SECTION_ID = "minimizer.guidance"


def _load_plugin():
    package = ROOT / "__init__.py"
    spec = importlib.util.spec_from_file_location(
        "hermes_minimizer_under_test",
        package,
        submodule_search_locations=[str(ROOT)],
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _isolated_plugin_home(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    home = tmp_path / "hermes-home"
    plugin = home / "plugins" / "hermes-minimizer"
    plugin.mkdir(parents=True)
    for name in ("__init__.py", "plugin.yaml", "policy.md"):
        shutil.copy2(ROOT / name, plugin / name)
    (home / "bundled-plugins").mkdir()
    (home / "config.yaml").write_text(
        "plugins:\n  enabled:\n    - hermes-minimizer\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.update(
        HERMES_HOME=str(home),
        HERMES_BUNDLED_PLUGINS=str(home / "bundled-plugins"),
        HERMES_ENABLE_PROJECT_PLUGINS="0",
        PYTHONPATH=os.pathsep.join(
            filter(None, (str(HERMES_SOURCE), env.get("PYTHONPATH", "")))
        ),
    )
    return home, env


def _run_native(code: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    _, env = _isolated_plugin_home(tmp_path)
    code = textwrap.dedent(code)
    python = env.get("HERMES_PYTHON")
    if python:
        bootstrap = (
            "import os, sys; "
            "os.environ.pop('PYTHONHOME', None); "
            f"sys.path.insert(0, {str(HERMES_SOURCE)!r}); "
            "sys._hermes_pin_default_home = True; "
            "import hermes_bootstrap; "
            f"exec({code!r})"
        )
        command = [python, "-I", "-c", bootstrap]
    else:
        command = [sys.executable, "-c", code]
    return subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=90,
        check=False,
    )


def test_policy_preserves_order_precedence_safety_and_proof():
    policy = (ROOT / "policy.md").read_text(encoding="utf-8")
    rungs = [
        "1. Required behavior already exists",
        "2. The responsible layer, type, helper, or pattern owns it",
        "3. The standard library, native platform, browser, database, runtime, or an installed dependency owns it",
        "4. A small new implementation fits the current architecture",
        "5. Existing structure obstructs clear ownership",
    ]

    assert [policy.index(rung) for rung in rungs] == sorted(
        policy.index(rung) for rung in rungs
    )
    assert "without distortion" in policy
    assert "System, user, and repository instructions outrank this default" in policy
    assert "trust-boundary validation" in policy
    assert "hardware calibration" in policy
    assert "explicitly requested behavior" in policy
    assert "smallest sufficient proof" in policy
    assert len(policy.strip()) <= 4000


def test_unsupported_native_api_fails_with_actionable_message():
    plugin = _load_plugin()

    with pytest.raises(RuntimeError, match=r"Hermes >=0\.22\.0.*register_system_prompt_section"):
        plugin.register(object())


def test_real_native_discovery_registration_and_render_are_deterministic(tmp_path):
    result = _run_native(
        f"""
        from hermes_cli.plugins import PluginManager

        manager = PluginManager()
        manager.discover_and_load()
        loaded = manager._plugins["hermes-minimizer"]
        assert loaded.enabled and not loaded.error

        first = manager.render_system_prompt_sections({{"session_id": "one"}})
        second = manager.render_system_prompt_sections({{"session_id": "two"}})
        assert first == second
        assert len(first) == 1
        assert first[0].id == {SECTION_ID!r}
        assert first[0].position == "after_memory"
        assert "simplest complete system" in first[0].content
        """,
        tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_real_assembled_prompt_contains_one_stable_section(tmp_path):
    result = _run_native(
        f"""
        from agent.system_prompt import build_system_prompt
        from hermes_cli import plugins
        from hermes_cli.plugins import PluginManager
        from run_agent import AIAgent

        manager = PluginManager()
        manager.discover_and_load()
        plugins._plugin_manager = manager
        agent = AIAgent(
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
            model="test/model",
            provider="openrouter",
            platform="cli",
            quiet_mode=True,
            skip_context_files=True,
            skip_memory=True,
            session_id="minimizer-prompt-test",
        )

        first = build_system_prompt(agent)
        second = build_system_prompt(agent)
        header = "## Plugin Context: {SECTION_ID}"
        assert first == second
        assert first.count(header) == 1
        assert first.count("Build the simplest complete system") == 1
        """,
        tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
