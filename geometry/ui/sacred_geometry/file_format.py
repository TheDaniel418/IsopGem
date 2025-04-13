"""File format for the Sacred Geometry Explorer.

This module contains the file format for the Sacred Geometry Explorer,
which is used to save and load geometry constructions.
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from loguru import logger
from PyQt6.QtGui import QColor

from geometry.ui.sacred_geometry.model import (
    GeometricObject, Point, Line, Circle, Style, ObjectType
)


class GeometryEncoder(json.JSONEncoder):
    """JSON encoder for geometry objects."""

    def default(self, obj):
        """Encode a geometry object as JSON.

        Args:
            obj: Object to encode

        Returns:
            JSON-serializable representation of the object
        """
        if isinstance(obj, QColor):
            # Convert QColor to a list of RGBA values
            return [obj.red(), obj.green(), obj.blue(), obj.alpha()]
        elif isinstance(obj, GeometricObject):
            # Base properties for all geometric objects
            result = {
                "id": obj.id,
                "type": obj.__class__.__name__,
                "name": obj.name,
                "visible": obj.visible,
                "locked": obj.locked,
                "selected": obj.selected,
                "style": {
                    "stroke_color": [obj.style.stroke_color.red(), obj.style.stroke_color.green(), obj.style.stroke_color.blue(), obj.style.stroke_color.alpha()],
                    "fill_color": [obj.style.fill_color.red(), obj.style.fill_color.green(), obj.style.fill_color.blue(), obj.style.fill_color.alpha()],
                    "stroke_width": obj.style.stroke_width,
                    "stroke_style": int(obj.style.stroke_style.value),
                    "fill_style": int(obj.style.fill_style.value),
                    "point_size": obj.style.point_size,
                    "font_family": obj.style.font_family,
                    "font_size": obj.style.font_size,
                    "font_style": obj.style.font_style
                }
            }

            # Add type-specific properties
            if isinstance(obj, Point):
                result.update({
                    "x": obj.x,
                    "y": obj.y
                })
            elif isinstance(obj, Line):
                result.update({
                    "x1": obj.x1,
                    "y1": obj.y1,
                    "x2": obj.x2,
                    "y2": obj.y2
                })
            elif isinstance(obj, Circle):
                result.update({
                    "center": obj.center.id,
                    "radius": obj.radius
                })

            return result

        # Let the base class handle other types
        return super().default(obj)


def serialize_construction(objects: List[GeometricObject]) -> Dict[str, Any]:
    """Serialize a construction to a dictionary.

    Args:
        objects: List of geometric objects in the construction

    Returns:
        Dictionary representation of the construction
    """
    # Create dictionary with metadata
    construction = {
        "version": "1.0",
        "type": "sacred_geometry_construction",
        "objects": []
    }

    # Add objects
    for obj in objects:
        construction["objects"].append(obj)

    # Serialize to JSON
    return json.loads(json.dumps(construction, cls=GeometryEncoder))


def save_construction(file_path: str, objects: List[GeometricObject]) -> bool:
    """Save a construction to a file.

    Args:
        file_path: Path to save the file to
        objects: List of geometric objects in the construction

    Returns:
        True if the construction was saved successfully, False otherwise
    """
    try:
        # Serialize construction
        construction = serialize_construction(objects)

        # Save to file
        with open(file_path, 'w') as f:
            json.dump(construction, f, indent=2)

        logger.debug(f"Saved construction to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving construction to {file_path}: {e}")
        return False


def deserialize_construction(data: Dict[str, Any]) -> Tuple[List[GeometricObject], Dict[str, GeometricObject]]:
    """Deserialize a construction from a dictionary.

    Args:
        data: Dictionary representation of the construction

    Returns:
        Tuple of (list of geometric objects, dictionary mapping object IDs to objects)
    """
    # Check version and type
    version = data.get("version", "unknown")
    type_ = data.get("type", "unknown")

    if version != "1.0" or type_ != "sacred_geometry_construction":
        logger.warning(f"Unknown construction format: version={version}, type={type_}")

    # Create objects
    objects = []
    obj_map = {}

    # First pass: create all points
    for obj_data in data.get("objects", []):
        if obj_data.get("type") == "Point":
            # Create point
            point = Point(
                x=obj_data.get("x", 0),
                y=obj_data.get("y", 0),
                name=obj_data.get("name", "")
            )

            # Set ID
            point.id = obj_data.get("id", point.id)

            # Set properties
            point.visible = obj_data.get("visible", True)
            point.locked = obj_data.get("locked", False)
            point.selected = obj_data.get("selected", False)

            # Set style
            style_data = obj_data.get("style", {})

            # Handle color values (convert from RGBA list to QColor)
            if "stroke_color" in style_data and isinstance(style_data["stroke_color"], list):
                rgba = style_data["stroke_color"]
                if len(rgba) == 4:
                    point.style.stroke_color = QColor(rgba[0], rgba[1], rgba[2], rgba[3])

            if "fill_color" in style_data and isinstance(style_data["fill_color"], list):
                rgba = style_data["fill_color"]
                if len(rgba) == 4:
                    point.style.fill_color = QColor(rgba[0], rgba[1], rgba[2], rgba[3])

            # Set other style properties
            point.style.stroke_width = style_data.get("stroke_width", point.style.stroke_width)

            # Handle enum values
            if "stroke_style" in style_data:
                from PyQt6.QtCore import Qt
                point.style.stroke_style = Qt.PenStyle(style_data["stroke_style"])

            if "fill_style" in style_data:
                from PyQt6.QtCore import Qt
                point.style.fill_style = Qt.BrushStyle(style_data["fill_style"])

            point.style.point_size = style_data.get("point_size", point.style.point_size)
            point.style.font_family = style_data.get("font_family", point.style.font_family)
            point.style.font_size = style_data.get("font_size", point.style.font_size)
            point.style.font_style = style_data.get("font_style", point.style.font_style)

            # Add to lists
            objects.append(point)
            obj_map[point.id] = point

    # Second pass: create all other objects
    for obj_data in data.get("objects", []):
        if obj_data.get("type") == "Line":
            # Get line coordinates
            x1 = obj_data.get("x1", 0)
            y1 = obj_data.get("y1", 0)
            x2 = obj_data.get("x2", 0)
            y2 = obj_data.get("y2", 0)

            # Handle legacy format with p1 and p2 references
            if "p1" in obj_data and "p2" in obj_data:
                p1_id = obj_data.get("p1")
                p2_id = obj_data.get("p2")

                if p1_id in obj_map and p2_id in obj_map:
                    p1 = obj_map[p1_id]
                    p2 = obj_map[p2_id]
                    x1, y1 = p1.x, p1.y
                    x2, y2 = p2.x, p2.y
                else:
                    logger.warning(f"Could not create line: points not found (p1={p1_id}, p2={p2_id})")
                    continue

            # Create line
            line = Line(x1, y1, x2, y2, obj_data.get("name", ""))

            # Set ID
            line.id = obj_data.get("id", line.id)

            # Set properties
            line.visible = obj_data.get("visible", True)
            line.locked = obj_data.get("locked", False)
            line.selected = obj_data.get("selected", False)

            # Set style
            style_data = obj_data.get("style", {})

            # Handle color values (convert from RGBA list to QColor)
            if "stroke_color" in style_data and isinstance(style_data["stroke_color"], list):
                rgba = style_data["stroke_color"]
                if len(rgba) == 4:
                    line.style.stroke_color = QColor(rgba[0], rgba[1], rgba[2], rgba[3])

            if "fill_color" in style_data and isinstance(style_data["fill_color"], list):
                rgba = style_data["fill_color"]
                if len(rgba) == 4:
                    line.style.fill_color = QColor(rgba[0], rgba[1], rgba[2], rgba[3])

            # Set other style properties
            line.style.stroke_width = style_data.get("stroke_width", line.style.stroke_width)

            # Handle enum values
            if "stroke_style" in style_data:
                from PyQt6.QtCore import Qt
                line.style.stroke_style = Qt.PenStyle(style_data["stroke_style"])

            if "fill_style" in style_data:
                from PyQt6.QtCore import Qt
                line.style.fill_style = Qt.BrushStyle(style_data["fill_style"])

            line.style.point_size = style_data.get("point_size", line.style.point_size)
            line.style.font_family = style_data.get("font_family", line.style.font_family)
            line.style.font_size = style_data.get("font_size", line.style.font_size)
            line.style.font_style = style_data.get("font_style", line.style.font_style)

            # Add to lists
            objects.append(line)
            obj_map[line.id] = line

        elif obj_data.get("type") == "Circle":
            # Get center point
            center_id = obj_data.get("center")

            if center_id in obj_map:
                center = obj_map[center_id]

                # Create circle
                circle = Circle(center, obj_data.get("radius", 1), obj_data.get("name", ""))

                # Set ID
                circle.id = obj_data.get("id", circle.id)

                # Set properties
                circle.visible = obj_data.get("visible", True)
                circle.locked = obj_data.get("locked", False)
                circle.selected = obj_data.get("selected", False)

                # Set style
                style_data = obj_data.get("style", {})

                # Handle color values (convert from RGBA list to QColor)
                if "stroke_color" in style_data and isinstance(style_data["stroke_color"], list):
                    rgba = style_data["stroke_color"]
                    if len(rgba) == 4:
                        circle.style.stroke_color = QColor(rgba[0], rgba[1], rgba[2], rgba[3])

                if "fill_color" in style_data and isinstance(style_data["fill_color"], list):
                    rgba = style_data["fill_color"]
                    if len(rgba) == 4:
                        circle.style.fill_color = QColor(rgba[0], rgba[1], rgba[2], rgba[3])

                # Set other style properties
                circle.style.stroke_width = style_data.get("stroke_width", circle.style.stroke_width)

                # Handle enum values
                if "stroke_style" in style_data:
                    from PyQt6.QtCore import Qt
                    circle.style.stroke_style = Qt.PenStyle(style_data["stroke_style"])

                if "fill_style" in style_data:
                    from PyQt6.QtCore import Qt
                    circle.style.fill_style = Qt.BrushStyle(style_data["fill_style"])

                circle.style.point_size = style_data.get("point_size", circle.style.point_size)
                circle.style.font_family = style_data.get("font_family", circle.style.font_family)
                circle.style.font_size = style_data.get("font_size", circle.style.font_size)
                circle.style.font_style = style_data.get("font_style", circle.style.font_style)

                # Add to lists
                objects.append(circle)
                obj_map[circle.id] = circle
            else:
                logger.warning(f"Could not create circle: center point not found (center={center_id})")

    return objects, obj_map


def load_construction(file_path: str) -> Optional[List[GeometricObject]]:
    """Load a construction from a file.

    Args:
        file_path: Path to load the file from

    Returns:
        List of geometric objects in the construction, or None if loading failed
    """
    try:
        # Load from file
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Deserialize construction
        objects, _ = deserialize_construction(data)

        logger.debug(f"Loaded construction from {file_path}")
        return objects
    except Exception as e:
        logger.error(f"Error loading construction from {file_path}: {e}")
        return None
