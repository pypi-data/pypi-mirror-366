Core Concepts
=============

Understanding FlexFloat's Architecture
--------------------------------------

FlexFloat is designed around the concept of **growable exponents** and **fixed-size fractions**. This section explains the fundamental concepts that make FlexFloat unique.

IEEE 754 Foundation
~~~~~~~~~~~~~~~~~~~

FlexFloat builds upon the IEEE 754 double-precision floating-point standard:

- **Sign bit**: 1 bit indicating positive (0) or negative (1)
- **Exponent**: Variable length (starts at 11 bits for double precision)
- **Fraction**: Fixed at 52 bits (mantissa without implicit leading 1)

Traditional IEEE 754 Limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Standard double-precision floats have limitations:

- **Range**: Approximately ±1.8 × 10^308
- **Overflow**: Numbers beyond this range become infinity
- **Underflow**: Very small numbers become zero

FlexFloat's Innovation
~~~~~~~~~~~~~~~~~~~~~~

FlexFloat overcomes these limitations through:

1. **Growable Exponents**: When a number exceeds the current exponent range, FlexFloat automatically increases the exponent bit length
2. **Fixed Precision**: The fraction remains at 52 bits, maintaining consistent precision
3. **Seamless Transition**: Operations seamlessly handle the transition between different exponent sizes

Number Representation
---------------------

FlexFloat Structure
~~~~~~~~~~~~~~~~~~~

A FlexFloat number consists of:

.. code-block:: python

   FlexFloat(
       sign=False,           # Boolean: False=positive, True=negative
       exponent=BitArray,    # Variable-length exponent
       fraction=BitArray     # Fixed 52-bit fraction
   )

Example representations:

.. code-block:: python

   from flexfloat import FlexFloat

   # Standard double precision equivalent
   x = FlexFloat.from_float(1.5)
   print(f"Sign: {x.sign}")  # Sign: False
   print(f"Exponent length: {len(x.exponent)} bits")  # Exponent length: 11 bits
   print(f"Fraction length: {len(x.fraction)} bits")  # Fraction length: 52 bits

Exponent Growth
~~~~~~~~~~~~~~~

When an operation would cause overflow, FlexFloat grows the exponent:

.. code-block:: python

   from flexfloat import FlexFloat

   # Start with standard precision
   x = FlexFloat.from_float(10.0)
   print(f"Initial exponent length: {len(x.exponent)} bits")  # Initial exponent length: 11 bits

   # Perform operation that would overflow standard float
   large = x ** 400
   print(f"After large operation: {len(large.exponent)} bits")  # After large operation: 14 bits

Special Values
--------------

FlexFloat supports all IEEE 754 special values with extended range:

Infinity
~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat

   # Positive and negative infinity
   pos_inf = FlexFloat.infinity()
   neg_inf = FlexFloat.infinity(sign=True)

   # Infinity arithmetic
   result = pos_inf + FlexFloat.from_float(1000)  # Still positive infinity
   result = pos_inf * neg_inf                     # Negative infinity

NaN (Not a Number)
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat

   # Create NaN
   nan = FlexFloat.nan()

   # NaN propagation
   result = nan + FlexFloat.from_float(42)        # Result is NaN
   result = FlexFloat.zero() / FlexFloat.zero()   # Division by zero gives NaN

Zero Values
~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat

   # Zero value
   zero = FlexFloat.zero()

   # Zero arithmetic
   result = zero + zero        # Zero
   result = FlexFloat.from_float(1) * zero    # Zero

Precision and Accuracy
----------------------

Mantissa Precision
~~~~~~~~~~~~~~~~~~

FlexFloat maintains 52-bit fraction precision regardless of exponent size:

.. code-block:: python

   from flexfloat import FlexFloat

   # All these maintain the same fractional precision
   small = FlexFloat.from_float(1.23456789012345)
   medium = FlexFloat.from_float(1.23456789012345e100)
   large = FlexFloat.from_float(1.23456789012345e1000)

Rounding Behavior
~~~~~~~~~~~~~~~~~

FlexFloat follows IEEE 754 rounding rules:

- **Round to nearest, ties to even** (default)
- Consistent rounding across all operations
- Preserves mathematical properties

.. code-block:: python

   from flexfloat import FlexFloat

   # Rounding examples
   x = FlexFloat.from_float(1) / FlexFloat.from_float(3)     # 0.333...
   y = x * FlexFloat.from_float(3)                # Close to 1.0, with rounding

Comparison with Standard Floats
-------------------------------

Range Comparison
~~~~~~~~~~~~~~~~

.. list-table:: Range Comparison
   :header-rows: 1
   :widths: 30 35 35

   * - Type
     - Minimum Magnitude
     - Maximum Magnitude
   * - IEEE 754 Double
     - ~2.2 × 10^-308
     - ~1.8 × 10^308
   * - FlexFloat
     - Limited by memory
     - Limited by memory

Performance Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Standard range**: FlexFloat performs similarly to double precision
- **Extended range**: Some overhead due to dynamic exponent management
- **Memory usage**: Scales with exponent size

Use Cases
---------

FlexFloat is ideal for:

Scientific Computing
~~~~~~~~~~~~~~~~~~~~

- Astronomical calculations (very large distances)
- Quantum mechanics (very small scales)
- Numerical analysis requiring extended range

Financial Modeling
~~~~~~~~~~~~~~~~~~

- Long-term compound interest calculations
- Risk modeling with extreme scenarios
- High-precision currency conversions

Engineering Applications
~~~~~~~~~~~~~~~~~~~~~~~~

- Simulations requiring extended precision
- Control systems with wide dynamic ranges
- Signal processing with extreme values

Mathematical Research
~~~~~~~~~~~~~~~~~~~~~

- Number theory computations
- Iterative algorithms prone to overflow
- Exploration of mathematical constants
