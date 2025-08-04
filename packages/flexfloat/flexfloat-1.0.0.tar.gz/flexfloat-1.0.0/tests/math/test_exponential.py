"""Tests for exponential and power functions in FlexFloat math module."""

import math
import unittest

from flexfloat import FlexFloat
from flexfloat import math as ffmath
from tests.math import TestMathSetup


class TestExponentialFunctions(TestMathSetup):
    """Test exponential and power functions."""

    def test_exp_normal_cases(self):
        """Test exp function with normal values."""
        self.compare_with_math(ffmath.exp, math.exp, self.regular_values)

    def test_exp_edge_cases(self):
        """Test exp function with edge cases."""
        # Test zero
        result = ffmath.exp(FlexFloat.from_float(0.0))
        self.assertAlmostEqualRel(result.to_float(), 1.0)

        # Test positive infinity
        result = ffmath.exp(FlexFloat.infinity(sign=False))
        self.assertTrue(result.is_infinity())
        self.assertFalse(result.sign)

        # Test negative infinity
        result = ffmath.exp(FlexFloat.infinity(sign=True))
        self.assertTrue(result.is_zero())

        # Test NaN
        result = ffmath.exp(FlexFloat.nan())
        self.assertTrue(result.is_nan())

    def test_exp_extreme_values(self):
        """Test exp with values outside normal float range."""
        # Very large positive values should not overflow
        large_val = FlexFloat.from_float(1000.0)  # Would overflow normal exp
        result = ffmath.exp(large_val)
        self.assertFalse(
            result.is_infinity(), "exp should handle large values without overflow"
        )
        self.assertTrue(result > 1e100, "exp of large value should be very large")

        # Very large negative values should approach zero
        large_neg_val = FlexFloat.from_float(-1000.0)
        result = ffmath.exp(large_neg_val)
        self.assertFalse(result.is_zero(), "Should not be exactly zero")
        self.assertTrue(result < 1e-100, "exp of large negative should be very small")

    def test_pow_normal_cases(self):
        """Test pow function with normal cases."""
        test_cases = [
            (2.0, 3.0),
            (3.0, 2.0),
            (4.0, 0.5),
            (9.0, 0.5),
            (1.0, 100.0),
            (100.0, 0.0),
            (-2.0, 3.0),
            (-2.0, 2.0),
            (0.5, 2.0),
            (0.25, 0.5),
        ]

        for base, exp in test_cases:
            with self.subTest(base=base, exp=exp):
                ff_base = FlexFloat.from_float(base)
                ff_exp = FlexFloat.from_float(exp)
                result = ffmath.pow(ff_base, ff_exp)
                expected = math.pow(base, exp)

                if math.isnan(expected):
                    self.assertTrue(result.is_nan())
                elif math.isinf(expected):
                    self.assertTrue(result.is_infinity())
                    self.assertEqual(result.sign, expected < 0)
                else:
                    self.assertAlmostEqualRel(result.to_float(), expected, 1e-10)

    def test_pow_edge_cases(self):
        """Test pow function edge cases."""
        # Test x^0 = 1 for any finite x
        for val in [0.0, 1.0, -1.0, 100.0, -100.0]:
            result = ffmath.pow(FlexFloat.from_float(val), FlexFloat.from_float(0.0))
            self.assertAlmostEqualRel(result.to_float(), 1.0)

        # Test 1^x = 1 for any finite x
        for exp in [0.0, 1.0, -1.0, 100.0, -100.0]:
            result = ffmath.pow(FlexFloat.from_float(1.0), FlexFloat.from_float(exp))
            self.assertAlmostEqualRel(result.to_float(), 1.0)

        # Test 0^x cases
        result = ffmath.pow(FlexFloat.from_float(0.0), FlexFloat.from_float(2.0))
        self.assertTrue(result.is_zero())

        result = ffmath.pow(FlexFloat.from_float(0.0), FlexFloat.from_float(-2.0))
        self.assertTrue(result.is_infinity())

    def test_exp_with_manageable_inputs(self):
        """Test exp function with inputs that won't cause overflow."""
        # Use smaller inputs that won't cause exp to overflow
        manageable_inputs = [
            FlexFloat.from_float(10.0),
            FlexFloat.from_float(50.0),
            FlexFloat.from_float(100.0),
            FlexFloat.from_float(-10.0),
            FlexFloat.from_float(-50.0),
            FlexFloat.from_float(-100.0),
        ]

        zero = FlexFloat.from_int(0)
        one = FlexFloat.from_int(1)

        for input_val in manageable_inputs:
            exp_result = ffmath.exp(input_val)

            # Basic sanity checks
            self.assertFalse(
                exp_result.is_nan(), "exp of manageable input should not be NaN"
            )

            if input_val > zero:
                self.assertTrue(exp_result > one, "exp(positive_input) should be > 1")
            elif input_val < zero:
                self.assertTrue(
                    exp_result > zero, "exp(negative_input) should be positive"
                )
                self.assertTrue(exp_result < one, "exp(negative_input) should be < 1")
            else:  # input is 0
                self.assertAlmostEqualRel(exp_result.to_float(), 1.0)

    def test_pow_extreme_exponents(self):
        """Test pow with extreme exponents."""
        # Large exponent
        base = FlexFloat.from_float(2.0)
        large_exp = FlexFloat.from_float(1000.0)
        result = ffmath.pow(base, large_exp)

        # Should not overflow to infinity in FlexFloat
        self.assertFalse(
            result.is_infinity(), "FlexFloat should handle large exponents"
        )

        # Very small exponent (large negative)
        small_exp = FlexFloat.from_float(-1000.0)
        result = ffmath.pow(base, small_exp)
        self.assertFalse(result.is_zero(), "Should not be exactly zero")
        self.assertTrue(result.to_float() < 1e-100, "Should be very small")

    def test_pow_with_extreme_integers(self):
        """Test pow using extreme integer bases."""
        # Test powers where the result would normally overflow
        base = FlexFloat.from_int(10)
        exp = FlexFloat.from_int(100)
        result = ffmath.pow(base, exp)

        # This should equal our extreme FlexFloat from_int(10^100)
        expected = FlexFloat.from_int(10**100)
        self.assertAlmostEqualRel(
            result.to_float(), expected.to_float(), tolerance=1e-10
        )

        # Test fractional exponents with large bases
        large_base = FlexFloat.from_int(10**50)
        fractional_exp = FlexFloat.from_float(0.5)  # Square root
        result = ffmath.pow(large_base, fractional_exp)

        # Should equal sqrt(10^50) = 10^25
        expected = FlexFloat.from_int(10**25)
        self.assertAlmostEqualRel(
            result.to_float(), expected.to_float(), tolerance=1e-8
        )

    def test_pow_with_extreme_bases(self):
        """Test pow function with extreme bases and reasonable exponents."""
        reasonable_exponents = [
            FlexFloat.from_float(0.5),  # Square root
            FlexFloat.from_float(2.0),  # Square
            FlexFloat.from_float(0.1),  # Small fractional
        ]

        zero = FlexFloat.from_int(0)
        one = FlexFloat.from_int(1)

        for extreme_val in self.extreme_flexfloats:
            if extreme_val <= zero:
                continue  # Skip negative bases for fractional exponents

            for exp_val in reasonable_exponents:
                pow_result = ffmath.pow(extreme_val, exp_val)

                # Basic sanity checks
                self.assertFalse(
                    pow_result.is_nan(),
                    "pow(extreme_base, reasonable_exp) should not be NaN",
                )

                # For positive bases, result should be positive
                self.assertTrue(
                    pow_result > zero, "pow(positive_base, exp) should be positive"
                )

                # For square root, result should be less than base if base > 1
                if exp_val < one and extreme_val > one:
                    self.assertTrue(
                        pow_result < extreme_val,
                        "pow(base > 1, exp < 1) should be less than base",
                    )
                # For square, result should be greater than base if base > 1
                elif exp_val > one and extreme_val > one:
                    self.assertTrue(
                        pow_result > extreme_val,
                        "pow(base > 1, exp > 1) should be greater than base",
                    )

    def test_function_composition(self):
        """Test composing multiple math functions."""
        # Test exp(log(x)) = x for positive x
        for val in [0.1, 1.0, 2.0, 10.0, 100.0]:
            x = FlexFloat.from_float(val)
            result = ffmath.exp(ffmath.log(x))
            self.assertAlmostEqualRel(result.to_float(), val)

        # Test log(exp(x)) = x for reasonable x
        for val in [0.0, 0.1, 1.0, 2.0, 5.0]:
            x = FlexFloat.from_float(val)
            result = ffmath.log(ffmath.exp(x))
            self.assertAlmostEqualRel(result.to_float(), val)

        # Test sqrt(x^2) = |x|
        for val in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            x = FlexFloat.from_float(val)
            result = ffmath.sqrt(x * x)
            expected = abs(val)
            self.assertAlmostEqualRel(result.to_float(), expected)


if __name__ == "__main__":
    unittest.main()
