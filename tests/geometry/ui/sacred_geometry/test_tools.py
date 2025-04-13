"""Tests for the geometry tools."""

import unittest
from unittest.mock import MagicMock, patch
import math
import sys
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QMouseEvent
from PyQt6.QtWidgets import QApplication

# Create QApplication instance for the tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from geometry.ui.sacred_geometry.model import Point, Line, LineType, Style
from geometry.ui.sacred_geometry.tools import LineTool, CircleTool, ToolState, ToolOptions


class TestLineTool(unittest.TestCase):
    """Tests for the LineTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = LineTool()
        self.tool.explorer = MagicMock()
        self.tool.canvas = MagicMock()
        self.tool.canvas.scene = MagicMock()
        self.tool.options = ToolOptions()
        self.tool.options.show_preview = True
        self.tool.options.snap_to_grid = True
        self.tool.options.snap_to_objects = True
        self.tool._init_tool()

    def test_line_tool_initialization(self):
        """Test that the LineTool initializes correctly."""
        self.assertEqual(self.tool.name, "Line")
        self.assertEqual(self.tool.icon_name, "line")
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.line_type, LineType.SEGMENT)
        self.assertEqual(self.tool.stroke_color, QColor(0, 0, 0))
        self.assertEqual(self.tool.stroke_width, 1.0)
        self.assertEqual(self.tool.stroke_style, Qt.PenStyle.SolidLine)

    def test_line_type_setting(self):
        """Test that the line type can be set."""
        self.tool.set_line_type(LineType.RAY)
        self.assertEqual(self.tool.line_type, LineType.RAY)

        self.tool.set_line_type(LineType.INFINITE)
        self.assertEqual(self.tool.line_type, LineType.INFINITE)

        self.tool.set_line_type(LineType.SEGMENT)
        self.assertEqual(self.tool.line_type, LineType.SEGMENT)

    def test_line_style_setting(self):
        """Test that the line style can be set."""
        # Test stroke color
        test_color = QColor(255, 0, 0)
        self.tool.set_stroke_color(test_color)
        self.assertEqual(self.tool.stroke_color, test_color)

        # Test stroke width
        self.tool.set_stroke_width(2.5)
        self.assertEqual(self.tool.stroke_width, 2.5)

        # Test stroke style
        self.tool.set_stroke_style(Qt.PenStyle.DashLine)
        self.assertEqual(self.tool.stroke_style, Qt.PenStyle.DashLine)

    def test_create_line_style(self):
        """Test that the line style is created correctly."""
        # Set custom style
        test_color = QColor(255, 0, 0)
        self.tool.set_stroke_color(test_color)
        self.tool.set_stroke_width(2.5)
        self.tool.set_stroke_style(Qt.PenStyle.DashLine)

        # Create style
        style = self.tool._create_line_style()

        # Check style properties
        self.assertEqual(style.stroke_color, test_color)
        self.assertEqual(style.stroke_width, 2.5)
        self.assertEqual(style.stroke_style, Qt.PenStyle.DashLine)

    @patch('geometry.ui.sacred_geometry.tools.LineTool._create_object')
    def test_line_creation(self, mock_create_object):
        """Test that lines can be created."""
        # Mock the _snap_position_with_info method to return a fixed position
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - set start point
        self.tool.mouse_press(event, QPointF(0, 0))
        self.assertEqual(self.tool.state, ToolState.ACTIVE)
        self.assertEqual(self.tool.data['start_point'], QPointF(0, 0))

        # Change position for second point
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 100), None, None))

        # Second click - create line
        self.tool.mouse_press(event, QPointF(100, 100))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(args[0], 'line')
        self.assertEqual(kwargs['x1'], 0)
        self.assertEqual(kwargs['y1'], 0)
        self.assertEqual(kwargs['x2'], 100)
        self.assertEqual(kwargs['y2'], 100)
        self.assertEqual(kwargs['line_type'], LineType.SEGMENT)

        # Check that the tool state was reset
        self.assertEqual(self.tool.state, ToolState.IDLE)

    @patch('geometry.ui.sacred_geometry.tools.LineTool._create_object')
    def test_different_line_types(self, mock_create_object):
        """Test that different line types can be created."""
        # Mock the _snap_position_with_info method to return a fixed position
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Test ray
        self.tool.set_line_type(LineType.RAY)

        # First click - set start point
        self.tool.mouse_press(event, QPointF(0, 0))

        # Change position for second point
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 100), None, None))

        # Second click - create ray
        self.tool.mouse_press(event, QPointF(100, 100))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(kwargs['line_type'], LineType.RAY)

        # Reset mock
        mock_create_object.reset_mock()

        # Test infinite line
        self.tool.set_line_type(LineType.INFINITE)

        # First click - set start point
        self.tool.mouse_press(event, QPointF(0, 0))

        # Change position for second point
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 100), None, None))

        # Second click - create infinite line
        self.tool.mouse_press(event, QPointF(100, 100))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(kwargs['line_type'], LineType.INFINITE)


class TestCircleTool(unittest.TestCase):
    """Tests for the CircleTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = CircleTool()
        self.tool.explorer = MagicMock()
        self.tool.canvas = MagicMock()
        self.tool.canvas.scene = MagicMock()
        self.tool.options = ToolOptions()
        self.tool.options.show_preview = True
        self.tool.options.snap_to_grid = True
        self.tool.options.snap_to_objects = True

        # Initialize data without creating toolbar
        self.tool.data = {
            'center_point': None,
            'preview_circle': None,
            'snap_target': None,
            'snap_type': None,
            'points': []
        }
        self.tool.state = ToolState.IDLE

    def test_circle_tool_initialization(self):
        """Test that the CircleTool initializes correctly."""
        self.assertEqual(self.tool.name, "Circle")
        self.assertEqual(self.tool.icon_name, "circle")
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.stroke_color, QColor(0, 0, 0))
        self.assertEqual(self.tool.stroke_width, 1.0)
        self.assertEqual(self.tool.stroke_style, Qt.PenStyle.SolidLine)
        self.assertEqual(self.tool.fill_color.alpha(), 50)  # Transparent white
        self.assertEqual(self.tool.fill_style, Qt.BrushStyle.SolidPattern)
        self.assertEqual(self.tool.mode, CircleTool.MODE_CENTER_POINT)
        self.assertEqual(self.tool.fixed_radius, 100.0)

    def test_circle_modes(self):
        """Test that circle modes can be changed."""
        # Test center-point mode
        self.tool._on_mode_changed(CircleTool.MODE_CENTER_POINT)
        self.assertEqual(self.tool.mode, CircleTool.MODE_CENTER_POINT)

        # Test fixed-radius mode
        self.tool._on_mode_changed(CircleTool.MODE_FIXED_RADIUS)
        self.assertEqual(self.tool.mode, CircleTool.MODE_FIXED_RADIUS)

        # Test diameter mode
        self.tool._on_mode_changed(CircleTool.MODE_DIAMETER)
        self.assertEqual(self.tool.mode, CircleTool.MODE_DIAMETER)

        # Test three-points mode
        self.tool._on_mode_changed(CircleTool.MODE_THREE_POINTS)
        self.assertEqual(self.tool.mode, CircleTool.MODE_THREE_POINTS)

    def test_fixed_radius(self):
        """Test that fixed radius can be set."""
        # Set fixed radius
        self.tool.set_fixed_radius(50.0)
        self.assertEqual(self.tool.fixed_radius, 50.0)

    def test_circle_style_setting(self):
        """Test that the circle style can be set."""
        # Test stroke color
        test_color = QColor(255, 0, 0)
        self.tool.set_stroke_color(test_color)
        self.assertEqual(self.tool.stroke_color, test_color)

        # Test stroke width
        self.tool.set_stroke_width(2.5)
        self.assertEqual(self.tool.stroke_width, 2.5)

        # Test stroke style
        self.tool.set_stroke_style(Qt.PenStyle.DashLine)
        self.assertEqual(self.tool.stroke_style, Qt.PenStyle.DashLine)

        # Test fill color
        fill_color = QColor(0, 255, 0, 100)
        self.tool.set_fill_color(fill_color)
        self.assertEqual(self.tool.fill_color, fill_color)

        # Test fill style
        self.tool.set_fill_style(Qt.BrushStyle.DiagCrossPattern)
        self.assertEqual(self.tool.fill_style, Qt.BrushStyle.DiagCrossPattern)

    def test_create_circle_style(self):
        """Test that the circle style is created correctly."""
        # Set custom style
        stroke_color = QColor(255, 0, 0)
        fill_color = QColor(0, 255, 0, 100)
        self.tool.set_stroke_color(stroke_color)
        self.tool.set_stroke_width(2.5)
        self.tool.set_stroke_style(Qt.PenStyle.DashLine)
        self.tool.set_fill_color(fill_color)
        self.tool.set_fill_style(Qt.BrushStyle.DiagCrossPattern)

        # Create style
        style = self.tool._create_circle_style()

        # Check style properties
        self.assertEqual(style.stroke_color, stroke_color)
        self.assertEqual(style.stroke_width, 2.5)
        self.assertEqual(style.stroke_style, Qt.PenStyle.DashLine)
        self.assertEqual(style.fill_color, fill_color)
        self.assertEqual(style.fill_style, Qt.BrushStyle.DiagCrossPattern)

    @patch('geometry.ui.sacred_geometry.tools.CircleTool._create_object')
    def test_circle_creation(self, mock_create_object):
        """Test that circles can be created."""
        # Mock the _snap_position_with_info method to return a fixed position
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - set center point
        self.tool.mouse_press(event, QPointF(0, 0))
        self.assertEqual(self.tool.state, ToolState.ACTIVE)
        self.assertEqual(self.tool.data['center_point'], QPointF(0, 0))

        # Change position for second point
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 0), None, None))

        # Second click - create circle
        self.tool.mouse_press(event, QPointF(100, 0))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(args[0], 'circle')
        self.assertEqual(kwargs['cx'], 0)
        self.assertEqual(kwargs['cy'], 0)
        self.assertEqual(kwargs['radius'], 100.0)

        # Check that the tool state was reset
        self.assertEqual(self.tool.state, ToolState.IDLE)

    @patch('geometry.ui.sacred_geometry.tools.CircleTool._create_object')
    def test_fixed_radius_circle_creation(self, mock_create_object):
        """Test that fixed radius circles can be created."""
        # Set fixed radius mode
        self.tool._on_mode_changed(CircleTool.MODE_FIXED_RADIUS)
        self.tool.set_fixed_radius(50.0)

        # Mock the _snap_position_with_info method to return a fixed position
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Click to create circle
        self.tool.mouse_press(event, QPointF(0, 0))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        _, kwargs = mock_create_object.call_args
        self.assertEqual(kwargs['radius'], 50.0)  # Should use fixed radius

    @patch('geometry.ui.sacred_geometry.tools.CircleTool._create_object')
    def test_diameter_circle_creation(self, mock_create_object):
        """Test that circles can be created by diameter."""
        # Set diameter mode
        self.tool._on_mode_changed(CircleTool.MODE_DIAMETER)

        # Mock the _snap_position_with_info method to return fixed positions
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - set first point of diameter
        self.tool.mouse_press(event, QPointF(0, 0))
        self.assertEqual(self.tool.state, ToolState.ACTIVE)

        # Change position for second point
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 0), None, None))

        # Second click - create circle
        self.tool.mouse_press(event, QPointF(100, 0))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        _, kwargs = mock_create_object.call_args
        self.assertEqual(kwargs['cx'], 50.0)  # Center should be midpoint of diameter
        self.assertEqual(kwargs['cy'], 0.0)
        self.assertEqual(kwargs['radius'], 50.0)  # Radius should be half of diameter

    @patch('geometry.ui.sacred_geometry.tools.CircleTool._create_object')
    def test_three_points_circle_creation(self, mock_create_object):
        """Test that circles can be created through three points."""
        # Set three-points mode
        self.tool._on_mode_changed(CircleTool.MODE_THREE_POINTS)

        # Mock the _snap_position_with_info method to return fixed positions
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - set first point
        self.tool.mouse_press(event, QPointF(0, 0))
        self.assertEqual(self.tool.state, ToolState.ACTIVE)

        # Second click - set second point
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 0), None, None))
        self.tool.mouse_press(event, QPointF(100, 0))

        # Mock the _calculate_circle_from_three_points method to return a fixed result
        self.tool._calculate_circle_from_three_points = MagicMock(return_value=(QPointF(50, 25), 50.0))

        # Third click - set third point and create circle
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(50, 50), None, None))
        self.tool.mouse_press(event, QPointF(50, 50))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        _, kwargs = mock_create_object.call_args
        self.assertEqual(kwargs['cx'], 50.0)
        self.assertEqual(kwargs['cy'], 25.0)
        self.assertEqual(kwargs['radius'], 50.0)


if __name__ == '__main__':
    unittest.main()
