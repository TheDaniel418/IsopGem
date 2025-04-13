"""Tests for the Compass Tool."""

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

from geometry.ui.sacred_geometry.model import Point, Circle, Style
from geometry.ui.sacred_geometry.tools import CompassTool


class TestCompassTool(unittest.TestCase):
    """Tests for the CompassTool class."""

    def setUp(self):
        """Set up the test."""
        self.tool = CompassTool()
        self.tool.explorer = MagicMock()
        self.tool.canvas = MagicMock()
        self.tool.canvas.scene = MagicMock()
        self.tool._init_tool()

    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.tool.name, "Compass")
        self.assertEqual(self.tool.icon_name, "compass")
        self.assertEqual(self.tool.state, self.tool.STATE_SELECTING_RADIUS)
        self.assertIsNone(self.tool.data.get('radius'))
        self.assertEqual(self.tool.data.get('radius_points', []), [])

    def test_radius_selection(self):
        """Test radius selection."""
        # Mock the _snap_position_with_info method to return fixed positions
        self.tool._snap_position_with_info = MagicMock(side_effect=[
            (QPointF(0, 0), 'grid', None),
            (QPointF(30, 40), 'grid', None)
        ])

        # Mock the _create_object method to return mock points
        mock_point1 = MagicMock(spec=Point)
        mock_point1.x = 0
        mock_point1.y = 0
        
        mock_point2 = MagicMock(spec=Point)
        mock_point2.x = 30
        mock_point2.y = 40
        
        self.tool._create_object = MagicMock(side_effect=[mock_point1, mock_point2])

        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton

        # First click - select first point
        self.tool.mouse_press(event, QPointF(0, 0))
        self.assertEqual(len(self.tool.data['radius_points']), 1)
        self.assertEqual(self.tool.state, self.tool.STATE_SELECTING_RADIUS)
        
        # Second click - select second point and calculate radius
        self.tool.mouse_press(event, QPointF(30, 40))
        self.assertEqual(len(self.tool.data['radius_points']), 2)
        self.assertEqual(self.tool.state, self.tool.STATE_DRAWING_CIRCLES)
        
        # Check that radius was calculated correctly (should be 50)
        self.assertAlmostEqual(self.tool.data['radius'], 50.0)

    def test_circle_creation(self):
        """Test circle creation."""
        # Set up the tool with a predefined radius
        self.tool.state = self.tool.STATE_DRAWING_CIRCLES
        self.tool.data['radius'] = 50.0
        
        # Mock the _snap_position_with_info method to return a fixed position
        self.tool._snap_position_with_info = MagicMock(return_value=(QPointF(100, 100), 'grid', None))
        
        # Mock the _create_object method
        self.tool._create_object = MagicMock()
        
        # Create a mock mouse event
        event = MagicMock()
        event.button.return_value = Qt.MouseButton.LeftButton
        
        # Click to create a circle
        self.tool.mouse_press(event, QPointF(100, 100))
        
        # Check that _create_object was called with the correct parameters
        self.tool._create_object.assert_called_once()
        args, kwargs = self.tool._create_object.call_args
        self.assertEqual(kwargs['cx'], 100)
        self.assertEqual(kwargs['cy'], 100)
        self.assertEqual(kwargs['radius'], 50.0)

    def test_preview_radius_line(self):
        """Test preview of radius line."""
        # Set up the tool with one point selected
        mock_point = MagicMock(spec=Point)
        mock_point.x = 0
        mock_point.y = 0
        self.tool.data['radius_points'] = [mock_point]
        
        # Call preview method
        self.tool._preview_radius_line(QPointF(30, 40))
        
        # Check that addLine was called with the correct parameters
        self.tool.canvas.scene.addLine.assert_called_once()
        args, kwargs = self.tool.canvas.scene.addLine.call_args
        line = args[0]
        self.assertEqual(line.x1(), 0)
        self.assertEqual(line.y1(), 0)
        self.assertEqual(line.x2(), 30)
        self.assertEqual(line.y2(), 40)
        
        # Check that addSimpleText was called to display the distance
        self.tool.canvas.scene.addSimpleText.assert_called_once()
        args, kwargs = self.tool.canvas.scene.addSimpleText.call_args
        self.assertEqual(args[0], "50.00")  # Distance should be 50

    def test_preview_circle(self):
        """Test preview of circle."""
        # Set up the tool with a predefined radius
        self.tool.data['radius'] = 50.0
        
        # Call preview method
        self.tool._preview_circle(QPointF(100, 100))
        
        # Check that addEllipse was called with the correct parameters
        self.tool.canvas.scene.addEllipse.assert_called_once()
        args, kwargs = self.tool.canvas.scene.addEllipse.call_args
        self.assertEqual(args[0], 50)  # x - radius
        self.assertEqual(args[1], 50)  # y - radius
        self.assertEqual(args[2], 100)  # width (2 * radius)
        self.assertEqual(args[3], 100)  # height (2 * radius)

    def test_key_press_escape(self):
        """Test handling of escape key press."""
        # Set up the tool in drawing circles state
        self.tool.state = self.tool.STATE_DRAWING_CIRCLES
        self.tool.data['radius'] = 50.0
        self.tool.data['radius_points'] = [MagicMock(), MagicMock()]
        
        # Create a mock key event for Escape
        event = MagicMock()
        event.key.return_value = Qt.Key.Key_Escape
        
        # Call key_press method
        self.tool.key_press(event)
        
        # Check that state was reset to selecting radius
        self.assertEqual(self.tool.state, self.tool.STATE_SELECTING_RADIUS)
        self.assertEqual(self.tool.data['radius_points'], [])
        self.assertIsNone(self.tool.data['radius'])


if __name__ == '__main__':
    unittest.main()
