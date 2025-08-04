"""
Tests for FlexFloat.to_int method.

This module tests the to_int method which converts FlexFloat instances
to unbounded Python integers.
"""

import math
import unittest
from sys import float_info

from flexfloat import FlexFloat


class TestToInt(unittest.TestCase):
    """Test cases for FlexFloat.to_int method."""

    def test_to_int_zero(self):
        """Test to_int with zero values."""
        zero = FlexFloat.from_float(0.0)
        self.assertEqual(zero.to_int(), 0)

        neg_zero = FlexFloat.from_float(-0.0)
        self.assertEqual(neg_zero.to_int(), 0)

    def test_to_int_positive_integers(self):
        """Test to_int with positive integer values."""
        test_values = [1, 2, 3, 4, 5, 10, 100, 1000, 12345]

        for i in test_values:
            with self.subTest(value=i):
                ff = FlexFloat.from_float(i)
                result = ff.to_int()
                self.assertEqual(result, i, f"to_int({i}) failed")
                self.assertIsInstance(result, int)

    def test_to_int_negative_integers(self):
        """Test to_int with negative integer values."""
        test_values = [-1, -2, -3, -4, -5, -10, -100, -1000, -12345]

        for i in test_values:
            with self.subTest(value=i):
                ff = FlexFloat.from_float(i)
                result = ff.to_int()
                self.assertEqual(result, i, f"to_int({i}) failed")
                self.assertIsInstance(result, int)

    def test_to_int_fractional_values(self):
        """Test to_int with fractional values (should truncate towards zero)."""
        test_cases = [
            1.5,
            1.9,
            2.1,
            2.9,
            -1.5,
            -1.9,
            -2.1,
            -2.9,
            0.1,
            0.9,
            -0.1,
            -0.9,
            3.14159,
            -3.14159,
            99.999,
            -99.999,
        ]

        for float_val in test_cases:
            with self.subTest(value=float_val):
                ff = FlexFloat.from_float(float_val)
                result = ff.to_int()
                expected_int = int(float_val)

                self.assertEqual(
                    result,
                    expected_int,
                    f"to_int({float_val}) = {result}, expected {expected_int}",
                )
                self.assertIsInstance(result, int)

    def test_to_int_special_values(self):
        """Test to_int with special floating-point values."""
        # Test infinity - should raise an exception
        pos_inf = FlexFloat.infinity()
        with self.assertRaises((ValueError, OverflowError, ArithmeticError)):
            pos_inf.to_int()

        neg_inf = FlexFloat.infinity(True)
        with self.assertRaises((ValueError, OverflowError, ArithmeticError)):
            neg_inf.to_int()

        # Test NaN - should raise an exception
        nan = FlexFloat.nan()
        with self.assertRaises((ValueError, OverflowError, ArithmeticError)):
            nan.to_int()

    def test_to_int_python_float_comparison(self):
        """Test to_int against Python's built-in float to int conversion."""
        test_values = [
            0.0,
            -0.0,
            1.0,
            -1.0,
            1.5,
            -1.5,
            2.7,
            -2.7,
            3.14159,
            -3.14159,
            10.5,
            -10.5,
            100.99,
            -100.99,
            1000000.0,
            -1000000.0,
            0.000001,
            -0.000001,
            42.42,
            -42.42,
            123.456,
            -123.456,
        ]

        for val in test_values:
            with self.subTest(value=val):
                ff = FlexFloat.from_float(val)
                python_result = int(val)
                flexfloat_result = ff.to_int()
                self.assertEqual(
                    flexfloat_result,
                    python_result,
                    f"FlexFloat.to_int({val}) = {flexfloat_result}, "
                    f"but int({val}) = {python_result}",
                )

    def test_to_int_large_values(self):
        """Test to_int with large values."""
        # Test with large integers that can be exactly represented
        large_values = [
            2**10,
            2**20,
            2**30,
            2**30 + 123,
            -(2**10),
            -(2**20),
            -(2**30),
            -(2**30 - 123),
        ]

        for val in large_values:
            with self.subTest(value=val):
                ff = FlexFloat.from_float(val)
                result = ff.to_int()
                self.assertEqual(result, int(float(val)))

    def test_to_int_beyond_float_bounds(self):
        """Test to_int with values that may exceed normal float precision."""
        # Test with the largest integer exactly representable in double precision
        huge_values = [2**600, 2**1000, -(2**600), -(2**1000)]
        margin = 1234

        for val in huge_values:
            val += margin  # So there is truncation
            with self.subTest(value=val):
                ff = FlexFloat.from_float(val)
                self.assertEqual(ff.to_int(), val - margin)

    def test_to_int_edge_cases(self):
        """Test to_int with edge cases and boundary values."""
        # Test very small positive and negative values
        tiny_values = [1e-10, -1e-10, 1e-100, -1e-100]
        for val in tiny_values:
            with self.subTest(value=val):
                ff = FlexFloat.from_float(val)
                result = ff.to_int()
                self.assertEqual(result, 0, f"to_int({val}) should be 0")

        # Test values just above and below integers
        edge_cases = [
            (0.9999999, 0),
            (1.0000001, 1),
            (-0.9999999, 0),
            (-1.0000001, -1),
            (9.9999999, 9),
            (10.0000001, 10),
        ]

        for val, expected in edge_cases:
            with self.subTest(value=val):
                ff = FlexFloat.from_float(val)
                result = ff.to_int()
                self.assertEqual(result, expected)

    def test_to_int_powers_of_two(self):
        """Test to_int with powers of 2."""
        for exp in range(0, 256):
            power_of_2 = 2**exp
            neg_power_of_2 = -(2**exp)

            with self.subTest(exponent=exp):
                # Positive power of 2
                ff_pos = FlexFloat.from_float(power_of_2)
                self.assertEqual(ff_pos.to_int(), power_of_2)

                # Negative power of 2
                ff_neg = FlexFloat.from_float(neg_power_of_2)
                self.assertEqual(ff_neg.to_int(), neg_power_of_2)

    def test_to_float_precision_limits(self):
        """Test to_int at the precision limits of floating-point format."""
        # Test around the precision limit of double precision floats
        min_float = float_info.min
        ff = FlexFloat.from_float(min_float) / 1000
        self.assertEqual(ff.to_int(), 0, f"to_int({min_float}) should be 0")

        max_float = float_info.max
        ff = FlexFloat.from_float(max_float) * 1000
        self.assertLess(
            ff.to_int(),
            int(max_float) * 1000,
        )
        self.assertGreater(
            ff.to_int(),
            int(max_float),
        )

    def test_to_int_consistency(self):
        """Test that to_int is consistent with mathematical truncation."""
        test_values = [
            (5.7, 5),
            (5.3, 5),
            (5.0, 5),
            (-5.7, -5),
            (-5.3, -5),
            (-5.0, -5),
            (0.5, 0),
            (-0.5, 0),
            (1.99999, 1),
            (-1.99999, -1),
        ]

        for val, expected in test_values:
            with self.subTest(value=val):
                ff = FlexFloat.from_float(val)
                result = ff.to_int()
                self.assertEqual(result, expected)

                # Verify it matches math.trunc behavior
                self.assertEqual(result, math.trunc(val))


if __name__ == "__main__":
    unittest.main()
