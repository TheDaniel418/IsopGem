"""Tests for the Parallel Line Tool."""

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
from geometry.ui.sacred_geometry.tools import ParallelLineTool, ToolState, ToolOptions


class TestParallelLineTool(unittest.TestCase):
    """Tests for the ParallelLineTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = ParallelLineTool()
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
        self.assertEqual(self.tool.name, "Parallel Line")
        self.assertEqual(self.tool.icon_name, "parallel_line")
        self.assertEqual(self.tool.state, ToolState.IDLE)
        self.assertEqual(self.tool.line_type, LineType.SEGMENT)
        self.assertTrue(self.tool.show_distance)

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

    def test_calculate_distance_to_line(self):
        """Test calculating the distance from a point to a line."""
        # Create a horizontal line
        line = Line(0, 0, 10, 0)

        # Calculate distance from a point above the line
        point = QPointF(5, 5)
        distance = self.tool._calculate_distance_to_line(point, line)
        self.assertAlmostEqual(distance, 5.0)

        # Create a vertical line
        line = Line(0, 0, 0, 10)

        # Calculate distance from a point to the right of the line
        point = QPointF(5, 5)
        distance = self.tool._calculate_distance_to_line(point, line)
        self.assertAlmostEqual(distance, 5.0)

        # Create a diagonal line
        line = Line(0, 0, 10, 10)

        # Calculate distance from a point
        point = QPointF(0, 10)
        distance = self.tool._calculate_distance_to_line(point, line)
        self.assertAlmostEqual(distance, 7.071, delta=0.001)  # 10/sqrt(2)

    def test_calculate_parallel_line_points(self):
        """Test calculating points for a parallel line."""
        # Create a horizontal line
        line = Line(0, 0, 10, 0)

        # Calculate parallel line through a point above the line
        point = QPointF(5, 5)
        p1, p2 = self.tool._calculate_parallel_line_points(point, line)

        # Check that the line is horizontal (same y-coordinate)
        self.assertAlmostEqual(p1.y(), p2.y())
        self.assertAlmostEqual(p1.y(), 5.0)

        # Check that the line has the same direction as the original
        self.assertGreater(p2.x(), p1.x())

        # Create a vertical line
        line = Line(0, 0, 0, 10)

        # Calculate parallel line through a point to the right of the line
        point = QPointF(5, 5)
        p1, p2 = self.tool._calculate_parallel_line_points(point, line)

        # Check that the line is vertical (same x-coordinate)
        self.assertAlmostEqual(p1.x(), p2.x())
        self.assertAlmostEqual(p1.x(), 5.0)

        # Check that the line has the same direction as the original
        self.assertGreater(p2.y(), p1.y())

    @patch('geometry.ui.sacred_geometry.tools.ParallelLineTool._create_object')
    def test_create_parallel_line(self, mock_create_object):
        """Test creating a parallel line."""
        # Create mock objects
        mock_point = MagicMock()
        mock_point.x = 5
        mock_point.y = 5
        mock_line = MagicMock()
        mock_line.x1 = 0
        mock_line.y1 = 0
        mock_line.x2 = 10
        mock_line.y2 = 0

        # Set up the tool data
        self.tool.data['reference_point'] = mock_point
        self.tool.data['reference_line'] = mock_line

        # Create a mock line object to return
        mock_line_obj = MagicMock()
        mock_line_obj.metadata = {}
        mock_create_object.return_value = mock_line_obj

        # Call the method
        self.tool._create_parallel_line()

        # Check that _create_object was called with correct parameters
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(args[0], 'line')
        self.assertEqual(kwargs['line_type'], LineType.SEGMENT)

        # Check that distance was stored in metadata
        self.assertIn('parallel_distance', mock_line_obj.metadata)
        self.assertAlmostEqual(mock_line_obj.metadata['parallel_distance'], 5.0)

    def test_mouse_press_first_click(self):
        """Test mouse press for the first click (selecting a line)."""
        # Create mock objects
        mock_line = MagicMock(spec=Line)
        mock_line.p1 = Point(0, 0)
        mock_line.p2 = Point(10, 0)

        # Mock the _snap_position_with_info method to return a fixed position and object
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(5, 0), 'object', mock_line))

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Call the method
        self.tool.mouse_press(event, QPointF(5, 0))

        # Check that the reference line was set
        self.assertEqual(self.tool.data['reference_line'], mock_line)
        self.assertEqual(self.tool.state, ToolState.ACTIVE)

    @patch('geometry.ui.sacred_geometry.tools.ParallelLineTool._create_object')
    @patch('geometry.ui.sacred_geometry.tools.ParallelLineTool._create_parallel_line')
    def test_mouse_press_second_click(self, mock_create_parallel_line, mock_create_object):
        """Test mouse press for the second click (selecting a point)."""
        # Set up the tool state
        self.tool.state = ToolState.ACTIVE

        # Create mock objects
        mock_line = MagicMock()
        mock_line.x1 = 0
        mock_line.y1 = 0
        mock_line.x2 = 10
        mock_line.y2 = 0
        self.tool.data['reference_line'] = mock_line

        # Mock the _snap_position_with_info method to return a fixed position
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(5, 5), 'grid', None))

        # Mock the _complete_operation method
        self.tool._complete_operation = MagicMock()

        # Create a mock point object to return
        mock_point = MagicMock()
        mock_create_object.return_value = mock_point

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # Call the method
        self.tool.mouse_press(event, QPointF(5, 5))

        # Check that a point was created
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(args[0], 'point')
        self.assertEqual(kwargs['x'], 5)
        self.assertEqual(kwargs['y'], 5)

        # Check that the reference point was set
        self.assertEqual(self.tool.data['reference_point'], mock_point)

        # Check that _create_parallel_line was called
        mock_create_parallel_line.assert_called_once()

        # Check that _complete_operation was called
        self.tool._complete_operation.assert_called_once()


if __name__ == '__main__':
    unittest.main()
