"""Tests for FlexFloat multiplication operations."""

import unittest

from flexfloat import FlexFloat, ListBoolBitArray
from tests import FlexFloatTestCase


class TestMultiplication(FlexFloatTestCase):
    """Test FlexFloat multiplication operations."""

    def test_flexfloat_multiplication_with_zero_returns_zero(self):
        f1 = 5.0
        f2 = 0.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 * bf2
        expected = f1 * f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_with_one_returns_original(self):
        f1 = 5.0
        f2 = 1.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 * bf2
        expected = f1 * f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_simple_case_works_correctly(self):
        f1 = 2.0
        f2 = 3.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 * bf2
        expected = f1 * f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_fractional_values_works_correctly(self):
        f1 = 0.5
        f2 = 0.25
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 * bf2
        expected = f1 * f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_negative_values_works_correctly(self):
        f1 = -2.0
        f2 = 3.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 * bf2
        expected = f1 * f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_both_negative_works_correctly(self):
        f1 = -2.0
        f2 = -3.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 * bf2
        expected = f1 * f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_large_numbers_works_correctly(self):
        f1 = 1.0e5
        f2 = 2.0e10
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 * bf2
        expected = f1 * f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_small_numbers_works_correctly(self):
        f1 = 1.0e-10
        f2 = 2.0e-15
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 * bf2
        expected = f1 * f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_special_values_nan(self):
        nan = FlexFloat.nan()
        normal = FlexFloat.from_float(5.0)
        result1 = nan * normal
        self.assertTrue(result1.is_nan())
        result2 = normal * nan
        self.assertTrue(result2.is_nan())
        result3 = nan * nan
        self.assertTrue(result3.is_nan())

    def test_flexfloat_multiplication_special_values_infinity(self):
        inf = FlexFloat.infinity()
        neg_inf = FlexFloat.infinity(sign=True)
        normal = FlexFloat.from_float(5.0)
        neg_normal = FlexFloat.from_float(-3.0)
        result1 = inf * normal
        self.assertTrue(result1.is_infinity())
        self.assertFalse(result1.sign)
        result2 = inf * neg_normal
        self.assertTrue(result2.is_infinity())
        self.assertTrue(result2.sign)
        result3 = neg_inf * normal
        self.assertTrue(result3.is_infinity())
        self.assertTrue(result3.sign)
        result4 = neg_inf * neg_normal
        self.assertTrue(result4.is_infinity())
        self.assertFalse(result4.sign)

    def test_flexfloat_multiplication_overflow_detection(self):
        large1 = FlexFloat.from_float(1.7e308)
        large2 = FlexFloat.from_float(2.0)
        result = large1 * large2
        self.assertFalse(result.is_infinity())
        self.assertGreater(len(result.exponent), 11)

    def test_flexfloat_multiplication_underflow_to_zero(self):
        small1 = FlexFloat.from_float(1e-323)
        small2 = FlexFloat.from_float(1e-200)
        result = small1 * small2
        self.assertFalse(result.is_zero())
        self.assertGreater(len(result.exponent), 11)

    def test_flexfloat_multiplication_precision_edge_cases(self):
        test_cases = [
            (1.0000000000000002, 1.0000000000000002),
            (0.9999999999999998, 0.9999999999999998),
            (1.5, 1.3333333333333333),
            (3.141592653589793, 2.718281828459045),
            (1.23456789e15, 9.87654321e-16),
        ]
        for f1, f2 in test_cases:
            with self.subTest(f1=f1, f2=f2):
                bf1 = FlexFloat.from_float(f1)
                bf2 = FlexFloat.from_float(f2)
                result = bf1 * bf2
                expected = f1 * f2
                if expected != 0:
                    rel_error = abs((result.to_float() - expected) / expected)
                    self.assertLess(rel_error, 1e-14)
                else:
                    self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_commutative_property(self):
        test_cases = [
            (2.5, 4.0),
            (-1.5, 3.0),
            (0.125, 8.0),
            (1e10, 1e-5),
            (-7.0, -11.0),
        ]
        for f1, f2 in test_cases:
            with self.subTest(f1=f1, f2=f2):
                bf1 = FlexFloat.from_float(f1)
                bf2 = FlexFloat.from_float(f2)
                result1 = bf1 * bf2
                result2 = bf2 * bf1
                self.assertAlmostEqualRel(result1.to_float(), result2.to_float())

    def test_flexfloat_multiplication_associative_property(self):
        test_cases = [
            (2.0, 3.0, 4.0),
            (0.5, 0.25, 8.0),
            (-1.0, 2.0, -3.0),
            (1.1, 1.2, 1.3),
        ]
        for f1, f2, f3 in test_cases:
            with self.subTest(f1=f1, f2=f2, f3=f3):
                bf1 = FlexFloat.from_float(f1)
                bf2 = FlexFloat.from_float(f2)
                bf3 = FlexFloat.from_float(f3)
                result1 = (bf1 * bf2) * bf3
                result2 = bf1 * (bf2 * bf3)
                self.assertAlmostEqualRel(result1.to_float(), result2.to_float())

    def test_flexfloat_multiplication_distributive_property(self):
        test_cases = [
            (2.0, 3.0, 4.0),
            (1.5, -2.0, 0.5),
            (0.1, 0.2, 0.3),
        ]
        for a, b, c in test_cases:
            with self.subTest(a=a, b=b, c=c):
                bf_a = FlexFloat.from_float(a)
                bf_b = FlexFloat.from_float(b)
                bf_c = FlexFloat.from_float(c)
                left = bf_a * (bf_b + bf_c)
                right = (bf_a * bf_b) + (bf_a * bf_c)
                self.assertAlmostEqualRel(left.to_float(), right.to_float())

    def test_flexfloat_multiplication_powers_of_two(self):
        test_cases = [
            (2.0, 4.0),
            (0.5, 0.25),
            (16.0, 0.0625),
            (1024.0, 1.0 / 1024.0),
        ]
        for f1, f2 in test_cases:
            with self.subTest(f1=f1, f2=f2):
                bf1 = FlexFloat.from_float(f1)
                bf2 = FlexFloat.from_float(f2)
                result = bf1 * bf2
                expected = f1 * f2
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_denormalized_numbers(self):
        tiny1 = FlexFloat.from_float(1e-150)
        tiny2 = FlexFloat.from_float(1e-150)
        result = tiny1 * tiny2
        expected = 1e-150 * 1e-150

        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_multiplication_mixed_operand_types(self):
        bf = FlexFloat.from_float(3.5)
        result1 = bf * 2
        self.assertAlmostEqualRel(result1.to_float(), 7.0)
        result2 = bf * 1.5
        self.assertAlmostEqualRel(result2.to_float(), 5.25)
        result3 = 4 * bf
        self.assertAlmostEqualRel(result3.to_float(), 14.0)
        result4 = 2.5 * bf
        self.assertAlmostEqualRel(result4.to_float(), 8.75)

    def test_flexfloat_multiplication_extreme_exponent_ranges(self):
        large_exp = FlexFloat(
            sign=False,
            exponent=ListBoolBitArray.from_signed_int(2046, 12),
            fraction=ListBoolBitArray.from_signed_int(1, 52),
        )
        multiplier = FlexFloat.from_float(8.0)
        result = large_exp * multiplier
        self.assertGreater(len(result.exponent), len(large_exp.exponent))

    def test_flexfloat_multiplication_exponent_growth_on_overflow(self):
        large1 = FlexFloat.from_float(1e200)
        large2 = FlexFloat.from_float(1e200)
        result = large1 * large2
        self.assertFalse(result.is_infinity())
        original_exp_length = len(large1.exponent)
        self.assertGreater(len(result.exponent), original_exp_length)
        self.assertGreater(abs(result.to_float()), 0)

    def test_flexfloat_multiplication_exponent_growth_on_underflow(self):
        small1 = FlexFloat.from_float(1e-200)
        small2 = FlexFloat.from_float(1e-200)
        result = small1 * small2
        self.assertFalse(result.is_zero())
        original_exp_length = len(small1.exponent)
        self.assertGreater(len(result.exponent), original_exp_length)
        self.assertFalse(result.is_infinity())


if __name__ == "__main__":
    unittest.main()
