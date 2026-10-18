"""Behavior contracts for the authored documentation fixtures."""

import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("variant", ["before", "after"])
def test_ordered_deduplication_contract(variant):
    path = ROOT / "examples" / "ordered_dedup" / f"{variant}.py"
    assert path.is_file(), f"Missing example: {path}"
    unique_names = runpy.run_path(str(path))["unique_names"]
    for names, expected in [
        ([], []),
        ([""], [""]),
        (["tea", "tea", "Tea", "水", "", "水"], ["tea", "Tea", "水", ""]),
        (["a", "b", "a", "c", "b"], ["a", "b", "c"]),
    ]:
        original = names.copy()
        actual = unique_names(names)
        assert actual == expected
        assert names == original
        assert actual is not names
    for invalid in (None, "tea", ("tea",)):
        with pytest.raises(TypeError, match="^names must be a list$"):
            unique_names(invalid)
    for invalid in ([1], ["tea", None], [["tea"]]):
        with pytest.raises(TypeError, match="^names must contain only strings$"):
            unique_names(invalid)


@pytest.mark.parametrize("variant", ["before", "after"])
def test_single_renderer_contract(variant):
    path = ROOT / "examples" / "single_renderer" / f"{variant}.py"
    assert path.is_file(), f"Missing example: {path}"
    render_message = runpy.run_path(str(path))["render_message"]
    assert render_message("Ada") == "Hello, Ada!"
    assert render_message("  水  ", style="plain") == "Hello, 水!"
    assert render_message("A\nB") == "Hello, A\nB!"
    for invalid in (None, 1, []):
        with pytest.raises(TypeError, match="^name must be a string$"):
            render_message(invalid)
    for invalid in ("", " \t\n"):
        with pytest.raises(ValueError, match="^name must not be blank$"):
            render_message(invalid)
    for invalid_style in ("html", "", None):
        with pytest.raises(ValueError, match="^unsupported style$"):
            render_message(None, style=invalid_style)
    with pytest.raises(TypeError):
        render_message("Ada", "plain")


@pytest.mark.parametrize("from_root", [True, False])
def test_standalone_verifier_runs_and_counts_lines(tmp_path, from_root):
    script = ROOT / "examples" / "check.py"
    assert script.is_file(), "Missing standalone verifier"
    result = subprocess.run(
        [sys.executable, "examples/check.py" if from_root else str(script)],
        cwd=ROOT if from_root else tmp_path,
        text=True, capture_output=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Authored illustrative fixtures; not a model benchmark." in result.stdout
    for example in ("ordered_dedup", "single_renderer"):
        before, after = [
            len((ROOT / "examples" / example / f"{variant}.py").read_text().splitlines())
            for variant in ("before", "after")
        ]
        assert f"{example}: {before} -> {after} physical lines ({after - before:+d}); behavior PASS" in result.stdout


def test_verifier_returns_nonzero_for_broken_behavior(tmp_path):
    source = ROOT / "examples"
    assert (source / "check.py").is_file(), "Missing standalone verifier"
    target = tmp_path / "examples"
    shutil.copytree(source, target)
    (target / "ordered_dedup" / "after.py").write_text(
        "def unique_names(names):\n    return names\n", encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, str(target / "check.py")],
        cwd=tmp_path, text=True, capture_output=True, timeout=30,
    )
    assert result.returncode != 0
    assert "FAIL" in result.stdout + result.stderr
    assert "behavior PASS" not in result.stdout


def test_verifier_counts_imports_comments_and_blank_lines(tmp_path):
    source = ROOT / "examples"
    assert (source / "check.py").is_file(), "Missing standalone verifier"
    target = tmp_path / "examples"
    shutil.copytree(source, target)
    before = target / "ordered_dedup" / "before.py"
    text = before.read_text(encoding="utf-8")
    before.write_text("import math\n# Count this comment too.\n\n" + text, encoding="utf-8")
    old_count = len(text.splitlines()) + 3
    new_count = len((target / "ordered_dedup" / "after.py").read_text().splitlines())
    result = subprocess.run(
        [sys.executable, str(target / "check.py")],
        cwd=tmp_path, text=True, capture_output=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"ordered_dedup: {old_count} -> {new_count} physical lines ({new_count - old_count:+d}); behavior PASS" in result.stdout
