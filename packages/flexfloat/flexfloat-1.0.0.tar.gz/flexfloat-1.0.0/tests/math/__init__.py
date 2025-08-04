"""Math tests package for FlexFloat."""

import math
from typing import Callable, List

from flexfloat import FlexFloat
from flexfloat import math as ffmath
from tests import FlexFloatTestCase


class TestMathSetup(FlexFloatTestCase):
    """Base test class with common test setup and utilities for math functions."""

    def setUp(self):
        """Set up common test values to avoid code duplication."""
        # Basic test values
        self.basic_values = [
            0.0,
            1.0,
            -1.0,
            2.0,
            -2.0,
            0.5,
            -0.5,
            1.5,
            -1.5,
            3.14159,
            -3.14159,
            2.71828,
            -2.71828,
        ]

        # Various sizes - small values
        self.small_values = [
            1e-10,
            -1e-10,
            1e-100,
            -1e-100,
            1e-300,
            -1e-300,
            1e-308,
            -1e-308,
            # Values near denormal range
            2.225073858507201e-308,  # Smallest normal double
            1.1125369292536007e-308,  # Half of smallest normal
        ]

        # Various sizes - large values
        self.large_values = [
            1e10,
            -1e10,
            1e100,
            -1e100,
            1e200,
            -1e200,
            1e300,
            -1e300,
            # Values near overflow for standard doubles
            1.7976931348623157e308,  # Near max double
            1.7976931348623157e307,  # 10x smaller than max
        ]

        # Edge case values
        self.edge_values = [
            0.0,
            -0.0,  # Both positive and negative zero
            float("inf"),
            float("-inf"),  # Infinities
            float("nan"),  # NaN
        ]

        # Create extreme FlexFloat values using from_int for very large integers
        self.extreme_flexfloats = [
            # Very large integers that exceed normal float precision
            FlexFloat.from_int(10**100),  # 1 googol
            FlexFloat.from_int(-(10**100)),  # -1 googol
            FlexFloat.from_int(2**1000),  # 2^1000 (very large power of 2)
            FlexFloat.from_int(-(2**1000)),  # -2^1000
            FlexFloat.from_int(10**500),  # 1 followed by 500 zeros
            FlexFloat.from_int(-(10**500)),  # Negative version
            # Large factorials that regular floats can't represent exactly
            FlexFloat.from_int(math.factorial(100)),  # 100!
            FlexFloat.from_int(-math.factorial(100)),  # -100!
            FlexFloat.from_int(math.factorial(200)),  # 200! (much larger)
            # Powers of small primes that grow very large
            FlexFloat.from_int(3**1000),  # 3^1000
            FlexFloat.from_int(7**500),  # 7^500
        ]

        # Combined regular test values (excluding extremes for standard comparisons)
        self.regular_values = self.basic_values + self.small_values + self.large_values

        # All test values including edge cases (but not outside normal float range)
        self.all_regular_values = self.regular_values + [
            val for val in self.edge_values if not math.isnan(val)
        ]

    def create_flexfloat_values(self, float_values: List[float]) -> List[FlexFloat]:
        """Convert list of float values to FlexFloat objects."""
        return [FlexFloat.from_float(val) for val in float_values]

    def compare_with_math(
        self,
        ff_func: Callable[[FlexFloat], FlexFloat],
        math_func: Callable[[float], float],
        test_values: List[float],
        tolerance: float = 1e-10,
    ) -> None:
        """Compare FlexFloat math function with Python math equivalent."""
        for val in test_values:
            ff_val = FlexFloat.from_float(val)
            with self.subTest(value=val):
                try:
                    ff_result = ff_func(ff_val)
                    math_result = math_func(val)

                    # Handle special cases
                    if math.isnan(math_result):
                        self.assertTrue(
                            ff_result.is_nan(), f"Expected NaN for input {val}"
                        )
                    elif math.isinf(math_result):
                        self.assertTrue(
                            ff_result.is_infinity(),
                            f"Expected infinity for input {val}",
                        )
                        self.assertEqual(
                            ff_result.sign,
                            math_result < 0,
                            f"Wrong sign for infinity with input {val}",
                        )
                    else:
                        ff_float = ff_result.to_float()
                        self.assertAlmostEqualRel(ff_float, math_result, tolerance)

                except Exception:
                    # Check if ff_func didn't raise an OverflowError
                    try:
                        ff_func(ff_val)
                    except (OverflowError, ValueError) as e:
                        self.fail(
                            f"FlexFloat function raised {type(e).__name__} "
                            f"for input {val}: {e}"
                        )


class TestMathConstants(TestMathSetup):
    """Test mathematical constants in the math module."""

    def test_constants_are_flexfloat(self):
        """Test that mathematical constants are FlexFloat instances."""
        self.assertIsInstance(ffmath.e, FlexFloat)
        self.assertIsInstance(ffmath.pi, FlexFloat)
        self.assertIsInstance(ffmath.tau, FlexFloat)
        self.assertIsInstance(ffmath.inf, FlexFloat)
        self.assertIsInstance(ffmath.nan, FlexFloat)

    def test_constants_values(self):
        """Test that mathematical constants have correct values."""
        self.assertAlmostEqualRel(ffmath.e.to_float(), math.e, 1e-15)
        self.assertAlmostEqualRel(ffmath.pi.to_float(), math.pi, 1e-15)
        self.assertAlmostEqualRel(ffmath.tau.to_float(), math.tau, 1e-15)
        self.assertTrue(ffmath.inf.is_infinity())
        self.assertFalse(ffmath.inf.sign)
        self.assertTrue(ffmath.nan.is_nan())
