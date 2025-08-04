BitArray Module
===============

The BitArray module provides different implementations for efficient bit manipulation in FlexFloat.

Base BitArray Protocol
----------------------

.. autoclass:: flexfloat.BitArray
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Implementations
---------------

ListBoolBitArray
^^^^^^^^^^^^^^^^

.. autoclass:: flexfloat.ListBoolBitArray
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

ListInt64BitArray
^^^^^^^^^^^^^^^^^

.. autoclass:: flexfloat.ListInt64BitArray
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

BigIntBitArray
^^^^^^^^^^^^^^

.. autoclass:: flexfloat.BigIntBitArray
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Usage Examples
--------------

Choosing a BitArray Implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from flexfloat import FlexFloat, ListBoolBitArray, ListInt64BitArray, BigIntBitArray

   # Use different implementations
   FlexFloat.set_bitarray_implementation(ListBoolBitArray)
   FlexFloat.set_bitarray_implementation(ListInt64BitArray)
   FlexFloat.set_bitarray_implementation(BigIntBitArray)
   
Performance Characteristics
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: BitArray Performance Comparison
   :header-rows: 1
   :widths: 25 25 25 25

   * - Implementation
     - Memory Usage
     - Speed
     - Best Use Case
   * - ListBoolBitArray
     - High
     - Slow
     - Debugging, small numbers
   * - ListInt64BitArray
     - Medium
     - Fast
     - General purpose
   * - BigIntBitArray
     - Low
     - Very Fast
     - Large numbers, production

Direct BitArray Usage
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from flexfloat import ListInt64BitArray

   # Create a BitArray
   bits = ListInt64BitArray([0], length=8)  # 8-bit array

   # Set individual bits
   bits[0] = True
   bits[7] = True

   # Get bits
   print(bits[0])  # True
   print(bits[1])  # False

   # Convert to integer
   value = bits.to_int()
   print(value)    # 129

   # Create from integer
   bits2 = ListInt64BitArray.from_signed_int(128, 8)
   print(bits2.to_int())  # 255

BitArray Operations
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from flexfloat import ListInt64BitArray

   # Create BitArrays
   a = ListInt64BitArray.from_signed_int(12, 4)  # 1100
   b = ListInt64BitArray.from_signed_int(10, 4)  # 1010

   # Bitwise operations (if implemented)
   and_result = a & b    # 1000 = 8
   or_result = a | b     # 1110 = 14
   xor_result = a ^ b    # 0110 = 6
   not_result = ~a       # 0011 = 3

Extending BitArrays
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from flexfloat import ListInt64BitArray

   # Start with small BitArray
   bits = ListInt64BitArray.from_signed_int(5, 4)  # 0101
   print(len(bits))  # 4

   # Extend it (if implemented)
   extended = bits.extend(8)
   print(len(extended))  # 8
   print(extended.to_int())  # Still 5, but with more bits

Custom BitArray Implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can create your own BitArray implementation by following the protocol:

.. code-block:: python

   from flexfloat.bitarray import BitArray
   from typing import Iterator

   class CustomBitArray(BitArray):
       def __init__(self, length: int):
           self._data = [False] * length
       def __len__(self) -> int:
           return len(self._data)
       def __getitem__(self, index: int) -> bool:
           return self._data[index]
       def __setitem__(self, index: int, value: bool) -> None:
           self._data[index] = value
       def __iter__(self) -> Iterator[bool]:
           return iter(self._data)
       def to_int(self) -> int:
           result = 0
           for i, bit in enumerate(self._data):
               if bit:
                   result |= (1 << i)
           return result
       @classmethod
       def from_signed_int(cls, value: int, length: int) -> 'CustomBitArray':
           bits = cls(length)
           for i in range(length):
               bits[i] = bool(value & (1 << i))
           return bits
