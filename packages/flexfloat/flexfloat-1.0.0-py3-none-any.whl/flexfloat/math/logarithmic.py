"""
Logarithmic functions for FlexFloat arithmetic.

This module provides implementations of logarithmic functions for FlexFloat numbers,
including the natural logarithm (ln), logarithm to arbitrary base, log10, log2, and
log1p. The algorithms use Taylor series and range reduction for accuracy and performance
with arbitrary-precision floating-point arithmetic.

Functions:
    log(x, base): Compute the logarithm of x to a given base.
    log10(x): Compute the base-10 logarithm of x.
    log2(x): Compute the base-2 logarithm of x.
    log1p(x): Compute the natural logarithm of 1 + x, accurate for small x.

Example:
    from flexfloat.math.logarithmic import log, log10, log2, log1p
    from flexfloat.core import FlexFloat

    x = FlexFloat.from_float(10.0)
    print(log(x, FlexFloat.from_float(2.0)))  # log base 2
    print(log10(x))
    print(log2(x))
    print(log1p(FlexFloat.from_float(1e-5)))
"""

from typing import Final

from ..core import FlexFloat
from .constants import e

# Internal constants for calculations
_1: Final[FlexFloat] = FlexFloat.from_float(1.0)
_2: Final[FlexFloat] = FlexFloat.from_float(2.0)
_10: Final[FlexFloat] = FlexFloat.from_float(10.0)
_EPSILON_15: Final[FlexFloat] = FlexFloat.from_float(1e-15)


def _ln_taylor_series(
    x: FlexFloat,
    max_iterations: int = 100,
    tolerance: FlexFloat = FlexFloat.from_float(1e-16),
) -> FlexFloat:
    """Compute the natural logarithm of x using a fast-converging Taylor series.

    Uses the identity ln(x) = 2 * artanh((x-1)/(x+1)), which converges rapidly for x
    near 1.

    Args:
        x (FlexFloat): The input value (should be close to 1 for best convergence).
        max_iterations (int, optional): Maximum number of terms. Defaults to 100.
        tolerance (FlexFloat, optional): Convergence threshold. Defaults to 1e-16.

    Returns:
        FlexFloat: The natural logarithm of x.
    """
    x_minus_1 = x - _1
    x_plus_1 = x + _1

    # Check for division by zero
    if x_plus_1.is_zero():
        return FlexFloat.nan()

    y = x_minus_1 / x_plus_1
    tolerance = tolerance.abs()

    # Initialize series: artanh(y) = y + y³/3 + y⁵/5 + ...
    result = y.copy()
    y_squared = y * y
    term = y.copy()

    for n in range(1, max_iterations):
        # Calculate next term: y^(2n+1) / (2n+1)
        term *= y_squared
        term_contribution = term / (2 * n + 1)
        result += term_contribution

        # Check for convergence (compare absolute values)
        if term_contribution.abs() < tolerance:
            break

    # Return 2 * artanh((x-1)/(x+1))
    return _2 * result


def _ln_range_reduction(x: FlexFloat) -> FlexFloat:
    """Compute the natural logarithm of x using range reduction and Taylor series.

    For small x, uses ln(x) = -ln(1/x). For large x, uses iterative square roots.
    For values near 1, uses the Taylor series directly.

    Args:
        x (FlexFloat): The input value (must be positive).

    Returns:
        FlexFloat: The natural logarithm of x.
    """
    # For very small values, use ln(x) = -ln(1/x)
    if x < 0.1:
        reciprocal = _1 / x
        return -_ln_range_reduction(reciprocal)

    # For values close to 1, use direct Taylor series
    if x <= 2.0:
        return _ln_taylor_series(x)

    # For large values, use iterative square roots
    multiplier = _1

    from . import sqrt

    max_reductions = 30
    for _ in range(max_reductions):
        if x <= 2.0:
            break
        x = sqrt(x)
        multiplier = multiplier * _2

    # Compute ln(current_x) using Taylor series
    ln_result = _ln_taylor_series(x)

    # Apply the multiplier
    return multiplier * ln_result


def log(x: FlexFloat, base: FlexFloat = e) -> FlexFloat:
    """Compute the logarithm of x to a given base using Taylor series and range
    reduction.

    Handles special cases and uses the change of base formula for arbitrary bases.

    Args:
        x (FlexFloat): The value to compute the logarithm of.
        base (FlexFloat, optional): The base of the logarithm. Defaults to e.

    Returns:
        FlexFloat: The logarithm of x to the given base.
    """
    # Handle special cases
    if x.is_nan() or base.is_nan():
        return FlexFloat.nan()

    if x.is_zero() or x.sign:  # x <= 0
        return FlexFloat.nan()

    if x.is_infinity():
        return FlexFloat.infinity(sign=False)

    # Handle base special cases
    if base.is_zero() or base.sign or base.is_infinity():
        return FlexFloat.nan()

    # Check if base is 1 (which would make logarithm undefined)
    if abs(base - _1) < _EPSILON_15:
        return FlexFloat.nan()

    # If x is 1, log of any valid base is 0
    if abs(x - _1) < _EPSILON_15:
        return FlexFloat.zero()

    # Compute natural logarithm using range reduction and Taylor series
    ln_x = _ln_range_reduction(x)

    # If base is e (natural logarithm), return directly
    if abs(base - e) < _EPSILON_15:
        return ln_x

    # For other bases, use change of base formula: log_base(x) = ln(x) / ln(base)
    ln_base = _ln_range_reduction(base)
    return ln_x / ln_base


def log10(x: FlexFloat) -> FlexFloat:
    """Return the base-10 logarithm of x.

    Args:
        x (FlexFloat): The value to compute the base-10 logarithm of.

    Returns:
        FlexFloat: The base-10 logarithm of x.
    """
    return log(x, _10)


def log1p(x: FlexFloat) -> FlexFloat:
    """Return the natural logarithm of 1 + x, accurate for small x.

    Args:
        x (FlexFloat): The value to compute the natural logarithm of 1 + x.

    Returns:
        FlexFloat: The natural logarithm of 1 + x.
    """
    # Handle special cases
    if x.is_nan():
        return FlexFloat.nan()

    # Check if 1 + x would be <= 0
    one_plus_x = _1 + x
    if one_plus_x.is_zero() or one_plus_x.sign:
        return FlexFloat.nan()

    if one_plus_x.is_infinity():
        return FlexFloat.infinity(sign=False)

    # For small x, use Taylor series directly: ln(1+x) = x - x²/2 + x³/3 - ...
    if abs(x) < 0.5:  # Direct Taylor series for better accuracy
        return _ln_taylor_series(one_plus_x)

    # For larger x, use the regular log function
    return log(one_plus_x)


def log2(x: FlexFloat) -> FlexFloat:
    """Return the base-2 logarithm of x.

    Args:
        x (FlexFloat): The value to compute the base-2 logarithm of.

    Returns:
        FlexFloat: The base-2 logarithm of x.
    """
    return log(x, _2)
