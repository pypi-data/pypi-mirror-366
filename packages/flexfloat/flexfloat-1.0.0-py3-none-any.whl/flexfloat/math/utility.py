"""
Utility functions for FlexFloat math operations.

This module provides a wide range of utility functions for FlexFloat arithmetic,
including rounding, modular arithmetic, sign manipulation, error functions, gamma
functions, and more. These functions are designed to support advanced mathematical
operations and special functions for arbitrary-precision floating-point arithmetic.

Functions:
    floor(x): Return the floor of x.
    ceil(x): Return the ceiling of x.
    fmod(x, y): Return the remainder of x divided by y.
    copysign(x, y): Return a FlexFloat with the magnitude of x and the sign of y.
    fabs(x): Return the absolute value of x.
    isinf(x): Check if x is infinity.
    isnan(x): Check if x is NaN.
    isfinite(x): Check if x is finite.
    trunc(x): Truncate x towards zero.
    ulp(x): Return the unit in the last place of x.
    fma(x, y, z): Return (x * y) + z with extended precision.
    dist(p, q): Return the Euclidean distance between two points.
    hypot(*coordinates): Return the Euclidean norm of coordinates.
    isclose(a, b, ...): Check if two values are close within a tolerance.
    ldexp(x, i): Return x * (2**i).
    frexp(x): Decompose x into mantissa and exponent.
    fsum(seq): Accurately sum a sequence of values.
    modf(x): Split x into fractional and integer parts.
    remainder(x, y): Return the IEEE 754-style remainder.
    nextafter(x, y, ...): Return the next representable value after x towards y.
    erf(x): Return the error function of x.
    erfc(x): Return the complementary error function of x.
    gamma(x): Return the gamma function of x.
    lgamma(x): Return the natural logarithm of the absolute value of the gamma function.

Example:
    from flexfloat.math.utility import floor, ceil, erf, gamma
    from flexfloat.core import FlexFloat

    x = FlexFloat.from_float(3.7)
    print(floor(x))  # 3.0
    print(ceil(x))   # 4.0
    print(erf(x))    # Error function value
    print(gamma(x))  # Gamma function value
"""

from typing import Final, Iterable

from ..bitarray import BitArray
from ..core import FlexFloat
from .constants import e, pi
from .exponential import exp, pow
from .sqrt import sqrt

# Internal constants for calculations
_0_5: Final[FlexFloat] = FlexFloat.from_float(0.5)
_0_75: Final[FlexFloat] = FlexFloat.from_float(0.75)
_0_8: Final[FlexFloat] = FlexFloat.from_float(0.8)
_1: Final[FlexFloat] = FlexFloat.from_float(1.0)
_1_5: Final[FlexFloat] = FlexFloat.from_float(1.5)
_2: Final[FlexFloat] = FlexFloat.from_float(2.0)
_2_2: Final[FlexFloat] = FlexFloat.from_float(2.2)
_2_5: Final[FlexFloat] = FlexFloat.from_float(2.5)
_3: Final[FlexFloat] = FlexFloat.from_int(3)
_3_5: Final[FlexFloat] = FlexFloat.from_float(3.5)
_4_5: Final[FlexFloat] = FlexFloat.from_float(4.5)
_5: Final[FlexFloat] = FlexFloat.from_int(5)
_6: Final[FlexFloat] = FlexFloat.from_int(6)
_7: Final[FlexFloat] = FlexFloat.from_float(7.0)
_8: Final[FlexFloat] = FlexFloat.from_int(8)
_9: Final[FlexFloat] = FlexFloat.from_int(9)
_10: Final[FlexFloat] = FlexFloat.from_int(10)
_11: Final[FlexFloat] = FlexFloat.from_int(11)
_12: Final[FlexFloat] = FlexFloat.from_int(12)
_20: Final[FlexFloat] = FlexFloat.from_int(20)
_50: Final[FlexFloat] = FlexFloat.from_int(50)
_288: Final[FlexFloat] = FlexFloat.from_int(288)
_360: Final[FlexFloat] = FlexFloat.from_int(360)

_N_2_5: Final[FlexFloat] = FlexFloat.from_float(-2.5)
_2_SQRT_PI: Final[FlexFloat] = _2 / sqrt(pi)

_GAMMA_LANZCOS_COEFF: Final[list[FlexFloat]] = [
    FlexFloat.from_float(0.99999999999980993),
    FlexFloat.from_float(676.5203681218851),
    FlexFloat.from_float(-1259.1392167224028),
    FlexFloat.from_float(771.32342877765313),
    FlexFloat.from_float(-176.61502916214059),
    FlexFloat.from_float(12.507343278686905),
    FlexFloat.from_float(-0.13857109526572012),
    FlexFloat.from_float(9.9843695780195716e-6),
    FlexFloat.from_float(1.5056327351493116e-7),
]


def floor(x: FlexFloat) -> FlexFloat:
    """Return the floor of x as a FlexFloat.

    Args:
        x (FlexFloat): The value to compute the floor of.

    Returns:
        FlexFloat: The largest integer less than or equal to x.
    """
    if x.is_nan() or x.is_infinity():
        return x.copy()

    x_int = int(x)
    recasted_x = FlexFloat.from_int(x_int)
    return FlexFloat.from_int(x_int - (1 if x < recasted_x else 0))


def ceil(x: FlexFloat) -> FlexFloat:
    """Return the ceiling of x as a FlexFloat.

    Args:
        x (FlexFloat): The value to compute the ceiling of.

    Returns:
        FlexFloat: The smallest integer greater than or equal to x.
    """
    if x.is_nan() or x.is_infinity():
        return x.copy()

    x_int = int(x)
    recasted_x = FlexFloat.from_int(x_int)
    return FlexFloat.from_int(x_int + (1 if x > recasted_x else 0))


def fmod(x: FlexFloat, y: FlexFloat) -> FlexFloat:
    """Return the remainder of x divided by y (modulo operation).

    Args:
        x (FlexFloat): The dividend value.
        y (FlexFloat): The divisor value.

    Returns:
        FlexFloat: The remainder of x divided by y.
    """
    if y.is_zero():
        return FlexFloat.nan()  # Handle division by zero
    quotient = floor(x / y)
    return x - (y * quotient)


def copysign(x: FlexFloat, y: FlexFloat) -> FlexFloat:
    """Return a FlexFloat with the magnitude of x and the sign of y.

    Args:
        x (FlexFloat): The value to use the magnitude from.
        y (FlexFloat): The value to use the sign from.

    Returns:
        FlexFloat: A FlexFloat with the magnitude of x and the sign of y.
    """
    result = x.abs()
    if y.sign:
        result = -result
    return result


def fabs(x: FlexFloat) -> FlexFloat:
    """Return the absolute value of x as a FlexFloat.

    Args:
        x (FlexFloat): The value to compute the absolute value of.

    Returns:
        FlexFloat: The absolute value of x.
    """
    return abs(x)


def isinf(x: FlexFloat) -> bool:
    """Check if x is positive or negative infinity.

    Args:
        x (FlexFloat): The value to check.

    Returns:
        bool: True if x is infinity, False otherwise.
    """
    return x.is_infinity()


def isnan(x: FlexFloat) -> bool:
    """Check if x is NaN (not a number).

    Args:
        x (FlexFloat): The value to check.

    Returns:
        bool: True if x is NaN, False otherwise.
    """
    return x.is_nan()


def isfinite(x: FlexFloat) -> bool:
    """Check if x is finite (not NaN or infinity).

    Args:
        x (FlexFloat): The value to check.

    Returns:
        bool: True if x is finite, False otherwise.
    """
    return not (x.is_nan() or x.is_infinity())


def trunc(x: FlexFloat) -> FlexFloat:
    """Return the integer part of x, truncated towards zero.

    Args:
        x (FlexFloat): The value to truncate.

    Returns:
        FlexFloat: The integer part of x.
    """
    return ceil(x) if x.sign else floor(x)


def ulp(x: FlexFloat) -> FlexFloat:
    """Return the unit in the last place (ULP) of x.

    Args:
        x (FlexFloat): The value to compute the ULP of.

    Returns:
        FlexFloat: The ULP of x.
    """
    import math

    if x.is_nan() or x.is_infinity() or x.is_zero():
        return FlexFloat.nan()

    # Use Python's math.ulp function as reference and convert result
    x_float = x.to_float()
    ulp_value = math.ulp(x_float)
    return FlexFloat.from_float(ulp_value)


def fma(x: FlexFloat, y: FlexFloat, z: FlexFloat) -> FlexFloat:
    """Return (x * y) + z with extended precision.

    Args:
        x (FlexFloat): The first multiplicand.
        y (FlexFloat): The second multiplicand.
        z (FlexFloat): The value to add.

    Returns:
        FlexFloat: The result of (x * y) + z.
    """
    return (x * y) + z


def dist(p: Iterable[FlexFloat], q: Iterable[FlexFloat]) -> FlexFloat:
    """Return the Euclidean distance between two points p and q.

    Args:
        p (Iterable[FlexFloat]): The first point coordinates.
        q (Iterable[FlexFloat]): The second point coordinates.

    Returns:
        FlexFloat: The Euclidean distance between p and q.
    """
    from .sqrt import sqrt

    return sqrt(sum(((a - b) ** 2 for a, b in zip(p, q)), FlexFloat.zero()))


def hypot(*coordinates: FlexFloat) -> FlexFloat:
    """Return the Euclidean norm (L2 norm) of the given coordinates.

    Args:
        *coordinates (FlexFloat): The coordinates to compute the norm of.

    Returns:
        FlexFloat: The Euclidean norm of the coordinates.
    """
    from .sqrt import sqrt

    return sqrt(sum((coord**2 for coord in coordinates), FlexFloat.zero()))


def isclose(
    a: FlexFloat,
    b: FlexFloat,
    *,
    rel_tol: FlexFloat = FlexFloat.from_float(1e-09),
    abs_tol: FlexFloat = FlexFloat.from_float(0.0),
) -> bool:
    """Check if two FlexFloat values are close to each other within a tolerance.

    Args:
        a (FlexFloat): The first value to compare.
        b (FlexFloat): The second value to compare.
        rel_tol (FlexFloat, optional): Relative tolerance. Defaults to 1e-09.
        abs_tol: Absolute tolerance. Defaults to 0.0.

    Returns:
        bool: True if a and b are close within the given tolerances, False otherwise.
    """
    if a.is_nan() or b.is_nan():
        return False

    if a.is_infinity() or b.is_infinity():
        return a.is_infinity() and b.is_infinity() and a.sign == b.sign

    diff = (a - b).abs()
    return diff <= abs_tol or diff <= rel_tol * max(a.abs(), b.abs(), _1)


def ldexp(x: FlexFloat, i: int) -> FlexFloat:
    """Return x multiplied by 2 raised to the power i.

    Args:
        x (FlexFloat): The value to scale.
        i (int): The exponent value.

    Returns:
        FlexFloat: The result of x * (2**i).
    """
    return x * (_2**i)


def frexp(x: FlexFloat) -> tuple[FlexFloat, int]:
    """Decompose a FlexFloat into its mantissa and exponent.

    Args:
        x (FlexFloat): The value to decompose.

    Returns:
        tuple[FlexFloat, int]: (mantissa, exponent) such that x = mantissa *
            2**exponent.
    """
    bitarray = FlexFloat._bitarray_implementation  # type: ignore[attr-defined]
    return (
        FlexFloat(
            sign=x.sign,
            fraction=x.fraction,
            exponent=bitarray.from_bits([True] * 11),
        ),
        x.exponent.to_signed_int() + 2,
    )


def fsum(seq: Iterable[FlexFloat]) -> FlexFloat:
    """Accurately sum a sequence of FlexFloat values (sorted by exponent).

    Args:
        seq (Iterable[FlexFloat]): The sequence of values to sum.

    Returns:
        FlexFloat: The sum of the sequence.
    """
    return sum(
        sorted(seq, key=lambda x: -abs(x.exponent.to_signed_int())), FlexFloat.zero()
    )


def modf(x: FlexFloat) -> tuple[FlexFloat, FlexFloat]:
    """Split a FlexFloat into its fractional and integer parts.

    Args:
        x (FlexFloat): The value to split.

    Returns:
        tuple[FlexFloat, FlexFloat]: (fractional part, integer part), with the
            fractional part having the same sign as x.
    """
    int_part = floor(x) if x.to_float() >= 0 else ceil(x)
    frac_part = x - int_part
    return (frac_part, int_part)


def remainder(x: FlexFloat, y: FlexFloat) -> FlexFloat:
    """Return the IEEE 754-style remainder of x with respect to y.

    Args:
        x (FlexFloat): The dividend value.
        y (FlexFloat): The divisor value.

    Returns:
        FlexFloat: The IEEE 754-style remainder.
    """
    # TODO: Make it generic, so it works with any FlexFloat size
    if y.is_zero():
        return FlexFloat.nan()
    q = (x / y).to_float()
    n = int(round(q))
    # Round ties to even
    if abs(q - n) == 0.5:
        n = int(2 * round(q / 2.0))
    return x - y * FlexFloat.from_int(n)


def nextafter(x: FlexFloat, y: FlexFloat, *, steps: int | None = None) -> FlexFloat:
    """Return the next representable FlexFloat value after x towards y.

    This function returns the next representable floating-point value after x
    in the direction of y. If steps is provided, it advances steps times.

    This implementation works directly with FlexFloat's bit representation and
    supports arbitrary exponent sizes, unlike the standard library version
    which is limited to 64-bit IEEE 754 precision.

    Args:
        x (FlexFloat): The starting value.
        y (FlexFloat): The target value.
        steps (int | None, optional): The number of steps to take. Defaults to 1 step.

    Returns:
        FlexFloat: The next representable value after x towards y.

    Special cases:
        - nextafter(NaN, y) = NaN
        - nextafter(x, NaN) = NaN
        - nextafter(x, x) = x
        - nextafter(±∞, finite) moves towards finite values
        - nextafter(finite, ±∞) moves towards infinity
    """
    if x.is_nan() or y.is_nan():
        return FlexFloat.nan()

    if x == y:
        return x.copy()

    steps_to_take = 1 if steps is None else abs(steps)
    if steps_to_take == 0:
        return x.copy()

    result = x.copy()
    direction = 1 if y > x else -1

    for _ in range(steps_to_take):
        result = _nextafter_single_step(result, direction)
        if result == y:
            break

    return result


def _nextafter_single_step(x: FlexFloat, direction: int) -> FlexFloat:
    """Take a single step towards the next representable value.

    Args:
        x (FlexFloat): The starting value.
        direction (int): 1 for increasing, -1 for decreasing.

    Returns:
        FlexFloat: The next representable value in the given direction.
    """
    # Handle special cases
    if x.is_nan():
        return FlexFloat.nan()

    # Handle infinity cases
    if x.is_infinity():
        if direction > 0 and not x.sign:
            # +inf towards larger values stays +inf
            return x.copy()
        elif direction < 0 and x.sign:
            # -inf towards smaller values stays -inf
            return x.copy()

        # Moving away from infinity towards finite values
        # Return the largest/smallest finite representable value
        return _get_extreme_finite_value(x.sign == (direction > 0))

    # Handle zero
    if x.is_zero():
        return (
            _get_smallest_positive_value()
            if direction > 0
            else _get_smallest_negative_value()
        )

    # For finite non-zero values, we need to manipulate the bit representation
    # Direction depends on both the sign and the requested direction
    if (not x.sign and direction > 0) or (x.sign and direction < 0):
        # Moving away from zero (increasing magnitude)
        return _increment_magnitude(x)
    # Moving towards zero (decreasing magnitude)
    return _decrement_magnitude(x)


def _get_extreme_finite_value(negative: bool) -> FlexFloat:
    """Get the largest finite representable value (positive or negative).

    Args:
        negative (bool): True for most negative, False for most positive.

    Returns:
        FlexFloat: The extreme finite value.
    """
    # Start with a base FlexFloat to get the right BitArray implementation
    result = FlexFloat.from_float(1.0)

    # Create maximum exponent (all 1s except the last bit which would make it infinity)
    # For standard IEEE 754, max exponent is 11111111110
    # (0x7FE in big-endian, 0x3FF in offset)
    for i in range(len(result.exponent)):
        result.exponent[i] = i < (len(result.exponent) - 1)  # All 1s except MSB

    # Create maximum fraction (all 1s)
    for i in range(len(result.fraction)):
        result.fraction[i] = True

    result.sign = negative
    return result


def _get_smallest_positive_value() -> FlexFloat:
    """Get the smallest positive representable value (subnormal minimum).

    Returns:
        FlexFloat: The smallest positive value.
    """
    # Start with zero and set the LSB of the fraction
    result = FlexFloat.zero()
    result.fraction[0] = True  # Set the least significant bit
    return result


def _get_smallest_negative_value() -> FlexFloat:
    """Get the smallest negative representable value (most negative subnormal).

    Returns:
        FlexFloat: The smallest negative value.
    """
    # Start with zero and set the LSB of the fraction and sign
    result = FlexFloat.zero()
    result.fraction[0] = True  # Set the least significant bit
    result.sign = True
    return result


def _increment_magnitude(x: FlexFloat) -> FlexFloat:
    """Increment the magnitude of a finite non-zero value.

    Args:
        x (FlexFloat): The value to increment.

    Returns:
        FlexFloat: The value with incremented magnitude.
    """
    result = x.copy()

    # Try to increment the fraction first (add 1 to the least significant bit)
    carry = True
    for i in range(len(result.fraction)):
        if carry:
            if result.fraction[i]:
                result.fraction[i] = False
                # Carry continues
            else:
                result.fraction[i] = True
                carry = False
                break

    # If we still have a carry, we need to increment the exponent
    if carry:
        # Increment exponent
        exponent_carry = True
        for i in range(len(result.exponent)):
            if exponent_carry:
                if result.exponent[i]:
                    result.exponent[i] = False
                    # Carry continues
                else:
                    result.exponent[i] = True
                    exponent_carry = False
                    break

        # If exponent overflowed, we need to grow it or handle infinity
        if exponent_carry:
            # Check if this would create infinity
            if _would_create_infinity(result.exponent):
                return FlexFloat.infinity(sign=result.sign)
            # We need to grow the exponent, but this is complex to do manually
            # For now, we'll handle this by using the existing arithmetic operations
            # Add the smallest possible increment by creating a value with the same
            # exponent but minimal fraction and adding it
            min_increment = FlexFloat.zero()
            # Copy the exponent structure but with a minimal value
            for i in range(len(result.exponent)):
                min_increment.exponent[i] = result.exponent[i]
            # Reset fraction to minimal value
            min_increment.fraction[0] = True
            min_increment.sign = result.sign

            # This might overflow to infinity, which is correct behavior
            return result + min_increment

    return result


def _decrement_magnitude(x: FlexFloat) -> FlexFloat:
    """Decrement the magnitude of a finite non-zero value.

    Args:
        x (FlexFloat): The value to decrement.

    Returns:
        FlexFloat: The value with decremented magnitude.
    """
    result = x.copy()

    # Try to decrement the fraction first (subtract 1 from the least significant bit)
    borrow = True
    for i in range(len(result.fraction)):
        if borrow:
            if result.fraction[i]:
                result.fraction[i] = False
                borrow = False
                break
            result.fraction[i] = True
            # Borrow continues

    # If we still have a borrow, we need to decrement the exponent
    if borrow:
        # Check if exponent is zero (would underflow to subnormal/zero)
        if all(not bit for bit in result.exponent):
            # Already at minimum exponent, return zero
            return FlexFloat.zero(sign=result.sign)

        # Decrement exponent
        exponent_borrow = True
        for i in range(len(result.exponent)):
            if exponent_borrow:
                if result.exponent[i]:
                    result.exponent[i] = False
                    exponent_borrow = False
                    break
                result.exponent[i] = True
                # Borrow continues

        # Set all fraction bits to 1 (since we borrowed from exponent)
        for i in range(len(result.fraction)):
            result.fraction[i] = True

    return result


def _would_create_infinity(exponent: "BitArray") -> bool:
    """Check if incrementing this exponent would create infinity.

    Args:
        exponent (BitArray): The exponent to check.

    Returns:
        bool: True if incrementing would create infinity.
    """
    # In IEEE 754, infinity is when all exponent bits are 1
    # Check if current exponent is all 1s except possibly the last bit
    exponent_value = exponent.to_signed_int()
    max_normal_exponent = (1 << (len(exponent) - 1)) - 2  # Reserve all-1s for infinity

    return exponent_value >= max_normal_exponent


# Unimplemented functions that raise NotImplementedError
def erf(x: FlexFloat) -> FlexFloat:
    """Return the error function of x.

    The error function is defined as:
    erf(x) = (2/√π) * ∫[0 to x] e^(-t²) dt

    This implementation uses Abramowitz and Stegun approximation for |x| < 2.2,
    and asymptotic expansion for larger values.

    Args:
        x (FlexFloat): The value to compute the error function of.

    Returns:
        FlexFloat: The error function value erf(x).

    Special cases:
        - erf(NaN) = NaN
        - erf(+∞) = 1
        - erf(-∞) = -1
        - erf(0) = 0
        - erf(-x) = -erf(x) (odd function)
    """
    # Handle special cases
    if x.is_nan():
        return x.copy()

    if x.is_infinity():
        return _1.copy() if not x.sign else -_1.copy()

    if x.is_zero():
        return FlexFloat.zero()

    # Use the odd function property: erf(-x) = -erf(x)
    if x.sign:
        return -erf(-x)

    # For small values, use Taylor series
    if x < _0_5:
        return _erf_taylor_series(x)

    # For moderate values (0.5 <= x < 2.2), use Abramowitz and Stegun approximation
    if x < _2_2:
        return _erf_abramowitz_stegun(x)

    # For large values, use asymptotic expansion
    if x < _6:
        return _erf_asymptotic(x)

    # For very large values, erf(x) ≈ 1
    return _1.copy()


def _erf_taylor_series(
    x: FlexFloat,
    max_terms: int = 50,
    tolerance: FlexFloat = FlexFloat.from_float(1e-16),
) -> FlexFloat:
    """Compute erf(x) using Taylor series for small x.

    erf(x) = (2/√π) * [x - x³/3 + x⁵/(2!*5) - x⁷/(3!*7) + ...]
           = (2/√π) * Σ[n=0 to ∞] (-1)ⁿ * x^(2n+1) / (n! * (2n+1))

    Args:
        x (FlexFloat): The input value (should be small for good convergence).
        max_terms (int, optional): Maximum number of terms. Defaults to 50.
        tolerance (FlexFloat, optional): Convergence threshold. Defaults to 1e-16.
    """
    result = x.copy()
    x_squared = x * x
    term = x.copy()

    for n in range(1, max_terms):
        # Next term: (-1)^n * x^(2n+1) / (n! * (2n+1))
        term = -term * x_squared / n
        term_contribution = term / (2 * n + 1)
        result += term_contribution

        if term_contribution.abs() < tolerance:
            break

    return _2_SQRT_PI * result


def _erf_abramowitz_stegun(
    x: FlexFloat,
    p: FlexFloat = FlexFloat.from_float(0.3275911),
    a1: FlexFloat = FlexFloat.from_float(0.254829592),
    a2: FlexFloat = FlexFloat.from_float(-0.284496736),
    a3: FlexFloat = FlexFloat.from_float(1.421413741),
    a4: FlexFloat = FlexFloat.from_float(-1.453152027),
    a5: FlexFloat = FlexFloat.from_float(1.061405429),
) -> FlexFloat:
    """Compute erf(x) using Abramowitz and Stegun approximation.

    Uses the approximation:
    erf(x) ≈ 1 - (a₁t + a₂t² + a₃t³ + a₄t⁴ + a₅t⁵) * e^(-x²)
    where t = 1/(1 + px) and p = 0.3275911

    Maximum error is about 1.5e-7.
    """
    from .exponential import exp

    t = _1 / (_1 + p * x)
    exp_term = exp(-(x * x))

    polynomial = a1 * t + a2 * (t**2) + a3 * (t**3) + a4 * (t**4) + a5 * (t**5)

    return _1 - polynomial * exp_term


def _erf_asymptotic(x: FlexFloat) -> FlexFloat:
    """Compute erf(x) using asymptotic expansion for large x.

    Uses: erf(x) ≈ 1 - (e^(-x²)/(x√π)) * [1 - 1/(2x²) + 3/(4x⁴) - ...]
    """
    x_squared = x * x
    exp_term = exp(-x_squared)
    sqrt_pi_x = sqrt(pi) * x

    # First few terms of the asymptotic series
    series = _1 - _1 / (_2 * x_squared) + _0_75 / (x_squared**_2)

    return _1 - (exp_term / sqrt_pi_x) * series


def _erfc_continued_fraction(x: FlexFloat) -> FlexFloat:
    """Compute erfc(x) using continued fraction representation.

    Uses the continued fraction:
    erfc(x) = (e^(-x²)/(x√π)) * (1/(1 + a₁/(1 + a₂/(1 + a₃/...))))
    where aₙ = n/(2x²)

    This method works well for x > 0.8 and provides high precision.
    """
    from .exponential import exp
    from .sqrt import sqrt

    x_squared = x * x
    exp_term = exp(-x_squared)
    sqrt_pi_x = sqrt(pi) * x

    # For smaller x values, we need more terms and better convergence
    # Adjust the number of terms based on x value for optimal precision
    if x < _1_5:
        max_terms = 50  # More terms for smaller x
    elif x < _2_5:
        max_terms = 30  # Moderate terms for medium x
    else:
        max_terms = 20  # Fewer terms for larger x

    # Evaluate continued fraction from bottom up
    cf = FlexFloat.zero()
    for n in range(max_terms, 0, -1):
        a_n = FlexFloat.from_int(n) / (_2 * x_squared)
        cf = a_n / (_1 + cf)

    return (exp_term / sqrt_pi_x) / (_1 + cf)


def erfc(x: FlexFloat) -> FlexFloat:
    """Return the complementary error function of x.

    The complementary error function is defined as:
    erfc(x) = 1 - erf(x) = (2/√π) * ∫[x to ∞] e^(-t²) dt

    This function is computed as erfc(x) = 1 - erf(x) for most values,
    but uses direct computation for large positive values to avoid
    precision loss from subtracting two numbers close to 1.

    Args:
        x (FlexFloat): The value to compute the complementary error function of.

    Returns:
        FlexFloat: The complementary error function value erfc(x).

    Special cases:
        - erfc(NaN) = NaN
        - erfc(+∞) = 0
        - erfc(-∞) = 2
        - erfc(0) = 1
    """
    # Handle special cases
    if x.is_nan():
        return x.copy()

    if x.is_infinity():
        return FlexFloat.zero() if not x.sign else _2.copy()

    if x.is_zero():
        return _1.copy()

    # For large positive values, compute directly to avoid precision loss
    if x > _4_5:
        return _erfc_asymptotic_direct(x)

    # For values around 2.5-4.5, use continued fraction for better precision
    if x > _2_5:
        return _erfc_continued_fraction(x)

    # For moderate positive values (0.8-2.5), use continued fraction with higher
    # precision
    if x > _0_8:
        return _erfc_continued_fraction(x)

    # For large negative values, use erfc(-x) = 2 - erfc(x)
    if x < -_1:
        if x < -_4_5:
            return _2 - _erfc_asymptotic_direct(-x)
        elif x < _N_2_5:
            return _2 - _erfc_continued_fraction(-x)
        return _2 - _erfc_continued_fraction(-x)

    # For small values around zero, use erfc(x) = 1 - erf(x)
    return _1 - erf(x)


def _erfc_asymptotic_direct(x: FlexFloat) -> FlexFloat:
    """Compute erfc(x) directly for large positive x using asymptotic expansion.

    Uses: erfc(x) ≈ (e^(-x²)/(x√π)) *
        [1 - 1/(2x²) + 3/(4x⁴) - 15/(8x⁶) + 105/(16x⁸) - ...]

    The general term is: (-1)^n * (2n-1)!! / (2^n * x^(2n))

    This avoids precision loss from computing 1 - erf(x) when erf(x) ≈ 1.
    """
    from .exponential import exp
    from .sqrt import sqrt

    x_squared = x * x
    exp_term = exp(-x_squared)
    sqrt_pi_x = sqrt(pi) * x

    # Compute asymptotic series with sufficient terms for accuracy
    # The series: 1 - 1/(2x²) + 3/(4x⁴) - 15/(8x⁶) + 105/(16x⁸) - 945/(32x¹⁰) + ...

    inv_x_squared = _1 / x_squared
    two_inv_x_squared = inv_x_squared / _2

    series = _1
    term = two_inv_x_squared  # First term: 1/(2x²)
    series -= term

    # Build subsequent terms iteratively to maintain precision
    # Each term: term_n = term_{n-1} * (2n-1) * (2n-3) / (2 * x²)
    term *= _3 * two_inv_x_squared  # 3/(4x⁴)
    series += term

    term *= _5 * two_inv_x_squared  # 15/(8x⁶)
    series -= term

    # Add more terms for better accuracy, especially around x=4
    if x >= _3_5:
        term *= _7 * two_inv_x_squared  # 105/(16x⁸)
        series += term

        if x < _8:  # For moderate values, add even more terms
            term *= _9 * two_inv_x_squared  # 945/(32x¹⁰)
            series -= term

            if x < _6:  # For x around 4-6, add one more term
                term *= _11 * two_inv_x_squared  # 10395/(64x¹²)
                series += term

    return (exp_term / sqrt_pi_x) * series


def _gamma_lanczos_approximation(x: FlexFloat) -> FlexFloat:
    """Compute gamma function using Lanczos approximation.

    This implementation uses the Lanczos approximation, which is accurate
    for moderate values of x. The coefficients are optimized for double precision.

    Args:
        x (FlexFloat): The value to compute gamma of (should be > 0.5).

    Returns:
        FlexFloat: The computed gamma value.
    """
    from .exponential import exp
    from .sqrt import sqrt

    # Lanczos coefficients for g = 7, n = 9
    g = _7

    # Use the identity Γ(z+1) = z*Γ(z) to shift x to > 1 if needed
    x_shifted = x.copy()
    shift_product = _1.copy()

    while x_shifted < _1:
        shift_product *= x_shifted
        x_shifted += _1

    z = x_shifted - _1

    # Compute the Lanczos sum
    lanczos_sum = _GAMMA_LANZCOS_COEFF[0].copy()
    for i in range(1, len(_GAMMA_LANZCOS_COEFF)):
        lanczos_sum += _GAMMA_LANZCOS_COEFF[i] / (z + i)

    # Compute the gamma function using Lanczos formula
    # Γ(z+1) = √(2π) * (z+g+0.5)^(z+0.5) * e^(-z-g-0.5) * A_g(z)
    z_plus_g_half = z + g + _0_5

    # Calculate each component
    sqrt_2pi = sqrt(_2 * pi)
    power_term = pow(z_plus_g_half, z + _0_5)
    exp_term = exp(-(z + g + _0_5))

    result = sqrt_2pi * power_term * exp_term * lanczos_sum

    # Apply the shift correction if we shifted the input
    return result / shift_product


def _gamma_stirling_approximation(x: FlexFloat) -> FlexFloat:
    """Compute gamma function using Stirling's approximation for large x.

    Uses the asymptotic expansion: Γ(x) ≈ √(2π/x) * (x/e)^x * (1 + 1/(12x) + ...)

    Args:
        x (FlexFloat): The value to compute gamma of (should be large, > 10).

    Returns:
        FlexFloat: The computed gamma value.
    """
    from .sqrt import sqrt

    sqrt_2pi_over_x = sqrt(_2 * pi / x)
    x_over_e_to_x = pow(x / e, x)

    # First-order correction term: 1 + 1/(12*x)
    correction = _1 + _1 / (_12 * x)

    # For very high precision, we could add more terms:
    # + 1/(288*x²) - 139/(51840*x³) + ...
    if x > _50:
        x_squared = x * x
        correction += _1 / (_288 * x_squared)

    return sqrt_2pi_over_x * x_over_e_to_x * correction


def gamma(x: FlexFloat) -> FlexFloat:
    """Return the gamma function of x.

    The gamma function is defined as Γ(x) = ∫₀^∞ t^(x-1) * e^(-t) dt.
    For positive integers n, Γ(n) = (n-1)!.

    This implementation uses:
    - Direct calculation for small integer values
    - Lanczos approximation for moderate values
    - Stirling's approximation for large values
    - Reflection formula for negative values

    Args:
        x (FlexFloat): The value to compute the gamma function of.

    Returns:
        FlexFloat: The gamma function value Γ(x).

    Special cases:
        - gamma(NaN) = NaN
        - gamma(+∞) = +∞
        - gamma(-∞) = NaN
        - gamma(0) = +∞ (with sign depending on approach)
        - gamma(negative integer) = NaN
    """
    from .constants import pi
    from .trigonometric import sin

    # Handle special cases
    if x.is_nan():
        return x.copy()

    if x.is_infinity():
        if x.sign:  # negative infinity
            return FlexFloat.nan()
        else:  # positive infinity
            return x.copy()

    if x.is_zero():
        # gamma(0) is +∞, but we need to consider the sign based on the approach
        # direction. For simplicity, return +∞
        return FlexFloat.infinity()

    # Check for negative integers (gamma is undefined there)
    if x.sign and x == floor(x):
        return FlexFloat.nan()

    # For small positive integers, use the factorial identity: Γ(n) = (n-1)!
    if not x.sign and x <= FlexFloat.from_int(10) and x == floor(x):
        n = int(x)
        if n == 1:
            return _1.copy()
        result = _1.copy()
        for i in range(1, n):
            result *= FlexFloat.from_int(i)
        return result

    # For negative values, use the reflection formula: Γ(z)Γ(1-z) = π/sin(πz)
    if x.sign:
        # Γ(x) = π / (sin(π*x) * Γ(1-x))
        one_minus_x = _1 - x
        sin_pi_x = sin(pi * x)

        if sin_pi_x.is_zero():
            return FlexFloat.nan()  # At negative integers

        gamma_1_minus_x = gamma(one_minus_x)
        return pi / (sin_pi_x * gamma_1_minus_x)

    # For large positive values, use Stirling's approximation
    if x > _20:
        return _gamma_stirling_approximation(x)

    # For moderate positive values, use Lanczos approximation
    return _gamma_lanczos_approximation(x)


def lgamma(x: FlexFloat) -> FlexFloat:
    """Return the natural logarithm of the absolute value of the gamma function.

    This function computes ln(|Γ(x)|), which is useful for avoiding overflow
    when computing the gamma function of large arguments.

    Args:
        x (FlexFloat): The value to compute the logarithm of the gamma function of.

    Returns:
        FlexFloat: The natural logarithm of the absolute value of Γ(x).

    Special cases:
        - lgamma(NaN) = NaN
        - lgamma(+∞) = +∞
        - lgamma(-∞) = +∞
        - lgamma(0) = +∞
        - lgamma(negative integer) = +∞
    """
    from .logarithmic import log
    from .trigonometric import sin

    # Handle special cases
    if x.is_nan():
        return x.copy()

    if x.is_infinity():
        return FlexFloat.infinity()  # Both +∞ and -∞ give +∞

    if x.is_zero():
        return FlexFloat.infinity()

    # For negative integers, lgamma is +∞
    if x.sign and x == floor(x):
        return FlexFloat.infinity()

    # For small positive integers, use log of factorial
    if not x.sign and x <= _10 and x == floor(x):
        n = int(x)
        if n == 1:
            return FlexFloat.zero()  # ln(Γ(1)) = ln(0!) = ln(1) = 0
        result = FlexFloat.zero()
        for i in range(1, n):
            result += log(FlexFloat.from_int(i))
        return result

    # For negative values, use the reflection formula
    # ln|Γ(x)| = ln(π) - ln|sin(πx)| - ln|Γ(1-x)|
    if x.sign:
        one_minus_x = _1 - x
        sin_pi_x = sin(pi * x)

        if sin_pi_x.is_zero():
            return FlexFloat.infinity()

        lgamma_1_minus_x = lgamma(one_minus_x)
        return log(pi) - log(sin_pi_x.abs()) - lgamma_1_minus_x

    # For large positive values, use Stirling's approximation in log form
    # ln(Γ(x)) ≈ (x-0.5)*ln(x) - x + 0.5*ln(2π) + 1/(12x) + ...
    if x > _20:
        from .logarithmic import log

        x_minus_half = x - _0_5
        ln_x = log(x)
        ln_2pi = log(_2 * pi)

        result = x_minus_half * ln_x - x + _0_5 * ln_2pi

        # Add correction terms
        correction = _1 / (_12 * x)
        if x > _50:
            correction -= _1 / (_360 * x * x * x)

        return result + correction

    # For moderate values, compute gamma and then take log
    gamma_x = gamma(x)
    if gamma_x.is_zero() or gamma_x.is_infinity():
        return FlexFloat.infinity()

    return log(gamma_x.abs())
