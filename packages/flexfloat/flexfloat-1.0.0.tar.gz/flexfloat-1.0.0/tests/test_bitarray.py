"""Tests for BitArray class and utility functions."""

import unittest

from flexfloat import ListBoolBitArray
from tests import FlexFloatTestCase


class TestBitArray(FlexFloatTestCase):
    """Test BitArray class and utility functions."""

    # === BitArray to Integer Conversion Tests ===
    def test_bitarray_to_int_converts_empty_array_to_zero(self):
        """Test that empty bit array converts to zero."""
        bit_array = ListBoolBitArray.from_bits([])
        expected = 0
        result = bit_array.to_int()
        self.assertEqual(result, expected)

    def test_bitarray_to_int_converts_all_false_to_zero(self):
        """Test that all False bits convert to zero."""
        bit_array = ListBoolBitArray.from_bits([False] * 64)
        expected = 0
        result = bit_array.to_int()
        self.assertEqual(result, expected)

    def test_bitarray_to_int_converts_single_bit_correctly(self):
        """Test that single True bit converts to 1."""
        bit_array = ListBoolBitArray.from_bits([True, False])
        expected = 1
        result = bit_array.to_int()
        self.assertEqual(result, expected)

    def test_bitarray_to_int_converts_multiple_bits_correctly(self):
        """Test conversion of multiple bit patterns."""
        # Test binary 101 (decimal 5)
        bit_array = ListBoolBitArray.from_bits([True, False, True])
        expected = 5
        result = bit_array.to_int()
        self.assertEqual(result, expected)

    def test_bitarray_to_int_converts_large_number_correctly(self):
        """Test conversion of large bit array to integer."""
        bit_array = ListBoolBitArray.parse_bitarray(
            reversed(
                "11111111 11111111 11111111 11111111"
                "11111111 11111111 11111111 11111001"
            )
        )
        expected = 18446744073709551609
        result = bit_array.to_int()
        self.assertEqual(result, expected)

    def test_bitarray_to_int_handles_leading_zeros(self):
        """Test that leading zeros don't affect the result."""
        bit_array1 = ListBoolBitArray.from_bits([True, False, True])  # 101 = 5
        bit_array2 = ListBoolBitArray.from_bits(
            [True, False, True, False, False]  # 00101 = 5
        )
        result1 = bit_array1.to_int()
        result2 = bit_array2.to_int()
        self.assertEqual(result1, result2)

    # === Signed Integer Conversion Tests ===
    def test_bitarray_to_signed_int_converts_zero_bias_correctly(self):
        """Test signed integer conversion with zero as negative bias."""
        bitarray = ListBoolBitArray.parse_bitarray("10000000000")  # 11-bit array
        expected = -1023  # -2^(11-1) + 1 = -1024 + 1
        result = bitarray.to_signed_int()
        self.assertEqual(result, expected)

    def test_bitarray_to_signed_int_converts_near_zero_correctly(self):
        """Test signed integer conversion near zero."""
        bitarray = ListBoolBitArray.parse_bitarray("11111111110")  # 11-bit array
        expected = -1  # -2^(11-1) + 1023 = -1024 + 1023
        result = bitarray.to_signed_int()
        self.assertEqual(result, expected)

    def test_bitarray_to_signed_int_converts_maximum_value_correctly(self):
        """Test signed integer conversion at maximum value."""
        bitarray = ListBoolBitArray.parse_bitarray("11111111111")  # 11-bit array
        expected = 1023  # -2^(11-1) + 2047 = -1024 + 2047
        result = bitarray.to_signed_int()
        self.assertEqual(result, expected)

    def test_bitarray_to_signed_int_raises_error_on_empty_array(self):
        """Test that assertion error is raised for empty bit array."""
        with self.assertRaises(AssertionError):
            ListBoolBitArray.from_bits([]).to_signed_int()

    def test_bitarray_to_signed_int_handles_different_lengths(self):
        """Test signed integer conversion with different bit array lengths."""
        # 8-bit test: bias = 2^7 = 128
        bitarray_8bit = ListBoolBitArray.parse_bitarray("00000001")  # 128 in unsigned
        expected_8bit = 0  # 128 - 128 = 0
        result_8bit = bitarray_8bit.to_signed_int()
        self.assertEqual(result_8bit, expected_8bit)

        # 4-bit test: bias = 2^3 = 8
        bitarray_4bit = ListBoolBitArray.parse_bitarray("0011")  # 12 in unsigned
        expected_4bit = 4  # 12 - 8 = 4
        result_4bit = bitarray_4bit.to_signed_int()
        self.assertEqual(result_4bit, expected_4bit)

    def test_signed_int_to_bitarray_converts_zero_correctly(self):
        """Test conversion of zero to signed bit array."""
        value = 0
        length = 8
        result = ListBoolBitArray.from_signed_int(value, length)
        # bias = 128, so 0 + 128 = 128
        expected = ListBoolBitArray.parse_bitarray("00000001")
        self.assertEqual(result, expected)

    def test_signed_int_to_bitarray_converts_positive_value_correctly(self):
        """Test conversion of positive value to signed bit array."""
        value = 5
        length = 8
        result = ListBoolBitArray.from_signed_int(value, length)

        expected = ListBoolBitArray.parse_bitarray("10100001")
        self.assertEqual(result, expected)

    def test_signed_int_to_bitarray_converts_negative_value_correctly(self):
        """Test conversion of negative value to signed bit array."""
        value = -5
        length = 8
        result = ListBoolBitArray.from_signed_int(value, length)
        # bias = 128, so -5 + 128 = 123
        expected = ListBoolBitArray.parse_bitarray("11011110")
        self.assertEqual(result, expected)

    def test_signed_int_to_bitarray_raises_error_on_overflow(self):
        """Test that assertion error is raised when value exceeds range."""
        # For 8-bit: max_value = (1 << 7) - 1 = 127, min_value = -(1 << 7) = -128
        # So range is -128 to 255

        # Test values within range should work
        try:
            ListBoolBitArray.from_signed_int(127, 8)
            ListBoolBitArray.from_signed_int(-128, 8)
        except AssertionError:
            self.fail("Valid values should not raise AssertionError")

        # Test values that should definitely fail
        with self.assertRaises(AssertionError):
            ListBoolBitArray.from_signed_int(256, 8)  # Beyond max range
        with self.assertRaises(AssertionError):
            ListBoolBitArray.from_signed_int(-129, 8)  # Beyond min range

    def test_signed_int_to_bitarray_roundtrip_preserves_value(self):
        """Test that signed int->bitarray->signed int preserves the original value."""
        length = 8
        test_values = [0, 1, -1, 127, -128, 50, -75]
        for value in test_values:
            bit_array = ListBoolBitArray.from_signed_int(value, length)
            result = bit_array.to_signed_int()
            self.assertEqual(result, value, f"Roundtrip failed for {value}")

    # === Bit Array Shifting Tests ===
    def test_shift_bitarray_no_shift_returns_original(self):
        """Test that zero shift returns the original array."""
        bit_array = [True, False, True, False]
        result = ListBoolBitArray.from_bits(bit_array).shift(0)
        self.assertEqual(result, ListBoolBitArray.from_bits(bit_array))

    def test_shift_bitarray_left_shift_with_default_fill(self):
        """Test left shift with default False fill."""
        bit_array = [True, False, True, False]
        result = ListBoolBitArray.from_bits(bit_array).shift(-2)
        expected = ListBoolBitArray.from_bits([False, False, True, False])
        self.assertEqual(result, expected)

    def test_shift_bitarray_left_shift_with_true_fill(self):
        """Test left shift with True fill value."""
        bit_array = [True, False, True, False]
        result = ListBoolBitArray.from_bits(bit_array).shift(-2, fill=True)
        expected = ListBoolBitArray.from_bits([True, True, True, False])
        self.assertEqual(result, expected)

    def test_shift_bitarray_right_shift_with_default_fill(self):
        """Test right shift with default False fill."""
        bit_array = [True, False, True, False]
        result = ListBoolBitArray.from_bits(bit_array).shift(2)
        expected = ListBoolBitArray.from_bits([True, False, False, False])
        self.assertEqual(result, expected)

    def test_shift_bitarray_right_shift_with_true_fill(self):
        """Test right shift with True fill value."""
        bit_array = [True, False, True, False]
        result = ListBoolBitArray.from_bits(bit_array).shift(2, fill=True)
        expected = ListBoolBitArray.from_bits([True, False, True, True])
        self.assertEqual(result, expected)

    def test_shift_bitarray_shift_entire_length(self):
        """Test shifting by the entire length of the array."""
        bit_array = [True, False, True, False]
        # Left shift by entire length
        result_left = ListBoolBitArray.from_bits(bit_array).shift(-4)
        expected_left = ListBoolBitArray.from_bits([False, False, False, False])
        self.assertEqual(result_left, expected_left)

        # Right shift by entire length
        result_right = ListBoolBitArray.from_bits(bit_array).shift(4)
        expected_right = ListBoolBitArray.from_bits([False, False, False, False])
        self.assertEqual(result_right, expected_right)

    def test_shift_bitarray_shift_beyond_length(self):
        """Test shifting beyond the array length."""
        bit_array = [True, False, True, False]
        result = ListBoolBitArray.from_bits(bit_array).shift(-5)
        expected = ListBoolBitArray.from_bits([False] * len(bit_array))
        self.assertEqual(result, expected)

    def test_shift_bitarray_preserves_array_length(self):
        """Test that shifting preserves array length for reasonable shifts."""
        bit_array = [True, False, True, False, True]
        shifts = [0, 1, -1, 3, -3]
        for shift in shifts:
            result = ListBoolBitArray.from_bits(bit_array).shift(shift)
            self.assertEqual(
                len(result),
                len(bit_array),
                f"Length not preserved for shift {shift}",
            )

    # === BitArray Class Method Tests ===
    def test_bitarray_shift_method_works_correctly(self):
        """Test that BitArray.shift method works correctly."""
        bit_array = ListBoolBitArray.from_bits([True, False, True, False])

        # Test no shift
        result = bit_array.shift(0)
        self.assertEqual(result, bit_array)

        # Test left shift
        result = bit_array.shift(-2)
        expected = ListBoolBitArray.from_bits([False, False, True, False])
        self.assertEqual(result, expected)

        # Test right shift
        result = bit_array.shift(2)
        expected = ListBoolBitArray.from_bits([True, False, False, False])
        self.assertEqual(result, expected)

    def test_bitarray_from_signed_int_class_method(self):
        """Test BitArray.from_signed_int class method."""
        value = 5
        length = 8
        result = ListBoolBitArray.from_signed_int(value, length)
        expected = ListBoolBitArray.parse_bitarray("10100001")
        self.assertEqual(result, expected)

    def test_bitarray_factory_methods(self):
        """Test BitArray factory methods."""
        # Test zeros
        zeros = ListBoolBitArray.zeros(5)
        self.assertEqual(zeros, ListBoolBitArray.from_bits([False] * 5))

        # Test ones
        ones = ListBoolBitArray.ones(5)
        self.assertEqual(ones, ListBoolBitArray.from_bits([True] * 5))

    def test_bitarray_utility_methods(self):
        """Test BitArray utility methods."""
        bit_array = ListBoolBitArray.from_bits([True, False, True, True, False])

        # Test any
        self.assertTrue(bit_array.any())

        # Test all
        self.assertFalse(bit_array.all())

        # Test count
        self.assertEqual(bit_array.count(True), 3)
        self.assertEqual(bit_array.count(False), 2)

        # Test copy
        copy = bit_array.copy()
        self.assertEqual(copy, bit_array)
        self.assertIsNot(copy, bit_array)


if __name__ == "__main__":
    unittest.main()
