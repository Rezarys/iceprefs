"""Names for the macOS virtual key codes and modifier mask used by Ice.

Ice stores a key combination as a two element JSON array, ``[key, modifiers]``.
``key`` is a macOS virtual key code, ``modifiers`` is a bit mask. Both are read
from the published Ice source: ``Ice/Hotkeys/KeyCombination.swift`` for the
array, ``Ice/Hotkeys/Modifiers.swift`` for the mask.

A virtual key code names a physical key, not a character, so the names below
are the ones a US ANSI keyboard prints on that key.
"""

CONTROL = 1 << 0
OPTION = 1 << 1
SHIFT = 1 << 2
COMMAND = 1 << 3

# Order and symbols follow Modifiers.canonicalOrder in the Ice source.
MODIFIERS = (
    (CONTROL, "Control", "⌃"),
    (OPTION, "Option", "⌥"),
    (SHIFT, "Shift", "⇧"),
    (COMMAND, "Command", "⌘"),
)

KEY_NAMES = {
    0: "A", 1: "S", 2: "D", 3: "F", 4: "H", 5: "G", 6: "Z", 7: "X", 8: "C",
    9: "V", 11: "B", 12: "Q", 13: "W", 14: "E", 15: "R", 16: "Y", 17: "T",
    18: "1", 19: "2", 20: "3", 21: "4", 22: "6", 23: "5", 24: "=", 25: "9",
    26: "7", 27: "-", 28: "8", 29: "0", 30: "]", 31: "O", 32: "U", 33: "[",
    34: "I", 35: "P", 36: "Return", 37: "L", 38: "J", 39: "'", 40: "K",
    41: ";", 42: "\\", 43: ",", 44: "/", 45: "N", 46: "M", 47: ".",
    48: "Tab", 49: "Space", 50: "`", 51: "Delete", 53: "Escape",
    55: "Command", 56: "Shift", 57: "Caps Lock", 58: "Option", 59: "Control",
    60: "Right Shift", 61: "Right Option", 62: "Right Control",
    63: "Function", 64: "F17", 65: "Keypad .", 67: "Keypad *", 69: "Keypad +",
    71: "Keypad Clear", 72: "Volume Up", 73: "Volume Down", 74: "Mute",
    75: "Keypad /", 76: "Keypad Enter", 78: "Keypad -", 79: "F18", 80: "F19",
    81: "Keypad =", 82: "Keypad 0", 83: "Keypad 1", 84: "Keypad 2",
    85: "Keypad 3", 86: "Keypad 4", 87: "Keypad 5", 88: "Keypad 6",
    89: "Keypad 7", 90: "F20", 91: "Keypad 8", 92: "Keypad 9", 96: "F5",
    97: "F6", 98: "F7", 99: "F3", 100: "F8", 101: "F9", 103: "F11",
    105: "F13", 106: "F16", 107: "F14", 109: "F10", 111: "F12", 113: "F15",
    114: "Help", 115: "Home", 116: "Page Up", 117: "Forward Delete",
    118: "F4", 119: "End", 120: "F2", 121: "Page Down", 122: "F1",
    123: "Left Arrow", 124: "Right Arrow", 125: "Down Arrow", 126: "Up Arrow",
}


def key_name(code):
    """Return the US ANSI name of a virtual key code, or ``None`` if unknown."""
    return KEY_NAMES.get(code)


def modifier_names(mask):
    """Return the modifier names held in ``mask``, in the order Ice shows them."""
    return [name for bit, name, _ in MODIFIERS if mask & bit]


def modifier_symbols(mask):
    """Return the modifier symbols held in ``mask``, in the order Ice shows them."""
    return "".join(symbol for bit, _, symbol in MODIFIERS if mask & bit)


def unknown_modifier_bits(mask):
    """Return the bits of ``mask`` that no modifier of the Ice source claims."""
    known = CONTROL | OPTION | SHIFT | COMMAND
    return mask & ~known


def describe_combination(code, mask):
    """Describe one key combination.

    ``key`` is the US ANSI name, or ``null`` when the code is not in the table,
    in which case ``key_code`` alone says which physical key it was.
    """
    name = key_name(code)
    described = {
        "key": name,
        "key_code": code,
        "modifiers": modifier_names(mask),
        "modifier_mask": mask,
        "display": modifier_symbols(mask) + (name if name is not None else "?"),
    }
    extra = unknown_modifier_bits(mask)
    if extra:
        described["unknown_modifier_bits"] = extra
    return described
