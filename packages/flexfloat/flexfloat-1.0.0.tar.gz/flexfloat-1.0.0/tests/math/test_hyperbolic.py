"""Tests for hyperbolic functions in FlexFloat math module."""

import math
import unittest

from flexfloat import FlexFloat
from flexfloat import math as ffmath
from tests.math import TestMathSetup


class TestHyperbolicFunctions(TestMathSetup):
    """Test hyperbolic functions."""

    def test_sinh_normal_cases(self):
        """Test hyperbolic sine function with comprehensive normal values."""
        normal_values = [
            -5.0,
            -3.0,
            -2.0,
            -1.0,
            -0.5,
            -0.1,
            0.0,
            0.1,
            0.5,
            1.0,
            2.0,
            3.0,
            5.0,
        ]
        self.compare_with_math(ffmath.sinh, math.sinh, normal_values)

    def test_sinh_variety_of_sizes(self):
        """Test sinh with various magnitude values."""
        small_values = [1e-10, -1e-10, 1e-15, -1e-15]
        medium_values = self.basic_values
        # Large values but not too large to avoid overflow in standard math
        large_values = [10.0, -10.0, 20.0, -20.0]

        all_values = small_values + medium_values + large_values
        self.compare_with_math(ffmath.sinh, math.sinh, all_values, tolerance=1e-12)

    def test_sinh_edge_cases(self):
        """Test sinh function with edge cases."""
        # Test zero
        self.assertAlmostEqualRel(
            ffmath.sinh(FlexFloat.from_float(0.0)).to_float(), 0.0
        )

        # Test infinities
        self.assertTrue(ffmath.sinh(FlexFloat.infinity(sign=False)).is_infinity())
        self.assertFalse(ffmath.sinh(FlexFloat.infinity(sign=False)).sign)
        self.assertTrue(ffmath.sinh(FlexFloat.infinity(sign=True)).is_infinity())
        self.assertTrue(ffmath.sinh(FlexFloat.infinity(sign=True)).sign)

        # Test NaN
        self.assertTrue(ffmath.sinh(FlexFloat.nan()).is_nan())

    def test_sinh_extreme_values(self):
        """Test sinh with values outside normal float range."""
        # Large positive values - should grow exponentially but not overflow
        large_positive = [50.0, 100.0, 200.0]

        for val in large_positive:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.sinh(ff_val)
                self.assertFalse(
                    result.is_infinity(), f"sinh({val}) should not overflow to infinity"
                )
                self.assertTrue(
                    result > FlexFloat.from_float(1e20),
                    f"sinh({val}) should be very large",
                )

        # Large negative values - should be large negative
        large_negative = [-50.0, -100.0, -200.0]

        for val in large_negative:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.sinh(ff_val)
                self.assertFalse(result.is_infinity())
                self.assertTrue(result < FlexFloat.from_float(-1e20))

    def test_cosh_normal_cases(self):
        """Test hyperbolic cosine function with comprehensive normal values."""
        normal_values = [
            -5.0,
            -3.0,
            -2.0,
            -1.0,
            -0.5,
            -0.1,
            0.0,
            0.1,
            0.5,
            1.0,
            2.0,
            3.0,
            5.0,
        ]
        self.compare_with_math(ffmath.cosh, math.cosh, normal_values)

    def test_cosh_edge_cases(self):
        """Test cosh function with edge cases."""
        # Test zero - cosh(0) = 1
        self.assertAlmostEqualRel(
            ffmath.cosh(FlexFloat.from_float(0.0)).to_float(), 1.0
        )

        # Test infinities - cosh(±∞) = +∞
        self.assertTrue(ffmath.cosh(FlexFloat.infinity(sign=False)).is_infinity())
        self.assertFalse(ffmath.cosh(FlexFloat.infinity(sign=False)).sign)
        self.assertTrue(ffmath.cosh(FlexFloat.infinity(sign=True)).is_infinity())
        self.assertFalse(ffmath.cosh(FlexFloat.infinity(sign=True)).sign)

        # Test NaN
        self.assertTrue(ffmath.cosh(FlexFloat.nan()).is_nan())

    def test_tanh_normal_cases(self):
        """Test hyperbolic tangent function with comprehensive normal values."""
        normal_values = [
            -10.0,
            -5.0,
            -3.0,
            -2.0,
            -1.0,
            -0.5,
            -0.1,
            0.0,
            0.1,
            0.5,
            1.0,
            2.0,
            3.0,
            5.0,
            10.0,
        ]
        self.compare_with_math(ffmath.tanh, math.tanh, normal_values)

    def test_tanh_edge_cases(self):
        """Test tanh function with edge cases."""
        # Test zero
        self.assertAlmostEqualRel(
            ffmath.tanh(FlexFloat.from_float(0.0)).to_float(), 0.0
        )

        # Test asymptotic behavior
        self.assertAlmostEqualRel(
            ffmath.tanh(FlexFloat.infinity(sign=False)).to_float(), 1.0, tolerance=1e-14
        )
        self.assertAlmostEqualRel(
            ffmath.tanh(FlexFloat.infinity(sign=True)).to_float(), -1.0, tolerance=1e-14
        )

        # Test NaN
        self.assertTrue(ffmath.tanh(FlexFloat.nan()).is_nan())

    def test_tanh_extreme_values(self):
        """Test tanh with extreme values - should be bounded to [-1, 1]."""
        extreme_values = [100.0, -100.0, 1000.0, -1000.0, 1e10, -1e10]

        for val in extreme_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.tanh(ff_val)
                self.assertFalse(result.is_nan())
                self.assertFalse(result.is_infinity())
                # tanh should be bounded to [-1, 1] and approach ±1 for large |x|
                self.assertTrue(result.abs() <= FlexFloat.from_float(1.0))
                expected_sign = 1.0 if val > 0 else -1.0
                self.assertTrue(abs(result.to_float() - expected_sign) < 1e-10)


class TestInverseHyperbolicFunctions(TestMathSetup):
    """Test inverse hyperbolic functions."""

    def test_asinh_normal_cases(self):
        """Test inverse hyperbolic sine with comprehensive values."""
        # asinh has domain (-∞, ∞)
        normal_values = [
            -100.0,
            -10.0,
            -5.0,
            -2.0,
            -1.0,
            -0.5,
            -0.1,
            0.0,
            0.1,
            0.5,
            1.0,
            2.0,
            5.0,
            10.0,
            100.0,
        ]
        self.compare_with_math(ffmath.asinh, math.asinh, normal_values)

    def test_asinh_edge_cases(self):
        """Test asinh with edge cases."""
        # Test zero
        self.assertAlmostEqualRel(
            ffmath.asinh(FlexFloat.from_float(0.0)).to_float(), 0.0
        )

        # Test infinities
        self.assertTrue(ffmath.asinh(FlexFloat.infinity(sign=False)).is_infinity())
        self.assertFalse(ffmath.asinh(FlexFloat.infinity(sign=False)).sign)
        self.assertTrue(ffmath.asinh(FlexFloat.infinity(sign=True)).is_infinity())
        self.assertTrue(ffmath.asinh(FlexFloat.infinity(sign=True)).sign)

        # Test NaN
        self.assertTrue(ffmath.asinh(FlexFloat.nan()).is_nan())

    def test_acosh_normal_cases(self):
        """Test inverse hyperbolic cosine with valid domain values."""
        # acosh has domain [1, ∞)
        valid_values = [1.0, 1.1, 1.5, 2.0, 3.0, 5.0, 10.0, 50.0, 100.0]
        self.compare_with_math(ffmath.acosh, math.acosh, valid_values)

    def test_acosh_edge_cases(self):
        """Test acosh with edge cases."""
        # Test boundary at x = 1
        self.assertAlmostEqualRel(
            ffmath.acosh(FlexFloat.from_float(1.0)).to_float(), 0.0
        )

        # Test positive infinity
        self.assertTrue(ffmath.acosh(FlexFloat.infinity(sign=False)).is_infinity())
        self.assertFalse(ffmath.acosh(FlexFloat.infinity(sign=False)).sign)

        # Test domain violations (x < 1)
        invalid_values = [0.5, 0.0, -1.0, -10.0]
        for val in invalid_values:
            with self.subTest(value=val):
                result = ffmath.acosh(FlexFloat.from_float(val))
                self.assertTrue(result.is_nan(), f"acosh({val}) should return NaN")

        # Test NaN
        self.assertTrue(ffmath.acosh(FlexFloat.nan()).is_nan())

    def test_atanh_normal_cases(self):
        """Test inverse hyperbolic tangent with valid domain values."""
        # atanh has domain (-1, 1)
        valid_values = [-0.99, -0.9, -0.5, -0.1, 0.0, 0.1, 0.5, 0.9, 0.99]
        self.compare_with_math(ffmath.atanh, math.atanh, valid_values)

    def test_atanh_edge_cases(self):
        """Test atanh with edge cases."""
        # Test zero
        self.assertAlmostEqualRel(
            ffmath.atanh(FlexFloat.from_float(0.0)).to_float(), 0.0
        )

        # Test domain violations (|x| >= 1)
        invalid_values = [1.0, -1.0, 1.1, -1.1, 2.0, -2.0]
        for val in invalid_values:
            with self.subTest(value=val):
                result = ffmath.atanh(FlexFloat.from_float(val))
                self.assertTrue(result.is_nan(), f"atanh({val}) should return NaN")

        # Test NaN
        self.assertTrue(ffmath.atanh(FlexFloat.nan()).is_nan())

    def test_atanh_near_boundaries(self):
        """Test atanh behavior very close to domain boundaries."""
        near_boundary_values = [0.9999, -0.9999, 0.99999, -0.99999]

        for val in near_boundary_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.atanh(ff_val)
                expected = math.atanh(val)
                # Should be finite but very large
                self.assertFalse(result.is_infinity())
                self.assertFalse(result.is_nan())
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-10)


class TestHyperbolicIdentities(TestMathSetup):
    """Test hyperbolic function identities and relationships."""

    def test_hyperbolic_identities(self):
        """Test hyperbolic function identities."""
        test_values = [0.1, 0.5, 1.0, 2.0, 3.0]

        for x in test_values:
            with self.subTest(x=x):
                fx = FlexFloat.from_float(x)

                # Fundamental hyperbolic identity: cosh²(x) - sinh²(x) = 1
                sinh_x = ffmath.sinh(fx)
                cosh_x = ffmath.cosh(fx)
                identity = cosh_x * cosh_x - sinh_x * sinh_x
                self.assertAlmostEqualRel(identity.to_float(), 1.0, tolerance=1e-13)

                # tanh(x) = sinh(x) / cosh(x)
                tanh_x = ffmath.tanh(fx)
                tanh_from_def = sinh_x / cosh_x
                self.assertAlmostEqualRel(
                    tanh_x.to_float(), tanh_from_def.to_float(), tolerance=1e-14
                )

    def test_inverse_function_relationships(self):
        """Test relationships between hyperbolic functions and their inverses."""
        # Test asinh(sinh(x)) = x
        test_values = [-3.0, -1.0, -0.5, 0.0, 0.5, 1.0, 3.0]

        for x in test_values:
            with self.subTest(function="asinh(sinh(x))", x=x):
                fx = FlexFloat.from_float(x)
                result = ffmath.asinh(ffmath.sinh(fx))
                self.assertAlmostEqualRel(result.to_float(), x, tolerance=1e-12)

        # Test acosh(cosh(x)) = |x| for x >= 0
        test_positive_values = [0.0, 0.5, 1.0, 2.0, 3.0]

        for x in test_positive_values:
            with self.subTest(function="acosh(cosh(x))", x=x):
                fx = FlexFloat.from_float(x)
                result = ffmath.acosh(ffmath.cosh(fx))
                self.assertAlmostEqualRel(result.to_float(), abs(x), tolerance=1e-12)

        # Test atanh(tanh(x)) = x for appropriate domain
        test_bounded_values = [-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0]

        for x in test_bounded_values:
            with self.subTest(function="atanh(tanh(x))", x=x):
                fx = FlexFloat.from_float(x)
                result = ffmath.atanh(ffmath.tanh(fx))
                self.assertAlmostEqualRel(result.to_float(), x, tolerance=1e-12)

    def test_extreme_precision_requirements(self):
        """Test hyperbolic functions with extreme precision requirements."""
        # Test with FlexFloat's extended precision capabilities
        extreme_precision_values = [
            1e-50,
            -1e-50,  # Very small
            1e-100,
            -1e-100,  # Extremely small
        ]

        for val in extreme_precision_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)

                # For very small x: sinh(x) ≈ x, cosh(x) ≈ 1, tanh(x) ≈ x
                sinh_result = ffmath.sinh(ff_val)
                cosh_result = ffmath.cosh(ff_val)
                tanh_result = ffmath.tanh(ff_val)

                self.assertAlmostEqualRel(sinh_result.to_float(), val, tolerance=1e-15)
                self.assertAlmostEqualRel(cosh_result.to_float(), 1.0, tolerance=1e-15)
                self.assertAlmostEqualRel(tanh_result.to_float(), val, tolerance=1e-15)


if __name__ == "__main__":
    unittest.main()
