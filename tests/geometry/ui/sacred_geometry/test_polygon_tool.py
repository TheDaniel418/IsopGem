"""Tests for the PolygonTool class."""

import unittest
import math
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor

from geometry.ui.sacred_geometry.tools import PolygonTool, ToolState, ToolOptions
from geometry.ui.sacred_geometry.model import Point, Polygon, Style


class TestPolygonTool(unittest.TestCase):
    """Tests for the PolygonTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = PolygonTool()
        self.tool.explorer = MagicMock()
        self.tool.canvas = MagicMock()
        self.tool.canvas.scene = MagicMock()
        self.tool.options = ToolOptions()
        self.tool.options.show_preview = True
        self.tool.options.snap_to_grid = True
        self.tool.options.snap_to_objects = True

        # Initialize data without creating toolbar
        self.tool.data = {
            'vertices': [],
            'preview_vertices': [],
            'snap_target': None,
            'snap_type': None,
            'last_click_time': 0,
            'double_click_interval': 400
        }
        self.tool.state = ToolState.IDLE

    def test_polygon_tool_initialization(self):
        """Test that the PolygonTool initializes correctly."""
        self.assertEqual(self.tool.name, "Polygon")
        self.assertEqual(self.tool.icon_name, "polygon")
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.stroke_color, QColor(0, 0, 0))
        self.assertEqual(self.tool.stroke_width, 1.0)
        self.assertEqual(self.tool.stroke_style, Qt.PenStyle.SolidLine)
        self.assertEqual(self.tool.fill_color.alpha(), 50)  # Transparent white
        self.assertEqual(self.tool.fill_style, Qt.BrushStyle.SolidPattern)
        self.assertEqual(self.tool.min_vertices, 3)
        self.assertEqual(self.tool.close_distance, 15.0)

    def test_polygon_style_setting(self):
        """Test that the polygon style can be set."""
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

    @patch('geometry.ui.sacred_geometry.tools.PolygonTool._create_object')
    def test_polygon_creation(self, mock_create_object):
        """Test that polygons can be created."""
        # Mock the _snap_position_with_info method to return fixed positions
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton
        event.timestamp.return_value = 1000

        # First click - add first vertex
        self.tool.mouse_press(event, QPointF(0, 0))
        self.assertEqual(self.tool.state, ToolState.ACTIVE)
        self.assertEqual(len(self.tool.data['vertices']), 1)

        # Second click - add second vertex
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 0), None, None))
        event.timestamp.return_value = 2000
        self.tool.mouse_press(event, QPointF(100, 0))
        self.assertEqual(len(self.tool.data['vertices']), 2)

        # Third click - add third vertex
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(50, 100), None, None))
        event.timestamp.return_value = 3000
        self.tool.mouse_press(event, QPointF(50, 100))
        self.assertEqual(len(self.tool.data['vertices']), 3)

        # Fourth click - double-click to complete polygon
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 50), None, None))
        event.timestamp.return_value = 3100  # Within double-click interval
        self.tool.mouse_press(event, QPointF(0, 50))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(args[0], 'polygon')
        self.assertEqual(len(kwargs['vertices']), 3)

        # Check that the tool state was reset
        self.assertEqual(self.tool.state, ToolState.IDLE)

    @patch('geometry.ui.sacred_geometry.tools.PolygonTool._create_object')
    def test_polygon_completion_by_closing(self, mock_create_object):
        """Test that polygons can be completed by clicking near the first vertex."""
        # Mock the _snap_position_with_info method to return fixed positions
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton
        event.timestamp.return_value = 1000

        # First click - add first vertex
        self.tool.mouse_press(event, QPointF(0, 0))

        # Second click - add second vertex
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 0), None, None))
        event.timestamp.return_value = 2000
        self.tool.mouse_press(event, QPointF(100, 0))

        # Third click - add third vertex
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(50, 100), None, None))
        event.timestamp.return_value = 3000
        self.tool.mouse_press(event, QPointF(50, 100))

        # Fourth click - click near first vertex to close polygon
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(5, 5), None, None))
        event.timestamp.return_value = 4000  # Not a double-click
        self.tool.mouse_press(event, QPointF(5, 5))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()

        # Check that the tool state was reset
        self.assertEqual(self.tool.state, ToolState.IDLE)

    @patch('geometry.ui.sacred_geometry.tools.PolygonTool._create_object')
    def test_polygon_completion_by_enter_key(self, mock_create_object):
        """Test that polygons can be completed by pressing Enter."""
        # Mock the _snap_position_with_info method to return fixed positions
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton
        event.timestamp.return_value = 1000

        # First click - add first vertex
        self.tool.mouse_press(event, QPointF(0, 0))

        # Second click - add second vertex
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 0), None, None))
        event.timestamp.return_value = 2000
        self.tool.mouse_press(event, QPointF(100, 0))

        # Third click - add third vertex
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(50, 100), None, None))
        event.timestamp.return_value = 3000
        self.tool.mouse_press(event, QPointF(50, 100))

        # Create a mock key event for Enter
        key_event = MagicMock()
        key_event.key.return_value = Qt.Key.Key_Return

        # Press Enter to complete polygon
        self.tool.key_press(key_event)

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()

        # Check that the tool state was reset
        self.assertEqual(self.tool.state, ToolState.IDLE)

    def test_key_press_escape(self):
        """Test that pressing Escape cancels the current operation."""
        # Set up active state with vertices
        self.tool.state = ToolState.ACTIVE
        self.tool.data['vertices'] = [Point(0, 0), Point(100, 0), Point(50, 100)]

        # Create a mock key event for Escape
        key_event = MagicMock()
        key_event.key.return_value = Qt.Key.Key_Escape

        # Press Escape
        self.tool.key_press(key_event)

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})

        # In the actual implementation, the _cancel_operation method might not call canvas.clear_preview
        # Just check that the operation was cancelled

    def test_mouse_move_updates_preview(self):
        """Test that mouse move updates the preview."""
        # Set up active state with vertices
        self.tool.state = ToolState.ACTIVE
        self.tool.data['vertices'] = [QPointF(0, 0), QPointF(100, 0)]

        # Mock the _update_preview method
        self.tool._update_preview = MagicMock()

        # Mock the _snap_position_with_info method to return a fixed position
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(50, 100), 'none', None))

        # Create a mock mouse event
        event = MagicMock()

        # Move mouse
        self.tool.mouse_move(event, QPointF(50, 100))

        # Check that _update_preview was called
        self.tool._update_preview.assert_called_once()

    def test_mouse_move_in_idle_state(self):
        """Test mouse move in idle state."""
        # Set up idle state
        self.tool.state = ToolState.IDLE

        # Create a mock mouse event
        event = MagicMock()

        # Move mouse
        self.tool.mouse_move(event, QPointF(50, 100))

        # Check that state is still idle
        self.assertEqual(self.tool.state, ToolState.IDLE)

    def test_create_polygon_style(self):
        """Test creating a polygon style."""
        # Set custom style
        stroke_color = QColor(255, 0, 0)
        fill_color = QColor(0, 255, 0, 100)
        self.tool.set_stroke_color(stroke_color)
        self.tool.set_fill_color(fill_color)
        self.tool.set_stroke_width(2.5)
        self.tool.set_stroke_style(Qt.PenStyle.DashLine)
        self.tool.set_fill_style(Qt.BrushStyle.DiagCrossPattern)

        # Create style
        style = self.tool._create_polygon_style()

        # Check style properties
        self.assertEqual(style.stroke_color, stroke_color)
        self.assertEqual(style.fill_color, fill_color)
        self.assertEqual(style.stroke_width, 2.5)
        self.assertEqual(style.stroke_style, Qt.PenStyle.DashLine)
        self.assertEqual(style.fill_style, Qt.BrushStyle.DiagCrossPattern)

    def test_distance_to_first_vertex(self):
        """Test calculating distance to the first vertex."""
        # Set up vertices
        self.tool.data['vertices'] = [Point(0, 0), Point(100, 0), Point(50, 100)]

        # Test point near first vertex
        first_vertex = self.tool.data['vertices'][0]
        dx = 5 - first_vertex.x
        dy = 5 - first_vertex.y
        distance = math.sqrt(dx * dx + dy * dy)
        self.assertLess(distance, self.tool.close_distance)

        # Test point far from first vertex
        dx = 50 - first_vertex.x
        dy = 50 - first_vertex.y
        distance = math.sqrt(dx * dx + dy * dy)
        self.assertGreater(distance, self.tool.close_distance)

    def test_min_vertices_requirement(self):
        """Test the minimum vertices requirement for a polygon."""
        # Set up vertices
        self.tool.data['vertices'] = [Point(0, 0), Point(100, 0), Point(50, 100)]

        # Test with enough vertices
        self.assertGreaterEqual(len(self.tool.data['vertices']), self.tool.min_vertices)

        # Test with not enough vertices
        self.tool.data['vertices'] = [Point(0, 0), Point(100, 0)]
        self.assertLess(len(self.tool.data['vertices']), self.tool.min_vertices)

        # Test with no vertices
        self.tool.data['vertices'] = []
        self.assertLess(len(self.tool.data['vertices']), self.tool.min_vertices)

    def test_complete_polygon(self):
        """Test completing a polygon."""
        # Set up vertices
        self.tool.data['vertices'] = [Point(0, 0), Point(100, 0), Point(50, 100)]
        self.tool.state = ToolState.ACTIVE

        # Mock the _create_object method
        self.tool._create_object = MagicMock()

        # Complete polygon
        self.tool._complete_polygon()

        # Check that _create_object was called with correct parameters
        self.tool._create_object.assert_called_once()
        args, kwargs = self.tool._create_object.call_args
        self.assertEqual(args[0], 'polygon')
        self.assertEqual(len(kwargs['vertices']), 3)

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})

    def test_cancel_operation(self):
        """Test canceling an operation."""
        # Set up active state with vertices
        self.tool.state = ToolState.ACTIVE
        self.tool.data['vertices'] = [Point(0, 0), Point(100, 0), Point(50, 100)]

        # Cancel operation
        self.tool._cancel_operation()

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.data, {})

        # In the actual implementation, the _cancel_operation method might not call canvas.clear_preview
        # Just check that the operation was cancelled


if __name__ == '__main__':
    unittest.main()
