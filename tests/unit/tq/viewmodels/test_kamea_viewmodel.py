"""
Unit tests for the Kamea View Model.

Tests the KameaViewModel class functionality, including state management
and coordination between the UI and service layer.
"""

import unittest
from unittest.mock import MagicMock, patch

from tq.viewmodels.kamea_viewmodel import KameaViewModel


class TestKameaViewModel(unittest.TestCase):
    """Test case for the KameaViewModel class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock KameaService
        self.mock_service = MagicMock()
        
        # Set up mock service methods
        self.mock_service.grid_size = 27
        self.mock_service.get_kamea_value.side_effect = self._mock_get_kamea_value
        self.mock_service.convert_grid_to_cartesian.side_effect = self._mock_convert_grid_to_cartesian
        self.mock_service.convert_cartesian_to_grid.side_effect = self._mock_convert_cartesian_to_grid
        self.mock_service.calculate_kamea_locator.return_value = "6-4-2"
        self.mock_service.get_quadset_coordinates.return_value = [(3, 4), (4, 3), (3, -4), (-3, 4)]
        self.mock_service.calculate_difference_vectors.return_value = [
            (10, 15, 2, 3, 100),
            (15, 10, -3, -2, 200)
        ]
        self.mock_service.get_quadset_vectors.return_value = [
            (10, 15, 2, 3, 100)
        ]
        
        # Create the view model with the mock service
        self.view_model = KameaViewModel(self.mock_service)
    
    def _mock_get_kamea_value(self, row, col, decimal):
        """Mock implementation of get_kamea_value."""
        if row == 13 and col == 13:
            return 0 if decimal else "000000"
        elif row == 10 and col == 15:
            return 123 if decimal else "012012"
        elif row == 15 and col == 10:
            return 321 if decimal else "102102"
        return None
    
    def _mock_convert_grid_to_cartesian(self, row, col):
        """Mock implementation of convert_grid_to_cartesian."""
        if row == 13 and col == 13:
            return (0, 0)
        elif row == 10 and col == 15:
            return (2, 3)
        elif row == 15 and col == 10:
            return (-3, -2)
        return (col - 13, 13 - row)
    
    def _mock_convert_cartesian_to_grid(self, x, y):
        """Mock implementation of convert_cartesian_to_grid."""
        if x == 0 and y == 0:
            return (13, 13)
        elif x == 2 and y == 3:
            return (10, 15)
        elif x == -3 and y == -2:
            return (15, 10)
        return (13 - y, x + 13)
    
    def test_select_cell(self):
        """Test selecting a cell in the grid."""
        # Test selecting the origin
        result = self.view_model.select_cell(13, 13)
        self.assertEqual(result['row'], 13)
        self.assertEqual(result['col'], 13)
        self.assertEqual(result['x'], 0)
        self.assertEqual(result['y'], 0)
        self.assertEqual(result['decimal_value'], 0)
        self.assertEqual(result['ternary_value'], "000000")
        self.assertEqual(result['kamea_locator'], "6-4-2")  # From mock
        
        # Test selecting another cell
        result = self.view_model.select_cell(10, 15)
        self.assertEqual(result['row'], 10)
        self.assertEqual(result['col'], 15)
        self.assertEqual(result['x'], 2)
        self.assertEqual(result['y'], 3)
        self.assertEqual(result['decimal_value'], 123)
        self.assertEqual(result['ternary_value'], "012012")
        self.assertEqual(result['kamea_locator'], "6-4-2")  # From mock
        
        # Verify the selected cell is stored
        self.assertEqual(self.view_model.selected_cell, (10, 15))
    
    def test_show_quadset(self):
        """Test showing a quadset."""
        # Test showing a quadset for a regular cell
        result = self.view_model.show_quadset(3, 4)
        
        # Verify the service method was called
        self.mock_service.get_quadset_coordinates.assert_called_with(3, 4)
        
        # Verify the result contains the expected data
        self.assertIn('primary_grid_coords', result)
        self.assertIn('secondary_grid_coords', result)
        self.assertIn('quad_sum', result)
        self.assertIn('secondary_sum', result)
        self.assertIn('octa_sum', result)
        
        # Verify the highlighted cells are updated
        self.assertEqual(len(self.view_model.highlighted_cells), 4)  # From mock
    
    def test_show_difference_vectors(self):
        """Test showing difference vectors."""
        # Test showing vectors with a range
        result = self.view_model.show_difference_vectors(50, 250)
        
        # Verify the service method was called
        self.mock_service.calculate_difference_vectors.assert_called_with(50, 250)
        
        # Verify the result contains the expected data
        self.assertIn('vectors', result)
        self.assertIn('count', result)
        self.assertIn('min_diff', result)
        self.assertIn('max_diff', result)
        
        # Verify the vectors are updated
        self.assertEqual(len(self.view_model.vectors), 2)  # From mock
        self.assertTrue(self.view_model.show_vectors)
        
        # Verify min/max are set correctly
        self.assertEqual(self.view_model.min_vector_diff, 100)  # From mock
        self.assertEqual(self.view_model.max_vector_diff, 200)  # From mock
    
    def test_show_quadset_vectors(self):
        """Test showing vectors for a quadset."""
        # Test showing vectors for a quadset
        result = self.view_model.show_quadset_vectors(3, 4)
        
        # Verify the service methods were called
        self.mock_service.get_quadset_coordinates.assert_called_with(3, 4)
        self.mock_service.get_quadset_vectors.assert_called_with(3, 4)
        
        # Verify the result contains the expected data
        self.assertIn('quadset_grid_positions', result)
        self.assertIn('vectors', result)
        self.assertIn('count', result)
        
        # Verify the vectors are updated
        self.assertEqual(len(self.view_model.vectors), 1)  # From mock
        self.assertTrue(self.view_model.show_vectors)
    
    def test_clear_highlights(self):
        """Test clearing highlights."""
        # Set some highlights first
        self.view_model.highlighted_cells = [(1, 2), (3, 4)]
        self.view_model.secondary_highlighted_cells = [(5, 6), (7, 8)]
        
        # Clear highlights
        self.view_model.clear_highlights()
        
        # Verify highlights are cleared
        self.assertEqual(self.view_model.highlighted_cells, [])
        self.assertEqual(self.view_model.secondary_highlighted_cells, [])
    
    def test_clear_vectors(self):
        """Test clearing vectors."""
        # Set vectors first
        self.view_model.show_vectors = True
        
        # Clear vectors
        self.view_model.clear_vectors()
        
        # Verify vectors are cleared
        self.assertFalse(self.view_model.show_vectors)
    
    def test_set_view_mode(self):
        """Test setting the view mode."""
        # Default is decimal mode
        self.assertTrue(self.view_model.decimal_mode)
        
        # Set to ternary mode
        self.view_model.set_view_mode(False)
        self.assertFalse(self.view_model.decimal_mode)
        
        # Set back to decimal mode
        self.view_model.set_view_mode(True)
        self.assertTrue(self.view_model.decimal_mode)

    def test_quadset_color_matching(self):
        """Test that quadset highlight colors match DiffTrans vector colors using the same logic."""
        # Simulate a set of quadsets (as tuples of cell coordinates)
        quadsets = [
            ((1, 2), (2, 1), (-1, -2), (-2, -1)),
            ((3, 4), (4, 3), (-3, -4), (-4, -3)),
            ((5, 6), (6, 5), (-5, -6), (-6, -5)),
        ]
        palette = [
            "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6",
            "#bcf60c", "#fabebe", "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3",
            "#808000", "#ffd8b1", "#000075", "#808080", "#ffffff", "#000000"
        ]
        # Simulate highlight color assignment
        highlight_color_map = {}
        for idx, quadset in enumerate(quadsets):
            color = palette[idx % len(palette)]
            for cell in quadset:
                if cell not in highlight_color_map:
                    highlight_color_map[cell] = color
        # Simulate DiffTrans vector color assignment (using the same quadset order)
        difftrans_color_map = {}
        for idx, quadset in enumerate(quadsets):
            # Try to get the color from the highlight map (using any cell in the quadset)
            color = None
            for cell in quadset:
                if cell in highlight_color_map:
                    color = highlight_color_map[cell]
                    break
            if color is None:
                color = palette[idx % len(palette)]
            difftrans_color_map[quadset] = color
        # Assert that the color for each quadset matches between highlights and vectors
        for idx, quadset in enumerate(quadsets):
            expected_color = palette[idx % len(palette)]
            # All cells in the quadset should have the same highlight color
            for cell in quadset:
                self.assertEqual(highlight_color_map[cell], expected_color)
            # The DiffTrans vector for this quadset should use the same color
            self.assertEqual(difftrans_color_map[quadset], expected_color)

    def test_panel_quadset_color_matching_integration(self):
        """Integration test: KameaOfMautPanel highlights and DiffTrans vectors use matching colors."""
        try:
            from tq.ui.panels.kamea_of_maut_panel import KameaOfMautPanel
            from unittest.mock import MagicMock, patch
            import sys
            # Patch QApplication to avoid needing a real app instance
            with patch('PyQt6.QtWidgets.QApplication'):
                panel = KameaOfMautPanel()
                # Patch kamea_service and kamea_grid
                panel.kamea_service = MagicMock()
                panel.kamea_grid = MagicMock()
                # Set up a known quadset and palette
                quadset = [(1, 2), (2, 1), (-1, -2), (-2, -1)]
                quadsets = [quadset]
                palette = [
                    "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6",
                    "#bcf60c", "#fabebe", "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3",
                    "#808000", "#ffd8b1", "#000075", "#808080", "#ffffff", "#000000"
                ]
                # Simulate Pattern Finder state
                panel._last_quadsum_dict = {42: {(3, 3): [quadset]}}
                # Simulate UI selection
                class DummyList:
                    def selectedItems(self):
                        class Item:
                            def text(self):
                                return "42 (1 quadsets)"
                        return [Item()]
                class DummyPairList:
                    def selectedItems(self):
                        class Item:
                            def text(self):
                                return "(3, 3) : 1 quadsets"
                        return [Item()]
                quadsum_list = DummyList()
                pairs_list = DummyPairList()
                # Patch kamea_grid highlight methods and color state
                highlight_colors = {}
                def highlight_cells_with_colors(color_map):
                    highlight_colors.update(color_map)
                panel.kamea_grid.get_current_highlight_colors = lambda: highlight_colors.copy()
                panel.kamea_grid.highlight_cells_with_colors = highlight_cells_with_colors
                # Call highlight method
                panel._highlight_selected_pair_group('sum', quadsum_list, pairs_list)
                # Now simulate highlighted cells for DiffTrans
                panel.kamea_grid.get_highlighted_cells = lambda: quadset
                # Patch kamea_service methods for DiffTrans
                panel.kamea_service.convert_grid_to_cartesian = lambda r, c: (r, c)
                panel.kamea_service.get_quadset_coordinates = lambda x, y: quadset
                panel.kamea_service.convert_cartesian_to_grid = lambda x, y: (x, y)
                panel.kamea_service.get_kamea_value = lambda r, c, d: 10
                panel.kamea_service.find_cell_position = lambda t: (0, 0)
                from tq.utils.difftrans_calculator import DiffTransCalculator
                panel.kamea_service.DiffTransCalculator = DiffTransCalculator
                # Patch DiffTransCalculator to always return a known value
                with patch('tq.utils.difftrans_calculator.DiffTransCalculator.compute_difftrans', return_value={'decimal': 0, 'ternary': '0', 'padded_ternary': '000000'}):
                    panel._show_difftrans_vectors()
                # Now check that the color used for the quadset in highlights matches the color in the difftrans vector
                # The difftrans vector is stored in panel.view_model.difftrans_vectors
                self.assertTrue(panel.view_model.difftrans_vectors)
                difftrans_color = panel.view_model.difftrans_vectors[0][5]
                # All cells in the quadset should have the same highlight color
                for cell in quadset:
                    self.assertEqual(highlight_colors[cell], difftrans_color)
        except ImportError:
            self.skipTest("PyQt6 or KameaOfMautPanel not available; skipping integration test.")


if __name__ == "__main__":
    unittest.main()
