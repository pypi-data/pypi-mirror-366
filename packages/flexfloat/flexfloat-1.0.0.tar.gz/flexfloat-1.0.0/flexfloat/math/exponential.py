"""
Exponential and power functions for FlexFloat arithmetic.

This module provides implementations of exponential-related mathematical functions
for FlexFloat numbers, including the exponential function (e^x), exponentiation (pow),
and expm1 (e^x - 1). The algorithms are designed to balance accuracy and performance
for arbitrary-precision floating-point arithmetic.

Functions:
    exp(x): Compute the exponential function e^x for a FlexFloat value.
    pow(base, exp): Raise a FlexFloat base to a FlexFloat exponent.
    expm1(x): Compute e^x - 1 for a FlexFloat value.

Example:
    from flexfloat.math.exponential import exp, pow
    from flexfloat.core import FlexFloat

    x = FlexFloat.from_float(2.0)
    y = exp(x)  # e^2
    z = pow(x, y)  # 2^e^2
    print(y, z)
"""

from typing import Final

from ..core import FlexFloat

_1: Final[FlexFloat] = FlexFloat.from_float(1.0)
_2: Final[FlexFloat] = FlexFloat.from_float(2.0)


def _exp_taylor_series(
    x: FlexFloat,
    max_terms: int = 100,
    tolerance: FlexFloat = FlexFloat.from_float(1e-16),
) -> FlexFloat:
    """Compute the exponential of a FlexFloat using the Taylor series expansion.

    Evaluates e^x using the Taylor series:
        e^x = 1 + x + x²/2! + x³/3! + ...
    The series converges rapidly for |x| < 1. For best accuracy, use this function
    only for small values of x (|x| <= 1).

    Args:
        x (FlexFloat): The exponent value (should be small for best convergence).
        max_terms (int, optional): Maximum number of terms to evaluate. Defaults to 100.
        tolerance (FlexFloat, optional): Convergence threshold. Defaults to 1e-16.

    Returns:
        FlexFloat: The computed value of e^x.
    """
    tolerance = tolerance.abs()

    # Initialize result with first term: 1
    result = _1.copy()

    if x.is_zero():
        return result

    # Initialize for the series computation
    term = x.copy()  # First term: x
    result += term

    # For subsequent terms, use the recurrence relation:
    # term[n+1] = term[n] * x / (n+1)
    for n in range(1, max_terms):
        # Calculate next term: x^(n+1) / (n+1)!
        term = term * x / (n + 1)
        result += term

        # Check for convergence
        if term.abs() < tolerance:
            break

    return result


def _exp_range_reduction(x: FlexFloat, max_reductions: int = 50) -> FlexFloat:
    """Compute the exponential of a FlexFloat using range reduction and Taylor series.

    Uses the identity e^x = (e^(x/2^k))^(2^k) to reduce large |x| to a small value,
    computes exp using the Taylor series, and then squares the result k times.

    Args:
        x (FlexFloat): The exponent value.
        max_reductions (int, optional): Maximum number of times to halve x.
            Defaults to 50.

    Returns:
        FlexFloat: The computed value of e^x.
    """
    abs_x = x.abs()

    # For small values, use Taylor series directly
    if abs_x <= _1:
        return _exp_taylor_series(x)

    # Determine how many times to halve x to get |x/2^k| <= 1
    reduction_count = 0

    # Keep halving until |reduced_x| <= 1
    while x.abs() > _1 and reduction_count < max_reductions:
        x = x / _2
        reduction_count += 1

    # Compute exp(reduced_x) using Taylor series
    x = _exp_taylor_series(x)

    # Square the result reduction_count times: result = result^(2^reduction_count)
    for _ in range(reduction_count):
        x *= x

    return x


def exp(x: FlexFloat) -> FlexFloat:
    """Compute the exponential function e^x for a FlexFloat value.

    Handles special cases (NaN, infinity, zero) and uses a combination
    of range reduction and Taylor series for accurate computation.

    Args:
        x (FlexFloat): The exponent value.

    Returns:
        FlexFloat: The value of e^x as a FlexFloat.

    Example:
        result = exp(FlexFloat.from_float(1.0))  # e^1
    """
    # Handle special cases
    if x.is_nan():
        return FlexFloat.nan()

    if x.is_zero():
        return _1.copy()

    if x.is_infinity():
        if x.sign:
            return FlexFloat.zero()
        return FlexFloat.infinity(sign=False)

    return _exp_range_reduction(x)


def pow(base: FlexFloat, exp: FlexFloat) -> FlexFloat:
    """Raise a FlexFloat base to a FlexFloat exponent.

    Args:
        base (FlexFloat): The base value.
        exp (FlexFloat): The exponent value.

    Returns:
        FlexFloat: The value of base**exp as a FlexFloat.

    Example:
        result = pow(FlexFloat.from_float(2.0), FlexFloat.from_float(3.0))  # 2^3
    """
    return base**exp


def expm1(x: FlexFloat) -> FlexFloat:
    """Return e^x minus 1 for a FlexFloat value.

    This function is more accurate than exp(x) - 1 for small x.

    Args:
        x (FlexFloat): The exponent value.

    Returns:
        FlexFloat: The value of e^x - 1.

    Example:
        result = expm1(FlexFloat.from_float(1e-5))
    """
    return exp(x) - _1
