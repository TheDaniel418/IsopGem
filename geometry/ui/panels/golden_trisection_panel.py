"""Golden Trisection panel module.

This module provides a UI panel for exploring the Golden Trisection.
"""
import math
from typing import List

from PyQt6.QtCore import QLineF, QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from geometry.services.golden_mean_service import GoldenMeanService


class BaseVisualizationWidget(QWidget):
    """Base class for Golden Trisection visualization widgets."""

    def __init__(self, parent=None):
        """Initialize the visualization widget.

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

        # Custom trisection values (for updating from calculator)
        self.custom_trisection = None

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
            zoom: Zoom level factor
        """
        self.zoom_level = max(0.1, min(5.0, zoom))
        self.update()

    def set_precision(self, precision: int) -> None:
        """Set the number of decimal places for measurements.

        Args:
            precision: Number of decimal places
        """
        self.precision = precision
        self.update()

    def toggle_animation(self, active: bool) -> None:
        """Toggle animation.

        Args:
            active: Whether animation is active
        """
        self.animation_active = active

        if active:
            self.animation_frame = 0
            self.animation_timer.start(self.animation_speed)
        else:
            self.animation_timer.stop()
            self.update()

    def set_animation_speed(self, speed: int) -> None:
        """Set the animation speed.

        Args:
            speed: Animation speed (ms)
        """
        self.animation_speed = speed
        if self.animation_active:
            self.animation_timer.setInterval(speed)

    def update_animation(self) -> None:
        """Update the animation frame."""
        self.animation_frame += 1
        if self.animation_frame > 360:  # Reset after a full cycle
            self.animation_frame = 0
        self.update()

    def update_from_segments(self, first: float, second: float, third: float) -> None:
        """Update the visualization based on the segment values from calculator.

        Args:
            first: First segment value (1)
            second: Second segment value (ρ)
            third: Third segment value (σ)
        """
        # Store custom trisection values for drawing
        total_length = first + second + third

        # Calculate the proportional ratios (segment to total)
        ratio_first = first / total_length
        ratio_second = second / total_length
        ratio_third = third / total_length

        # Calculate the Golden Trisection ratios
        rho = second / first  # ρ (rho) - second to first ratio
        sigma = third / first  # σ (sigma) - third to first ratio

        # Prepare custom trisection data
        self.custom_trisection = {
            "first_segment": first,
            "second_segment": second,
            "third_segment": third,
            "total_length": total_length,
            "ratio_first": ratio_first,
            "ratio_second": ratio_second,
            "ratio_third": ratio_third,
            "rho": rho,  # ρ - second segment to first segment ratio
            "sigma": sigma,  # σ - third segment to first segment ratio
            "rho_lowercase": ratio_first,  # For display in measurements
            "sigma_lowercase": ratio_second,  # For display in measurements
            "third_ratio": ratio_third,  # For display in measurements
        }

        # Trigger redraw
        self.update()

    def paintEvent(self, event) -> None:
        """Paint event handler.

        Args:
            event: QPaintEvent
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set up transformations for zoom
        painter.scale(self.zoom_level, self.zoom_level)

        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(painter)

        # Draw the visualization (to be implemented by subclasses)
        self._draw_visualization(painter)

    def _draw_grid(self, painter: QPainter) -> None:
        """Draw a grid.

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

    def _draw_visualization(self, painter: QPainter) -> None:
        """Draw the visualization (to be implemented by subclasses).

        Args:
            painter: QPainter object
        """
        pass


class TrisectionLineVisualizer(BaseVisualizationWidget):
    """Widget for visualizing the Golden Trisection line."""

    def _draw_visualization(self, painter: QPainter) -> None:
        """Draw the Golden Trisection line visualization.

        Args:
            painter: QPainter object
        """
        self._draw_golden_trisection(painter)

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
        if self.custom_trisection:
            # Use custom trisection but scale to fit the visualization area
            total_custom = (
                self.custom_trisection["first_segment"]
                + self.custom_trisection["second_segment"]
                + self.custom_trisection["third_segment"]
            )

            # Calculate segments proportionally to display area
            first_segment = length * (
                self.custom_trisection["first_segment"] / total_custom
            )
            second_segment = length * (
                self.custom_trisection["second_segment"] / total_custom
            )
            third_segment = length - first_segment - second_segment  # Ensure exact fit

            # Create a trisection dictionary with the scaled values
            trisection = {
                "first_segment": first_segment,
                "second_segment": second_segment,
                "third_segment": third_segment,
                "total_length": length,
                "rho": self.custom_trisection["rho"],
                "sigma": self.custom_trisection["sigma"],
                "rho_lowercase": self.custom_trisection["ratio_first"],
                "sigma_lowercase": self.custom_trisection["ratio_second"],
                "third_ratio": self.custom_trisection["ratio_third"],
            }
        else:
            # Use the standard golden trisection calculation
            trisection = self.service.calculate_golden_trisection(length)

        # Calculate the points for drawing based on segments
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

        # Draw the three segments with appropriate colors
        # First segment (red - unit length - 1)
        painter.setPen(QPen(QColor(200, 0, 0), 5))
        painter.drawLine(QPointF(start_x, y), QPointF(first_point, y))

        # Second segment (green - middle - RHO)
        painter.setPen(QPen(QColor(0, 150, 0), 5))
        painter.drawLine(QPointF(first_point, y), QPointF(second_point, y))

        # Third segment (blue - largest - SIGMA)
        painter.setPen(QPen(QColor(0, 0, 200), 5))
        painter.drawLine(QPointF(second_point, y), QPointF(start_x + length, y))

        # Add segment labels
        if self.show_labels:
            painter.setFont(QFont("Arial", 12))

            # First segment label (1)
            painter.setPen(QColor(200, 0, 0))
            painter.drawText(
                QPointF(start_x + trisection["first_segment"] / 2 - 15, y - 15), "1"
            )

            # Second segment label (ρ)
            painter.setPen(QColor(0, 150, 0))
            painter.drawText(
                QPointF(first_point + trisection["second_segment"] / 2 - 15, y - 15),
                "ρ",
            )

            # Third segment label (σ)
            painter.setPen(QColor(0, 0, 200))
            painter.drawText(
                QPointF(second_point + trisection["third_segment"] / 2 - 15, y - 15),
                "σ",
            )

        # Draw animation if active
        if self.animation_active:
            progress = min(1.0, self.animation_frame / 120)

            # Draw animated rectangles showing the Golden Trisection segments
            if progress > 0.3:
                # Get the trisection values for our animation
                RHO = trisection["rho"]  # ρ (uppercase rho) - short diagonal
                SIGMA = trisection["sigma"]  # σ (uppercase sigma) - long diagonal

                # First segment rectangle (red - unit length - 1)
                first_width = trisection["first_segment"]
                height1 = 40
                first_rect = QRectF(start_x, y - height1 / 2, first_width, height1)
                painter.setBrush(QBrush(QColor(200, 0, 0, 150)))
                painter.setPen(QPen(QColor(200, 0, 0), 2))
                painter.drawRect(first_rect)

                # Add unit label in animation
                painter.setPen(QColor(200, 0, 0))
                painter.setFont(QFont("Arial", 9))
                painter.drawText(QPointF(start_x + first_width / 2 - 5, y), "1")

                # Second segment rectangle (green - middle length - ρ)
                second_width = trisection["second_segment"]
                height2 = height1 * 1.2  # Make height proportional to segment ratio
                second_rect = QRectF(
                    first_point, y - height2 / 2, second_width, height2
                )
                painter.setBrush(QBrush(QColor(0, 150, 0, 150)))
                painter.setPen(QPen(QColor(0, 150, 0), 2))
                painter.drawRect(second_rect)

                # Add rho label in animation
                painter.setPen(QColor(0, 150, 0))
                painter.drawText(
                    QPointF(first_point + second_width / 2 - 20, y), f"ρ≈{RHO:.3f}"
                )

                # Third segment rectangle (blue - largest length - σ)
                third_width = trisection["third_segment"]
                height3 = height1 * 1.5  # Make height proportional to segment ratio
                third_rect = QRectF(second_point, y - height3 / 2, third_width, height3)
                painter.setBrush(QBrush(QColor(0, 0, 200, 150)))
                painter.setPen(QPen(QColor(0, 0, 200), 2))
                painter.drawRect(third_rect)

                # Add sigma label in animation
                painter.setPen(QColor(0, 0, 200))
                painter.drawText(
                    QPointF(second_point + third_width / 2 - 20, y), f"σ≈{SIGMA:.3f}"
                )

        # Draw labels if enabled
        if self.show_labels:
            painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(
                QPointF(start_x + length / 2 - 80, y - 40), "Golden Trisection (1:ρ:σ)"
            )

        # Show measurements if enabled
        if self.show_measurements:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.black)

            # Get values from the trisection
            first_ratio = trisection["rho_lowercase"]
            second_ratio = trisection["sigma_lowercase"]
            third_ratio = trisection["third_ratio"]
            RHO = trisection["rho"]  # Ρ (rho uppercase)
            SIGMA = trisection["sigma"]  # Σ (sigma uppercase)

            # Show actual values from the calculator if custom trisection is being used
            if self.custom_trisection:
                # Display actual segment values from calculator
                painter.drawText(
                    QPointF(start_x + length / 2 - 240, y + 50),
                    f"Segments: 1 = {self.custom_trisection['first_segment']:.{self.precision}f}, "
                    f"ρ = {self.custom_trisection['second_segment']:.{self.precision}f}, "
                    f"σ = {self.custom_trisection['third_segment']:.{self.precision}f}",
                )
            else:
                # Display scaled segment values from visualization
                painter.drawText(
                    QPointF(start_x + length / 2 - 240, y + 50),
                    f"Segments: 1 = {trisection['first_segment']:.{self.precision}f}, "
                    f"ρ = {trisection['second_segment']:.{self.precision}f}, "
                    f"σ = {trisection['third_segment']:.{self.precision}f}",
                )

            # Display the trisection ratios
            painter.drawText(
                QPointF(start_x + length / 2 - 240, y + 70),
                f"Proportion: 1 : ρ = {RHO:.{self.precision}f} : σ = {SIGMA:.{self.precision}f}",
            )

            # Display segment ratios to total length
            painter.drawText(
                QPointF(start_x + length / 2 - 240, y + 90),
                f"Segment ratios to total: {first_ratio:.{self.precision}f} : {second_ratio:.{self.precision}f} : {third_ratio:.{self.precision}f}",
            )


class HeptagonVisualizer(BaseVisualizationWidget):
    """Widget for visualizing the Golden Trisection in a heptagon."""

    def _draw_visualization(self, painter: QPainter) -> None:
        """Draw the heptagon visualization.

        Args:
            painter: QPainter object
        """
        width = self.width() / self.zoom_level
        height = self.height() / self.zoom_level
        self._draw_heptagon(painter, width / 2, height / 2, min(width, height) * 0.3)

    def _draw_heptagon(
        self, painter: QPainter, center_x: float, center_y: float, radius: float
    ) -> None:
        """Draw a heptagon with its diagonals to illustrate Golden Trisection.

        Args:
            painter: QPainter object
            center_x: X coordinate of center
            center_y: Y coordinate of center
            radius: Radius of heptagon
        """
        # Create points for heptagon vertices
        points = []
        for i in range(7):
            angle = 2 * math.pi * i / 7 - math.pi / 2  # Start from top position
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(QPointF(x, y))

        # Draw heptagon outline
        painter.setPen(QPen(QColor(100, 100, 100), 1.5))
        path = QPainterPath()
        path.moveTo(points[0])
        for i in range(1, 7):
            path.lineTo(points[i])
        path.closeSubpath()
        painter.drawPath(path)

        # Get the trisection values from the service for educational comparison
        service = GoldenMeanService.get_instance()
        trisection_values = service.calculate_golden_trisection(1.0)

        SIGMA = trisection_values["sigma"]  # Σ (sigma uppercase) - Long diagonal
        RHO = trisection_values["rho"]  # Ρ (rho uppercase) - Short diagonal

        # Draw the unit edge (with red color - corresponds to first segment - unit length)
        painter.setPen(QPen(QColor(200, 0, 0), 2.5))
        edge = QLineF(points[0], points[1])  # Adjacent vertices
        painter.drawLine(edge)

        # Draw short diagonal (Ρ - uppercase Rho ≈ 1.802 - green color - corresponds to second segment)
        painter.setPen(QPen(QColor(0, 150, 0), 2.5))
        short_diagonal = QLineF(points[0], points[2])  # Skip 1 vertex
        painter.drawLine(short_diagonal)

        # Draw long diagonal (Σ - uppercase Sigma ≈ 2.247 - blue color - corresponds to third segment)
        painter.setPen(QPen(QColor(0, 0, 200), 2.5))
        long_diagonal = QLineF(points[0], points[3])  # Skip 2 vertices
        painter.drawLine(long_diagonal)

        # Draw vertex points slightly larger
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        for point in points:
            painter.drawEllipse(point, 3, 3)

        # Add labels with improved positioning
        if self.show_labels:
            painter.setFont(QFont("Arial", 9))

            # Label for the edge (corresponds to first segment in trisection - unit length)
            painter.setPen(QColor(200, 0, 0))  # Red
            midpoint_edge = QPointF(
                (points[0].x() + points[1].x()) / 2, (points[0].y() + points[1].y()) / 2
            )
            offset_edge = self._get_perpendicular_offset(points[0], points[1], 15)
            painter.drawText(
                QPointF(
                    midpoint_edge.x() + offset_edge.x(),
                    midpoint_edge.y() + offset_edge.y(),
                ),
                "1 (unit edge)",
            )

            # Label for short diagonal (corresponds to second segment in trisection)
            painter.setPen(QColor(0, 150, 0))  # Green
            midpoint_short = QPointF(
                (points[0].x() + points[2].x()) / 2, (points[0].y() + points[2].y()) / 2
            )
            offset_short = self._get_perpendicular_offset(points[0], points[2], 15)
            painter.drawText(
                QPointF(
                    midpoint_short.x() + offset_short.x(),
                    midpoint_short.y() + offset_short.y(),
                ),
                f"ρ ≈ {RHO:.3f}",
            )

            # Label for long diagonal (corresponds to third segment in trisection)
            painter.setPen(QColor(0, 0, 200))  # Blue
            midpoint_long = QPointF(
                (points[0].x() + points[3].x()) / 2, (points[0].y() + points[3].y()) / 2
            )
            offset_long = self._get_perpendicular_offset(points[0], points[3], 15)
            painter.drawText(
                QPointF(
                    midpoint_long.x() + offset_long.x(),
                    midpoint_long.y() + offset_long.y(),
                ),
                f"σ ≈ {SIGMA:.3f}",
            )

            # Add title for the visualization
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(
                QPointF(center_x - 140, center_y - radius - 20),
                "Unit-Edge Heptagon with Golden Trisection Diagonals",
            )

        # Show measurements if enabled
        if self.show_measurements:
            painter.setFont(QFont("Arial", 10))
            painter.setPen(Qt.GlobalColor.black)

            # Display edge length
            painter.drawText(
                QPointF(center_x - radius, center_y + radius + 20), "Unit edge = 1.0"
            )

            # Display diagonal lengths
            painter.drawText(
                QPointF(center_x - radius, center_y + radius + 40),
                f"Short diagonal (ρ) = {RHO:.{self.precision}f}",
            )

            painter.drawText(
                QPointF(center_x - radius, center_y + radius + 60),
                f"Long diagonal (σ) = {SIGMA:.{self.precision}f}",
            )

            # Display relationships
            if center_x > 200:  # Only if there's enough space
                painter.drawText(
                    QPointF(center_x - radius, center_y + radius + 80),
                    f"ρ² = σ + 1 → {RHO*RHO:.{self.precision}f} ≈ {SIGMA+1:.{self.precision}f}",
                )

                painter.drawText(
                    QPointF(center_x - radius, center_y + radius + 100),
                    f"σ² = ρ + σ + 1 → {SIGMA*SIGMA:.{self.precision}f} ≈ {RHO+SIGMA+1:.{self.precision}f}",
                )

                painter.drawText(
                    QPointF(center_x - radius, center_y + radius + 120),
                    f"ρ·σ = ρ + σ → {RHO*SIGMA:.{self.precision}f} ≈ {RHO+SIGMA:.{self.precision}f}",
                )

    def _get_perpendicular_offset(
        self, p1: QPointF, p2: QPointF, distance: float
    ) -> QPointF:
        """Calculate a perpendicular offset for label positioning.

        Args:
            p1: First point
            p2: Second point
            distance: Desired distance

        Returns:
            Offset point perpendicular to line
        """
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = math.sqrt(dx * dx + dy * dy)

        if length < 0.001:  # Avoid division by zero
            return QPointF(distance, distance)

        # Get perpendicular vector
        perpX = -dy / length * distance
        perpY = dx / length * distance

        return QPointF(perpX, perpY)


class NestedHeptagonVisualizer(BaseVisualizationWidget):
    """Widget for visualizing nested heptagons using the Golden Trisection relationships."""

    def _draw_visualization(self, painter: QPainter) -> None:
        """Draw the nested heptagons visualization.

        Args:
            painter: QPainter object
        """
        width = self.width() / self.zoom_level
        height = self.height() / self.zoom_level
        self._draw_nested_heptagons(
            painter, width / 2, height / 2, min(width, height) * 0.35
        )

    def _draw_nested_heptagons(
        self, painter: QPainter, center_x: float, center_y: float, radius: float
    ) -> None:
        """Draw nested heptagons with relationships based on Golden Trisection.

        Args:
            painter: QPainter object
            center_x: X coordinate of center
            center_y: Y coordinate of center
            radius: Radius of outer heptagon
        """
        # Get the standard trisection values
        service = GoldenMeanService.get_instance()
        trisection = service.calculate_golden_trisection(1.0)

        # Get the Golden Trisection constants
        SIGMA = trisection["sigma"]  # σ (uppercase sigma) - Long diagonal
        RHO = trisection["rho"]  # ρ (uppercase rho) - Short diagonal

        # Calculate the relationships for nested heptagons
        # Edge length of the outer heptagon in relation to the middle one
        outer_scale = SIGMA * RHO  # or SIGMA + RHO (these are approximately equal)
        # Edge length of the inner heptagon in relation to the middle one
        inner_scale = 1 / (SIGMA * RHO)

        # Draw the middle heptagon with unit edge length (red)
        middle_radius = radius / outer_scale
        middle_points = self._create_heptagon_points(center_x, center_y, middle_radius)
        self._draw_heptagon_outline(painter, middle_points, QColor(200, 0, 0), 2.0)

        # Draw the outer heptagon (blue)
        outer_points = self._create_heptagon_points(center_x, center_y, radius)
        self._draw_heptagon_outline(painter, outer_points, QColor(0, 0, 200), 2.0)

        # Draw the inner heptagon (green)
        inner_radius = middle_radius * inner_scale
        inner_points = self._create_heptagon_points(center_x, center_y, inner_radius)
        self._draw_heptagon_outline(painter, inner_points, QColor(0, 150, 0), 2.0)

        # Draw vertex points for all heptagons
        self._draw_vertex_points(painter, outer_points)
        self._draw_vertex_points(painter, middle_points)
        self._draw_vertex_points(painter, inner_points)

        # Draw connections between corresponding vertices
        if self.animation_active:
            progress = min(1.0, self.animation_frame / 180)
            if progress > 0.3:
                self._draw_nested_connections(
                    painter, outer_points, middle_points, inner_points, progress
                )

        # Add labels and measurements
        if self.show_labels:
            self._add_nested_heptagon_labels(
                painter,
                center_x,
                center_y,
                radius,
                middle_radius,
                inner_radius,
                SIGMA,
                RHO,
            )

        if self.show_measurements:
            self._add_nested_heptagon_measurements(
                painter, center_x, center_y, radius, SIGMA, RHO
            )

    def _create_heptagon_points(
        self, center_x: float, center_y: float, radius: float
    ) -> List[QPointF]:
        """Create points for a heptagon with given center and radius.

        Args:
            center_x: X coordinate of center
            center_y: Y coordinate of center
            radius: Radius of heptagon

        Returns:
            List of points for heptagon vertices
        """
        points = []
        for i in range(7):
            angle = 2 * math.pi * i / 7 - math.pi / 2  # Start from top position
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(QPointF(x, y))
        return points

    def _draw_heptagon_outline(
        self, painter: QPainter, points: List[QPointF], color: QColor, line_width: float
    ) -> None:
        """Draw a heptagon outline with given points and color.

        Args:
            painter: QPainter object
            points: List of points for heptagon vertices
            color: Color for the outline
            line_width: Width of the outline
        """
        painter.setPen(QPen(color, line_width))
        path = QPainterPath()
        path.moveTo(points[0])
        for i in range(1, 7):
            path.lineTo(points[i])
        path.closeSubpath()
        painter.drawPath(path)

    def _draw_vertex_points(
        self, painter: QPainter, points: List[QPointF], size: float = 3.0
    ) -> None:
        """Draw vertex points for a heptagon.

        Args:
            painter: QPainter object
            points: List of points for heptagon vertices
            size: Size of vertex points
        """
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        for point in points:
            painter.drawEllipse(point, size, size)

    def _draw_nested_connections(
        self,
        painter: QPainter,
        outer_points: List[QPointF],
        middle_points: List[QPointF],
        inner_points: List[QPointF],
        progress: float,
    ) -> None:
        """Draw connections between corresponding vertices of nested heptagons.

        Args:
            painter: QPainter object
            outer_points: List of points for outer heptagon vertices
            middle_points: List of points for middle heptagon vertices
            inner_points: List of points for inner heptagon vertices
            progress: Animation progress (0.0 to 1.0)
        """
        # Draw connections with dashed lines
        dash_pen = QPen(QColor(100, 100, 100, 180), 0.8, Qt.PenStyle.DashLine)
        painter.setPen(dash_pen)

        # Connect vertices from outer to inner heptagon passing through middle heptagon
        for i in range(7):
            # Connect outer to middle
            painter.drawLine(QLineF(outer_points[i], middle_points[i]))
            # Connect middle to inner
            painter.drawLine(QLineF(middle_points[i], inner_points[i]))

        # In animation, highlight one set of connected vertices
        if progress > 0.5:
            # Determine which vertex to highlight based on animation progress
            vertex_index = int((self.animation_frame / 10) % 7)

            highlight_pen = QPen(QColor(255, 120, 0), 1.8)
            painter.setPen(highlight_pen)
            painter.drawLine(
                QLineF(outer_points[vertex_index], middle_points[vertex_index])
            )
            painter.drawLine(
                QLineF(middle_points[vertex_index], inner_points[vertex_index])
            )

            # Also highlight the vertices themselves
            painter.setBrush(QBrush(QColor(255, 120, 0)))
            painter.drawEllipse(outer_points[vertex_index], 4, 4)
            painter.drawEllipse(middle_points[vertex_index], 4, 4)
            painter.drawEllipse(inner_points[vertex_index], 4, 4)

    def _add_nested_heptagon_labels(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        outer_radius: float,
        middle_radius: float,
        inner_radius: float,
        SIGMA: float,
        RHO: float,
    ) -> None:
        """Add labels to the nested heptagon visualization.

        Args:
            painter: QPainter object
            center_x: X coordinate of center
            center_y: Y coordinate of center
            outer_radius: Radius of outer heptagon
            middle_radius: Radius of middle heptagon
            inner_radius: Radius of inner heptagon
            SIGMA: Sigma value
            RHO: Rho value
        """
        # Add title
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(
            QPointF(center_x - 130, center_y - outer_radius - 25),
            "Nested Heptagons with Golden Trisection",
        )

        # Label the heptagons
        painter.setFont(QFont("Arial", 9))

        # Outer heptagon (blue)
        painter.setPen(QColor(0, 0, 200))
        painter.drawText(
            QPointF(center_x - 120, center_y - outer_radius - 5),
            f"Outer Heptagon (edge length ≈ {SIGMA * RHO:.3f} units)",
        )

        # Middle heptagon (red) - unit edge length
        painter.setPen(QColor(200, 0, 0))
        painter.drawText(
            QPointF(center_x - 120, center_y - middle_radius - 5),
            "Middle Heptagon (unit edge length = 1)",
        )

        # Inner heptagon (green)
        painter.setPen(QColor(0, 150, 0))
        painter.drawText(
            QPointF(center_x - 120, center_y - inner_radius - 5),
            f"Inner Heptagon (edge length ≈ {1/(SIGMA * RHO):.3f} units)",
        )

    def _add_nested_heptagon_measurements(
        self,
        painter: QPainter,
        center_x: float,
        center_y: float,
        radius: float,
        SIGMA: float,
        RHO: float,
    ) -> None:
        """Add measurements to the nested heptagon visualization.

        Args:
            painter: QPainter object
            center_x: X coordinate of center
            center_y: Y coordinate of center
            radius: Radius of outer heptagon
            SIGMA: Sigma value
            RHO: Rho value
        """
        painter.setFont(QFont("Arial", 9))
        painter.setPen(Qt.GlobalColor.black)

        # Calculate relationship values
        sr_product = SIGMA * RHO
        sr_sum = SIGMA + RHO

        # Position for the measurements
        y_pos = center_y + radius + 20
        x_pos = center_x - radius * 0.8

        # Display the relationship between the heptagons
        painter.drawText(
            QPointF(x_pos, y_pos),
            f"ρ·σ = {sr_product:.{self.precision}f} ≈ ρ+σ = {sr_sum:.{self.precision}f}",
        )

        painter.drawText(
            QPointF(x_pos, y_pos + 20),
            "Outer heptagon edge length = Middle heptagon edge × ρ·σ",
        )

        painter.drawText(
            QPointF(x_pos, y_pos + 40),
            "Inner heptagon edge length = Middle heptagon edge ÷ ρ·σ",
        )

        # Show more detailed mathematical relationships
        if center_x > 220:
            painter.drawText(
                QPointF(x_pos, y_pos + 60),
                f"Ratio of edge lengths (Outer : Middle : Inner) = {sr_product:.{self.precision}f} : 1 : {1/sr_product:.{self.precision}f}",
            )

            painter.drawText(
                QPointF(x_pos, y_pos + 80),
                "The nested heptagons demonstrate the self-similar structure through the Golden Trisection",
            )

            painter.drawText(
                QPointF(x_pos, y_pos + 100),
                f"1/ρσ = {1/sr_product:.{self.precision}f} (inner heptagon edge length relative to middle)",
            )


class TabbedVisualizationArea(QTabWidget):
    """Tabbed container for different Golden Trisection visualizations."""

    def __init__(self, parent=None):
        """Initialize the tabbed visualization area.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create visualization widgets
        self.trisection_visualizer = TrisectionLineVisualizer()
        self.heptagon_visualizer = HeptagonVisualizer()
        self.nested_heptagon_visualizer = NestedHeptagonVisualizer()

        # Add tabs
        self.addTab(self.trisection_visualizer, "Line Trisection")
        self.addTab(self.heptagon_visualizer, "Heptagon Visualization")
        self.addTab(self.nested_heptagon_visualizer, "Nested Heptagons")

        # Store references to all visualization widgets for control access
        self.visualizers = [
            self.trisection_visualizer,
            self.heptagon_visualizer,
            self.nested_heptagon_visualizer,
        ]

    def toggle_labels(self, show: bool) -> None:
        """Toggle display of labels across all tabs."""
        for visualizer in self.visualizers:
            visualizer.toggle_labels(show)

    def toggle_measurements(self, show: bool) -> None:
        """Toggle display of measurements across all tabs."""
        for visualizer in self.visualizers:
            visualizer.toggle_measurements(show)

    def toggle_grid(self, show: bool) -> None:
        """Toggle display of grid across all tabs."""
        for visualizer in self.visualizers:
            visualizer.toggle_grid(show)

    def set_zoom(self, zoom: float) -> None:
        """Set zoom level across all tabs."""
        for visualizer in self.visualizers:
            visualizer.set_zoom(zoom)

    def set_precision(self, precision: int) -> None:
        """Set precision for measurements across all tabs."""
        for visualizer in self.visualizers:
            visualizer.set_precision(precision)

    def toggle_animation(self, active: bool) -> None:
        """Toggle animation across all tabs."""
        for visualizer in self.visualizers:
            visualizer.toggle_animation(active)

    def set_animation_speed(self, speed: int) -> None:
        """Set animation speed across all tabs."""
        for visualizer in self.visualizers:
            visualizer.set_animation_speed(speed)

    def update_from_segments(self, first: float, second: float, third: float) -> None:
        """Update visualizations with custom segment values."""
        for visualizer in self.visualizers:
            visualizer.update_from_segments(first, second, third)


class GoldenTrisectionPanel(QWidget):
    """Panel for exploring the Golden Trisection."""

    def __init__(self, parent=None):
        """Initialize the panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Get service instances
        self.service = GoldenMeanService.get_instance()

        # Initialize UI
        self._init_ui()

        # Initial calculations
        self._calculate_trisection()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left panel with visualization and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # Title
        title_label = QLabel("Golden Trisection Explorer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        left_layout.addWidget(title_label)

        # Add tabbed visualization area
        self.tabbed_visualization = TabbedVisualizationArea()
        left_layout.addWidget(self.tabbed_visualization, 1)

        # Add controls below the drawing area
        controls_panel = self._create_controls_panel()
        left_layout.addWidget(controls_panel)

        # Add the left panel to main layout
        main_layout.addWidget(left_panel, 3)  # Give it more space

        # Add calculations panel to main layout
        calculations_panel = self._create_calculations_panel()
        main_layout.addWidget(calculations_panel, 1)  # Give it less space

    def _create_controls_panel(self) -> QGroupBox:
        """Create the controls panel.

        Returns:
            QGroupBox containing the controls
        """
        controls_group = QGroupBox("Visualization Controls")
        controls_layout = QGridLayout(controls_group)

        # Display options
        show_labels_check = QCheckBox("Show Labels")
        show_labels_check.setChecked(True)
        show_labels_check.toggled.connect(self.tabbed_visualization.toggle_labels)
        controls_layout.addWidget(show_labels_check, 0, 0)

        show_measurements_check = QCheckBox("Show Measurements")
        show_measurements_check.setChecked(True)
        show_measurements_check.toggled.connect(
            self.tabbed_visualization.toggle_measurements
        )
        controls_layout.addWidget(show_measurements_check, 0, 1)

        show_grid_check = QCheckBox("Show Grid")
        show_grid_check.setChecked(False)
        show_grid_check.toggled.connect(self.tabbed_visualization.toggle_grid)
        controls_layout.addWidget(show_grid_check, 0, 2)

        # Zoom control
        zoom_label = QLabel("Zoom:")
        controls_layout.addWidget(zoom_label, 1, 0)

        zoom_slider = QSlider(Qt.Orientation.Horizontal)
        zoom_slider.setRange(10, 200)
        zoom_slider.setValue(100)  # Default value of 1.0
        zoom_slider.setTickInterval(10)
        zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        zoom_slider.valueChanged.connect(
            lambda v: self.tabbed_visualization.set_zoom(v / 100.0)
        )
        controls_layout.addWidget(zoom_slider, 1, 1, 1, 2)

        # Precision
        precision_label = QLabel("Precision:")
        controls_layout.addWidget(precision_label, 2, 0)

        precision_spin = QSpinBox()
        precision_spin.setRange(2, 10)
        precision_spin.setValue(4)
        precision_spin.valueChanged.connect(self.tabbed_visualization.set_precision)
        controls_layout.addWidget(precision_spin, 2, 1)

        # Animation controls
        animate_check = QCheckBox("Animate")
        animate_check.setChecked(False)
        animate_check.toggled.connect(self.tabbed_visualization.toggle_animation)
        controls_layout.addWidget(animate_check, 3, 0)

        speed_label = QLabel("Speed:")
        controls_layout.addWidget(speed_label, 3, 1)

        speed_slider = QSlider(Qt.Orientation.Horizontal)
        speed_slider.setRange(10, 200)
        speed_slider.setValue(100)  # Default value
        speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        speed_slider.valueChanged.connect(
            lambda v: self.tabbed_visualization.set_animation_speed(210 - v)
        )
        controls_layout.addWidget(speed_slider, 3, 2)

        return controls_group

    def _create_calculations_panel(self) -> QScrollArea:
        """Create the calculations panel.

        Returns:
            QScrollArea containing the calculations panel
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
        self.trisection_length_spin.setDecimals(6)
        self.trisection_length_spin.valueChanged.connect(self._calculate_trisection)
        trisection_layout.addRow("Total length:", self.trisection_length_spin)

        # First segment (unit length - 1)
        self.trisection_first = QDoubleSpinBox()
        self.trisection_first.setRange(0.1, 10000)
        self.trisection_first.setValue(20.0)
        self.trisection_first.setSingleStep(0.1)
        self.trisection_first.setDecimals(6)
        self.trisection_first.valueChanged.connect(self._calculate_from_first_segment)
        trisection_layout.addRow("First segment (1):", self.trisection_first)

        # Second segment (middle - ρ)
        self.trisection_second = QDoubleSpinBox()
        self.trisection_second.setRange(0.1, 10000)
        self.trisection_second.setValue(36.04)  # Approx 1.802 * 20
        self.trisection_second.setSingleStep(0.1)
        self.trisection_second.setDecimals(6)
        self.trisection_second.valueChanged.connect(self._calculate_from_second_segment)
        trisection_layout.addRow("Second segment (ρ):", self.trisection_second)

        # Third segment (largest - σ)
        self.trisection_third = QDoubleSpinBox()
        self.trisection_third.setRange(0.1, 10000)
        self.trisection_third.setValue(44.94)  # Approx 2.247 * 20
        self.trisection_third.setSingleStep(0.1)
        self.trisection_third.setDecimals(6)
        self.trisection_third.valueChanged.connect(self._calculate_from_third_segment)
        trisection_layout.addRow("Third segment (σ):", self.trisection_third)

        # Proportions
        self.trisection_ratio_whole_to_first = QLineEdit()
        self.trisection_ratio_whole_to_first.setReadOnly(True)
        trisection_layout.addRow("Total / First:", self.trisection_ratio_whole_to_first)

        self.trisection_ratio_first_to_second = QLineEdit()
        self.trisection_ratio_first_to_second.setReadOnly(True)
        trisection_layout.addRow(
            "Second / First (ρ):", self.trisection_ratio_first_to_second
        )

        self.trisection_ratio_second_to_third = QLineEdit()
        self.trisection_ratio_second_to_third.setReadOnly(True)
        trisection_layout.addRow(
            "Third / Second (σ/ρ):", self.trisection_ratio_second_to_third
        )

        layout.addWidget(trisection_group)

        # Golden Trisection information
        trisection_info_group = QGroupBox("Golden Trisection Properties")
        trisection_info_layout = QVBoxLayout(trisection_info_group)

        info_text = (
            "A Golden Trisection divides a line into three segments in the proportion 1:ρ:σ, "
            "which relates directly to the heptagon diagonals.\n\n"
            "Properties:\n"
            "- In a unit-edge heptagon (edge length = 1), the three segments follow the proportion 1:ρ:σ where:\n"
            "  • First segment = 1 (unit length)\n"
            "  • Second segment = ρ ≈ 1.802 (rho uppercase)\n"
            "  • Third segment = σ ≈ 2.247 (sigma uppercase)\n"
            "- These values come directly from the heptagon geometry:\n"
            "  • ρ ≈ 1.802 - corresponds to the short diagonal of a unit-edge heptagon\n"
            "  • σ ≈ 2.247 - corresponds to the long diagonal of a unit-edge heptagon\n\n"
            "Heptagon Connection:\n"
            "- When a heptagon has edge length = 1, its diagonals have special lengths\n"
            "- The shorter diagonal has length ρ ≈ 1.802 (connecting vertices separated by 1)\n"
            "- The longer diagonal has length σ ≈ 2.247 (connecting vertices separated by 2)\n"
            "- These values satisfy important cubic equations: x³-x²-2x+1=0 and x³-2x²-x+1=0\n"
            "- They exhibit remarkable properties: ρ² = σ+1, σ² = ρ+σ+1, and ρ·σ = ρ+σ\n\n"
            "Mathematical Constants:\n"
            "- ρ (uppercase Rho) ≈ 1.8019... - short diagonal length in unit-edge heptagon\n"
            "- σ (uppercase Sigma) ≈ 2.2470... - long diagonal length in unit-edge heptagon\n"
            "- These values can be calculated using trigonometry:\n"
            "  • σ = sin(4π/7) / sin(π/7)\n"
            "  • ρ = sin(2π/7) / sin(π/7)\n\n"
            "Golden Ratio Comparison:\n"
            "- Golden Ratio (φ) ≈ 1.6180...\n"
            "- Golden Mean uses φ for segment proportions (line divided in proportion 1:φ)\n"
            "- Golden Trisection uses the specific heptagon constants (1:ρ:σ)\n"
            "- Both are important in geometry, but have distinct mathematical origins"
        )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        trisection_info_layout.addWidget(info_label)

        layout.addWidget(trisection_info_group)
        layout.addStretch()

        scroll.setWidget(panel)
        return scroll

    def _calculate_trisection(self) -> None:
        """Calculate golden trisection of a line."""
        total_length = self.trisection_length_spin.value()

        # Use the service to calculate the trisection
        trisection = self.service.calculate_golden_trisection(total_length)

        # Extract values
        first_segment = trisection["first_segment"]
        second_segment = trisection["second_segment"]
        third_segment = trisection["third_segment"]

        # Calculate ratios
        ratio_whole_to_first = total_length / first_segment
        ratio_second_to_first = second_segment / first_segment
        ratio_third_to_second = third_segment / second_segment

        # Get the special trisection constants
        RHO = trisection["rho"]  # Ρ (rho uppercase)
        SIGMA = trisection["sigma"]  # Σ (sigma uppercase)

        # Update display with blockSignals to prevent infinite loops
        self.trisection_first.blockSignals(True)
        self.trisection_second.blockSignals(True)
        self.trisection_third.blockSignals(True)
        self.trisection_first.setValue(first_segment)
        self.trisection_second.setValue(second_segment)
        self.trisection_third.setValue(third_segment)
        self.trisection_first.blockSignals(False)
        self.trisection_second.blockSignals(False)
        self.trisection_third.blockSignals(False)
        self.trisection_ratio_whole_to_first.setText(f"{ratio_whole_to_first:.6f}")
        self.trisection_ratio_first_to_second.setText(
            f"{ratio_second_to_first:.6f} (≈{RHO:.6f})"
        )
        self.trisection_ratio_second_to_third.setText(
            f"{ratio_third_to_second:.6f} (≈{SIGMA/RHO:.6f})"
        )

        # Update visualization with the actual segment values
        self.tabbed_visualization.update_from_segments(
            first_segment, second_segment, third_segment
        )

    def _calculate_from_first_segment(self) -> None:
        """Calculate golden trisection based on the first segment (unit) value."""
        unit_length = self.trisection_first.value()

        # Get the special trisection constants
        service = GoldenMeanService.get_instance()
        RHO = service.calculate_golden_trisection(1.0)["rho"]  # Ρ (rho uppercase)
        SIGMA = service.calculate_golden_trisection(1.0)["sigma"]  # Σ (sigma uppercase)

        # Calculate remaining segments
        second_segment = unit_length * RHO
        third_segment = unit_length * SIGMA

        # Calculate total length
        total_length = unit_length + second_segment + third_segment

        # Update the total length spinner (will trigger recalculation)
        self.trisection_length_spin.blockSignals(True)
        self.trisection_length_spin.setValue(total_length)
        self.trisection_length_spin.blockSignals(False)

        # Calculate ratios
        ratio_whole_to_first = total_length / unit_length
        ratio_second_to_first = second_segment / unit_length
        ratio_third_to_second = third_segment / second_segment

        # Update display manually
        self.trisection_second.blockSignals(True)
        self.trisection_third.blockSignals(True)
        self.trisection_second.setValue(second_segment)
        self.trisection_third.setValue(third_segment)
        self.trisection_second.blockSignals(False)
        self.trisection_third.blockSignals(False)
        self.trisection_ratio_whole_to_first.setText(f"{ratio_whole_to_first:.6f}")
        self.trisection_ratio_first_to_second.setText(
            f"{ratio_second_to_first:.6f} (≈{RHO:.6f})"
        )
        self.trisection_ratio_second_to_third.setText(
            f"{ratio_third_to_second:.6f} (≈{SIGMA/RHO:.6f})"
        )

        # Update visualization
        self.tabbed_visualization.update_from_segments(
            unit_length, second_segment, third_segment
        )

    def _calculate_from_second_segment(self) -> None:
        """Calculate golden trisection based on the second segment (ρ) value."""
        second_segment = self.trisection_second.value()

        # Get the special trisection constants
        service = GoldenMeanService.get_instance()
        RHO = service.calculate_golden_trisection(1.0)["rho"]  # Ρ (rho uppercase)
        SIGMA = service.calculate_golden_trisection(1.0)["sigma"]  # Σ (sigma uppercase)

        # Calculate remaining segments
        unit_length = second_segment / RHO
        third_segment = unit_length * SIGMA

        # Calculate total length
        total_length = unit_length + second_segment + third_segment

        # Update the total length spinner (will trigger recalculation)
        self.trisection_length_spin.blockSignals(True)
        self.trisection_length_spin.setValue(total_length)
        self.trisection_length_spin.blockSignals(False)

        # Calculate ratios
        ratio_whole_to_first = total_length / unit_length
        ratio_second_to_first = second_segment / unit_length
        ratio_third_to_second = third_segment / second_segment

        # Update display manually
        self.trisection_first.blockSignals(True)
        self.trisection_third.blockSignals(True)
        self.trisection_first.setValue(unit_length)
        self.trisection_third.setValue(third_segment)
        self.trisection_first.blockSignals(False)
        self.trisection_third.blockSignals(False)
        self.trisection_ratio_whole_to_first.setText(f"{ratio_whole_to_first:.6f}")
        self.trisection_ratio_first_to_second.setText(
            f"{ratio_second_to_first:.6f} (≈{RHO:.6f})"
        )
        self.trisection_ratio_second_to_third.setText(
            f"{ratio_third_to_second:.6f} (≈{SIGMA/RHO:.6f})"
        )

        # Update visualization
        self.tabbed_visualization.update_from_segments(
            unit_length, second_segment, third_segment
        )

    def _calculate_from_third_segment(self) -> None:
        """Calculate golden trisection based on the third segment (σ) value."""
        third_segment = self.trisection_third.value()

        # Get the special trisection constants
        service = GoldenMeanService.get_instance()
        RHO = service.calculate_golden_trisection(1.0)["rho"]  # Ρ (rho uppercase)
        SIGMA = service.calculate_golden_trisection(1.0)["sigma"]  # Σ (sigma uppercase)

        # Calculate remaining segments
        unit_length = third_segment / SIGMA
        second_segment = unit_length * RHO

        # Calculate total length
        total_length = unit_length + second_segment + third_segment

        # Update the total length spinner (will trigger recalculation)
        self.trisection_length_spin.blockSignals(True)
        self.trisection_length_spin.setValue(total_length)
        self.trisection_length_spin.blockSignals(False)

        # Calculate ratios
        ratio_whole_to_first = total_length / unit_length
        ratio_second_to_first = second_segment / unit_length
        ratio_third_to_second = third_segment / second_segment

        # Update display manually
        self.trisection_first.blockSignals(True)
        self.trisection_second.blockSignals(True)
        self.trisection_first.setValue(unit_length)
        self.trisection_second.setValue(second_segment)
        self.trisection_first.blockSignals(False)
        self.trisection_second.blockSignals(False)
        self.trisection_ratio_whole_to_first.setText(f"{ratio_whole_to_first:.6f}")
        self.trisection_ratio_first_to_second.setText(
            f"{ratio_second_to_first:.6f} (≈{RHO:.6f})"
        )
        self.trisection_ratio_second_to_third.setText(
            f"{ratio_third_to_second:.6f} (≈{SIGMA/RHO:.6f})"
        )

        # Update visualization
        self.tabbed_visualization.update_from_segments(
            unit_length, second_segment, third_segment
        )
