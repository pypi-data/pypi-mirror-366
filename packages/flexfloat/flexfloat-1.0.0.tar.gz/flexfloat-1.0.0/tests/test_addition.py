"""Tests for FlexFloat addition operations."""

import unittest

from flexfloat import FlexFloat
from tests import FlexFloatTestCase


class TestAddition(FlexFloatTestCase):
    """Test FlexFloat addition operations."""

    def test_flexfloat_addition_with_zero_returns_original(self):
        f1 = 0.0
        f2 = 0.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 + bf2
        expected = f1 + f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_addition_simple_case_works_correctly(self):
        f1 = 1.0
        f2 = 1.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 + bf2
        expected = f1 + f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_addition_different_values_works_correctly(self):
        f1 = 1.0
        f2 = 2.0
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 + bf2
        expected = f1 + f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_addition_large_numbers_works_correctly(self):
        f1 = 1.57e17
        f2 = 2.34e18
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 + bf2
        expected = f1 + f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_addition_overflow_works_correctly(self):
        f1 = 1e308
        f2 = 1e308
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 + bf2
        self.assertFalse(result.is_infinity())
        self.assertGreater(len(result.exponent), 11)

    def test_flexfloat_addition_rejects_non_flexfloat_operands(self):
        bf = FlexFloat.from_float(1.0)
        with self.assertRaises(TypeError):
            bf + "not a number"  # type: ignore[operator]

    def test_flexfloat_addition_handles_nan_operands(self):
        bf_normal = FlexFloat.from_float(1.0)
        bf_nan = FlexFloat.from_float(float("nan"))
        result = bf_normal + bf_nan
        self.assertTrue(result.is_nan())

    def test_flexfloat_addition_handles_infinity_operands(self):
        bf_normal = FlexFloat.from_float(1.0)
        bf_inf = FlexFloat.from_float(float("inf"))
        bf_neg_inf = FlexFloat.from_float(float("-inf"))
        result_inf = bf_normal + bf_inf
        self.assertTrue(result_inf.is_infinity())
        self.assertFalse(result_inf.sign)
        result_neg_inf = bf_normal + bf_neg_inf
        self.assertTrue(result_neg_inf.is_infinity())
        self.assertTrue(result_neg_inf.sign)
        result_zero = bf_inf + bf_neg_inf
        self.assertTrue(result_zero.is_nan())

    def test_flexfloat_addition_with_mixed_signs_uses_subtraction(self):
        f1 = 5.0
        f2 = -3.0
        bf_pos = FlexFloat.from_float(f1)
        bf_neg = FlexFloat.from_float(f2)
        result = bf_pos + bf_neg
        expected = f1 + f2
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_addition_comprehensive_basic_cases(self):
        test_cases = [
            (0.0, 0.0),
            (1.0, 0.0),
            (0.0, 1.0),
            (1.0, 2.0),
            (2.0, 4.0),
            (4.0, 8.0),
        ]
        for a, b in test_cases:
            with self.subTest(a=a, b=b):
                bf_a = FlexFloat.from_float(a)
                bf_b = FlexFloat.from_float(b)
                result = bf_a + bf_b
                expected = a + b
                actual = result.to_float()
                self.assertAlmostEqualRel(actual, expected)

    def test_flexfloat_addition_fractional_cases(self):
        test_cases = [
            (0.5, 0.5),
            (0.125, 0.375),
            (0.25, 0.25),
            (0.75, 0.25),
            (1.25, 2.75),
            (3.5, 4.5),
            (7.25, 0.75),
        ]
        for a, b in test_cases:
            with self.subTest(a=a, b=b):
                bf_a = FlexFloat.from_float(a)
                bf_b = FlexFloat.from_float(b)
                result = bf_a + bf_b
                expected = a + b
                actual = result.to_float()
                self.assertAlmostEqualRel(actual, expected)

    def test_flexfloat_addition_original_bug_case(self):
        f1 = 7.5
        f2 = 2.5
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 + bf2
        expected = f1 + f2
        self.assertAlmostEqualRel(result.to_float(), expected)
        result_reverse = bf2 + bf1
        expected_reverse = f2 + f1
        self.assertAlmostEqualRel(result_reverse.to_float(), expected_reverse)

    def test_flexfloat_addition_different_exponents(self):
        test_cases = [
            (1.0, 0.001),
            (1000.0, 0.1),
            (0.001, 1000.0),
            (1.5, 0.0625),
            (8.0, 0.125),
        ]
        for a, b in test_cases:
            with self.subTest(a=a, b=b):
                bf_a = FlexFloat.from_float(a)
                bf_b = FlexFloat.from_float(b)
                result = bf_a + bf_b
                actual = result.to_float()
                expected = a + b
                self.assertAlmostEqualRel(actual, expected)

    def test_flexfloat_addition_large_numbers(self):
        test_cases = [
            (1000000.0, 2000000.0),
            (1e10, 2e10),
            (1.23e15, 4.56e15),
        ]
        for a, b in test_cases:
            with self.subTest(a=a, b=b):
                bf_a = FlexFloat.from_float(a)
                bf_b = FlexFloat.from_float(b)
                result = bf_a + bf_b
                expected = a + b
                actual = result.to_float()
                self.assertAlmostEqualRel(actual, expected)

    def test_flexfloat_addition_small_numbers(self):
        test_cases = [
            (1e-10, 2e-10),
            (1e-100, 2e-100),
            (5e-16, 5e-16),
        ]
        for a, b in test_cases:
            with self.subTest(a=a, b=b):
                bf_a = FlexFloat.from_float(a)
                bf_b = FlexFloat.from_float(b)
                result = bf_a + bf_b
                actual = result.to_float()
                expected = a + b
                self.assertAlmostEqualRel(actual, expected)

    def test_flexfloat_addition_mantissa_carry_cases(self):
        test_cases = [
            (1.5, 1.5),
            (3.75, 4.25),
            (7.5, 8.5),
            (15.5, 16.5),
        ]
        for a, b in test_cases:
            with self.subTest(a=a, b=b):
                bf_a = FlexFloat.from_float(a)
                bf_b = FlexFloat.from_float(b)
                result = bf_a + bf_b
                actual = result.to_float()
                expected = a + b
                self.assertAlmostEqualRel(actual, expected)

    def test_flexfloat_addition_edge_precision_cases(self):
        f1 = 1.0000000000000002
        f2 = 1.0000000000000002
        bf1 = FlexFloat.from_float(f1)
        bf2 = FlexFloat.from_float(f2)
        result = bf1 + bf2
        expected = f1 + f2
        actual = result.to_float()
        self.assertAlmostEqualRel(actual, expected)

    def test_flexfloat_addition_commutative_property(self):
        test_values = [1.0, 2.5, 7.5, 0.125, 1000.0, 1e-10]
        for i, a in enumerate(test_values):
            for b in test_values[i + 1 :]:
                with self.subTest(a=a, b=b):
                    bf_a = FlexFloat.from_float(a)
                    bf_b = FlexFloat.from_float(b)
                    result1 = bf_a + bf_b
                    result2 = bf_b + bf_a
                    self.assertAlmostEqualRel(result1.to_float(), result2.to_float())

    def test_flexfloat_addition_associative_property(self):
        test_cases = [
            (1.0, 2.0, 3.0),
            (0.5, 1.5, 2.5),
            (7.5, 2.5, 5.0),
            (0.125, 0.25, 0.375),
        ]
        for a, b, c in test_cases:
            with self.subTest(a=a, b=b, c=c):
                bf_a = FlexFloat.from_float(a)
                bf_b = FlexFloat.from_float(b)
                bf_c = FlexFloat.from_float(c)
                result1 = (bf_a + bf_b) + bf_c
                result2 = bf_a + (bf_b + bf_c)
                self.assertAlmostEqualRel(result1.to_float(), result2.to_float())

    def test_flexfloat_addition_identity_element(self):
        test_values = [0.0, 1.0, -1.0, 0.5, 7.5, 2.5, 1000.0, 1e-10, 1e10]
        for value in test_values:
            with self.subTest(value=value):
                bf_value = FlexFloat.from_float(value)
                bf_zero = FlexFloat.from_float(0.0)
                result1 = bf_value + bf_zero
                result2 = bf_zero + bf_value
                self.assertAlmostEqualRel(result1.to_float(), value)
                self.assertAlmostEqualRel(result2.to_float(), value)


if __name__ == "__main__":
    unittest.main()
