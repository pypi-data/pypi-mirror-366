Math Module
===========

The FlexFloat math module provides mathematical functions that work with FlexFloat numbers.

.. automodule:: flexfloat.math
   :members:
   :undoc-members:
   :show-inheritance:

Logarithmic Functions
=====================

.. autofunction:: flexfloat.math.log
   :no-index:
.. autofunction:: flexfloat.math.log2
   :no-index:
.. autofunction:: flexfloat.math.log10
   :no-index:

Exponential Functions
=====================

.. autofunction:: flexfloat.math.exp
   :no-index:

Power Functions
===============

.. autofunction:: flexfloat.math.sqrt
   :no-index:
.. autofunction:: flexfloat.math.pow
   :no-index:

Examples
--------

Logarithmic Operations
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat
   from flexfloat import math as ffmath

   x = FlexFloat.from_float(100.0)

   # Natural logarithm
   ln_x = ffmath.log(x)      # Natural log (base e)
   print(ln_x)

   # Base-2 logarithm  
   log2_x = ffmath.log2(x)
   print(log2_x)

   # Base-10 logarithm
   log10_x = ffmath.log10(x)
   print(log10_x)

Exponential Operations
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat
   from flexfloat import math as ffmath

   x = FlexFloat.from_float(2.0)

   # Natural exponential
   exp_x = ffmath.exp(x)
   print(exp_x)

Power Operations
~~~~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat
   from flexfloat import math as ffmath

   x = FlexFloat.from_float(16.0)
   y = FlexFloat.from_float(3.0)

   # Square root
   sqrt_x = ffmath.sqrt(x)
   print(sqrt_x)

   # General power
   pow_xy = ffmath.pow(x, y)
   print(pow_xy)

Working with Large Numbers
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat
   from flexfloat import math as ffmath

   # Large number operations
   large = FlexFloat.from_float(10) ** 100
   
   # Logarithm of large number
   log_large = ffmath.log10(large)
   print(log_large)

   # Square root of large number
   sqrt_large = ffmath.sqrt(large)
   print(sqrt_large)

Special Cases
~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat
   from flexfloat import math as ffmath

   zero = FlexFloat.zero()
   one = FlexFloat.from_float(1.0)
   inf = FlexFloat.infinity()

   # Logarithm special cases
   print(ffmath.log(one))    # 0.0
   print(ffmath.log(inf))    # infinity
   # ffmath.log(zero)        # would be negative infinity or error

   # Exponential special cases
   print(ffmath.exp(zero))   # 1.0
   print(ffmath.exp(inf))    # infinity

   # Power special cases
   print(ffmath.sqrt(zero))  # 0.0
   print(ffmath.sqrt(one))   # 1.0
   print(ffmath.pow(zero, one))  # 0.0
