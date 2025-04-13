"""Point geometric object for the Sacred Geometry Explorer.

This module contains the Point class that represents a point in 2D space.
"""

from typing import Dict, Any
import math
from PyQt6.QtCore import QPointF, QRectF

from geometry.ui.sacred_geometry.model.base import GeometricObject
from geometry.ui.sacred_geometry.model.enums import ObjectType
from geometry.ui.sacred_geometry.model.style import Style


class Point(GeometricObject):
    """A point in 2D space."""

    object_type = ObjectType.POINT

    def __init__(self, x: float = 0, y: float = 0, name: str = None, style: Style = None) -> None:
        """Initialize a point.

        Args:
            x: X coordinate
            y: Y coordinate
            name: Optional name for the point
            style: Optional style for the point
        """
        super().__init__(name, style)
        self.x = x
        self.y = y

    def to_dict(self) -> Dict[str, Any]:
        """Convert the point to a dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "x": self.x,
            "y": self.y
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Point':
        """Create a point from a dictionary."""
        point = cls(
            x=data.get("x", 0),
            y=data.get("y", 0),
            name=data.get("name")
        )

        # Load base class properties
        point.id = data.get("id", point.id)
        point.visible = data.get("visible", True)
        point.locked = data.get("locked", False)

        if "style" in data:
            point.style = Style.from_dict(data["style"])

        point.tags = set(data.get("tags", []))
        point.dependencies = set(data.get("dependencies", []))
        point.dependents = set(data.get("dependents", []))
        point.metadata = data.get("metadata", {}).copy()

        return point

    def get_bounds(self) -> QRectF:
        """Get the bounding rectangle of the point."""
        half_size = self.style.point_size / 2
        return QRectF(self.x - half_size, self.y - half_size, self.style.point_size, self.style.point_size)

    def contains_point(self, point: QPointF, tolerance: float = 5.0) -> bool:
        """Check if the point contains or is near the given point."""
        dx = self.x - point.x()
        dy = self.y - point.y()
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= max(tolerance, self.style.point_size / 2)

    def move_by(self, dx: float, dy: float) -> None:
        """Move the point by the given delta."""
        self.x += dx
        self.y += dy

        # Notify dependents (like lines) that this point has moved
        # This is handled by the canvas when the point is moved through the UI

    def rotate(self, angle: float, center: QPointF = None) -> None:
        """Rotate the point by the given angle around the given center."""
        if center is None:
            # No rotation around self
            return

        # Convert angle to radians
        angle_rad = math.radians(angle)

        # Translate to origin
        x = self.x - center.x()
        y = self.y - center.y()

        # Rotate
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a

        # Translate back
        self.x = new_x + center.x()
        self.y = new_y + center.y()

    def scale(self, sx: float, sy: float, center: QPointF = None) -> None:
        """Scale the point by the given factors around the given center."""
        if center is None:
            # Scale around origin
            self.x *= sx
            self.y *= sy
        else:
            # Scale around center
            self.x = center.x() + (self.x - center.x()) * sx
            self.y = center.y() + (self.y - center.y()) * sy

    def distance_to(self, point: QPointF) -> float:
        """Calculate the distance from the point to the given point."""
        dx = self.x - point.x()
        dy = self.y - point.y()
        return math.sqrt(dx * dx + dy * dy)

    def to_qpointf(self) -> QPointF:
        """Convert to QPointF."""
        return QPointF(self.x, self.y)