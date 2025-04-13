"""Line geometric object for the Sacred Geometry Explorer.

This module contains the Line class that represents a line in 2D space.
"""

from typing import Dict, Any, List
import math
from PyQt6.QtCore import QPointF, QRectF

from geometry.ui.sacred_geometry.model.base import GeometricObject
from geometry.ui.sacred_geometry.model.enums import ObjectType, LineType
from geometry.ui.sacred_geometry.model.style import Style


class Line(GeometricObject):
    """A line defined by two endpoints.

    The line can be a segment (finite length), a ray (infinite in one direction),
    or an infinite line (infinite in both directions).
    """

    object_type = ObjectType.LINE

    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 1, y2: float = 0,
                 name: str = None, style: Style = None,
                 line_type: LineType = LineType.SEGMENT) -> None:
        """Initialize a line.

        Args:
            x1: X coordinate of first endpoint
            y1: Y coordinate of first endpoint
            x2: X coordinate of second endpoint
            y2: Y coordinate of second endpoint
            name: Optional name for the line
            style: Optional style for the line
            line_type: Type of line (segment, ray, or infinite)
        """
        super().__init__(name, style)
        # Store endpoints as private coordinates to prevent direct access
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self.line_type = line_type

        # Add debug logging for initialization
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line initialized with P1=({self._x1}, {self._y1}), P2=({self._x2}, {self._y2})")

    # Add properties for direct access to the private attributes
    @property
    def x1(self) -> float:
        """Get the x coordinate of the first endpoint."""
        return self._x1

    @x1.setter
    def x1(self, value: float) -> None:
        """Set the x coordinate of the first endpoint."""
        # Add debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.x1 setter called with value {value}")
        logger.debug(f"DEBUG: Before x1 change: P1=({self._x1}, {self._y1}), P2=({self._x2}, {self._y2})")

        # Update only x1
        self._x1 = value

        logger.debug(f"DEBUG: After x1 change: P1=({self._x1}, {self._y1}), P2=({self._x2}, {self._y2})")

    @property
    def y1(self) -> float:
        """Get the y coordinate of the first endpoint."""
        return self._y1

    @y1.setter
    def y1(self, value: float) -> None:
        """Set the y coordinate of the first endpoint."""
        # Add debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.y1 setter called with value {value}")
        logger.debug(f"DEBUG: Before y1 change: P1=({self._x1}, {self._y1}), P2=({self._x2}, {self._y2})")

        # Update only y1
        self._y1 = value

        logger.debug(f"DEBUG: After y1 change: P1=({self._x1}, {self._y1}), P2=({self._x2}, {self._y2})")

    @property
    def x2(self) -> float:
        """Get the x coordinate of the second endpoint."""
        return self._x2

    @x2.setter
    def x2(self, value: float) -> None:
        """Set the x coordinate of the second endpoint."""
        # Add debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.x2 setter called with value {value}")
        logger.debug(f"DEBUG: Before x2 change: P1=({self._x1}, {self._y1}), P2=({self._x2}, {self._y2})")

        # Update only x2
        self._x2 = value

        logger.debug(f"DEBUG: After x2 change: P1=({self._x1}, {self._y1}), P2=({self._x2}, {self._y2})")

    @property
    def y2(self) -> float:
        """Get the y coordinate of the second endpoint."""
        return self._y2

    @y2.setter
    def y2(self, value: float) -> None:
        """Set the y coordinate of the second endpoint."""
        # Add debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.y2 setter called with value {value}")
        logger.debug(f"DEBUG: Before y2 change: P1=({self._x1}, {self._y1}), P2=({self._x2}, {self._y2})")

        # Update only y2
        self._y2 = value

        logger.debug(f"DEBUG: After y2 change: P1=({self._x1}, {self._y1}), P2=({self._x2}, {self._y2})")

    def to_dict(self) -> Dict[str, Any]:
        """Convert the line to a dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "line_type": self.line_type.name
        })
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Line':
        """Create a line from a dictionary."""
        # Get coordinates
        x1 = data.get("x1", 0)
        y1 = data.get("y1", 0)
        x2 = data.get("x2", 1)
        y2 = data.get("y2", 0)

        # Handle legacy format with p1/p2 points
        if "p1" in data and data["p1"]:
            p1 = data["p1"]
            x1 = p1.get("x", 0)
            y1 = p1.get("y", 0)
        if "p2" in data and data["p2"]:
            p2 = data["p2"]
            x2 = p2.get("x", 1)
            y2 = p2.get("y", 0)

        # Get line type
        line_type = LineType.SEGMENT  # Default
        if "line_type" in data:
            try:
                line_type = LineType[data["line_type"]]
            except (KeyError, ValueError):
                # If line_type is invalid, use default
                pass

        line = cls(
            x1=x1,
            y1=y1,
            x2=x2,
            y2=y2,
            name=data.get("name"),
            line_type=line_type
        )

        # Load base class properties
        line.id = data.get("id", line.id)
        line.visible = data.get("visible", True)
        line.locked = data.get("locked", False)

        if "style" in data:
            line.style = Style.from_dict(data["style"])

        line.tags = set(data.get("tags", []))
        line.dependencies = set(data.get("dependencies", []))
        line.dependents = set(data.get("dependents", []))
        line.metadata = data.get("metadata", {}).copy()

        return line

    def get_bounds(self) -> QRectF:
        """Get the bounding rectangle of the line.

        For segments, this is the rectangle containing the two endpoints.
        For rays and infinite lines, this is a large rectangle that covers
        the visible area of the canvas.
        """
        x1, y1 = self.x1, self.y1
        x2, y2 = self.x2, self.y2

        # Add padding for line width
        padding = self.style.stroke_width / 2

        if self.line_type == LineType.SEGMENT:
            # For segments, just use the rectangle containing the endpoints
            return QRectF(
                min(x1, x2) - padding,
                min(y1, y2) - padding,
                abs(x2 - x1) + padding * 2,
                abs(y2 - y1) + padding * 2
            )
        elif self.line_type == LineType.RAY:
            # For rays, extend the line in the direction from p1 to p2
            # Calculate direction vector
            dx = x2 - x1
            dy = y2 - y1

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in the direction of p2
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x = x2 + dx * extension
            extended_y = y2 + dy * extension

            return QRectF(
                min(x1, extended_x) - padding,
                min(y1, extended_y) - padding,
                abs(extended_x - x1) + padding * 2,
                abs(extended_y - y1) + padding * 2
            )
        else:  # LineType.INFINITE
            # For infinite lines, extend in both directions
            # Calculate direction vector
            dx = x2 - x1
            dy = y2 - y1

            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length

            # Extend the line by a large amount in both directions
            extension = 10000  # A large value to ensure the line extends beyond the visible area
            extended_x1 = x1 - dx * extension
            extended_y1 = y1 - dy * extension
            extended_x2 = x2 + dx * extension
            extended_y2 = y2 + dy * extension

            return QRectF(
                min(extended_x1, extended_x2) - padding,
                min(extended_y1, extended_y2) - padding,
                abs(extended_x2 - extended_x1) + padding * 2,
                abs(extended_y2 - extended_y1) + padding * 2
            )

    def contains_point(self, point: QPointF, tolerance: float = 5.0) -> bool:
        """Check if the line contains or is near the given point."""
        return self.distance_to(point) <= tolerance

    def move_by(self, dx: float, dy: float) -> None:
        """Move the line by the given delta."""
        # Store original values for debugging
        old_x1, old_y1 = self.x1, self.y1
        old_x2, old_y2 = self.x2, self.y2

        # Log before update
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.move_by({dx}, {dy}) called")
        logger.debug(f"DEBUG: Before move_by: P1=({old_x1}, {old_y1}), P2=({old_x2}, {old_y2})")

        # Move both endpoints
        self.x1 += dx
        self.y1 += dy
        self.x2 += dx
        self.y2 += dy

        # Log after update
        logger.debug(f"DEBUG: After move_by: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

    def move_endpoint(self, endpoint: int, x: float, y: float) -> None:
        """Move a specific endpoint to the given position.

        Args:
            endpoint: 1 for the first endpoint, 2 for the second endpoint
            x: New x coordinate
            y: New y coordinate
        """
        # Store original values for debugging
        old_x1, old_y1 = self.x1, self.y1
        old_x2, old_y2 = self.x2, self.y2

        # Get the current stack trace to see who called this method
        import traceback
        stack = traceback.extract_stack()
        caller = stack[-2]  # The caller is the second-to-last entry in the stack

        # Log before update
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.move_endpoint({endpoint}, {x}, {y}) called from {caller.filename}:{caller.lineno}")
        logger.debug(f"DEBUG: Before move: P1=({old_x1}, {old_y1}), P2=({old_x2}, {old_y2})")

        # ONLY update the specified endpoint
        if endpoint == 1:
            # Save the original values of the other endpoint
            orig_x2, orig_y2 = self.x2, self.y2

            # Update only endpoint 1
            self.x1 = x
            self.y1 = y

            # Verify endpoint 2 hasn't changed
            if self.x2 != orig_x2 or self.y2 != orig_y2:
                logger.error(f"ERROR: Endpoint 2 changed unexpectedly from ({orig_x2}, {orig_y2}) to ({self.x2}, {self.y2})")
                # Force it back to the original value
                self.x2 = orig_x2
                self.y2 = orig_y2

            logger.debug(f"DEBUG: Moving ONLY endpoint 1 to ({x}, {y})")
        elif endpoint == 2:
            # Save the original values of the other endpoint
            orig_x1, orig_y1 = self.x1, self.y1

            # Update only endpoint 2
            self.x2 = x
            self.y2 = y

            # Verify endpoint 1 hasn't changed
            if self.x1 != orig_x1 or self.y1 != orig_y1:
                logger.error(f"ERROR: Endpoint 1 changed unexpectedly from ({orig_x1}, {orig_y1}) to ({self.x1}, {self.y1})")
                # Force it back to the original value
                self.x1 = orig_x1
                self.y1 = orig_y1

            logger.debug(f"DEBUG: Moving ONLY endpoint 2 to ({x}, {y})")

        # Log after update
        logger.debug(f"DEBUG: After move: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

    # Add properties for endpoint coordinates to support property panel
    @property
    def endpoint1_x(self) -> float:
        """Get the x coordinate of the first endpoint."""
        return self.x1

    @endpoint1_x.setter
    def endpoint1_x(self, value: float) -> None:
        """Set the x coordinate of the first endpoint."""
        # Store original values for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.endpoint1_x setter called with value {value}")
        logger.debug(f"DEBUG: Before endpoint1_x change: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

        # Store the original value of the other endpoint
        orig_x2, orig_y2 = self.x2, self.y2

        # Update only the first endpoint's x coordinate
        self.x1 = value

        # Verify the other endpoint hasn't changed
        if self.x2 != orig_x2 or self.y2 != orig_y2:
            logger.error(f"ERROR: Endpoint 2 changed unexpectedly in endpoint1_x setter from ({orig_x2}, {orig_y2}) to ({self.x2}, {self.y2})")
            # Force it back to the original value
            self.x2 = orig_x2
            self.y2 = orig_y2

        logger.debug(f"DEBUG: After endpoint1_x change: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

    @property
    def endpoint1_y(self) -> float:
        """Get the y coordinate of the first endpoint."""
        return self.y1

    @endpoint1_y.setter
    def endpoint1_y(self, value: float) -> None:
        """Set the y coordinate of the first endpoint."""
        # Store original values for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.endpoint1_y setter called with value {value}")
        logger.debug(f"DEBUG: Before endpoint1_y change: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

        # Store the original value of the other endpoint
        orig_x2, orig_y2 = self.x2, self.y2

        # Update only the first endpoint's y coordinate
        self.y1 = value

        # Verify the other endpoint hasn't changed
        if self.x2 != orig_x2 or self.y2 != orig_y2:
            logger.error(f"ERROR: Endpoint 2 changed unexpectedly in endpoint1_y setter from ({orig_x2}, {orig_y2}) to ({self.x2}, {self.y2})")
            # Force it back to the original value
            self.x2 = orig_x2
            self.y2 = orig_y2

        logger.debug(f"DEBUG: After endpoint1_y change: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

    @property
    def endpoint2_x(self) -> float:
        """Get the x coordinate of the second endpoint."""
        return self.x2

    @endpoint2_x.setter
    def endpoint2_x(self, value: float) -> None:
        """Set the x coordinate of the second endpoint."""
        # Store original values for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.endpoint2_x setter called with value {value}")
        logger.debug(f"DEBUG: Before endpoint2_x change: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

        # Store the original value of the other endpoint
        orig_x1, orig_y1 = self.x1, self.y1

        # Update only the second endpoint's x coordinate
        self.x2 = value

        # Verify the other endpoint hasn't changed
        if self.x1 != orig_x1 or self.y1 != orig_y1:
            logger.error(f"ERROR: Endpoint 1 changed unexpectedly in endpoint2_x setter from ({orig_x1}, {orig_y1}) to ({self.x1}, {self.y1})")
            # Force it back to the original value
            self.x1 = orig_x1
            self.y1 = orig_y1

        logger.debug(f"DEBUG: After endpoint2_x change: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

    @property
    def endpoint2_y(self) -> float:
        """Get the y coordinate of the second endpoint."""
        return self.y2

    @endpoint2_y.setter
    def endpoint2_y(self, value: float) -> None:
        """Set the y coordinate of the second endpoint."""
        # Store original values for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"DEBUG: Line.endpoint2_y setter called with value {value}")
        logger.debug(f"DEBUG: Before endpoint2_y change: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

        # Store the original value of the other endpoint
        orig_x1, orig_y1 = self.x1, self.y1

        # Update only the second endpoint's y coordinate
        self.y2 = value

        # Verify the other endpoint hasn't changed
        if self.x1 != orig_x1 or self.y1 != orig_y1:
            logger.error(f"ERROR: Endpoint 1 changed unexpectedly in endpoint2_y setter from ({orig_x1}, {orig_y1}) to ({self.x1}, {self.y1})")
            # Force it back to the original value
            self.x1 = orig_x1
            self.y1 = orig_y1

        logger.debug(f"DEBUG: After endpoint2_y change: P1=({self.x1}, {self.y1}), P2=({self.x2}, {self.y2})")

    def get_endpoint(self, endpoint: int) -> tuple[float, float]:
        """Get the coordinates of a specific endpoint.

        Args:
            endpoint: 1 for the first endpoint, 2 for the second endpoint

        Returns:
            Tuple of (x, y) coordinates
        """
        if endpoint == 1:
            return (self.x1, self.y1)
        elif endpoint == 2:
            return (self.x2, self.y2)
        return (0, 0)  # Default fallback

    def rotate(self, angle: float, center: QPointF = None) -> None:
        """Rotate the line by the given angle around the given center."""
        if center is None:
            # Use midpoint as center
            center = QPointF((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

        # Convert angle to radians
        angle_rad = math.radians(angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)

        # Translate points so that center is at origin
        x1 = self.x1 - center.x()
        y1 = self.y1 - center.y()
        x2 = self.x2 - center.x()
        y2 = self.y2 - center.y()

        # Rotate points
        new_x1 = x1 * cos_angle - y1 * sin_angle
        new_y1 = x1 * sin_angle + y1 * cos_angle
        new_x2 = x2 * cos_angle - y2 * sin_angle
        new_y2 = x2 * sin_angle + y2 * cos_angle

        # Translate points back
        self.x1 = new_x1 + center.x()
        self.y1 = new_y1 + center.y()
        self.x2 = new_x2 + center.x()
        self.y2 = new_y2 + center.y()

    def scale(self, sx: float, sy: float, center: QPointF = None) -> None:
        """Scale the line by the given factors around the given center."""
        if center is None:
            # Use midpoint as center
            center = QPointF((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

        # Translate points so that center is at origin
        x1 = self.x1 - center.x()
        y1 = self.y1 - center.y()
        x2 = self.x2 - center.x()
        y2 = self.y2 - center.y()

        # Scale points
        x1 *= sx
        y1 *= sy
        x2 *= sx
        y2 *= sy

        # Translate points back
        self.x1 = x1 + center.x()
        self.y1 = y1 + center.y()
        self.x2 = x2 + center.x()
        self.y2 = y2 + center.y()

    def distance_to(self, point: QPointF) -> float:
        """Calculate the distance from the line to the given point.

        The behavior depends on the line type:
        - For segments, the distance is to the closest point on the segment
        - For rays, the distance is to the closest point on the ray
        - For infinite lines, the distance is to the closest point on the line
        """
        x1, y1 = self.x1, self.y1
        x2, y2 = self.x2, self.y2
        x0, y0 = point.x(), point.y()

        # Calculate line length squared
        line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2

        # If line is actually a point, return distance to that point
        if line_length_sq < 1e-10:
            return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

        # Calculate projection of point onto line
        t = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_sq

        # Clamp t based on line type
        if self.line_type == LineType.SEGMENT:
            # For segments, clamp t to [0, 1]
            t = max(0, min(1, t))
        elif self.line_type == LineType.RAY:
            # For rays, clamp t to [0, infinity)
            t = max(0, t)
        # For infinite lines, t is unclamped

        # Calculate closest point on line
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)

        # Return distance to closest point
        return math.sqrt((x0 - closest_x) ** 2 + (y0 - closest_y) ** 2)

    def intersect(self, other: GeometricObject) -> List[QPointF]:
        """Calculate intersection points with another object."""
        from geometry.ui.sacred_geometry.model.circle import Circle

        if isinstance(other, Line):
            return self._intersect_line(other)
        elif isinstance(other, Circle):
            return self._intersect_circle(other)
        else:
            return []

    def update_from_dependencies(self) -> None:
        """Update the line when its dependencies (endpoints) change.

        This method is called when one of the line's endpoints has moved.
        The line's position is already determined by its endpoints,
        so we just need to trigger a visual update in the canvas.
        """
        # The visual update will be handled by the canvas
        # This method is mainly a hook for the notification system
        pass

    def _intersect_line(self, other: 'Line') -> List[QPointF]:
        """Calculate intersection point with another line.

        The behavior depends on the line types of both lines.
        """
        x1, y1 = self.x1, self.y1
        x2, y2 = self.x2, self.y2
        x3, y3 = other.x1, other.y1
        x4, y4 = other.x2, other.y2

        # Calculate determinants
        den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

        # Check if lines are parallel
        if abs(den) < 1e-10:
            return []

        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den

        # Calculate intersection point
        x = x1 + ua * (x2 - x1)
        y = y1 + ua * (y2 - y1)
        intersection = QPointF(x, y)

        # Check if intersection is valid based on line types
        valid_intersection = True

        # Check this line
        if self.line_type == LineType.SEGMENT:
            # For segments, intersection must be within the segment
            if not (0 <= ua <= 1):
                valid_intersection = False
        elif self.line_type == LineType.RAY:
            # For rays, intersection must be in the direction of the ray
            if ua < 0:
                valid_intersection = False
        # For infinite lines, any intersection is valid

        # Check other line
        if valid_intersection:
            if other.line_type == LineType.SEGMENT:
                # For segments, intersection must be within the segment
                if not (0 <= ub <= 1):
                    valid_intersection = False
            elif other.line_type == LineType.RAY:
                # For rays, intersection must be in the direction of the ray
                if ub < 0:
                    valid_intersection = False
            # For infinite lines, any intersection is valid

        if valid_intersection:
            return [intersection]

        return []

    def _intersect_circle(self, circle) -> List[QPointF]:
        """Calculate intersection points with a circle."""
        # This will be implemented when we implement the Circle class
        # For now, we'll just return an empty list
        return []