"""Circle geometric object for the Sacred Geometry Explorer.

This module contains the Circle class that represents a circle in 2D space.
"""

import math
from typing import Any, Dict, List

from PyQt6.QtCore import QPointF, QRectF

from geometry.ui.sacred_geometry.model.base import GeometricObject
from geometry.ui.sacred_geometry.model.enums import ObjectType
from geometry.ui.sacred_geometry.model.point import Point
from geometry.ui.sacred_geometry.model.style import Style


class Circle(GeometricObject):
    """A circle defined by a center point and radius."""

    object_type = ObjectType.CIRCLE

    def __init__(
        self,
        center_x: float = 0,
        center_y: float = 0,
        radius: float = 1,
        name: str = None,
        style: Style = None,
        center: Point = None,
    ) -> None:
        """Initialize a circle.

        Args:
            center_x: X-coordinate of center (if center Point is not provided)
            center_y: Y-coordinate of center (if center Point is not provided)
            radius: Radius
            name: Optional name for the circle
            style: Optional style for the circle
            center: Optional center point (for backward compatibility)
        """
        super().__init__(name, style)

        # For backward compatibility, accept either a Point object or direct coordinates
        if center is not None and isinstance(center, Point):
            self.center_x = center.x
            self.center_y = center.y
            # Add dependency for backward compatibility
            if hasattr(center, "id"):
                self.dependencies.add(center.id)
        else:
            self.center_x = center_x
            self.center_y = center_y

        self.radius = radius

        # Create a property for backward compatibility
        self._center = None

    # Center property for backward compatibility
    @property
    def center(self):
        """Get the center point (for backward compatibility)."""
        if (
            self._center is None
            or self._center.x != self.center_x
            or self._center.y != self.center_y
        ):
            self._center = Point(self.center_x, self.center_y)
        return self._center

    @center.setter
    def center(self, point):
        """Set the center point (for backward compatibility)."""
        if isinstance(point, Point):
            self.center_x = point.x
            self.center_y = point.y
            self._center = point
        elif isinstance(point, QPointF):
            self.center_x = point.x()
            self.center_y = point.y()
            self._center = None
        elif isinstance(point, tuple) and len(point) >= 2:
            self.center_x = point[0]
            self.center_y = point[1]
            self._center = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the circle to a dictionary for serialization."""
        data = super().to_dict()
        data.update(
            {
                "center_x": self.center_x,
                "center_y": self.center_y,
                "radius": self.radius,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Circle":
        """Create a circle from a dictionary."""
        # Handle both new format (center_x, center_y) and old format (center object)
        if "center" in data and data["center"] and isinstance(data["center"], dict):
            # Old format with center point
            center = Point.from_dict(data["center"])
            circle = cls(
                center=center, radius=data.get("radius", 1), name=data.get("name")
            )
        else:
            # New format with direct coordinates
            circle = cls(
                center_x=data.get("center_x", 0),
                center_y=data.get("center_y", 0),
                radius=data.get("radius", 1),
                name=data.get("name"),
            )

        # Load base class properties
        circle.id = data.get("id", circle.id)
        circle.visible = data.get("visible", True)
        circle.locked = data.get("locked", False)

        if "style" in data:
            circle.style = Style.from_dict(data["style"])

        circle.tags = set(data.get("tags", []))
        circle.dependencies = set(data.get("dependencies", []))
        circle.dependents = set(data.get("dependents", []))
        circle.metadata = data.get("metadata", {}).copy()

        return circle

    def get_bounds(self) -> QRectF:
        """Get the bounding rectangle of the circle."""
        # Add padding for stroke width
        padding = self.style.stroke_width / 2
        total_radius = self.radius + padding

        return QRectF(
            self.center_x - total_radius,
            self.center_y - total_radius,
            total_radius * 2,
            total_radius * 2,
        )

    def contains_point(self, point: QPointF, tolerance: float = 5.0) -> bool:
        """Check if the circle contains or is near the given point."""
        # Check if point is near the circumference
        dx = point.x() - self.center_x
        dy = point.y() - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)
        return abs(distance - self.radius) <= tolerance

    def move_by(self, dx: float, dy: float) -> None:
        """Move the circle by the given delta."""
        self.center_x += dx
        self.center_y += dy
        self._center = None  # Invalidate cached center point

    def rotate(self, angle: float, center: QPointF = None) -> None:
        """Rotate the circle by the given angle around the given center."""
        # Only the center needs to be rotated, the circle itself is rotationally invariant
        if center is not None:
            # Convert angle to radians
            angle_rad = math.radians(angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Translate to origin
            dx = self.center_x - center.x()
            dy = self.center_y - center.y()

            # Rotate
            new_dx = dx * cos_a - dy * sin_a
            new_dy = dx * sin_a + dy * cos_a

            # Translate back
            self.center_x = center.x() + new_dx
            self.center_y = center.y() + new_dy
            self._center = None  # Invalidate cached center point

    def scale(self, sx: float, sy: float, center: QPointF = None) -> None:
        """Scale the circle by the given factors around the given center."""
        # Scale the center position
        if center is not None:
            # Translate to origin
            dx = self.center_x - center.x()
            dy = self.center_y - center.y()

            # Scale
            new_dx = dx * sx
            new_dy = dy * sy

            # Translate back
            self.center_x = center.x() + new_dx
            self.center_y = center.y() + new_dy
            self._center = None  # Invalidate cached center point

        # Scale the radius (use average of sx and sy for uniform scaling)
        scale_factor = (abs(sx) + abs(sy)) / 2
        self.radius *= scale_factor

    def distance_to(self, point: QPointF) -> float:
        """Calculate the distance from the circle to the given point."""
        # Calculate distance from center to point
        dx = point.x() - self.center_x
        dy = point.y() - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)

        # Return absolute difference between distance and radius
        return abs(distance - self.radius)

    def intersect(self, other: GeometricObject) -> List[QPointF]:
        """Calculate intersection points with another object."""
        from geometry.ui.sacred_geometry.model.line import Line

        if isinstance(other, Line):
            return self._intersect_line(other)
        elif isinstance(other, Circle):
            return self._intersect_circle(other)
        else:
            return []

    def _intersect_line(self, line: "Line") -> List[QPointF]:
        """Calculate intersection points with a line."""
        # Get line parameters
        x1, y1 = line.x1, line.y1
        x2, y2 = line.x2, line.y2

        # Get circle parameters
        cx, cy = self.center_x, self.center_y
        r = self.radius

        # Calculate line direction vector
        dx = x2 - x1
        dy = y2 - y1

        # Calculate line length squared
        line_length_sq = dx * dx + dy * dy

        # If line is actually a point, return empty list
        if line_length_sq < 1e-10:
            return []

        # Calculate closest point on line to circle center
        t = ((cx - x1) * dx + (cy - y1) * dy) / line_length_sq

        # Calculate closest point coordinates
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # Calculate distance from closest point to circle center
        distance_sq = (closest_x - cx) ** 2 + (closest_y - cy) ** 2

        # Check if line intersects circle
        if distance_sq > r * r:
            return []

        # Calculate distance from closest point to intersection points
        dist_to_intersection = math.sqrt(r * r - distance_sq)

        # Calculate intersection points
        t1 = t - dist_to_intersection / math.sqrt(line_length_sq)
        t2 = t + dist_to_intersection / math.sqrt(line_length_sq)

        result = []

        # Check if first intersection point is within line segment
        if 0 <= t1 <= 1 or line.line_type != line.line_type.SEGMENT:
            x = x1 + t1 * dx
            y = y1 + t1 * dy
            result.append(QPointF(x, y))

        # Check if second intersection point is within line segment
        if (0 <= t2 <= 1 or line.line_type != line.line_type.SEGMENT) and abs(
            t1 - t2
        ) > 1e-10:  # Avoid duplicates
            x = x1 + t2 * dx
            y = y1 + t2 * dy
            result.append(QPointF(x, y))

        return result

    def _intersect_circle(self, other: "Circle") -> List[QPointF]:
        """Calculate intersection points with another circle."""
        # Get circle parameters
        x1, y1 = self.center_x, self.center_y
        r1 = self.radius

        x2, y2 = other.center_x, other.center_y
        r2 = other.radius

        # Calculate distance between centers
        dx = x2 - x1
        dy = y2 - y1
        d = math.sqrt(dx * dx + dy * dy)

        # Check if circles are too far apart or one is inside the other
        if d > r1 + r2 or d < abs(r1 - r2) or d < 1e-10:
            return []

        # Calculate intersection points
        a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
        h = math.sqrt(r1 * r1 - a * a)

        # Calculate midpoint
        x3 = x1 + a * dx / d
        y3 = y1 + a * dy / d

        # Calculate intersection points
        x4 = x3 + h * dy / d
        y4 = y3 - h * dx / d

        x5 = x3 - h * dy / d
        y5 = y3 + h * dx / d

        # Return intersection points
        if abs(x4 - x5) < 1e-10 and abs(y4 - y5) < 1e-10:
            # Circles are tangent, only one intersection point
            return [QPointF(x4, y4)]
        else:
            return [QPointF(x4, y4), QPointF(x5, y5)]
