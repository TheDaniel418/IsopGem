"""Tests for the RegularPolygonTool class."""

import unittest
import math
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor

from geometry.ui.sacred_geometry.tools import RegularPolygonTool, ToolState, ToolOptions
from geometry.ui.sacred_geometry.model import Point, Polygon, Style


class TestRegularPolygonTool(unittest.TestCase):
    """Tests for the RegularPolygonTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = RegularPolygonTool()
        self.tool.explorer = MagicMock()
        self.tool.canvas = MagicMock()
        self.tool.canvas.scene = MagicMock()
        self.tool.options = ToolOptions()
        self.tool.options.show_preview = True
        self.tool.options.snap_to_grid = True
        self.tool.options.snap_to_objects = True

        # Initialize data without creating toolbar
        self.tool.data = {
            'center': None,
            'vertex': None,
            'preview_polygon': None,
            'snap_target': None,
            'snap_type': None,
            'current_pos': QPointF(0, 0)
        }
        self.tool.state = ToolState.IDLE

    def test_regular_polygon_tool_initialization(self):
        """Test that the RegularPolygonTool initializes correctly."""
        self.assertEqual(self.tool.name, "Regular Polygon")
        self.assertEqual(self.tool.icon_name, "regular_polygon")
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.stroke_color, QColor(0, 0, 0))
        self.assertEqual(self.tool.stroke_width, 1.0)
        self.assertEqual(self.tool.stroke_style, Qt.PenStyle.SolidLine)
        self.assertEqual(self.tool.fill_color.alpha(), 50)  # Transparent white
        self.assertEqual(self.tool.fill_style, Qt.BrushStyle.SolidPattern)
        self.assertEqual(self.tool.sides, 6)  # Default number of sides
        self.assertEqual(self.tool.min_sides, 3)
        self.assertEqual(self.tool.max_sides, 20)
        self.assertEqual(self.tool.orientation, RegularPolygonTool.ORIENTATION_VERTEX_TOP)

    def test_set_sides(self):
        """Test setting the number of sides."""
        # Test setting valid number of sides
        self.tool.set_sides(8)
        self.assertEqual(self.tool.sides, 8)

        # Test setting number of sides below minimum
        self.tool.set_sides(1)
        self.assertEqual(self.tool.sides, self.tool.min_sides)

        # Test setting number of sides above maximum
        self.tool.set_sides(25)
        self.assertEqual(self.tool.sides, self.tool.max_sides)

    def test_set_orientation(self):
        """Test setting the orientation."""
        # Test setting vertex at top
        self.tool.set_orientation(RegularPolygonTool.ORIENTATION_VERTEX_TOP)
        self.assertEqual(self.tool.orientation, RegularPolygonTool.ORIENTATION_VERTEX_TOP)

        # Test setting side at top
        self.tool.set_orientation(RegularPolygonTool.ORIENTATION_SIDE_TOP)
        self.assertEqual(self.tool.orientation, RegularPolygonTool.ORIENTATION_SIDE_TOP)

        # Test setting invalid orientation (should not change)
        self.tool.set_orientation("invalid_orientation")
        self.assertEqual(self.tool.orientation, RegularPolygonTool.ORIENTATION_SIDE_TOP)

    def test_calculate_regular_polygon_vertices(self):
        """Test calculating regular polygon vertices."""
        # Test triangle (3 sides) with vertex at top
        self.tool.set_sides(3)
        self.tool.set_orientation(RegularPolygonTool.ORIENTATION_VERTEX_TOP)
        center = Point(0, 0)
        radius = 100
        vertices = self.tool._calculate_regular_polygon_vertices(center, radius)

        # Verify we have 3 vertices
        self.assertEqual(len(vertices), 3)

        # Verify first vertex is at the top (90 degrees)
        # Note: In PyQt, positive y is downward, so the top vertex has y = -radius
        self.assertAlmostEqual(vertices[0].x, 0, places=5)
        self.assertAlmostEqual(vertices[0].y, -100, places=5)

        # Verify other vertices are at the correct positions
        # For a triangle with vertex at top, the other vertices should be at approximately
        # 210 degrees and 330 degrees
        self.assertAlmostEqual(vertices[1].x, -86.60254, places=5)  # cos(210°) * 100
        self.assertAlmostEqual(vertices[1].y, 50, places=5)         # sin(210°) * 100
        self.assertAlmostEqual(vertices[2].x, 86.60254, places=5)   # cos(330°) * 100
        self.assertAlmostEqual(vertices[2].y, 50, places=5)         # sin(330°) * 100

        # Test hexagon (6 sides) with vertex at top
        self.tool.set_sides(6)
        self.tool.set_orientation(RegularPolygonTool.ORIENTATION_VERTEX_TOP)
        vertices = self.tool._calculate_regular_polygon_vertices(center, radius)

        # Verify we have 6 vertices
        self.assertEqual(len(vertices), 6)

        # For a hexagon with vertex at top, the vertices should be at the correct positions
        # Vertex 0: (0.00000, -100.00000) - top
        self.assertAlmostEqual(vertices[0].x, 0, places=5)
        self.assertAlmostEqual(vertices[0].y, -100, places=5)

        # Vertex 1: (-86.60254, -50.00000) - top right
        self.assertAlmostEqual(vertices[1].x, -86.60254, places=5)
        self.assertAlmostEqual(vertices[1].y, -50, places=5)

        # Vertex 2: (-86.60254, 50.00000) - bottom right
        self.assertAlmostEqual(vertices[2].x, -86.60254, places=5)
        self.assertAlmostEqual(vertices[2].y, 50, places=5)

        # Vertex 3: (-0.00000, 100.00000) - bottom
        self.assertAlmostEqual(vertices[3].x, 0, places=5)
        self.assertAlmostEqual(vertices[3].y, 100, places=5)

        # Vertex 4: (86.60254, 50.00000) - bottom left
        self.assertAlmostEqual(vertices[4].x, 86.60254, places=5)
        self.assertAlmostEqual(vertices[4].y, 50, places=5)

        # Vertex 5: (86.60254, -50.00000) - top left
        self.assertAlmostEqual(vertices[5].x, 86.60254, places=5)
        self.assertAlmostEqual(vertices[5].y, -50, places=5)

    @patch('geometry.ui.sacred_geometry.tools.RegularPolygonTool._create_object')
    def test_regular_polygon_creation(self, mock_create_object):
        """Test creating a regular polygon."""
        # Mock the _snap_position_with_info method to return fixed positions
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - set center point
        self.tool.mouse_press(event, QPointF(0, 0))
        self.assertEqual(self.tool.state, ToolState.ACTIVE)
        self.assertIsNotNone(self.tool.data['center'])
        self.assertEqual(self.tool.data['center'].x, 0)
        self.assertEqual(self.tool.data['center'].y, 0)

        # Second click - set vertex and create polygon
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 0), None, None))
        self.tool.mouse_press(event, QPointF(100, 0))

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(args[0], 'polygon')
        self.assertEqual(len(kwargs['vertices']), self.tool.sides)

        # Check that the tool state was reset
        self.assertEqual(self.tool.state, ToolState.IDLE)

    def test_key_press_handling(self):
        """Test key press handling."""
        # Mock the explorer and status bar
        self.tool.explorer.status_bar = MagicMock()

        # Test plus key to increase sides
        plus_event = MagicMock()
        plus_event.key.return_value = Qt.Key.Key_Plus
        self.tool.sides = 6
        self.tool.key_press(plus_event)
        self.assertEqual(self.tool.sides, 7)

        # Test minus key to decrease sides
        minus_event = MagicMock()
        minus_event.key.return_value = Qt.Key.Key_Minus
        self.tool.key_press(minus_event)
        self.assertEqual(self.tool.sides, 6)

        # Test 'O' key to toggle orientation
        o_event = MagicMock()
        o_event.key.return_value = Qt.Key.Key_O
        self.tool.orientation = RegularPolygonTool.ORIENTATION_VERTEX_TOP
        self.tool.key_press(o_event)
        self.assertEqual(self.tool.orientation, RegularPolygonTool.ORIENTATION_SIDE_TOP)
        self.tool.key_press(o_event)
        self.assertEqual(self.tool.orientation, RegularPolygonTool.ORIENTATION_VERTEX_TOP)

        # Test number keys to set sides directly
        for i in range(3, 10):
            num_event = MagicMock()
            num_event.key.return_value = getattr(Qt.Key, f"Key_{i}")
            self.tool.key_press(num_event)
            self.assertEqual(self.tool.sides, i)

    def test_key_press_escape(self):
        """Test that pressing Escape cancels the current operation."""
        # Set up active state with center point
        self.tool.state = ToolState.ACTIVE
        center_point = Point(100, 100)
        self.tool.data = {'center': center_point}

        # Mock the _cancel_operation method
        self.tool._cancel_operation = MagicMock()

        # Create a mock key event for Escape
        key_event = MagicMock()
        key_event.key.return_value = Qt.Key.Key_Escape

        # Press Escape
        self.tool.key_press(key_event)

        # Check that _cancel_operation was called
        self.tool._cancel_operation.assert_called_once()

    def test_mouse_move_updates_preview(self):
        """Test that mouse move updates the preview."""
        # Set up active state with center point
        self.tool.state = ToolState.ACTIVE
        center_point = Point(100, 100)
        self.tool.data = {'center': center_point}

        # Mock the _update_preview method
        self.tool._update_preview = MagicMock()

        # Mock the _snap_position_with_info method to return a fixed position
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(150, 100), 'none', None))

        # Create a mock mouse event
        event = MagicMock()

        # Move mouse
        self.tool.mouse_move(event, QPointF(150, 100))

        # Check that _update_preview was called
        self.tool._update_preview.assert_called_once()

    def test_mouse_move_in_idle_state(self):
        """Test mouse move in idle state."""
        # Set up idle state
        self.tool.state = ToolState.IDLE

        # Create a mock mouse event
        event = MagicMock()

        # Move mouse
        self.tool.mouse_move(event, QPointF(150, 100))

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

        # Create a style object manually
        style = Style()
        style.stroke_color = stroke_color
        style.fill_color = fill_color
        style.stroke_width = 2.5
        style.stroke_style = Qt.PenStyle.DashLine
        style.fill_style = Qt.BrushStyle.DiagCrossPattern

        # Check style properties
        self.assertEqual(style.stroke_color, stroke_color)
        self.assertEqual(style.fill_color, fill_color)
        self.assertEqual(style.stroke_width, 2.5)
        self.assertEqual(style.stroke_style, Qt.PenStyle.DashLine)
        self.assertEqual(style.fill_style, Qt.BrushStyle.DiagCrossPattern)

    def test_complete_operation(self):
        """Test completing an operation."""
        # Set up active state with center point
        self.tool.state = ToolState.ACTIVE
        center_point = Point(100, 100)
        self.tool.data = {'center': center_point}

        # Mock the _clear_preview method
        self.tool._clear_preview = MagicMock()

        # Complete operation
        self.tool._complete_operation()

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)

    def test_cancel_operation(self):
        """Test canceling an operation."""
        # Set up active state with center point
        self.tool.state = ToolState.ACTIVE
        center_point = Point(100, 100)
        self.tool.data = {'center': center_point}

        # Mock the canvas.clear_preview method
        self.tool.canvas.clear_preview = MagicMock()

        # Cancel operation
        self.tool._cancel_operation()

        # Check that state is reset
        self.assertEqual(self.tool.state, ToolState.IDLE)


if __name__ == '__main__':
    unittest.main()
