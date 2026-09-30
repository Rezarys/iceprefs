import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout

import fixture
from iceprefs.cli import main

# The exact block the README shows for `iceprefs Ice.plist --key Hotkeys`.
# The README copies this constant. The test below compares it to what the tool
# really prints, so the README cannot drift away from the tool.
README_SAMPLE = """{
  "Hotkeys": {
    "SearchMenuBarItems": {
      "display": "⌥⌘Space",
      "key": "Space",
      "key_code": 49,
      "modifier_mask": 10,
      "modifiers": [
        "Option",
        "Command"
      ]
    },
    "ToggleApplicationMenus": null,
    "ToggleHiddenSection": {
      "display": "⌃⌘I",
      "key": "I",
      "key_code": 34,
      "modifier_mask": 9,
      "modifiers": [
        "Control",
        "Command"
      ]
    }
  }
}
"""


def run(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class TestReadmeSample(unittest.TestCase):
    def test_the_whole_rendering_is_the_one_shown_in_the_readme(self):
        with fixture.TempPrefs(fixture.readme_settings()) as path:
            code, out, err = run([path, "--key", "Hotkeys"])
        self.assertEqual(0, code)
        self.assertEqual("", err)
        self.assertEqual(README_SAMPLE, out)

    def test_the_readme_sample_is_valid_json(self):
        json.loads(README_SAMPLE)


class TestCli(unittest.TestCase):
    def test_the_whole_file_prints_when_no_key_is_asked_for(self):
        with fixture.TempPrefs(fixture.readme_settings()) as path:
            code, out, _ = run([path])
        self.assertEqual(0, code)
        self.assertEqual(sorted(fixture.readme_settings()), sorted(json.loads(out)))

    def test_several_keys_can_be_asked_for_at_once(self):
        with fixture.TempPrefs(fixture.readme_settings()) as path:
            code, out, _ = run([path, "-k", "UseIceBar", "-k", "AutoRehide"])
        self.assertEqual(0, code)
        self.assertEqual({"AutoRehide": True, "UseIceBar": False}, json.loads(out))

    def test_asking_for_a_setting_the_file_has_not_got_fails_and_names_it(self):
        with fixture.TempPrefs(fixture.readme_settings()) as path:
            code, out, err = run([path, "--key", "NoSuchSetting"])
        self.assertEqual(2, code)
        self.assertEqual("", out)
        self.assertIn("NoSuchSetting", err)

    def test_compact_prints_one_line_holding_the_same_thing(self):
        with fixture.TempPrefs(fixture.readme_settings()) as path:
            _, indented, _ = run([path])
            code, compact, _ = run([path, "--compact"])
        self.assertEqual(0, code)
        self.assertEqual(1, compact.count("\n"))
        self.assertEqual(json.loads(indented), json.loads(compact))

    def test_a_missing_file_fails_with_a_message_and_prints_nothing(self):
        code, out, err = run([os.path.join("no", "such", "file.plist")])
        self.assertEqual(2, code)
        self.assertEqual("", out)
        self.assertTrue(err.startswith("iceprefs: "))

    def test_the_file_is_left_exactly_as_it_was(self):
        with fixture.TempPrefs(fixture.readme_settings()) as path:
            with open(path, "rb") as handle:
                before = handle.read()
            run([path])
            with open(path, "rb") as handle:
                after = handle.read()
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
