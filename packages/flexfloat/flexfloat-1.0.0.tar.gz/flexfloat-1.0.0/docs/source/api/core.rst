Core API
========

This section documents the core FlexFloat class and its methods.

FlexFloat Class
---------------

.. autoclass:: flexfloat.FlexFloat
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __add__, __sub__, __mul__, __truediv__, __pow__, __eq__, __ne__, __lt__, __le__, __gt__, __ge__, __str__, __repr__, __float__, __int__, __bool__, pretty, abs, copy
   :no-index:

Class Methods
~~~~~~~~~~~~~

.. automethod:: flexfloat.FlexFloat.from_float
   :no-index:
.. automethod:: flexfloat.FlexFloat.nan
   :no-index:
.. automethod:: flexfloat.FlexFloat.infinity
   :no-index:
.. automethod:: flexfloat.FlexFloat.zero
   :no-index:
.. automethod:: flexfloat.FlexFloat.set_bitarray_implementation
   :no-index:

Instance Methods
~~~~~~~~~~~~~~~~

Type Checking
^^^^^^^^^^^^^

.. automethod:: flexfloat.FlexFloat.is_zero
   :no-index:
.. automethod:: flexfloat.FlexFloat.is_infinity
   :no-index:
.. automethod:: flexfloat.FlexFloat.is_nan
   :no-index:

Conversion Methods
^^^^^^^^^^^^^^^^^^

.. automethod:: flexfloat.FlexFloat.to_float
   :no-index:
.. automethod:: flexfloat.FlexFloat.copy
   :no-index:
.. automethod:: flexfloat.FlexFloat.abs
   :no-index:
.. automethod:: flexfloat.FlexFloat.pretty
   :no-index:

Examples
--------

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat

   # Create FlexFloat numbers
   x = FlexFloat.from_float(1.5)
   y = FlexFloat.from_float(2.5)

   # Arithmetic operations
   sum_result = x + y
   print(sum_result)  # 4.00000e+00
   product = x * y
   print(product)  # 3.75000e+00
   quotient = x / y
   print(quotient)  # 6.00000e-01
   power = x ** 2
   print(power)  # 2.25000e+00

Special Values
~~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat

   # Create special values
   inf = FlexFloat.infinity()
   nan = FlexFloat.nan()
   zero = FlexFloat.zero()

   # Check types
   print(inf.is_infinity())    # True
   print(nan.is_nan())         # True
   print(zero.is_zero())       # True
   print(inf)                  # inf
   print(nan)                  # nan
   print(zero)                 # 0.0

Large Numbers
~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat

   # Work with numbers beyond float range
   large = FlexFloat.from_float(10) ** 400
   very_large = large * FlexFloat.from_float(2)

   print(very_large)  # 5.67344e+921

Type Conversions
~~~~~~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat

   # From various types
   from_int = FlexFloat.from_float(42)
   from_float = FlexFloat.from_float(3.14159)

   # To various types
   as_float = from_float.to_float()

   # Copy and abs
   copy = from_float.copy()
   absolute = from_float.abs()

   # Pretty string
   print(from_float.pretty())  # FlexFloat(exponent=1, fraction=2570632149304942)
