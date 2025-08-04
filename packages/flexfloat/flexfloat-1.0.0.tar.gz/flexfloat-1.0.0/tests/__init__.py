"""Base test utilities for the flexfloat package."""

import unittest


class FlexFloatTestCase(unittest.TestCase):
    """Base test case class with common utilities for FlexFloat tests."""

    def assertAlmostEqualRel(
        self, first: float, second: float, tolerance: float = 1e-7
    ):
        """Assert that two floats are approximately equal within a relative tolerance.

        Args:
            first (float): The first float to compare.
            second (float): The second float to compare.
            tolerance (float): The relative tolerance for comparison.
        Raises:
            AssertionError: If the floats are not approximately equal within the
                specified tolerance.
        """
        rel_difference = abs(first - second) / max(abs(first), abs(second), 1e-10)
        if rel_difference > tolerance:
            raise self.failureException(
                f"{first} != {second} within tolerance {tolerance} "
                f"(relative difference: {rel_difference})"
            )
