"""Tests for FlexFloat comparison operations."""

import unittest

from flexfloat import FlexFloat
from tests import FlexFloatTestCase


class TestFlexFloatComparison(FlexFloatTestCase):
    """Test FlexFloat comparison operations."""

    def setUp(self):
        """Set up test fixtures."""
        # Standard test values
        self.zero = FlexFloat.from_float(0.0)
        self.positive_zero = FlexFloat.from_float(0.0)
        self.negative_zero = FlexFloat.from_float(-0.0)
        self.one = FlexFloat.from_float(1.0)
        self.two = FlexFloat.from_float(2.0)
        self.negative_one = FlexFloat.from_float(-1.0)
        self.negative_two = FlexFloat.from_float(-2.0)
        self.pi = FlexFloat.from_float(3.14159)
        self.e = FlexFloat.from_float(2.71828)

        # Special values
        self.positive_inf = FlexFloat.from_float(float("inf"))
        self.negative_inf = FlexFloat.from_float(float("-inf"))
        self.nan = FlexFloat.from_float(float("nan"))
        self.another_nan = FlexFloat.from_float(float("nan"))

        # Small values for precision testing
        self.small_positive = FlexFloat.from_float(1e-10)
        self.small_negative = FlexFloat.from_float(-1e-10)
        self.very_small = FlexFloat.from_float(1e-100)

    # === Test comparison operators (indirect testing of _compare) ===
    def test_compare_functionality_through_operators(self):
        """Test _compare functionality through public comparison operators."""
        # Test equal values
        self.assertTrue(self.one == FlexFloat.from_float(1.0))
        self.assertTrue(self.zero == self.positive_zero)
        self.assertTrue(self.zero == self.negative_zero)

        # Test less than relationships
        self.assertTrue(self.one < self.two)
        self.assertTrue(self.negative_two < self.negative_one)
        self.assertTrue(self.negative_one < self.one)

        # Test greater than relationships
        self.assertTrue(self.two > self.one)
        self.assertTrue(self.negative_one > self.negative_two)
        self.assertTrue(self.one > self.negative_one)

        # Test NaN comparisons (all should be False except !=)
        self.assertFalse(self.nan == self.one)
        self.assertFalse(self.one == self.nan)
        self.assertFalse(self.nan == self.another_nan)
        self.assertTrue(self.nan != self.one)  # Only != should be True

        # Test infinity comparisons
        self.assertTrue(self.positive_inf > self.one)
        self.assertTrue(self.one < self.positive_inf)
        self.assertTrue(self.negative_inf < self.one)
        self.assertTrue(self.positive_inf == self.positive_inf)
        self.assertTrue(self.positive_inf > self.negative_inf)

    # === Test __eq__ method ===
    def test_equality_same_values(self):
        """Test equality with same values."""
        self.assertTrue(self.one == FlexFloat.from_float(1.0))
        self.assertTrue(self.zero == self.positive_zero)
        self.assertTrue(self.zero == self.negative_zero)
        self.assertTrue(self.pi == FlexFloat.from_float(3.14159))

    def test_equality_different_values(self):
        """Test equality with different values."""
        self.assertFalse(self.one == self.two)
        self.assertFalse(self.one == self.negative_one)
        self.assertFalse(self.pi == self.e)

    def test_equality_with_nan(self):
        """Test equality with NaN values."""
        self.assertFalse(self.nan == self.nan)
        self.assertFalse(self.nan == self.another_nan)
        self.assertFalse(self.nan == self.one)
        self.assertFalse(self.one == self.nan)

    def test_equality_with_infinity(self):
        """Test equality with infinity values."""
        self.assertTrue(self.positive_inf == FlexFloat.from_float(float("inf")))
        self.assertTrue(self.negative_inf == FlexFloat.from_float(float("-inf")))
        self.assertFalse(self.positive_inf == self.negative_inf)
        self.assertFalse(self.positive_inf == self.one)

    def test_equality_with_mixed_types(self):
        """Test equality with mixed numeric types."""
        self.assertTrue(self.one == 1.0)
        self.assertTrue(self.one == 1)
        self.assertTrue(self.zero == 0.0)
        self.assertTrue(self.zero == 0)
        self.assertFalse(self.one == 2.0)
        self.assertFalse(self.one == "1")  # Non-numeric type

    # === Test __ne__ method ===
    def test_inequality_same_values(self):
        """Test inequality with same values."""
        self.assertFalse(self.one != FlexFloat.from_float(1.0))
        self.assertFalse(self.zero != self.positive_zero)
        self.assertFalse(self.pi != FlexFloat.from_float(3.14159))

    def test_inequality_different_values(self):
        """Test inequality with different values."""
        self.assertTrue(self.one != self.two)
        self.assertTrue(self.one != self.negative_one)
        self.assertTrue(self.pi != self.e)

    def test_inequality_with_nan(self):
        """Test inequality with NaN values."""
        self.assertTrue(self.nan != self.nan)
        self.assertTrue(self.nan != self.another_nan)
        self.assertTrue(self.nan != self.one)
        self.assertTrue(self.one != self.nan)

    def test_inequality_with_mixed_types(self):
        """Test inequality with mixed numeric types."""
        self.assertFalse(self.one != 1.0)
        self.assertFalse(self.one != 1)
        self.assertTrue(self.one != 2.0)
        self.assertTrue(self.one != "1")  # Non-numeric type

    # === Test __lt__ method ===
    def test_less_than_basic(self):
        """Test basic less than comparisons."""
        self.assertTrue(self.one < self.two)
        self.assertTrue(self.negative_two < self.negative_one)
        self.assertTrue(self.negative_one < self.zero)
        self.assertTrue(self.zero < self.one)
        self.assertFalse(self.two < self.one)
        self.assertFalse(self.one < self.one)

    def test_less_than_with_infinity(self):
        """Test less than with infinity values."""
        self.assertTrue(self.one < self.positive_inf)
        self.assertTrue(self.negative_inf < self.one)
        self.assertTrue(self.negative_inf < self.positive_inf)
        self.assertFalse(self.positive_inf < self.one)
        self.assertFalse(self.positive_inf < self.positive_inf)

    def test_less_than_with_nan(self):
        """Test less than with NaN values."""
        self.assertFalse(self.nan < self.one)
        self.assertFalse(self.one < self.nan)
        self.assertFalse(self.nan < self.nan)

    def test_less_than_with_mixed_types(self):
        """Test less than with mixed numeric types."""
        self.assertTrue(self.one < 2.0)
        self.assertTrue(self.one < 2)
        self.assertFalse(self.one < 1.0)
        self.assertFalse(self.two < 1.0)

    # === Test __le__ method ===
    def test_less_than_or_equal_basic(self):
        """Test basic less than or equal comparisons."""
        self.assertTrue(self.one <= self.two)
        self.assertTrue(self.one <= self.one)
        self.assertTrue(self.negative_two <= self.negative_one)
        self.assertTrue(self.zero <= self.zero)
        self.assertFalse(self.two <= self.one)

    def test_less_than_or_equal_with_infinity(self):
        """Test less than or equal with infinity values."""
        self.assertTrue(self.one <= self.positive_inf)
        self.assertTrue(self.positive_inf <= self.positive_inf)
        self.assertTrue(self.negative_inf <= self.one)
        self.assertFalse(self.positive_inf <= self.one)

    def test_less_than_or_equal_with_nan(self):
        """Test less than or equal with NaN values."""
        self.assertFalse(self.nan <= self.one)
        self.assertFalse(self.one <= self.nan)
        self.assertFalse(self.nan <= self.nan)

    # === Test __gt__ method ===
    def test_greater_than_basic(self):
        """Test basic greater than comparisons."""
        self.assertTrue(self.two > self.one)
        self.assertTrue(self.negative_one > self.negative_two)
        self.assertTrue(self.one > self.zero)
        self.assertTrue(self.zero > self.negative_one)
        self.assertFalse(self.one > self.two)
        self.assertFalse(self.one > self.one)

    def test_greater_than_with_infinity(self):
        """Test greater than with infinity values."""
        self.assertTrue(self.positive_inf > self.one)
        self.assertTrue(self.one > self.negative_inf)
        self.assertTrue(self.positive_inf > self.negative_inf)
        self.assertFalse(self.one > self.positive_inf)
        self.assertFalse(self.positive_inf > self.positive_inf)

    def test_greater_than_with_nan(self):
        """Test greater than with NaN values."""
        self.assertFalse(self.nan > self.one)
        self.assertFalse(self.one > self.nan)
        self.assertFalse(self.nan > self.nan)

    # === Test __ge__ method ===
    def test_greater_than_or_equal_basic(self):
        """Test basic greater than or equal comparisons."""
        self.assertTrue(self.two >= self.one)
        self.assertTrue(self.one >= self.one)
        self.assertTrue(self.negative_one >= self.negative_two)
        self.assertTrue(self.zero >= self.zero)
        self.assertFalse(self.one >= self.two)

    def test_greater_than_or_equal_with_infinity(self):
        """Test greater than or equal with infinity values."""
        self.assertTrue(self.positive_inf >= self.one)
        self.assertTrue(self.positive_inf >= self.positive_inf)
        self.assertTrue(self.one >= self.negative_inf)
        self.assertFalse(self.one >= self.positive_inf)

    def test_greater_than_or_equal_with_nan(self):
        """Test greater than or equal with NaN values."""
        self.assertFalse(self.nan >= self.one)
        self.assertFalse(self.one >= self.nan)
        self.assertFalse(self.nan >= self.nan)

    # === Test edge cases and precision ===
    def test_comparison_small_values(self):
        """Test comparisons with very small values."""
        self.assertTrue(self.small_positive > self.zero)
        self.assertTrue(self.zero > self.small_negative)
        self.assertTrue(self.small_positive > self.small_negative)
        self.assertTrue(self.very_small > self.zero)

    def test_comparison_precision(self):
        """Test comparisons with values that differ by small amounts."""
        val1 = FlexFloat.from_float(1.0000000001)
        val2 = FlexFloat.from_float(1.0000000002)

        # These should still be distinguishable
        self.assertTrue(val1 < val2)
        self.assertTrue(val2 > val1)
        self.assertFalse(val1 == val2)

    def test_comparison_with_zero_variants(self):
        """Test comparisons with positive and negative zero."""
        self.assertTrue(self.positive_zero == self.negative_zero)
        self.assertFalse(self.positive_zero != self.negative_zero)
        self.assertFalse(self.positive_zero < self.negative_zero)
        self.assertFalse(self.positive_zero > self.negative_zero)
        self.assertTrue(self.positive_zero <= self.negative_zero)
        self.assertTrue(self.positive_zero >= self.negative_zero)

    def test_transitivity(self):
        """Test transitivity of comparison operations."""
        # If a < b and b < c, then a < c
        a = FlexFloat.from_float(1.0)
        b = FlexFloat.from_float(2.0)
        c = FlexFloat.from_float(3.0)

        self.assertTrue(a < b)
        self.assertTrue(b < c)
        self.assertTrue(a < c)  # Transitivity

        # Same for <=
        self.assertTrue(a <= b)
        self.assertTrue(b <= c)
        self.assertTrue(a <= c)  # Transitivity

    def test_reflexivity(self):
        """Test reflexivity of comparison operations."""
        # a == a should always be True (except for NaN)
        self.assertTrue(self.one == self.one)
        self.assertTrue(self.zero == self.zero)
        self.assertTrue(self.positive_inf == self.positive_inf)

        # a <= a and a >= a should always be True (except for NaN)
        self.assertTrue(self.one <= self.one)
        self.assertTrue(self.one >= self.one)

        # NaN is special
        self.assertFalse(self.nan == self.nan)

    def test_antisymmetry(self):
        """Test antisymmetry of comparison operations."""
        # If a <= b and b <= a, then a == b
        a = FlexFloat.from_float(1.0)
        b = FlexFloat.from_float(1.0)

        self.assertTrue(a <= b)
        self.assertTrue(b <= a)
        self.assertTrue(a == b)

    def test_consistency(self):
        """Test consistency between different comparison operators."""
        # If a < b, then a <= b and a != b and not (a > b) and not (a >= b)
        a = FlexFloat.from_float(1.0)
        b = FlexFloat.from_float(2.0)

        self.assertTrue(a < b)
        self.assertTrue(a <= b)
        self.assertTrue(a != b)
        self.assertFalse(a > b)
        self.assertFalse(a >= b)
        self.assertFalse(a == b)

    # === Test sorting and ordering ===
    def test_sorting(self):
        """Test that FlexFloat values can be sorted correctly."""
        values = [
            FlexFloat.from_float(3.14),
            FlexFloat.from_float(-1.0),
            FlexFloat.from_float(0.0),
            FlexFloat.from_float(2.71),
            FlexFloat.from_float(-3.14),
            FlexFloat.from_float(1.0),
        ]

        sorted_values = sorted(values)
        expected_order = [-3.14, -1.0, 0.0, 1.0, 2.71, 3.14]

        for i, expected in enumerate(expected_order):
            self.assertEqual(sorted_values[i], FlexFloat.from_float(expected))

    def test_min_max(self):
        """Test min and max functions with FlexFloat values."""
        values = [
            FlexFloat.from_float(3.14),
            FlexFloat.from_float(-1.0),
            FlexFloat.from_float(2.71),
        ]

        self.assertEqual(min(values), FlexFloat.from_float(-1.0))
        self.assertEqual(max(values), FlexFloat.from_float(3.14))


if __name__ == "__main__":
    unittest.main()
