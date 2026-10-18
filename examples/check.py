"""Verify authored fixtures and count physical source lines; stdlib Python 3.10+."""

import runpy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLES = ("ordered_dedup", "single_renderer")


class FixtureContracts(unittest.TestCase):
    def test_ordered_dedup(self):
        for variant in ("before", "after"):
            with self.subTest(variant=variant):
                unique_names = runpy.run_path(str(HERE / "ordered_dedup" / f"{variant}.py"))["unique_names"]
                for names, expected in (
                    ([], []),
                    ([""], [""]),
                    (["tea", "tea", "Tea", "水", "", "水"], ["tea", "Tea", "水", ""]),
                    (["a", "b", "a", "c", "b"], ["a", "b", "c"]),
                ):
                    original = names.copy()
                    actual = unique_names(names)
                    self.assertEqual(actual, expected)
                    self.assertEqual(names, original)
                    self.assertIsNot(actual, names)
                for invalid in (None, "tea", ("tea",)):
                    with self.assertRaisesRegex(TypeError, "^names must be a list$"):
                        unique_names(invalid)
                for invalid in ([1], ["tea", None], [["tea"]]):
                    with self.assertRaisesRegex(TypeError, "^names must contain only strings$"):
                        unique_names(invalid)

    def test_single_renderer(self):
        for variant in ("before", "after"):
            with self.subTest(variant=variant):
                render_message = runpy.run_path(str(HERE / "single_renderer" / f"{variant}.py"))["render_message"]
                self.assertEqual(render_message("Ada"), "Hello, Ada!")
                self.assertEqual(render_message("  水  ", style="plain"), "Hello, 水!")
                self.assertEqual(render_message("A\nB"), "Hello, A\nB!")
                for invalid in (None, 1, []):
                    with self.assertRaisesRegex(TypeError, "^name must be a string$"):
                        render_message(invalid)
                for invalid in ("", " \t\n"):
                    with self.assertRaisesRegex(ValueError, "^name must not be blank$"):
                        render_message(invalid)
                for invalid_style in ("html", "", None):
                    with self.assertRaisesRegex(ValueError, "^unsupported style$"):
                        render_message(None, style=invalid_style)
                with self.assertRaises(TypeError):
                    render_message("Ada", "plain")


def main() -> int:
    print("Authored illustrative fixtures; not a model benchmark.")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FixtureContracts)
    result = unittest.TextTestRunner(stream=sys.stdout).run(suite)
    if not result.wasSuccessful():
        return 1
    print("Physical source lines include imports, comments, and blank lines.")
    for example in EXAMPLES:
        before, after = (
            len((HERE / example / f"{variant}.py").read_text(encoding="utf-8").splitlines())
            for variant in ("before", "after")
        )
        print(f"{example}: {before} -> {after} physical lines ({after - before:+d}); behavior PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
