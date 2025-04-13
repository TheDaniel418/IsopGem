"""Factory for creating geometric objects.

This module contains the GeometricObjectFactory class that provides
factory methods for creating geometric objects.
"""

from typing import Dict, Any, Type, Optional
import logging

from geometry.ui.sacred_geometry.model.base import GeometricObject
from geometry.ui.sacred_geometry.model.enums import ObjectType
from geometry.ui.sacred_geometry.model.point import Point
from geometry.ui.sacred_geometry.model.line import Line, LineType
from geometry.ui.sacred_geometry.model.circle import Circle
from geometry.ui.sacred_geometry.model.polygon import Polygon
from geometry.ui.sacred_geometry.model.text import Text

# Set up logging
logger = logging.getLogger(__name__)


class GeometricObjectFactory:
    """Factory for creating geometric objects."""

    @staticmethod
    def create_object(object_type: ObjectType, **kwargs) -> Optional[GeometricObject]:
        """Create a geometric object of the specified type.

        Args:
            object_type: Type of object to create
            **kwargs: Additional arguments for the object constructor

        Returns:
            Created geometric object or None if the type is invalid
        """
        if object_type == ObjectType.POINT:
            return Point(
                x=kwargs.get('x', 0),
                y=kwargs.get('y', 0),
                name=kwargs.get('name'),
                style=kwargs.get('style')
            )
        elif object_type == ObjectType.LINE:
            return Line(
                x1=kwargs.get('x1', 0),
                y1=kwargs.get('y1', 0),
                x2=kwargs.get('x2', 1),
                y2=kwargs.get('y2', 0),
                name=kwargs.get('name'),
                style=kwargs.get('style'),
                line_type=kwargs.get('line_type', LineType.SEGMENT)
            )
        elif object_type == ObjectType.CIRCLE:
            return Circle(
                center=kwargs.get('center'),
                radius=kwargs.get('radius', 1),
                name=kwargs.get('name'),
                style=kwargs.get('style')
            )
        elif object_type == ObjectType.POLYGON:
            return Polygon(
                vertices=kwargs.get('vertices', []),
                name=kwargs.get('name'),
                style=kwargs.get('style')
            )
        elif object_type == ObjectType.TEXT:
            return Text(
                position=kwargs.get('position'),
                content=kwargs.get('content', ''),
                name=kwargs.get('name'),
                style=kwargs.get('style')
            )
        else:
            logger.warning(f"Unknown object type: {object_type}")
            return None

    @staticmethod
    def create_from_dict(data: Dict[str, Any]) -> Optional[GeometricObject]:
        """Create a geometric object from a dictionary.

        Args:
            data: Dictionary representation of the object

        Returns:
            Created geometric object or None if the type is invalid
        """
        # Get object type
        object_type_name = data.get('object_type')
        if not object_type_name:
            logger.warning(f"Missing object_type in data: {data}")
            return None

        try:
            object_type = ObjectType[object_type_name]
        except (KeyError, ValueError):
            logger.warning(f"Invalid object_type: {object_type_name}")
            return None

        # Create object based on type
        if object_type == ObjectType.POINT:
            return Point.from_dict(data)
        elif object_type == ObjectType.LINE:
            return Line.from_dict(data)
        elif object_type == ObjectType.CIRCLE:
            return Circle.from_dict(data)
        elif object_type == ObjectType.POLYGON:
            return Polygon.from_dict(data)
        elif object_type == ObjectType.TEXT:
            return Text.from_dict(data)
        else:
            logger.warning(f"Unsupported object_type: {object_type}")
            return None