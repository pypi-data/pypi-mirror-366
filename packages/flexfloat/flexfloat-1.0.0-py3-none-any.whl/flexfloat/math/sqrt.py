"""
Square root and cube root functions for FlexFloat arithmetic.

This module provides implementations of square root and cube root functions for
FlexFloat numbers, using Taylor series, Newton-Raphson, and scaling algorithms for
accuracy and performance with arbitrary-precision floating-point arithmetic.

Functions:
    sqrt(x): Compute the square root of x using a hybrid algorithm.
    cbrt(x): Compute the cube root of x.

Example:
    from flexfloat.math.sqrt import sqrt, cbrt
    from flexfloat.core import FlexFloat

    x = FlexFloat.from_float(9.0)
    print(sqrt(x))  # 3.0
    print(cbrt(x))  # ~2.08
"""

from typing import Callable, Final, TypeAlias

from ..core import FlexFloat
from ..types import Number

_0_5: Final[FlexFloat] = FlexFloat.from_float(0.5)
_1: Final[FlexFloat] = FlexFloat.from_float(1.0)
_2: Final[FlexFloat] = FlexFloat.from_float(2.0)
_3: Final[FlexFloat] = FlexFloat.from_float(3.0)
_10: Final[FlexFloat] = FlexFloat.from_float(10.0)
_1000: Final[FlexFloat] = FlexFloat.from_float(1000.0)
_SMALL: Final[FlexFloat] = FlexFloat.from_float(1e-30)
_LARGE: Final[FlexFloat] = FlexFloat.from_float(1e40)

_ArithmeticOperation: TypeAlias = Callable[[FlexFloat, FlexFloat | Number], FlexFloat]
"""Type alias for arithmetic operations on FlexFloat instances.
This is used to define operations like addition, subtraction, multiplication, and
division between FlexFloat and Number types."""


def _sqrt_taylor_core(
    x: FlexFloat,
    max_terms: int = 100,
    tolerance: FlexFloat = FlexFloat.from_float(1e-16),
) -> FlexFloat:
    """Compute the square root of a FlexFloat in [0.5, 2] using a Taylor series.

    Uses the binomial expansion for sqrt(1+u), where u = x - 1. This is fast and
    accurate for values close to 1.

    Args:
        x (FlexFloat): Input value in [0.5, 2].
        max_terms (int, optional): Maximum number of terms. Defaults to 100.
        tolerance (FlexFloat, optional): Convergence threshold. Defaults to 1e-16.

    Returns:
        FlexFloat: The square root of x.
    """
    # Transform to √(1+u) form where u = x - 1
    u = x - _1
    tolerance = tolerance.abs()

    # Initialize result with first term: 1
    result = _1.copy()

    if u.is_zero():
        return result

    # Initialize for the series computation
    term = u / _2  # First term: u/2
    result += term

    # For subsequent terms, use the recurrence relation:
    # coefficient[n+1] = coefficient[n] * (1/2 - n) / (n + 1)
    coefficient = _0_5  # coefficient for u^1 term
    u_power = u.copy()  # u^1

    for n in range(1, max_terms):
        # Update coefficient: coeff[n+1] = coeff[n] * (1/2 - n) / (n + 1)
        coefficient = coefficient * (_0_5 - n) / (n + 1)

        # Update u power
        u_power = u_power * u  # u^(n+1)

        # Calculate new term
        term = coefficient * u_power
        result += term

        # Check for convergence
        if term.abs() < tolerance:
            break

    return result


def _sqrt_newton_raphson_core(
    x: FlexFloat,
    max_iterations: int = 100,
    tolerance: FlexFloat = FlexFloat.from_float(1e-16),
) -> FlexFloat:
    """Compute the square root of a FlexFloat using the Newton-Raphson method.

    This method is efficient for general positive values and converges rapidly.

    Args:
        x (FlexFloat): The input value (must be positive).
        max_iterations (int, optional): Maximum iterations. Defaults to 100.
        tolerance (FlexFloat, optional): Convergence threshold. Defaults to 1e-16.

    Returns:
        FlexFloat: The square root of x.
    """
    # Better initial guess strategy
    if x >= _1:
        # For x >= 1, use x/2 as initial guess, but ensure it's reasonable
        guess = x / _2
        # If x is very large, use a better approximation
        if x > _1000:
            # Use bit manipulation approach for better initial guess
            # For now, use a simple heuristic
            guess = x / _10
    else:
        # For 0 < x < 1, start with 1 (since sqrt(x) is between x and 1)
        guess = _1.copy()

    tolerance = tolerance.abs()

    for _ in range(max_iterations):
        # Newton-Raphson iteration: new_guess = (guess + x/guess) / 2
        x_over_guess = x / guess
        new_guess = (guess + x_over_guess) / _2

        # Check for convergence using relative error
        diff = (new_guess - guess).abs()
        relative_error = diff / new_guess.abs() if not new_guess.is_zero() else diff

        if relative_error < tolerance:
            return new_guess

        # Update guess for next iteration
        guess = new_guess

    return guess


def _scale_sqrt(
    x: FlexFloat,
    scale_up: bool,
    lower_bound: FlexFloat = FlexFloat.from_float(1e-20),
    upper_bound: FlexFloat = FlexFloat.from_float(1e20),
    scale_factor_sqrt: FlexFloat = FlexFloat.from_float(1024.0),
    scale_factor_sqrt_result: FlexFloat = FlexFloat.from_float(32.0),
) -> FlexFloat:
    """Scale a FlexFloat value for square root computation to avoid precision issues.

    Args:
        x (FlexFloat): The value to scale.
        scale_up (bool): If True, scale up; if False, scale down.
        lower_bound (FlexFloat, optional): Lower bound for scaling. Defaults to 1e-20.
        upper_bound (FlexFloat, optional): Upper bound for scaling. Defaults to 1e20.

    Returns:
        FlexFloat: The square root of the scaled value.
    """
    operation: _ArithmeticOperation = (
        FlexFloat.__truediv__ if scale_up else FlexFloat.__mul__
    )
    inverse_operation: _ArithmeticOperation = (
        FlexFloat.__mul__ if scale_up else FlexFloat.__truediv__
    )

    scale_count = 0

    while (x < lower_bound or x > upper_bound) and scale_count < 100:
        x = operation(x, scale_factor_sqrt)
        scale_count += 1

    scaled_result = _sqrt_newton_raphson_core(x)

    for _ in range(scale_count):
        scaled_result = inverse_operation(scaled_result, scale_factor_sqrt_result)

    return scaled_result


def sqrt(x: FlexFloat) -> FlexFloat:
    """Compute the square root of a FlexFloat using a hybrid algorithm.

    Selects the optimal method based on the input:
      - Taylor series for values near 1 (fast, accurate)
      - Newton-Raphson for general values
      - Scaling for very small or large values
    Handles special cases (NaN, zero, negative, infinity).

    Args:
        x (FlexFloat): The value to compute the square root of.

    Returns:
        FlexFloat: The square root of x.

    Raises:
        ValueError: If x is negative (returns NaN for real numbers).
    """
    # Handle special cases
    if x.is_nan():
        return FlexFloat.nan()

    if x.is_zero():
        return FlexFloat.zero()

    if x.sign:  # x < 0
        return FlexFloat.nan()  # Square root of negative number

    if x.is_infinity():
        return FlexFloat.infinity(sign=False)

    # Hybrid approach: use Taylor series for values close to 1, Newton-Raphson otherwise
    # Taylor series is much faster and equally accurate for values near 1
    if abs(x - _1) < FlexFloat.from_float(0.2):
        return _sqrt_taylor_core(x)

    # For extremely small values, use scaling to avoid precision issues
    if x < _SMALL:
        return _scale_sqrt(x, scale_up=False)

    # For extremely large values, use scaling to avoid numerical issues
    if x > _LARGE:
        return _scale_sqrt(x, scale_up=True)

    # For normal values, use the core algorithm
    return _sqrt_newton_raphson_core(x)


def cbrt(x: FlexFloat) -> FlexFloat:
    """Return the cube root of x.

    Args:
        x (FlexFloat): The value to compute the cube root of.

    Returns:
        FlexFloat: The cube root of x.
    """
    # Handle special cases
    if x.is_nan():
        return FlexFloat.nan()

    if x.is_zero():
        return FlexFloat.zero()

    if x.is_infinity():
        return FlexFloat.infinity(sign=x.sign)

    # For negative numbers, use the identity: cbrt(-x) = -cbrt(x)
    if x.sign:
        return -cbrt(-x)

    # Use the identity: cbrt(x) = x^(1/3) = exp(ln(x)/3)
    from .exponential import exp
    from .logarithmic import log

    return exp(log(x) / _3)
