"""
Floating point utility functions for FlexFloat arithmetic.

This module provides utility functions for working with FlexFloat numbers, including
sign manipulation, absolute value, and checks for special values
(infinity, NaN, finite). These functions are analogous to those in Python's math module
but operate on FlexFloat instances for arbitrary-precision floating-point arithmetic.

Functions:
    copysign(x, y): Return a FlexFloat with the magnitude of x and the sign of y.
    fabs(x): Return the absolute value of a FlexFloat.
    isinf(x): Check if a FlexFloat is positive or negative infinity.
    isnan(x): Check if a FlexFloat is NaN (not a number).
    isfinite(x): Check if a FlexFloat is finite (not infinity or NaN).

Example:
    from flexfloat.math.floating_point import copysign, fabs, isinf
    from flexfloat.core import FlexFloat

    x = FlexFloat.from_float(-3.5)
    y = FlexFloat.from_float(2.0)
    z = copysign(x, y)  # z has magnitude 3.5 and sign of y (positive)
    print(z)
    print(fabs(x))
    print(isinf(z))
"""

from ..core import FlexFloat


def copysign(x: FlexFloat, y: FlexFloat) -> FlexFloat:
    """Return a FlexFloat with the magnitude of x and the sign of y.

    Args:
        x (FlexFloat): Value whose magnitude is used.
        y (FlexFloat): Value whose sign is used.

    Returns:
        FlexFloat: A FlexFloat with the magnitude of x and the sign of y.

    Example:
        result = copysign(FlexFloat.from_float(-2.0), FlexFloat.from_float(3.0))
        # result is 2.0 (positive)
    """
    result = x.copy()
    result.sign = y.sign
    return result


def fabs(x: FlexFloat) -> FlexFloat:
    """Return the absolute value of a FlexFloat.

    Args:
        x (FlexFloat): The value to get the absolute value of.

    Returns:
        FlexFloat: The absolute value of x.

    Example:
        result = fabs(FlexFloat.from_float(-5.0))  # result is 5.0
    """
    return abs(x)


def isinf(x: FlexFloat) -> bool:
    """Check if a FlexFloat is positive or negative infinity.

    Args:
        x (FlexFloat): The value to check.

    Returns:
        bool: True if x is infinity, False otherwise.

    Example:
        result = isinf(FlexFloat.infinity())  # result is True
    """
    return x.is_infinity()


def isnan(x: FlexFloat) -> bool:
    """Check if a FlexFloat is NaN (not a number).

    Args:
        x (FlexFloat): The value to check.

    Returns:
        bool: True if x is NaN, False otherwise.

    Example:
        result = isnan(FlexFloat.nan())  # result is True
    """
    return x.is_nan()


def isfinite(x: FlexFloat) -> bool:
    """Check if a FlexFloat is finite (not infinity or NaN).

    Args:
        x (FlexFloat): The value to check.

    Returns:
        bool: True if x is finite, False otherwise.

    Example:
        result = isfinite(FlexFloat.from_float(1.0))  # result is True
    """
    return not x.is_infinity() and not x.is_nan()
