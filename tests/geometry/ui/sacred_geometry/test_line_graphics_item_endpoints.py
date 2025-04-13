"""Tests for the LineGraphicsItem endpoint manipulation."""

import pytest
from PyQt6.QtCore import QPointF

from geometry.ui.sacred_geometry.model import Line, LineType
from geometry.ui.sacred_geometry.graphics_items import LineGraphicsItem


class TestLineGraphicsItemEndpoints:
    """Tests for the LineGraphicsItem endpoint manipulation."""

    def test_move_handle_updates_endpoints(self):
        """Test that moving handles updates the line endpoints."""
        # Create a line
        line = Line(1, 2, 3, 4, name="Test Line", line_type=LineType.SEGMENT)
        
        # Create a line graphics item
        item = LineGraphicsItem(line)
        
        # Move the first handle (TOP_LEFT)
        item.move_handle(item.HANDLE_TOP_LEFT, QPointF(5, 6))
        
        # Check that the line has been updated
        p1 = line.get_endpoint(1)
        p2 = line.get_endpoint(2)
        assert p1 == (5, 6)
        assert p2 == (3, 4)
        
        # Move the second handle (BOTTOM_RIGHT)
        item.move_handle(item.HANDLE_BOTTOM_RIGHT, QPointF(7, 8))
        
        # Check that the line has been updated
        p1 = line.get_endpoint(1)
        p2 = line.get_endpoint(2)
        assert p1 == (5, 6)
        assert p2 == (7, 8)
