"""Text geometric object for the Sacred Geometry Explorer.

This module contains the Text class that represents text in 2D space.
"""

import math
from typing import Any, Dict

from PyQt6.QtCore import QPointF, QRectF

from geometry.ui.sacred_geometry.model.base import GeometricObject
from geometry.ui.sacred_geometry.model.enums import ObjectType
from geometry.ui.sacred_geometry.model.point import Point
from geometry.ui.sacred_geometry.model.style import Style


class Text(GeometricObject):
    """Text at a specific position."""

    object_type = ObjectType.TEXT

    def __init__(
        self,
        position: Point = None,
        content: str = "",
        name: str = None,
        style: Style = None,
    ) -> None:
        """Initialize text.

        Args:
            position: Position of the text
            content: Text content
            name: Optional name for the text
            style: Optional style for the text
        """
        super().__init__(name, style)
        self.position = position or Point()
        self.content = content
        self.rotation = 0.0  # Rotation angle in degrees

        # Add dependencies
        if position and hasattr(position, "id"):
            self.dependencies.add(position.id)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the text to a dictionary for serialization."""
        data = super().to_dict()
        data.update(
            {
                "position": self.position.to_dict()
                if hasattr(self.position, "to_dict")
                else None,
                "content": self.content,
                "rotation": self.rotation,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Text":
        """Create text from a dictionary."""
        position = (
            Point.from_dict(data["position"])
            if "position" in data and data["position"]
            else Point()
        )

        text = cls(
            position=position, content=data.get("content", ""), name=data.get("name")
        )

        # Set rotation
        text.rotation = data.get("rotation", 0.0)

        # Load base class properties
        text.id = data.get("id", text.id)
        text.visible = data.get("visible", True)
        text.locked = data.get("locked", False)

        if "style" in data:
            text.style = Style.from_dict(data["style"])

        text.tags = set(data.get("tags", []))
        text.dependencies = set(data.get("dependencies", []))
        text.dependents = set(data.get("dependents", []))
        text.metadata = data.get("metadata", {}).copy()

        return text

    def get_bounds(self) -> QRectF:
        """Get the bounding rectangle of the text.

        Note: This is an approximation since the actual bounds depend on the font metrics.
        """
        # Approximate text size based on content length and font size
        char_width = self.style.font_size * 0.6  # Approximate character width
        text_width = len(self.content) * char_width
        text_height = self.style.font_size * 1.2  # Approximate line height

        # Add padding
        padding = 2.0

        # Create bounds rectangle centered at position
        return QRectF(
            self.position.x - text_width / 2 - padding,
            self.position.y - text_height / 2 - padding,
            text_width + padding * 2,
            text_height + padding * 2,
        )

    def contains_point(self, point: QPointF, tolerance: float = 5.0) -> bool:
        """Check if the text contains or is near the given point."""
        # Get bounds
        bounds = self.get_bounds()

        # Expand bounds by tolerance
        bounds.adjust(-tolerance, -tolerance, tolerance, tolerance)

        # Check if point is inside expanded bounds
        return bounds.contains(point)

    def move_by(self, dx: float, dy: float) -> None:
        """Move the text by the given delta."""
        self.position.move_by(dx, dy)

    def rotate(self, angle: float, center: QPointF = None) -> None:
        """Rotate the text by the given angle around the given center."""
        # Update rotation angle
        self.rotation = (self.rotation + angle) % 360

        # If center is not at text position, also move the position
        if center is not None and (
            center.x() != self.position.x or center.y() != self.position.y
        ):
            self.position.rotate(angle, center)

    def scale(self, sx: float, sy: float, center: QPointF = None) -> None:
        """Scale the text by the given factors around the given center."""
        # Scale the position
        if center is not None:
            self.position.scale(sx, sy, center)

        # Note: We don't scale the font size here, as that would be handled by the style

    def distance_to(self, point: QPointF) -> float:
        """Calculate the distance from the text to the given point."""
        # Get bounds
        bounds = self.get_bounds()

        # If point is inside bounds, distance is 0
        if bounds.contains(point):
            return 0.0

        # Calculate distance to nearest edge of bounds
        dx = max(bounds.left() - point.x(), 0, point.x() - bounds.right())
        dy = max(bounds.top() - point.y(), 0, point.y() - bounds.bottom())
        return math.sqrt(dx * dx + dy * dy)

    def set_content(self, content: str) -> None:
        """Set the text content.

        Args:
            content: New text content
        """
        self.content = content

    def get_content(self) -> str:
        """Get the text content.

        Returns:
            Text content
        """
        return self.content

    def set_position(self, position: Point) -> None:
        """Set the text position.

        Args:
            position: New position
        """
        # Remove dependency on old position
        if hasattr(self.position, "id"):
            self.dependencies.discard(self.position.id)

        # Set new position
        self.position = position

        # Add dependency on new position
        if hasattr(position, "id"):
            self.dependencies.add(position.id)

    def get_position(self) -> Point:
        """Get the text position.

        Returns:
            Text position
        """
        return self.position

    def set_rotation(self, rotation: float) -> None:
        """Set the text rotation.

        Args:
            rotation: Rotation angle in degrees
        """
        self.rotation = rotation % 360

    def get_rotation(self) -> float:
        """Get the text rotation.

        Returns:
            Rotation angle in degrees
        """
        return self.rotation
