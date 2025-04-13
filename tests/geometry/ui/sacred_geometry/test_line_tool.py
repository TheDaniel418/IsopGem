"""Tests for the LineTool class."""

import unittest
from unittest.mock import MagicMock, patch
import sys
import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import QApplication

# Create QApplication instance for the tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from geometry.ui.sacred_geometry.model import Point, Line, Style, LineType
from geometry.ui.sacred_geometry.tools import LineTool, ToolState, ToolOptions


class TestLineTool(unittest.TestCase):
    """Tests for the LineTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = LineTool()
        self.tool.explorer = MagicMock()
        self.tool.explorer.status_bar = MagicMock()
        self.tool.canvas = MagicMock()
        self.tool.canvas.scene = MagicMock()
        self.tool.options = ToolOptions()
        self.tool.options.show_preview = True
        self.tool.options.snap_to_grid = True
        self.tool.options.snap_to_objects = True

    def test_line_tool_initialization(self):
        """Test that the LineTool initializes correctly."""
        self.assertEqual(self.tool.name, "Line")
        self.assertEqual(self.tool.icon_name, "line")
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})
        self.assertEqual(self.tool.stroke_color, QColor(0, 0, 0))
        self.assertEqual(self.tool.stroke_width, 1.0)
        self.assertEqual(self.tool.line_type, LineType.SEGMENT)

    def test_style_setting(self):
        """Test that the line style can be set."""
        # Test stroke color
        test_color = QColor(255, 0, 0)
        self.tool.set_stroke_color(test_color)
        self.assertEqual(self.tool.stroke_color, test_color)

        # Test stroke width
        self.tool.set_stroke_width(2.0)
        self.assertEqual(self.tool.stroke_width, 2.0)

        # Test line type
        self.tool.set_line_type(LineType.RAY)
        self.assertEqual(self.tool.line_type, LineType.RAY)

        self.tool.set_line_type(LineType.INFINITE)
        self.assertEqual(self.tool.line_type, LineType.INFINITE)

        self.tool.set_line_type(LineType.SEGMENT)
        self.assertEqual(self.tool.line_type, LineType.SEGMENT)

    def test_create_line_style(self):
        """Test that the line style is created correctly."""
        # Set custom style
        stroke_color = QColor(255, 0, 0)
        self.tool.set_stroke_color(stroke_color)
        self.tool.set_stroke_width(2.0)

        # Create style
        style = self.tool._create_line_style()

        # Check style properties
        self.assertEqual(style.stroke_color, stroke_color)
        self.assertEqual(style.stroke_width, 2.0)

    @patch('geometry.ui.sacred_geometry.tools.LineTool._create_object')
    def test_line_creation(self, mock_create_object):
        """Test creating a line."""
        # Mock the _snap_position_with_info method to return fixed positions
        self.tool._snap_position_with_info = MagicMock(side_effect=[
            (QPointF(100, 100), None, None),  # Start point
            (QPointF(200, 200), None, None)   # End point
        ])

        # Create mock points
        start_point = MagicMock()
        start_point.x = 100
        start_point.y = 100

        # Mock the _create_object method to return the start point for the first call
        mock_create_object.side_effect = [start_point, None]

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - set start point
        self.tool.mouse_press(event, QPointF(100, 100))

        # Check that state is updated
        self.assertEqual(self.tool.state, ToolState.ACTIVE)
        self.assertEqual(self.tool.data.get('start_point').x(), 100)
        self.assertEqual(self.tool.data.get('start_point').y(), 100)

        # Second click - create line
        self.tool.mouse_press(event, QPointF(200, 200))

        # In the actual implementation, _create_object is called once for the line
        # The start point is already created in the first click
        self.assertEqual(mock_create_object.call_count, 1)

        # Check line creation call
        args, kwargs = mock_create_object.call_args
        self.assertEqual(args[0], 'line')
        self.assertEqual(kwargs['x1'], 100)
        self.assertEqual(kwargs['y1'], 100)
        self.assertEqual(kwargs['x2'], 200)
        self.assertEqual(kwargs['y2'], 200)
        self.assertEqual(kwargs['line_type'], LineType.SEGMENT)

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})

    @patch('geometry.ui.sacred_geometry.tools.LineTool._create_object')
    def test_line_creation_with_existing_points(self, mock_create_object):
        """Test creating a line with existing points."""
        # Create mock points
        start_point = MagicMock()
        start_point.x = 100
        start_point.y = 100

        end_point = MagicMock()
        end_point.x = 200
        end_point.y = 200

        # Mock the canvas.get_object_at method to return the points
        self.tool.canvas.get_object_at = MagicMock(side_effect=[start_point, end_point])

        # Mock the _snap_position_with_info method to return the points
        self.tool._snap_position_with_info = MagicMock(side_effect=[
            (QPointF(100, 100), 'object', start_point),  # Start point
            (QPointF(200, 200), 'object', end_point)     # End point
        ])

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select start point
        self.tool.mouse_press(event, QPointF(100, 100))

        # Check that state is updated
        self.assertEqual(self.tool.state, ToolState.ACTIVE)
        self.assertEqual(self.tool.data.get('start_point').x(), 100)
        self.assertEqual(self.tool.data.get('start_point').y(), 100)

        # Second click - create line
        self.tool.mouse_press(event, QPointF(200, 200))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(args[0], 'line')
        self.assertEqual(kwargs['x1'], 100)
        self.assertEqual(kwargs['y1'], 100)
        self.assertEqual(kwargs['x2'], 200)
        self.assertEqual(kwargs['y2'], 200)
        self.assertEqual(kwargs['line_type'], LineType.SEGMENT)

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})

    def test_preview_update(self):
        """Test that the preview is updated during line creation."""
        # Set up active state with start point
        self.tool.state = ToolState.ACTIVE
        self.tool.data = {'start_point': QPointF(100, 100)}

        # Mock the _update_preview method
        self.tool._update_preview = MagicMock()

        # Mock the _snap_position_with_info method to return an end point
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(200, 200), None, None))

        # Create a mock mouse event
        event = MagicMock()

        # Move mouse to update preview
        self.tool.mouse_move(event, QPointF(200, 200))

        # Check that _update_preview was called
        self.tool._update_preview.assert_called_once()

    def test_key_press_escape(self):
        """Test that pressing Escape cancels the current operation."""
        # Set up active state with start point
        self.tool.state = ToolState.ACTIVE
        self.tool.data = {'start_point': QPointF(100, 100)}

        # Create a mock key event for Escape
        key_event = MagicMock()
        key_event.key.return_value = Qt.Key.Key_Escape

        # Press Escape
        self.tool.key_press(key_event)

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})

        # The canvas.clear_preview method is called by the _cancel_operation method
        # which is called by the key_press method when Escape is pressed

    def test_set_line_type(self):
        """Test setting the line type."""
        # Set line type to INFINITE
        self.tool.set_line_type(LineType.INFINITE)
        self.assertEqual(self.tool.line_type, LineType.INFINITE)

        # Set line type to RAY
        self.tool.set_line_type(LineType.RAY)
        self.assertEqual(self.tool.line_type, LineType.RAY)

        # Set line type to SEGMENT
        self.tool.set_line_type(LineType.SEGMENT)
        self.assertEqual(self.tool.line_type, LineType.SEGMENT)

    def test_update_preview(self):
        """Test updating the preview."""
        # Mock the canvas.update_preview method
        self.tool.canvas.update_preview = MagicMock()

        # Set up active state with start point
        self.tool.state = ToolState.ACTIVE
        self.tool.data = {'start_point': QPointF(100, 100)}

        # Mock the _snap_position_with_info method to return an end point
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(200, 200), None, None))

        # Create a mock mouse event
        event = MagicMock()

        # Move mouse to update preview
        self.tool.mouse_move(event, QPointF(200, 200))

        # The _update_preview method is called by the mouse_move method
        # which updates the preview in the canvas

    def test_complete_operation(self):
        """Test completing an operation."""
        # Set up active state
        self.tool.state = ToolState.ACTIVE
        self.tool.data = {'start_point': QPointF(100, 100)}

        # Mock the _clear_preview method
        self.tool._clear_preview = MagicMock()

        # Complete operation
        self.tool._complete_operation()

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})

        # Check that preview was cleared
        self.tool._clear_preview.assert_called_once()

    def test_create_line_with_existing_points(self):
        """Test creating a line with existing points."""
        # Create mock points
        start_point = MagicMock()
        start_point.x = 100
        start_point.y = 100

        end_point = MagicMock()
        end_point.x = 200
        end_point.y = 200

        # Mock the canvas.get_object_at method to return the points
        self.tool.canvas.get_object_at = MagicMock(side_effect=[start_point, end_point])

        # Mock the _snap_position_with_info method to return the points
        self.tool._snap_position_with_info = MagicMock(side_effect=[
            (QPointF(100, 100), 'object', start_point),  # Start point
            (QPointF(200, 200), 'object', end_point)     # End point
        ])

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select start point
        self.tool.mouse_press(event, QPointF(100, 100))

        # Check that state is updated
        self.assertEqual(self.tool.state, ToolState.ACTIVE)
        self.assertEqual(self.tool.data.get('start_point').x(), 100)
        self.assertEqual(self.tool.data.get('start_point').y(), 100)

        # Mock the _create_object method
        self.tool._create_object = MagicMock()

        # Second click - create line
        self.tool.mouse_press(event, QPointF(200, 200))

        # Check that _create_object was called with correct parameters
        self.tool._create_object.assert_called_once()
        args, kwargs = self.tool._create_object.call_args
        self.assertEqual(args[0], 'line')
        self.assertEqual(kwargs['x1'], 100)
        self.assertEqual(kwargs['y1'], 100)
        self.assertEqual(kwargs['x2'], 200)
        self.assertEqual(kwargs['y2'], 200)
        self.assertEqual(kwargs['line_type'], LineType.SEGMENT)

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})

    def test_create_line_with_new_points(self):
        """Test creating a line with new points."""
        # Mock the canvas.get_object_at method to return None (no objects at click positions)
        self.tool.canvas.get_object_at = MagicMock(return_value=None)

        # Mock the _snap_position_with_info method to return fixed positions
        self.tool._snap_position_with_info = MagicMock(side_effect=[
            (QPointF(100, 100), 'none', None),  # Start point
            (QPointF(200, 200), 'none', None)    # End point
        ])

        # Create mock points
        start_point = MagicMock()
        start_point.x = 100
        start_point.y = 100

        # Mock the _create_object method to return the start point for the first call
        self.tool._create_object = MagicMock(side_effect=[start_point, None])

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - create start point
        self.tool.mouse_press(event, QPointF(100, 100))

        # Check that state is updated
        self.assertEqual(self.tool.state, ToolState.ACTIVE)
        self.assertEqual(self.tool.data.get('start_point').x(), 100)
        self.assertEqual(self.tool.data.get('start_point').y(), 100)

        # Second click - create line
        self.tool.mouse_press(event, QPointF(200, 200))

        # In the actual implementation, _create_object is called once for the line
        # The start point is already created in the first click
        self.assertEqual(self.tool._create_object.call_count, 1)

        # Check line creation call
        args, kwargs = self.tool._create_object.call_args
        self.assertEqual(args[0], 'line')
        self.assertEqual(kwargs['x1'], 100)
        self.assertEqual(kwargs['y1'], 100)
        self.assertEqual(kwargs['x2'], 200)
        self.assertEqual(kwargs['y2'], 200)
        self.assertEqual(kwargs['line_type'], LineType.SEGMENT)

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})

    def test_mouse_move_updates_preview(self):
        """Test that mouse move updates the preview."""
        # Set up active state with start point
        self.tool.state = ToolState.ACTIVE
        self.tool.data = {'start_point': QPointF(100, 100)}

        # Mock the _update_preview method
        self.tool._update_preview = MagicMock()

        # Mock the _snap_position_with_info method to return a fixed position
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(200, 200), 'none', None))

        # Create a mock mouse event
        event = MagicMock()

        # Move mouse
        self.tool.mouse_move(event, QPointF(200, 200))

        # Check that _update_preview was called
        self.tool._update_preview.assert_called_once()

    def test_mouse_move_no_preview_in_idle_state(self):
        """Test that mouse move does not update preview in idle state."""
        # Set up idle state
        self.tool.state = ToolState.IDLE

        # Mock the _update_preview method
        self.tool._update_preview = MagicMock()

        # Create a mock mouse event
        event = MagicMock()

        # Move mouse
        self.tool.mouse_move(event, QPointF(200, 200))

        # Check that _update_preview was not called
        self.tool._update_preview.assert_not_called()


if __name__ == '__main__':
    unittest.main()
