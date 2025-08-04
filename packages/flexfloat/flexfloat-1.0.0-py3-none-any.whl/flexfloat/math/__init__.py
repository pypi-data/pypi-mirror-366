"""
flexfloat.math - Mathematical Functions for FlexFloat

This module provides mathematical functions for the FlexFloat type, mirroring the
interface and behavior of Python's built-in math module where possible, but operating on
arbitrary-precision floating-point numbers. All functions are designed to work with
FlexFloat objects, enabling high-precision and customizable floating-point arithmetic
for scientific, engineering, and numerical applications.

Features:
    - Implements core mathematical operations (exp, sqrt, pow, log, etc.) for FlexFloat.
    - Provides constants (e, pi, tau, inf, nan) as FlexFloat instances.
    - Handles special cases (NaN, infinity, zero) according to IEEE 754 semantics.
    - Uses numerically stable algorithms (Taylor series, Newton-Raphson,
        range reduction) for accuracy.
    - Designed to be a drop-in replacement for math functions in code using FlexFloat.

Example:
    from flexfloat.math import sqrt, exp, log, pi
    from flexfloat import FlexFloat
    a = FlexFloat.from_float(2.0)
    b = sqrt(a)
    print(f"sqrt(2) = {b}")
    print(f"exp(1) = {exp(FlexFloat.from_float(1.0))}")
    print(f"log(e) = {log(exp(FlexFloat.from_float(1.0)))}")
    print(f"pi = {pi}")
"""

# Import all public constants
from .constants import e, inf, nan, pi, tau

# Import all exponential and power functions
from .exponential import exp, expm1, pow

# Import floating point utilities
from .floating_point import copysign, fabs, isfinite, isinf, isnan

# Import all hyperbolic functions
from .hyperbolic import acosh, asinh, atanh, cosh, sinh, tanh

# Import all logarithmic functions
from .logarithmic import log, log1p, log2, log10

# Import all square root functions
from .sqrt import cbrt, sqrt

# Import all trigonometric functions
from .trigonometric import (
    acos,
    asin,
    atan,
    atan2,
    cos,
    degrees,
    radians,
    sin,
    tan,
)

# Import other utility functions
from .utility import (
    ceil,
    dist,
    erf,
    erfc,
    floor,
    fma,
    fmod,
    frexp,
    fsum,
    gamma,
    hypot,
    isclose,
    ldexp,
    lgamma,
    modf,
    nextafter,
    remainder,
    trunc,
    ulp,
)

__all__ = [
    # Constants
    "e",
    "inf",
    "nan",
    "pi",
    "tau",
    # Exponential and power functions
    "exp",
    "expm1",
    "pow",
    # Logarithmic functions
    "log",
    "log10",
    "log1p",
    "log2",
    # Square root functions
    "cbrt",
    "sqrt",
    # Trigonometric functions
    "acos",
    "asin",
    "atan",
    "atan2",
    "cos",
    "degrees",
    "radians",
    "sin",
    "tan",
    # Hyperbolic functions
    "acosh",
    "asinh",
    "atanh",
    "cosh",
    "sinh",
    "tanh",
    # Floating point utilities
    "copysign",
    "fabs",
    "isfinite",
    "isinf",
    "isnan",
    # Other utility functions
    "ceil",
    "dist",
    "erf",
    "erfc",
    "floor",
    "fma",
    "fmod",
    "frexp",
    "fsum",
    "gamma",
    "hypot",
    "isclose",
    "ldexp",
    "lgamma",
    "modf",
    "nextafter",
    "remainder",
    "trunc",
    "ulp",
]
