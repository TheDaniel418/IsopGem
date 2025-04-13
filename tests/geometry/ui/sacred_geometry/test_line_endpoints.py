"""Tests for the Line endpoint manipulation methods."""

import pytest
from PyQt6.QtCore import QPointF

from geometry.ui.sacred_geometry.model import Line, LineType


class TestLineEndpoints:
    """Tests for the Line endpoint manipulation methods."""

    def test_get_endpoint(self):
        """Test getting line endpoints."""
        # Create a line
        line = Line(1, 2, 3, 4, name="Test Line", line_type=LineType.SEGMENT)
        
        # Get endpoints
        p1 = line.get_endpoint(1)
        p2 = line.get_endpoint(2)
        
        # Check endpoints
        assert p1 == (1, 2)
        assert p2 == (3, 4)
        
        # Check invalid endpoint
        p3 = line.get_endpoint(3)
        assert p3 == (0, 0)
        
    def test_move_endpoint(self):
        """Test moving line endpoints."""
        # Create a line
        line = Line(1, 2, 3, 4, name="Test Line", line_type=LineType.SEGMENT)
        
        # Move first endpoint
        line.move_endpoint(1, 5, 6)
        
        # Check endpoints
        p1 = line.get_endpoint(1)
        p2 = line.get_endpoint(2)
        assert p1 == (5, 6)
        assert p2 == (3, 4)
        
        # Move second endpoint
        line.move_endpoint(2, 7, 8)
        
        # Check endpoints
        p1 = line.get_endpoint(1)
        p2 = line.get_endpoint(2)
        assert p1 == (5, 6)
        assert p2 == (7, 8)
        
        # Move invalid endpoint (should do nothing)
        line.move_endpoint(3, 9, 10)
        
        # Check endpoints
        p1 = line.get_endpoint(1)
        p2 = line.get_endpoint(2)
        assert p1 == (5, 6)
        assert p2 == (7, 8)
