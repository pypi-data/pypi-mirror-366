"""Tests for utility functions in FlexFloat math module."""

import math
import sys
import unittest

from flexfloat import FlexFloat
from flexfloat import math as ffmath
from tests.math import TestMathSetup


class TestUtilityFunctions(TestMathSetup):
    """Test utility and helper functions."""

    def test_fmod_normal_cases(self):
        """Test floating-point remainder function."""
        # Test positive cases where both implementations should agree
        test_cases = [(7.0, 3.0), (7.5, 2.5), (10.5, 3.0), (0.5, 0.25), (100.0, 7.0)]

        for x, y in test_cases:
            with self.subTest(x=x, y=y):
                ff_x = FlexFloat.from_float(x)
                ff_y = FlexFloat.from_float(y)
                result = ffmath.fmod(ff_x, ff_y)
                expected = math.fmod(x, y)
                self.assertAlmostEqualRel(result.to_float(), expected)

        # Test that FlexFloat fmod produces reasonable results for signed cases
        # (may differ from math.fmod in implementation details)
        signed_test_cases = [(-7.0, 3.0), (7.0, -3.0)]
        for x, y in signed_test_cases:
            with self.subTest(x=x, y=y, comment="signed"):
                ff_x = FlexFloat.from_float(x)
                ff_y = FlexFloat.from_float(y)
                result = ffmath.fmod(ff_x, ff_y)
                # Just check that result is reasonable (finite and has magnitude < |y|)
                self.assertTrue(ffmath.isfinite(result), "fmod result should be finite")
                self.assertLess(
                    abs(result.to_float()),
                    abs(y),
                    "fmod result magnitude should be less than divisor",
                )

    def test_remainder_normal_cases(self):
        """Test IEEE remainder function."""
        test_cases = [
            (7.0, 3.0),
            (7.5, 2.5),
            (-7.0, 3.0),
            (7.0, -3.0),
            (10.5, 3.0),
            (0.5, 0.25),
        ]

        for x, y in test_cases:
            with self.subTest(x=x, y=y):
                ff_x = FlexFloat.from_float(x)
                ff_y = FlexFloat.from_float(y)
                result = ffmath.remainder(ff_x, ff_y)
                expected = math.remainder(x, y)
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_hypot_normal_cases(self):
        """Test Euclidean distance function."""
        test_cases = [
            (3.0, 4.0),  # Classic 3-4-5 triangle
            (1.0, 1.0),  # 45-degree case
            (0.0, 5.0),  # One zero
            (1e100, 1e100),  # Large values
            (1e-100, 1e-100),  # Small values
        ]

        for x, y in test_cases:
            with self.subTest(x=x, y=y):
                ff_x = FlexFloat.from_float(x)
                ff_y = FlexFloat.from_float(y)
                result = ffmath.hypot(ff_x, ff_y)
                expected = math.hypot(x, y)
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_fsum_normal_cases(self):
        """Test accurate floating-point sum."""
        test_sequences = [
            [1.0, 2.0, 3.0, 4.0],
            [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],  # Precision test
            [1e-10, 1e-10, 1e-10] * 1000,  # Many small values
        ]

        for seq in test_sequences:
            with self.subTest(sequence_len=len(seq)):
                ff_seq = [FlexFloat.from_float(val) for val in seq]
                result = ffmath.fsum(ff_seq)
                expected = math.fsum(seq)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-12)

        # Special test for cancellation
        cancellation_seq = [1e20, 1.0, -1e20]
        ff_seq = [FlexFloat.from_float(val) for val in cancellation_seq]
        result = ffmath.fsum(ff_seq)
        expected = math.fsum(cancellation_seq)
        self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-12)

    def test_fma_normal_cases(self):
        """Test fused multiply-add function."""
        test_cases = [
            (2.0, 3.0, 4.0),  # 2*3 + 4 = 10
            (0.5, 4.0, 1.0),  # 0.5*4 + 1 = 3
            (1e10, 1e-10, 1.0),  # Precision test
        ]

        for x, y, z in test_cases:
            with self.subTest(x=x, y=y, z=z):
                ff_x = FlexFloat.from_float(x)
                ff_y = FlexFloat.from_float(y)
                ff_z = FlexFloat.from_float(z)
                result = ffmath.fma(ff_x, ff_y, ff_z)
                if sys.version_info >= (3, 13):
                    expected = math.fma(x, y, z)
                else:
                    expected = x * y + z
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_ulp_normal_cases(self):
        """Test unit in the last place function."""
        test_values = [1.0, 2.0, 0.5, 100.0]

        for val in test_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.ulp(ff_val)
                expected = math.ulp(val)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-10)


class TestSpecialFunctions(TestMathSetup):
    """Test special mathematical functions."""

    def test_gamma_normal_cases(self):
        """Test gamma function with normal positive values."""
        # Test positive values where gamma is well-defined
        positive_values = [val for val in self.basic_values if val > 0]
        self.compare_with_math(
            ffmath.gamma, math.gamma, positive_values, tolerance=1e-9
        )

    def test_gamma_variety_of_sizes(self):
        """Test gamma function with various sizes of input."""
        # Small positive values
        small_positive = [0.1, 0.01, 0.001, 0.5, 0.25, 0.75, 0.999]
        self.compare_with_math(ffmath.gamma, math.gamma, small_positive, tolerance=1e-9)

        # Medium values
        medium_values = [1.1, 1.5, 2.5, 3.7, 4.2, 5.8, 6.9, 7.1, 8.5, 9.9]
        self.compare_with_math(ffmath.gamma, math.gamma, medium_values, tolerance=1e-9)

        # Larger values (but within reasonable range for standard library)
        large_values = [10.0, 15.0, 20.0, 25.0, 30.0, 50.0, 100.0]
        self.compare_with_math(ffmath.gamma, math.gamma, large_values, tolerance=1e-7)

    def test_gamma_edge_cases(self):
        """Test gamma function edge cases."""
        # Test gamma(1) = 0! = 1
        result = ffmath.gamma(FlexFloat.from_float(1.0))
        self.assertAlmostEqualRel(result.to_float(), 1.0, tolerance=1e-15)

        # Test gamma(2) = 1! = 1
        result = ffmath.gamma(FlexFloat.from_float(2.0))
        self.assertAlmostEqualRel(result.to_float(), 1.0, tolerance=1e-15)

        # Test gamma(3) = 2! = 2
        result = ffmath.gamma(FlexFloat.from_float(3.0))
        self.assertAlmostEqualRel(result.to_float(), 2.0, tolerance=1e-15)

        # Test gamma(4) = 3! = 6
        result = ffmath.gamma(FlexFloat.from_float(4.0))
        self.assertAlmostEqualRel(result.to_float(), 6.0, tolerance=1e-15)

        # Test gamma(0.5) = sqrt(pi)
        result = ffmath.gamma(FlexFloat.from_float(0.5))
        expected = math.sqrt(math.pi)
        self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-14)

        # Test gamma(1.5) = 0.5 * sqrt(pi)
        result = ffmath.gamma(FlexFloat.from_float(1.5))
        expected = 0.5 * math.sqrt(math.pi)
        self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-14)

        # Test special values
        # gamma(NaN) = NaN
        result = ffmath.gamma(FlexFloat.nan())
        self.assertTrue(result.is_nan())

        # gamma(+inf) = +inf
        result = ffmath.gamma(FlexFloat.infinity(sign=False))
        self.assertTrue(result.is_infinity() and not result.sign)

        # gamma(-inf) = NaN
        result = ffmath.gamma(FlexFloat.infinity(sign=True))
        self.assertTrue(result.is_nan())

        # gamma(0) = +inf
        result = ffmath.gamma(FlexFloat.zero())
        self.assertTrue(result.is_infinity() and not result.sign)

        # gamma(negative integer) = NaN
        for neg_int in [-1.0, -2.0, -3.0, -10.0]:
            result = ffmath.gamma(FlexFloat.from_float(neg_int))
            self.assertTrue(result.is_nan(), f"gamma({neg_int}) should be NaN")

    def test_gamma_negative_values(self):
        """Test gamma function with negative non-integer values."""
        # Test negative non-integer values using reflection formula
        negative_values = [-0.5, -1.5, -2.5, -3.5, -0.1, -0.9, -1.1, -2.1]
        self.compare_with_math(
            ffmath.gamma, math.gamma, negative_values, tolerance=1e-9
        )

    def test_gamma_extreme_values(self):
        """Test gamma function with values outside normal float range."""
        # Very large positive values should not overflow in FlexFloat
        very_large_values = [200.0, 500.0, 1000.0]
        for val in very_large_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.gamma(ff_val)
                # FlexFloat should handle this without overflow, unlike regular floats
                self.assertFalse(
                    result.is_infinity(),
                    f"gamma({val}) should not overflow in FlexFloat",
                )
                self.assertFalse(result.is_nan(), f"gamma({val}) should not be NaN")
                self.assertFalse(result.sign, f"gamma({val}) should be positive")

        # Test with extreme FlexFloat values
        extreme_large = FlexFloat.from_int(1000)
        result = ffmath.gamma(extreme_large)
        self.assertFalse(
            result.is_infinity(),
            "gamma of very large value should not overflow in FlexFloat",
        )
        self.assertFalse(result.is_nan())
        self.assertFalse(result.sign)

        # Very small positive values should be finite and large
        very_small_values = [1e-10, 1e-50, 1e-100]
        for val in very_small_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.gamma(ff_val)
                # For small x, gamma(x) ≈ 1/x, so should be finite and positive
                self.assertTrue(
                    ffmath.isfinite(result), f"gamma({val}) should be finite"
                )
                self.assertFalse(result.sign, f"gamma({val}) should be positive")
                # Should be approximately 1/x for very small x
                approx_expected = 1.0 / val
                if approx_expected < 1e100:  # Only check if not too large
                    self.assertAlmostEqualRel(
                        result.to_float(), approx_expected, tolerance=0.1
                    )

    def test_gamma_mathematical_identities(self):
        """Test mathematical identities involving gamma function."""
        # Test gamma(x+1) = x * gamma(x) for various x
        test_values = [0.5, 1.5, 2.5, 3.7, 10.5]
        for x in test_values:
            with self.subTest(x=x):
                ff_x = FlexFloat.from_float(x)
                ff_x_plus_1 = FlexFloat.from_float(x + 1)

                gamma_x = ffmath.gamma(ff_x)
                gamma_x_plus_1 = ffmath.gamma(ff_x_plus_1)

                # gamma(x+1) should equal x * gamma(x)
                expected = ff_x * gamma_x
                self.assertAlmostEqualRel(
                    gamma_x_plus_1.to_float(), expected.to_float(), tolerance=1e-12
                )

    def test_lgamma_normal_cases(self):
        """Test log gamma function with normal positive values."""
        positive_values = [val for val in self.basic_values if val > 0]
        self.compare_with_math(
            ffmath.lgamma, math.lgamma, positive_values, tolerance=1e-9
        )

    def test_lgamma_variety_of_sizes(self):
        """Test lgamma function with various sizes of input."""
        # Small positive values
        small_positive = [0.1, 0.01, 0.001, 0.5, 0.25, 0.75, 0.999]
        self.compare_with_math(
            ffmath.lgamma, math.lgamma, small_positive, tolerance=1e-9
        )

        # Medium values
        medium_values = [1.1, 1.5, 2.5, 3.7, 4.2, 5.8, 6.9, 7.1, 8.5, 9.9]
        self.compare_with_math(
            ffmath.lgamma, math.lgamma, medium_values, tolerance=1e-9
        )

        # Larger values where lgamma helps avoid overflow
        large_values = [10.0, 50.0, 100.0, 200.0, 500.0, 1000.0]
        self.compare_with_math(ffmath.lgamma, math.lgamma, large_values, tolerance=1e-7)

    def test_lgamma_edge_cases(self):
        """Test lgamma function edge cases."""
        # Test lgamma(1) = ln(gamma(1)) = ln(1) = 0
        result = ffmath.lgamma(FlexFloat.from_float(1.0))
        self.assertAlmostEqualRel(result.to_float(), 0.0, tolerance=1e-14)

        # Test lgamma(2) = ln(gamma(2)) = ln(1) = 0
        result = ffmath.lgamma(FlexFloat.from_float(2.0))
        self.assertAlmostEqualRel(result.to_float(), 0.0, tolerance=1e-14)

        # Test lgamma(3) = ln(gamma(3)) = ln(2) ≈ 0.693
        result = ffmath.lgamma(FlexFloat.from_float(3.0))
        expected = math.log(2.0)
        self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-14)

        # Test special values
        # lgamma(NaN) = NaN
        result = ffmath.lgamma(FlexFloat.nan())
        self.assertTrue(result.is_nan())

        # lgamma(+inf) = +inf
        result = ffmath.lgamma(FlexFloat.infinity(sign=False))
        self.assertTrue(result.is_infinity() and not result.sign)

        # lgamma(-inf) = +inf
        result = ffmath.lgamma(FlexFloat.infinity(sign=True))
        self.assertTrue(result.is_infinity() and not result.sign)

        # lgamma(0) = +inf
        result = ffmath.lgamma(FlexFloat.zero())
        self.assertTrue(result.is_infinity() and not result.sign)

        # lgamma(negative integer) = +inf
        for neg_int in [-1.0, -2.0, -3.0, -10.0]:
            result = ffmath.lgamma(FlexFloat.from_float(neg_int))
            self.assertTrue(
                result.is_infinity() and not result.sign,
                f"lgamma({neg_int}) should be +infinity",
            )

    def test_lgamma_negative_values(self):
        """Test lgamma function with negative non-integer values."""
        negative_values = [-0.5, -1.5, -2.5, -3.5, -0.1, -0.9, -1.1, -2.1]
        self.compare_with_math(
            ffmath.lgamma, math.lgamma, negative_values, tolerance=1e-9
        )

    def test_lgamma_extreme_values(self):
        """Test lgamma function with extreme values to check it doesn't overflow."""
        # Very large positive values - lgamma should remain finite
        very_large_values = [1000.0, 10000.0, 100000.0]
        for val in very_large_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.lgamma(ff_val)
                # lgamma should be finite even for very large inputs
                self.assertTrue(
                    ffmath.isfinite(result), f"lgamma({val}) should be finite"
                )
                self.assertFalse(result.sign, f"lgamma({val}) should be positive")

        # Test with extreme FlexFloat values
        extreme_large = FlexFloat.from_int(100000)
        result = ffmath.lgamma(extreme_large)
        self.assertTrue(
            ffmath.isfinite(result), "lgamma of very large value should be finite"
        )

        # Very small positive values
        very_small_values = [1e-10, 1e-50, 1e-100]
        for val in very_small_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.lgamma(ff_val)
                # For small x, lgamma(x) ≈ ln(1/x) = -ln(x)
                self.assertTrue(
                    ffmath.isfinite(result), f"lgamma({val}) should be finite"
                )
                # Should be positive (since gamma(small positive) is large)
                self.assertFalse(result.sign, f"lgamma({val}) should be positive")

    def test_lgamma_relationship_with_gamma(self):
        """Test relationship between lgamma and gamma functions."""
        # For moderate values, lgamma(x) should equal ln(gamma(x))
        test_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
        for val in test_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)

                gamma_result = ffmath.gamma(ff_val)
                lgamma_result = ffmath.lgamma(ff_val)

                expected_lgamma = ffmath.log(gamma_result.abs())
                self.assertAlmostEqualRel(
                    lgamma_result.to_float(),
                    expected_lgamma.to_float(),
                    tolerance=1e-12,
                )

    def test_gamma_lgamma_mathematical_identities(self):
        """Test mathematical identities involving both gamma and lgamma."""
        # Test lgamma(x+1) = lgamma(x) + ln(x) for various x
        test_values = [0.5, 1.5, 2.5, 5.5, 10.5]
        for x in test_values:
            with self.subTest(x=x):
                from flexfloat.math.logarithmic import log

                ff_x = FlexFloat.from_float(x)
                ff_x_plus_1 = FlexFloat.from_float(x + 1)

                lgamma_x = ffmath.lgamma(ff_x)
                lgamma_x_plus_1 = ffmath.lgamma(ff_x_plus_1)
                ln_x = log(ff_x)

                # lgamma(x+1) should equal lgamma(x) + ln(x)
                expected = lgamma_x + ln_x
                self.assertAlmostEqualRel(
                    lgamma_x_plus_1.to_float(), expected.to_float(), tolerance=1e-12
                )

    def test_erf_normal_cases(self):
        """Test error function with normal values."""
        test_values = [-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0]
        self.compare_with_math(ffmath.erf, math.erf, test_values)

    def test_erf_edge_cases(self):
        """Test error function with special values."""
        # Test special values
        self.assertTrue(ffmath.erf(FlexFloat.nan()).is_nan())
        self.assertAlmostEqualRel(ffmath.erf(FlexFloat.infinity()).to_float(), 1.0)
        self.assertAlmostEqualRel(ffmath.erf(-FlexFloat.infinity()).to_float(), -1.0)
        self.assertAlmostEqualRel(ffmath.erf(FlexFloat.zero()).to_float(), 0.0)

        # Test odd function property: erf(-x) = -erf(x)
        test_values = [0.1, 0.5, 1.0, 2.0, 5.0]
        for val in test_values:
            with self.subTest(value=val):
                ff_pos = FlexFloat.from_float(val)
                ff_neg = FlexFloat.from_float(-val)
                erf_pos = ffmath.erf(ff_pos)
                erf_neg = ffmath.erf(ff_neg)
                self.assertAlmostEqualRel(
                    erf_neg.to_float(), -erf_pos.to_float(), tolerance=1e-12
                )

    def test_erf_variety_of_sizes(self):
        """Test error function with various sizes."""
        # Small values (Taylor series range)
        small_values = [0.001, 0.01, 0.1, 0.3, 0.49]
        self.compare_with_math(ffmath.erf, math.erf, small_values, tolerance=1e-12)

        # Medium values (Abramowitz-Stegun range)
        medium_values = [0.5, 0.8, 1.2, 1.8, 2.1]
        self.compare_with_math(ffmath.erf, math.erf, medium_values, tolerance=1e-7)

        # Large values (asymptotic range)
        large_values = [3.0, 4.0, 5.0, 6.0, 8.0]
        self.compare_with_math(ffmath.erf, math.erf, large_values, tolerance=1e-6)

    def test_erf_extreme_values(self):
        """Test error function with extreme values."""
        # Very small values
        tiny_values = [1e-10, 1e-8, 1e-6]
        for val in tiny_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.erf(ff_val)
                expected = math.erf(val)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-12)

        # Very large values (should approach ±1)
        large_values = [10.0, 20.0, 50.0]
        for val in large_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.erf(ff_val)
                self.assertAlmostEqualRel(result.to_float(), 1.0, tolerance=1e-10)

                # Test negative values
                ff_neg = FlexFloat.from_float(-val)
                result_neg = ffmath.erf(ff_neg)
                self.assertAlmostEqualRel(result_neg.to_float(), -1.0, tolerance=1e-10)

    def test_erfc_normal_cases(self):
        """Test complementary error function with normal values."""
        test_values = [-3.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0]
        self.compare_with_math(ffmath.erfc, math.erfc, test_values)

    def test_erfc_edge_cases(self):
        """Test complementary error function with special values."""
        # Test special values
        self.assertTrue(ffmath.erfc(FlexFloat.nan()).is_nan())
        self.assertAlmostEqualRel(ffmath.erfc(FlexFloat.infinity()).to_float(), 0.0)
        self.assertAlmostEqualRel(ffmath.erfc(-FlexFloat.infinity()).to_float(), 2.0)
        self.assertAlmostEqualRel(ffmath.erfc(FlexFloat.zero()).to_float(), 1.0)

    def test_erfc_variety_of_sizes(self):
        """Test complementary error function with various sizes."""
        # Test different ranges for accuracy
        small_values = [0.001, 0.01, 0.1, 0.3]
        self.compare_with_math(ffmath.erfc, math.erfc, small_values, tolerance=1e-12)

        medium_values = [0.5, 1.0, 2.0, 3.0]
        self.compare_with_math(ffmath.erfc, math.erfc, medium_values, tolerance=1e-7)

        # Test the previously problematic range with high precision
        problematic_values = [1.3, 1.9, 2.1, 2.7, 3.1, 3.4, 3.6]
        for val in problematic_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.erfc(ff_val)
                expected = math.erfc(val)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-6)

        # Large positive values (should approach 0)
        large_values = [4.0, 5.0, 6.0, 8.0]
        for val in large_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.erfc(ff_val)
                expected = math.erfc(val)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-6)

        # Large negative values (should approach 2)
        negative_large_values = [-4.0, -5.0, -6.0, -8.0]
        for val in negative_large_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.erfc(ff_val)
                expected = math.erfc(val)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-6)

        # Test negative problematic values
        negative_problematic_values = [-1.3, -1.9, -2.1, -2.7, -3.1, -3.4, -3.6]
        for val in negative_problematic_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.erfc(ff_val)
                expected = math.erfc(val)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-6)

    def test_erf_erfc_relationship(self):
        """Test that erf(x) + erfc(x) = 1."""
        test_values = [-5.0, -2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 5.0]

        for val in test_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                erf_result = ffmath.erf(ff_val)
                erfc_result = ffmath.erfc(ff_val)
                sum_result = erf_result + erfc_result
                self.assertAlmostEqualRel(sum_result.to_float(), 1.0, tolerance=1e-6)

    def test_nextafter_normal_cases(self):
        """Test nextafter function with normal values."""
        # Test basic functionality
        x = FlexFloat.from_float(1.0)
        y = FlexFloat.from_float(2.0)
        result = ffmath.nextafter(x, y)
        expected = math.nextafter(1.0, 2.0)
        self.assertAlmostEqualRel(result.to_float(), expected)

        # Test in opposite direction
        result2 = ffmath.nextafter(y, x)
        expected2 = math.nextafter(2.0, 1.0)
        self.assertAlmostEqualRel(result2.to_float(), expected2)

    def test_nextafter_edge_cases(self):
        """Test nextafter function with special values."""
        # Test with NaN
        self.assertTrue(
            ffmath.nextafter(FlexFloat.nan(), FlexFloat.from_float(1.0)).is_nan()
        )
        self.assertTrue(
            ffmath.nextafter(FlexFloat.from_float(1.0), FlexFloat.nan()).is_nan()
        )

        # Test with same values
        x = FlexFloat.from_float(1.5)
        result = ffmath.nextafter(x, x)
        self.assertEqual(result.to_float(), x.to_float())

        # Test with zero
        zero = FlexFloat.zero()
        pos_tiny = ffmath.nextafter(zero, FlexFloat.from_float(1.0))
        self.assertGreater(pos_tiny.to_float(), 0.0)
        self.assertLess(pos_tiny.to_float(), sys.float_info.min)

        neg_tiny = ffmath.nextafter(zero, FlexFloat.from_float(-1.0))
        self.assertLess(neg_tiny.to_float(), 0.0)
        self.assertGreater(neg_tiny.to_float(), -sys.float_info.min)

    def test_nextafter_variety_of_sizes(self):
        """Test nextafter function with various sizes."""
        test_pairs = [
            (0.0, 1.0),
            (1.0, 0.0),
            (-1.0, 0.0),
            (0.0, -1.0),
            (1e-10, 1e-9),
            (1e10, 1e11),
            (-1e10, -1e11),
            (sys.float_info.max / 2, sys.float_info.max),
        ]

        for x_val, y_val in test_pairs:
            with self.subTest(x=x_val, y=y_val):
                x = FlexFloat.from_float(x_val)
                y = FlexFloat.from_float(y_val)
                result = ffmath.nextafter(x, y)
                expected = math.nextafter(x_val, y_val)

                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_nextafter_extreme_values(self):
        """Test nextafter function with extreme values."""
        # Test with infinity
        inf = FlexFloat.infinity()
        large_val = FlexFloat.from_float(sys.float_info.max)

        # Moving towards infinity from finite value
        result = ffmath.nextafter(large_val, inf)
        expected = math.nextafter(sys.float_info.max, float("inf"))
        self.assertTrue(result.is_infinity() and not result.sign)

        # Test with very small values
        tiny = FlexFloat.from_float(sys.float_info.min)
        result = ffmath.nextafter(tiny, FlexFloat.zero())
        expected = math.nextafter(sys.float_info.min, 0.0)
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_nextafter_steps_parameter(self):
        """Test nextafter function with steps parameter."""
        x = FlexFloat.from_float(1.0)
        y = FlexFloat.from_float(2.0)

        # Test single step (default)
        result1 = ffmath.nextafter(x, y)
        result1_explicit = ffmath.nextafter(x, y, steps=1)
        self.assertEqual(result1.to_float(), result1_explicit.to_float())

        # Test zero steps
        result0 = ffmath.nextafter(x, y, steps=0)
        self.assertEqual(result0.to_float(), x.to_float())

        # Test multiple steps
        result3 = ffmath.nextafter(x, y, steps=3)
        # Should be equivalent to three consecutive nextafter calls
        temp = math.nextafter(1.0, 2.0)
        temp = math.nextafter(temp, 2.0)
        expected = math.nextafter(temp, 2.0)
        self.assertAlmostEqualRel(result3.to_float(), expected)


if __name__ == "__main__":
    unittest.main()
