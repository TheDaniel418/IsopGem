"""Tests for user interaction with tools."""

import unittest
from unittest.mock import MagicMock, patch
import sys
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import QApplication

# Create QApplication instance for the tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from geometry.ui.sacred_geometry.model import Point, Line, Circle, Style
from geometry.ui.sacred_geometry.tools import PointTool, LineTool, CircleTool, SelectionTool, ToolState, ToolOptions
from geometry.ui.sacred_geometry.explorer import SacredGeometryExplorer


class TestUserInteraction(unittest.TestCase):
    """Tests for user interaction with tools."""

    def setUp(self):
        """Set up the test."""
        # Create a mock explorer
        self.explorer = MagicMock(spec=SacredGeometryExplorer)
        self.explorer.canvas = MagicMock()
        self.explorer.canvas.scene = MagicMock()
        self.explorer.toolbar = MagicMock()
        self.explorer.status_bar = MagicMock()

        # Create tools
        self.point_tool = PointTool()
        self.line_tool = LineTool()
        self.circle_tool = CircleTool()
        self.selection_tool = SelectionTool()

        # Set up tools
        for tool in [self.point_tool, self.line_tool, self.circle_tool, self.selection_tool]:
            tool.explorer = self.explorer
            tool.canvas = self.explorer.canvas
            tool.options = ToolOptions()
            tool.options.show_preview = True
            tool.options.snap_to_grid = True
            tool.options.snap_to_objects = True
            # Skip _init_tool() as it requires UI components

    def test_keyboard_shortcuts(self):
        """Test keyboard shortcuts."""
        # Create a mock key event for Escape
        escape_event = MagicMock(spec=QKeyEvent)
        escape_event.key.return_value = Qt.Key.Key_Escape

        # Set up line tool with active state
        self.line_tool.state = ToolState.ACTIVE
        self.line_tool.data = {'start_point': QPointF(0, 0)}

        # Press Escape
        self.line_tool.key_press(escape_event)

        # Check that tool state was reset
        self.assertEqual(self.line_tool.state, ToolState.IDLE)
        self.assertEqual(self.line_tool.data, {})

        # Create a mock key event for Enter
        enter_event = MagicMock(spec=QKeyEvent)
        enter_event.key.return_value = Qt.Key.Key_Return

        # Set up polygon tool with active state
        self.line_tool.state = ToolState.ACTIVE
        self.line_tool.data = {'start_point': QPointF(0, 0)}

        # Mock the _complete_operation method
        self.line_tool._complete_operation = MagicMock()

        # Press Enter
        self.line_tool.key_press(enter_event)

        # Check that _complete_operation was called
        self.line_tool._complete_operation.assert_called_once()

    def test_mouse_interactions(self):
        """Test mouse interactions."""
        # Create mock mouse events
        press_event = MagicMock(spec=QMouseEvent)
        press_event.button.return_value = Qt.MouseButton.LeftButton

        move_event = MagicMock(spec=QMouseEvent)

        release_event = MagicMock(spec=QMouseEvent)
        release_event.button.return_value = Qt.MouseButton.LeftButton

        # Mock the _snap_position_with_info method
        self.point_tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 100), None, None))

        # Mock the _create_object method
        self.point_tool._create_object = MagicMock()

        # Press mouse button
        self.point_tool.mouse_press(press_event, QPointF(100, 100))

        # Check that _create_object was called
        self.point_tool._create_object.assert_called_once()

        # Set up selection tool with dragging state
        self.selection_tool.dragging = True
        self.selection_tool.drag_start_pos = QPointF(100, 100)
        self.selection_tool.drag_objects = [MagicMock()]

        # Mock the _move_objects method
        self.selection_tool._move_objects = MagicMock()

        # Move mouse
        self.selection_tool.mouse_move(move_event, QPointF(150, 150))

        # Check that _move_objects was called with correct parameters
        self.selection_tool._move_objects.assert_called_once()
        args, kwargs = self.selection_tool._move_objects.call_args
        self.assertEqual(args[0], 50)  # dx = 150 - 100
        self.assertEqual(args[1], 50)  # dy = 150 - 100

        # Release mouse button
        self.selection_tool.mouse_release(release_event, QPointF(150, 150))

        # Check that dragging state was reset
        self.assertFalse(self.selection_tool.dragging)
        self.assertIsNone(self.selection_tool.drag_start_pos)
        self.assertEqual(self.selection_tool.drag_objects, [])

    def test_double_click(self):
        """Test double-click interaction."""
        # Create a mock double-click event
        double_click_event = MagicMock(spec=QMouseEvent)
        double_click_event.button.return_value = Qt.MouseButton.LeftButton

        # Mock the _snap_position_with_info method
        self.selection_tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 100), None, None))

        # Create a mock object
        mock_obj = MagicMock()
        mock_obj.x = 100
        mock_obj.y = 100

        # Mock the canvas.find_object_at method to return the object
        self.explorer.canvas.find_object_at = MagicMock(return_value=mock_obj)

        # Mock the _edit_object_properties method
        self.selection_tool._edit_object_properties = MagicMock()

        # Double-click on object
        self.selection_tool.mouse_double_click(double_click_event, QPointF(100, 100))

        # Check that _edit_object_properties was called with the object
        self.selection_tool._edit_object_properties.assert_called_once_with(mock_obj)

    def test_tool_options(self):
        """Test tool options."""
        # Test snap to grid option
        self.point_tool.options.snap_to_grid = True
        self.point_tool._snap_to_grid = MagicMock(return_value=QPointF(100, 100))

        # Mock the _snap_to_objects method to return no snap
        self.point_tool._snap_to_objects = MagicMock(return_value=(None, None))

        # Check that snap to grid is used
        pos, snap_type, snap_target = self.point_tool._snap_position_with_info(QPointF(95, 95))
        self.assertEqual(pos, QPointF(100, 100))
        self.assertEqual(snap_type, 'grid')

        # Test snap to objects option
        self.point_tool.options.snap_to_grid = False
        self.point_tool.options.snap_to_objects = True

        # Mock the _snap_to_objects method to return a snap
        mock_obj = MagicMock()
        self.point_tool._snap_to_objects = MagicMock(return_value=(QPointF(200, 200), mock_obj))

        # Check that snap to objects is used
        pos, snap_type, snap_target = self.point_tool._snap_position_with_info(QPointF(195, 195))
        self.assertEqual(pos, QPointF(200, 200))
        self.assertEqual(snap_type, 'object')
        self.assertEqual(snap_target, mock_obj)

        # Test show preview option
        self.line_tool.options.show_preview = True
        self.line_tool.state = ToolState.ACTIVE
        self.line_tool.data = {'start_point': QPointF(0, 0)}

        # Mock the _update_preview method
        self.line_tool._update_preview = MagicMock()

        # Move mouse
        self.line_tool.mouse_move(MagicMock(), QPointF(100, 100))

        # Check that _update_preview was called
        self.line_tool._update_preview.assert_called_once()

        # Test continuous creation option
        self.point_tool.options.continuous_creation = True

        # Mock the _create_object method
        self.point_tool._create_object = MagicMock()

        # Mock the _snap_position_with_info method
        self.point_tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 100), None, None))

        # Create a mock mouse event
        event = MagicMock(spec=QMouseEvent)
        event.button.return_value = Qt.MouseButton.LeftButton

        # Create a point
        self.point_tool.mouse_press(event, QPointF(100, 100))

        # Check that tool state is still IDLE (ready for next creation)
        self.assertEqual(self.point_tool.state, ToolState.IDLE)


if __name__ == '__main__':
    unittest.main()
