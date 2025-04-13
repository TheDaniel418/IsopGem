"""Tests for the IntersectionTool class."""

import unittest
from unittest.mock import MagicMock, patch
import sys
import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QMouseEvent
from PyQt6.QtWidgets import QApplication

# Create QApplication instance for the tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from geometry.ui.sacred_geometry.model import Point, Line, Circle, Style, LineType
from geometry.ui.sacred_geometry.tools import IntersectionTool, ToolState, ToolOptions


class TestIntersectionTool(unittest.TestCase):
    """Tests for the IntersectionTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = IntersectionTool()
        self.tool.explorer = MagicMock()
        self.tool.canvas = MagicMock()
        self.tool.canvas.scene = MagicMock()
        self.tool.options = ToolOptions()
        self.tool.options.show_preview = True
        self.tool.options.snap_to_grid = True
        self.tool.options.snap_to_objects = True
        self.tool._init_tool()

    def test_intersection_tool_initialization(self):
        """Test that the IntersectionTool initializes correctly."""
        self.assertEqual(self.tool.name, "Intersection")
        self.assertEqual(self.tool.icon_name, "intersection")
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertIsNone(self.tool.first_object)
        self.assertIsNone(self.tool.second_object)
        self.assertEqual(self.tool.point_size, 5.0)
        self.assertEqual(self.tool.stroke_color, QColor(0, 0, 0))
        self.assertEqual(self.tool.fill_color, QColor(255, 255, 255))

    def test_point_style_setting(self):
        """Test that the point style can be set."""
        # Test point size
        self.tool.set_point_size(8.0)
        self.assertEqual(self.tool.point_size, 8.0)

        # Test stroke color
        test_color = QColor(255, 0, 0)
        self.tool.set_stroke_color(test_color)
        self.assertEqual(self.tool.stroke_color, test_color)

        # Test fill color
        fill_color = QColor(0, 255, 0)
        self.tool.set_fill_color(fill_color)
        self.assertEqual(self.tool.fill_color, fill_color)

    def test_create_point_style(self):
        """Test that the point style is created correctly."""
        # Set custom style
        self.tool.set_point_size(8.0)
        stroke_color = QColor(255, 0, 0)
        fill_color = QColor(0, 255, 0)
        self.tool.set_stroke_color(stroke_color)
        self.tool.set_fill_color(fill_color)

        # Create style
        style = self.tool._create_point_style()

        # Check style properties
        self.assertEqual(style.point_size, 8.0)
        self.assertEqual(style.stroke_color, stroke_color)
        self.assertEqual(style.fill_color, fill_color)

    @patch('geometry.ui.sacred_geometry.tools.IntersectionTool._create_intersection_points')
    def test_line_line_intersection(self, mock_create_intersection_points):
        """Test finding intersection between two lines."""
        # Create mock lines
        line1 = MagicMock()
        line1.__class__.__name__ = 'Line'

        line2 = MagicMock()
        line2.__class__.__name__ = 'Line'

        # Mock the intersect method to return a fixed intersection point
        intersection_point = QPointF(100, 100)
        line1.intersect.return_value = [intersection_point]

        # Mock the canvas.find_object_at method to return the lines
        self.tool.canvas.find_object_at = MagicMock(side_effect=[line1, line2])

        # Create mock mouse events
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select first line
        self.tool.mouse_press(event, QPointF(0, 0))

        # Check that first object is set
        self.assertEqual(self.tool.first_object, line1)

        # Second click - select second line and create intersection
        self.tool.mouse_press(event, QPointF(0, 0))

        # In the actual implementation, second_object might be reset to None after creating intersections
        # Just check that the intersection was created
        mock_create_intersection_points.assert_called_once()

        # Check that _create_intersection_points was called with correct parameters
        args, kwargs = mock_create_intersection_points.call_args
        self.assertEqual(args[0], [intersection_point])

        # Check that tool state is reset
        self.assertIsNone(self.tool.first_object)
        self.assertIsNone(self.tool.second_object)

    @patch('geometry.ui.sacred_geometry.tools.IntersectionTool._create_intersection_points')
    def test_line_circle_intersection(self, mock_create_intersection_points):
        """Test finding intersection between a line and a circle."""
        # Create mock line and circle
        line = MagicMock()
        line.__class__.__name__ = 'Line'

        circle = MagicMock()
        circle.__class__.__name__ = 'Circle'

        # Mock the intersect method to return fixed intersection points
        intersection_points = [QPointF(100, 100), QPointF(200, 200)]
        line.intersect.return_value = intersection_points

        # Mock the canvas.find_object_at method to return the objects
        self.tool.canvas.find_object_at = MagicMock(side_effect=[line, circle])

        # Create mock mouse events
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select line
        self.tool.mouse_press(event, QPointF(0, 0))

        # Check that first object is set
        self.assertEqual(self.tool.first_object, line)

        # Second click - select circle and create intersections
        self.tool.mouse_press(event, QPointF(0, 0))

        # In the actual implementation, second_object might be reset to None after creating intersections
        # Just check that the intersection was created
        mock_create_intersection_points.assert_called_once()

        # Check that _create_intersection_points was called with correct parameters
        mock_create_intersection_points.assert_called_once()
        args, kwargs = mock_create_intersection_points.call_args
        self.assertEqual(args[0], intersection_points)

        # Check that tool state is reset
        self.assertIsNone(self.tool.first_object)
        self.assertIsNone(self.tool.second_object)

    @patch('geometry.ui.sacred_geometry.tools.IntersectionTool._create_intersection_points')
    def test_circle_circle_intersection(self, mock_create_intersection_points):
        """Test finding intersection between two circles."""
        # Create mock circles
        circle1 = MagicMock()
        circle1.__class__.__name__ = 'Circle'

        circle2 = MagicMock()
        circle2.__class__.__name__ = 'Circle'

        # Mock the intersect method to return fixed intersection points
        intersection_points = [QPointF(100, 100), QPointF(200, 200)]
        circle1.intersect.return_value = intersection_points

        # Mock the canvas.find_object_at method to return the circles
        self.tool.canvas.find_object_at = MagicMock(side_effect=[circle1, circle2])

        # Create mock mouse events
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select first circle
        self.tool.mouse_press(event, QPointF(0, 0))

        # Check that first object is set
        self.assertEqual(self.tool.first_object, circle1)

        # Second click - select second circle and create intersections
        self.tool.mouse_press(event, QPointF(0, 0))

        # In the actual implementation, second_object might be reset to None after creating intersections
        # Just check that the intersection was created
        mock_create_intersection_points.assert_called_once()

        # Check that _create_intersection_points was called with correct parameters
        mock_create_intersection_points.assert_called_once()
        args, kwargs = mock_create_intersection_points.call_args
        self.assertEqual(args[0], intersection_points)

        # Check that tool state is reset
        self.assertIsNone(self.tool.first_object)
        self.assertIsNone(self.tool.second_object)

    @patch('geometry.ui.sacred_geometry.tools.IntersectionTool._create_object')
    def test_create_intersection_points(self, mock_create_object):
        """Test creating intersection points."""
        # Create intersection points
        intersection_points = [QPointF(100, 100), QPointF(200, 200)]

        # Call the method
        self.tool._create_intersection_points(intersection_points)

        # Check that _create_object was called for each intersection point
        self.assertEqual(mock_create_object.call_count, 2)

        # Check first call
        args1, kwargs1 = mock_create_object.call_args_list[0]
        self.assertEqual(args1[0], 'point')
        self.assertEqual(kwargs1['x'], 100)
        self.assertEqual(kwargs1['y'], 100)

        # Check second call
        args2, kwargs2 = mock_create_object.call_args_list[1]
        self.assertEqual(args2[0], 'point')
        self.assertEqual(kwargs2['x'], 200)
        self.assertEqual(kwargs2['y'], 200)

    def test_no_intersection(self):
        """Test handling when there is no intersection."""
        # Create mock objects
        line1 = MagicMock()
        line1.__class__.__name__ = 'Line'

        line2 = MagicMock()
        line2.__class__.__name__ = 'Line'

        # Mock the intersect method to return no intersection points
        line1.intersect.return_value = []

        # Mock the canvas.find_object_at method to return the lines
        self.tool.canvas.find_object_at = MagicMock(side_effect=[line1, line2])

        # Mock the explorer.status_bar.showMessage method
        self.tool.explorer.status_bar = MagicMock()

        # Create mock mouse events
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select first line
        self.tool.mouse_press(event, QPointF(0, 0))

        # Reset the mock to clear previous calls
        self.tool.explorer.status_bar.showMessage.reset_mock()

        # Second click - select second line but no intersection
        self.tool.mouse_press(event, QPointF(0, 0))

        # Check that status bar message was shown with the correct message
        self.tool.explorer.status_bar.showMessage.assert_any_call("No intersections found. Select first object for next intersection.")

        # Check that tool state is reset
        self.assertIsNone(self.tool.first_object)
        self.assertIsNone(self.tool.second_object)

    def test_key_press_escape(self):
        """Test that pressing Escape cancels the current operation."""
        # Set up selection state
        self.tool.first_object = MagicMock()

        # Create a mock key event for Escape
        key_event = MagicMock()
        key_event.key.return_value = Qt.Key.Key_Escape

        # Press Escape
        self.tool.key_press(key_event)

        # Check that selection state is reset
        self.assertIsNone(self.tool.first_object)
        self.assertIsNone(self.tool.second_object)


if __name__ == '__main__':
    unittest.main()
