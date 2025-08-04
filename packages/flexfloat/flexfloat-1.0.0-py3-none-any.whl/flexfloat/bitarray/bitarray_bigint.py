"""Infinite-size int-based BitArray implementation for the flexfloat package.

This implementation is suitable for extremely large bit arrays, leveraging Python's
arbitrary-precision integers. Bit order: LSB-first (least significant bit at index 0).

Example:
    from flexfloat.bitarray import BigIntBitArray
    ba = BigIntBitArray(0b1011, length=4)
    print(list(ba))
    # Output: [True, True, False, True]
"""

from __future__ import annotations

import struct
from typing import Iterator, overload

from .bitarray import BitArray
from .bitarray_mixins import BitArrayCommonMixin


class BigIntBitArray(BitArrayCommonMixin):
    """A memory-efficient bit array class using Python's infinite-size int.

    This implementation stores all bits as a single Python integer, leveraging
    Python's arbitrary precision arithmetic for potentially unlimited size.
    Since Python integers are arbitrary precision, this can handle bit arrays
    of any size limited only by available memory.
    """

    def __init__(self, value: int = 0, length: int = 0):
        """Initializes a BigIntBitArray.

        Args:
            value (int, optional): Initial integer value representing the bits. Defaults
                to 0.
            length (int, optional): The number of bits in the array. Defaults to 0.

        Raises:
            ValueError: If length is negative.
        """
        super().__init__()
        if length < 0:
            raise ValueError("Length must be non-negative")
        self._length: int = length
        self._value: int = value

    @classmethod
    def from_bits(cls, bits: list[bool] | None = None) -> "BigIntBitArray":
        """Creates a BitArray from a list of boolean values.

        Args:
            bits (list[bool] | None, optional): List of boolean values. Defaults to
                None, which creates an empty BitArray.

        Returns:
            BigIntBitArray: A BitArray created from the bits.
        """
        if bits is None:
            return cls()
        value = 0

        # Pack bits into a single integer (LSB-first)
        # Least significant bit is at index 0
        for i, bit in enumerate(bits):
            if bit:
                value |= 1 << i

        return cls(value, len(bits))

    @classmethod
    def zeros(cls, length: int) -> "BigIntBitArray":
        """Creates a BitArray filled with zeros.

        Args:
            length (int): The length of the bit array.

        Returns:
            BigIntBitArray: A BitArray filled with False values.
        """
        return cls(0, length)

    @classmethod
    def ones(cls, length: int) -> "BigIntBitArray":
        """Creates a BitArray filled with ones.

        Args:
            length (int): The length of the bit array.

        Returns:
            BigIntBitArray: A BitArray filled with True values.
        """
        return cls((1 << length) - 1 if length > 0 else 0, length)

    def _get_bit(self, index: int) -> bool:
        """Gets a single bit at the specified index (LSB-first).

        Args:
            index (int): The bit index (LSB-first).

        Returns:
            bool: The value of the bit at the specified index.

        Raises:
            IndexError: If index is out of range.
        """
        if index < 0 or index >= self._length:
            raise IndexError("Bit index out of range")
        bit_position = index  # LSB-first
        return bool(self._value & (1 << bit_position))

    def _set_bit(self, index: int, value: bool) -> None:
        """Sets a single bit at the specified index (LSB-first).

        Args:
            index (int): The bit index (LSB-first).
            value (bool): The value to set.

        Raises:
            IndexError: If index is out of range.
        """
        if index < 0 or index >= self._length:
            raise IndexError("Bit index out of range")
        bit_position = index  # LSB-first

        if value:
            self._value |= 1 << bit_position
        else:
            self._value &= ~(1 << bit_position)

    def to_float(self) -> float:
        """Converts a 64-bit array to a floating-point number (LSB-first).

        Returns:
            float: The floating-point number represented by the bit array.

        Raises:
            AssertionError: If the bit array is not 64 bits long.
        """
        assert self._length == 64, "Bit array must be 64 bits long."

        # Convert integer to bytes (big-endian)
        byte_values = bytearray()
        value = self._value
        for i in range(8):
            byte = (value >> (i * 8)) & 0xFF  # LSB-first
            byte_values.append(byte)

        # Unpack as double precision (64 bits)
        float_value = struct.unpack("<d", bytes(byte_values))[0]
        return float_value  # type: ignore

    def to_int(self) -> int:
        """Converts the bit array to an unsigned integer (LSB-first).

        Returns:
            int: The integer represented by the bit array.
        """
        return self._value

    def copy(self) -> "BigIntBitArray":
        """Creates a copy of the bit array.

        Returns:
            BigIntBitArray: A new BitArray with the same bits.
        """
        return BigIntBitArray(self._value, self._length)

    def __len__(self) -> int:
        """Returns the length of the bit array.

        Returns:
            int: The number of bits in the array.
        """
        return self._length

    @overload
    def __getitem__(self, index: int) -> bool: ...
    @overload
    def __getitem__(self, index: slice) -> BigIntBitArray: ...

    def __getitem__(self, index: int | slice) -> bool | BigIntBitArray:
        """Gets an item or slice from the bit array.

        Args:
            index (int or slice): The index or slice to retrieve.

        Returns:
            bool or BigIntBitArray: The bit value or a new BitArray for the slice.
        """
        if isinstance(index, int):
            return self._get_bit(index)
        start, stop, step = index.indices(self._length)
        if step != 1:
            # Handle step != 1 by extracting individual bits
            bits: list[bool] = [self._get_bit(i) for i in range(start, stop, step)]
        else:
            # Efficient slice extraction for step == 1
            bits = []
            for i in range(start, stop):
                bits.append(self._get_bit(i))
        return BigIntBitArray.from_bits(bits)

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
            ValueError: If value length does not match slice length.
        """
        if isinstance(index, int):
            if not isinstance(value, bool):
                raise TypeError("Value must be bool for single index")
            self._set_bit(index, value)
        else:  # slice
            start, stop, step = index.indices(self._length)

            # Convert value to list of bools
            if isinstance(value, bool):
                raise TypeError("Cannot assign bool to slice")
            if not hasattr(value, "__iter__"):
                raise TypeError("Value must be iterable for slice assignment")
            value_list = list(value)

            if step != 1:
                # Handle step != 1
                indices = list(range(start, stop, step))
                if len(value_list) != len(indices):
                    raise ValueError("Value length doesn't match slice length")
                for i, v in zip(indices, value_list):
                    self._set_bit(i, bool(v))
            else:
                # Handle step == 1
                if len(value_list) != (stop - start):
                    raise ValueError("Value length doesn't match slice length")
                for i, v in enumerate(value_list):
                    self._set_bit(start + i, bool(v))

    def __iter__(self) -> Iterator[bool]:
        """Iterates over the bits in the array.

        Yields:
            bool: The next bit in the array.
        """
        for i in range(self._length):
            yield self._get_bit(i)

    def __add__(self, other: BitArray | list[bool]) -> "BigIntBitArray":
        """Concatenates two bit arrays.

        Args:
            other (BitArray or list[bool]): The other bit array or list to concatenate.

        Returns:
            BigIntBitArray: The concatenated bit array.

        Raises:
            TypeError: If other is not iterable.
        """
        if hasattr(other, "__iter__"):
            other_bits = list(other)
        else:
            raise TypeError("Can only concatenate with iterable")

        all_bits = list(self) + other_bits
        return BigIntBitArray.from_bits(all_bits)

    def __radd__(self, other: list[bool]) -> "BigIntBitArray":
        """Reverse concatenation with a list.

        Args:
            other (list[bool]): The list to concatenate before this bit array.

        Returns:
            BigIntBitArray: The concatenated bit array.

        Raises:
            TypeError: If other is not iterable.
        """
        if hasattr(other, "__iter__"):
            other_bits = list(other)
        else:
            raise TypeError("Can only concatenate with iterable")

        all_bits = other_bits + list(self)
        return BigIntBitArray.from_bits(all_bits)

    def __repr__(self) -> str:
        """Returns a string representation of the BitArray.

        Returns:
            str: String representation of the BitArray.
        """
        return f"BigIntBitArray({list(self)})"
