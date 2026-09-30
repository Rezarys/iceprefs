# iceprefs

```
pip install iceprefs
```

Print an Ice preferences file as readable JSON, including the hotkeys that `plutil` leaves as base64.

Not affiliated with Ice or with its author. "Ice" is used here only to say which file this tool reads.

## Why

Ice has no export and no configuration path yet, so the way to move settings between machines is `defaults export com.jordanbaird.Ice`, which gives you a property list. Converting that with `plutil -convert json` gets you most of the way, but not all of it: Ice stores your hotkeys, and your Ice icon, as data blobs holding JSON, so those come out as base64 and a diff of two machines tells you nothing about them.

`iceprefs` reads the same file and unwraps those blobs, so what you get is the whole thing in one readable, sorted, stable JSON document that you can keep in your dotfiles and diff.

## Use

```
iceprefs
```

With no argument it reads `~/Library/Preferences/com.jordanbaird.Ice.plist`. Give it a path to read a file you exported somewhere else. Both the binary and the XML form of a property list are accepted.

```
iceprefs Ice.plist --key Hotkeys
```

```json
{
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
```

That block is checked against the real output of the tool by the test suite, so it cannot go stale.

Options:

- `-k NAME`, `--key NAME`: print only this setting. Repeat the option for several settings. Asking for a setting the file has not got fails and names it.
- `--compact`: print one line instead of an indented block.
- `--version`: print the version.

## What it does and does not do

It only reads. It never writes to the file, and the test suite checks that the bytes on disk are the same before and after a run. There is no import side: putting settings back is what `defaults import` already does, and this tool does not duplicate it.

A data blob that does not hold valid JSON is not dropped and not guessed at. It comes out as an object saying how many bytes it held and carrying those bytes as base64, so nothing is lost silently.

Key names are those of a US ANSI keyboard. A stored hotkey holds a virtual key code, which names a physical key rather than a character, so the `key_code` number is always printed next to the name. If your layout prints something else on that key, the number is the thing to trust.

A modifier bit that the Ice source does not claim is reported in an `unknown_modifier_bits` field rather than being dropped.

## Honest reserve

This tool has never been run against a real Ice profile, only against fixtures written for its tests. The setting names, the hotkey encoding, the modifier mask and the fact that the Ice icon is stored the same way were read from the published Ice source in September 2026: `Ice/Utilities/Defaults.swift`, `Ice/Settings/SettingsManagers/HotkeySettingsManager.swift`, `Ice/Settings/SettingsManagers/GeneralSettingsManager.swift`, `Ice/Hotkeys/KeyCombination.swift` and `Ice/Hotkeys/Modifiers.swift`. If a future version of Ice changes the shape of what it stores in a data blob, that setting comes out as an unreadable blob rather than as a wrong value. If it keeps the shape and changes what the numbers mean, this tool has no way of telling, and would print a wrong key name with a right `key_code` next to it. That is the case to watch, and the reason the number is always printed.

If you run it on a real profile and something comes out wrong, please open an issue with what you saw. That is the only way this reserve gets shorter.

## Requirements

Python 3.9 or later. No dependencies, standard library only.

## Origin

Asked for in https://github.com/jordanbaird/Ice/issues/326.

## Note

Built with AI assistance, reviewed and tested by me.

## Licence

MIT, Younes Z.
