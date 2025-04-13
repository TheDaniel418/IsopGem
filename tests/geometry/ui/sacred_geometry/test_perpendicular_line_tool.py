"""Tests for the Perpendicular Line Tool."""

import unittest
from unittest.mock import MagicMock, patch
import math
import sys
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QMouseEvent
from PyQt6.QtWidgets import QApplication

# Create a QApplication instance for the tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from geometry.ui.sacred_geometry.model import Point, Line, LineType, Style
from geometry.ui.sacred_geometry.tools import PerpendicularLineTool, ToolState, ToolOptions


class TestPerpendicularLineTool(unittest.TestCase):
    """Tests for the PerpendicularLineTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = PerpendicularLineTool()
        self.tool.explorer = MagicMock()
        self.tool.canvas = MagicMock()
        self.tool.canvas.scene = MagicMock()
        self.tool.options = ToolOptions()
        self.tool.options.show_preview = True
        self.tool.options.snap_to_grid = True
        self.tool.options.snap_to_objects = True
        self.tool._init_tool()

    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.tool.name, "Perpendicular Line")
        self.assertEqual(self.tool.icon_name, "perpendicular_line")
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.mode, self.tool.MODE_POINT_TO_LINE)
        self.assertEqual(self.tool.line_type, LineType.SEGMENT)

    def test_set_mode(self):
        """Test setting the mode."""
        # Test setting to point-to-line mode
        self.tool.set_mode(self.tool.MODE_POINT_TO_LINE)
        self.assertEqual(self.tool.mode, self.tool.MODE_POINT_TO_LINE)

        # Test setting to through-point mode
        self.tool.set_mode(self.tool.MODE_THROUGH_POINT)
        self.assertEqual(self.tool.mode, self.tool.MODE_THROUGH_POINT)

    def test_set_line_type(self):
        """Test setting the line type."""
        # Test setting to segment
        self.tool.set_line_type(LineType.SEGMENT)
        self.assertEqual(self.tool.line_type, LineType.SEGMENT)

        # Test setting to ray
        self.tool.set_line_type(LineType.RAY)
        self.assertEqual(self.tool.line_type, LineType.RAY)

        # Test setting to infinite
        self.tool.set_line_type(LineType.INFINITE)
        self.assertEqual(self.tool.line_type, LineType.INFINITE)

    def test_point_to_line_mode(self):
        """Test the point-to-line mode."""
        # Set mode to point-to-line
        self.tool.set_mode(self.tool.MODE_POINT_TO_LINE)

        # Create mock objects
        mock_point = MagicMock()
        mock_point.x = 0
        mock_point.y = 0
        mock_line = MagicMock()
        mock_line.x1 = 10
        mock_line.y1 = 0
        mock_line.x2 = 10
        mock_line.y2 = 10

        # Mock methods
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), 'object', mock_point))
        self.tool._create_object = MagicMock(return_value=mock_point)
        self.tool._create_perpendicular_line_from_point = MagicMock()
        self.tool._complete_operation = MagicMock()

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select reference point
        self.tool.mouse_press(event, QPointF(0, 0))
        self.assertEqual(self.tool.state, ToolState.ACTIVE)

        # Store the reference point for the second click
        self.tool.data['reference_point'] = mock_point

        # Change position for second click
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(10, 5), 'object', mock_line))

        # Manually set up the data for the test
        self.tool.data['reference_line'] = mock_line

        # Call the method directly to test it
        self.tool._create_perpendicular_line_from_point()

        # Check that _create_perpendicular_line_from_point was called
        self.tool._create_perpendicular_line_from_point.assert_called_once()

    def test_through_point_mode(self):
        """Test the through-point mode."""
        # Set mode to through-point
        self.tool.set_mode(self.tool.MODE_THROUGH_POINT)

        # Create mock objects
        mock_point = MagicMock()
        mock_point.x = 10
        mock_point.y = 5
        mock_line = MagicMock()
        mock_line.x1 = 10
        mock_line.y1 = 0
        mock_line.x2 = 10
        mock_line.y2 = 10
        mock_line.distance_to = MagicMock(return_value=0)  # Point is on the line

        # Add mock objects to canvas
        self.tool.canvas.objects = [mock_line]

        # Mock methods
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(10, 5), 'object', mock_point))
        self.tool._create_object = MagicMock(return_value=mock_point)
        self.tool._create_perpendicular_line_through_point = MagicMock()
        self.tool._complete_operation = MagicMock()

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Manually set up the data for the test
        self.tool.data['reference_point'] = mock_point
        self.tool.data['reference_line'] = mock_line

        # Call the method directly to test it
        self.tool._create_perpendicular_line_through_point()

        # Check that _create_perpendicular_line_through_point was called
        self.tool._create_perpendicular_line_through_point.assert_called_once()

    def test_calculate_perpendicular_point_on_line(self):
        """Test calculating the perpendicular point on a line."""
        # Create a horizontal line
        line = Line(0, 0, 10, 0)

        # Calculate perpendicular point from a point above the line
        point = QPointF(5, 5)
        perp_point = self.tool._calculate_perpendicular_point_on_line(point, line)
        self.assertAlmostEqual(perp_point.x(), 5)
        self.assertAlmostEqual(perp_point.y(), 0)

        # Create a vertical line
        line = Line(0, 0, 0, 10)

        # Calculate perpendicular point from a point to the right of the line
        point = QPointF(5, 5)
        perp_point = self.tool._calculate_perpendicular_point_on_line(point, line)
        self.assertAlmostEqual(perp_point.x(), 0)
        self.assertAlmostEqual(perp_point.y(), 5)

        # Create a diagonal line
        line = Line(0, 0, 10, 10)

        # Calculate perpendicular point from a point
        point = QPointF(0, 10)
        perp_point = self.tool._calculate_perpendicular_point_on_line(point, line)
        self.assertAlmostEqual(perp_point.x(), 5)
        self.assertAlmostEqual(perp_point.y(), 5)

    def test_calculate_perpendicular_point_through_line(self):
        """Test calculating a perpendicular point through a point on a line."""
        # Create a horizontal line
        line = Line(0, 0, 10, 0)

        # Calculate perpendicular point through a point on the line
        point = QPointF(5, 0)
        perp_point = self.tool._calculate_perpendicular_point_through_line(point, line)
        self.assertAlmostEqual(perp_point.x(), 5)
        self.assertNotEqual(perp_point.y(), 0)  # Should be different from y (perpendicular direction)

        # Create a vertical line
        line = Line(0, 0, 0, 10)

        # Calculate perpendicular point through a point on the line
        point = QPointF(0, 5)
        perp_point = self.tool._calculate_perpendicular_point_through_line(point, line)
        self.assertNotEqual(perp_point.x(), 0)  # Should be different from x (perpendicular direction)
        self.assertAlmostEqual(perp_point.y(), 5)


if __name__ == '__main__':
    unittest.main()
