"""Memory-efficient int64-based BitArray implementation for the flexfloat package.

This implementation is ideal for large bit arrays, as it packs 64 bits per integer.
Bit order: LSB-first (least significant bit at index 0, increasing to MSB).

Example:
    from flexfloat.bitarray import ListInt64BitArray
    ba = ListInt64BitArray([0b10101010], length=8)
    print(list(ba))
    # Output: [False, True, False, True, False, True, False, True]
"""

from __future__ import annotations

import struct
from typing import Iterator, overload

from .bitarray import BitArray
from .bitarray_mixins import BitArrayCommonMixin


class ListInt64BitArray(BitArrayCommonMixin):
    """A memory-efficient bit array class using a list of int64 values.

    This implementation packs 64 bits per integer, making it more memory efficient
    for large bit arrays compared to the boolean list implementation.
    """

    def __init__(self, chunks: list[int] | None = None, length: int = 0):
        """Initializes a ListInt64BitArray.

        Args:
            chunks (list[int] | None, optional): Initial list of int64 chunks. Defaults
                to empty list.
            length (int, optional): The amount of bits in the array. Defaults to 0.

        Raises:
            ValueError: If length is negative.
        """
        super().__init__()
        chunks = chunks or []
        if length < 0:
            raise ValueError("Length must be non-negative")
        self._length: int = length
        self._chunks: list[int] = chunks

    @classmethod
    def from_bits(cls, bits: list[bool] | None = None) -> "ListInt64BitArray":
        """Creates a BitArray from a list of boolean values.

        Args:
            bits (list[bool] | None, optional): List of boolean values in LSB-first
                order. Defaults to None, which creates an empty BitArray.

        Returns:
            ListInt64BitArray: A BitArray created from the bits.
        """
        if bits is None:
            return cls()
        chunks: list[int] = []

        for i in range(0, len(bits), 64):
            chunk = 0
            chunk_end = min(i + 64, len(bits))
            for j in range(i, chunk_end):
                if bits[j]:
                    chunk |= 1 << (j - i)
            chunks.append(chunk)

        return cls(chunks, len(bits))

    @classmethod
    def zeros(cls, length: int) -> "ListInt64BitArray":
        """Creates a BitArray filled with zeros.

        Args:
            length (int): The length of the bit array.

        Returns:
            ListInt64BitArray: A BitArray filled with False values.
        """
        return cls([0] * ((length + 63) // 64), length)

    @classmethod
    def ones(cls, length: int) -> "ListInt64BitArray":
        """Creates a BitArray filled with ones.

        Args:
            length (int): The length of the bit array.

        Returns:
            ListInt64BitArray: A BitArray filled with True values.
        """
        chunks = [0xFFFFFFFFFFFFFFFF] * (length // 64)
        if length % 64 > 0:
            partial_chunk = (1 << (length % 64)) - 1
            chunks.append(partial_chunk)
        return cls(chunks, length)

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
        chunk_index = index // 64
        bit_index = index % 64
        bit_position = bit_index  # LSB-first
        return bool(self._chunks[chunk_index] & (1 << bit_position))

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
        chunk_index = index // 64
        bit_index = index % 64
        bit_position = bit_index  # LSB-first
        mask = 1 << bit_position
        self._chunks[chunk_index] ^= (-value ^ self._chunks[chunk_index]) & mask

    def to_int(self) -> int:
        """Converts the bit array to an unsigned integer (LSB-first).

        Returns:
            int: The integer represented by the bit array.
        """
        result = 0
        for i in range(self._length):
            if self._get_bit(i):
                result |= 1 << i
        return result

    def to_float(self) -> float:
        """Converts a 64-bit array to a floating-point number (LSB-first).

        Returns:
            float: The floating-point number represented by the bit array.

        Raises:
            AssertionError: If the bit array is not 64 bits long.
        """
        assert self._length == 64, "Bit array must be 64 bits long."
        chunk = self._chunks[0]
        byte_values = bytearray()
        for i in range(8):
            byte = (chunk >> (i * 8)) & 0xFF  # LSB-first
            byte_values.append(byte)
        float_value = struct.unpack("<d", bytes(byte_values))[0]
        return float_value  # type: ignore

    def copy(self) -> "ListInt64BitArray":
        """Creates a copy of the bit array.

        Returns:
            ListInt64BitArray: A new BitArray with the same bits.
        """
        return ListInt64BitArray(self._chunks.copy(), self._length)

    def __len__(self) -> int:
        """Returns the length of the bit array.

        Returns:
            int: The number of bits in the array.
        """
        return self._length

    @overload
    def __getitem__(self, index: int) -> bool: ...
    @overload
    def __getitem__(self, index: slice) -> "ListInt64BitArray": ...

    def __getitem__(self, index: int | slice) -> bool | ListInt64BitArray:
        """Get a bit or a slice of bits as a new ListInt64BitArray."""
        if isinstance(index, slice):
            start, stop, step = index.indices(self._length)
            bits = [self._get_bit(i) for i in range(start, stop, step)]
            return ListInt64BitArray.from_bits(bits)
        return self._get_bit(index)

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
        if isinstance(index, slice):
            start, stop, step = index.indices(self._length)
            indices = list(range(start, stop, step))

            if isinstance(value, BitArray):
                values = list(value)
            elif isinstance(value, list):
                values = value
            else:
                raise TypeError("Cannot assign a single bool to a slice")

            if len(indices) != len(values):
                raise ValueError("Length mismatch in slice assignment")

            for i, v in zip(indices, values):
                self._set_bit(i, v)
            return

        if isinstance(value, bool):
            self._set_bit(index, value)
        else:
            raise TypeError("Cannot assign a list or BitArray to a single index")

    def __iter__(self) -> Iterator[bool]:
        """Iterates over the bits in the array.

        Yields:
            bool: The next bit in the array.
        """
        for i in range(self._length):
            yield self._get_bit(i)

    def __add__(self, other: BitArray | list[bool]) -> "ListInt64BitArray":
        """Concatenates two bit arrays.

        Args:
            other (BitArray or list[bool]): The other bit array or list to concatenate.

        Returns:
            ListInt64BitArray: The concatenated bit array.
        """
        if isinstance(other, BitArray):
            return ListInt64BitArray.from_bits(list(self) + list(other))
        return ListInt64BitArray.from_bits(list(self) + other)

    def __radd__(self, other: list[bool]) -> "ListInt64BitArray":
        """Reverse concatenation with a list.

        Args:
            other (list[bool]): The list to concatenate before this bit array.

        Returns:
            ListInt64BitArray: The concatenated bit array.
        """
        return ListInt64BitArray.from_bits(other + list(self))

    def __eq__(self, other: object) -> bool:
        """Checks equality with another BitArray or list.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, BitArray):
            if len(self) != len(other):
                return False
            return all(a == b for a, b in zip(self, other))
        if isinstance(other, list):
            return list(self) == other
        return False

    def __bool__(self) -> bool:
        """Returns True if any bit is set.

        Returns:
            bool: True if any bit is set, False otherwise.
        """
        return any(chunk != 0 for chunk in self._chunks)

    def __repr__(self) -> str:
        """Returns a string representation of the BitArray.

        Returns:
            str: String representation of the BitArray.
        """
        return f"ListInt64BitArray({list(self)})"

    def any(self) -> bool:
        """Returns True if any bit is set to True.

        Returns:
            bool: True if any bit is set to True, False otherwise.
        """
        return any(chunk != 0 for chunk in self._chunks)

    def all(self) -> bool:
        """Returns True if all bits are set to True.

        Returns:
            bool: True if all bits are set to True, False otherwise.
        """
        if self._length == 0:
            return True

        # Check full chunks
        num_full_chunks = self._length // 64
        for i in range(num_full_chunks):
            if self._chunks[i] != 0xFFFFFFFFFFFFFFFF:
                return False

        # Check partial chunk if exists
        remaining_bits = self._length % 64
        if remaining_bits > 0:
            expected_pattern = (1 << remaining_bits) - 1
            if self._chunks[-1] != expected_pattern:
                return False

        return True
