"""Tests for trigonometric and hyperbolic functions in FlexFloat math module."""

import math
import unittest

from flexfloat import FlexFloat
from flexfloat import math as ffmath
from tests.math import TestMathSetup


class TestTrigonometricFunctions(TestMathSetup):
    """Comprehensive tests for trigonometric functions."""

    # ==================== SINE FUNCTION TESTS ====================

    def test_sin_normal_cases(self):
        """Test sine function with comprehensive normal values."""
        # Standard angles in radians
        standard_angles = [
            0.0,  # 0°
            math.pi / 6,  # 30°
            math.pi / 4,  # 45°
            math.pi / 3,  # 60°
            math.pi / 2,  # 90°
            2 * math.pi / 3,  # 120°
            3 * math.pi / 4,  # 135°
            5 * math.pi / 6,  # 150°
            math.pi,  # 180°
            7 * math.pi / 6,  # 210°
            5 * math.pi / 4,  # 225°
            4 * math.pi / 3,  # 240°
            3 * math.pi / 2,  # 270°
            5 * math.pi / 3,  # 300°
            7 * math.pi / 4,  # 315°
            11 * math.pi / 6,  # 330°
            2 * math.pi,  # 360°
        ]

        # Add negative angles
        negative_angles = [-angle for angle in standard_angles[1:]]  # Skip 0

        # Add random values
        random_values = [-15.7, -5.2, -2.1, 0.1, 1.3, 4.7, 10.5, 25.8]

        all_values = standard_angles + negative_angles + random_values
        self.compare_with_math(ffmath.sin, math.sin, all_values)

    def test_sin_variety_of_sizes(self):
        """Test sine with various magnitude values."""
        # Small values near zero
        small_values = [1e-10, -1e-10, 1e-15, -1e-15, 1e-20]

        # Medium values
        medium_values = self.basic_values

        # Large values (but still reasonable for trig functions)
        large_values = [100.5, -100.5, 1000.1, -1000.1, 10000.7, -10000.7]

        all_sizes = small_values + medium_values + large_values
        self.compare_with_math(ffmath.sin, math.sin, all_sizes, tolerance=1e-12)

    def test_sin_edge_cases(self):
        """Test sine function with edge cases."""
        # Test zero (both positive and negative)
        self.assertAlmostEqualRel(ffmath.sin(FlexFloat.from_float(0.0)).to_float(), 0.0)
        self.assertAlmostEqualRel(
            ffmath.sin(FlexFloat.from_float(-0.0)).to_float(), 0.0
        )

        # Test NaN
        result = ffmath.sin(FlexFloat.nan())
        self.assertTrue(result.is_nan())

        # Test positive infinity
        result = ffmath.sin(FlexFloat.infinity(sign=False))
        self.assertTrue(result.is_nan())

        # Test negative infinity
        result = ffmath.sin(FlexFloat.infinity(sign=True))
        self.assertTrue(result.is_nan())

    def test_sin_extreme_values(self):
        """Test sine with values outside normal float range."""
        # Very large angles - sin should still be bounded [-1, 1]
        very_large_angles = [1e10, -1e10, 1e20, -1e20, 1e50, -1e50]

        for angle in very_large_angles:
            with self.subTest(angle=angle):
                ff_angle = FlexFloat.from_float(angle)
                result = ffmath.sin(ff_angle)
                self.assertFalse(result.is_nan(), f"sin({angle}) should not be NaN")
                self.assertFalse(
                    result.is_infinity(), f"sin({angle}) should not be infinite"
                )
                # sin should be bounded
                self.assertTrue(
                    result.abs() <= FlexFloat.from_float(1.0),
                    f"sin({angle}) should be in [-1, 1], got {result.to_float()}",
                )

    def test_sin_mathematical_identities(self):
        """Test mathematical identities involving sine."""
        test_values = [0.1, 0.5, 1.0, 1.5, 2.0, math.pi / 4, math.pi / 3]

        for x in test_values:
            with self.subTest(x=x):
                fx = FlexFloat.from_float(x)

                # sin(-x) = -sin(x)
                sin_x = ffmath.sin(fx)
                sin_neg_x = ffmath.sin(-fx)
                self.assertAlmostEqualRel(
                    (-sin_x).to_float(), sin_neg_x.to_float(), tolerance=1e-14
                )

                # sin²(x) + cos²(x) = 1
                cos_x = ffmath.cos(fx)
                sin_sq_plus_cos_sq = sin_x * sin_x + cos_x * cos_x
                self.assertAlmostEqualRel(
                    sin_sq_plus_cos_sq.to_float(), 1.0, tolerance=1e-13
                )

    # ==================== COSINE FUNCTION TESTS ====================

    def test_cos_normal_cases(self):
        """Test cosine function with comprehensive normal values."""
        # Use same comprehensive angle set as sine
        standard_angles = [
            0.0,
            math.pi / 6,
            math.pi / 4,
            math.pi / 3,
            math.pi / 2,
            2 * math.pi / 3,
            3 * math.pi / 4,
            5 * math.pi / 6,
            math.pi,
            7 * math.pi / 6,
            5 * math.pi / 4,
            4 * math.pi / 3,
            3 * math.pi / 2,
            5 * math.pi / 3,
            7 * math.pi / 4,
            11 * math.pi / 6,
            2 * math.pi,
        ]
        negative_angles = [-angle for angle in standard_angles[1:]]
        random_values = [-15.7, -5.2, -2.1, 0.1, 1.3, 4.7, 10.5, 25.8]

        all_values = standard_angles + negative_angles + random_values
        self.compare_with_math(ffmath.cos, math.cos, all_values)

    def test_cos_variety_of_sizes(self):
        """Test cosine with various magnitude values."""
        small_values = [1e-10, -1e-10, 1e-15, -1e-15, 1e-20]
        medium_values = self.basic_values
        large_values = [100.5, -100.5, 1000.1, -1000.1, 10000.7, -10000.7]

        all_sizes = small_values + medium_values + large_values
        self.compare_with_math(ffmath.cos, math.cos, all_sizes, tolerance=1e-12)

    def test_cos_edge_cases(self):
        """Test cosine function with edge cases."""
        # Test zero - cos(0) = 1
        self.assertAlmostEqualRel(ffmath.cos(FlexFloat.from_float(0.0)).to_float(), 1.0)

        # Test NaN and infinities
        self.assertTrue(ffmath.cos(FlexFloat.nan()).is_nan())
        self.assertTrue(ffmath.cos(FlexFloat.infinity(sign=False)).is_nan())
        self.assertTrue(ffmath.cos(FlexFloat.infinity(sign=True)).is_nan())

    def test_cos_extreme_values(self):
        """Test cosine with values outside normal float range."""
        very_large_angles = [1e10, -1e10, 1e20, -1e20, 1e50, -1e50]

        for angle in very_large_angles:
            with self.subTest(angle=angle):
                ff_angle = FlexFloat.from_float(angle)
                result = ffmath.cos(ff_angle)
                self.assertFalse(result.is_nan())
                self.assertFalse(result.is_infinity())
                self.assertTrue(result.abs() <= FlexFloat.from_float(1.0))

    def test_cos_mathematical_identities(self):
        """Test mathematical identities involving cosine."""
        test_values = [0.1, 0.5, 1.0, 1.5, 2.0, math.pi / 4, math.pi / 3]

        for x in test_values:
            with self.subTest(x=x):
                fx = FlexFloat.from_float(x)

                # cos(-x) = cos(x) (even function)
                cos_x = ffmath.cos(fx)
                cos_neg_x = ffmath.cos(-fx)
                self.assertAlmostEqualRel(
                    cos_x.to_float(), cos_neg_x.to_float(), tolerance=1e-14
                )

    # ==================== TANGENT FUNCTION TESTS ====================

    def test_tan_normal_cases(self):
        """Test tangent function with normal values, avoiding singularities."""
        # Avoid multiples of π/2 where tan is undefined
        safe_angles = [
            0.0,
            math.pi / 6,
            math.pi / 4,
            math.pi / 3,
            2 * math.pi / 3,
            3 * math.pi / 4,
            5 * math.pi / 6,
            -math.pi / 6,
            -math.pi / 4,
            -math.pi / 3,
            -2 * math.pi / 3,
            -3 * math.pi / 4,
            -5 * math.pi / 6,
        ]
        random_safe = [0.1, 0.5, 1.0, 1.4, -0.1, -0.5, -1.0, -1.4]

        all_values = safe_angles + random_safe
        self.compare_with_math(ffmath.tan, math.tan, all_values)

    def test_tan_variety_of_sizes(self):
        """Test tangent with various magnitude values."""
        small_values = [1e-10, -1e-10, 1e-15, -1e-15]
        medium_values = [
            val for val in self.basic_values if abs(val) < 1.4
        ]  # Avoid near π/2
        # Large values but avoid multiples of π/2
        large_values = [100.1, -100.1, 1000.2, -1000.2]

        all_sizes = small_values + medium_values + large_values
        self.compare_with_math(ffmath.tan, math.tan, all_sizes, tolerance=1e-12)

    def test_tan_edge_cases(self):
        """Test tangent function with edge cases."""
        # Test zero
        self.assertAlmostEqualRel(ffmath.tan(FlexFloat.from_float(0.0)).to_float(), 0.0)

        # Test NaN and infinities
        self.assertTrue(ffmath.tan(FlexFloat.nan()).is_nan())
        self.assertTrue(ffmath.tan(FlexFloat.infinity(sign=False)).is_nan())
        self.assertTrue(ffmath.tan(FlexFloat.infinity(sign=True)).is_nan())

    def test_tan_near_singularities(self):
        """Test tangent behavior near singularities (π/2, 3π/2, etc.)."""
        pi_2 = math.pi / 2

        # Test values very close to π/2 but not exactly π/2
        near_pi_2_values = [
            pi_2 - 1e-10,
            pi_2 + 1e-10,
            pi_2 - 1e-15,
            pi_2 + 1e-15,
            -pi_2 - 1e-10,
            -pi_2 + 1e-10,
        ]

        for val in near_pi_2_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.tan(ff_val)
                # Should be very large but finite
                self.assertFalse(result.is_nan(), f"tan({val}) should not be NaN")
                self.assertTrue(
                    result.abs() > FlexFloat.from_float(1e9),
                    f"tan({val}) should be very large",
                )

    def test_tan_extreme_values(self):
        """Test tangent with values outside normal float range."""
        # Large angles - tan can be very large but should not overflow to infinity
        very_large_angles = [
            1e10,
            -1e10,
            1e15,
            -1e15,
        ]  # Avoiding exact multiples of π/2

        for angle in very_large_angles:
            with self.subTest(angle=angle):
                ff_angle = FlexFloat.from_float(angle)
                result = ffmath.tan(ff_angle)
                # tan might be very large but should be finite (unless at singularity)
                if not result.is_infinity():
                    self.assertFalse(result.is_nan(), f"tan({angle}) should not be NaN")

    def test_radians_normal_cases(self):
        """Test radians conversion function."""
        degree_values = [0.0, 30.0, 45.0, 60.0, 90.0, 180.0, 270.0, 360.0]

        for degrees in degree_values:
            with self.subTest(degrees=degrees):
                ff_degrees = FlexFloat.from_float(degrees)
                result = ffmath.radians(ff_degrees)
                expected = math.radians(degrees)
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_degrees_normal_cases(self):
        """Test degrees conversion function."""
        radian_values = [
            0.0,
            math.pi / 6,
            math.pi / 4,
            math.pi / 3,
            math.pi / 2,
            math.pi,
        ]

        for radians in radian_values:
            with self.subTest(radians=radians):
                ff_radians = FlexFloat.from_float(radians)
                result = ffmath.degrees(ff_radians)
                expected = math.degrees(radians)
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_trigonometric_identities_comprehensive(self):
        """Test comprehensive trigonometric identities."""
        test_values = [0.1, 0.5, 1.0, 1.5, 2.0, math.pi / 6, math.pi / 4, math.pi / 3]

        for x in test_values:
            with self.subTest(x=x):
                fx = FlexFloat.from_float(x)

                # Fundamental identity: sin²(x) + cos²(x) = 1
                sin_x = ffmath.sin(fx)
                cos_x = ffmath.cos(fx)
                identity1 = sin_x * sin_x + cos_x * cos_x
                self.assertAlmostEqualRel(identity1.to_float(), 1.0, tolerance=1e-14)

                # tan(x) = sin(x) / cos(x) (when cos(x) ≠ 0)
                if cos_x.abs() > FlexFloat.from_float(1e-10):
                    tan_x = ffmath.tan(fx)
                    tan_from_sin_cos = sin_x / cos_x
                    self.assertAlmostEqualRel(
                        tan_x.to_float(), tan_from_sin_cos.to_float(), tolerance=1e-12
                    )


class TestInverseTrigonometricFunctions(TestMathSetup):
    """Test inverse trigonometric functions."""

    def test_asin_normal_cases(self):
        """Test arc sine function with comprehensive normal values."""
        # Domain of asin is [-1, 1]
        domain_values = [
            -1.0,
            -0.9,
            -0.8,
            -0.7,
            -0.6,
            -0.5,
            -0.4,
            -0.3,
            -0.2,
            -0.1,
            0.0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0,
        ]

        # Special values
        special_values = [
            -1.0,  # asin(-1) = -π/2
            -math.sqrt(3) / 2,  # asin(-√3/2) = -π/3
            -math.sqrt(2) / 2,  # asin(-√2/2) = -π/4
            -0.5,  # asin(-1/2) = -π/6
            0.0,  # asin(0) = 0
            0.5,  # asin(1/2) = π/6
            math.sqrt(2) / 2,  # asin(√2/2) = π/4
            math.sqrt(3) / 2,  # asin(√3/2) = π/3
            1.0,  # asin(1) = π/2
        ]

        all_values = domain_values + special_values
        # Remove duplicates
        all_values = list(set(all_values))
        self.compare_with_math(ffmath.asin, math.asin, all_values)

    def test_asin_variety_of_sizes(self):
        """Test asin with various magnitudes within valid domain."""
        # Very small values
        small_values = [1e-10, -1e-10, 1e-15, -1e-15, 1e-20, -1e-20]

        # Values close to boundaries
        near_boundary = [0.99999, -0.99999, 0.999999, -0.999999]

        all_values = small_values + near_boundary
        self.compare_with_math(ffmath.asin, math.asin, all_values, tolerance=1e-14)

    def test_asin_edge_cases(self):
        """Test asin function with edge cases."""
        # Test zero
        self.assertAlmostEqualRel(
            ffmath.asin(FlexFloat.from_float(0.0)).to_float(), 0.0
        )

        # Test boundaries
        pi_2 = math.pi / 2
        self.assertAlmostEqualRel(
            ffmath.asin(FlexFloat.from_float(1.0)).to_float(), pi_2, tolerance=1e-14
        )
        self.assertAlmostEqualRel(
            ffmath.asin(FlexFloat.from_float(-1.0)).to_float(), -pi_2, tolerance=1e-14
        )

        # Test NaN
        self.assertTrue(ffmath.asin(FlexFloat.nan()).is_nan())

        # Test infinities (should return NaN)
        self.assertTrue(ffmath.asin(FlexFloat.infinity(sign=False)).is_nan())
        self.assertTrue(ffmath.asin(FlexFloat.infinity(sign=True)).is_nan())

    def test_asin_domain_violations(self):
        """Test asin with values outside domain [-1, 1]."""
        invalid_values = [1.1, -1.1, 2.0, -2.0, 10.0, -10.0]

        for val in invalid_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.asin(ff_val)
                self.assertTrue(result.is_nan(), f"asin({val}) should return NaN")

    def test_asin_extreme_precision(self):
        """Test asin with extreme precision requirements."""
        # Very precise values near boundaries
        precise_values = [0.9999999999999999, -0.9999999999999999, 1e-100, -1e-100]

        for val in precise_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.asin(ff_val)
                expected = math.asin(val)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-12)

    def test_acos_normal_cases(self):
        """Test arc cosine function with comprehensive normal values."""
        # Same domain as asin: [-1, 1]
        domain_values = [
            -1.0,
            -0.9,
            -0.8,
            -0.7,
            -0.6,
            -0.5,
            -0.4,
            -0.3,
            -0.2,
            -0.1,
            0.0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5,
            0.6,
            0.7,
            0.8,
            0.9,
            1.0,
        ]
        self.compare_with_math(ffmath.acos, math.acos, domain_values)

    def test_acos_edge_cases(self):
        """Test acos function with edge cases."""
        # Test boundaries
        self.assertAlmostEqualRel(
            ffmath.acos(FlexFloat.from_float(1.0)).to_float(), 0.0, tolerance=1e-14
        )
        self.assertAlmostEqualRel(
            ffmath.acos(FlexFloat.from_float(-1.0)).to_float(), math.pi, tolerance=1e-14
        )
        self.assertAlmostEqualRel(
            ffmath.acos(FlexFloat.from_float(0.0)).to_float(),
            math.pi / 2,
            tolerance=1e-14,
        )

        # Test NaN and domain violations
        self.assertTrue(ffmath.acos(FlexFloat.nan()).is_nan())
        self.assertTrue(ffmath.acos(FlexFloat.from_float(1.1)).is_nan())
        self.assertTrue(ffmath.acos(FlexFloat.from_float(-1.1)).is_nan())

    def test_atan_normal_cases(self):
        """Test arc tangent function with comprehensive normal values."""
        # atan has domain (-∞, ∞)
        wide_range = [
            -100.0,
            -50.0,
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
            50.0,
            100.0,
        ]
        self.compare_with_math(ffmath.atan, math.atan, wide_range)

    def test_atan_variety_of_sizes(self):
        """Test atan with various magnitude values."""
        small_values = [1e-10, -1e-10, 1e-100, -1e-100]
        large_values = [1e10, -1e10, 1e100, -1e100]

        all_values = small_values + self.basic_values + large_values
        self.compare_with_math(ffmath.atan, math.atan, all_values, tolerance=1e-14)

    def test_atan_edge_cases(self):
        """Test atan function with edge cases."""
        # Test zero
        self.assertAlmostEqualRel(
            ffmath.atan(FlexFloat.from_float(0.0)).to_float(), 0.0
        )

        # Test asymptotic behavior
        pi_2 = math.pi / 2
        self.assertAlmostEqualRel(
            ffmath.atan(FlexFloat.infinity(sign=False)).to_float(),
            pi_2,
            tolerance=1e-14,
        )
        self.assertAlmostEqualRel(
            ffmath.atan(FlexFloat.infinity(sign=True)).to_float(),
            -pi_2,
            tolerance=1e-14,
        )

        # Test NaN
        self.assertTrue(ffmath.atan(FlexFloat.nan()).is_nan())

    def test_atan_extreme_values(self):
        """Test atan with values outside normal float range."""
        extreme_values = [1e50, -1e50, 1e100, -1e100, 1e200, -1e200]

        for val in extreme_values:
            with self.subTest(value=val):
                ff_val = FlexFloat.from_float(val)
                result = ffmath.atan(ff_val)
                # Should approach ±π/2
                self.assertFalse(result.is_nan())
                self.assertFalse(result.is_infinity())
                expected_sign = 1 if val > 0 else -1
                self.assertTrue(
                    abs(result.to_float() - expected_sign * math.pi / 2) < 1e-10
                )

    def test_atan2_comprehensive(self):
        """Comprehensive test for atan2 function."""
        # Test all quadrants and special cases
        test_cases = [
            # First quadrant
            (1.0, 1.0),
            (2.0, 1.0),
            (1.0, 2.0),
            (3.0, 4.0),
            # Second quadrant
            (1.0, -1.0),
            (2.0, -1.0),
            (1.0, -2.0),
            (3.0, -4.0),
            # Third quadrant
            (-1.0, -1.0),
            (-2.0, -1.0),
            (-1.0, -2.0),
            (-3.0, -4.0),
            # Fourth quadrant
            (-1.0, 1.0),
            (-2.0, 1.0),
            (-1.0, 2.0),
            (-3.0, 4.0),
            # Axes
            (0.0, 1.0),
            (0.0, -1.0),
            (1.0, 0.0),
            (-1.0, 0.0),
            # Small values
            (1e-10, 1e-10),
            (-1e-10, 1e-10),
            (1e-10, -1e-10),
            (-1e-10, -1e-10),
            # Large values
            (1e10, 1e10),
            (-1e10, 1e10),
            (1e10, -1e10),
            (-1e10, -1e10),
        ]

        for y, x in test_cases:
            with self.subTest(y=y, x=x):
                ff_y = FlexFloat.from_float(y)
                ff_x = FlexFloat.from_float(x)
                result = ffmath.atan2(ff_y, ff_x)
                expected = math.atan2(y, x)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-14)

    def test_atan2_edge_cases(self):
        """Test atan2 with edge cases and infinities."""
        # Test with infinities
        inf_cases = [
            (float("inf"), float("inf")),  # π/4
            (float("inf"), float("-inf")),  # 3π/4
            (float("-inf"), float("-inf")),  # -3π/4
            (float("-inf"), float("inf")),  # -π/4
            (float("inf"), 1.0),  # π/2
            (float("-inf"), 1.0),  # -π/2
            (1.0, float("inf")),  # 0
            (1.0, float("-inf")),  # π
        ]

        for y, x in inf_cases:
            with self.subTest(y=y, x=x):
                ff_y = (
                    FlexFloat.infinity(sign=(y < 0))
                    if math.isinf(y)
                    else FlexFloat.from_float(y)
                )
                ff_x = (
                    FlexFloat.infinity(sign=(x < 0))
                    if math.isinf(x)
                    else FlexFloat.from_float(x)
                )
                result = ffmath.atan2(ff_y, ff_x)
                expected = math.atan2(y, x)
                self.assertAlmostEqualRel(result.to_float(), expected, tolerance=1e-14)


if __name__ == "__main__":
    unittest.main()
