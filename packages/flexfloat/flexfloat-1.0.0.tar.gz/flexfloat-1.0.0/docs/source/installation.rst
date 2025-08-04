Installation
============

Requirements
------------

FlexFloat requires Python 3.11 or higher.

Installing from PyPI
--------------------

The easiest way to install FlexFloat is using pip:

.. code-block:: bash

   pip install flexfloat

This will install FlexFloat with all core features including the complete mathematical function library.

Verifying Installation
---------------------

You can verify that FlexFloat is installed correctly:

.. code-block:: python

   import flexfloat
   from flexfloat.math import pi, sin
   
   print(f"FlexFloat version: {flexfloat.__version__}")
   
   # Test basic functionality
   x = flexfloat.FlexFloat.from_float(2.0)
   result = sin(pi / flexfloat.FlexFloat.from_float(4.0))
   
   print(f"sin(pi/4) ≈ {result.to_float()}")  # Should be = 0.707

This should output the version number and demonstrate that both core arithmetic and mathematical functions are working.
Installing from Source
----------------------

To install from source, first clone the repository:

.. code-block:: bash

   git clone https://github.com/ferranSanchezLlado/flexfloat-py.git
   cd flexfloat-py

Then install the package:

.. code-block:: bash

   pip install .

Development Installation
------------------------

For development, you can install the package in editable mode with development dependencies:

.. code-block:: bash

   git clone https://github.com/ferranSanchezLlado/flexfloat-py.git
   cd flexfloat-py
   pip install -e ".[dev]"

This will install the package in editable mode along with all development dependencies including:

- pytest (testing framework)
- black (code formatting)
- mypy (type checking)
- pylint (linting)
- sphinx (documentation)

Verifying Installation
----------------------

To verify that FlexFloat is installed correctly, you can run:

.. code-block:: python

   import flexfloat
   print(flexfloat.__author__)  # Ferran Sanchez Llado

Or test basic functionality:

.. code-block:: python

   from flexfloat import FlexFloat
   
   x = FlexFloat(1.5)
   y = FlexFloat(2.5)
   result = x + y
   print(result)  # 4.00000e+00

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Error**
   If you get an import error, make sure you have Python 3.11 or higher:
   
   .. code-block:: bash
   
      python --version

**Permission Error**
   If you get permission errors during installation, try using a virtual environment:
   
   .. code-block:: bash
   
      python -m venv flexfloat-env
      source flexfloat-env/bin/activate  # On Windows: flexfloat-env\Scripts\activate
      pip install flexfloat

Virtual Environment
~~~~~~~~~~~~~~~~~~~

We recommend using a virtual environment to avoid conflicts with other packages:

.. code-block:: bash

   # Create virtual environment
   python -m venv flexfloat-env
   
   # Activate virtual environment
   # On Windows:
   flexfloat-env\Scripts\activate
   # On macOS/Linux:
   source flexfloat-env/bin/activate
   
   # Install FlexFloat
   pip install flexfloat
