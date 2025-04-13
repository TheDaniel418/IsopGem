"""Tests for the Line class in the model module."""

import math
import pytest
from PyQt6.QtCore import QPointF

from geometry.ui.sacred_geometry.model import Line, LineType


class TestLine:
    """Tests for the Line class."""

    def test_init(self):
        """Test initializing a line."""
        # Test default initialization
        line = Line()
        assert line.x1 == 0
        assert line.y1 == 0
        assert line.x2 == 1
        assert line.y2 == 0
        assert line.line_type == LineType.SEGMENT

        # Test initialization with coordinates
        line = Line(1, 2, 3, 4)
        assert line.x1 == 1
        assert line.y1 == 2
        assert line.x2 == 3
        assert line.y2 == 4
        assert line.line_type == LineType.SEGMENT

        # Test initialization with line type
        line = Line(1, 2, 3, 4, line_type=LineType.RAY)
        assert line.x1 == 1
        assert line.y1 == 2
        assert line.x2 == 3
        assert line.y2 == 4
        assert line.line_type == LineType.RAY

    def test_to_dict(self):
        """Test converting a line to a dictionary."""
        line = Line(1, 2, 3, 4, name="Test Line", line_type=LineType.RAY)
        data = line.to_dict()
        assert data["x1"] == 1
        assert data["y1"] == 2
        assert data["x2"] == 3
        assert data["y2"] == 4
        assert data["name"] == "Test Line"
        assert data["line_type"] == "RAY"

    def test_from_dict(self):
        """Test creating a line from a dictionary."""
        data = {
            "x1": 1,
            "y1": 2,
            "x2": 3,
            "y2": 4,
            "name": "Test Line",
            "line_type": "RAY"
        }
        line = Line.from_dict(data)
        assert line.x1 == 1
        assert line.y1 == 2
        assert line.x2 == 3
        assert line.y2 == 4
        assert line.name == "Test Line"
        assert line.line_type == LineType.RAY

        # Test with legacy format (p1/p2)
        data = {
            "p1": {"x": 1, "y": 2},
            "p2": {"x": 3, "y": 4},
            "name": "Test Line",
            "line_type": "RAY"
        }
        line = Line.from_dict(data)
        assert line.x1 == 1
        assert line.y1 == 2
        assert line.x2 == 3
        assert line.y2 == 4
        assert line.name == "Test Line"
        assert line.line_type == LineType.RAY

    def test_get_bounds(self):
        """Test getting the bounding rectangle of a line."""
        # Test segment
        line = Line(1, 2, 3, 4, line_type=LineType.SEGMENT)
        bounds = line.get_bounds()
        assert bounds.left() == pytest.approx(1 - line.style.stroke_width / 2)
        assert bounds.top() == pytest.approx(2 - line.style.stroke_width / 2)
        assert bounds.right() == pytest.approx(3 + line.style.stroke_width / 2)
        assert bounds.bottom() == pytest.approx(4 + line.style.stroke_width / 2)

    def test_contains_point(self):
        """Test checking if a line contains a point."""
        line = Line(1, 2, 5, 6, line_type=LineType.SEGMENT)
        # Point on the line
        assert line.contains_point(QPointF(3, 4), tolerance=0.1)
        # Point not on the line
        assert not line.contains_point(QPointF(3, 5), tolerance=0.1)

    def test_move_by(self):
        """Test moving a line."""
        line = Line(1, 2, 3, 4)
        line.move_by(10, 20)
        assert line.x1 == 11
        assert line.y1 == 22
        assert line.x2 == 13
        assert line.y2 == 24

    def test_rotate(self):
        """Test rotating a line."""
        line = Line(1, 0, 3, 0)  # Horizontal line
        # Rotate 90 degrees around origin
        line.rotate(90, QPointF(0, 0))
        assert line.x1 == pytest.approx(0)
        assert line.y1 == pytest.approx(1)
        assert line.x2 == pytest.approx(0)
        assert line.y2 == pytest.approx(3)

    def test_scale(self):
        """Test scaling a line."""
        line = Line(1, 2, 3, 4)
        # Scale by 2 around origin
        line.scale(2, 2, QPointF(0, 0))
        assert line.x1 == 2
        assert line.y1 == 4
        assert line.x2 == 6
        assert line.y2 == 8

    def test_distance_to(self):
        """Test calculating the distance from a line to a point."""
        # Segment
        line = Line(0, 0, 4, 0, line_type=LineType.SEGMENT)
        # Point above the line
        assert line.distance_to(QPointF(2, 3)) == 3
        # Point beyond the line
        assert line.distance_to(QPointF(6, 0)) == 2

        # Ray
        line = Line(0, 0, 4, 0, line_type=LineType.RAY)
        # Point beyond the ray
        assert line.distance_to(QPointF(6, 0)) == 0

        # Infinite line
        line = Line(0, 0, 4, 0, line_type=LineType.INFINITE)
        # Point beyond the line
        assert line.distance_to(QPointF(-2, 0)) == 0

    def test_intersect_line(self):
        """Test calculating intersection points with another line."""
        # Two segments that intersect
        line1 = Line(0, 0, 4, 4, line_type=LineType.SEGMENT)
        line2 = Line(0, 4, 4, 0, line_type=LineType.SEGMENT)
        intersections = line1.intersect(line2)
        assert len(intersections) == 1
        assert intersections[0].x() == pytest.approx(2)
        assert intersections[0].y() == pytest.approx(2)

        # Two segments that don't intersect
        line1 = Line(0, 0, 1, 1, line_type=LineType.SEGMENT)
        line2 = Line(3, 3, 4, 4, line_type=LineType.SEGMENT)
        intersections = line1.intersect(line2)
        assert len(intersections) == 0

        # Segment and ray that intersect
        line1 = Line(0, 0, 4, 4, line_type=LineType.SEGMENT)
        line2 = Line(0, 4, 4, 0, line_type=LineType.RAY)
        intersections = line1.intersect(line2)
        assert len(intersections) == 1
        assert intersections[0].x() == pytest.approx(2)
        assert intersections[0].y() == pytest.approx(2)

        # Parallel lines
        line1 = Line(0, 0, 4, 0, line_type=LineType.SEGMENT)
        line2 = Line(0, 1, 4, 1, line_type=LineType.SEGMENT)
        intersections = line1.intersect(line2)
        assert len(intersections) == 0
