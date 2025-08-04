FlexFloat 1.0.0 Documentation
=============================

.. image:: https://img.shields.io/badge/python-3.11+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.11+

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

.. image:: https://badge.fury.io/py/flexfloat.svg
   :target: https://badge.fury.io/py/flexfloat
   :alt: PyPI version

Welcome to FlexFloat 1.0.0, a high-precision Python library for arbitrary precision floating-point arithmetic with **growable exponents** and **fixed-size fractions**.

FlexFloat extends IEEE 754 double-precision format to handle numbers beyond the standard range while maintaining computational efficiency and precision consistency.

✨ Key Features
----------------

- **🔢 Growable Exponents**: Dynamically expand exponent size to handle extremely large (>10^308) or small (<10^-308) numbers
- **🎯 Fixed-Size Fractions**: Maintain IEEE 754-compatible 52-bit fraction precision for consistent accuracy
- **⚡ Full Arithmetic Support**: Addition, subtraction, multiplication, division, and power operations
- **📐 Complete Math Library**: Comprehensive mathematical functions including trigonometric, logarithmic, exponential, and hyperbolic functions
- **🔧 Multiple BitArray Backends**: Choose between bool-list, int64-list, and big-integer implementations for optimal performance
- **🌟 Special Value Handling**: Complete support for NaN, ±infinity, and zero values
- **🛡️ Overflow Protection**: Automatic exponent growth prevents overflow/underflow errors
- **📊 IEEE 754 Baseline**: Fully compatible with standard double-precision format as the starting point

🚀 Quick Start
---------------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install flexfloat

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from flexfloat import FlexFloat
   from flexfloat.math import sin, cos, pi, exp, log

   # Create FlexFloat numbers
   x = FlexFloat.from_float(1.5)
   y = FlexFloat.from_float(2.5)

   # Basic arithmetic
   result = x + y
   print(result.to_float())  # 4.0

   # Mathematical functions
   angle = pi / FlexFloat.from_float(4.0)  # π/4 radians
   sin_result = sin(angle)  # sin(45°) ≈ 0.707
   
   # Exponential and logarithmic functions
   exp_result = exp(x)      # e^1.5
   log_result = log(y)      # ln(2.5)

   # Handle very large numbers that would overflow standard floats
   large_a = FlexFloat.from_float(1e308)
   large_b = FlexFloat.from_float(1e308)
   large_result = large_a + large_b  # No overflow!

Mathematical Functions
~~~~~~~~~~~~~~~~~~~

FlexFloat 1.0.0 includes a comprehensive mathematical function library:

.. code-block:: python

   from flexfloat.math import *
   
   # Trigonometric functions
   sin(x), cos(x), tan(x)
   asin(x), acos(x), atan(x), atan2(y, x)
   
   # Exponential and logarithmic functions  
   exp(x), expm1(x), pow(x, y)
   log(x), log10(x), log2(x), log1p(x)
   
   # Hyperbolic functions
   sinh(x), cosh(x), tanh(x)
   asinh(x), acosh(x), atanh(x)
   
   # Square root functions
   sqrt(x), cbrt(x)
   
   # Mathematical constants
   pi, e, tau, inf, nan
   
   # Utility functions
   ceil(x), floor(x), fabs(x), fmod(x, y)

📚 Table of Contents
---------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   user_guide/index
   examples/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/core
   api/bitarray
   api/types

.. toctree::
   :maxdepth: 2
   :caption: Math Library

   api/math
   api/constants
   api/trigonometric
   api/exponential  
   api/logarithmic
   api/hyperbolic

📖 API Documentation
---------------------

Core Classes
~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :template: class.rst

   flexfloat.FlexFloat

BitArray Implementations
~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :template: class.rst

   flexfloat.BitArray
   flexfloat.ListBoolBitArray
   flexfloat.ListInt64BitArray
   flexfloat.BigIntBitArray

Math Functions
~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary
   :template: module.rst

   flexfloat.math

🔗 Indices and Tables
----------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

🤝 Contributing
----------------

We welcome contributions! Please see our `Contributing Guide <contributing.html>`_ for details on how to get started.

📄 License
-----------

This project is licensed under the MIT License - see the `License <license.html>`_ file for details.

💬 Support
-----------

If you encounter any issues or have questions, please:

1. Check the `documentation <https://flexfloat-py.readthedocs.io/>`_
2. Search existing `GitHub issues <https://github.com/ferranSanchezLlado/flexfloat-py/issues>`_
3. Create a new issue if needed

📊 Version Information
-----------------------

This documentation is for FlexFloat version |version|.
