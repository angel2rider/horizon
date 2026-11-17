"""Tests for the layering scanner's Rust source helpers."""

import unittest

from tools.layering import rust_text as rt


class TestRegionsTest(unittest.TestCase):
    @staticmethod
    def regions(source):
        return rt.test_regions(rt.blank(source))

    def test_existing_test_attributes_still_work(self):
        for attr in ("#[test]", "#[cfg(test)]"):
            with self.subTest(attr=attr):
                source = f"{attr}\nfn t() {{}}\n"
                regions, mods = self.regions(source)
                self.assertEqual(len(regions), 1)
                self.assertTrue(rt.in_regions(regions, source.index("fn t")))
                self.assertEqual(mods, [])

    def test_stacked_cfg_all_test_is_a_test_region(self):
        source = '#[cfg(all(test, feature = "x"))]\nmod t {\n    fn helper() {}\n}\n'
        regions, _ = self.regions(source)
        self.assertEqual(len(regions), 1)
        self.assertTrue(rt.in_regions(regions, source.index("mod t")))
        self.assertTrue(rt.in_regions(regions, source.index("helper")))

    def test_other_cfg_shapes_with_test_are_test_regions(self):
        for attr in (
            '#[cfg(any(test, feature = "x"))]',
            "#[cfg(all(unix, test))]",
            '#[cfg(all(not(unix), test, feature = "x"))]',
            '#[cfg(all(feature = "x", any(unix, test)))]',
        ):
            with self.subTest(attr=attr):
                source = f"{attr}\nfn t() {{}}\n"
                regions, _ = self.regions(source)
                self.assertEqual(len(regions), 1)
                self.assertTrue(rt.in_regions(regions, source.index("fn t")))

    def test_negated_and_string_test_are_not_test_regions(self):
        for attr in (
            "#[cfg(not(test))]",
            "#[cfg(all(unix, not(test)))]",
            '#[cfg(feature = "test")]',
            "#[cfg(unix)]",
        ):
            with self.subTest(attr=attr):
                source = f"{attr}\nfn prod() {{}}\n"
                regions, _ = self.regions(source)
                self.assertEqual(regions, [])

    def test_mod_declared_under_stacked_cfg_is_a_test_mod(self):
        source = '#[cfg(all(test, feature = "x"))]\nmod hidden;\n'
        _, mods = self.regions(source)
        self.assertEqual(mods, ["hidden"])


if __name__ == "__main__":
    unittest.main()
