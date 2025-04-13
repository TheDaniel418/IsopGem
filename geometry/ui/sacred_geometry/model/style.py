"""Style properties for geometric objects.

This module contains the Style class used to define the visual appearance
of geometric objects in the Sacred Geometry Explorer.
"""

from typing import Dict, Any
from dataclasses import dataclass, field
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPen, QBrush, QColor


@dataclass
class Style:
    """Style properties for geometric objects."""
    stroke_color: QColor = field(default_factory=lambda: QColor(0, 0, 0))
    fill_color: QColor = field(default_factory=lambda: QColor(255, 255, 255, 0))  # Transparent by default
    stroke_width: float = 1.0
    stroke_style: Qt.PenStyle = Qt.PenStyle.SolidLine
    fill_style: Qt.BrushStyle = Qt.BrushStyle.SolidPattern
    point_size: float = 5.0
    font_family: str = "Arial"
    font_size: float = 12.0
    font_style: int = 0  # 0 = normal, 1 = bold, 2 = italic, 3 = bold italic

    def to_dict(self) -> Dict[str, Any]:
        """Convert the style to a dictionary for serialization."""
        return {
            "stroke_color": [self.stroke_color.red(), self.stroke_color.green(), self.stroke_color.blue(), self.stroke_color.alpha()],
            "fill_color": [self.fill_color.red(), self.fill_color.green(), self.fill_color.blue(), self.fill_color.alpha()],
            "stroke_width": self.stroke_width,
            "stroke_style": int(self.stroke_style.value),
            "fill_style": int(self.fill_style.value),
            "point_size": self.point_size,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "font_style": self.font_style
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Style':
        """Create a style from a dictionary."""
        style = cls()

        if "stroke_color" in data:
            r, g, b, a = data["stroke_color"]
            style.stroke_color = QColor(r, g, b, a)

        if "fill_color" in data:
            r, g, b, a = data["fill_color"]
            style.fill_color = QColor(r, g, b, a)

        style.stroke_width = data.get("stroke_width", 1.0)
        style.stroke_style = Qt.PenStyle(data.get("stroke_style", int(Qt.PenStyle.SolidLine)))
        style.fill_style = Qt.BrushStyle(data.get("fill_style", int(Qt.BrushStyle.SolidPattern)))
        style.point_size = data.get("point_size", 5.0)
        style.font_family = data.get("font_family", "Arial")
        style.font_size = data.get("font_size", 12.0)
        style.font_style = data.get("font_style", 0)

        return style

    def get_pen(self) -> QPen:
        """Get a QPen based on the style."""
        pen = QPen(self.stroke_color)
        pen.setWidthF(self.stroke_width)
        pen.setStyle(self.stroke_style)
        return pen

    def get_brush(self) -> QBrush:
        """Get a QBrush based on the style."""
        brush = QBrush(self.fill_color)
        brush.setStyle(self.fill_style)
        return brush