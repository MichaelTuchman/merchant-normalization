"""Synthetic, offline tests of the approved description lookup contract."""

import unittest
from copy import deepcopy

from merchant_normalization import normalize_merchant


class MerchantLookupTests(unittest.TestCase):
    def setUp(self):
        self.mappings = {
            "EXAMPLE CAFE CITY ZZ": "Example Cafe",
            "EXAMPLE CAFE ONLINE": "Example Cafe",
            "EXAMPLE CAFE": "Example Cafe Express",
        }

    def lookup(self, description):
        return normalize_merchant(
            description, self.mappings, mapping_version="synthetic-v1"
        )

    def test_approved_exact_match_and_provenance(self):
        result = self.lookup("EXAMPLE CAFE CITY ZZ")
        self.assertEqual(result.merchant_name, "Example Cafe")
        self.assertEqual(result.review_status, "approved")
        self.assertEqual(result.method, "exact_description")
        self.assertEqual(result.mapping_version, "synthetic-v1")
        self.assertEqual(result.description, "EXAMPLE CAFE CITY ZZ")

    def test_unknown_missing_and_blank_are_unresolved(self):
        for description in ("UNLISTED SHOP", None, "", " \t\n"):
            with self.subTest(description=description):
                result = self.lookup(description)
                self.assertIsNone(result.merchant_name)
                self.assertEqual(result.review_status, "unresolved")
                self.assertEqual(result.method, "none")
                self.assertEqual(result.description, description)

    def test_no_implicit_cleaning_or_approximate_matching(self):
        for description in (
            "example cafe city zz", "EXAMPLE CAFE CITY ZZ ",
            "EXAMPLE  CAFE CITY ZZ", "EXAMPLE CAFE CITY", "EXAMPLE CAFE CITY ZY",
        ):
            with self.subTest(description=description):
                self.assertEqual(self.lookup(description).review_status, "unresolved")

    def test_exact_key_wins_over_shared_prefix(self):
        self.assertEqual(self.lookup("EXAMPLE CAFE").merchant_name, "Example Cafe Express")
        self.assertEqual(self.lookup("EXAMPLE CAFE CITY ZZ").merchant_name, "Example Cafe")

    def test_different_descriptions_can_share_merchant(self):
        self.assertEqual(
            self.lookup("EXAMPLE CAFE CITY ZZ").merchant_name,
            self.lookup("EXAMPLE CAFE ONLINE").merchant_name,
        )

    def test_repeated_transactions_reuse_mapping_without_mutation(self):
        transactions = [
            {"description": "EXAMPLE CAFE CITY ZZ", "amount": -12.34},
            {"description": "EXAMPLE CAFE CITY ZZ", "amount": -56.78},
        ]
        original = deepcopy(transactions)
        original_mappings = self.mappings.copy()
        results = [self.lookup(row["description"]) for row in transactions]
        self.assertEqual(len(results), len(transactions))
        self.assertEqual(results[0], results[1])
        self.assertEqual(results, [self.lookup(row["description"]) for row in transactions])
        self.assertEqual(transactions, original)
        self.assertEqual(self.mappings, original_mappings)

    def test_empty_table_leaves_description_unresolved(self):
        result = normalize_merchant("EXAMPLE CAFE", {}, mapping_version="empty-v1")
        self.assertEqual(result.review_status, "unresolved")

    def test_invalid_description_type(self):
        with self.assertRaises(TypeError):
            self.lookup(123)

    def test_invalid_table_entries(self):
        for mappings in ({"": "Cafe"}, {None: "Cafe"}, {"A": " "}, {"A": None}):
            with self.subTest(mappings=mappings), self.assertRaises(ValueError):
                normalize_merchant("A", mappings, mapping_version="v1")

    def test_invalid_table_type(self):
        with self.assertRaises(TypeError):
            normalize_merchant("A", [("A", "Cafe")], mapping_version="v1")

    def test_version_is_required_and_nonblank(self):
        for version in (None, "", " "):
            with self.subTest(version=version), self.assertRaises(ValueError):
                normalize_merchant("A", {}, mapping_version=version)


if __name__ == "__main__":
    unittest.main()
