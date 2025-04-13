"""Enumerations for the Sacred Geometry Explorer.

This module contains enumerations used by the geometric object model.
"""

from enum import Enum, auto


class ObjectType(Enum):
    """Enumeration of geometric object types."""

    POINT = auto()
    LINE = auto()
    CIRCLE = auto()
    POLYGON = auto()
    ARC = auto()
    ANGLE = auto()
    TEXT = auto()
    GROUP = auto()


class LineType(Enum):
    """Enumeration of line types."""

    SEGMENT = auto()  # Line segment with finite length
    RAY = auto()  # Ray starting at p1 and extending infinitely through p2
    INFINITE = auto()  # Infinite line passing through p1 and p2
