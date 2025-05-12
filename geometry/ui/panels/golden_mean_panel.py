"""Golden Mean panel module.

This module provides a UI panel for exploring the Golden Mean.
"""

import math
from typing import List, Tuple

from loguru import logger
from PyQt6.QtCore import QLineF, QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from geometry.services.golden_mean_service import GoldenMeanService


class GoldenMeanDrawingArea(QWidget):
    """A widget for drawing Golden Mean visualizations."""

    def __init__(self, parent=None):
        """Initialize the drawing area.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: white;")

        # Get the Golden Mean service
        self.service = GoldenMeanService.get_instance()

        # Visualization parameters
        self.visualization_type = "rectangle"  # Default visualization
        self.show_labels = True
        self.show_measurements = True
        self.show_grid = False
        self.zoom_level = 1.0
        self.precision = 4  # Decimal places for displayed values
        self.animation_speed = 50  # Animation speed (ms)

        # Animation parameters
        self.animation_active = False
        self.animation_frame = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)

    def set_visualization_type(self, viz_type: str) -> None:
        """Set the visualization type.

        Args:
            viz_type: Type of visualization to display
        """
        self.visualization_type = viz_type
        self.update()

    def toggle_labels(self, show: bool) -> None:
        """Toggle display of labels.

        Args:
            show: Whether to show labels
        """
        self.show_labels = show
        self.update()

    def toggle_measurements(self, show: bool) -> None:
        """Toggle display of measurements.

        Args:
            show: Whether to show measurements
        """
        self.show_measurements = show
        self.update()

    def toggle_grid(self, show: bool) -> None:
        """Toggle display of grid.

        Args:
            show: Whether to show grid
        """
        self.show_grid = show
        self.update()

    def set_zoom(self, zoom: float) -> None:
        """Set the zoom level.

        Args:
            zoom: Zoom level
        """
        self.zoom_level = zoom
        self.update()

    def set_precision(self, precision: int) -> None:
        """Set the precision for measurements.

        Args:
            precision: Number of decimal places
        """
        self.precision = precision
        self.update()

    def toggle_animation(self, active: bool) -> None:
        """Toggle animation.

        Args:
            active: Whether animation should be active
        """
        self.animation_active = active

        if active:
            self.animation_timer.start(self.animation_speed)
        else:
            self.animation_timer.stop()
            self.animation_frame = 0
            self.update()

    def set_animation_speed(self, speed: int) -> None:
        """Set animation speed.

        Args:
            speed: Animation speed in milliseconds
        """
        self.animation_speed = speed
        if self.animation_active:
            self.animation_timer.setInterval(speed)

    def update_animation(self) -> None:
        """Update the animation frame."""
        self.animation_frame += 1
        if self.animation_frame >= 360:
            self.animation_frame = 0
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the visualization.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Apply zoom
        painter.scale(self.zoom_level, self.zoom_level)

        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(painter)

        # Dispatch to the appropriate drawing method based on visualization type
        if self.visualization_type == "rectangle":
            self._draw_golden_rectangle(painter)
        elif self.visualization_type == "spiral":
            self._draw_golden_spiral(painter)
        elif self.visualization_type == "fibonacci":
            self._draw_fibonacci_squares(painter)
        elif self.visualization_type == "pentagram":
            self._draw_pentagram(painter)
        elif self.visualization_type == "triangle":
            self._draw_golden_triangle(painter)
        elif self.visualization_type == "ratio":
            self._draw_golden_ratio_line(painter)
        elif self.visualization_type == "trisection":
            self._draw_golden_trisection(painter)
        elif self.visualization_type == "all":
            self._draw_combined_visualization(painter)

    def _draw_grid(self, painter: QPainter) -> None:
        """Draw a grid on the drawing area.

        Args:
            painter: QPainter object
        """
        width = self.width() / self.zoom_level
        height = self.height() / self.zoom_level

        # Set grid color and pen
        grid_pen = QPen(QColor(200, 200, 200), 0.5)
        painter.setPen(grid_pen)

        # Draw horizontal grid lines
        for y in range(0, int(height), 20):
            painter.drawLine(QLineF(0, y, width, y))

        # Draw vertical grid lines
        for x in range(0, int(width), 20):
            painter.drawLine(QLineF(x, 0, x, height))

    def _draw_golden_rectangle(self, painter: QPainter) -> None:
        """Draw a golden rectangle visualization.

        Args:
            painter: QPainter object
        """
        width = min(self.width(), self.height()) * 0.8 / self.zoom_level
        height = width / self.service.get_phi()

        # Center the rectangle
        center_x = self.width() / (2 * self.zoom_level)
        center_y = self.height() / (2 * self.zoom_level)
        rect_x = center_x - width / 2
        rect_y = center_y - height / 2

        # Draw the rectangle
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(QRectF(rect_x, rect_y, width, height))

        # Draw the square within the rectangle
        painter.setPen(QPen(QColor(0, 100, 200), 1.5))
        painter.drawRect(QRectF(rect_x, rect_y, height, height))

        # Draw the remaining smaller golden rectangle
        painter.setPen(QPen(QColor(200, 0, 100), 1.5))
        painter.drawRect(QRectF(rect_x + height, rect_y, width - height, height))

        # Draw arcs to show the golden spiral
        if self.animation_active:
            self._draw_animated_golden_spiral(painter, rect_x, rect_y, width, height)

        # Draw labels if enabled
        if self.show_labels:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.black)

            # Label the original rectangle
            painter.drawText(
                QPointF(rect_x + width / 2 - 40, rect_y - 5), "Golden Rectangle"
            )

            # Label the square
            painter.setPen(QColor(0, 100, 200))
            painter.drawText(
                QPointF(rect_x + height / 2 - 20, rect_y + height / 2), "1"
            )

            # Label the remaining rectangle
            painter.setPen(QColor(200, 0, 100))
            painter.drawText(
                QPointF(
                    rect_x + height + (width - height) / 2 - 20, rect_y + height / 2
                ),
                "1/φ",
            )

        # Show measurements if enabled
        if self.show_measurements:
            painter.setFont(QFont("Arial", 8))
            painter.setPen(Qt.GlobalColor.black)

            phi_formatted = f"{self.service.get_phi():.{self.precision}f}"
            phi_inv_formatted = f"{self.service.get_phi_inverse():.{self.precision}f}"

            # Width measurement
            painter.drawText(
                QPointF(rect_x + width / 2 - 30, rect_y + height + 15),
                f"Width = {phi_formatted}",
            )

            # Height measurement
            painter.drawText(QPointF(rect_x - 50, rect_y + height / 2), "Height = 1")

            # Square and remaining rectangle measurements
            painter.setPen(QColor(0, 100, 200))
            painter.drawText(
                QPointF(rect_x + height / 2 - 30, rect_y + height + 30), "1 × 1"
            )

            painter.setPen(QColor(200, 0, 100))
            painter.drawText(
                QPointF(
                    rect_x + height + (width - height) / 2 - 40, rect_y + height + 30
                ),
                f"{phi_inv_formatted} × 1",
            )

    def _draw_animated_golden_spiral(
        self,
        painter: QPainter,
        rect_x: float,
        rect_y: float,
        width: float,
        height: float,
    ) -> None:
        """Draw an animated golden spiral within the golden rectangle.

        Args:
            painter: QPainter object
            rect_x: X coordinate of the rectangle
            rect_y: Y coordinate of the rectangle
            width: Width of the rectangle
            height: Height of the rectangle
        """
        # Animation progress (0 to 1)
        progress = min(1.0, self.animation_frame / 180)

        # Starting points for the spiral
        squares = []

        # First square (largest)
        current_x = rect_x
        current_y = rect_y
        current_size = height
        squares.append((current_x, current_y, current_size))

        # Calculate subsequent squares
        size_ratio = 1.0 / self.service.get_phi()
        for i in range(6):  # Limit to 6 iterations
            next_size = current_size * size_ratio

            if i % 4 == 0:  # Right side
                next_x = current_x + current_size
                next_y = current_y
            elif i % 4 == 1:  # Bottom side
                next_x = current_x + current_size - next_size
                next_y = current_y + current_size
            elif i % 4 == 2:  # Left side
                next_x = current_x - next_size
                next_y = current_y + current_size - next_size
            else:  # Top side
                next_x = current_x
                next_y = current_y - next_size

            current_x = next_x
            current_y = next_y
            current_size = next_size
            squares.append((current_x, current_y, current_size))

        # Draw spiral arcs
        painter.setPen(QPen(QColor(0, 150, 0), 2))
        path = QPainterPath()

        # Start at the inner corner of the first square
        start_x = rect_x + height
        start_y = rect_y
        path.moveTo(start_x, start_y)

        # Draw arcs for each square up to the current animation progress
        num_arcs = min(int(progress * len(squares)), len(squares))
        for i in range(num_arcs):
            x, y, size = squares[i]
            if i % 4 == 0:  # Start from top-right, go to bottom-right
                path.arcTo(QRectF(x, y, size, size), 90, 90)
            elif i % 4 == 1:  # Start from bottom-right, go to bottom-left
                path.arcTo(QRectF(x, y, size, size), 0, 90)
            elif i % 4 == 2:  # Start from bottom-left, go to top-left
                path.arcTo(QRectF(x, y, size, size), 270, 90)
            else:  # Start from top-left, go to top-right
                path.arcTo(QRectF(x, y, size, size), 180, 90)

        painter.drawPath(path)

    def _draw_golden_spiral(self, painter: QPainter) -> None:
        """Draw a golden spiral visualization.

        Args:
            painter: QPainter object
        """
        # Base size for the spiral
        base_size = min(self.width(), self.height()) * 0.8 / self.zoom_level

        # Center point
        center_x = self.width() / (2 * self.zoom_level)
        center_y = self.height() / (2 * self.zoom_level)

        # Draw the spiral using logarithmic spiral formula r = a * e^(b*theta)
        # where b = ln(phi)/(pi/2)
        a = 5  # Starting radius
        b = math.log(self.service.get_phi()) / (math.pi / 2)

        # Draw spiral path
        path = QPainterPath()
        first_point = True

        # Animation progress for spiral drawing
        max_angle = 8 * math.pi  # 4 full turns
        if self.animation_active:
            current_angle = max_angle * (self.animation_frame / 360)
        else:
            current_angle = max_angle

        # Calculate points along the spiral
        for angle in [i * 0.05 for i in range(int(current_angle / 0.05) + 1)]:
            r = a * math.exp(b * angle)
            x = center_x + r * math.cos(angle)
            y = center_y + r * math.sin(angle)

            if first_point:
                path.moveTo(x, y)
                first_point = False
            else:
                path.lineTo(x, y)

        # Draw the spiral
        painter.setPen(QPen(QColor(0, 150, 0), 2))
        painter.drawPath(path)

        # Draw labels if enabled
        if self.show_labels:
            painter.setFont(QFont("Arial", 12))
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(
                QPointF(center_x - 60, center_y - base_size / 2 - 20), "Golden Spiral"
            )

        # Show measurements if enabled
        if self.show_measurements:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.black)

            phi_formatted = f"{self.service.get_phi():.{self.precision}f}"

            painter.drawText(
                QPointF(center_x - base_size / 2, center_y + base_size / 2 + 20),
                f"φ = {phi_formatted}",
            )

    def _draw_fibonacci_squares(self, painter: QPainter) -> None:
        """Draw Fibonacci squares visualization.

        Args:
            painter: QPainter object
        """
        # Get Fibonacci numbers
        fib = self.service.get_fibonacci_sequence(10)[1:]  # Skip first 0

        # Scale factor to fit the drawing area
        max_fib = fib[-1] + fib[-2]
        scale = min(self.width(), self.height()) * 0.8 / (max_fib * self.zoom_level)

        # Center point
        center_x = self.width() / (2 * self.zoom_level)
        center_y = self.height() / (2 * self.zoom_level)

        # Starting position (bottom-left of the layout)
        start_x = center_x - (fib[-1] * scale) / 2
        start_y = center_y + (fib[-1] * scale) / 2

        # Colors for the squares
        colors = [
            QColor(255, 100, 100),  # Red
            QColor(100, 255, 100),  # Green
            QColor(100, 100, 255),  # Blue
            QColor(255, 255, 100),  # Yellow
            QColor(255, 100, 255),  # Purple
            QColor(100, 255, 255),  # Cyan
        ]

        # Track current position and orientation
        current_x = start_x
        current_y = start_y
        direction = 0  # 0: up, 1: left, 2: down, 3: right

        # Draw squares
        squares = []
        for i, num in enumerate(reversed(fib)):
            size = num * scale

            # Determine position based on direction
            if direction == 0:  # Up
                current_y -= size
            elif direction == 1:  # Left
                current_x -= size
            elif direction == 2:  # Down
                current_y += size
            elif direction == 3:  # Right
                current_x += size

            # Store square for spiral drawing
            squares.append((current_x, current_y, size))

            # Draw the square
            color = colors[i % len(colors)]
            painter.setBrush(QBrush(color.lighter(150)))
            painter.setPen(QPen(color.darker(120), 2))
            painter.drawRect(QRectF(current_x, current_y, size, size))

            # Draw the Fibonacci number
            if self.show_labels and size > 20:
                painter.setFont(QFont("Arial", int(size / 10)))
                painter.setPen(Qt.GlobalColor.black)
                painter.drawText(
                    QPointF(
                        current_x + size / 2 - int(size / 10) * len(str(num)) / 2,
                        current_y + size / 2 + int(size / 20),
                    ),
                    str(num),
                )

            # Update direction for next square
            direction = (direction + 1) % 4

        # Draw the spiral if animation is active
        if self.animation_active:
            self._draw_fibonacci_spiral(painter, squares)

        # Show title and measurements if enabled
        if self.show_labels:
            painter.setFont(QFont("Arial", 12))
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(
                QPointF(center_x - 80, center_y - (fib[-1] * scale) / 2 - 20),
                "Fibonacci Squares",
            )

        if self.show_measurements:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.black)

            ratio_formatted = f"{fib[-1] / fib[-2]:.{self.precision}f}"
            phi_formatted = f"{self.service.get_phi():.{self.precision}f}"

            painter.drawText(
                QPointF(center_x - 150, center_y + (fib[-1] * scale) / 2 + 30),
                f"Fibonacci Ratio {fib[-1]}/{fib[-2]} = {ratio_formatted} (approx. φ = {phi_formatted})",
            )

    def _draw_fibonacci_spiral(
        self, painter: QPainter, squares: List[Tuple[float, float, float]]
    ) -> None:
        """Draw a spiral through Fibonacci squares.

        Args:
            painter: QPainter object
            squares: List of (x, y, size) tuples for squares
        """
        # Animation progress (0 to 1)
        progress = min(1.0, self.animation_frame / 180)

        # Draw spiral arcs
        painter.setPen(QPen(QColor(0, 150, 0), 2))
        path = QPainterPath()

        # Start at the inner corner of the smallest square
        first_square = squares[-1]
        start_x = first_square[0] + first_square[2]
        start_y = first_square[1] + first_square[2]
        path.moveTo(start_x, start_y)

        # Draw arcs for each square up to the current animation progress
        num_arcs = min(int(progress * len(squares)), len(squares))
        for i in range(num_arcs):
            idx = len(squares) - i - 1
            x, y, size = squares[idx]

            direction = (4 - (i % 4)) % 4

            if direction == 0:  # Bottom-right to bottom-left
                path.arcTo(QRectF(x, y, size, size), 0, 90)
            elif direction == 1:  # Bottom-left to top-left
                path.arcTo(QRectF(x, y, size, size), 90, 90)
            elif direction == 2:  # Top-left to top-right
                path.arcTo(QRectF(x, y, size, size), 180, 90)
            elif direction == 3:  # Top-right to bottom-right
                path.arcTo(QRectF(x, y, size, size), 270, 90)

        painter.drawPath(path)

    def _draw_pentagram(self, painter: QPainter) -> None:
        """Draw a pentagram visualization.

        Args:
            painter: QPainter object
        """
        # Base size for the pentagram
        radius = min(self.width(), self.height()) * 0.4 / self.zoom_level

        # Center point
        center_x = self.width() / (2 * self.zoom_level)
        center_y = self.height() / (2 * self.zoom_level)

        # Calculate pentagon points
        pentagon_points = []
        for i in range(5):
            angle = 2 * math.pi * i / 5 - math.pi / 2  # Starting from top
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            pentagon_points.append(QPointF(x, y))

        # Draw the pentagon
        painter.setPen(QPen(QColor(100, 100, 255), 2))
        for i in range(5):
            painter.drawLine(pentagon_points[i], pentagon_points[(i + 1) % 5])

        # Draw the pentagram
        painter.setPen(QPen(QColor(255, 100, 100), 2))
        for i in range(5):
            painter.drawLine(pentagon_points[i], pentagon_points[(i + 2) % 5])

        # Draw animation if active
        if self.animation_active:
            progress = self.animation_frame / 360

            # Highlight phi relationships
            if progress > 0.3:
                # Calculate key points in the pentagram
                diagonal_length = (
                    pentagon_points[0] - pentagon_points[2]
                ).manhattanLength()
                side_length = (
                    pentagon_points[0] - pentagon_points[1]
                ).manhattanLength()

                # Highlight the diagonal
                painter.setPen(QPen(QColor(0, 200, 0), 3))
                painter.drawLine(pentagon_points[0], pentagon_points[2])

                # Highlight a side
                painter.setPen(QPen(QColor(0, 0, 200), 3))
                painter.drawLine(pentagon_points[0], pentagon_points[1])

        # Draw labels if enabled
        if self.show_labels:
            painter.setFont(QFont("Arial", 12))
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(
                QPointF(center_x - 50, center_y - radius - 20), "Pentagram"
            )

        # Show measurements if enabled
        if self.show_measurements:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.black)

            phi_formatted = f"{self.service.get_phi():.{self.precision}f}"

            # Pentagram contains many golden ratio relationships
            painter.drawText(
                QPointF(center_x - 120, center_y + radius + 20),
                f"Ratio of diagonal to side ≈ φ = {phi_formatted}",
            )

    def _draw_golden_triangle(self, painter: QPainter) -> None:
        """Draw golden triangles visualization.

        Args:
            painter: QPainter object
        """
        # Base size for the triangle
        base = min(self.width(), self.height()) * 0.8 / self.zoom_level

        # Center point
        center_x = self.width() / (2 * self.zoom_level)
        center_y = self.height() / (2 * self.zoom_level)

        # Calculate height of the golden triangle (isosceles with ratio φ)
        # For a golden triangle with base 2 units, the legs are φ units
        height = (
            base * math.sqrt(self.service.get_phi() * self.service.get_phi() - 1) / 2
        )

        # Points of the triangle
        p1 = QPointF(center_x - base / 2, center_y + height / 2)
        p2 = QPointF(center_x + base / 2, center_y + height / 2)
        p3 = QPointF(center_x, center_y - height / 2)

        # Draw the triangle
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        path.lineTo(p1)
        painter.drawPath(path)

        # Calculate and draw the golden gnomon if animation is active
        if self.animation_active:
            progress = min(1.0, self.animation_frame / 120)

            # Calculate point on the left side that divides it in golden ratio
            golden_point = QPointF(
                p1.x() + (p3.x() - p1.x()) * self.service.get_phi_inverse(),
                p1.y() + (p3.y() - p1.y()) * self.service.get_phi_inverse(),
            )

            # Draw the line dividing the triangle
            painter.setPen(QPen(QColor(200, 100, 50), 2))
            painter.drawLine(p2, golden_point)

            # Draw the resulting triangles with different colors
            if progress > 0.5:
                # Draw the golden triangle
                painter.setPen(QPen(QColor(50, 150, 200), 2))
                golden_path = QPainterPath()
                golden_path.moveTo(p3)
                golden_path.lineTo(p2)
                golden_path.lineTo(golden_point)
                golden_path.lineTo(p3)
                painter.drawPath(golden_path)

                # Draw the gnomon triangle
                painter.setPen(QPen(QColor(150, 200, 50), 2))
                gnomon_path = QPainterPath()
                gnomon_path.moveTo(p1)
                gnomon_path.lineTo(p2)
                gnomon_path.lineTo(golden_point)
                gnomon_path.lineTo(p1)
                painter.drawPath(gnomon_path)

        # Draw labels if enabled
        if self.show_labels:
            painter.setFont(QFont("Arial", 12))
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(
                QPointF(center_x - 60, center_y - height / 2 - 20), "Golden Triangle"
            )

            if self.animation_active and self.animation_frame > 180:
                painter.setFont(QFont("Arial", 10))
                painter.setPen(QColor(50, 150, 200))
                painter.drawText(
                    QPointF(center_x, center_y - height / 4), "Golden Triangle"
                )

                painter.setPen(QColor(150, 200, 50))
                painter.drawText(
                    QPointF(center_x - 20, center_y + height / 4), "Gnomon"
                )

        # Show measurements if enabled
        if self.show_measurements:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.black)

            phi_formatted = f"{self.service.get_phi():.{self.precision}f}"

            painter.drawText(
                QPointF(center_x - 100, center_y + height / 2 + 20),
                f"Ratio of leg to base/2 = φ = {phi_formatted}",
            )

    def _draw_golden_ratio_line(self, painter: QPainter) -> None:
        """Draw a line divided by golden ratio.

        Args:
            painter: QPainter object
        """
        # Base length for the line
        length = min(self.width(), self.height()) * 0.8 / self.zoom_level

        # Line position
        start_x = self.width() / (2 * self.zoom_level) - length / 2
        end_x = start_x + length
        y = self.height() / (2 * self.zoom_level)

        # Calculate golden section point
        golden_x = start_x + length * self.service.get_phi_inverse()

        # Draw the line
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(QLineF(start_x, y, end_x, y))

        # Draw division point
        painter.setPen(QPen(QColor(200, 0, 0), 2))
        painter.drawLine(QLineF(golden_x, y - 10, golden_x, y + 10))

        # Draw animation if active
        if self.animation_active:
            progress = min(1.0, self.animation_frame / 120)

            # Draw rectangles with widths in golden ratio
            height = 30
            if progress > 0.3:
                # Draw the major segment rectangle
                major_width = length * self.service.get_phi_inverse()
                major_rect = QRectF(start_x, y - height / 2, major_width, height)
                painter.setBrush(QBrush(QColor(100, 200, 100, 150)))
                painter.setPen(QPen(QColor(0, 150, 0), 2))
                painter.drawRect(major_rect)

                # Draw the minor segment rectangle
                minor_width = length - major_width
                minor_rect = QRectF(golden_x, y - height / 2, minor_width, height)
                painter.setBrush(QBrush(QColor(200, 100, 100, 150)))
                painter.setPen(QPen(QColor(150, 0, 0), 2))
                painter.drawRect(minor_rect)

        # Draw labels if enabled
        if self.show_labels:
            painter.setFont(QFont("Arial", 12))
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(
                QPointF(start_x + length / 2 - 80, y - 40), "Golden Ratio Division"
            )

            painter.setFont(QFont("Arial", 10))
            painter.setPen(QColor(0, 150, 0))
            painter.drawText(
                QPointF(
                    start_x + length * self.service.get_phi_inverse() / 2 - 15, y + 5
                ),
                "Major",
            )

            painter.setPen(QColor(150, 0, 0))
            painter.drawText(
                QPointF(
                    golden_x
                    + (length - length * self.service.get_phi_inverse()) / 2
                    - 15,
                    y + 5,
                ),
                "Minor",
            )

        # Show measurements if enabled
        if self.show_measurements:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.black)

            phi_formatted = f"{self.service.get_phi():.{self.precision}f}"
            phi_inverse_formatted = (
                f"{self.service.get_phi_inverse():.{self.precision}f}"
            )

            painter.drawText(
                QPointF(start_x + length / 2 - 100, y + 50),
                f"Major/Minor = φ = {phi_formatted}, Major/Total = 1/φ = {phi_inverse_formatted}",
            )

    def _draw_golden_trisection(self, painter: QPainter) -> None:
        """Draw a visualization of a golden trisection.

        Args:
            painter: QPainter object
        """
        # Base length for the line
        length = min(self.width(), self.height()) * 0.8 / self.zoom_level

        # Line position
        start_x = self.width() / (2 * self.zoom_level) - length / 2
        end_x = start_x + length
        y = self.height() / (2 * self.zoom_level)

        # Calculate golden trisection points
        trisection = self.service.calculate_golden_trisection(length)
        first_point = start_x + trisection["first_segment"]
        second_point = first_point + trisection["second_segment"]

        # Draw the main line
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(QLineF(start_x, y, end_x, y))

        # Draw division points
        painter.setPen(QPen(QColor(200, 0, 0), 2))
        painter.drawLine(QLineF(first_point, y - 10, first_point, y + 10))

        painter.setPen(QPen(QColor(0, 0, 200), 2))
        painter.drawLine(QLineF(second_point, y - 10, second_point, y + 10))

        # Draw animation if active
        if self.animation_active:
            progress = min(1.0, self.animation_frame / 120)

            # Draw rectangles with heights in golden ratio
            if progress > 0.3:
                # First segment rectangle
                first_width = trisection["first_segment"]
                height1 = 40
                first_rect = QRectF(start_x, y - height1 / 2, first_width, height1)
                painter.setBrush(QBrush(QColor(100, 200, 100, 150)))
                painter.setPen(QPen(QColor(0, 150, 0), 2))
                painter.drawRect(first_rect)

                # Second segment rectangle
                second_width = trisection["second_segment"]
                height2 = height1 * self.service.get_phi_inverse()
                second_rect = QRectF(
                    first_point, y - height2 / 2, second_width, height2
                )
                painter.setBrush(QBrush(QColor(200, 100, 100, 150)))
                painter.setPen(QPen(QColor(150, 0, 0), 2))
                painter.drawRect(second_rect)

                # Third segment rectangle
                third_width = trisection["third_segment"]
                height3 = height2 * self.service.get_phi_inverse()
                third_rect = QRectF(second_point, y - height3 / 2, third_width, height3)
                painter.setBrush(QBrush(QColor(100, 100, 200, 150)))
                painter.setPen(QPen(QColor(0, 0, 150), 2))
                painter.drawRect(third_rect)

        # Draw labels if enabled
        if self.show_labels:
            painter.setFont(QFont("Arial", 12))
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(
                QPointF(start_x + length / 2 - 80, y - 40), "Golden Trisection"
            )

            painter.setFont(QFont("Arial", 10))
            painter.setPen(QColor(0, 150, 0))
            painter.drawText(
                QPointF(start_x + trisection["first_segment"] / 2 - 15, y + 5), "a"
            )

            painter.setPen(QColor(150, 0, 0))
            painter.drawText(
                QPointF(first_point + trisection["second_segment"] / 2 - 15, y + 5), "b"
            )

            painter.setPen(QColor(0, 0, 150))
            painter.drawText(
                QPointF(second_point + trisection["third_segment"] / 2 - 15, y + 5), "c"
            )

        # Show measurements if enabled
        if self.show_measurements:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.black)

            phi = self.service.get_phi()
            phi_formatted = f"{phi:.{self.precision}f}"

            painter.drawText(
                QPointF(start_x + length / 2 - 140, y + 50),
                f"a = {trisection['first_segment']:.{self.precision}f}, "
                f"b = {trisection['second_segment']:.{self.precision}f}, "
                f"c = {trisection['third_segment']:.{self.precision}f}",
            )

            painter.drawText(
                QPointF(start_x + length / 2 - 110, y + 70),
                f"L/a = a/b = b/c ≈ φ = {phi_formatted}",
            )

    def _draw_combined_visualization(self, painter: QPainter) -> None:
        """Draw a combined visualization of golden ratio structures.

        Args:
            painter: QPainter object
        """
        # Simply draw several visualizations in a smaller size
        original_zoom = self.zoom_level

        # Adjust the zoom level to fit multiple visualizations
        self.zoom_level = original_zoom * 2.5

        # Save current visualization type to restore later
        original_viz = self.visualization_type

        # Layouts for the visualizations
        viz_positions = [
            (0.25, 0.25),  # Top-left
            (0.75, 0.25),  # Top-right
            (0.25, 0.75),  # Bottom-left
            (0.75, 0.75),  # Bottom-right
            (0.5, 0.5),  # Center
        ]

        viz_types = ["rectangle", "spiral", "fibonacci", "pentagram", "ratio"]

        # Draw each visualization
        width = self.width() / self.zoom_level
        height = self.height() / self.zoom_level

        for i, (pos_x, pos_y) in enumerate(viz_positions):
            if i < len(viz_types):
                # Save current state
                painter.save()

                # Translate to position
                painter.translate(
                    width * pos_x - width / 4, height * pos_y - height / 4
                )

                # Set visualization type and draw
                self.visualization_type = viz_types[i]

                # Scale down
                painter.scale(0.5, 0.5)

                # Determine which drawing method to call
                if self.visualization_type == "rectangle":
                    self._draw_golden_rectangle(painter)
                elif self.visualization_type == "spiral":
                    self._draw_golden_spiral(painter)
                elif self.visualization_type == "fibonacci":
                    self._draw_fibonacci_squares(painter)
                elif self.visualization_type == "pentagram":
                    self._draw_pentagram(painter)
                elif self.visualization_type == "ratio":
                    self._draw_golden_ratio_line(painter)

                # Restore state
                painter.restore()

        # Restore original settings
        self.visualization_type = original_viz
        self.zoom_level = original_zoom

        # Add title
        painter.setFont(QFont("Arial", 14))
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(QPointF(width / 2 - 100, 20), "Golden Ratio Manifestations")


class GoldenMeanPanel(QWidget):
    """Panel for exploring the Golden Mean."""

    def __init__(self, parent=None):
        """Initialize the Golden Mean panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Get the Golden Mean service
        self.service = GoldenMeanService.get_instance()

        # Initialize UI
        self._init_ui()

        logger.debug("GoldenMeanPanel initialized")

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        main_layout = QHBoxLayout(self)

        # Left side - Controls area
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)

        # Control groups
        self._create_visualization_controls(controls_layout)
        self._create_display_controls(controls_layout)
        self._create_animation_controls(controls_layout)
        self._create_info_section(controls_layout)

        # Add stretch to push controls to the top
        controls_layout.addStretch()

        # Middle section - Drawing area
        self.drawing_area = GoldenMeanDrawingArea(self)

        # Right side - Calculations panel
        calculations_widget = QWidget()
        calculations_layout = QVBoxLayout(calculations_widget)
        self._create_calculations_panel(calculations_layout)

        # Add components to main layout
        main_layout.addWidget(controls_widget, 1)  # 1/4 of width
        main_layout.addWidget(self.drawing_area, 2)  # 2/4 of width
        main_layout.addWidget(calculations_widget, 1)  # 1/4 of width

        # Initialize the calculations panel to match the default visualization (Rectangle)
        self.calc_stack.setCurrentIndex(0)

    def _create_visualization_controls(self, parent_layout: QVBoxLayout) -> None:
        """Create visualization controls section.

        Args:
            parent_layout: Parent layout to add controls to
        """
        group = QGroupBox("Visualization Type")
        layout = QVBoxLayout(group)

        # Visualization type combo
        viz_combo = QComboBox()
        viz_combo.addItems(
            [
                "Golden Rectangle",
                "Golden Spiral",
                "Fibonacci Squares",
                "Pentagram",
                "Golden Triangle",
                "Golden Ratio Line",
                "Combined View",
            ]
        )
        viz_combo.currentIndexChanged.connect(self._handle_viz_change)

        layout.addWidget(viz_combo)
        parent_layout.addWidget(group)

        # Store reference
        self.viz_combo = viz_combo

    def _create_display_controls(self, parent_layout: QVBoxLayout) -> None:
        """Create display controls section.

        Args:
            parent_layout: Parent layout to add controls to
        """
        group = QGroupBox("Display Options")
        layout = QGridLayout(group)

        # Label toggle
        labels_check = QCheckBox("Show Labels")
        labels_check.setChecked(True)
        labels_check.toggled.connect(self._handle_labels_toggle)
        layout.addWidget(labels_check, 0, 0)

        # Measurements toggle
        measurements_check = QCheckBox("Show Measurements")
        measurements_check.setChecked(True)
        measurements_check.toggled.connect(self._handle_measurements_toggle)
        layout.addWidget(measurements_check, 0, 1)

        # Grid toggle
        grid_check = QCheckBox("Show Grid")
        grid_check.setChecked(False)
        grid_check.toggled.connect(self._handle_grid_toggle)
        layout.addWidget(grid_check, 1, 0)

        # Precision control
        precision_label = QLabel("Precision:")
        layout.addWidget(precision_label, 1, 1)

        precision_spin = QSpinBox()
        precision_spin.setRange(1, 10)
        precision_spin.setValue(4)
        precision_spin.valueChanged.connect(self._handle_precision_change)
        layout.addWidget(precision_spin, 1, 2)

        # Zoom control
        zoom_label = QLabel("Zoom:")
        layout.addWidget(zoom_label, 2, 0)

        zoom_slider = QSlider(Qt.Orientation.Horizontal)
        zoom_slider.setRange(50, 300)
        zoom_slider.setValue(100)
        zoom_slider.valueChanged.connect(self._handle_zoom_change)
        layout.addWidget(zoom_slider, 2, 1, 1, 2)

        parent_layout.addWidget(group)

        # Store references
        self.labels_check = labels_check
        self.measurements_check = measurements_check
        self.grid_check = grid_check
        self.precision_spin = precision_spin
        self.zoom_slider = zoom_slider

    def _create_animation_controls(self, parent_layout: QVBoxLayout) -> None:
        """Create animation controls section.

        Args:
            parent_layout: Parent layout to add controls to
        """
        group = QGroupBox("Animation")
        layout = QGridLayout(group)

        # Animation toggle
        animation_check = QCheckBox("Enable Animation")
        animation_check.setChecked(False)
        animation_check.toggled.connect(self._handle_animation_toggle)
        layout.addWidget(animation_check, 0, 0)

        # Animation speed control
        speed_label = QLabel("Speed:")
        layout.addWidget(speed_label, 1, 0)

        speed_slider = QSlider(Qt.Orientation.Horizontal)
        speed_slider.setRange(10, 200)  # Faster to slower (msec)
        speed_slider.setValue(50)  # Default value
        speed_slider.setInvertedAppearance(True)  # Invert so right is faster
        speed_slider.valueChanged.connect(self._handle_speed_change)
        layout.addWidget(speed_slider, 1, 1)

        parent_layout.addWidget(group)

        # Store references
        self.animation_check = animation_check
        self.speed_slider = speed_slider

    def _create_info_section(self, parent_layout: QVBoxLayout) -> None:
        """Create information section.

        Args:
            parent_layout: Parent layout to add info to
        """
        group = QGroupBox("Golden Mean Information")
        layout = QVBoxLayout(group)

        # Scrollable area for information
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)

        # Information labels
        phi_label = QLabel(f"φ (Phi) = {self.service.get_phi():.10f}")
        phi_label.setStyleSheet("font-weight: bold; color: #0077cc;")
        info_layout.addWidget(phi_label)

        phi_inv_label = QLabel(f"1/φ = {self.service.get_phi_inverse():.10f}")
        info_layout.addWidget(phi_inv_label)

        # Description
        description = QLabel(
            "The Golden Ratio (φ or phi) is a special mathematical constant "
            "approximately equal to 1.618034. It appears frequently in geometry, "
            "art, architecture, and natural phenomena. A Golden Rectangle has a "
            "length-to-width ratio of φ."
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin-top: 5px;")
        info_layout.addWidget(description)

        # Formulas
        formulas_label = QLabel("Formulas:")
        formulas_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        info_layout.addWidget(formulas_label)

        formulas = QLabel(
            "φ = (1 + √5)/2 ≈ 1.618034\n" "φ² = φ + 1\n" "1/φ = φ - 1 ≈ 0.618034"
        )
        info_layout.addWidget(formulas)

        # Fibonacci relation
        fib_label = QLabel("Fibonacci Sequence Relation:")
        fib_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        info_layout.addWidget(fib_label)

        fib = self.service.get_fibonacci_sequence(15)
        fib_ratios = [
            f"{fib[i]}/{fib[i-1]} = {fib[i]/fib[i-1]:.6f}" for i in range(5, 15)
        ]
        fib_text = "As n increases, Fib(n+1)/Fib(n) approaches φ:\n"
        fib_text += "\n".join(fib_ratios)

        fib_info = QLabel(fib_text)
        info_layout.addWidget(fib_info)

        # Add stretch to the info layout
        info_layout.addStretch()

        # Set the widget for the scroll area
        scroll.setWidget(info_widget)
        layout.addWidget(scroll)

        parent_layout.addWidget(group)

    def _create_calculations_panel(self, parent_layout: QVBoxLayout) -> None:
        """Create the calculations panel.

        Args:
            parent_layout: Parent layout to add panel to
        """
        # Title
        title_label = QLabel("Golden Mean Calculations")
        title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; margin-bottom: 10px;"
        )
        parent_layout.addWidget(title_label)

        # Create the stacked widget to hold different calculation panels
        self.calc_stack = QStackedWidget()

        # Create specialized calculation panels for each visualization type
        self.rectangle_calc_panel = self._create_rectangle_calculations()
        self.spiral_calc_panel = self._create_spiral_calculations()
        self.fibonacci_calc_panel = self._create_fibonacci_calculations()
        self.pentagram_calc_panel = self._create_pentagram_calculations()
        self.triangle_calc_panel = self._create_triangle_calculations()
        self.ratio_calc_panel = self._create_ratio_calculations()
        self.trisection_calc_panel = self._create_trisection_calculations()
        self.combined_calc_panel = self._create_combined_calculations()

        # Add the panels to the stacked widget
        self.calc_stack.addWidget(self.rectangle_calc_panel)  # index 0
        self.calc_stack.addWidget(self.spiral_calc_panel)  # index 1
        self.calc_stack.addWidget(self.fibonacci_calc_panel)  # index 2
        self.calc_stack.addWidget(self.pentagram_calc_panel)  # index 3
        self.calc_stack.addWidget(self.triangle_calc_panel)  # index 4
        self.calc_stack.addWidget(self.ratio_calc_panel)  # index 5
        self.calc_stack.addWidget(self.trisection_calc_panel)  # index 6
        self.calc_stack.addWidget(self.combined_calc_panel)  # index 7

        # Add the stacked widget to the parent layout
        parent_layout.addWidget(self.calc_stack)

        # Initial calculations
        self._calculate_all()

    def _create_rectangle_calculations(self) -> QScrollArea:
        """Create calculations panel for Golden Rectangle visualization.

        Returns:
            QScrollArea containing the rectangle calculations
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Rectangle dimensions calculator
        rect_group = QGroupBox("Golden Rectangle Calculator")
        rect_layout = QFormLayout(rect_group)

        # Width input field
        self.rect_width_spin = QDoubleSpinBox()
        self.rect_width_spin.setRange(0.1, 10000)
        self.rect_width_spin.setValue(1.618)
        self.rect_width_spin.setSingleStep(0.1)
        self.rect_width_spin.setDecimals(4)
        self.rect_width_spin.valueChanged.connect(self._calculate_width_changed)
        rect_layout.addRow("Width:", self.rect_width_spin)

        # Height input field
        self.rect_height_spin = QDoubleSpinBox()
        self.rect_height_spin.setRange(0.1, 10000)
        self.rect_height_spin.setValue(1.0)
        self.rect_height_spin.setSingleStep(0.1)
        self.rect_height_spin.setDecimals(4)
        self.rect_height_spin.valueChanged.connect(self._calculate_height_changed)
        rect_layout.addRow("Height:", self.rect_height_spin)

        # Golden status indicator
        self.is_golden_rect = QLabel()
        rect_layout.addRow("Is Golden?", self.is_golden_rect)

        # Rectangle properties
        self.rect_ratio = QLineEdit()
        self.rect_ratio.setReadOnly(True)
        rect_layout.addRow("Width/Height Ratio:", self.rect_ratio)

        # Hypotenuse calculation
        self.rect_hypotenuse = QLineEdit()
        self.rect_hypotenuse.setReadOnly(True)
        rect_layout.addRow("Diagonal (Hypotenuse):", self.rect_hypotenuse)

        # Hypotenuse input for calculations
        hypotenuse_layout = QHBoxLayout()
        self.hypotenuse_input = QDoubleSpinBox()
        self.hypotenuse_input.setRange(0.1, 10000)
        self.hypotenuse_input.setValue(1.9)  # Default value
        self.hypotenuse_input.setSingleStep(0.1)
        self.hypotenuse_input.setDecimals(4)
        hypotenuse_layout.addWidget(self.hypotenuse_input)

        calc_hyp_button = QPushButton("Calculate Golden Rectangle")
        calc_hyp_button.clicked.connect(self._calculate_from_hypotenuse)
        hypotenuse_layout.addWidget(calc_hyp_button)
        rect_layout.addRow("Enter Diagonal:", hypotenuse_layout)

        # Other rectangle properties
        self.rect_area = QLineEdit()
        self.rect_area.setReadOnly(True)
        rect_layout.addRow("Area:", self.rect_area)

        self.rect_perimeter = QLineEdit()
        self.rect_perimeter.setReadOnly(True)
        rect_layout.addRow("Perimeter:", self.rect_perimeter)

        # Buttons for preset operations
        buttons_layout = QHBoxLayout()

        make_golden_btn = QPushButton("Make Golden")
        make_golden_btn.clicked.connect(self._make_golden_rectangle)
        buttons_layout.addWidget(make_golden_btn)

        swap_btn = QPushButton("Swap W/H")
        swap_btn.clicked.connect(self._swap_rectangle_dimensions)
        buttons_layout.addWidget(swap_btn)

        rect_layout.addRow("Actions:", buttons_layout)

        layout.addWidget(rect_group)

        # Golden Ratio information
        ratio_info_group = QGroupBox("Golden Rectangle Properties")
        ratio_info_layout = QVBoxLayout(ratio_info_group)

        info_text = (
            "A Golden Rectangle has a width-to-height ratio equal to the Golden Ratio (φ ≈ 1.618).\n\n"
            "Properties:\n"
            "- If you remove a square from a golden rectangle, the remaining rectangle is also golden\n"
            "- This self-similarity allows the creation of the golden spiral\n"
            "- Golden rectangles appear in art, architecture, and design due to their aesthetic appeal"
        )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        ratio_info_layout.addWidget(info_label)

        layout.addWidget(ratio_info_group)
        layout.addStretch()

        scroll.setWidget(panel)
        return scroll

    def _create_spiral_calculations(self) -> QScrollArea:
        """Create calculations panel for Golden Spiral visualization.

        Returns:
            QScrollArea containing the spiral calculations
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Spiral parameters
        spiral_group = QGroupBox("Golden Spiral Parameters")
        spiral_layout = QFormLayout(spiral_group)

        # Starting radius
        self.spiral_radius_spin = QDoubleSpinBox()
        self.spiral_radius_spin.setRange(1, 1000)
        self.spiral_radius_spin.setValue(5)
        self.spiral_radius_spin.setSingleStep(1)
        self.spiral_radius_spin.valueChanged.connect(self._update_spiral_parameters)
        spiral_layout.addRow("Starting radius:", self.spiral_radius_spin)

        # Number of turns
        self.spiral_turns_spin = QDoubleSpinBox()
        self.spiral_turns_spin.setRange(0.25, 10)
        self.spiral_turns_spin.setValue(4)
        self.spiral_turns_spin.setSingleStep(0.25)
        self.spiral_turns_spin.valueChanged.connect(self._update_spiral_parameters)
        spiral_layout.addRow("Number of turns:", self.spiral_turns_spin)

        # Growth factor (phi)
        self.spiral_growth = QLineEdit()
        self.spiral_growth.setReadOnly(True)
        self.spiral_growth.setText(f"{self.service.get_phi():.6f}")
        spiral_layout.addRow("Growth factor (φ):", self.spiral_growth)

        # Formula
        formula_label = QLabel("Formula: r = a × e^(b×θ), where b = ln(φ)/(π/2)")
        formula_label.setStyleSheet("font-style: italic;")
        spiral_layout.addRow("", formula_label)

        # Final radius calculation
        self.spiral_final_radius = QLineEdit()
        self.spiral_final_radius.setReadOnly(True)
        spiral_layout.addRow("Final radius:", self.spiral_final_radius)

        layout.addWidget(spiral_group)

        # Spiral info
        info_group = QGroupBox("Golden Spiral Information")
        info_layout = QVBoxLayout(info_group)

        info_text = (
            "The Golden Spiral is a logarithmic spiral whose growth factor is φ (the Golden Ratio).\n\n"
            "Properties:\n"
            "- It grows by a factor of φ for every quarter turn (90°)\n"
            "- It can be approximated by drawing arcs connecting opposite corners of squares in the Fibonacci tiling\n"
            "- Golden spirals appear in nature, such as in nautilus shells, pine cones, and galaxies"
        )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        layout.addWidget(info_group)
        layout.addStretch()

        # Initialize calculations
        self._update_spiral_parameters()

        scroll.setWidget(panel)
        return scroll

    def _create_fibonacci_calculations(self) -> QScrollArea:
        """Create calculations panel for Fibonacci Squares visualization.

        Returns:
            QScrollArea containing the Fibonacci calculations
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Fibonacci sequence calculator
        fib_group = QGroupBox("Fibonacci Sequence")
        fib_layout = QVBoxLayout(fib_group)

        # Input for number of terms
        fib_input_layout = QHBoxLayout()
        self.fib_n_spin = QSpinBox()
        self.fib_n_spin.setRange(1, 100)
        self.fib_n_spin.setValue(10)
        self.fib_n_spin.valueChanged.connect(self._calculate_fibonacci)
        fib_input_layout.addWidget(QLabel("Calculate up to F"))
        fib_input_layout.addWidget(self.fib_n_spin)
        fib_input_layout.addWidget(QLabel(":"))
        fib_layout.addLayout(fib_input_layout)

        # Display for sequence
        self.fib_result = QTextEdit()
        self.fib_result.setReadOnly(True)
        self.fib_result.setMaximumHeight(100)
        fib_layout.addWidget(self.fib_result)

        # Golden ratio approximation
        self.fib_ratio_result = QLineEdit()
        self.fib_ratio_result.setReadOnly(True)
        fib_layout.addWidget(QLabel("Ratio Fn+1/Fn approaches φ:"))
        fib_layout.addWidget(self.fib_ratio_result)

        # Square sizes
        self.fib_squares_info = QTextEdit()
        self.fib_squares_info.setReadOnly(True)
        self.fib_squares_info.setMaximumHeight(80)
        fib_layout.addWidget(QLabel("Square sizes in visualization:"))
        fib_layout.addWidget(self.fib_squares_info)

        layout.addWidget(fib_group)

        # Lucas sequence
        lucas_group = QGroupBox("Lucas Sequence")
        lucas_layout = QVBoxLayout(lucas_group)

        # Input for number of Lucas terms
        lucas_input_layout = QHBoxLayout()
        self.lucas_n_spin = QSpinBox()
        self.lucas_n_spin.setRange(1, 50)
        self.lucas_n_spin.setValue(10)
        self.lucas_n_spin.valueChanged.connect(self._calculate_lucas)
        lucas_input_layout.addWidget(QLabel("Calculate up to L"))
        lucas_input_layout.addWidget(self.lucas_n_spin)
        lucas_input_layout.addWidget(QLabel(":"))
        lucas_layout.addLayout(lucas_input_layout)

        # Display for Lucas sequence
        self.lucas_result = QTextEdit()
        self.lucas_result.setReadOnly(True)
        self.lucas_result.setMaximumHeight(80)
        lucas_layout.addWidget(self.lucas_result)

        # Lucas sequence ratio
        self.lucas_ratio_result = QLineEdit()
        self.lucas_ratio_result.setReadOnly(True)
        lucas_layout.addWidget(QLabel("Ratio Ln+1/Ln approaches φ:"))
        lucas_layout.addWidget(self.lucas_ratio_result)

        layout.addWidget(lucas_group)

        # Information on Fibonacci and Golden Ratio
        info_group = QGroupBox("Fibonacci & Golden Ratio Connection")
        info_layout = QVBoxLayout(info_group)

        info_text = (
            "The Fibonacci sequence (0, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...) is defined by:\n"
            "F₀ = 0, F₁ = 1, Fₙ = Fₙ₋₁ + Fₙ₋₂ for n > 1\n\n"
            "As n increases, the ratio Fₙ₊₁/Fₙ approaches the Golden Ratio φ ≈ 1.618034.\n\n"
            "The Lucas sequence (2, 1, 3, 4, 7, 11, 18, 29, ...) follows the same recurrence relation\n"
            "but starts with different values: L₀ = 2, L₁ = 1"
        )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        layout.addWidget(info_group)
        layout.addStretch()

        scroll.setWidget(panel)
        return scroll

    def _create_pentagram_calculations(self) -> QScrollArea:
        """Create calculations panel for Pentagram visualization.

        Returns:
            QScrollArea containing the pentagram calculations
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Pentagram parameters
        penta_group = QGroupBox("Pentagram Dimensions")
        penta_layout = QFormLayout(penta_group)

        # Outer radius
        self.penta_radius_spin = QDoubleSpinBox()
        self.penta_radius_spin.setRange(1, 1000)
        self.penta_radius_spin.setValue(100)
        self.penta_radius_spin.setSingleStep(5)
        self.penta_radius_spin.valueChanged.connect(
            self._calculate_pentagram_from_radius
        )
        penta_layout.addRow("Outer radius:", self.penta_radius_spin)

        # Side length
        self.penta_side_spin = QDoubleSpinBox()
        self.penta_side_spin.setRange(0.1, 1000)
        self.penta_side_spin.setValue(58.7785)  # Initial value for radius 100
        self.penta_side_spin.setSingleStep(1)
        self.penta_side_spin.setDecimals(4)
        self.penta_side_spin.valueChanged.connect(self._calculate_pentagram_from_side)
        penta_layout.addRow("Pentagon side length:", self.penta_side_spin)

        # Diagonal length
        self.penta_diagonal_spin = QDoubleSpinBox()
        self.penta_diagonal_spin.setRange(0.1, 1000)
        self.penta_diagonal_spin.setValue(95.1057)  # Initial value for radius 100
        self.penta_diagonal_spin.setSingleStep(1)
        self.penta_diagonal_spin.setDecimals(4)
        self.penta_diagonal_spin.valueChanged.connect(
            self._calculate_pentagram_from_diagonal
        )
        penta_layout.addRow("Pentagon diagonal:", self.penta_diagonal_spin)

        # Ratio of diagonal to side
        self.penta_ratio = QLineEdit()
        self.penta_ratio.setReadOnly(True)
        penta_layout.addRow("Diagonal/Side Ratio:", self.penta_ratio)

        # Pentagram inner radius
        self.penta_inner_radius = QLineEdit()
        self.penta_inner_radius.setReadOnly(True)
        penta_layout.addRow("Inner radius:", self.penta_inner_radius)

        layout.addWidget(penta_group)

        # Pentagram info
        info_group = QGroupBox("Pentagram & Golden Ratio")
        info_layout = QVBoxLayout(info_group)

        info_text = (
            "The regular pentagram contains numerous instances of the Golden Ratio:\n\n"
            "- The ratio of a diagonal to a side of a regular pentagon is exactly φ\n"
            "- Each intersection of line segments creates a perfect Golden Triangle\n"
            "- A smaller pentagram within can be drawn by connecting the points of intersection\n"
            "- This self-similarity creates an infinite sequence of nested pentagrams\n\n"
            "The pentagram has been used as a symbol for mathematical perfection throughout history."
        )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        layout.addWidget(info_group)
        layout.addStretch()

        # Initialize calculations
        self._calculate_pentagram()

        scroll.setWidget(panel)
        return scroll

    def _create_triangle_calculations(self) -> QScrollArea:
        """Create calculations panel for Golden Triangle visualization.

        Returns:
            QScrollArea containing the triangle calculations
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Triangle parameters
        triangle_group = QGroupBox("Golden Triangle Calculator")
        triangle_layout = QFormLayout(triangle_group)

        # Base width
        self.triangle_base_spin = QDoubleSpinBox()
        self.triangle_base_spin.setRange(0.1, 1000)
        self.triangle_base_spin.setValue(100)
        self.triangle_base_spin.setSingleStep(5)
        self.triangle_base_spin.valueChanged.connect(self._calculate_triangle)
        triangle_layout.addRow("Base width:", self.triangle_base_spin)

        # Leg length
        self.triangle_leg = QLineEdit()
        self.triangle_leg.setReadOnly(True)
        triangle_layout.addRow("Leg length:", self.triangle_leg)

        # Height
        self.triangle_height = QLineEdit()
        self.triangle_height.setReadOnly(True)
        triangle_layout.addRow("Height:", self.triangle_height)

        # Area
        self.triangle_area = QLineEdit()
        self.triangle_area.setReadOnly(True)
        triangle_layout.addRow("Area:", self.triangle_area)

        # Division point (for golden gnomon)
        self.triangle_division = QLineEdit()
        self.triangle_division.setReadOnly(True)
        triangle_layout.addRow("Division point (1/φ):", self.triangle_division)

        layout.addWidget(triangle_group)

        # Golden triangle info
        info_group = QGroupBox("Golden Triangle Properties")
        info_layout = QVBoxLayout(info_group)

        info_text = (
            "A Golden Triangle is an isosceles triangle where the ratio of a leg to the base is φ:1.\n\n"
            "Properties:\n"
            "- Dividing a golden triangle by drawing a line from the apex to a point that divides the base in the golden ratio "
            "creates a new golden triangle and a golden gnomon (another type of golden triangle)\n"
            "- This self-similarity allows for infinite subdivision\n"
            "- Golden triangles appear in pentagrams, dodecahedrons, and icosahedrons\n"
            "- The acute angle in a golden triangle is 36°"
        )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        layout.addWidget(info_group)
        layout.addStretch()

        # Initialize calculations
        self._calculate_triangle()

        scroll.setWidget(panel)
        return scroll

    def _create_ratio_calculations(self) -> QScrollArea:
        """Create calculations panel for Golden Ratio Line visualization.

        Returns:
            QScrollArea containing the ratio line calculations
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Line division calculator
        ratio_group = QGroupBox("Golden Ratio Division")
        ratio_layout = QFormLayout(ratio_group)

        # Total length
        self.line_length_spin = QDoubleSpinBox()
        self.line_length_spin.setRange(1, 10000)
        self.line_length_spin.setValue(100)
        self.line_length_spin.setSingleStep(5)
        self.line_length_spin.valueChanged.connect(self._calculate_line_division)
        ratio_layout.addRow("Total length:", self.line_length_spin)

        # Major segment
        self.line_major = QLineEdit()
        self.line_major.setReadOnly(True)
        ratio_layout.addRow("Major segment (a):", self.line_major)

        # Minor segment
        self.line_minor = QLineEdit()
        self.line_minor.setReadOnly(True)
        ratio_layout.addRow("Minor segment (b):", self.line_minor)

        # Proportions
        self.line_whole_to_major = QLineEdit()
        self.line_whole_to_major.setReadOnly(True)
        ratio_layout.addRow("Total / Major (= φ):", self.line_whole_to_major)

        self.line_major_to_minor = QLineEdit()
        self.line_major_to_minor.setReadOnly(True)
        ratio_layout.addRow("Major / Minor (= φ):", self.line_major_to_minor)

        layout.addWidget(ratio_group)

        # Golden Ratio calculation group
        general_group = QGroupBox("Golden Ratio Calculator")
        general_layout = QFormLayout(general_group)

        # Input fields
        self.value_a_spin = QDoubleSpinBox()
        self.value_a_spin.setRange(0.001, 1000000)
        self.value_a_spin.setDecimals(6)
        self.value_a_spin.setValue(1.0)
        self.value_a_spin.setSingleStep(0.1)
        self.value_a_spin.valueChanged.connect(self._calculate_golden_ratio)
        general_layout.addRow("Value A:", self.value_a_spin)

        self.relation_combo = QComboBox()
        self.relation_combo.addItem("A:B = B:(A+B)", "direct")
        self.relation_combo.addItem("A:B = 1:φ", "basic")
        self.relation_combo.addItem("A:B = φ:1", "inverse")
        self.relation_combo.addItem("A = B × φ", "multiply")
        self.relation_combo.addItem("A = B / φ", "divide")
        self.relation_combo.currentIndexChanged.connect(self._calculate_golden_ratio)
        general_layout.addRow("Relation:", self.relation_combo)

        self.value_b_result = QLineEdit()
        self.value_b_result.setReadOnly(True)
        general_layout.addRow("Value B:", self.value_b_result)

        layout.addWidget(general_group)

        # Info about golden ratio line
        info_group = QGroupBox("Golden Section Properties")
        info_layout = QVBoxLayout(info_group)

        info_text = (
            "A line divided by the Golden Ratio creates a 'Golden Section'.\n\n"
            "In a golden section:\n"
            "- The ratio of the whole line to the larger segment equals the ratio of the larger segment to the smaller segment\n"
            "- This creates the proportion: (a+b):a = a:b = φ\n"
            "- This division was known as the 'divine proportion' in Renaissance art and architecture\n"
            "- It's commonly used in composition to create aesthetically pleasing arrangements"
        )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)

        layout.addWidget(info_group)
        layout.addStretch()

        # Initialize calculations
        self._calculate_line_division()

        scroll.setWidget(panel)
        return scroll

    def _create_trisection_calculations(self) -> QScrollArea:
        """Create calculations panel for Golden Trisection visualization.

        Returns:
            QScrollArea containing the trisection calculations
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Trisection calculator
        trisection_group = QGroupBox("Golden Trisection Calculator")
        trisection_layout = QFormLayout(trisection_group)

        # Total length
        self.trisection_length_spin = QDoubleSpinBox()
        self.trisection_length_spin.setRange(1, 10000)
        self.trisection_length_spin.setValue(100)
        self.trisection_length_spin.setSingleStep(5)
        self.trisection_length_spin.valueChanged.connect(self._calculate_trisection)
        trisection_layout.addRow("Total length:", self.trisection_length_spin)

        # First segment (largest)
        self.trisection_first = QLineEdit()
        self.trisection_first.setReadOnly(True)
        trisection_layout.addRow("First segment (a):", self.trisection_first)

        # Second segment (middle)
        self.trisection_second = QLineEdit()
        self.trisection_second.setReadOnly(True)
        trisection_layout.addRow("Second segment (b):", self.trisection_second)

        # Third segment (smallest)
        self.trisection_third = QLineEdit()
        self.trisection_third.setReadOnly(True)
        trisection_layout.addRow("Third segment (c):", self.trisection_third)

        # Proportions
        self.trisection_ratio_whole_to_first = QLineEdit()
        self.trisection_ratio_whole_to_first.setReadOnly(True)
        trisection_layout.addRow("Total / a:", self.trisection_ratio_whole_to_first)

        self.trisection_ratio_first_to_second = QLineEdit()
        self.trisection_ratio_first_to_second.setReadOnly(True)
        trisection_layout.addRow("a / b:", self.trisection_ratio_first_to_second)

        self.trisection_ratio_second_to_third = QLineEdit()
        self.trisection_ratio_second_to_third.setReadOnly(True)
        trisection_layout.addRow("b / c:", self.trisection_ratio_second_to_third)

        # Calculate from first segment input
        first_segment_layout = QHBoxLayout()
        self.first_segment_input = QDoubleSpinBox()
        self.first_segment_input.setRange(0.1, 10000)
        self.first_segment_input.setValue(61.8)  # Default value approximating phi^2
        self.first_segment_input.setSingleStep(0.1)
        self.first_segment_input.setDecimals(4)
        first_segment_layout.addWidget(self.first_segment_input)

        calc_from_first_button = QPushButton("Calculate From First Segment")
        calc_from_first_button.clicked.connect(self._calculate_from_first_segment)
        first_segment_layout.addWidget(calc_from_first_button)
        trisection_layout.addRow("First segment value:", first_segment_layout)

        layout.addWidget(trisection_group)

        # Golden Trisection information
        trisection_info_group = QGroupBox("Golden Trisection Properties")
        trisection_info_layout = QVBoxLayout(trisection_info_group)

        info_text = (
            "A Golden Trisection divides a line into three segments (a, b, c) where:\n\n"
            "L/a = a/b = b/c = φ (the Golden Ratio)\n\n"
            "Properties:\n"
            "- The three segments are in geometric progression with ratio φ\n"
            "- a = L/(1 + φ⁻¹ + φ⁻²), b = a/φ, c = b/φ\n"
            "- If L = 1, then a ≈ 0.618², b ≈ 0.618³, c ≈ 0.618⁴\n"
            "- This creates a self-similar fractal pattern when applied recursively\n"
            "- The Golden Trisection extends the concept of the Golden Section (which divides a line into two segments)"
        )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        trisection_info_layout.addWidget(info_label)

        layout.addWidget(trisection_info_group)
        layout.addStretch()

        # Initialize calculations
        self._calculate_trisection()

        scroll.setWidget(panel)
        return scroll

    def _create_combined_calculations(self) -> QScrollArea:
        """Create calculations panel for Combined visualization.

        Returns:
            QScrollArea containing the combined view calculations
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Golden Ratio constants
        constants_group = QGroupBox("Golden Ratio Constants")
        constants_layout = QFormLayout(constants_group)

        # Phi value
        phi_value = QLineEdit(f"{self.service.get_phi():.10f}")
        phi_value.setReadOnly(True)
        constants_layout.addRow("φ (phi):", phi_value)

        # Inverse phi
        phi_inv_value = QLineEdit(f"{self.service.get_phi_inverse():.10f}")
        phi_inv_value.setReadOnly(True)
        constants_layout.addRow("1/φ:", phi_inv_value)

        # Phi squared
        phi_squared = QLineEdit(f"{self.service.get_phi() ** 2:.10f}")
        phi_squared.setReadOnly(True)
        constants_layout.addRow("φ²:", phi_squared)

        # Phi formula
        phi_formula = QLineEdit("(1 + √5) / 2")
        phi_formula.setReadOnly(True)
        constants_layout.addRow("Formula:", phi_formula)

        layout.addWidget(constants_group)

        # Golden angles
        angles_group = QGroupBox("Golden Angles")
        angles_layout = QFormLayout(angles_group)

        # Golden angle (in spiral phyllotaxis)
        golden_angle = QLineEdit(
            f"{360 / (self.service.get_phi() ** 2):.6f}° ≈ 137.508°"
        )
        golden_angle.setReadOnly(True)
        angles_layout.addRow("Golden Angle:", golden_angle)

        # Pentagon internal angle
        pentagon_angle = QLineEdit("108°")
        pentagon_angle.setReadOnly(True)
        angles_layout.addRow("Pentagon Internal Angle:", pentagon_angle)

        # Golden triangle acute angle
        triangle_angle = QLineEdit("36°")
        triangle_angle.setReadOnly(True)
        angles_layout.addRow("Golden Triangle Acute Angle:", triangle_angle)

        layout.addWidget(angles_group)

        # Overview of visualizations
        overview_group = QGroupBox("Visualization Overview")
        overview_layout = QVBoxLayout(overview_group)

        overview_text = (
            "The current view shows multiple manifestations of the Golden Ratio:\n\n"
            "• Golden Rectangle: A rectangle with width-to-height ratio of φ:1\n"
            "• Golden Spiral: A logarithmic spiral with growth factor φ\n"
            "• Fibonacci Squares: Squares with sizes following the Fibonacci sequence\n"
            "• Pentagram: Contains golden triangles and golden ratio proportions\n"
            "• Golden Ratio Line: A line divided into the golden ratio (φ:1)\n\n"
            "Select a specific visualization type for more detailed calculations."
        )

        overview_label = QLabel(overview_text)
        overview_label.setWordWrap(True)
        overview_layout.addWidget(overview_label)

        layout.addWidget(overview_group)
        layout.addStretch()

        scroll.setWidget(panel)
        return scroll

    def _calculate_all(self) -> None:
        """Calculate all values based on the current visualization."""
        # Get current visualization type index
        viz_index = self.viz_combo.currentIndex()

        # Call appropriate calculation method
        if viz_index == 0:  # Rectangle
            self._calculate_rectangle()
        elif viz_index == 1:  # Spiral
            self._update_spiral_parameters()
        elif viz_index == 2:  # Fibonacci
            self._calculate_fibonacci()
            self._calculate_lucas()
        elif viz_index == 3:  # Pentagram
            self._calculate_pentagram_from_radius()
        elif viz_index == 4:  # Triangle
            self._calculate_triangle()
        elif viz_index == 5:  # Ratio line
            self._calculate_line_division()
            self._calculate_golden_ratio()
        # For combined view, no specific calculations needed

    def _calculate_golden_ratio(self) -> None:
        """Calculate golden ratio based on inputs."""
        value_a = self.value_a_spin.value()
        relation = self.relation_combo.currentData()

        if relation == "direct":
            # A:B = B:(A+B)
            # B/A = (A+B)/B
            # B^2 = A(A+B)
            # B^2 = A^2 + AB
            # B^2 - AB - A^2 = 0
            # Using quadratic formula: B = (A + sqrt(A^2 + 4A^2))/2
            value_b = (value_a + math.sqrt(value_a**2 + 4 * value_a**2)) / 2
        elif relation == "basic":
            # A:B = 1:φ
            value_b = value_a * self.service.get_phi()
        elif relation == "inverse":
            # A:B = φ:1
            value_b = value_a / self.service.get_phi()
        elif relation == "multiply":
            # A = B × φ
            value_b = value_a / self.service.get_phi()
        elif relation == "divide":
            # A = B / φ
            value_b = value_a * self.service.get_phi()
        else:
            value_b = 0

        self.value_b_result.setText(f"{value_b:.6f}")

    def _calculate_fibonacci(self) -> None:
        """Calculate Fibonacci numbers and ratio."""
        n = self.fib_n_spin.value()
        fib_sequence = self.service.get_fibonacci_sequence(n)

        # Format sequence
        sequence_text = ", ".join([str(num) for num in fib_sequence])
        self.fib_result.setText(sequence_text)

        # Calculate ratio of last two numbers
        if len(fib_sequence) >= 2 and fib_sequence[-2] != 0:
            ratio = fib_sequence[-1] / fib_sequence[-2]
            self.fib_ratio_result.setText(
                f"{ratio:.8f} (φ ≈ {self.service.get_phi():.8f})"
            )
        else:
            self.fib_ratio_result.setText("Need more numbers")

        # Update squares information (if this is for Fibonacci visualization)
        if self.viz_combo.currentIndex() == 2:  # Fibonacci
            # Get a subset of the sequence to display as squares
            display_sequence = (
                fib_sequence[-8:] if len(fib_sequence) > 8 else fib_sequence
            )
            squares_text = "Square sizes: " + ", ".join(
                [str(num) for num in display_sequence if num > 0]
            )
            self.fib_squares_info.setText(squares_text)

    def _calculate_lucas(self) -> None:
        """Calculate Lucas numbers and ratio."""
        n = self.lucas_n_spin.value()
        lucas_sequence = self.service.get_lucas_sequence(n)

        # Format sequence
        sequence_text = ", ".join([str(num) for num in lucas_sequence])
        self.lucas_result.setText(sequence_text)

        # Calculate ratio of last two numbers
        if len(lucas_sequence) >= 2 and lucas_sequence[-2] != 0:
            ratio = lucas_sequence[-1] / lucas_sequence[-2]
            self.lucas_ratio_result.setText(
                f"{ratio:.8f} (φ ≈ {self.service.get_phi():.8f})"
            )
        else:
            self.lucas_ratio_result.setText("Need more numbers")

    def _calculate_rectangle(self) -> None:
        """Calculate rectangle dimensions and check if it's golden."""
        width = self.rect_width_spin.value()
        height = self.rect_height_spin.value()

        # Calculate ratio, area, perimeter and hypotenuse
        ratio = width / height
        area = width * height
        perimeter = 2 * (width + height)
        hypotenuse = math.sqrt(width**2 + height**2)

        # Update display
        self.rect_ratio.setText(f"{ratio:.6f} (φ ≈ {self.service.get_phi():.6f})")
        self.rect_area.setText(f"{area:.4f}")
        self.rect_perimeter.setText(f"{perimeter:.4f}")
        self.rect_hypotenuse.setText(f"{hypotenuse:.4f}")

        # Check if it's a golden rectangle (ratio is approximately φ)
        phi = self.service.get_phi()

        # Allow for small rounding errors (within 1%)
        is_golden = abs(ratio - phi) < 0.016 or abs(1 / ratio - phi) < 0.016

        if is_golden:
            self.is_golden_rect.setText("Yes ✓")
            self.is_golden_rect.setStyleSheet("color: green; font-weight: bold;")
        else:
            diff_direct = abs(ratio - phi)
            diff_inverse = abs(1 / ratio - phi)
            diff = min(diff_direct, diff_inverse)
            self.is_golden_rect.setText(f"No (off by {diff:.4f})")
            self.is_golden_rect.setStyleSheet("color: red;")

    def _calculate_width_changed(self) -> None:
        """Update height when width changes to maintain golden ratio."""
        # Only execute if this function was called directly from the width spinbox
        if self.sender() == self.rect_width_spin:
            width = self.rect_width_spin.value()
            height = width / self.service.get_phi()

            # Update the height without triggering signals
            self.rect_height_spin.blockSignals(True)
            self.rect_height_spin.setValue(height)
            self.rect_height_spin.blockSignals(False)

        # Calculate all rectangle properties
        self._calculate_rectangle()

    def _calculate_height_changed(self) -> None:
        """Update width when height changes to maintain golden ratio."""
        # Only execute if this function was called directly from the height spinbox
        if self.sender() == self.rect_height_spin:
            height = self.rect_height_spin.value()
            width = height * self.service.get_phi()

            # Update the width without triggering signals
            self.rect_width_spin.blockSignals(True)
            self.rect_width_spin.setValue(width)
            self.rect_width_spin.blockSignals(False)

        # Calculate all rectangle properties
        self._calculate_rectangle()

    def _calculate_from_hypotenuse(self) -> None:
        """Calculate golden rectangle dimensions from hypotenuse."""
        diagonal = self.hypotenuse_input.value()

        # For a golden rectangle with width W and height H:
        # If W = φ * H, then diagonal² = W² + H² = (φ*H)² + H² = H² * (φ² + 1)
        # So H = diagonal / sqrt(φ² + 1)
        phi = self.service.get_phi()
        height = diagonal / math.sqrt(phi**2 + 1)
        width = height * phi

        # Update the dimensions without triggering signals
        self.rect_width_spin.blockSignals(True)
        self.rect_height_spin.blockSignals(True)

        self.rect_width_spin.setValue(width)
        self.rect_height_spin.setValue(height)

        self.rect_width_spin.blockSignals(False)
        self.rect_height_spin.blockSignals(False)

        # Calculate all rectangle properties
        self._calculate_rectangle()

    def _make_golden_rectangle(self) -> None:
        """Adjust rectangle dimensions to make it golden."""
        height = self.rect_height_spin.value()
        width = height * self.service.get_phi()

        # Update the width without triggering signals
        self.rect_width_spin.blockSignals(True)
        self.rect_width_spin.setValue(width)
        self.rect_width_spin.blockSignals(False)

        self._calculate_rectangle()

    def _swap_rectangle_dimensions(self) -> None:
        """Swap width and height of the rectangle."""
        width = self.rect_width_spin.value()
        height = self.rect_height_spin.value()

        self.rect_width_spin.blockSignals(True)
        self.rect_height_spin.blockSignals(True)

        self.rect_width_spin.setValue(height)
        self.rect_height_spin.setValue(width)

        self.rect_width_spin.blockSignals(False)
        self.rect_height_spin.blockSignals(False)

        self._calculate_rectangle()

    def _update_spiral_parameters(self) -> None:
        """Update spiral calculations based on input parameters."""
        start_radius = self.spiral_radius_spin.value()
        turns = self.spiral_turns_spin.value()

        # Calculate growth factor (phi)
        phi = self.service.get_phi()

        # Calculate final radius (after specified number of turns)
        # For logarithmic spiral with growth factor φ, radius grows by φ each 90° turn
        # So for n complete turns (each 360°), growth is φ^(4n)
        final_radius = start_radius * (phi ** (4 * turns))
        self.spiral_final_radius.setText(f"{final_radius:.2f}")

    def _calculate_pentagram_from_radius(self) -> None:
        """Calculate pentagram dimensions based on outer radius."""
        # Block signals to prevent circular updates
        self.penta_side_spin.blockSignals(True)
        self.penta_diagonal_spin.blockSignals(True)

        radius = self.penta_radius_spin.value()

        # For a regular pentagon, if R is the outer radius:
        # Side length = 2 * R * sin(π/5)
        side_length = 2 * radius * math.sin(math.pi / 5)

        # Diagonal length = 2 * R * cos(π/10)
        diagonal_length = 2 * radius * math.cos(math.pi / 10)

        # Update the spin box values
        self.penta_side_spin.setValue(side_length)
        self.penta_diagonal_spin.setValue(diagonal_length)

        # Unblock signals
        self.penta_side_spin.blockSignals(False)
        self.penta_diagonal_spin.blockSignals(False)

        # Calculate and update the remaining values
        self._update_pentagram_calculations(radius, side_length, diagonal_length)

    def _calculate_pentagram_from_side(self) -> None:
        """Calculate pentagram dimensions based on side length."""
        # Only execute if this function was called directly from the side length spinbox
        if self.sender() == self.penta_side_spin:
            # Block signals to prevent circular updates
            self.penta_radius_spin.blockSignals(True)
            self.penta_diagonal_spin.blockSignals(True)

            side_length = self.penta_side_spin.value()

            # Calculate radius from side length
            # R = side_length / (2 * sin(π/5))
            radius = side_length / (2 * math.sin(math.pi / 5))

            # Calculate diagonal from radius
            # diagonal = 2 * R * cos(π/10)
            diagonal_length = 2 * radius * math.cos(math.pi / 10)

            # Update the spin box values
            self.penta_radius_spin.setValue(radius)
            self.penta_diagonal_spin.setValue(diagonal_length)

            # Unblock signals
            self.penta_radius_spin.blockSignals(False)
            self.penta_diagonal_spin.blockSignals(False)

            # Calculate and update the remaining values
            self._update_pentagram_calculations(radius, side_length, diagonal_length)

    def _calculate_pentagram_from_diagonal(self) -> None:
        """Calculate pentagram dimensions based on diagonal length."""
        # Only execute if this function was called directly from the diagonal spinbox
        if self.sender() == self.penta_diagonal_spin:
            # Block signals to prevent circular updates
            self.penta_radius_spin.blockSignals(True)
            self.penta_side_spin.blockSignals(True)

            diagonal_length = self.penta_diagonal_spin.value()

            # Calculate radius from diagonal length
            # R = diagonal_length / (2 * cos(π/10))
            radius = diagonal_length / (2 * math.cos(math.pi / 10))

            # Calculate side length from radius
            # side = 2 * R * sin(π/5)
            side_length = 2 * radius * math.sin(math.pi / 5)

            # Update the spin box values
            self.penta_radius_spin.setValue(radius)
            self.penta_side_spin.setValue(side_length)

            # Unblock signals
            self.penta_radius_spin.blockSignals(False)
            self.penta_side_spin.blockSignals(False)

            # Calculate and update the remaining values
            self._update_pentagram_calculations(radius, side_length, diagonal_length)

    def _update_pentagram_calculations(
        self, radius: float, side_length: float, diagonal_length: float
    ) -> None:
        """Update all pentagram calculations based on given dimensions."""
        # Ratio of diagonal to side (should equal φ)
        ratio = diagonal_length / side_length

        # Inner radius (radius of inscribed circle)
        inner_radius = radius * math.cos(math.pi / 5)

        # Update display
        self.penta_ratio.setText(f"{ratio:.6f} (φ ≈ {self.service.get_phi():.6f})")
        self.penta_inner_radius.setText(f"{inner_radius:.4f}")

    def _calculate_pentagram(self) -> None:
        """Calculate pentagram dimensions - used for backward compatibility."""
        self._calculate_pentagram_from_radius()

    def _calculate_triangle(self) -> None:
        """Calculate golden triangle dimensions based on base width."""
        base = self.triangle_base_spin.value()
        phi = self.service.get_phi()

        # For golden triangle, if base = 2 units, legs = φ units
        # Scale accordingly for our base
        leg_length = base * phi / 2

        # Calculate height using Pythagorean theorem
        # For an isosceles triangle with base b and leg length l
        # h² = l² - (b/2)²
        height = math.sqrt(leg_length**2 - (base / 2) ** 2)

        # Calculate area: A = (b * h) / 2
        area = (base * height) / 2

        # Division point for golden gnomon
        # Division point = φ inverse = 1/φ = φ - 1
        division_point = base * self.service.get_phi_inverse()

        # Update display
        self.triangle_leg.setText(f"{leg_length:.4f}")
        self.triangle_height.setText(f"{height:.4f}")
        self.triangle_area.setText(f"{area:.4f}")
        self.triangle_division.setText(f"{division_point:.4f}")

    def _calculate_line_division(self) -> None:
        """Calculate golden section division of a line."""
        total_length = self.line_length_spin.value()
        phi = self.service.get_phi()

        # Calculate segments in golden ratio
        # a:b = (a+b):a = φ
        # If a+b = total_length, then a = total_length * φ⁻¹
        major_segment = total_length * self.service.get_phi_inverse()
        minor_segment = total_length - major_segment

        # Calculate ratios
        whole_to_major = total_length / major_segment
        major_to_minor = major_segment / minor_segment

        # Update display
        self.line_major.setText(f"{major_segment:.6f}")
        self.line_minor.setText(f"{minor_segment:.6f}")
        self.line_whole_to_major.setText(f"{whole_to_major:.6f} (φ ≈ {phi:.6f})")
        self.line_major_to_minor.setText(f"{major_to_minor:.6f} (φ ≈ {phi:.6f})")

    def _calculate_trisection(self) -> None:
        """Calculate golden trisection of a line."""
        total_length = self.trisection_length_spin.value()
        phi = self.service.get_phi()

        # Use the service to calculate the trisection
        trisection = self.service.calculate_golden_trisection(total_length)

        # Extract values
        first_segment = trisection["first_segment"]
        second_segment = trisection["second_segment"]
        third_segment = trisection["third_segment"]

        # Calculate ratios
        ratio_whole_to_first = total_length / first_segment
        ratio_first_to_second = first_segment / second_segment
        ratio_second_to_third = second_segment / third_segment

        # Update display
        self.trisection_first.setText(f"{first_segment:.6f}")
        self.trisection_second.setText(f"{second_segment:.6f}")
        self.trisection_third.setText(f"{third_segment:.6f}")
        self.trisection_ratio_whole_to_first.setText(
            f"{ratio_whole_to_first:.6f} (φ ≈ {phi:.6f})"
        )
        self.trisection_ratio_first_to_second.setText(
            f"{ratio_first_to_second:.6f} (φ ≈ {phi:.6f})"
        )
        self.trisection_ratio_second_to_third.setText(
            f"{ratio_second_to_third:.6f} (φ ≈ {phi:.6f})"
        )

    def _calculate_from_first_segment(self) -> None:
        """Calculate golden trisection based on the first segment value."""
        first_segment = self.first_segment_input.value()
        phi = self.service.get_phi()

        # Calculate remaining segments
        second_segment = first_segment / phi
        third_segment = second_segment / phi
        total_length = first_segment + second_segment + third_segment

        # Update the length input without triggering calculations
        self.trisection_length_spin.blockSignals(True)
        self.trisection_length_spin.setValue(total_length)
        self.trisection_length_spin.blockSignals(False)

        # Calculate and update all values
        self._calculate_trisection()

    def _handle_viz_change(self, index: int) -> None:
        """Handle visualization type change.

        Args:
            index: Index of the selected visualization
        """
        viz_map = {
            0: "rectangle",
            1: "spiral",
            2: "fibonacci",
            3: "pentagram",
            4: "triangle",
            5: "ratio",
            6: "all",
        }

        # Update drawing area
        self.drawing_area.set_visualization_type(viz_map[index])

        # Update calculations pane to match the visualization type
        self.calc_stack.setCurrentIndex(index)

        # Calculate the appropriate values for the selected visualization
        self._calculate_all()

    def _handle_labels_toggle(self, checked: bool) -> None:
        """Handle labels toggle.

        Args:
            checked: Whether the checkbox is checked
        """
        self.drawing_area.toggle_labels(checked)

    def _handle_measurements_toggle(self, checked: bool) -> None:
        """Handle measurements toggle.

        Args:
            checked: Whether the checkbox is checked
        """
        self.drawing_area.toggle_measurements(checked)

    def _handle_grid_toggle(self, checked: bool) -> None:
        """Handle grid toggle.

        Args:
            checked: Whether the checkbox is checked
        """
        self.drawing_area.toggle_grid(checked)

    def _handle_precision_change(self, value: int) -> None:
        """Handle precision change.

        Args:
            value: New precision value
        """
        self.drawing_area.set_precision(value)

    def _handle_zoom_change(self, value: int) -> None:
        """Handle zoom change.

        Args:
            value: New zoom value
        """
        self.drawing_area.set_zoom(value / 100)

    def _handle_animation_toggle(self, checked: bool) -> None:
        """Handle animation toggle.

        Args:
            checked: Whether the checkbox is checked
        """
        self.drawing_area.toggle_animation(checked)

    def _handle_speed_change(self, value: int) -> None:
        """Handle animation speed change.

        Args:
            value: New speed value
        """
        self.drawing_area.set_animation_speed(value)
