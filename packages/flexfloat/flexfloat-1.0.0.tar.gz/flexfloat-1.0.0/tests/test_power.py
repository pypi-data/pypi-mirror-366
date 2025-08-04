"""Tests for FlexFloat power and exponential operations."""

import math
import unittest

from flexfloat import FlexFloat, ListBoolBitArray
from flexfloat import math as ffmath
from tests import FlexFloatTestCase


class TestPower(FlexFloatTestCase):
    """Test FlexFloat power operations."""

    def test_flexfloat_power_with_zero_base_and_positive_exponent_returns_zero(self):
        """Test that 0^n returns zero for positive n."""
        base = FlexFloat.from_float(0.0)
        exponent = FlexFloat.from_float(2.0)
        result = base**exponent
        expected = 0.0**2.0
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_with_zero_base_and_zero_exponent_returns_one(self):
        """Test that 0^0 returns 1."""
        base = FlexFloat.from_float(0.0)
        exponent = FlexFloat.from_float(0.0)
        result = base**exponent
        expected = 0.0**0.0
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_with_zero_base_and_negative_exponent_returns_infinity(
        self,
    ):
        """Test that 0^(-n) returns infinity for positive n."""
        base = FlexFloat.from_float(0.0)
        exponent = FlexFloat.from_float(-2.0)
        result = base**exponent
        self.assertTrue(result.is_infinity())

    def test_flexfloat_power_with_one_base_returns_one(self):
        """Test that 1^n returns 1 for any n."""
        base = FlexFloat.from_float(1.0)
        test_exponents = [0.0, 1.0, 2.0, -1.0, 0.5, -2.5]
        for exp_val in test_exponents:
            with self.subTest(exponent=exp_val):
                exponent = FlexFloat.from_float(exp_val)
                result = base**exponent
                expected = 1.0**exp_val
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_with_zero_exponent_returns_one(self):
        """Test that n^0 returns 1 for any non-zero n."""
        test_bases = [2.0, -2.0, 0.5, -0.5, 10.0, 1e10, 1e-10]
        exponent = FlexFloat.from_float(0.0)
        for base_val in test_bases:
            with self.subTest(base=base_val):
                base = FlexFloat.from_float(base_val)
                result = base**exponent
                expected = base_val**0.0
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_with_one_exponent_returns_base(self):
        """Test that n^1 returns n."""
        test_bases = [2.0, -2.0, 0.5, -0.5, 10.0, 1e10, 1e-10]
        exponent = FlexFloat.from_float(1.0)
        for base_val in test_bases:
            with self.subTest(base=base_val):
                base = FlexFloat.from_float(base_val)
                result = base**exponent
                expected = base_val**1.0
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_simple_integer_exponents(self):
        """Test power operations with simple integer exponents."""
        test_cases = [
            (2.0, 2.0),  # 2^2 = 4
            (2.0, 3.0),  # 2^3 = 8
            (3.0, 2.0),  # 3^2 = 9
            (5.0, 2.0),  # 5^2 = 25
            (10.0, 2.0),  # 10^2 = 100
        ]
        for base_val, exp_val in test_cases:
            with self.subTest(base=base_val, exponent=exp_val):
                base = FlexFloat.from_float(base_val)
                exponent = FlexFloat.from_float(exp_val)
                result = base**exponent
                expected = base_val**exp_val
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_negative_integer_exponents(self):
        """Test power operations with negative integer exponents."""
        test_cases = [
            (2.0, -1.0),  # 2^-1 = 0.5
            (2.0, -2.0),  # 2^-2 = 0.25
            (4.0, -1.0),  # 4^-1 = 0.25
            (10.0, -1.0),  # 10^-1 = 0.1
        ]
        for base_val, exp_val in test_cases:
            with self.subTest(base=base_val, exponent=exp_val):
                base = FlexFloat.from_float(base_val)
                exponent = FlexFloat.from_float(exp_val)
                result = base**exponent
                expected = base_val**exp_val
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_fractional_exponents(self):
        """Test power operations with fractional exponents."""
        test_cases = [
            (4.0, 0.5),  # 4^0.5 = 2
            (9.0, 0.5),  # 9^0.5 = 3
            (8.0, 1.0 / 3.0),  # 8^(1/3) = 2
            (27.0, 1.0 / 3.0),  # 27^(1/3) = 3
            (16.0, 0.25),  # 16^0.25 = 2
        ]
        for base_val, exp_val in test_cases:
            with self.subTest(base=base_val, exponent=exp_val):
                base = FlexFloat.from_float(base_val)
                exponent = FlexFloat.from_float(exp_val)
                result = base**exponent
                expected = base_val**exp_val
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_negative_base_integer_exponents(self):
        """Test power operations with negative base and integer exponents."""
        test_cases = [
            (-2.0, 2.0),  # (-2)^2 = 4
            (-2.0, 3.0),  # (-2)^3 = -8
            (-3.0, 2.0),  # (-3)^2 = 9
            (-3.0, 3.0),  # (-3)^3 = -27
        ]
        for base_val, exp_val in test_cases:
            with self.subTest(base=base_val, exponent=exp_val):
                base = FlexFloat.from_float(base_val)
                exponent = FlexFloat.from_float(exp_val)
                result = base**exponent
                expected = base_val**exp_val
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_negative_base_fractional_exponents_returns_nan(self):
        """Test that negative base with fractional exponent returns NaN."""
        base = FlexFloat.from_float(-2.0)
        exponent = FlexFloat.from_float(0.5)
        result = base**exponent
        self.assertTrue(result.is_nan() or math.isnan(result.to_float()))

    def test_flexfloat_power_large_exponents(self):
        """Test power operations with large exponents."""
        test_cases = [
            (2.0, 10.0),  # 2^10 = 1024
            (10.0, 5.0),  # 10^5 = 100000
            (1.1, 20.0),  # 1.1^20
        ]
        for base_val, exp_val in test_cases:
            with self.subTest(base=base_val, exponent=exp_val):
                base = FlexFloat.from_float(base_val)
                exponent = FlexFloat.from_float(exp_val)
                result = base**exponent
                expected = base_val**exp_val
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_small_base_large_negative_exponents(self):
        """Test power operations with small base and large negative exponents."""
        test_cases = [
            (0.5, -10.0),  # 0.5^-10 = 1024
            (0.1, -5.0),  # 0.1^-5 = 100000
        ]
        for base_val, exp_val in test_cases:
            with self.subTest(base=base_val, exponent=exp_val):
                base = FlexFloat.from_float(base_val)
                exponent = FlexFloat.from_float(exp_val)
                result = base**exponent
                expected = base_val**exp_val
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_overflow_handling(self):
        """Test power operations that would cause overflow."""
        large_base = FlexFloat.from_float(10.0)
        large_exponent = FlexFloat.from_float(400.0)
        result = large_base**large_exponent

        # Should not be infinity due to extended precision
        self.assertFalse(result.is_infinity())
        # Should have extended exponent
        self.assertGreater(len(result.exponent), 11)

    def test_flexfloat_power_underflow_handling(self):
        """Test power operations that would cause underflow."""
        small_base = FlexFloat.from_float(0.1)
        large_exponent = FlexFloat.from_float(-400.0)
        result = small_base**large_exponent

        # Should not be zero due to extended precision
        self.assertFalse(result.is_zero())
        # Should have extended exponent
        self.assertGreater(len(result.exponent), 11)

    def test_flexfloat_power_handles_nan_operands(self):
        """Test power operations with NaN operands."""
        nan = FlexFloat.nan()
        normal = FlexFloat.from_float(2.0)

        result1 = nan**normal
        self.assertTrue(result1.is_nan())

        result2 = normal**nan
        self.assertTrue(result2.is_nan())

        result3 = nan**nan
        self.assertTrue(result3.is_nan())

    def test_flexfloat_power_handles_infinity_operands(self):
        """Test power operations with infinity operands."""
        inf = FlexFloat.infinity()
        neg_inf = FlexFloat.infinity(sign=True)
        normal = FlexFloat.from_float(2.0)
        negative = FlexFloat.from_float(-1.0)

        # inf^positive = inf
        result1 = inf**normal
        self.assertTrue(result1.is_infinity())
        self.assertFalse(result1.sign)

        # inf^negative = 0
        result2 = inf**negative
        self.assertTrue(result2.is_zero())

        # positive^inf = inf (for base > 1)
        result3 = normal**inf
        self.assertTrue(result3.is_infinity())

        # negative_inf^even = inf
        result4 = neg_inf ** FlexFloat.from_float(2.0)
        self.assertTrue(result4.is_infinity())

        # negative_inf^odd = -inf
        result5 = neg_inf ** FlexFloat.from_float(3.0)
        self.assertTrue(result5.is_infinity())
        self.assertTrue(result5.sign)

    def test_flexfloat_power_rejects_non_flexfloat_operands(self):
        """Test that power operations reject non-FlexFloat operands."""
        bf = FlexFloat.from_float(2.0)
        with self.assertRaises(TypeError):
            bf ** "not a number"  # type: ignore

    def test_flexfloat_power_with_mixed_operand_types(self):
        """Test power operations with mixed operand types."""
        bf = FlexFloat.from_float(2.0)

        # FlexFloat ** int
        result1 = bf**3
        self.assertAlmostEqualRel(result1.to_float(), 8.0)

        # FlexFloat ** float
        result2 = bf**0.5
        self.assertAlmostEqualRel(result2.to_float(), math.sqrt(2.0))

        # int ** FlexFloat
        result3 = 3**bf
        self.assertAlmostEqualRel(result3.to_float(), 9.0)

        # float ** FlexFloat
        result4 = 4.0**bf
        self.assertAlmostEqualRel(result4.to_float(), 16.0)

    def test_flexfloat_power_mathematical_identities(self):
        """Test mathematical identities for power operations."""
        # (a^b)^c = a^(b*c)
        a = FlexFloat.from_float(2.0)
        b = FlexFloat.from_float(3.0)
        c = FlexFloat.from_float(2.0)

        left = (a**b) ** c
        right = a ** (b * c)
        self.assertAlmostEqualRel(left.to_float(), right.to_float())

        # a^b * a^c = a^(b+c)
        a = FlexFloat.from_float(3.0)
        b = FlexFloat.from_float(2.0)
        c = FlexFloat.from_float(3.0)

        left = (a**b) * (a**c)
        right = a ** (b + c)
        self.assertAlmostEqualRel(left.to_float(), right.to_float())

    def test_flexfloat_power_edge_precision_cases(self):
        """Test power operations with edge precision cases."""
        # Very close to 1
        base = FlexFloat.from_float(1.0000000000000002)
        exponent = FlexFloat.from_float(1000000.0)
        result = base**exponent
        expected = 1.0000000000000002**1000000.0

        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_powers_of_two(self):
        """Test power operations with powers of two."""
        test_cases = [
            (2.0, 1.0),
            (2.0, 2.0),
            (2.0, 3.0),
            (2.0, 4.0),
            (2.0, 5.0),
            (2.0, -1.0),
            (2.0, -2.0),
        ]
        for base_val, exp_val in test_cases:
            with self.subTest(base=base_val, exponent=exp_val):
                base = FlexFloat.from_float(base_val)
                exponent = FlexFloat.from_float(exp_val)
                result = base**exponent
                expected = base_val**exp_val
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_powers_of_ten(self):
        """Test power operations with powers of ten."""
        test_cases = [
            (10.0, 1.0),
            (10.0, 2.0),
            (10.0, 3.0),
            (10.0, -1.0),
            (10.0, -2.0),
        ]
        for base_val, exp_val in test_cases:
            with self.subTest(base=base_val, exponent=exp_val):
                base = FlexFloat.from_float(base_val)
                exponent = FlexFloat.from_float(exp_val)
                result = base**exponent
                expected = base_val**exp_val
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_mathematical_constants(self):
        """Test power operations with mathematical constants."""
        # e^2
        base = FlexFloat.from_float(math.e)
        exponent = FlexFloat.from_float(2.0)
        result = base**exponent
        expected = math.e**2.0
        self.assertAlmostEqualRel(result.to_float(), expected)

        # π^2
        base = FlexFloat.from_float(math.pi)
        exponent = FlexFloat.from_float(2.0)
        result = base**exponent
        expected = math.pi**2.0
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_power_extreme_exponent_ranges(self):
        """Test power operations with extreme exponent ranges."""
        # Create FlexFloat with large exponent
        large_exp = ListBoolBitArray.from_signed_int(1000, 15)
        base = FlexFloat(
            sign=False, exponent=large_exp, fraction=ListBoolBitArray.zeros(52)
        )
        exponent = FlexFloat.from_float(2000.0)
        result = base**exponent

        # Should handle extreme ranges without overflow to infinity
        self.assertFalse(result.is_infinity())
        self.assertGreater(len(result.exponent), len(base.exponent))

    def test_flexfloat_power_denormalized_numbers(self):
        """Test power operations with denormalized numbers."""
        tiny = FlexFloat.from_float(1e-200)
        exponent = FlexFloat.from_float(2.0)
        result = tiny**exponent

        self.assertGreater(len(result.exponent), 11)


class TestExponential(FlexFloatTestCase):
    """Test FlexFloat exponential operations."""

    def test_flexfloat_exp_zero_returns_one(self):
        """Test that exp(0) returns 1."""
        zero = FlexFloat.from_float(0.0)
        result = ffmath.exp(zero)
        expected = math.exp(0.0)
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_exp_one_returns_e(self):
        """Test that exp(1) returns e."""
        one = FlexFloat.from_float(1.0)
        result = ffmath.exp(one)
        expected = math.exp(1.0)
        self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_exp_simple_values(self):
        """Test exp with simple values."""
        test_cases = [0.5, 1.0, 2.0, -1.0, -0.5]
        for val in test_cases:
            with self.subTest(value=val):
                ff = FlexFloat.from_float(val)
                result = ffmath.exp(ff)
                expected = math.exp(val)
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_exp_large_positive_values(self):
        """Test exp with large positive values."""
        test_cases = [5.0, 10.0, 20.0]
        for val in test_cases:
            with self.subTest(value=val):
                ff = FlexFloat.from_float(val)
                result = ffmath.exp(ff)
                expected = math.exp(val)
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_exp_large_negative_values(self):
        """Test exp with large negative values."""
        test_cases = [-5.0, -10.0, -20.0]
        for val in test_cases:
            with self.subTest(value=val):
                ff = FlexFloat.from_float(val)
                result = ffmath.exp(ff)
                expected = math.exp(val)
                self.assertAlmostEqualRel(result.to_float(), expected)

    def test_flexfloat_exp_handles_nan(self):
        """Test that exp(NaN) returns NaN."""
        nan = FlexFloat.nan()
        result = ffmath.exp(nan)
        self.assertTrue(result.is_nan())

    def test_flexfloat_exp_handles_infinity(self):
        """Test exp with infinity operands."""
        # exp(+inf) = +inf
        pos_inf = FlexFloat.infinity()
        result1 = ffmath.exp(pos_inf)
        self.assertTrue(result1.is_infinity())
        self.assertFalse(result1.sign)

        # exp(-inf) = 0
        neg_inf = FlexFloat.infinity(sign=True)
        result2 = ffmath.exp(neg_inf)
        self.assertTrue(result2.is_zero())

    def test_flexfloat_exp_mathematical_constants(self):
        """Test exp with mathematical constants."""
        # exp(ln(2)) = 2
        ln2 = FlexFloat.from_float(math.log(2.0))
        result = ffmath.exp(ln2)
        self.assertAlmostEqualRel(result.to_float(), 2.0)

        # exp(ln(10)) = 10
        ln10 = FlexFloat.from_float(math.log(10.0))
        result = ffmath.exp(ln10)
        self.assertAlmostEqualRel(result.to_float(), 10.0)

    def test_flexfloat_exp_extreme_precision(self):
        """Test exp with extreme precision cases."""
        # Very small values near zero
        tiny = FlexFloat.from_float(1e-15)
        result = ffmath.exp(tiny)
        expected = math.exp(1e-15)
        self.assertAlmostEqualRel(result.to_float(), expected)

        # Test that exp maintains high precision
        val = FlexFloat.from_float(0.123456789)
        result = ffmath.exp(val)
        expected = math.exp(0.123456789)
        self.assertAlmostEqualRel(result.to_float(), expected)


if __name__ == "__main__":
    unittest.main()
