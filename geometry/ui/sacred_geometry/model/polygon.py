"""Polygon geometric object for the Sacred Geometry Explorer.

This module contains the Polygon class that represents a polygon in 2D space.
"""

import math
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt6.QtGui import QPolygonF

from geometry.ui.sacred_geometry.model.base import GeometricObject
from geometry.ui.sacred_geometry.model.enums import ObjectType
from geometry.ui.sacred_geometry.model.point import Point
from geometry.ui.sacred_geometry.model.style import Style


class Polygon(GeometricObject):
    """A polygon defined by a list of vertices."""

    object_type = ObjectType.POLYGON

    def __init__(
        self, vertices: List[Point] = None, name: str = None, style: Style = None
    ) -> None:
        """Initialize a polygon.

        Args:
            vertices: List of vertices
            name: Optional name for the polygon
            style: Optional style for the polygon
        """
        super().__init__(name, style)
        self.vertices = vertices or []

        # Add dependencies
        for vertex in self.vertices:
            if hasattr(vertex, "id"):
                self.dependencies.add(vertex.id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the polygon to a dictionary for serialization."""
        data = super().to_dict()
        data.update(
            {
                "vertices": [
                    v.to_dict() if hasattr(v, "to_dict") else None
                    for v in self.vertices
                ]
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Polygon":
        """Create a polygon from a dictionary."""
        vertices = []
        if "vertices" in data:
            for v_data in data["vertices"]:
                if v_data:
                    vertices.append(Point.from_dict(v_data))

        polygon = cls(vertices=vertices, name=data.get("name"))

        # Load base class properties
        polygon.id = data.get("id", polygon.id)
        polygon.visible = data.get("visible", True)
        polygon.locked = data.get("locked", False)

        if "style" in data:
            polygon.style = Style.from_dict(data["style"])

        polygon.tags = set(data.get("tags", []))
        polygon.dependencies = set(data.get("dependencies", []))
        polygon.dependents = set(data.get("dependents", []))
        polygon.metadata = data.get("metadata", {}).copy()

        return polygon

    def get_bounds(self) -> QRectF:
        """Get the bounding rectangle of the polygon."""
        if not self.vertices:
            return QRectF()

        # Find min/max coordinates
        min_x = min(v.x for v in self.vertices)
        min_y = min(v.y for v in self.vertices)
        max_x = max(v.x for v in self.vertices)
        max_y = max(v.y for v in self.vertices)

        # Add padding for stroke width
        padding = self.style.stroke_width / 2

        return QRectF(
            min_x - padding,
            min_y - padding,
            max_x - min_x + padding * 2,
            max_y - min_y + padding * 2,
        )

    def contains_point(self, point: QPointF, tolerance: float = 5.0) -> bool:
        """Check if the polygon contains or is near the given point."""
        if not self.vertices or len(self.vertices) < 3:
            return False

        # Create a QPolygonF for containment test
        poly = QPolygonF([QPointF(v.x, v.y) for v in self.vertices])

        # Check if point is inside polygon
        if poly.containsPoint(point, Qt.FillRule.OddEvenFill):
            return True

        # Check if point is near any edge
        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % len(self.vertices)]

            # Create a line for the edge
            line = QLineF(v1.x, v1.y, v2.x, v2.y)

            # Calculate distance from point to line
            normal = line.normalVector()
            normal.setLength(1.0)

            # Create a line from the point perpendicular to the edge
            perp_line = QLineF(
                point, QPointF(point.x() + normal.dx(), point.y() + normal.dy())
            )

            # Find intersection point
            intersection_point = QPointF()
            if (
                line.intersects(perp_line, intersection_point)
                == QLineF.IntersectionType.BoundedIntersection
            ):
                # Calculate distance from point to intersection
                dx = point.x() - intersection_point.x()
                dy = point.y() - intersection_point.y()
                distance = math.sqrt(dx * dx + dy * dy)

                if distance <= tolerance:
                    return True

        return False

    def move_by(self, dx: float, dy: float) -> None:
        """Move the polygon by the given delta."""
        for vertex in self.vertices:
            vertex.move_by(dx, dy)

    def rotate(self, angle: float, center: QPointF = None) -> None:
        """Rotate the polygon by the given angle around the given center."""
        if center is None:
            # Calculate centroid as rotation center
            if not self.vertices:
                return

            cx = sum(v.x for v in self.vertices) / len(self.vertices)
            cy = sum(v.y for v in self.vertices) / len(self.vertices)
            center = QPointF(cx, cy)

        # Rotate each vertex
        for vertex in self.vertices:
            vertex.rotate(angle, center)

    def scale(self, sx: float, sy: float, center: QPointF = None) -> None:
        """Scale the polygon by the given factors around the given center."""
        if center is None:
            # Calculate centroid as scaling center
            if not self.vertices:
                return

            cx = sum(v.x for v in self.vertices) / len(self.vertices)
            cy = sum(v.y for v in self.vertices) / len(self.vertices)
            center = QPointF(cx, cy)

        # Scale each vertex
        for vertex in self.vertices:
            vertex.scale(sx, sy, center)

    def distance_to(self, point: QPointF) -> float:
        """Calculate the distance from the polygon to the given point."""
        if not self.vertices or len(self.vertices) < 3:
            return float("inf")

        # Create a QPolygonF for containment test
        poly = QPolygonF([QPointF(v.x, v.y) for v in self.vertices])

        # If point is inside polygon, distance is 0
        if poly.containsPoint(point, Qt.FillRule.OddEvenFill):
            return 0.0

        # Find minimum distance to any edge
        min_distance = float("inf")
        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % len(self.vertices)]

            # Create a line for the edge
            line = QLineF(v1.x, v1.y, v2.x, v2.y)

            # Calculate distance from point to line segment
            line_length_sq = line.length() ** 2
            if line_length_sq < 1e-10:
                # Edge is a point, calculate distance to that point
                dx = point.x() - v1.x
                dy = point.y() - v1.y
                distance = math.sqrt(dx * dx + dy * dy)
            else:
                # Calculate projection of point onto line
                t = (
                    (point.x() - v1.x) * (v2.x - v1.x)
                    + (point.y() - v1.y) * (v2.y - v1.y)
                ) / line_length_sq

                # Clamp t to [0, 1] for line segment
                t = max(0, min(1, t))

                # Calculate closest point on line segment
                closest_x = v1.x + t * (v2.x - v1.x)
                closest_y = v1.y + t * (v2.y - v1.y)

                # Calculate distance to closest point
                dx = point.x() - closest_x
                dy = point.y() - closest_y
                distance = math.sqrt(dx * dx + dy * dy)

            min_distance = min(min_distance, distance)

        return min_distance

    def add_vertex(self, vertex: Point, index: Optional[int] = None) -> None:
        """Add a vertex to the polygon.

        Args:
            vertex: Vertex to add
            index: Optional index to insert at (if None, append to end)
        """
        if index is None:
            self.vertices.append(vertex)
        else:
            self.vertices.insert(index, vertex)

        # Add dependency
        if hasattr(vertex, "id"):
            self.dependencies.add(vertex.id)

    def remove_vertex(self, index: int) -> Optional[Point]:
        """Remove a vertex from the polygon.

        Args:
            index: Index of vertex to remove

        Returns:
            Removed vertex or None if index is invalid
        """
        if 0 <= index < len(self.vertices):
            vertex = self.vertices.pop(index)

            # Remove dependency
            if hasattr(vertex, "id"):
                self.dependencies.discard(vertex.id)

            return vertex

        return None

    def get_vertex(self, index: int) -> Optional[Point]:
        """Get a vertex from the polygon.

        Args:
            index: Index of vertex to get

        Returns:
            Vertex or None if index is invalid
        """
        if 0 <= index < len(self.vertices):
            return self.vertices[index]

        return None

    def set_vertex(self, index: int, vertex: Point) -> bool:
        """Set a vertex in the polygon.

        Args:
            index: Index of vertex to set
            vertex: New vertex

        Returns:
            True if successful, False if index is invalid
        """
        if 0 <= index < len(self.vertices):
            # Remove dependency on old vertex
            old_vertex = self.vertices[index]
            if hasattr(old_vertex, "id"):
                self.dependencies.discard(old_vertex.id)

            # Set new vertex
            self.vertices[index] = vertex

            # Add dependency on new vertex
            if hasattr(vertex, "id"):
                self.dependencies.add(vertex.id)

            return True

        return False

    def get_vertex_count(self) -> int:
        """Get the number of vertices in the polygon.

        Returns:
            Number of vertices
        """
        return len(self.vertices)

    def is_regular(self) -> bool:
        """Check if the polygon is regular (all sides equal length and all angles equal).

        Returns:
            True if the polygon is regular, False otherwise
        """
        if len(self.vertices) < 3:
            return False

        # Calculate side lengths
        side_lengths = []
        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % len(self.vertices)]
            dx = v2.x - v1.x
            dy = v2.y - v1.y
            side_lengths.append(math.sqrt(dx * dx + dy * dy))

        # Check if all side lengths are approximately equal
        avg_length = sum(side_lengths) / len(side_lengths)
        for length in side_lengths:
            if abs(length - avg_length) > 1e-6:
                return False

        # For a regular polygon, all vertices must lie on a circle
        # Calculate centroid
        cx = sum(v.x for v in self.vertices) / len(self.vertices)
        cy = sum(v.y for v in self.vertices) / len(self.vertices)

        # Calculate distances from centroid to vertices
        distances = []
        for v in self.vertices:
            dx = v.x - cx
            dy = v.y - cy
            distances.append(math.sqrt(dx * dx + dy * dy))

        # Check if all distances are approximately equal
        avg_distance = sum(distances) / len(distances)
        for distance in distances:
            if abs(distance - avg_distance) > 1e-6:
                return False

        return True

    def get_area(self) -> float:
        """Calculate the area of the polygon.

        Returns:
            Area of the polygon
        """
        if len(self.vertices) < 3:
            return 0.0

        # Calculate area using the shoelace formula
        area = 0.0
        for i in range(len(self.vertices)):
            j = (i + 1) % len(self.vertices)
            area += self.vertices[i].x * self.vertices[j].y
            area -= self.vertices[j].x * self.vertices[i].y

        return abs(area) / 2.0

    def get_perimeter(self) -> float:
        """Calculate the perimeter of the polygon.

        Returns:
            Perimeter of the polygon
        """
        if len(self.vertices) < 2:
            return 0.0

        # Calculate perimeter as sum of side lengths
        perimeter = 0.0
        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % len(self.vertices)]
            dx = v2.x - v1.x
            dy = v2.y - v1.y
            perimeter += math.sqrt(dx * dx + dy * dy)

        return perimeter

    def get_centroid(self) -> Point:
        """Calculate the centroid of the polygon.

        Returns:
            Centroid of the polygon
        """
        if not self.vertices:
            return Point()

        if len(self.vertices) == 1:
            return Point(self.vertices[0].x, self.vertices[0].y)

        if len(self.vertices) == 2:
            return Point(
                (self.vertices[0].x + self.vertices[1].x) / 2,
                (self.vertices[0].y + self.vertices[1].y) / 2,
            )

        # Calculate centroid using weighted average of triangle centroids
        total_area = 0.0
        cx = 0.0
        cy = 0.0

        # Use first vertex as reference point
        x0 = self.vertices[0].x
        y0 = self.vertices[0].y

        for i in range(1, len(self.vertices) - 1):
            # Create a triangle with vertices[0] and two adjacent vertices
            x1 = self.vertices[i].x
            y1 = self.vertices[i].y
            x2 = self.vertices[i + 1].x
            y2 = self.vertices[i + 1].y

            # Calculate triangle area
            area = ((x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)) / 2.0
            total_area += area

            # Calculate triangle centroid
            triangle_cx = (x0 + x1 + x2) / 3.0
            triangle_cy = (y0 + y1 + y2) / 3.0

            # Add weighted contribution to centroid
            cx += area * triangle_cx
            cy += area * triangle_cy

        if abs(total_area) < 1e-10:
            # Degenerate case, use average of vertices
            cx = sum(v.x for v in self.vertices) / len(self.vertices)
            cy = sum(v.y for v in self.vertices) / len(self.vertices)
        else:
            # Normalize by total area
            cx /= total_area
            cy /= total_area

        return Point(cx, cy)
