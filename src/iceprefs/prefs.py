"""Read an Ice preferences file and turn it into JSON ready values.

Ice keeps some of its settings as binary data holding JSON. ``plutil`` leaves
those as base64, which is the part of the file a reader cannot follow. This
module unwraps them, and says so plainly when it cannot.

The file is only ever read. Nothing here writes to it.
"""

import base64
import datetime
import json
import os
import plistlib

DEFAULT_PATH = "~/Library/Preferences/com.jordanbaird.Ice.plist"

# Ice stores this key as a mapping of action name to JSON encoded key
# combination. See Ice/Settings/SettingsManagers/HotkeySettingsManager.swift.
HOTKEYS_KEY = "Hotkeys"


class PrefsError(Exception):
    """The file is missing, unreadable, or not a preferences file."""


def _unwrap_data(raw):
    """Turn a data blob into the value it holds, or say it is unreadable."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _opaque(raw)
    try:
        return convert(json.loads(text))
    except ValueError:
        return _opaque(raw)


def _opaque(raw):
    return {
        "unreadable_data": {
            "bytes": len(raw),
            "base64": base64.b64encode(raw).decode("ascii"),
        }
    }


def convert(value):
    """Turn one plist value into a JSON ready value, unwrapping data blobs."""
    if isinstance(value, (bytes, bytearray)):
        return _unwrap_data(bytes(value))
    if isinstance(value, dict):
        return {str(k): convert(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [convert(v) for v in value]
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    return value


def _describe_hotkey(raw):
    """Describe one stored hotkey, or fall back to the generic unwrapping."""
    from .keys import describe_combination

    if not isinstance(raw, (bytes, bytearray)):
        return convert(raw)
    unwrapped = _unwrap_data(bytes(raw))
    if unwrapped is None:
        return None
    if (
        isinstance(unwrapped, list)
        and len(unwrapped) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in unwrapped)
    ):
        return describe_combination(unwrapped[0], unwrapped[1])
    return unwrapped


def convert_hotkeys(value):
    """Turn the stored ``Hotkeys`` mapping into named key combinations."""
    if not isinstance(value, dict):
        return convert(value)
    return {str(action): _describe_hotkey(raw) for action, raw in value.items()}


def load(path=None):
    """Read a preferences file and return its settings as JSON ready values.

    ``path`` defaults to where Ice keeps the file on macOS. Both the binary and
    the XML form of a preferences file are accepted.
    """
    resolved = os.path.expanduser(path if path is not None else DEFAULT_PATH)
    try:
        with open(resolved, "rb") as handle:
            raw = plistlib.load(handle)
    except OSError as exc:
        raise PrefsError("cannot read %s: %s" % (resolved, exc.strerror or exc))
    except plistlib.InvalidFileException:
        raise PrefsError("%s is not a property list file" % resolved)
    except ValueError as exc:
        raise PrefsError("%s is not a readable property list: %s" % (resolved, exc))

    if not isinstance(raw, dict):
        raise PrefsError(
            "%s holds a %s at its top level, not a set of settings"
            % (resolved, type(raw).__name__)
        )

    settings = {}
    for key, value in raw.items():
        name = str(key)
        if name == HOTKEYS_KEY:
            settings[name] = convert_hotkeys(value)
        else:
            settings[name] = convert(value)
    return settings
