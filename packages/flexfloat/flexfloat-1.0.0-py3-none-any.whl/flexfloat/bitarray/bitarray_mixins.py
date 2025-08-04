"""Mixin classes providing common BitArray functionality.

This module provides mixins for BitArray implementations, offering default methods that
rely on the BitArray protocol. Bit order is always LSB-first.

Example:
    class MyBitArray(BitArrayCommonMixin):
        ... # implement BitArray protocol methods
    ba = MyBitArray.from_bits([True, False])
    print(list(ba))
    # Output: [True, False]
"""

from __future__ import annotations

import struct
from typing import Any, Iterable

from .bitarray import BitArray


class BitArrayCommonMixin(BitArray):
    """Mixin providing common methods that can be implemented using the BitArray
    protocol.

    Bit order: LSB-first (least significant bit at index 0, increasing to MSB).

    This mixin provides default implementations for methods that can be expressed in
    terms of the core BitArray protocol methods (__iter__, __len__, etc.).

    Classes using this mixin must implement the BitArray protocol.
    """

    @classmethod
    def from_float(cls, value: float) -> BitArray:
        """Create a BitArray from a float value."""
        packed = struct.pack("<d", value)
        bits = [bool((byte >> bit) & 1) for byte in packed for bit in range(8)]
        return cls.from_bits(bits)

    @classmethod
    def from_signed_int(cls, value: int, length: int) -> BitArray:
        """Create a BitArray from a signed integer value."""
        half = 1 << (length - 1)
        max_value = half - 1
        min_value = -half

        assert (
            min_value <= value <= max_value
        ), "Value out of range for specified length."

        unsigned_value = value + half
        bits = [(unsigned_value >> i) & 1 == 1 for i in range(length)]
        return cls.from_bits(bits)

    @classmethod
    def parse_bitarray(cls, bitstring: Iterable[str]) -> BitArray:
        """Parses a string of bits (with optional spaces) into a BitArray instance."""
        return cls.from_bits([c == "1" for c in bitstring if c in "01"])

    def __str__(self) -> str:
        """Returns a string representation of the bits (LSB-first, index 0 is
        rightmost).

        Returns:
            str: String representation of the bits.
        """
        return "".join("1" if bit else "0" for bit in reversed(list(self)))

    def __eq__(self, other: Any) -> bool:
        """Checks equality with another BitArray or list.

        Args:
            other (Any): The object to compare with.

        Returns:
            bool: True if equal, False otherwise.
        """
        if hasattr(other, "__iter__") and hasattr(other, "__len__"):
            if len(self) != len(other):  # type: ignore
                return False
            return all(a == b for a, b in zip(self, other))  # type: ignore
        return False

    def __bool__(self) -> bool:
        """Returns True if any bit is set.

        Returns:
            bool: True if any bit is set, False otherwise.
        """
        return self.any()

    def any(self) -> bool:
        """Returns True if any bit is set to True.

        Returns:
            bool: True if any bit is set to True, False otherwise.
        """
        return any(self)

    def all(self) -> bool:
        """Returns True if all bits are set to True.

        Returns:
            bool: True if all bits are set to True, False otherwise.
        """
        return all(self)

    def count(self, value: bool = True) -> int:
        """Counts the number of bits set to the specified value.

        Args:
            value (bool, optional): The value to count. Defaults to True.

        Returns:
            int: The number of bits set to the specified value.
        """
        return sum(1 for bit in self if bit == value)

    def reverse(self) -> BitArray:
        """Returns a new BitArray with the bits in reverse order."""
        return self.from_bits(list(reversed(self)))

    def to_signed_int(self) -> int:
        """Converts a bit array into a signed integer using off-set binary
        representation.

        Returns:
            int: The signed integer represented by the bit array.

        Raises:
            AssertionError: If the bit array is empty.
        """
        assert len(self) > 0, "Bit array must not be empty."

        int_value: int = self.to_int()
        # Half of the maximum value
        bias = 1 << (len(self) - 1)
        # Subtract the bias to get the signed value
        return int_value - bias

    def shift(self, shift_amount: int, fill: bool = False) -> BitArray:
        """Shifts the bit array left or right by a specified number of bits."""
        if shift_amount == 0:
            return self.copy()

        bits = list(self)

        if abs(shift_amount) > len(bits):
            new_bits = [fill] * len(bits)
        elif shift_amount > 0:  # Right shift
            new_bits = bits[shift_amount:] + [fill] * shift_amount
        else:  # Left shift
            new_bits = [fill] * (-shift_amount) + bits[:shift_amount]

        return self.from_bits(new_bits)
