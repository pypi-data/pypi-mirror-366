"""BitArray protocol definition for the flexfloat package.

This module defines the BitArray protocol, which all BitArray implementations must
follow. The protocol ensures a consistent interface for bit manipulation.

Example:
    from flexfloat.bitarray import BitArray
    class MyBitArray(BitArray):
        ...
    my_bitarray = MyBitArray()
    isinstance(my_bitarray, BitArray)  # True
"""

from __future__ import annotations

from typing import Iterable, Iterator, Protocol, overload, runtime_checkable


@runtime_checkable
class BitArray(Protocol):
    """Protocol defining the interface for BitArray implementations.

    This protocol defines all the methods and properties that a BitArray
    implementation must provide.

    For consistency, all BitArray implementations should order bits as LSB-first,
    meaning the least significant bit is at index 0 and the most significant bit
    is at the highest index.
    """

    @classmethod
    def from_bits(cls, bits: list[bool] | None = None) -> "BitArray":
        """Creates a BitArray from a list of boolean values.

        Args:
            bits (list[bool] | None, optional): List of boolean values. Defaults to
                None, which creates an empty BitArray.

        Returns:
            BitArray: A BitArray created from the bits.
        """
        ...

    @classmethod
    def from_float(cls, value: float) -> "BitArray":
        """Converts a floating-point number to a bit array.

        Args:
            value (float): The floating-point number to convert.

        Returns:
            BitArray: A BitArray representing the bits of the floating-point number.
        """
        ...

    @classmethod
    def from_signed_int(cls, value: int, length: int) -> "BitArray":
        """Converts a signed integer to a bit array using off-set binary representation.

        Args:
            value (int): The signed integer to convert.
            length (int): The length of the resulting bit array.

        Returns:
            BitArray: A BitArray representing the bits of the signed integer.

        Raises:
            AssertionError: If the value is out of range for the specified length.
        """
        ...

    @classmethod
    def zeros(cls, length: int) -> "BitArray":
        """Creates a BitArray filled with zeros.

        Args:
            length (int): The length of the bit array.

        Returns:
            BitArray: A BitArray filled with False values.
        """
        ...

    @classmethod
    def ones(cls, length: int) -> "BitArray":
        """Creates a BitArray filled with ones.

        Args:
            length (int): The length of the bit array.

        Returns:
            BitArray: A BitArray filled with True values.
        """
        ...

    @classmethod
    def parse_bitarray(cls, bitstring: Iterable[str]) -> "BitArray":
        """Parses a string of bits (with optional spaces) into a BitArray instance.
        Non-valid characters are ignored.

        Args:
            bitstring (Iterable[str]): A string of bits, e.g., "1010 1100".

        Returns:
            BitArray: A BitArray instance created from the bit string.
        """
        ...

    def to_float(self) -> float:
        """Converts a 64-bit array to a floating-point number.

        Returns:
            float: The floating-point number represented by the bit array.

        Raises:
            AssertionError: If the bit array is not 64 bits long.
        """
        ...

    def to_int(self) -> int:
        """Converts the bit array to an unsigned integer.

        Returns:
            int: The integer represented by the bit array.
        """
        ...

    def to_signed_int(self) -> int:
        """Converts a bit array into a signed integer using off-set binary
        representation.

        Returns:
            int: The signed integer represented by the bit array.

        Raises:
            AssertionError: If the bit array is empty.
        """
        ...

    def shift(self, shift_amount: int, fill: bool = False) -> "BitArray":
        """Shifts the bit array left or right by a specified number of bits.

        This function shifts the bits in the array, filling in new bits with the
        specified fill value.
        If the value is positive, it shifts left; if negative, it shifts right.
        Fills the new bits with the specified fill value (default is False).

        Args:
            shift_amount (int): The number of bits to shift. Positive for left shift,
                negative for right shift.
            fill (bool, optional): The value to fill in the new bits created by the
                shift. Defaults to False.

        Returns:
            BitArray: A new BitArray with the bits shifted and filled.
        """
        ...

    def copy(self) -> "BitArray":
        """Creates a copy of the bit array.

        Returns:
            BitArray: A new BitArray with the same bits.
        """
        ...

    def __len__(self) -> int:
        """Returns the length of the bit array.

        Returns:
            int: The number of bits in the array.
        """
        ...

    @overload
    def __getitem__(self, index: int) -> bool: ...
    @overload
    def __getitem__(self, index: slice) -> "BitArray": ...

    def __getitem__(self, index: int | slice) -> bool | BitArray:
        """Get a bit or a slice of bits as a new BitArray."""
        ...

    @overload
    def __setitem__(self, index: int, value: bool) -> None: ...
    @overload
    def __setitem__(self, index: slice, value: "BitArray" | list[bool]) -> None: ...

    def __setitem__(
        self, index: int | slice, value: bool | list[bool] | "BitArray"
    ) -> None:
        """Sets an item or slice in the bit array.

        Args:
            index (int or slice): The index or slice to set.
            value (bool or list[bool] or BitArray): The value(s) to assign.
        """
        ...

    def __iter__(self) -> Iterator[bool]:
        """Iterates over the bits in the array.

        Yields:
            bool: The next bit in the array.
        """
        ...

    def __add__(self, other: "BitArray" | list[bool]) -> "BitArray":
        """Concatenates two bit arrays.

        Args:
            other (BitArray or list[bool]): The other bit array or list to concatenate.

        Returns:
            BitArray: The concatenated bit array.
        """
        ...

    def __radd__(self, other: list[bool]) -> "BitArray":
        """Reverse concatenation with a list.

        Args:
            other (list[bool]): The list to concatenate before this bit array.

        Returns:
            BitArray: The concatenated bit array.
        """
        ...

    def __eq__(self, other: object) -> bool:
        """Checks equality with another BitArray or list.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: True if equal, False otherwise.
        """
        ...

    def __bool__(self) -> bool:
        """Returns True if any bit is set.

        Returns:
            bool: True if any bit is set, False otherwise.
        """
        ...

    def __repr__(self) -> str:
        """Returns a string representation of the BitArray.

        Returns:
            str: String representation of the BitArray.
        """
        ...

    def __str__(self) -> str:
        """Returns a string representation of the bits.

        Returns:
            str: String representation of the bits.
        """
        ...

    def any(self) -> bool:
        """Returns True if any bit is set to True.

        Returns:
            bool: True if any bit is set to True, False otherwise.
        """
        ...

    def all(self) -> bool:
        """Returns True if all bits are set to True.

        Returns:
            bool: True if all bits are set to True, False otherwise.
        """
        ...

    def count(self, value: bool = True) -> int:
        """Counts the number of bits set to the specified value.

        Args:
            value (bool, optional): The value to count. Defaults to True.

        Returns:
            int: The number of bits set to the specified value.
        """
        ...

    def reverse(self) -> "BitArray":
        """Returns a new BitArray with the bits in reverse order.

        Returns:
            BitArray: A new BitArray with the bits in reverse order.
        """
        ...
