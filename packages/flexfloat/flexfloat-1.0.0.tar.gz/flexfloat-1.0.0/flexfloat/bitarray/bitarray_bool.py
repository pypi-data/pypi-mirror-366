"""List-based BitArray implementation for the flexfloat package.

This implementation is best for small or dynamically sized bit arrays.
Bit order: LSB-first (least significant bit at index 0, increasing to MSB).

Example:
    from flexfloat.bitarray import ListBoolBitArray
    ba = ListBoolBitArray([True, False, True])
    print(list(ba))
    # Output: [True, False, True]
"""

from __future__ import annotations

import struct
from typing import Iterator, overload

from .bitarray import BitArray
from .bitarray_mixins import BitArrayCommonMixin


class ListBoolBitArray(BitArrayCommonMixin):
    """A bit array class that encapsulates a list of booleans with utility methods.

    This implementation uses a list of boolean values to represent the bits,
    allowing for dynamic resizing and easy manipulation of individual bits.
    """

    def __init__(self, bits: list[bool] | None = None):
        """Initializes a ListBoolBitArray.

        Args:
            bits (list[bool] | None, optional): Initial list of boolean values. Defaults
                to empty list.
        """
        super().__init__()
        if bits is not None:
            self._bits = bits
        else:
            self._bits = []

    @classmethod
    def from_bits(cls, bits: list[bool] | None = None) -> "ListBoolBitArray":
        """Creates a BitArray from a list of boolean values.

        Args:
            bits (list[bool] | None, optional): List of boolean values. Defaults to
                None, which creates an empty BitArray.

        Returns:
            ListBoolBitArray: A BitArray created from the bits.
        """
        return cls(bits)

    @classmethod
    def zeros(cls, length: int) -> "ListBoolBitArray":
        """Creates a BitArray filled with zeros.

        Args:
            length (int): The length of the bit array.

        Returns:
            ListBoolBitArray: A BitArray filled with False values.
        """
        return cls([False] * length)

    @classmethod
    def ones(cls, length: int) -> "ListBoolBitArray":
        """Creates a BitArray filled with ones.

        Args:
            length (int): The length of the bit array.

        Returns:
            ListBoolBitArray: A BitArray filled with True values.
        """
        return cls([True] * length)

    def to_int(self) -> int:
        """Converts the bit array to an unsigned integer (LSB-first).

        Returns:
            int: The integer represented by the bit array.
        """
        return sum((1 << i) for i, bit in enumerate(self._bits) if bit)

    def copy(self) -> "ListBoolBitArray":
        """Creates a copy of the bit array.

        Returns:
            ListBoolBitArray: A new BitArray with the same bits.
        """
        return ListBoolBitArray(self._bits.copy())

    def to_float(self) -> float:
        """Converts a 64-bit array to a floating-point number (LSB-first).

        Returns:
            float: The floating-point number represented by the bit array.

        Raises:
            AssertionError: If the bit array is not 64 bits long.
        """
        assert len(self._bits) == 64, "Bit array must be 64 bits long."
        byte_values = bytearray()
        for i in range(0, 64, 8):
            byte = 0
            for j in range(8):
                if self._bits[i + j]:
                    byte |= 1 << j  # LSB-first
            byte_values.append(byte)
        float_value = struct.unpack("<d", bytes(byte_values))[0]
        return float_value  # type: ignore

    def __len__(self) -> int:
        """Returns the length of the bit array.

        Returns:
            int: The number of bits in the array.
        """
        return len(self._bits)

    @overload
    def __getitem__(self, index: int) -> bool: ...
    @overload
    def __getitem__(self, index: slice) -> ListBoolBitArray: ...

    def __getitem__(self, index: int | slice) -> bool | ListBoolBitArray:
        """Get a bit or a slice of bits as a new ListBoolBitArray."""
        if isinstance(index, slice):
            return ListBoolBitArray.from_bits(self._bits[index])
        return self._bits[index]

    @overload
    def __setitem__(self, index: int, value: bool) -> None: ...
    @overload
    def __setitem__(self, index: slice, value: BitArray | list[bool]) -> None: ...

    def __setitem__(
        self, index: int | slice, value: bool | list[bool] | BitArray
    ) -> None:
        """Sets an item or slice in the bit array.

        Args:
            index (int or slice): The index or slice to set.
            value (bool or list[bool] or BitArray): The value(s) to assign.

        Raises:
            TypeError: If value type does not match index type.
        """
        if isinstance(index, slice):
            if isinstance(value, BitArray):
                self._bits[index] = list(value)
            elif isinstance(value, list):
                self._bits[index] = value
            else:
                raise TypeError("Cannot assign a single bool to a slice")
            return
        if isinstance(value, bool):
            self._bits[index] = value
        else:
            raise TypeError("Cannot assign a list or BitArray to a single index")

    def __iter__(self) -> Iterator[bool]:
        """Iterates over the bits in the array.

        Yields:
            bool: The next bit in the array.
        """
        return iter(self._bits)

    def __add__(self, other: BitArray | list[bool]) -> "ListBoolBitArray":
        """Concatenates two bit arrays.

        Args:
            other (BitArray or list[bool]): The other bit array or list to concatenate.

        Returns:
            ListBoolBitArray: The concatenated bit array.
        """
        if isinstance(other, BitArray):
            return ListBoolBitArray(self._bits + list(other))
        return ListBoolBitArray(self._bits + other)

    def __radd__(self, other: list[bool]) -> "ListBoolBitArray":
        """Reverse concatenation with a list.

        Args:
            other (list[bool]): The list to concatenate before this bit array.

        Returns:
            ListBoolBitArray: The concatenated bit array.
        """
        return ListBoolBitArray(other + self._bits)

    def __repr__(self) -> str:
        """Returns a string representation of the BitArray.

        Returns:
            str: String representation of the BitArray.
        """
        return f"ListBoolBitArray({self._bits})"
