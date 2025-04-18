"""Polygon calculator module.

This module provides a calculator for polygon-related calculations.
It supports both regular and irregular polygons and provides methods
for calculating various properties such as area, perimeter, centroid,
and interior angles.
"""

import math
from typing import List, Optional, Tuple, Union

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QWidget

from geometry.ui.sacred_geometry.model import Point, Polygon, Style


class PolygonCalculator:
    """Calculator for polygon-related calculations."""

    def __init__(
        self, vertices: Optional[List[Union[Point, Tuple[float, float]]]] = None
    ):
        """Initialize the polygon calculator.

        Args:
            vertices: List of vertices as Point objects or (x, y) tuples
        """
        self.vertices = []
        if vertices:
            self.set_vertices(vertices)

    def set_vertices(self, vertices: List[Union[Point, Tuple[float, float]]]) -> None:
        """Set the vertices of the polygon.

        Args:
            vertices: List of vertices as Point objects or (x, y) tuples
        """
        self.vertices = []
        for vertex in vertices:
            if isinstance(vertex, Point):
                self.vertices.append(vertex)
            elif isinstance(vertex, tuple) and len(vertex) == 2:
                self.vertices.append(Point(vertex[0], vertex[1]))
            else:
                raise ValueError("Vertices must be Point objects or (x, y) tuples")

    def get_vertices(self) -> List[Point]:
        """Get the vertices of the polygon.

        Returns:
            List of vertices as Point objects
        """
        return self.vertices

    def calculate_area(self) -> float:
        """Calculate the area of the polygon using the Shoelace formula.

        Returns:
            Area of the polygon
        """
        if len(self.vertices) < 3:
            return 0.0

        # Shoelace formula (Gauss's area formula)
        area = 0.0
        n = len(self.vertices)
        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i].x * self.vertices[j].y
            area -= self.vertices[j].x * self.vertices[i].y
        return abs(area) / 2.0

    def calculate_perimeter(self) -> float:
        """Calculate the perimeter of the polygon.

        Returns:
            Perimeter of the polygon
        """
        if len(self.vertices) < 2:
            return 0.0

        perimeter = 0.0
        n = len(self.vertices)
        for i in range(n):
            j = (i + 1) % n
            dx = self.vertices[j].x - self.vertices[i].x
            dy = self.vertices[j].y - self.vertices[i].y
            perimeter += math.sqrt(dx * dx + dy * dy)
        return perimeter

    def calculate_centroid(self) -> Optional[Point]:
        """Calculate the centroid of the polygon.

        Returns:
            Centroid as a Point object, or None if the polygon has less than 3 vertices
        """
        if len(self.vertices) < 3:
            return None

        # Calculate centroid using the weighted average of triangle centroids
        area = self.calculate_area()
        if area == 0:
            return None

        cx, cy = 0.0, 0.0
        n = len(self.vertices)
        for i in range(n):
            j = (i + 1) % n
            factor = (
                self.vertices[i].x * self.vertices[j].y
                - self.vertices[j].x * self.vertices[i].y
            )
            cx += (self.vertices[i].x + self.vertices[j].x) * factor
            cy += (self.vertices[i].y + self.vertices[j].y) * factor

        # Divide by 6 times the area
        cx /= 6.0 * area
        cy /= 6.0 * area

        return Point(cx, cy)

    def calculate_interior_angle_sum(self) -> float:
        """Calculate the sum of interior angles of the polygon.

        Returns:
            Sum of interior angles in degrees
        """
        if len(self.vertices) < 3:
            return 0.0

        # Sum of interior angles = (n - 2) * 180 degrees
        return (len(self.vertices) - 2) * 180.0

    def calculate_interior_angle(self, index: int) -> Optional[float]:
        """Calculate the interior angle at a specific vertex.

        Args:
            index: Index of the vertex

        Returns:
            Interior angle in degrees, or None if the index is invalid
        """
        if len(self.vertices) < 3 or index < 0 or index >= len(self.vertices):
            return None

        n = len(self.vertices)
        prev_idx = (index - 1) % n
        next_idx = (index + 1) % n

        # Get the vectors from the current vertex to the previous and next vertices
        prev_x = self.vertices[prev_idx].x - self.vertices[index].x
        prev_y = self.vertices[prev_idx].y - self.vertices[index].y
        next_x = self.vertices[next_idx].x - self.vertices[index].x
        next_y = self.vertices[next_idx].y - self.vertices[index].y

        # Calculate the angle between the vectors
        dot_product = prev_x * next_x + prev_y * next_y
        prev_mag = math.sqrt(prev_x * prev_x + prev_y * prev_y)
        next_mag = math.sqrt(next_x * next_x + next_y * next_y)

        if prev_mag == 0 or next_mag == 0:
            return None

        # Calculate the angle in radians and convert to degrees
        cos_angle = dot_product / (prev_mag * next_mag)
        # Clamp cos_angle to [-1, 1] to avoid numerical errors
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)

        # For interior angles, we need to check if the angle is reflex
        # We can use the cross product to determine if the angle is reflex
        cross_product = prev_x * next_y - prev_y * next_x
        if cross_product < 0:
            angle_deg = 360.0 - angle_deg

        return angle_deg

    def calculate_all_interior_angles(self) -> List[float]:
        """Calculate all interior angles of the polygon.

        Returns:
            List of interior angles in degrees
        """
        angles = []
        for i in range(len(self.vertices)):
            angle = self.calculate_interior_angle(i)
            if angle is not None:
                angles.append(angle)
        return angles

    def is_regular(self, tolerance: float = 1e-6) -> bool:
        """Check if the polygon is regular.

        A polygon is regular if all sides have the same length and all interior angles are equal.

        Args:
            tolerance: Tolerance for floating-point comparisons

        Returns:
            True if the polygon is regular, False otherwise
        """
        if len(self.vertices) < 3:
            return False

        # Check if all sides have the same length
        n = len(self.vertices)
        side_lengths = []
        for i in range(n):
            j = (i + 1) % n
            dx = self.vertices[j].x - self.vertices[i].x
            dy = self.vertices[j].y - self.vertices[i].y
            side_lengths.append(math.sqrt(dx * dx + dy * dy))

        first_length = side_lengths[0]
        for length in side_lengths[1:]:
            if abs(length - first_length) > tolerance:
                return False

        # Check if all interior angles are equal
        angles = self.calculate_all_interior_angles()
        if not angles:
            return False

        first_angle = angles[0]
        for angle in angles[1:]:
            if abs(angle - first_angle) > tolerance:
                return False

        return True

    def contains_point(
        self, point: Union[Point, Tuple[float, float]], include_boundary: bool = True
    ) -> bool:
        """Check if a point is inside the polygon using the ray casting algorithm.

        Args:
            point: Point to check as a Point object or (x, y) tuple
            include_boundary: Whether to include points on the boundary

        Returns:
            True if the point is inside the polygon, False otherwise
        """
        if len(self.vertices) < 3:
            return False

        # Convert point to x, y coordinates
        if isinstance(point, Point):
            x, y = point.x, point.y
        elif isinstance(point, tuple) and len(point) == 2:
            x, y = point[0], point[1]
        else:
            raise ValueError("Point must be a Point object or (x, y) tuple")

        # Check if the point is on the boundary
        if include_boundary:
            n = len(self.vertices)
            for i in range(n):
                j = (i + 1) % n
                # Check if the point is on the line segment
                if self._point_on_line_segment(
                    x,
                    y,
                    self.vertices[i].x,
                    self.vertices[i].y,
                    self.vertices[j].x,
                    self.vertices[j].y,
                ):
                    return True

        # Ray casting algorithm
        inside = False
        n = len(self.vertices)
        j = n - 1
        for i in range(n):
            if (self.vertices[i].y > y) != (self.vertices[j].y > y) and (
                x
                < (self.vertices[j].x - self.vertices[i].x)
                * (y - self.vertices[i].y)
                / (self.vertices[j].y - self.vertices[i].y)
                + self.vertices[i].x
            ):
                inside = not inside
            j = i

        return inside

    def _point_on_line_segment(
        self,
        px: float,
        py: float,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        tolerance: float = 1e-6,
    ) -> bool:
        """Check if a point is on a line segment.

        Args:
            px, py: Point coordinates
            x1, y1: First endpoint of the line segment
            x2, y2: Second endpoint of the line segment
            tolerance: Tolerance for floating-point comparisons

        Returns:
            True if the point is on the line segment, False otherwise
        """
        # Calculate the distance from the point to the line
        line_length_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2
        if line_length_squared < tolerance:
            # The line segment is actually a point
            return abs(px - x1) < tolerance and abs(py - y1) < tolerance

        # Calculate the projection of the point onto the line
        t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length_squared
        if t < 0 or t > 1:
            # The projection is outside the line segment
            return False

        # Calculate the distance from the point to the projection
        projection_x = x1 + t * (x2 - x1)
        projection_y = y1 + t * (y2 - y1)
        distance_squared = (px - projection_x) ** 2 + (py - projection_y) ** 2

        return distance_squared < tolerance

    def calculate_moment_of_inertia(self, density: float = 1.0) -> float:
        """Calculate the moment of inertia of the polygon around its centroid.

        Args:
            density: Density of the polygon (mass per unit area)

        Returns:
            Moment of inertia
        """
        if len(self.vertices) < 3:
            return 0.0

        # Get the centroid
        centroid = self.calculate_centroid()
        if centroid is None:
            return 0.0

        # Translate vertices so that the centroid is at the origin
        translated_vertices = []
        for vertex in self.vertices:
            translated_vertices.append(
                Point(vertex.x - centroid.x, vertex.y - centroid.y)
            )

        # Calculate the moment of inertia using the formula for a polygon
        # I = (1/12) * density * sum((x[i+1] - x[i]) *
        #     (y[i]^2 + y[i]*y[i+1] + y[i+1]^2) * (x[i]*y[i+1] - x[i+1]*y[i]))
        moment = 0.0
        n = len(translated_vertices)
        for i in range(n):
            j = (i + 1) % n
            x_i, y_i = translated_vertices[i].x, translated_vertices[i].y
            x_j, y_j = translated_vertices[j].x, translated_vertices[j].y

            term1 = y_i * y_i + y_i * y_j + y_j * y_j
            term2 = x_i * y_j - x_j * y_i

            moment += (x_j - x_i) * term1 * term2

        moment = abs(moment) / 12.0 * density
        return moment

    def create_regular_polygon(
        self,
        sides: int,
        center_x: float,
        center_y: float,
        radius: float,
        orientation: str = "vertex_top",
    ) -> None:
        """Create a regular polygon with the specified number of sides.

        Args:
            sides: Number of sides
            center_x: X-coordinate of the center
            center_y: Y-coordinate of the center
            radius: Radius of the circumscribed circle
            orientation: Orientation of the polygon ('vertex_top' or 'side_top')
        """
        if sides < 3:
            raise ValueError("Number of sides must be at least 3")

        self.vertices = []

        # Calculate the angle offset based on the orientation
        angle_offset = 0.0
        if orientation == "vertex_top":
            angle_offset = math.pi / 2  # 90 degrees
        elif orientation == "side_top":
            angle_offset = math.pi / 2 - math.pi / sides  # 90 degrees - (180/n) degrees

        # Calculate the vertices
        for i in range(sides):
            angle = angle_offset + 2 * math.pi * i / sides
            x = center_x + radius * math.cos(angle)
            y = center_y - radius * math.sin(
                angle
            )  # Negative because y-axis is down in PyQt
            self.vertices.append(Point(x, y))

    def rotate(self, angle_degrees: float, center: Optional[Point] = None) -> None:
        """Rotate the polygon around a center point.

        Args:
            angle_degrees: Rotation angle in degrees
            center: Center of rotation, or None to use the centroid
        """
        if not self.vertices:
            return

        if center is None:
            center = self.calculate_centroid()
            if center is None:
                # If centroid calculation fails, use the first vertex as the center
                center = self.vertices[0]

        # Convert angle to radians
        angle_rad = math.radians(angle_degrees)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)

        # Rotate each vertex
        for i, vertex in enumerate(self.vertices):
            # Translate to origin
            x = vertex.x - center.x
            y = vertex.y - center.y

            # Rotate
            new_x = x * cos_angle - y * sin_angle
            new_y = x * sin_angle + y * cos_angle

            # Translate back
            self.vertices[i] = Point(new_x + center.x, new_y + center.y)

    def scale(
        self, scale_x: float, scale_y: float, center: Optional[Point] = None
    ) -> None:
        """Scale the polygon.

        Args:
            scale_x: Scale factor in the x direction
            scale_y: Scale factor in the y direction
            center: Center of scaling, or None to use the centroid
        """
        if not self.vertices:
            return

        if center is None:
            center = self.calculate_centroid()
            if center is None:
                # If centroid calculation fails, use the first vertex as the center
                center = self.vertices[0]

        # Scale each vertex
        for i, vertex in enumerate(self.vertices):
            # Translate to origin
            x = vertex.x - center.x
            y = vertex.y - center.y

            # Scale
            new_x = x * scale_x
            new_y = y * scale_y

            # Translate back
            self.vertices[i] = Point(new_x + center.x, new_y + center.y)

    def translate(self, dx: float, dy: float) -> None:
        """Translate the polygon.

        Args:
            dx: Translation in the x direction
            dy: Translation in the y direction
        """
        if not self.vertices:
            return

        # Translate each vertex
        for i, vertex in enumerate(self.vertices):
            self.vertices[i] = Point(vertex.x + dx, vertex.y + dy)

    def get_bounding_box(self) -> Optional[Tuple[float, float, float, float]]:
        """Get the bounding box of the polygon.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y), or None if the polygon has no vertices
        """
        if not self.vertices:
            return None

        min_x = min(vertex.x for vertex in self.vertices)
        min_y = min(vertex.y for vertex in self.vertices)
        max_x = max(vertex.x for vertex in self.vertices)
        max_y = max(vertex.y for vertex in self.vertices)

        return (min_x, min_y, max_x, max_y)

    def to_polygon_model(
        self, name: str = "Polygon", style: Optional[Style] = None
    ) -> Polygon:
        """Convert to a Polygon model object.

        Args:
            name: Name of the polygon
            style: Style of the polygon, or None to use default style

        Returns:
            Polygon model object
        """
        if not style:
            style = Style()
            style.stroke_color = QColor(0, 0, 0)
            style.fill_color = QColor(255, 255, 255, 50)
            style.stroke_width = 1.0
            style.stroke_style = Qt.PenStyle.SolidLine
            style.fill_style = Qt.BrushStyle.SolidPattern

        return Polygon(self.vertices, name=name, style=style)

    def draw(
        self,
        painter: QPainter,
        stroke_color: QColor = QColor(0, 0, 0),
        fill_color: QColor = QColor(255, 255, 255, 50),
        stroke_width: float = 1.0,
    ) -> None:
        """Draw the polygon using a QPainter.

        Args:
            painter: QPainter object
            stroke_color: Color of the stroke
            fill_color: Color of the fill
            stroke_width: Width of the stroke
        """
        if not self.vertices:
            return

        # Create a path for the polygon
        path = QPainterPath()
        path.moveTo(self.vertices[0].x, self.vertices[0].y)
        for vertex in self.vertices[1:]:
            path.lineTo(vertex.x, vertex.y)
        path.closeSubpath()

        # Save the current painter state
        painter.save()

        # Set the pen and brush
        pen = QPen(stroke_color)
        pen.setWidthF(stroke_width)
        painter.setPen(pen)
        painter.setBrush(QBrush(fill_color))

        # Draw the polygon
        painter.drawPath(path)

        # Restore the painter state
        painter.restore()


class PolygonCalculatorWidget(QWidget):
    """Widget for displaying and interacting with a polygon calculator."""

    def __init__(self, parent=None):
        """Initialize the widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculator = PolygonCalculator()
        self.setMinimumSize(400, 400)

    def set_calculator(self, calculator: PolygonCalculator) -> None:
        """Set the polygon calculator.

        Args:
            calculator: Polygon calculator
        """
        self.calculator = calculator
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the widget.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fill the background
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        # Draw the polygon
        if self.calculator and self.calculator.vertices:
            self.calculator.draw(painter)

            # Draw the centroid
            centroid = self.calculator.calculate_centroid()
            if centroid:
                painter.setPen(QPen(QColor(255, 0, 0), 2))
                painter.drawEllipse(QPointF(centroid.x, centroid.y), 5, 5)

            # Draw vertex labels
            painter.setPen(QPen(QColor(0, 0, 255), 1))
            for i, vertex in enumerate(self.calculator.vertices):
                painter.drawText(QPointF(vertex.x + 5, vertex.y - 5), f"{i}")
