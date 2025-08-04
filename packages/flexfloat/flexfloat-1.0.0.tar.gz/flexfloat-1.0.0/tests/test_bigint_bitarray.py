"""Tests specifically for the BigIntBitArray implementation."""

import unittest
from typing import Type

from flexfloat import BigIntBitArray
from tests import FlexFloatTestCase


class TestBigIntBitArray(FlexFloatTestCase):
    """Test the BigIntBitArray implementation."""

    def setUp(self):
        """Set up test fixtures."""
        self.impl_class: Type[BigIntBitArray] = BigIntBitArray

    def test_empty_initialization(self):
        """Test empty initialization."""
        ba = self.impl_class.from_bits()
        self.assertEqual(len(ba), 0)
        self.assertEqual(list(ba), [])
        self.assertEqual(ba.to_int(), 0)

    def test_basic_initialization(self):
        """Test basic initialization with bits."""
        bits = [True, False, True, False]
        ba = self.impl_class.from_bits(bits)
        self.assertEqual(len(ba), 4)
        self.assertEqual(list(ba), bits)

    def test_zeros_creation(self):
        """Test creating arrays filled with zeros."""
        for length in [0, 1, 8, 64, 100, 1000]:
            with self.subTest(length=length):
                ba = self.impl_class.zeros(length)
                self.assertEqual(len(ba), length)
                self.assertEqual(list(ba), [False] * length)
                self.assertEqual(ba.to_int(), 0)

    def test_ones_creation(self):
        """Test creating arrays filled with ones."""
        for length in [0, 1, 8, 64, 100, 1000]:
            with self.subTest(length=length):
                ba = self.impl_class.ones(length)
                self.assertEqual(len(ba), length)
                self.assertEqual(list(ba), [True] * length)
                expected_value = (1 << length) - 1
                self.assertEqual(ba.to_int(), expected_value)

    def test_parse_bitarray(self):
        """Test parsing bit strings."""
        test_cases: list[tuple[str, list[bool]]] = [
            ("", []),
            ("0", [False]),
            ("1", [True]),
            ("101", [True, False, True]),
            ("1010 1100", [True, False, True, False, True, True, False, False]),
            ("10 10 11 00", [True, False, True, False, True, True, False, False]),
        ]

        for bitstring, expected in test_cases:
            with self.subTest(bitstring=bitstring):
                ba = self.impl_class.parse_bitarray(bitstring)
                self.assertEqual(list(ba), expected)

    def test_get_set_bit(self):
        """Test getting and setting individual bits."""
        ba = self.impl_class.zeros(10)

        # Test setting bits using indexing (public interface)
        ba[0] = True
        ba[5] = True
        ba[9] = True

        # Test getting bits using indexing (public interface)
        expected = [True, False, False, False, False, True, False, False, False, True]
        for i, expected_bit in enumerate(expected):
            self.assertEqual(ba[i], expected_bit)

        # Test setting bit to False
        ba[5] = False
        self.assertFalse(ba[5])

    def test_indexing(self):
        """Test indexing operations."""
        bits = [True, False, True, False, True]
        ba = self.impl_class.from_bits(bits)

        # Test getting individual bits
        for i, expected in enumerate(bits):
            self.assertEqual(ba[i], expected)

        # Test setting individual bits
        ba[1] = True
        self.assertTrue(ba[1])
        ba[4] = False
        self.assertFalse(ba[4])

    def test_slicing(self):
        """Test slicing operations."""
        bits = [True, False, True, False, True, True, False, False]
        ba = self.impl_class.from_bits(bits)

        # Test slice getting
        slice_result = ba[2:6]
        expected_slice = [True, False, True, True]
        self.assertEqual(list(slice_result), expected_slice)

        # Test slice setting
        ba[2:6] = [False, True, False, False]
        expected_after = [True, False, False, True, False, False, False, False]
        self.assertEqual(list(ba), expected_after)

    def test_slice_with_step(self):
        """Test slicing with step."""
        bits = [True, False, True, False, True, True, False, False]
        ba = self.impl_class.from_bits(bits)

        # Test slice getting with step
        slice_result = ba[::2]  # Every other bit
        expected_slice = [True, True, True, False]
        self.assertEqual(list(slice_result), expected_slice)

        # Test slice setting with step
        ba[::2] = [False, False, False, True]
        expected_after = [False, False, False, False, False, True, True, False]
        self.assertEqual(list(ba), expected_after)

    def test_to_int(self):
        """Test conversion to integer."""
        test_cases: list[tuple[list[bool], int]] = [
            ([], 0),
            ([False], 0),
            ([True], 1),
            ([True, False], 1),
            ([True, True], 3),
            ([True, False, True], 5),
            ([True, False, True, False], 5),
        ]

        for bits, expected_int in test_cases:
            with self.subTest(bits=bits):
                ba = self.impl_class.from_bits(bits)
                self.assertEqual(ba.to_int(), expected_int)

    def test_to_signed_int(self):
        """Test conversion to signed integer."""
        # Test with various bit lengths using offset binary representation
        test_cases: list[tuple[list[bool], int]] = [
            ([True], 0),  # 1-bit: 1 -> 1 - 1 = 0
            ([False], -1),  # 1-bit: 0 -> 0 - 1 = -1
            ([True, False], -1),  # 2-bit: 01 (LSB-first) -> 1 - 2 = -1
            ([False, True], 0),  # 2-bit: 10 (LSB-first) -> 2 - 2 = 0
            ([False, False], -2),  # 2-bit: 00 -> 0 - 2 = -2
            ([True, True], 1),  # 2-bit: 11 -> 3 - 2 = 1
        ]

        for bits, expected_signed in test_cases:
            with self.subTest(bits=bits):
                ba = self.impl_class.from_bits(bits)
                self.assertEqual(ba.to_signed_int(), expected_signed)

    def test_from_signed_int(self):
        """Test creation from signed integer."""
        test_cases: list[tuple[int, int, list[bool]]] = [
            (0, 4, [False, False, False, True]),  # 0 -> 8 -> [0,0,0,1] (LSB-first)
            (-1, 4, [True, True, True, False]),  # -1 -> 7 -> [1,1,1,0] (LSB-first)
            (1, 4, [True, False, False, True]),  # 1 -> 9 -> [1,0,0,1] (LSB-first)
            (-8, 4, [False, False, False, False]),  # -8 -> 0 -> [0,0,0,0] (minimum)
            (7, 4, [True, True, True, True]),  # 7 -> 15 -> [1,1,1,1] (maximum)
        ]

        for value, length, expected_bits in test_cases:
            with self.subTest(value=value, length=length):
                ba = self.impl_class.from_signed_int(value, length)
                self.assertEqual(list(ba), expected_bits)
                # Verify round-trip
                self.assertEqual(ba.to_signed_int(), value)

    def test_to_float(self):
        """Test conversion to float for 64-bit arrays."""
        # Test with known float values
        test_values = [
            0.0,
            1.0,
            -1.0,
            3.14159,
            -2.718281828,
            float("inf"),
            -float("inf"),
        ]

        for value in test_values:
            with self.subTest(value=value):
                ba = self.impl_class.from_float(value)
                self.assertEqual(len(ba), 64)
                recovered = ba.to_float()
                self.assertEqual(recovered, value)

    def test_from_float(self):
        """Test creation from float."""
        ba = self.impl_class.from_float(1.0)
        self.assertEqual(len(ba), 64)
        # Verify it's a valid IEEE 754 representation
        self.assertEqual(ba.to_float(), 1.0)

    def test_shift_operations(self):
        """Test bit shifting operations."""
        bits = [True, False, True, False]  # In LSB-first: 1010 = 5 (1 + 4)
        ba = self.impl_class.from_bits(bits)

        # Test right shift (positive shift_amount)
        right_shifted = ba.shift(1)
        expected_right = [False, True, False, False]  # Right shift: 5 >> 1 = 2
        self.assertEqual(list(right_shifted), expected_right)

        # Test left shift (negative shift_amount)
        left_shifted = ba.shift(-1)
        expected_left = [False, True, False, True]  # Left shift: 5 << 1 = 10
        self.assertEqual(list(left_shifted), expected_left)

        # Test right shift with fill=True (positive shift_amount)
        right_fill = ba.shift(1, fill=True)
        expected_right_fill = [False, True, False, True]  # Right shift with fill=True
        self.assertEqual(list(right_fill), expected_right_fill)

        # Test left shift with fill=True (negative shift_amount)
        left_fill = ba.shift(-1, fill=True)
        expected_left_fill = [True, True, False, True]  # Left shift with fill=True
        self.assertEqual(list(left_fill), expected_left_fill)

    def test_copy(self):
        """Test copying bit arrays."""
        bits = [True, False, True, False]
        ba = self.impl_class.from_bits(bits)
        copy_ba = ba.copy()

        self.assertEqual(list(ba), list(copy_ba))
        self.assertIsNot(ba, copy_ba)

        # Modify original to ensure independence
        ba[0] = False
        self.assertNotEqual(list(ba), list(copy_ba))

    def test_iteration(self):
        """Test iteration over bit array."""
        bits = [True, False, True, False]
        ba = self.impl_class.from_bits(bits)

        iterated_bits = list(ba)
        self.assertEqual(iterated_bits, bits)

    def test_concatenation(self):
        """Test concatenation operations."""
        ba1 = self.impl_class.from_bits([True, False])
        ba2 = self.impl_class.from_bits([True, True])

        # Test __add__
        result = ba1 + ba2
        expected = [True, False, True, True]
        self.assertEqual(list(result), expected)

        # Test __radd__ with list
        result2 = [False, False] + ba1
        expected2 = [False, False, True, False]
        self.assertEqual(list(result2), expected2)

    def test_equality(self):
        """Test equality comparison."""
        ba1 = self.impl_class.from_bits([True, False, True])
        ba2 = self.impl_class.from_bits([True, False, True])
        ba3 = self.impl_class.from_bits([False, True, False])

        self.assertEqual(ba1, ba2)
        self.assertNotEqual(ba1, ba3)
        self.assertEqual(ba1, [True, False, True])
        self.assertNotEqual(ba1, [False, True, False])

    def test_boolean_operations(self):
        """Test boolean operations."""
        empty_ba = self.impl_class.from_bits([])
        zeros_ba = self.impl_class.zeros(5)
        ones_ba = self.impl_class.ones(5)
        mixed_ba = self.impl_class.from_bits([True, False, False, True, False])

        # Test __bool__
        self.assertFalse(bool(empty_ba))
        self.assertFalse(bool(zeros_ba))
        self.assertTrue(bool(ones_ba))
        self.assertTrue(bool(mixed_ba))

        # Test any
        self.assertFalse(empty_ba.any())
        self.assertFalse(zeros_ba.any())
        self.assertTrue(ones_ba.any())
        self.assertTrue(mixed_ba.any())

        # Test all
        self.assertTrue(empty_ba.all())  # Vacuously true
        self.assertFalse(zeros_ba.all())
        self.assertTrue(ones_ba.all())
        self.assertFalse(mixed_ba.all())

    def test_count(self):
        """Test counting bits."""
        ba = self.impl_class.from_bits([True, False, True, True, False])

        self.assertEqual(ba.count(True), 3)
        self.assertEqual(ba.count(False), 2)
        self.assertEqual(ba.count(), 3)  # Default is True

    def test_reverse(self):
        """Test reversing bit arrays."""
        bits = [True, False, True, False]
        ba = self.impl_class.from_bits(bits)
        reversed_ba = ba.reverse()

        expected = [False, True, False, True]
        self.assertEqual(list(reversed_ba), expected)

    def test_repr_and_str(self):
        """Test string representations."""
        bits = [True, False, True]
        ba = self.impl_class.from_bits(bits)

        # Test __str__
        self.assertEqual(str(ba), "101")

        # Test __repr__
        expected_repr = "BigIntBitArray([True, False, True])"
        self.assertEqual(repr(ba), expected_repr)

    def test_large_arrays(self):
        """Test with large bit arrays to verify infinite size capability."""
        # Test with arrays larger than typical fixed-size implementations
        large_size = 10000

        # Test large zeros array
        ba_zeros = self.impl_class.zeros(large_size)
        self.assertEqual(len(ba_zeros), large_size)
        self.assertEqual(ba_zeros.to_int(), 0)

        # Test large ones array
        ba_ones = self.impl_class.ones(large_size)
        self.assertEqual(len(ba_ones), large_size)
        expected_value = (1 << large_size) - 1
        self.assertEqual(ba_ones.to_int(), expected_value)

        # Test setting bits in large array
        ba_sparse = self.impl_class.zeros(large_size)
        ba_sparse[0] = True
        ba_sparse[large_size - 1] = True
        ba_sparse[large_size // 2] = True

        self.assertTrue(ba_sparse[0])
        self.assertTrue(ba_sparse[large_size - 1])
        self.assertTrue(ba_sparse[large_size // 2])
        self.assertEqual(ba_sparse.count(True), 3)

    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        ba = self.impl_class.from_bits([True, False, True])

        # Test index out of range
        with self.assertRaises(IndexError):
            _ = ba[5]

        with self.assertRaises(IndexError):
            _ = ba[-5]

        with self.assertRaises(IndexError):
            ba[5] = True

        # Test to_float with wrong size
        with self.assertRaises(AssertionError):
            ba.to_float()

        # Test to_signed_int with empty array
        empty_ba = self.impl_class.from_bits([])
        with self.assertRaises(AssertionError):
            empty_ba.to_signed_int()

    def test_memory_efficiency_indicators(self):
        """Test indicators that the implementation is memory efficient."""
        # Create a large bit array and verify basic operations work
        # This is more of a smoke test for memory efficiency
        large_size = 100000
        ba = self.impl_class.zeros(large_size)

        # Should be able to set bits efficiently
        ba[0] = True
        ba[large_size - 1] = True

        # Should be able to count efficiently
        self.assertEqual(ba.count(True), 2)

        # Should be able to convert to int (this tests that Python's
        # arbitrary precision int is working)
        expected_value = 1 << (large_size - 1) | 1
        self.assertEqual(ba.to_int(), expected_value)


if __name__ == "__main__":
    unittest.main()
