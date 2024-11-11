import unittest

from filters import Filter
from config import IncludeRule, ExcludeRule


class TestFilters(unittest.TestCase):

    def test_include_wildcard(self):
        this_filter = Filter([
            IncludeRule(rule="include", select=["*"]),
        ])
        self.assertTrue(this_filter.matches("foo"))

    def test_exclude_wildcard(self):
        this_filter = Filter([
            ExcludeRule(rule="exclude", select=["*"]),
        ])
        self.assertFalse(this_filter.matches("foo"))

    def test_specific_include(self):
        this_filter = Filter([
            ExcludeRule(rule="exclude", select=["*"]),
            IncludeRule(rule="include", select=["foo", "bar"]),
        ])
        self.assertTrue(this_filter.matches("foo"))
        self.assertTrue(this_filter.matches("bar"))
        self.assertFalse(this_filter.matches("baz"))

    def test_specific_exclude(self):
        this_filter = Filter([
            IncludeRule(rule="include", select=["*"]),
            ExcludeRule(rule="exclude", select=["foo", "bar"]),
        ])
        self.assertFalse(this_filter.matches("foo"))
        self.assertFalse(this_filter.matches("bar"))
        self.assertTrue(this_filter.matches("baz"))

    def test_specific_include_does_not_affect_includes(self):
        this_filter = Filter([
            IncludeRule(rule="include", select=["*"]),
            ExcludeRule(rule="exclude", select=["foo", "bar"]),
            IncludeRule(rule="include", select=["foo"]),
        ])
        self.assertTrue(this_filter.matches("foo"))
        self.assertFalse(this_filter.matches("bar"))
        self.assertTrue(this_filter.matches("baz"))

    def test_specific_exclude_does_not_affect_excludes(self):
        this_filter = Filter([
            ExcludeRule(rule="exclude", select=["*"]),
            IncludeRule(rule="include", select=["foo", "bar"]),
            ExcludeRule(rule="exclude", select=["foo"]),
        ])
        self.assertFalse(this_filter.matches("foo"))
        self.assertTrue(this_filter.matches("bar"))
        self.assertFalse(this_filter.matches("baz"))


if __name__ == "__main__":
    unittest.main()
