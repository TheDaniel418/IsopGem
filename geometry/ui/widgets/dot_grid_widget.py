"""Dot grid widget for visualizing figurate numbers."""

import math
import time
from typing import List, Tuple

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath
from PyQt6.QtWidgets import QWidget


class DotGridWidget(QWidget):
    """Widget for visualizing dots in a grid pattern."""

    def __init__(self, parent=None):
        """Initialize the widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Coordinates in format (x, y, layer, dot_number)
        self.coordinates: List[Tuple[float, float, int, int]] = []

        # Visualization settings
        self.dot_size = 10.0
        self.zoom_level = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.show_labels = True
        self.show_layers = True
        self.show_dot_numbers = False
        self.show_grid = False
        self.show_star_lines = True  # Show lines connecting the star points
        self.performance_mode = True  # Enable performance optimizations by default

        # Set minimum size for better visualization
        self.setMinimumSize(400, 400)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(240, 240, 240))
        self.setPalette(palette)

        # Mouse tracking for dragging
        self.setMouseTracking(True)
        self.dragging = False
        self.last_mouse_pos = None
        
        # Performance tracking
        self.last_render_time = 0

    def set_coordinates(self, coordinates: List[Tuple[float, float, int, int]]) -> None:
        """Set the coordinates to display.

        Args:
            coordinates: List of (x, y, layer, dot_number) coordinates
        """
        self.coordinates = coordinates
        self.update()

    def toggle_grid(self, show: bool) -> None:
        """Toggle grid display.

        Args:
            show: Whether to show the grid
        """
        self.show_grid = show
        self.update()

    def toggle_labels(self, show: bool) -> None:
        """Toggle labels display.

        Args:
            show: Whether to show labels
        """
        self.show_labels = show
        self.update()

    def toggle_layers(self, show: bool) -> None:
        """Toggle layer coloring.

        Args:
            show: Whether to color by layer
        """
        self.show_layers = show
        self.update()

    def toggle_dot_numbers(self, show: bool) -> None:
        """Toggle dot number display.

        Args:
            show: Whether to show dot numbers
        """
        self.show_dot_numbers = show
        self.update()

    def toggle_star_lines(self, show: bool) -> None:
        """Toggle star lines display.

        Args:
            show: Whether to show star lines
        """
        self.show_star_lines = show
        self.update()

    def set_dot_size(self, size: float) -> None:
        """Set the dot size.

        Args:
            size: Size of dots
        """
        self.dot_size = max(2.0, min(20.0, size))
        self.update()

    def paintEvent(self, _) -> None:
        """Paint the visualization.

        Args:
            _: Paint event (unused but required by Qt)
        """
        # Record start time for performance tracking
        start_time = time.time() if hasattr(time, 'time') else 0
        
        painter = QPainter(self)
        
        # Only use antialiasing if we're not in performance mode with large star numbers
        if not (self.performance_mode and len(self.coordinates) > 1000):
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()

        # Calculate center of the widget
        center_x = width / 2 + self.pan_x
        center_y = height / 2 + self.pan_y

        # Draw background
        painter.fillRect(0, 0, width, height, QColor(240, 240, 240))

        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(painter, center_x, center_y, width, height)

        # Draw dots
        self._draw_dots(painter, self.coordinates, center_x, center_y)
        
        # Record render time for performance tracking
        if hasattr(time, 'time'):
            self.last_render_time = time.time() - start_time

    def _draw_grid(self, painter: QPainter, center_x: float, center_y: float,
                  width: float, height: float) -> None:
        """Draw a grid for reference.

        Args:
            painter: QPainter object
            center_x: X-coordinate of center
            center_y: Y-coordinate of center
            width: Widget width
            height: Widget height
        """
        # Set grid pen
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.PenStyle.DotLine))

        # Draw horizontal grid lines
        grid_spacing = 50 * self.zoom_level
        y = center_y % grid_spacing
        while y < height:
            painter.drawLine(0, int(y), int(width), int(y))
            y += grid_spacing
        y = center_y % grid_spacing
        while y > 0:
            painter.drawLine(0, int(y), int(width), int(y))
            y -= grid_spacing

        # Draw vertical grid lines
        x = center_x % grid_spacing
        while x < width:
            painter.drawLine(int(x), 0, int(x), int(height))
            x += grid_spacing
        x = center_x % grid_spacing
        while x > 0:
            painter.drawLine(int(x), 0, int(x), int(height))
            x -= grid_spacing

        # Draw axes
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawLine(0, int(center_y), int(width), int(center_y))  # X-axis
        painter.drawLine(int(center_x), 0, int(center_x), int(height))  # Y-axis

    def _draw_dots(self, painter: QPainter, coordinates: List[Tuple[float, float, int, int]],
                  center_x: float, center_y: float) -> None:
        """Draw the dots and star lines using structured coordinates."""
        layer_colors = {
            0: QColor(255, 0, 0),      # Red for center
            1: QColor(0, 0, 255),      # Blue
            2: QColor(0, 180, 0),      # Green
            3: QColor(255, 165, 0),    # Orange
            4: QColor(128, 0, 128),    # Purple
            5: QColor(0, 128, 128),    # Teal
            6: QColor(255, 192, 203),  # Pink
            7: QColor(165, 42, 42),    # Brown
            8: QColor(64, 224, 208),   # Turquoise
            9: QColor(255, 215, 0)     # Gold
        }
        scale_factor = 30.0 * self.zoom_level
        # Use the new structure
        all_coords = coordinates
        layers = []
        # Draw star lines if enabled
        if self.show_star_lines:
            for layer_info in layers:
                outer_vertices = layer_info['outer_vertices']
                layer = layer_info['layer']
                if len(outer_vertices) >= 3:
                    # Determine line color
                    if self.show_layers:
                        color = layer_colors.get(layer, QColor.fromHsv((layer * 30) % 360, 200, 220))
                    else:
                        color = QColor(0, 120, 215)
                    color.setAlpha(150)
                    painter.setPen(QPen(color, 1.5))
                    # Draw classic star polygon
                    num_points = len(outer_vertices)
                    # Determine skip value (same as calculator)
                    if num_points == 5:
                        skip = 2
                    elif num_points == 6:
                        skip = 2
                    elif num_points == 7:
                        skip = 3
                    elif num_points == 8:
                        skip = 3
                    elif num_points == 9:
                        skip = 4
                    elif num_points == 10:
                        skip = 3
                    elif num_points == 11:
                        skip = 5
                    elif num_points == 12:
                        skip = 5
                    else:
                        skip = num_points // 2
                        if skip % 2 == 0 and num_points % 2 == 0:
                            skip = skip - 1
                    # Convert to screen coordinates
                    screen_verts = [
                        (center_x + x * scale_factor, center_y + y * scale_factor)
                        for (x, y, _, _) in outer_vertices
                    ]
                    # Draw the star
                    path = QPainterPath()
                    idx = 0
                    path.moveTo(*screen_verts[idx])
                    for _ in range(num_points):
                        idx = (idx + skip) % num_points
                        path.lineTo(*screen_verts[idx])
                    path.lineTo(*screen_verts[0])
                    painter.drawPath(path)
        # Draw all dots as before
        is_large_star = self.performance_mode and len(all_coords) > 500
        # Only use coordinates with 4 elements
        sorted_coordinates = [coord for coord in all_coords if isinstance(coord, (list, tuple)) and len(coord) == 4]
        sorted_coordinates = sorted(sorted_coordinates, key=lambda coord: coord[2])
        if is_large_star:
            coords_by_layer = {}
            for x, y, layer, dot_number in sorted_coordinates:
                if layer not in coords_by_layer:
                    coords_by_layer[layer] = []
                screen_x = center_x + x * scale_factor
                screen_y = center_y + y * scale_factor
                coords_by_layer[layer].append((screen_x, screen_y, dot_number))
            for layer, points in coords_by_layer.items():
                if self.show_layers:
                    color = layer_colors.get(layer, QColor.fromHsv((layer * 30) % 360, 200, 220))
                else:
                    color = QColor(0, 120, 215)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(color))
                for screen_x, screen_y, dot_number in points:
                    painter.drawEllipse(QPointF(screen_x, screen_y), self.dot_size / 2, self.dot_size / 2)
                painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                if self.show_dot_numbers and len(points) < 100:
                    for screen_x, screen_y, dot_number in points:
                        painter.drawEllipse(QPointF(screen_x, screen_y), self.dot_size / 2, self.dot_size / 2)
                        self._draw_dot_number(painter, dot_number, screen_x, screen_y, QColor(0, 0, 0))
                else:
                    for screen_x, screen_y, dot_number in points:
                        painter.drawEllipse(QPointF(screen_x, screen_y), self.dot_size / 2, self.dot_size / 2)
        else:
            for x, y, layer, dot_number in sorted_coordinates:
                screen_x = center_x + x * scale_factor
                screen_y = center_y + y * scale_factor
                if self.show_layers:
                    color = layer_colors.get(layer, QColor.fromHsv((layer * 30) % 360, 200, 220))
                else:
                    color = QColor(0, 120, 215)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(color))
                painter.drawEllipse(QPointF(screen_x, screen_y), self.dot_size / 2, self.dot_size / 2)
                painter.setPen(QPen(QColor(0, 0, 0, 100), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawEllipse(QPointF(screen_x, screen_y), self.dot_size / 2, self.dot_size / 2)
                if self.show_dot_numbers:
                    self._draw_dot_number(painter, dot_number, screen_x, screen_y, QColor(0, 0, 0))

    def _draw_dot_number(self, painter: QPainter, number: int, x: float, y: float,
                        color: QColor) -> None:
        """Draw a number on a dot.

        Args:
            painter: QPainter object
            number: Number to draw
            x: X-coordinate
            y: Y-coordinate
            color: Text color
        """
        # Set text properties
        painter.setPen(color)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)

        # Draw the number
        painter.drawText(
            int(x - self.dot_size),
            int(y - self.dot_size),
            int(self.dot_size * 2),
            int(self.dot_size * 2),
            Qt.AlignmentFlag.AlignCenter,
            str(number)
        )

    def mousePressEvent(self, event):
        """Handle mouse press events for panning.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.position()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events for panning.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def mouseMoveEvent(self, event):
        """Handle mouse move events for panning.

        Args:
            event: Mouse event
        """
        if self.dragging and self.last_mouse_pos:
            delta = event.position() - self.last_mouse_pos
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.last_mouse_pos = event.position()
            self.update()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming.

        Args:
            event: Wheel event
        """
        # Get the amount of scrolling
        delta = event.angleDelta().y()

        # Adjust zoom level
        if delta > 0:
            self.zoom_level *= 1.1  # Zoom in
        else:
            self.zoom_level /= 1.1  # Zoom out

        # Limit zoom level
        self.zoom_level = max(0.1, min(10.0, self.zoom_level))

        self.update()
