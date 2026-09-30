"""Build preferences files to test against.

These are written here, for these tests. They are not a real Ice profile: no
real profile has ever been read. Their shape follows the published Ice source,
file by file, as the README says.
"""

import json
import os
import plistlib
import tempfile


def hotkey(key_code, modifier_mask):
    """Encode a key combination the way Ice does: JSON, inside a data blob."""
    return json.dumps([key_code, modifier_mask]).encode("utf-8")


NO_HOTKEY = b"null"


def readme_settings():
    """The settings the README shows, and nothing else."""
    return {
        "ShowIceIcon": True,
        "UseIceBar": False,
        "AutoRehide": True,
        "RehideStrategy": "smart",
        "RehideInterval": 15.0,
        "Hotkeys": {
            "ToggleHiddenSection": hotkey(34, 9),
            "SearchMenuBarItems": hotkey(49, 10),
            "ToggleApplicationMenus": NO_HOTKEY,
        },
    }


def write(settings, directory, name="com.jordanbaird.Ice.plist", fmt=plistlib.FMT_BINARY):
    path = os.path.join(directory, name)
    with open(path, "wb") as handle:
        plistlib.dump(settings, handle, fmt=fmt)
    return path


class TempPrefs(object):
    """A preferences file on disk for the length of a `with` block."""

    def __init__(self, settings, fmt=plistlib.FMT_BINARY):
        self.settings = settings
        self.fmt = fmt
        self._directory = None
        self.path = None

    def __enter__(self):
        self._directory = tempfile.TemporaryDirectory()
        self.path = write(self.settings, self._directory.name, fmt=self.fmt)
        return self.path

    def __exit__(self, *exc_info):
        self._directory.cleanup()
        return False
