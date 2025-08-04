"""Tests for square root and cube root functions in FlexFloat math module."""

import math
import unittest

from flexfloat import FlexFloat
from flexfloat import math as ffmath
from tests.math import TestMathSetup


class TestSqrtFunctions(TestMathSetup):
    """Test square root and cube root functions."""

    def test_sqrt_normal_cases(self):
        """Test sqrt with normal positive values."""
        positive_values = [val for val in self.regular_values if val > 0]
        self.compare_with_math(ffmath.sqrt, math.sqrt, positive_values)

    def test_sqrt_edge_cases(self):
        """Test sqrt edge cases."""
        # Test zero
        result = ffmath.sqrt(FlexFloat.from_float(0.0))
        self.assertTrue(result.is_zero())

        # Test positive infinity
        result = ffmath.sqrt(FlexFloat.infinity(sign=False))
        self.assertTrue(result.is_infinity())
        self.assertFalse(result.sign)

        # Test NaN
        result = ffmath.sqrt(FlexFloat.nan())
        self.assertTrue(result.is_nan())

        # Test negative values (should return NaN)
        result = ffmath.sqrt(FlexFloat.from_float(-1.0))
        self.assertTrue(result.is_nan())

    def test_sqrt_extreme_values(self):
        """Test sqrt with very large and small values."""
        # Very large values
        large_val = FlexFloat.from_float(1e300)
        result = ffmath.sqrt(large_val)
        expected = math.sqrt(1e300)
        self.assertAlmostEqualRel(result.to_float(), expected, 1e-10)

        # Very small values
        small_val = FlexFloat.from_float(1e-300)
        result = ffmath.sqrt(small_val)
        expected = math.sqrt(1e-300)
        self.assertAlmostEqualRel(result.to_float(), expected, 1e-10)

    def test_cbrt_normal_cases(self):
        """Test cube root with normal values."""
        self.compare_with_math(
            ffmath.cbrt,
            math.cbrt,
            self.regular_values,
            tolerance=1e-9,
        )

    def test_cbrt_edge_cases(self):
        """Test cube root edge cases."""
        # Test zero
        result = ffmath.cbrt(FlexFloat.zero())
        self.assertTrue(result.is_zero())

        # Test perfect cubes
        test_cases = [(8.0, 2.0), (27.0, 3.0), (-8.0, -2.0), (-27.0, -3.0)]
        for input_val, expected in test_cases:
            result = ffmath.cbrt(FlexFloat.from_float(input_val))
            self.assertAlmostEqualRel(result.to_float(), expected, 1e-10)

    def test_sqrt_with_extreme_integers(self):
        """Test sqrt with very large integers created via from_int."""
        # Test sqrt of very large perfect squares
        large_int = FlexFloat.from_int(10**50)  # 1 followed by 50 zeros
        result = ffmath.sqrt(large_int)

        # sqrt(10^50) = 10^25
        expected = FlexFloat.from_int(10**25)
        # Should be very close to expected
        self.assertAlmostEqualRel(
            result.to_float(), expected.to_float(), tolerance=1e-8
        )

        # Test with perfect square of 2^100
        large_square = FlexFloat.from_int(2**100)
        result = ffmath.sqrt(large_square)
        expected = FlexFloat.from_int(2**50)
        # Should be exact for perfect squares of powers of 2
        self.assertAlmostEqualRel(
            result.to_float(), expected.to_float(), tolerance=1e-12
        )

    def test_sqrt_on_extreme_flexfloats(self):
        """Test sqrt function on extreme FlexFloat values."""
        for extreme_val in self.extreme_flexfloats:
            # Only non-negative values for sqrt
            if extreme_val < 0:
                continue
            result = ffmath.sqrt(extreme_val)
            self.assertFalse(
                result.is_nan(),
                "sqrt should not return NaN for positive extreme values",
            )

            # For values >= 1, sqrt should be <= original value
            if extreme_val >= 1:
                self.assertTrue(
                    result <= extreme_val,
                    "sqrt(large_value) should be less than or equal to the value",
                )
            else:
                # For values < 1, sqrt should be > original value
                self.assertTrue(
                    result > extreme_val,
                    "sqrt(small_value) should be greater than the value",
                )


if __name__ == "__main__":
    unittest.main()
