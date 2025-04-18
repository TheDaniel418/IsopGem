"""
Unit tests for the Kamea Service.

Tests the KameaService class functionality, including coordinate conversions,
quadset calculations, and conrune transformations.
"""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import numpy as np

from tq.services.kamea_service import KameaService


class TestKameaService(unittest.TestCase):
    """Test case for the KameaService class."""

    def setUp(self):
        """Set up test fixtures."""
        # Use the real KameaService with actual CSV data
        self.service = KameaService()

    def test_get_kamea_value(self):
        """Test getting values from the Kamea grid using real data."""
        # Test a few random positions for both decimal and ternary
        for (row, col) in [(13, 13), (10, 15), (15, 10), (0, 0), (26, 26)]:
            expected_decimal = self.service.decimal_data[row][col]
            expected_ternary = self.service.ternary_data[row][col]
            self.assertEqual(self.service.get_kamea_value(row, col, True), expected_decimal)
            self.assertEqual(self.service.get_kamea_value(row, col, False), expected_ternary)

    def test_convert_grid_to_cartesian(self):
        """Test converting grid coordinates to Cartesian coordinates."""
        # Origin
        self.assertEqual(self.service.convert_grid_to_cartesian(13, 13), (0, 0))

        # Positive x, positive y
        self.assertEqual(self.service.convert_grid_to_cartesian(10, 15), (2, 3))

        # Positive x, negative y
        self.assertEqual(self.service.convert_grid_to_cartesian(15, 15), (2, -2))

        # Negative x, positive y
        self.assertEqual(self.service.convert_grid_to_cartesian(10, 10), (-3, 3))

        # Negative x, negative y
        self.assertEqual(self.service.convert_grid_to_cartesian(15, 10), (-3, -2))

    def test_convert_cartesian_to_grid(self):
        """Test converting Cartesian coordinates to grid coordinates."""
        # Origin
        self.assertEqual(self.service.convert_cartesian_to_grid(0, 0), (13, 13))

        # Positive x, positive y
        self.assertEqual(self.service.convert_cartesian_to_grid(2, 3), (10, 15))

        # Positive x, negative y
        self.assertEqual(self.service.convert_cartesian_to_grid(2, -2), (15, 15))

        # Negative x, positive y
        self.assertEqual(self.service.convert_cartesian_to_grid(-3, 3), (10, 10))

        # Negative x, negative y
        self.assertEqual(self.service.convert_cartesian_to_grid(-3, -2), (15, 10))

    def test_get_quadset_coordinates(self):
        """Test getting quadset coordinates according to the canonical documentation.
        See: docs/kamea_mathematical_principles.md, section 'Quadsets'.
        """
        # Origin - should only return itself
        self.assertEqual(self.service.get_quadset_coordinates(0, 0), [(0, 0)])

        # Axis cells - should return the cell and its sign-inverted pair
        self.assertEqual(
            set(self.service.get_quadset_coordinates(5, 0)),
            set([(5, 0), (-5, 0)])
        )
        self.assertEqual(
            set(self.service.get_quadset_coordinates(0, 7)),
            set([(0, 7), (0, -7)])
        )
        self.assertEqual(
            set(self.service.get_quadset_coordinates(-8, 0)),
            set([(-8, 0), (8, 0)])
        )
        self.assertEqual(
            set(self.service.get_quadset_coordinates(0, -9)),
            set([(0, -9), (0, 9)])
        )

        # Regular cell - should return all four sign permutations
        self.assertEqual(
            set(self.service.get_quadset_coordinates(2, 10)),
            set([(2, 10), (-2, -10), (-2, 10), (2, -10)])
        )
        self.assertEqual(
            set(self.service.get_quadset_coordinates(3, 3)),
            set([(3, 3), (-3, -3), (-3, 3), (3, -3)])
        )
        self.assertEqual(
            set(self.service.get_quadset_coordinates(-4, 5)),
            set([(-4, 5), (4, -5), (4, 5), (-4, -5)])
        )
        self.assertEqual(
            set(self.service.get_quadset_coordinates(-6, -7)),
            set([(-6, -7), (6, 7), (6, -7), (-6, 7)])
        )

        # Test that swapping x and y produces a different quadset
        quadset_1 = set(self.service.get_quadset_coordinates(2, 10))
        quadset_2 = set(self.service.get_quadset_coordinates(10, 2))
        self.assertNotEqual(quadset_1, quadset_2)
        # But their quadsums (if implemented) should be equal (not tested here)

    def test_get_conrune_pair(self):
        """Test getting the conrune pair for a ternary value."""
        # Test with various ternary values
        self.assertEqual(self.service.get_conrune_pair("000000"), "000000")  # All zeros stay the same
        self.assertEqual(self.service.get_conrune_pair("111111"), "222222")  # All 1s become 2s
        self.assertEqual(self.service.get_conrune_pair("222222"), "111111")  # All 2s become 1s
        self.assertEqual(self.service.get_conrune_pair("012012"), "021021")  # Mixed digits
        self.assertEqual(self.service.get_conrune_pair("102102"), "201201")  # Mixed digits

    def test_extract_bigrams(self):
        """Test extracting bigrams from a ternary value."""
        # Test with a 6-digit ternary value
        self.assertEqual(
            self.service.extract_bigrams("012012"),
            ("02", "11", "20")  # (digits 6&1, 5&2, 4&3)
        )

        # Test with a shorter value that gets padded
        self.assertEqual(
            self.service.extract_bigrams("12"),
            ("02", "01", "00")  # Padded to "000012" then extracted
        )

    def test_calculate_kamea_locator(self):
        """Test calculating the Kamea Locator for a ternary value."""
        # Test with a 6-digit ternary value
        # Bigrams: ("02", "11", "20") -> decimal: (2, 4, 6)
        self.assertEqual(
            self.service.calculate_kamea_locator("012012"),
            "6-4-2"  # Format: region-area-cell
        )

        # Test with a shorter value that gets padded
        # Bigrams: ("02", "01", "00") -> decimal: (2, 1, 0)
        self.assertEqual(
            self.service.calculate_kamea_locator("12"),
            "0-1-2"  # Format: region-area-cell
        )

    def test_conrune_geometric_vs_ternary_equivalence(self):
        """Test that geometric reflection and ternary conrune transformation always agree for all cells in the Kamea grid using real data."""
        grid_size = self.service.grid_size
        center_row = grid_size // 2
        center_col = grid_size // 2
        mismatches = []
        for row in range(grid_size):
            for col in range(grid_size):
                ternary_value = self.service.get_kamea_value(row, col, False)
                if ternary_value is None:
                    continue
                ternary_value = str(ternary_value).zfill(6)
                # Geometric reflection
                reflected_row = 2 * center_row - row
                reflected_col = 2 * center_col - col
                # Bounds check
                if not (0 <= reflected_row < grid_size and 0 <= reflected_col < grid_size):
                    continue
                # Ternary conrune transformation
                conrune_ternary = self.service.get_conrune_pair(ternary_value)
                if conrune_ternary is None:
                    continue
                # The expected conrune position is the geometric reflection
                expected_conrune_ternary = str(self.service.get_kamea_value(reflected_row, reflected_col, False)).zfill(6)
                if conrune_ternary != expected_conrune_ternary:
                    mismatches.append({
                        'row': row,
                        'col': col,
                        'ternary': ternary_value,
                        'geometric': (reflected_row, reflected_col),
                        'conrune_ternary': conrune_ternary,
                        'expected_conrune_ternary': expected_conrune_ternary
                    })
        if mismatches:
            with open('conrune_mismatches.txt', 'w') as f:
                for m in mismatches[:10]:
                    f.write(f"row={m['row']}, col={m['col']}, ternary={m['ternary']}, "
                            f"geometric={m['geometric']}, conrune_ternary={m['conrune_ternary']}, "
                            f"expected_conrune_ternary={m['expected_conrune_ternary']}\n")
        self.assertEqual(len(mismatches), 0, f"Found mismatches between geometric and ternary conrune: see conrune_mismatches.txt")


if __name__ == "__main__":
    unittest.main()
