"""
Mathematical constants for FlexFloat arithmetic.

This module defines commonly used mathematical constants as FlexFloat instances.
These constants are intended for use in mathematical computations that require
arbitrary precision or FlexFloat-specific behavior.

Constants:
    e (FlexFloat): Euler's number (base of natural logarithm).
    pi (FlexFloat): The ratio of a circle's circumference to its diameter.
    tau (FlexFloat): The circle constant, equal to 2*pi.
    inf (FlexFloat): Positive infinity.
    nan (FlexFloat): Not-a-Number (NaN), used to represent undefined results.

Example:
    from flexfloat.math.constants import pi, e
    from flexfloat.core import FlexFloat

    # Use constants in FlexFloat arithmetic
    result = pi + e
    print(result)
    # Output: FlexFloat(...)
"""

import math
from typing import Final

from ..core import FlexFloat

# Public constants

e: Final[FlexFloat] = FlexFloat.from_float(math.e)
"""The mathematical constant e (Euler's number) as a FlexFloat.

Represents the base of the natural logarithm, approximately 2.71828.
"""

pi: Final[FlexFloat] = FlexFloat.from_float(math.pi)
"""The mathematical constant pi as a FlexFloat.

Represents the ratio of a circle's circumference to its diameter, approximately 3.14159.
"""

tau: Final[FlexFloat] = FlexFloat.from_float(math.tau)
"""The mathematical constant tau (2*pi) as a FlexFloat.

Tau is equal to 2 times pi, approximately 6.28318. Useful in trigonometry and geometry.
"""

inf: Final[FlexFloat] = FlexFloat.infinity()
"""Positive infinity as a FlexFloat.

Represents a value greater than any finite number. Used to indicate overflow or
unbounded results.
"""

nan: Final[FlexFloat] = FlexFloat.nan()
"""Not-a-Number (NaN) as a FlexFloat.

Represents undefined or unrepresentable results, such as 0/0 or sqrt(-1).
"""
