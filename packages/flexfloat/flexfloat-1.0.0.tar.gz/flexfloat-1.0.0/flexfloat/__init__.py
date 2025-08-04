"""FlexFloat - A library for arbitrary precision floating point arithmetic.

FlexFloat is a high-precision Python library for arbitrary precision floating-point
arithmetic with growable exponents and fixed-size fractions. It extends IEEE 754
double-precision format to handle numbers beyond the standard range while maintaining
computational efficiency and precision consistency.

Key Features:
    - Growable exponents for handling extremely large/small numbers
    - Fixed 52-bit fraction precision for consistency
    - Complete mathematical function library (trigonometric, logarithmic, exponential,
        hyperbolic)
    - Multiple BitArray backend implementations
    - IEEE 754 compatible special value handling
    - Pythonic interface with natural mathematical syntax

Example:
    from flexfloat import FlexFloat
    from flexfloat.math import sin, pi

    x = FlexFloat.from_float(2.0)
    angle = pi / FlexFloat.from_float(4.0)
    result = sin(angle)  # sin(π/4) ≈ 0.707

Modules:
    core: Main FlexFloat class implementation
    math: Complete mathematical function library
    bitarray: BitArray implementations (bool, int64, bigint)
    types: Type definitions and protocols
"""

from . import math
from .bitarray import (
    BigIntBitArray,
    BitArray,
    ListBoolBitArray,
    ListInt64BitArray,
)
from .core import FlexFloat

__version__ = "1.0.0"
__author__ = "Ferran Sanchez Llado"

__all__ = [
    "FlexFloat",
    "BitArray",
    "ListBoolBitArray",
    "ListInt64BitArray",
    "BigIntBitArray",
    "math",
]
