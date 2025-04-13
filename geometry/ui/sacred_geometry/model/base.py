"""Base class for all geometric objects.

This module contains the GeometricObject base class that provides common
functionality for all geometric objects in the Sacred Geometry Explorer.
"""

from typing import Any, ClassVar, Dict, List, Set, Type
from uuid import uuid4

from PyQt6.QtCore import QPointF, QRectF

from geometry.ui.sacred_geometry.model.enums import ObjectType
from geometry.ui.sacred_geometry.model.style import Style


class GeometricObject:
    """Base class for all geometric objects.

    This class provides common functionality for all geometric objects,
    such as identification, selection, and property access.
    """

    # Class variables
    object_type: ClassVar[ObjectType] = None
    registry: ClassVar[Dict[str, Type["GeometricObject"]]] = {}

    def __init_subclass__(cls, **kwargs):
        """Register subclasses for factory creation."""
        super().__init_subclass__(**kwargs)
        if cls.object_type is not None:
            GeometricObject.registry[cls.object_type.name] = cls

    def __init__(self, name: str = None, style: Style = None) -> None:
        """Initialize a geometric object.

        Args:
            name: Optional name for the object
            style: Optional style for the object
        """
        self.id = str(uuid4())
        self.name = name or f"Object_{self.id[:8]}"
        self.selected = False
        self.visible = True
        self.locked = False
        self.style = style or Style()
        self.tags: Set[str] = set()
        self.dependencies: Set[str] = set()  # IDs of objects this object depends on
        self.dependents: Set[str] = set()  # IDs of objects that depend on this object
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary for serialization.

        Returns:
            Dictionary representation of the object
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.__class__.__name__,
            "object_type": self.object_type.name if self.object_type else None,
            "visible": self.visible,
            "locked": self.locked,
            "style": self.style.to_dict(),
            "tags": list(self.tags),
            "dependencies": list(self.dependencies),
            "dependents": list(self.dependents),
            "metadata": self.metadata.copy(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GeometricObject":
        """Create an object from a dictionary.

        Args:
            data: Dictionary representation of the object

        Returns:
            Reconstructed geometric object
        """
        obj = cls(name=data.get("name"))
        obj.id = data.get("id", obj.id)
        obj.visible = data.get("visible", True)
        obj.locked = data.get("locked", False)

        if "style" in data:
            obj.style = Style.from_dict(data["style"])

        obj.tags = set(data.get("tags", []))
        obj.dependencies = set(data.get("dependencies", []))
        obj.dependents = set(data.get("dependents", []))
        obj.metadata = data.get("metadata", {}).copy()

        return obj

    def get_bounds(self) -> QRectF:
        """Get the bounding rectangle of the object.

        Returns:
            Bounding rectangle in scene coordinates
        """
        # Base implementation returns an empty rectangle
        # Subclasses should override this method
        return QRectF()

    def contains_point(self, point: QPointF, tolerance: float = 5.0) -> bool:
        """Check if the object contains or is near the given point.

        Args:
            point: Point to check in scene coordinates
            tolerance: Distance tolerance in pixels

        Returns:
            True if the object contains or is near the point
        """
        # Base implementation returns False
        # Subclasses should override this method
        return False

    def move_by(self, dx: float, dy: float) -> None:
        """Move the object by the given delta.

        Args:
            dx: X-axis delta
            dy: Y-axis delta
        """
        # Base implementation does nothing
        # Subclasses should override this method
        pass

    def rotate(self, angle: float, center: QPointF = None) -> None:
        """Rotate the object by the given angle around the given center.

        Args:
            angle: Rotation angle in degrees
            center: Rotation center (if None, use object center)
        """
        # Base implementation does nothing
        # Subclasses should override this method
        pass

    def scale(self, sx: float, sy: float, center: QPointF = None) -> None:
        """Scale the object by the given factors around the given center.

        Args:
            sx: X-axis scale factor
            sy: Y-axis scale factor
            center: Scaling center (if None, use object center)
        """
        # Base implementation does nothing
        # Subclasses should override this method
        pass

    def distance_to(self, point: QPointF) -> float:
        """Calculate the distance from the object to the given point.

        Args:
            point: Point to calculate distance to

        Returns:
            Distance to the point
        """
        # Base implementation returns infinity
        # Subclasses should override this method
        return float("inf")

    def intersect(self, other: "GeometricObject") -> List[QPointF]:
        """Calculate intersection points with another object.

        Args:
            other: Other geometric object

        Returns:
            List of intersection points
        """
        # Base implementation returns an empty list
        # Subclasses should override this method
        return []

    def clone(self) -> "GeometricObject":
        """Create a clone of this object.

        Returns:
            A new object with the same properties
        """
        # Default implementation uses serialization
        data = self.to_dict()
        data["id"] = str(uuid4())  # Generate a new ID
        return self.__class__.from_dict(data)

    def notify_dependents(self, canvas) -> None:
        """Notify all dependent objects that this object has changed.

        Args:
            canvas: The canvas containing all objects
        """
        for dependent_id in self.dependents:
            for obj in canvas.objects:
                if obj.id == dependent_id:
                    obj.update_from_dependencies()
                    break

    def update_from_dependencies(self) -> None:
        """Update the object when its dependencies change.

        This method should be overridden by subclasses that need to
        update their state when their dependencies change.
        """
        # Base implementation does nothing
        pass
