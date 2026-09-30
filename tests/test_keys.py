import unittest

from iceprefs.keys import (
    COMMAND,
    CONTROL,
    OPTION,
    SHIFT,
    describe_combination,
    key_name,
    modifier_names,
    modifier_symbols,
    unknown_modifier_bits,
)


class TestModifierMask(unittest.TestCase):
    def test_the_bits_are_the_ones_the_ice_source_declares(self):
        self.assertEqual((CONTROL, OPTION, SHIFT, COMMAND), (1, 2, 4, 8))

    def test_modifiers_come_out_in_the_order_ice_shows_them(self):
        self.assertEqual(
            ["Control", "Option", "Shift", "Command"],
            modifier_names(CONTROL | OPTION | SHIFT | COMMAND),
        )
        self.assertEqual("⌃⌥⇧⌘", modifier_symbols(CONTROL | OPTION | SHIFT | COMMAND))

    def test_an_empty_mask_holds_no_modifier(self):
        self.assertEqual([], modifier_names(0))
        self.assertEqual("", modifier_symbols(0))

    def test_a_bit_no_modifier_claims_is_reported_rather_than_dropped(self):
        self.assertEqual(16, unknown_modifier_bits(COMMAND | 16))
        self.assertEqual(0, unknown_modifier_bits(COMMAND | SHIFT))
        described = describe_combination(34, COMMAND | 16)
        self.assertEqual(16, described["unknown_modifier_bits"])

    def test_a_plain_combination_carries_no_unknown_bits_field(self):
        self.assertNotIn("unknown_modifier_bits", describe_combination(34, COMMAND))


class TestKeyNames(unittest.TestCase):
    def test_a_few_codes_that_anchor_the_table(self):
        self.assertEqual("A", key_name(0))
        self.assertEqual("I", key_name(34))
        self.assertEqual("Space", key_name(49))
        self.assertEqual("Escape", key_name(53))
        self.assertEqual("Up Arrow", key_name(126))

    def test_an_unknown_code_has_no_name(self):
        self.assertIsNone(key_name(999))

    def test_an_unknown_code_keeps_its_number_and_shows_a_question_mark(self):
        described = describe_combination(999, CONTROL)
        self.assertIsNone(described["key"])
        self.assertEqual(999, described["key_code"])
        self.assertEqual("⌃?", described["display"])


class TestDescribeCombination(unittest.TestCase):
    def test_control_command_i(self):
        self.assertEqual(
            {
                "key": "I",
                "key_code": 34,
                "modifiers": ["Control", "Command"],
                "modifier_mask": 9,
                "display": "⌃⌘I",
            },
            describe_combination(34, 9),
        )


if __name__ == "__main__":
    unittest.main()
