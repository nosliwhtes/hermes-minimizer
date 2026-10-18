"""Focused native contract checks; no provider calls or live user state."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import textwrap
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ["HERMES_SOURCE"]).resolve()
SECTION_ID = "minimizer.guidance"


def _plugin():
    spec = importlib.util.spec_from_file_location("minimizer_contract", ROOT / "__init__.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("ctx", [object(), SimpleNamespace(register_system_prompt_section=None),
                                  SimpleNamespace(register_system_prompt_section="not callable")])
def test_incompatible_api_requires_upgrade(ctx):
    with pytest.raises(RuntimeError, match=r"Hermes >=0\.22\.0.*register_system_prompt_section.*upgrade"):
        _plugin().register(ctx)


def _environment(tmp_path, *, enabled=True):
    home = tmp_path / "home"
    home.mkdir()
    hermes_home = tmp_path / "hermes-home"
    plugin_dir = hermes_home / "plugins" / "hermes-minimizer"
    plugin_dir.mkdir(parents=True)
    for name in ("__init__.py", "plugin.yaml", "policy.md"):
        shutil.copy2(ROOT / name, plugin_dir / name)
    bundled = hermes_home / "bundled-plugins"
    bundled.mkdir()
    (hermes_home / "config.yaml").write_text(
        "plugins:\n  enabled: " + ("[hermes-minimizer]" if enabled else "[]") + "\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.update(HOME=str(home), HERMES_HOME=str(hermes_home),
               HERMES_BUNDLED_PLUGINS=str(bundled), HERMES_ENABLE_PROJECT_PLUGINS="0")
    return env


def _native(code, env):
    # Both homes are set before bootstrap/import, including fresh resume processes.
    bootstrap = (
        "import sys; "
        f"sys.path.insert(0, {str(SOURCE)!r}); "
        "sys._hermes_pin_default_home = True; import hermes_bootstrap; "
        f"exec({textwrap.dedent(code)!r})"
    )
    proc = subprocess.run([sys.executable, "-I", "-c", bootstrap], cwd=ROOT,
                          env=env, text=True, capture_output=True, timeout=90)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout


def test_registration_is_one_exact_static_string_with_no_other_surface(tmp_path):
    _native('''
        import importlib.util
        import os
        from pathlib import Path
        from hermes_cli.plugins import PluginContext, PluginManager, PluginManifest
        root = Path(os.environ["HERMES_HOME"]) / "plugins" / "hermes-minimizer"
        expected = (root / "policy.md").read_text(encoding="utf-8").strip()
        manager = PluginManager()
        native = PluginContext(PluginManifest(name="hermes-minimizer", key="hermes-minimizer", source="user"), manager)
        calls = []
        class OnlyPromptSections:
            def register_system_prompt_section(self, *args, **kwargs):
                calls.append((args, kwargs))
                return native.register_system_prompt_section(*args, **kwargs)
            def __getattr__(self, name):
                raise AssertionError("Unexpected plugin surface: " + name)
        spec = importlib.util.spec_from_file_location("minimizer", root / "__init__.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.register(OnlyPromptSections())
        assert calls == [(("minimizer.guidance", expected), {"position": "after_memory"})]
        assert isinstance(calls[0][0][1], str) and not callable(calls[0][0][1])
        rendered = manager.render_system_prompt_sections({"session_id": "exact"})
        assert len(rendered) == 1
        assert (rendered[0].id, rendered[0].position, rendered[0].content) == (
            "minimizer.guidance", "after_memory", expected)
    ''', _environment(tmp_path))


_AGENT_SETUP = '''
import os
from pathlib import Path
from agent.system_prompt import build_system_prompt, invalidate_system_prompt
from hermes_cli import plugins
from hermes_cli.plugins import PluginManager
from run_agent import AIAgent
manager = PluginManager()
manager.discover_and_load()
plugins._plugin_manager = manager
'''

_AGENT_KWARGS = '''
api_key="test-key", base_url="https://openrouter.ai/api/v1", model="test/model",
provider="openrouter", platform="cli", quiet_mode=True,
skip_context_files=True, skip_memory=True,
'''


def test_disabled_plugin_has_no_section_in_fresh_session(tmp_path):
    _native(_AGENT_SETUP + f'''
assert manager.render_system_prompt_sections({{"session_id": "disabled"}}) == []
agent = AIAgent({_AGENT_KWARGS} session_id="disabled")
prompt = build_system_prompt(agent)
assert "## Plugin Context: minimizer.guidance" not in prompt
expected = (Path(os.environ["HERMES_HOME"]) / "plugins/hermes-minimizer/policy.md").read_text(encoding="utf-8").strip()
assert expected not in prompt
''', _environment(tmp_path, enabled=False))


def test_persisted_resume_and_normal_invalidation_keep_exact_section(tmp_path):
    # Mirrors upstream tests/agent/test_plugin_prompt_sections.py's real DB path.
    env = _environment(tmp_path)
    code = _AGENT_SETUP + f'''
import json
from agent.conversation_loop import _restore_or_build_system_prompt
from hermes_state import SessionDB
home = Path(os.environ["HERMES_HOME"])
expected = (home / "plugins/hermes-minimizer/policy.md").read_text(encoding="utf-8").strip()
db = SessionDB(db_path=home / "state.db")
session_id = "minimizer-contract-resume"
db.ensure_session(session_id, source="cli", model="test/model")
agent = AIAgent({_AGENT_KWARGS} session_id=session_id, session_db=db)
history = [] if os.environ["TEST_PHASE"] == "first" else [{{"role": "user", "content": "persisted"}}]
render = manager.render_system_prompt_sections
if history:
    def unexpected_render(_info):
        raise AssertionError("Resume must restore persisted prompt, not render sections")
    manager.render_system_prompt_sections = unexpected_render
_restore_or_build_system_prompt(agent, None, history)
manager.render_system_prompt_sections = render
prompt = agent._cached_system_prompt
assert db.get_session(session_id)["system_prompt"] == prompt
header = "## Plugin Context: minimizer.guidance"
assert prompt.count(header) == 1 and prompt.count(expected) == 1
rebuilt = None
if history:
    invalidate_system_prompt(agent)
    rebuilt = build_system_prompt(agent)
    assert rebuilt.count(header) == 1 and rebuilt.count(expected) == 1
    assert rebuilt.index(header) < rebuilt.index("Conversation started:")
print(json.dumps({{"prompt": prompt, "rebuilt": rebuilt}}))
db.close()
'''
    outputs = []
    for phase in ("first", "resume"):
        env["TEST_PHASE"] = phase
        outputs.append(json.loads(_native(code, env).strip().splitlines()[-1]))
    assert outputs[0]["prompt"] == outputs[1]["prompt"]
    assert outputs[1]["rebuilt"] is not None
