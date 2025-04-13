"""Geometric object model for the Sacred Geometry Explorer.

This package contains the geometric object model classes used by the
Sacred Geometry Explorer.
"""

# Import base class
from geometry.ui.sacred_geometry.model.base import GeometricObject
from geometry.ui.sacred_geometry.model.circle import Circle

# Import enumerations
from geometry.ui.sacred_geometry.model.enums import LineType, ObjectType

# Import factory
from geometry.ui.sacred_geometry.model.factory import GeometricObjectFactory
from geometry.ui.sacred_geometry.model.line import Line

# Import geometric objects
from geometry.ui.sacred_geometry.model.point import Point
from geometry.ui.sacred_geometry.model.polygon import Polygon

# Import style
from geometry.ui.sacred_geometry.model.style import Style
from geometry.ui.sacred_geometry.model.text import Text

# Define __all__ to control what is imported with 'from model import *'
__all__ = [
    "ObjectType",
    "LineType",
    "Style",
    "GeometricObject",
    "Point",
    "Line",
    "Circle",
    "Polygon",
    "Text",
    "GeometricObjectFactory",
]
