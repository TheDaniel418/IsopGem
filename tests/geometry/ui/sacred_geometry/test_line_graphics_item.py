"""Tests for the LineGraphicsItem class."""

import pytest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor

from geometry.ui.sacred_geometry.model import Line, LineType, Style
from geometry.ui.sacred_geometry.graphics_items import LineGraphicsItem


class TestLineGraphicsItem:
    """Tests for the LineGraphicsItem class."""

    def test_init(self):
        """Test initializing a line graphics item."""
        # Create a line
        line = Line(1, 2, 3, 4, name="Test Line", line_type=LineType.SEGMENT)
        # Create a line graphics item
        item = LineGraphicsItem(line)
        # Check that the item has the correct line
        assert item.line == line

    def test_update_from_object(self):
        """Test updating the item from the object."""
        # Create a line
        line = Line(1, 2, 3, 4, name="Test Line", line_type=LineType.SEGMENT)
        # Create a line graphics item
        item = LineGraphicsItem(line)
        # Modify the line
        line.x1 = 5
        line.y1 = 6
        line.x2 = 7
        line.y2 = 8
        # Update the item
        item.update_from_object()
        # Check that the item has been updated
        assert item.line.x1 == 5
        assert item.line.y1 == 6
        assert item.line.x2 == 7
        assert item.line.y2 == 8

    def test_update_object_from_item(self):
        """Test updating the object from the item."""
        # Create a line
        line = Line(1, 2, 3, 4, name="Test Line", line_type=LineType.SEGMENT)
        # Create a line graphics item
        item = LineGraphicsItem(line)
        # Move the item
        item.setPos(10, 20)
        # Update the object
        item.update_object_from_item()
        # Check that the line has been updated
        assert line.x1 == 11
        assert line.y1 == 22
        assert line.x2 == 13
        assert line.y2 == 24

    def test_handle_rect(self):
        """Test getting the handle rectangle."""
        # Create a line
        line = Line(1, 2, 3, 4, name="Test Line", line_type=LineType.SEGMENT)
        # Create a line graphics item
        item = LineGraphicsItem(line)
        # Get the handle rectangles
        rect1 = item.handle_rect(item.HANDLE_TOP_LEFT)
        rect2 = item.handle_rect(item.HANDLE_BOTTOM_RIGHT)
        # Check that the rectangles are correct
        assert rect1.center() == QPointF(1, 2)
        assert rect2.center() == QPointF(3, 4)

    def test_move_handle(self):
        """Test moving a handle."""
        # Create a line
        line = Line(1, 2, 3, 4, name="Test Line", line_type=LineType.SEGMENT)
        # Create a line graphics item
        item = LineGraphicsItem(line)
        # Move the first handle
        item.move_handle(item.HANDLE_TOP_LEFT, QPointF(5, 6))
        # Check that the line has been updated
        assert line.x1 == 5
        assert line.y1 == 6
        assert line.x2 == 3
        assert line.y2 == 4
        # Move the second handle
        item.move_handle(item.HANDLE_BOTTOM_RIGHT, QPointF(7, 8))
        # Check that the line has been updated
        assert line.x1 == 5
        assert line.y1 == 6
        assert line.x2 == 7
        assert line.y2 == 8
