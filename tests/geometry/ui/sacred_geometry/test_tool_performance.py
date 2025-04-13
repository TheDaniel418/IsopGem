"""Tests for tool performance."""

import unittest
import time
import sys
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication

# Create QApplication instance for the tests
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from geometry.ui.sacred_geometry.model import Point, Line, Circle, Style
from geometry.ui.sacred_geometry.tools import PointTool, LineTool, CircleTool, SelectionTool, ToolState, ToolOptions
from geometry.ui.sacred_geometry.explorer import SacredGeometryExplorer


class TestToolPerformance(unittest.TestCase):
    """Tests for tool performance."""

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

    @patch('geometry.ui.sacred_geometry.tools.PointTool._create_object')
    def test_point_creation_performance(self, mock_create_object):
        """Test performance of creating many points."""
        # Mock the _snap_position_with_info method to return fixed positions
        self.point_tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Create many points and measure time
        num_points = 100
        start_time = time.time()

        for i in range(num_points):
            self.point_tool.mouse_press(event, QPointF(i, i))

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Check that all points were created
        self.assertEqual(mock_create_object.call_count, num_points)

        # Check that creation time is reasonable (less than 1ms per point on average)
        self.assertLess(elapsed_time / num_points, 0.001)

    @patch('geometry.ui.sacred_geometry.tools.LineTool._create_object')
    def test_line_creation_performance(self, mock_create_object):
        """Test performance of creating many lines."""
        # Mock the _snap_position_with_info method to return fixed positions
        self.line_tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Create many lines and measure time
        num_lines = 50
        start_time = time.time()

        for i in range(num_lines):
            # First click - set start point
            self.line_tool.mouse_press(event, QPointF(i, i))

            # Second click - create line
            self.line_tool.mouse_press(event, QPointF(i + 10, i + 10))

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Check that all lines were created
        self.assertEqual(mock_create_object.call_count, num_lines)

        # Check that creation time is reasonable (less than 2ms per line on average)
        self.assertLess(elapsed_time / num_lines, 0.002)

    @patch('geometry.ui.sacred_geometry.tools.CircleTool._create_object')
    def test_circle_creation_performance(self, mock_create_object):
        """Test performance of creating many circles."""
        # Mock the _snap_position_with_info method to return fixed positions
        self.circle_tool._snap_position_with_info = MagicMock(return_value=(QPointF(0, 0), None, None))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Create many circles and measure time
        num_circles = 50
        start_time = time.time()

        for i in range(num_circles):
            # First click - set center point
            self.circle_tool.mouse_press(event, QPointF(i * 10, i * 10))

            # Second click - create circle
            self.circle_tool.mouse_press(event, QPointF(i * 10 + 5, i * 10 + 5))

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Check that all circles were created
        self.assertEqual(mock_create_object.call_count, num_circles)

        # Check that creation time is reasonable (less than 2ms per circle on average)
        self.assertLess(elapsed_time / num_circles, 0.002)

    @patch('geometry.ui.sacred_geometry.tools.SelectionTool._move_object')
    def test_selection_performance_with_many_objects(self, mock_move_object):
        """Test selection performance with many objects."""
        # Create many mock objects
        num_objects = 100
        objects = []

        for i in range(num_objects):
            obj = MagicMock()
            obj.x = i * 10
            obj.y = i * 10
            obj.id = f"object{i}"
            obj.locked = False
            objects.append(obj)

        # Mock the canvas.find_object_at method to return different objects
        self.explorer.canvas.find_object_at = MagicMock(side_effect=objects)

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Select each object and measure time
        start_time = time.time()

        for i in range(num_objects):
            self.selection_tool.mouse_press(event, QPointF(i * 10, i * 10))

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Check that all objects were selected
        self.assertEqual(self.explorer.canvas.select_object.call_count, num_objects)

        # Check that selection time is reasonable (less than 1ms per object on average)
        self.assertLess(elapsed_time / num_objects, 0.001)

    @patch('geometry.ui.sacred_geometry.tools.PointTool._snap_to_objects')
    def test_snap_to_objects_performance(self, mock_snap_to_objects):
        """Test performance of snapping to objects with many objects."""
        # Mock the _snap_to_objects method to return a fixed position and object
        mock_obj = MagicMock()
        mock_snap_to_objects.return_value = (QPointF(0, 0), mock_obj)

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Snap to objects many times and measure time
        num_snaps = 100
        start_time = time.time()

        for i in range(num_snaps):
            self.point_tool._snap_position_with_info(QPointF(i, i))

        end_time = time.time()
        elapsed_time = end_time - start_time

        # Check that snap was called for each position
        self.assertEqual(mock_snap_to_objects.call_count, num_snaps)

        # Check that snap time is reasonable (less than 1ms per snap on average)
        self.assertLess(elapsed_time / num_snaps, 0.001)


if __name__ == '__main__':
    unittest.main()
