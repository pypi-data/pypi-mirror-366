"""Tests for FlexFloat string representation (__str__ method)."""

import math
import unittest

from flexfloat import FlexFloat, ListBoolBitArray
from tests import FlexFloatTestCase


class TestStrRepresentation(FlexFloatTestCase):
    """Test FlexFloat string representation operations."""

    def test_str_zero_returns_correct_format(self):
        """Test that zero is represented as '0.0'."""
        ff = FlexFloat.from_float(0.0)
        expected = f"{0.0:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_negative_zero_returns_correct_format(self):
        """Test that negative zero is represented as '0.0'."""
        ff = FlexFloat.from_float(-0.0)
        expected = f"{-0.0:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_one_returns_correct_format(self):
        """Test that 1.0 is represented correctly."""
        ff = FlexFloat.from_float(1.0)
        expected = f"{1.0:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_negative_one_returns_correct_format(self):
        """Test that -1.0 is represented correctly."""
        ff = FlexFloat.from_float(-1.0)
        expected = f"{-1.0:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_small_decimal_returns_correct_format(self):
        """Test that small decimal numbers are represented correctly."""
        ff = FlexFloat.from_float(0.5)
        expected = f"{0.5:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(0.25)
        expected = f"{0.25:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(0.125)
        expected = f"{0.125:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_large_integers_returns_correct_format(self):
        """Test that large integers are represented correctly."""
        ff = FlexFloat.from_float(42.0)
        expected = f"{42.0:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(1000.0)
        expected = f"{1000.0:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(123456.0)
        expected = f"{123456.0:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_decimal_numbers_returns_correct_format(self):
        """Test that decimal numbers are represented correctly."""
        ff = FlexFloat.from_float(3.14159)
        expected = f"{3.14159:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(2.718281828)
        expected = f"{2.718281828:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_very_small_numbers_uses_scientific_notation(self):
        """Test that very small numbers use scientific notation."""
        ff = FlexFloat.from_float(1e-5)
        expected = f"{1e-5:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(1e-10)
        expected = f"{1e-10:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(1.23e-6)
        expected = f"{1.23e-6:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_very_large_numbers_uses_scientific_notation(self):
        """Test that very large numbers use scientific notation."""
        ff = FlexFloat.from_float(1e20)
        expected = f"{1e20:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(1.5e25)
        expected = f"{1.5e25:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_special_values(self):
        """Test that special values (NaN, Infinity) are represented correctly."""
        # Test NaN
        ff = FlexFloat.nan()
        self.assertEqual(str(ff), "nan")

        # Test positive infinity
        ff = FlexFloat.infinity(sign=False)
        self.assertEqual(str(ff), "inf")

        # Test negative infinity
        ff = FlexFloat.infinity(sign=True)
        self.assertEqual(str(ff), "-inf")

    def test_str_negative_numbers(self):
        """Test that negative numbers are represented correctly."""
        ff = FlexFloat.from_float(-3.14159)
        expected = f"{-3.14159:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(-42.0)
        expected = f"{-42.0:.5e}"
        self.assertEqual(str(ff), expected)

        ff = FlexFloat.from_float(-1e-5)
        expected = f"{-1e-5:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_edge_cases(self):
        """Test edge cases for string representation."""
        # Test minimum positive normalized number
        ff = FlexFloat.from_float(2.2250738585072014e-308)
        expected = f"{2.2250738585072014e-308:.5e}"
        self.assertEqual(str(ff), expected)

        # Test maximum finite number
        ff = FlexFloat.from_float(1.7976931348623157e308)
        expected = f"{1.7976931348623157e308:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_consistency_with_python_float(self):
        """Test that FlexFloat str() is consistent with Python float str()."""
        test_values = [
            0.0,
            1.0,
            -1.0,
            0.5,
            -0.5,
            3.14159,
            -3.14159,
            42.0,
            -42.0,
            1000.0,
            -1000.0,
            1e-5,
            -1e-5,
            1e-10,
            -1e-10,
            1e20,
            -1e20,
            1.5e25,
            -1.5e25,
            123.456789,
            -123.456789,
            0.000123456789,
            -0.000123456789,
        ]

        for value in test_values:
            with self.subTest(value=value):
                ff = FlexFloat.from_float(value)
                python_str = f"{value:.5e}"
                flexfloat_str = str(ff)
                self.assertEqual(
                    flexfloat_str,
                    python_str,
                    f"FlexFloat str({value}) = '{flexfloat_str}' != "
                    f"Python str({value}) = '{python_str}'",
                )

    def test_str_mathematical_constants(self):
        """Test string representation of mathematical constants."""
        # Test pi
        ff = FlexFloat.from_float(math.pi)
        expected = f"{math.pi:.5e}"
        self.assertEqual(str(ff), expected)

        # Test e
        ff = FlexFloat.from_float(math.e)
        expected = f"{math.e:.5e}"
        self.assertEqual(str(ff), expected)

        # Test sqrt(2)
        sqrt2 = math.sqrt(2)
        ff = FlexFloat.from_float(sqrt2)
        expected = f"{sqrt2:.5e}"
        self.assertEqual(str(ff), expected)

    def test_str_powers_of_two(self):
        """Test string representation of powers of two."""
        for i in range(-10, 11):
            value = 2.0**i
            with self.subTest(power=i, value=value):
                ff = FlexFloat.from_float(value)
                expected = f"{value:.5e}"
                self.assertEqual(str(ff), expected)

    def test_str_powers_of_ten(self):
        """Test string representation of powers of ten."""
        for i in range(-5, 6):
            value = 10.0**i
            with self.subTest(power=i, value=value):
                ff = FlexFloat.from_float(value)
                expected = f"{value:.5e}"
                self.assertEqual(str(ff), expected)

    def test_str_fractional_numbers(self):
        """Test string representation of various fractional numbers."""
        fractions = [
            1.0 / 3.0,  # 0.3333...
            1.0 / 7.0,  # 0.142857...
            22.0 / 7.0,  # approximation of pi
            355.0 / 113.0,  # better approximation of pi
        ]

        for value in fractions:
            with self.subTest(value=value):
                ff = FlexFloat.from_float(value)
                expected = f"{value:.5e}"
                self.assertEqual(str(ff), expected)

    def test_str_extended_exponent_numbers(self):
        """Test string representation of numbers with extended exponents."""
        # Test with large exponent
        extended_exp = ListBoolBitArray.from_signed_int(500, 12)  # 12-bit exponent
        frac = ListBoolBitArray.zeros(52)
        ff = FlexFloat(sign=False, exponent=extended_exp, fraction=frac)
        result = str(ff)
        # This represents 2^501, which in decimal scientific notation is ~6.54678e+150
        self.assertEqual(result, "6.54678e+150")

        # Test with negative large exponent
        extended_exp = ListBoolBitArray.from_signed_int(-500, 12)  # 12-bit exponent
        ff = FlexFloat(sign=False, exponent=extended_exp, fraction=frac)
        result = str(ff)
        # This represents 2^(-499), which in decimal scientific notation is 6.10987e-151
        self.assertEqual(result, "6.10987e-151")

        # Test with negative sign and extended exponent
        ff = FlexFloat(sign=True, exponent=extended_exp, fraction=frac)
        result = str(ff)
        self.assertEqual(result, "-6.10987e-151")

    def test_str_extreme_exponent_numbers(self):
        """Test string representation of numbers with extreme exponents."""
        # Test with very large exponent that causes overflow
        extended_exp = ListBoolBitArray.from_signed_int(2000, 15)  # 15-bit exponent
        frac = ListBoolBitArray.zeros(52)
        ff = FlexFloat(sign=False, exponent=extended_exp, fraction=frac)
        result = str(ff)
        # This represents 2^2001, which in decimal scientific notation is ~2.29626e+602
        self.assertTrue("e+" in result)
        self.assertIn("e+602", result)

    def test_str_extended_precision_arithmetic_results(self):
        """Test string representation after arithmetic with extended precision."""
        # Create very large numbers that will result in extended exponents
        ff1 = FlexFloat.from_float(1e150)
        ff2 = FlexFloat.from_float(1e150)

        # Multiplication should create a very large result
        result = ff1 * ff2
        result_str = str(result)

        # Should be in scientific notation
        self.assertTrue("e+" in result_str)
        # Should show approximately 1e300
        self.assertTrue(result_str.startswith("1.00000e+"))


if __name__ == "__main__":
    unittest.main()
