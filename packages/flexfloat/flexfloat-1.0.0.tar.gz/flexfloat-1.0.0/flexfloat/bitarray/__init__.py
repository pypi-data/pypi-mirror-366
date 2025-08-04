"""BitArray implementation for the flexfloat package.

This module provides a factory and utilities for working with different BitArray
implementations, including:
    - ListBoolBitArray: List of booleans (default, flexible, easy to use)
    - ListInt64BitArray: List of int64 chunks (memory efficient for large arrays)
    - BigIntBitArray: Single Python int (arbitrary size, efficient for very large
        arrays)

Example:
    from flexfloat.bitarray import create_bitarray
    ba = create_bitarray('int64', [True, False, True])
    print(type(ba).__name__)
    # Output: ListInt64BitArray
"""

from __future__ import annotations

from .bitarray import BitArray
from .bitarray_bigint import BigIntBitArray
from .bitarray_bool import ListBoolBitArray
from .bitarray_int64 import ListInt64BitArray
from .bitarray_mixins import BitArrayCommonMixin

__all__ = [
    "BitArray",
    "ListBoolBitArray",
    "ListInt64BitArray",
    "BigIntBitArray",
    "BitArrayCommonMixin",
]
