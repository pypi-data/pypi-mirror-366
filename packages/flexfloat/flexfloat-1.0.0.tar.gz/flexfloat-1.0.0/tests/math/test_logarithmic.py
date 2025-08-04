"""Tests for logarithmic functions in FlexFloat math module."""

import math
import unittest

from flexfloat import FlexFloat
from flexfloat import math as ffmath
from tests.math import TestMathSetup


class TestLogarithmicFunctions(TestMathSetup):
    """Test logarithmic functions."""

    def test_log_natural_normal_cases(self):
        """Test natural logarithm with normal positive values."""
        positive_values = [val for val in self.regular_values if val > 0]
        self.compare_with_math(ffmath.log, math.log, positive_values)

    def test_log_with_base_normal_cases(self):
        """Test logarithm with different bases."""
        positive_values = [val for val in self.basic_values if val > 0]
        bases = [2.0, 10.0, math.e]

        for base in bases:
            for val in positive_values:
                with self.subTest(value=val, base=base):
                    ff_val = FlexFloat.from_float(val)
                    ff_base = FlexFloat.from_float(base)
                    result = ffmath.log(ff_val, ff_base)
                    expected = math.log(val, base)
                    self.assertAlmostEqualRel(result.to_float(), expected, 1e-10)

    def test_log_edge_cases(self):
        """Test log edge cases."""
        # Test log(1) = 0
        result = ffmath.log(FlexFloat.from_float(1.0))
        self.assertAlmostEqualRel(result.to_float(), 0.0)

        # Test log(0) is undefined (should be -infinity or NaN)
        result = ffmath.log(FlexFloat.from_float(0.0))
        self.assertTrue(
            result.is_infinity() or result.is_nan(), "log(0) should be -infinity or NaN"
        )

        # Test log of negative values should be NaN
        result = ffmath.log(FlexFloat.from_float(-1.0))
        self.assertTrue(result.is_nan())

        # Test log(inf) = inf
        result = ffmath.log(FlexFloat.infinity(sign=False))
        self.assertTrue(result.is_infinity())
        self.assertFalse(result.sign)

    def test_log10_normal_cases(self):
        """Test base-10 logarithm."""
        positive_values = [val for val in self.regular_values if val > 0]
        self.compare_with_math(ffmath.log10, math.log10, positive_values)

    def test_log2_normal_cases(self):
        """Test base-2 logarithm."""
        positive_values = [val for val in self.regular_values if val > 0]
        self.compare_with_math(ffmath.log2, math.log2, positive_values)

    def test_log1p_normal_cases(self):
        """Test log(1+x) function."""
        # Test values near zero where log1p is more accurate
        test_values = [0.0, 1e-10, -1e-10, 1e-15, -1e-15, 0.1, -0.1, 0.5]
        self.compare_with_math(ffmath.log1p, math.log1p, test_values)

    def test_expm1_normal_cases(self):
        """Test exp(x)-1 function."""
        # Test values near zero where expm1 is more accurate
        test_values = [0.0, 1e-10, -1e-10, 1e-15, -1e-15, 0.1, -0.1, 0.5]
        self.compare_with_math(ffmath.expm1, math.expm1, test_values)

    def test_log_extreme_values(self):
        """Test log with extreme values."""
        # Very large value
        large_val = FlexFloat.from_float(1e308)
        result = ffmath.log(large_val)
        # FlexFloat may have different precision for extreme values
        # Just check it's in the right ballpark
        result_val = result.to_float()
        self.assertTrue(700 < result_val < 720)

        # Very small positive value
        small_val = FlexFloat.from_float(1e-308)
        result = ffmath.log(small_val)
        result_val = result.to_float()
        self.assertTrue(-720 < result_val < -700)

    def test_log_with_extreme_integers(self):
        """Test log with very large integers created via from_int."""
        # Test log of powers of 10
        large_power_of_10 = FlexFloat.from_int(10**100)
        result = ffmath.log10(large_power_of_10)
        # log10(10^100) should be exactly 100
        self.assertAlmostEqualRel(result.to_float(), 100.0, tolerance=1e-10)

        # Test natural log of powers of e (approximately)
        # e^100 is very large, let's use a smaller power we can compute
        large_int = FlexFloat.from_int(2**1000)
        result = ffmath.log(large_int)
        # ln(2^1000) = 1000 * ln(2) ≈ 1000 * 0.693147
        expected = 1000 * math.log(2)
        self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-8)

    def test_log_on_extreme_flexfloats(self):
        """Test log function on extreme FlexFloat values."""
        for extreme_val in self.extreme_flexfloats:
            if extreme_val > FlexFloat.from_int(0):  # Only positive values for log
                result = ffmath.log(extreme_val)
                self.assertFalse(
                    result.is_nan(),
                    "log should not return NaN for positive extreme values",
                )

                # For very large values, log should be large and positive
                if extreme_val > FlexFloat.from_float(1.0):
                    self.assertTrue(
                        result > FlexFloat.from_int(0),
                        "log of extreme value > 1 should be positive",
                    )

    def test_mathematical_identities(self):
        """Test that mathematical identities hold with FlexFloat operations."""
        # Test log(a*b) = log(a) + log(b)
        test_pairs = [(2.0, 3.0), (5.0, 7.0), (1.5, 2.5)]

        for a, b in test_pairs:
            with self.subTest(a=a, b=b):
                ff_a = FlexFloat.from_float(a)
                ff_b = FlexFloat.from_float(b)

                # log(a*b)
                product = ff_a * ff_b
                log_product = ffmath.log(product)

                # log(a) + log(b)
                log_a = ffmath.log(ff_a)
                log_b = ffmath.log(ff_b)
                sum_logs = log_a + log_b

                # Check that the values are close enough
                self.assertAlmostEqualRel(log_product.to_float(), sum_logs.to_float())


if __name__ == "__main__":
    unittest.main()
