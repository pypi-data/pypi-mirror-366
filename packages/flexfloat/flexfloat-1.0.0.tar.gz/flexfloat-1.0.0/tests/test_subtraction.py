"""Tests for FlexFloat subtraction operations."""

import unittest

from flexfloat import FlexFloat, ListBoolBitArray
from tests import FlexFloatTestCase


class TestSubtraction(FlexFloatTestCase):
    """Test FlexFloat subtraction operations."""

    def test_flexfloat_subtraction_with_zero_returns_original(self):
        f1 = 42.0
        f2 = 0.0
        bf = FlexFloat.from_float(f1)
        bf_zero = FlexFloat.from_float(f2)
        result = bf - bf_zero
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_subtraction_zero_minus_value_returns_negated(self):
        f1 = 0.0
        f2 = 42.0
        bf_zero = FlexFloat.from_float(f1)
        bf = FlexFloat.from_float(f2)
        result = bf_zero - bf
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_subtraction_same_value_returns_zero(self):
        bf = FlexFloat.from_float(123.456)
        result = bf - bf
        self.assertTrue(result.is_zero())

    def test_flexfloat_subtraction_simple_case_works_correctly(self):
        f1 = 5.0
        f2 = 3.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 - bf2
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_subtraction_negative_result_works_correctly(self):
        f1 = 3.0
        f2 = 5.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 - bf2
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_subtraction_large_numbers_works_correctly(self):
        f1 = 2.34e18
        f2 = 1.57e17
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 - bf2
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_subtraction_small_numbers_works_correctly(self):
        f1 = 1e-15
        f2 = 5e-16
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 - bf2
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_subtraction_different_exponents_works_correctly(self):
        f1 = 1000.0
        f2 = 0.001
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 - bf2
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_subtraction_rejects_non_flexfloat_operands(self):
        bf = FlexFloat.from_float(1.0)
        with self.assertRaises(TypeError):
            bf - "not a number"  # type: ignore

    def test_flexfloat_subtraction_handles_nan_operands(self):
        bf_normal = FlexFloat.from_float(1.0)
        bf_nan = FlexFloat.from_float(float("nan"))
        result1 = bf_normal - bf_nan
        self.assertTrue(result1.is_nan())
        result2 = bf_nan - bf_normal
        self.assertTrue(result2.is_nan())
        result3 = bf_nan - bf_nan
        self.assertTrue(result3.is_nan())

    def test_flexfloat_subtraction_handles_infinity_operands(self):
        bf_normal = FlexFloat.from_float(1.0)
        bf_inf = FlexFloat.from_float(float("inf"))
        bf_neg_inf = FlexFloat.from_float(float("-inf"))
        result1 = bf_normal - bf_inf
        self.assertTrue(result1.is_infinity())
        self.assertTrue(result1.sign)
        result2 = bf_normal - bf_neg_inf
        self.assertTrue(result2.is_infinity())
        self.assertFalse(result2.sign)
        result3 = bf_inf - bf_normal
        self.assertTrue(result3.is_infinity())
        self.assertFalse(result3.sign)
        result4 = bf_neg_inf - bf_normal
        self.assertTrue(result4.is_infinity())
        self.assertTrue(result4.sign)
        result5 = bf_inf - bf_inf
        self.assertTrue(result5.is_nan())
        result6 = bf_neg_inf - bf_neg_inf
        self.assertTrue(result6.is_nan())
        result7 = bf_inf - bf_neg_inf
        self.assertTrue(result7.is_infinity())
        self.assertFalse(result7.sign)
        result8 = bf_neg_inf - bf_inf
        self.assertTrue(result8.is_infinity())
        self.assertTrue(result8.sign)

    def test_flexfloat_subtraction_with_mixed_signs_becomes_addition(self):
        f1 = 5.0
        f2 = -3.0
        bf_pos = FlexFloat.from_float(f1)
        bf_neg = FlexFloat.from_float(f2)
        result1 = bf_pos - bf_neg
        expected1 = f1 - f2
        self.assertAlmostEqualRel(result1.to_float(), expected1)
        result2 = bf_neg - bf_pos
        expected2 = f2 - f1
        self.assertAlmostEqualRel(result2.to_float(), expected2)

    def test_flexfloat_subtraction_precision_loss_edge_cases(self):
        f1 = 1.0000000000000002
        f2 = 1.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 - bf2
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_subtraction_mantissa_borrowing(self):
        f1 = 1.25
        f2 = 1.75
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 - bf2
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_subtraction_denormalized_results(self):
        f1 = 1e-100
        f2 = 9e-101
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 - bf2
        expected = f1 - f2
        self.assertAlmostEqualRel(result.to_float(), expected)
        self.assertFalse(result.is_zero())
        self.assertGreater(result.to_float(), 0)
        f3 = 1.0000000000000002
        f4 = 1.0
        bf3 = FlexFloat.from_float(f3)
        bf4 = FlexFloat.from_float(f4)
        result2 = bf3 - bf4
        expected2 = f3 - f4
        self.assertAlmostEqualRel(result2.to_float(), expected2)
        self.assertGreater(result2.to_float(), 0)

    def test_flexfloat_subtraction_exponent_growth_on_underflow(self):
        """Test that subtraction causes exponent growth on underflow instead of going
        to zero like normal float."""
        # Test case 1: Subtracting very close small numbers that result in extreme
        # underflow
        # Create two very small numbers that are very close to each other
        small1 = FlexFloat.from_float(1e-300)
        small2 = FlexFloat.from_float(9.99999999999999e-301)  # Very close to small1

        # Perform subtraction - this should result in a very small number
        result = small1 - small2

        # Verify the result is not zero (unlike normal float which might underflow to 0)
        self.assertFalse(result.is_zero())

        # Verify that the exponent has grown to accommodate the underflow
        original_exp_length = len(small1.exponent)
        self.assertGreater(len(result.exponent), original_exp_length)

        # The result should be a very small positive number
        self.assertFalse(result.sign)  # Should be positive
        self.assertFalse(result.is_infinity())
        self.assertFalse(result.is_nan())

        # Test case 2: Subtraction that causes normalization shift and underflow
        # Create numbers where sub leads to significant leading zero cancellation
        num1 = FlexFloat.from_float(1.0000000000000002)  # Very close to 1.0
        num2 = FlexFloat.from_float(1.0)

        result2 = num1 - num2

        # This should not be zero and should handle the extreme precision
        self.assertFalse(result2.is_zero())
        self.assertGreater(result2.to_float(), 0)

        # Test case 3: Force underflow with manually constructed FlexFloats
        # Create FlexFloat with large negative exponent to test extreme underflow

        # Create a FlexFloat with a very small exponent near the limit
        small_exp_bf = FlexFloat(
            sign=False,
            exponent=ListBoolBitArray.from_signed_int(
                -1022, 11
            ),  # Near minimum for double precision
            fraction=ListBoolBitArray.from_signed_int(1, 52)[:52],
        )

        # Create another very close number
        slightly_larger = FlexFloat(
            sign=False,
            exponent=ListBoolBitArray.from_signed_int(-1022, 11),
            fraction=ListBoolBitArray.from_signed_int(2, 52)[:52],
        )

        result3 = slightly_larger - small_exp_bf

        # The result should not be zero and should require exponent growth
        self.assertFalse(result3.is_zero())

        # Check that the result's exponent is longer than the original standard 11-bit
        # exponent to handle the extreme underflow scenario
        self.assertGreater(len(result3.exponent), 11)

        # Verify the result represents a valid small number
        self.assertFalse(result3.is_infinity())
        self.assertFalse(result3.is_nan())


if __name__ == "__main__":
    unittest.main()
