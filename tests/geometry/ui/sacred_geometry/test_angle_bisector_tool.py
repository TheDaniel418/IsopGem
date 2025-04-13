"""Tests for the Angle Bisector Tool."""

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
from geometry.ui.sacred_geometry.tools import AngleBisectorTool, ToolState, ToolOptions


class TestAngleBisectorTool(unittest.TestCase):
    """Tests for the AngleBisectorTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = AngleBisectorTool()
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
        self.assertEqual(self.tool.name, "Angle Bisector")
        self.assertEqual(self.tool.icon_name, "angle_bisector")
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.mode, self.tool.MODE_THREE_POINTS)
        self.assertEqual(self.tool.line_type, LineType.RAY)

    def test_set_mode(self):
        """Test setting the mode."""
        # Test setting to three-points mode
        self.tool.set_mode(self.tool.MODE_THREE_POINTS)
        self.assertEqual(self.tool.mode, self.tool.MODE_THREE_POINTS)

        # Test setting to two-lines mode
        self.tool.set_mode(self.tool.MODE_TWO_LINES)
        self.assertEqual(self.tool.mode, self.tool.MODE_TWO_LINES)

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

    def test_calculate_angle_bisector_from_points(self):
        """Test calculating the angle bisector from three points."""
        # Create three points forming a right angle
        p1 = Point(0, 0)
        p2 = Point(10, 0)  # Vertex
        p3 = Point(10, 10)

        # Calculate bisector
        start_point, end_point = self.tool._calculate_angle_bisector_from_points(p1, p2, p3)

        # Check that the start point is at the vertex
        self.assertAlmostEqual(start_point.x(), 10.0)
        self.assertAlmostEqual(start_point.y(), 0.0)

        # Check that the bisector is at 45 degrees (for a right angle)
        # The vector from start to end should be (1, 1) normalized
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        length = math.sqrt(dx * dx + dy * dy)

        # Normalize the vector
        dx /= length
        dy /= length

        # Check that it's approximately (±1/sqrt(2), ±1/sqrt(2))
        # The direction could be flipped depending on implementation details
        self.assertAlmostEqual(abs(dx), 1/math.sqrt(2), delta=0.001)
        self.assertAlmostEqual(abs(dy), 1/math.sqrt(2), delta=0.001)

    def test_calculate_angle_bisector_from_lines(self):
        """Test calculating the angle bisector from two lines."""
        # Create two lines forming a right angle
        line1 = Line(0, 0, 10, 0)  # Horizontal line
        line2 = Line(10, 0, 10, 10)  # Vertical line

        # Calculate bisector
        start_point, end_point = self.tool._calculate_angle_bisector_from_lines(line1, line2)

        # Check that the start point is at the intersection
        self.assertAlmostEqual(start_point.x(), 10.0)
        self.assertAlmostEqual(start_point.y(), 0.0)

        # Check that the bisector is at 45 degrees (for a right angle)
        # The vector from start to end should be (1, 1) normalized
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        length = math.sqrt(dx * dx + dy * dy)

        # Normalize the vector
        dx /= length
        dy /= length

        # Check that it's approximately (±1/sqrt(2), ±1/sqrt(2))
        # The direction could be flipped depending on implementation details
        self.assertAlmostEqual(abs(dx), 1/math.sqrt(2), delta=0.001)
        self.assertAlmostEqual(abs(dy), 1/math.sqrt(2), delta=0.001)

    def test_three_points_mode(self):
        """Test the three-points mode."""
        # Set mode to three-points
        self.tool.set_mode(self.tool.MODE_THREE_POINTS)

        # Create mock objects
        mock_point1 = MagicMock(spec=Point)
        mock_point1.x = 0
        mock_point1.y = 0

        mock_point2 = MagicMock(spec=Point)
        mock_point2.x = 10
        mock_point2.y = 0

        mock_point3 = MagicMock(spec=Point)
        mock_point3.x = 10
        mock_point3.y = 10

        # Mock the _snap_position_with_info method to return fixed positions and objects
        self.tool._snap_position_with_info = MagicMock(side_effect=[
            (QPointF(0, 0), 'object', mock_point1),
            (QPointF(10, 0), 'object', mock_point2),
            (QPointF(10, 10), 'object', mock_point3)
        ])

        # Mock the _create_angle_bisector_from_points method
        self.tool._create_angle_bisector_from_points = MagicMock()

        # Mock the _complete_operation method
        self.tool._complete_operation = MagicMock()

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select first point
        self.tool.mouse_press(event, QPointF(0, 0))
        self.assertEqual(len(self.tool.data['points']), 1)

        # Second click - select second point (vertex)
        self.tool.mouse_press(event, QPointF(10, 0))
        self.assertEqual(len(self.tool.data['points']), 2)

        # Third click - select third point and create bisector
        self.tool.mouse_press(event, QPointF(10, 10))
        self.assertEqual(len(self.tool.data['points']), 3)

        # Check that _create_angle_bisector_from_points was called
        self.tool._create_angle_bisector_from_points.assert_called_once()

        # Check that _complete_operation was called
        self.tool._complete_operation.assert_called_once()

    def test_two_lines_mode(self):
        """Test the two-lines mode."""
        # Set mode to two-lines
        self.tool.set_mode(self.tool.MODE_TWO_LINES)

        # Create mock objects
        mock_line1 = MagicMock(spec=Line)
        mock_line1.x1 = 0
        mock_line1.y1 = 0
        mock_line1.x2 = 10
        mock_line1.y2 = 0

        mock_line2 = MagicMock(spec=Line)
        mock_line2.x1 = 10
        mock_line2.y1 = 0
        mock_line2.x2 = 10
        mock_line2.y2 = 10

        # Mock the _snap_position_with_info method to return fixed positions and objects
        self.tool._snap_position_with_info = MagicMock(side_effect=[
            (QPointF(5, 0), 'object', mock_line1),
            (QPointF(10, 5), 'object', mock_line2)
        ])

        # Mock the _create_angle_bisector_from_lines method
        self.tool._create_angle_bisector_from_lines = MagicMock()

        # Mock the _complete_operation method
        self.tool._complete_operation = MagicMock()

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select first line
        self.tool.mouse_press(event, QPointF(5, 0))
        self.assertEqual(len(self.tool.data['lines']), 1)

        # Second click - select second line and create bisector
        self.tool.mouse_press(event, QPointF(10, 5))
        self.assertEqual(len(self.tool.data['lines']), 2)

        # Check that _create_angle_bisector_from_lines was called
        self.tool._create_angle_bisector_from_lines.assert_called_once()

        # Check that _complete_operation was called
        self.tool._complete_operation.assert_called_once()


if __name__ == '__main__':
    unittest.main()
