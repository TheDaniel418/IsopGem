"""Geometric object model for the Sacred Geometry Explorer.

This package contains the geometric object model classes used by the
Sacred Geometry Explorer.
"""

# Import enumerations
from geometry.ui.sacred_geometry.model.enums import ObjectType, LineType

# Import style
from geometry.ui.sacred_geometry.model.style import Style

# Import base class
from geometry.ui.sacred_geometry.model.base import GeometricObject

# Import geometric objects
from geometry.ui.sacred_geometry.model.point import Point
from geometry.ui.sacred_geometry.model.line import Line
from geometry.ui.sacred_geometry.model.circle import Circle
from geometry.ui.sacred_geometry.model.polygon import Polygon
from geometry.ui.sacred_geometry.model.text import Text

# Import factory
from geometry.ui.sacred_geometry.model.factory import GeometricObjectFactory

# Define __all__ to control what is imported with 'from model import *'
__all__ = [
    'ObjectType',
    'LineType',
    'Style',
    'GeometricObject',
    'Point',
    'Line',
    'Circle',
    'Polygon',
    'Text',
    'GeometricObjectFactory'
]