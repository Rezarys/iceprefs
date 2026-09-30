import json
import os
import plistlib
import tempfile
import unittest

import fixture
from iceprefs.prefs import PrefsError, convert, load


class TestConvert(unittest.TestCase):
    def test_a_data_blob_holding_json_comes_out_as_that_json(self):
        self.assertEqual({"a": 1}, convert(json.dumps({"a": 1}).encode("utf-8")))

    def test_a_data_blob_holding_anything_else_is_named_unreadable(self):
        converted = convert(b"\x00\x01\x02")
        self.assertEqual(3, converted["unreadable_data"]["bytes"])
        self.assertEqual("AAEC", converted["unreadable_data"]["base64"])

    def test_text_that_is_not_json_is_also_named_unreadable(self):
        self.assertIn("unreadable_data", convert(b"not json at all"))

    def test_blobs_nested_inside_containers_are_unwrapped_too(self):
        self.assertEqual(
            {"outer": [{"inner": 7}]},
            convert({"outer": [json.dumps({"inner": 7}).encode("utf-8")]}),
        )

    def test_a_date_comes_out_as_an_iso_string(self):
        import datetime

        self.assertEqual(
            "2024-08-18T13:32:05",
            convert(datetime.datetime(2024, 8, 18, 13, 32, 5)),
        )

    def test_plain_values_pass_through_unchanged(self):
        self.assertEqual([True, 15.0, "smart", None], convert([True, 15.0, "smart", None]))


class TestLoad(unittest.TestCase):
    def test_a_binary_file_and_an_xml_file_read_the_same(self):
        settings = fixture.readme_settings()
        with fixture.TempPrefs(settings, fmt=plistlib.FMT_BINARY) as binary:
            from_binary = load(binary)
        with fixture.TempPrefs(settings, fmt=plistlib.FMT_XML) as xml:
            from_xml = load(xml)
        self.assertEqual(from_binary, from_xml)

    def test_hotkeys_come_out_named_rather_than_as_base64(self):
        with fixture.TempPrefs(fixture.readme_settings()) as path:
            settings = load(path)
        self.assertEqual("⌃⌘I", settings["Hotkeys"]["ToggleHiddenSection"]["display"])
        self.assertEqual("⌥⌘Space", settings["Hotkeys"]["SearchMenuBarItems"]["display"])

    def test_an_action_with_no_hotkey_stays_null(self):
        with fixture.TempPrefs(fixture.readme_settings()) as path:
            settings = load(path)
        self.assertIsNone(settings["Hotkeys"]["ToggleApplicationMenus"])

    def test_a_hotkey_blob_that_is_not_a_pair_of_numbers_is_not_forced_into_one(self):
        settings = {"Hotkeys": {"Odd": json.dumps(["I", "Command"]).encode("utf-8")}}
        with fixture.TempPrefs(settings) as path:
            loaded = load(path)
        self.assertEqual(["I", "Command"], loaded["Hotkeys"]["Odd"])

    def test_a_hotkey_blob_that_is_not_json_is_named_unreadable(self):
        settings = {"Hotkeys": {"Odd": b"\xff\xfe"}}
        with fixture.TempPrefs(settings) as path:
            loaded = load(path)
        self.assertIn("unreadable_data", loaded["Hotkeys"]["Odd"])

    def test_every_setting_of_the_file_comes_out_none_dropped(self):
        with fixture.TempPrefs(fixture.readme_settings()) as path:
            settings = load(path)
        self.assertEqual(
            sorted(fixture.readme_settings()), sorted(settings)
        )

    def test_other_data_blobs_are_unwrapped_as_well(self):
        settings = {"IceIcon": json.dumps({"name": "dot"}).encode("utf-8")}
        with fixture.TempPrefs(settings) as path:
            self.assertEqual({"name": "dot"}, load(path)["IceIcon"])


class TestLoadRefuses(unittest.TestCase):
    def test_a_missing_file_says_so_and_names_the_path(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = os.path.join(directory, "nope.plist")
            with self.assertRaises(PrefsError) as caught:
                load(missing)
        self.assertIn(missing, str(caught.exception))

    def test_a_file_that_is_not_a_property_list_says_so(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "x.plist")
            with open(path, "wb") as handle:
                handle.write(b"this is not a property list")
            with self.assertRaises(PrefsError) as caught:
                load(path)
        self.assertIn("property list", str(caught.exception))

    def test_a_property_list_that_is_not_a_set_of_settings_says_so(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "x.plist")
            with open(path, "wb") as handle:
                plistlib.dump([1, 2, 3], handle)
            with self.assertRaises(PrefsError) as caught:
                load(path)
        self.assertIn("top level", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
