"""Tests for FlexFloat division operations."""

import unittest

from flexfloat import FlexFloat
from tests import FlexFloatTestCase


class TestDivision(FlexFloatTestCase):
    """Test FlexFloat division operations."""

    def test_flexfloat_division_simple_case_works_correctly(self):
        f1 = 6.0
        f2 = 3.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        # Division operation (assumed implemented)
        result = bf1 / bf2
        expected = f1 / f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_division_by_one_returns_original(self):
        f1 = 42.0
        f2 = 1.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 / bf2
        expected = f1 / f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_division_with_zero_numerator_returns_zero(self):
        f1 = 0.0
        f2 = 5.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 / bf2
        expected = f1 / f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_division_by_zero_returns_infinity(self):
        f1 = 5.0
        f2 = 0.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 / bf2
        self.assertTrue(result.is_infinity() or result.is_nan())

    def test_flexfloat_zero_divided_by_zero_returns_nan(self):
        f1 = 0.0
        f2 = 0.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 / bf2
        self.assertTrue(result.is_nan())

    def test_flexfloat_division_negative_values_works_correctly(self):
        f1 = -8.0
        f2 = 2.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 / bf2
        expected = f1 / f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_division_fractional_values_works_correctly(self):
        f1 = 0.5
        f2 = 0.25
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 / bf2
        expected = f1 / f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_division_large_numbers_works_correctly(self):
        f1 = 1e308
        f2 = 1e154
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 / bf2
        expected = f1 / f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_division_infinity_by_value_returns_infinity(self):
        bf_inf = FlexFloat.infinity()
        bf_val = FlexFloat.from_float(2.0)
        result = bf_inf / bf_val
        self.assertTrue(result.is_infinity())

    def test_flexfloat_division_value_by_infinity_returns_zero(self):
        bf_val = FlexFloat.from_float(2.0)
        bf_inf = FlexFloat.infinity()
        result = bf_val / bf_inf
        self.assertTrue(result.is_zero())

    def test_flexfloat_division_nan_propagates(self):
        bf_nan = FlexFloat.nan()
        bf_val = FlexFloat.from_float(2.0)
        result = bf_nan / bf_val
        self.assertTrue(result.is_nan())
        result2 = bf_val / bf_nan
        self.assertTrue(result2.is_nan())

    def test_flexfloat_division_with_native_types(self):
        """Test division with mixed operand types (FlexFloat with native numbers)."""
        bf = FlexFloat.from_float(10.0)

        # FlexFloat / int
        result = bf / 2
        self.assertAlmostEqualRel(result.to_float(), 5.0)

        # FlexFloat / float
        result = bf / 2.5
        self.assertAlmostEqualRel(result.to_float(), 4.0)

        # int / FlexFloat
        result = 20 / bf
        self.assertAlmostEqualRel(result.to_float(), 2.0)

        # float / FlexFloat
        result = 15.0 / bf
        self.assertAlmostEqualRel(result.to_float(), 1.5)

    def test_flexfloat_division_sign_combinations(self):
        """Test all combinations of positive and negative operands."""
        pos = FlexFloat.from_float(8.0)
        neg = FlexFloat.from_float(-4.0)

        # positive / positive = positive
        result = pos / FlexFloat.from_float(2.0)
        self.assertAlmostEqualRel(result.to_float(), 4.0)
        self.assertFalse(result.sign)

        # positive / negative = negative
        result = pos / neg
        self.assertAlmostEqualRel(result.to_float(), -2.0)
        self.assertTrue(result.sign)

        # negative / positive = negative
        result = neg / FlexFloat.from_float(2.0)
        self.assertAlmostEqualRel(result.to_float(), -2.0)
        self.assertTrue(result.sign)

        # negative / negative = positive
        result = neg / FlexFloat.from_float(-2.0)
        self.assertAlmostEqualRel(result.to_float(), 2.0)
        self.assertFalse(result.sign)

    def test_flexfloat_division_small_numbers(self):
        """Test division with very small numbers for precision."""
        small1 = FlexFloat.from_float(1e-10)
        small2 = FlexFloat.from_float(2e-10)

        result = small1 / small2
        expected = 0.5
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_division_precision_edge_case(self):
        """Test division that might cause precision issues."""
        # Test case that could cause rounding errors
        a = FlexFloat.from_float(1.0)
        b = FlexFloat.from_float(3.0)

        result = a / b
        expected = 1.0 / 3.0

        # Allow for floating-point precision differences
        self.assertTrue(
            abs(result.to_float() - expected) < 1e-15,
            f"Expected {expected}, got {result.to_float()}",
        )

    def test_flexfloat_division_by_very_small_number(self):
        """Test division by a very small number (close to underflow)."""
        normal = FlexFloat.from_float(1.0)
        tiny = FlexFloat.from_float(1e-300)

        result = normal / tiny
        # Should be a very large number
        self.assertTrue(result.to_float() > 1e299)

    def test_flexfloat_division_resulting_in_very_small_number(self):
        """Test division that results in a very small number (close to underflow)."""
        tiny = FlexFloat.from_float(1e-300)
        large = FlexFloat.from_float(1e50)

        result = tiny / large

        self.assertFalse(result.is_zero())
        self.assertTrue(len(result.exponent) > 11)


if __name__ == "__main__":
    unittest.main()
