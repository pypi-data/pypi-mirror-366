"""
-------------------------------------------------------------------------------

Unit tests for the toolkit module

-------------------------------------------------------------------------------
"""

import unittest
import io
import sys
from elliptical_distribution_toolkit import print_toolkit_name


class TestToolkit(unittest.TestCase):
    """Test cases for the toolkit module."""

    def test_print_toolkit_name(self):
        """Test that print_toolkit_name prints the correct message."""
        # Redirect stdout to capture the printed output
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Call the function
        print_toolkit_name()

        # Reset stdout
        sys.stdout = sys.__stdout__

        # Check the captured output
        self.assertEqual(
            captured_output.getvalue().strip(),
            "I am the elliptical-distribution-toolkit"
        )


