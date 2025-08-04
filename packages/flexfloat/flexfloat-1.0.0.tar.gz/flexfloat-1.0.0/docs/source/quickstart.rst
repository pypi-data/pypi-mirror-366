Quick Start Guide
=================

This guide will help you get started with FlexFloat 1.0.0 quickly.

Basic Usage
-----------

Creating FlexFloat Numbers
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat

   # Create from float or int
   x = FlexFloat.from_float(42.0)
   y = FlexFloat.from_float(3.14159)
   z = FlexFloat.from_int(1000)
   
   print(x)  # FlexFloat representation of 42.0
   print(y)  # FlexFloat representation of 3.14159
   print(z)  # FlexFloat representation of 1000

Arithmetic Operations
~~~~~~~~~~~~~~~~~~~~~

FlexFloat supports all basic arithmetic operations:

.. code-block:: python

   from flexfloat import FlexFloat

   a = FlexFloat.from_float(10.5)
   b = FlexFloat.from_float(2.5)

   # Addition
   result_add = a + b
   print(result_add)  # 1.30000e+01

   # Subtraction
   result_sub = a - b
   print(result_sub)  # 8.00000e+00

   # Multiplication
   result_mul = a * b
   print(result_mul)  # 2.62500e+01

   # Division
   result_div = a / b
   print(result_div)  # 4.20000e+00

   # Power
   result_pow = a ** 2
   print(result_pow)  # 1.10250e+02

Working with Large Numbers
~~~~~~~~~~~~~~~~~~~~~~~~~~

FlexFloat can handle numbers beyond the range of standard floats:

.. code-block:: python

   from flexfloat import FlexFloat

   # Create a very large number
   large = FlexFloat.from_float(10) ** 400
   print(large)  # 2.83672e+921

   # Arithmetic with large numbers
   larger = large * FlexFloat.from_float(2)
   print(larger)  # 5.67344e+921

   # Very small numbers
   small = FlexFloat.from_float(1) / (FlexFloat.from_float(10) ** 400)
   print(small)  # 3.52520e-922

Mathematical Functions
~~~~~~~~~~~~~~~~~~~~~~

FlexFloat 1.0.0 includes a comprehensive mathematical function library:

.. code-block:: python

   from flexfloat import FlexFloat
   from flexfloat.math import sin, cos, tan, pi, e, exp, log, sqrt

   x = FlexFloat.from_float(2.0)
   angle = pi / FlexFloat.from_float(4.0)  # π/4 radians

   # Trigonometric functions
   sin_result = sin(angle)     # sin(45°) ≈ 0.707
   cos_result = cos(angle)     # cos(45°) ≈ 0.707
   tan_result = tan(angle)     # tan(45°) = 1.0

   # Logarithmic functions
   log_result = log(x)         # Natural logarithm
   log10_result = log10(x)     # Base-10 logarithm
   log2_result = log2(x)       # Base-2 logarithm

   # Exponential functions
   exp_result = exp(x)         # e^x
   power_result = pow(x, FlexFloat.from_float(3.0))  # x^3

   # Square root
   sqrt_result = sqrt(x)       # √x

   # Mathematical constants
   print(f"π = {pi.to_float()}")
   print(f"e = {e.to_float()}")

Working with Large Numbers
~~~~~~~~~~~~~~~~~~~~~~~~~~

FlexFloat can handle numbers beyond the range of standard floats:

.. code-block:: python

   from flexfloat import FlexFloat

   # Create a very large number that would overflow standard float
   large_base = FlexFloat.from_float(1e308)
   large_result = large_base + large_base  # No overflow!
   
   # Factorial of large numbers
   def flex_factorial(n):
       result = FlexFloat.from_float(1.0)
       for i in range(1, n + 1):
           result = result * FlexFloat.from_float(i)
       return result
   
   # Calculate 100! without overflow
   factorial_100 = flex_factorial(100)
   print(f"100! has {len(str(factorial_100.to_int()))} digits")

   # Power functions
   sqrt_result = ffmath.sqrt(x)
   pow_result = ffmath.pow(x, FlexFloat.from_float(3))

Special Values
~~~~~~~~~~~~~~

FlexFloat supports IEEE 754 special values:

.. code-block:: python

   from flexfloat import FlexFloat

   # Infinity
   pos_inf = FlexFloat.infinity()
   print(pos_inf.is_infinity())  # True
   neg_inf = FlexFloat.infinity(sign=True)

   # NaN (Not a Number)
   nan = FlexFloat.nan()
   print(nan.is_nan())  # True

   # Zero
   zero = FlexFloat.zero()
   print(zero.is_zero())  # True

BitArray Backends
~~~~~~~~~~~~~~~~~

FlexFloat supports different BitArray implementations for optimal performance:

.. code-block:: python

   from flexfloat import FlexFloat, ListBoolBitArray, ListInt64BitArray, BigIntBitArray

   # Set the BitArray implementation globally
   FlexFloat.set_bitarray_implementation(ListBoolBitArray)
   x1 = FlexFloat.from_float(1.5)
   print(x1)  # 1.50000e+00
   FlexFloat.set_bitarray_implementation(ListInt64BitArray)
   x2 = FlexFloat.from_float(1.5)
   print(x2)  # 1.50000e+00
   FlexFloat.set_bitarray_implementation(BigIntBitArray)
   x3 = FlexFloat.from_float(1.5)
   print(x3)  # 1.50000e+00

   # All produce the same result but with different internal representations
   print(x1.to_float() == x2.to_float() == x3.to_float())  # True

String Representation
~~~~~~~~~~~~~~~~~~~~~

FlexFloat provides multiple string representations:

.. code-block:: python

   from flexfloat import FlexFloat

   x = FlexFloat.from_float(123.456)

   # Default representation
   print(str(x))  # 1.23456e+02

   # Detailed representation
   print(repr(x)) # FlexFloat(sign=False, exponent=10000000101, fraction=1110110111010010111100011010100111111011111001110111)
