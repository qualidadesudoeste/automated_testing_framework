import unittest

from testing_framework.assertions import OPERATORS, resolve


class AssertionTests(unittest.TestCase):
    def test_boundary_and_collection_operators(self):
        self.assertTrue(OPERATORS["between"](10, [1, 10]))
        self.assertTrue(OPERATORS["length_eq"]([1, 2], 2))
        self.assertTrue(OPERATORS["unique"]([1, 2, 3], None))
        self.assertTrue(OPERATORS["sorted_desc"]([3, 2, 1], None))

    def test_string_and_null_operators(self):
        self.assertTrue(OPERATORS["matches"]("123.456.789-09", r"\d{3}\.\d{3}\.\d{3}-\d{2}"))
        self.assertTrue(OPERATORS["starts_with"]("Cliente ativo", "Cliente"))
        self.assertTrue(OPERATORS["is_null"](None, None))
        self.assertTrue(OPERATORS["not_null"](0, None))

    def test_resolves_nested_data(self):
        missing, value = resolve({"items": [{"id": 7}]}, "items.0.id")
        self.assertFalse(missing)
        self.assertEqual(value, 7)


if __name__ == "__main__":
    unittest.main()
