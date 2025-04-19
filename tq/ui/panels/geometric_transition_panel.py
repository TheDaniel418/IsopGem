"""
Purpose: Provides a panel for calculating ternary transitions between vertices of regular polygons

This file is part of the tq pillar and serves as a UI component.
It is responsible for visualizing regular polygons and calculating
the ternary transitions between their vertices.

Key components:
- GeometricTransitionPanel: Panel for visualizing and calculating transitions in regular polygons

Dependencies:
- PyQt6: For the user interface components
- tq.utils.ternary_converter: For converting between decimal and ternary
- tq.utils.ternary_transition: For applying the transition operation
- geometry.calculator.regular_polygon_calculator: For polygon calculations

Related files:
- tq/ui/tq_tab.py: Tab that provides a button to open this panel
- tq/utils/ternary_transition.py: Core transition functionality
- geometry/calculator/regular_polygon_calculator.py: Polygon calculation utilities
"""

import math
from typing import Dict, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from geometry.calculator.regular_polygon_calculator import RegularPolygonCalculator

# Import services for "Send to" functionality
from tq.services import tq_analysis_service
from tq.utils.ternary_converter import decimal_to_ternary, ternary_to_decimal
from tq.utils.ternary_transition import TernaryTransition

# Import for polygon calculator
try:
    from gematria.ui.dialogs.send_to_polygon_dialog import SendToPolygonDialog
    from geometry.services.polygon_service import PolygonService

    POLYCALC_AVAILABLE = True
except ImportError:
    POLYCALC_AVAILABLE = False


class PolygonVisualizerWidget(QWidget):
    """Widget for visualizing a regular polygon with transition values."""

    def __init__(self, parent=None):
        """Initialize the polygon visualizer widget."""
        super().__init__(parent)
        self.calculator = RegularPolygonCalculator(sides=3, radius=100.0)
        self.transitions: Dict[
            Tuple[int, int], int
        ] = {}  # (vertex1, vertex2) -> transition value
        self.show_transitions = True
        self.vertex_values: Dict[int, int] = {}  # vertex index -> value
        self.setMinimumSize(400, 400)
        self.setStyleSheet(
            """
            background-color: white;
            border-radius: 5px;
        """
        )

    def set_sides(self, sides: int):
        """Set the number of sides for the polygon.

        Args:
            sides: Number of sides (minimum 3)
        """
        self.calculator.set_sides(sides)
        self.update()

    def set_transitions(
        self, transitions: Dict[Tuple[int, int], int], special_pairs=None
    ):
        """Set the transition values between vertices.

        Args:
            transitions: Dictionary mapping vertex pairs to transition values
            special_pairs: Optional list of special transition pairs to highlight
        """
        self.transitions = transitions
        self.special_pairs = special_pairs if special_pairs is not None else []
        self.update()

    def toggle_transitions(self, show: bool):
        """Toggle the display of transition values.

        Args:
            show: Whether to show transition values
        """
        self.show_transitions = show
        self.update()

    def set_vertex_value(self, vertex_index: int, value: int):
        """Set the value for a specific vertex.

        Args:
            vertex_index: Index of the vertex
            value: Value to assign to the vertex
        """
        self.vertex_values[vertex_index] = value
        self.update()

    def paintEvent(self, event):
        """Paint the polygon and transitions."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate center and scale
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        # Check if we're drawing a cuboctahedron
        is_cuboctahedron = (
            hasattr(self, "special_pairs")
            and len(self.vertex_values) == 12
            and hasattr(self, "special_shape_id")
            and self.special_shape_id == "cuboctahedron"
        )

        # Get the polygon points
        if is_cuboctahedron:
            # Use a completely custom drawing for the cuboctahedron
            polygon = self._draw_custom_cuboctahedron(
                painter, width, height, center_x, center_y
            )
        else:
            # Calculate scale factor to fit the polygon in the widget
            scale_factor = min(width, height) * 0.4 / self.calculator.radius

            # Get the vertices
            vertices = self.calculator.get_vertices(0, 0)

            # Create a polygon for drawing
            polygon = []
            for vertex in vertices:
                # Scale and translate the vertex
                x = center_x + vertex.x * scale_factor
                y = center_y + vertex.y * scale_factor
                polygon.append(QPointF(x, y))

            # Draw the polygon with gradient fill
            painter.setPen(QPen(QColor(0, 0, 0), 2))

            # Create a gradient for the polygon fill
            gradient = QRadialGradient(center_x, center_y, min(width, height) * 0.4)
            gradient.setColorAt(0, QColor(240, 240, 255))  # Light blue at center
            gradient.setColorAt(1, QColor(200, 200, 240))  # Darker blue at edges
            painter.setBrush(QBrush(gradient))

            # Draw the polygon as a path
            path = QPainterPath()
            if polygon:
                path.moveTo(polygon[0])
                for point in polygon[1:]:
                    path.lineTo(point)
                path.closeSubpath()
                painter.drawPath(path)

                # Draw a subtle grid in the background
                painter.setPen(QPen(QColor(220, 220, 240), 0.5, Qt.PenStyle.DotLine))
                grid_size = 20
                for x in range(0, width, grid_size):
                    painter.drawLine(x, 0, x, height)
                for y in range(0, height, grid_size):
                    painter.drawLine(0, y, width, y)

                # Draw a circle at the center
                painter.setPen(QPen(QColor(100, 100, 180), 1))
                painter.setBrush(QBrush(QColor(220, 220, 255)))
                painter.drawEllipse(QPointF(center_x, center_y), 10, 10)

        # Draw vertex numbers
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        for i, point in enumerate(polygon):
            # Create a gradient for the vertex circle
            vertex_gradient = QRadialGradient(point.x(), point.y(), 18)
            vertex_gradient.setColorAt(0, QColor(220, 220, 255))
            vertex_gradient.setColorAt(1, QColor(180, 180, 240))

            # Draw a circle at each vertex with gradient and shadow
            # First draw shadow
            painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(point.x() + 2, point.y() + 2), 15, 15)

            # Then draw the vertex circle
            painter.setBrush(QBrush(vertex_gradient))
            painter.setPen(QPen(QColor(100, 100, 180), 1.5))
            painter.drawEllipse(point, 15, 15)

            # Draw the vertex number
            painter.setPen(QPen(QColor(0, 0, 100)))
            text_rect = QRectF(point.x() - 10, point.y() - 10, 20, 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, str(i))

            # If this vertex has a value assigned, display it inside the vertex circle
            # with a different color to make it stand out
            if i in self.vertex_values:
                # Use a smaller font for the value
                painter.setFont(QFont("Arial", 8))

                # Draw a small colored rectangle inside the vertex circle
                value_rect = QRectF(point.x() - 8, point.y() + 2, 16, 12)

                # Draw the value background
                painter.setBrush(QBrush(QColor(255, 255, 200)))
                painter.setPen(QPen(QColor(0, 100, 0), 1.0))
                painter.drawRect(value_rect)

                # Draw the value text
                painter.setPen(QPen(QColor(0, 100, 0)))
                painter.drawText(
                    value_rect, Qt.AlignmentFlag.AlignCenter, str(self.vertex_values[i])
                )

        # Draw transitions if enabled and not a cuboctahedron
        is_cuboctahedron = (
            hasattr(self, "special_shape_id")
            and self.special_shape_id == "cuboctahedron"
        )

        if self.show_transitions and self.transitions and not is_cuboctahedron:
            painter.setFont(QFont("Arial", 9))

            for (v1, v2), value in self.transitions.items():
                if v1 < len(polygon) and v2 < len(polygon):
                    # Get the points for the vertices
                    p1 = polygon[v1]
                    p2 = polygon[v2]

                    # Check if this is a special transition pair to highlight
                    is_special = hasattr(self, "special_pairs") and (
                        (v1, v2) in self.special_pairs or (v2, v1) in self.special_pairs
                    )

                    # Draw a line between the vertices with different style for special pairs
                    if is_special:
                        # Use a solid, thicker, more vibrant line for special transitions
                        painter.setPen(
                            QPen(QColor(100, 50, 200, 220), 2.5, Qt.PenStyle.SolidLine)
                        )
                    else:
                        # Use a dashed, thinner line for regular transitions
                        painter.setPen(
                            QPen(QColor(100, 100, 200, 180), 1.5, Qt.PenStyle.DashLine)
                        )

                    painter.drawLine(p1, p2)

                    # Only draw transition labels if not a cuboctahedron
                    if not is_cuboctahedron:
                        # Calculate line properties for positioning
                        dx = p2.x() - p1.x()
                        dy = p2.y() - p1.y()
                        line_length = math.sqrt(dx * dx + dy * dy)

                        # Calculate a better position for the transition value
                        # Position the label at a point along the line, but offset to avoid overlapping
                        # with other labels and vertices

                        # Use a smaller label size
                        label_width = 24
                        label_height = 18

                        # Find a position along the line that's not too close to either vertex
                        # Use a different position for each pair to reduce overlapping
                        position_factor = 0.5  # Default to midpoint

                        # Adjust position based on vertex indices to spread out labels
                        if (v1 + v2) % 3 == 0:
                            position_factor = 0.3  # Closer to first vertex
                        elif (v1 + v2) % 3 == 1:
                            position_factor = 0.5  # Middle
                        else:
                            position_factor = 0.7  # Closer to second vertex

                        # Calculate position
                        label_x = p1.x() + (p2.x() - p1.x()) * position_factor
                        label_y = p1.y() + (p2.y() - p1.y()) * position_factor

                        # Add a small offset perpendicular to the line to avoid sitting directly on the line
                        if line_length > 0:
                            # Calculate perpendicular direction
                            nx = -dy / line_length * 8  # Offset distance
                            ny = dx / line_length * 8

                            # Apply offset
                            label_x += nx
                            label_y += ny

                        # Create the label rectangle
                        text_rect = QRectF(
                            label_x - label_width / 2,
                            label_y - label_height / 2,
                            label_width,
                            label_height,
                        )

                        # Draw a background for the transition value
                        painter.setBrush(QBrush(QColor(255, 255, 220)))
                        painter.setPen(QPen(QColor(100, 100, 200, 200), 1.0))
                        painter.drawRoundedRect(text_rect, 5, 5)

                        # Draw the transition value
                        painter.setPen(QPen(QColor(0, 0, 100)))
                        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                        painter.drawText(
                            text_rect, Qt.AlignmentFlag.AlignCenter, str(value)
                        )

    def _draw_custom_cuboctahedron(self, painter, width, height, center_x, center_y):
        """Draw only the vertices of the 2D cuboctahedron for custom line drawing."""
        # Define the size of the drawing
        size = min(width, height) * 0.4

        # Create a light purple background
        painter.setPen(Qt.PenStyle.NoPen)
        gradient = QRadialGradient(center_x, center_y, size)
        gradient.setColorAt(0, QColor(230, 230, 255))  # Very light purple at center
        gradient.setColorAt(1, QColor(200, 200, 240))  # Slightly darker at edges
        painter.setBrush(QBrush(gradient))
        # Use QRectF for the ellipse to handle float values
        painter.drawEllipse(
            QRectF(center_x - size, center_y - size, size * 2, size * 2)
        )

        # Define the exact points for the cuboctahedron as shown in your reference image
        # This is a custom shape, not a regular polygon
        points = []

        # Define the outer hexagon points
        outer_hexagon = []
        for i in range(6):
            angle = i * math.pi / 3  # 6 points evenly spaced
            x = center_x + size * 0.9 * math.cos(angle)
            y = center_y + size * 0.9 * math.sin(angle)
            outer_hexagon.append(QPointF(x, y))

        # Define the inner triangles with a 30-degree rotation to the left
        # Convert 30 degrees to radians
        rotation = math.pi / 6  # 30 degrees in radians

        # First triangle (pointing up) - rotated 30 degrees counterclockwise
        triangle1 = []
        for i in [0, 2, 4]:  # Use vertices 0, 2, 4 of the hexagon (alternating)
            angle = (
                i * math.pi / 3 - rotation
            )  # Subtract rotation to rotate counterclockwise
            x = center_x + size * 0.4 * math.cos(angle)
            y = center_y + size * 0.4 * math.sin(angle)
            triangle1.append(QPointF(x, y))

        # Second triangle (pointing down) - rotated 30 degrees counterclockwise
        triangle2 = []
        for i in [1, 3, 5]:  # Use vertices 1, 3, 5 of the hexagon (alternating)
            angle = (
                i * math.pi / 3 - rotation
            )  # Subtract rotation to rotate counterclockwise
            x = center_x + size * 0.4 * math.cos(angle)
            y = center_y + size * 0.4 * math.sin(angle)
            triangle2.append(QPointF(x, y))

        # Combine all points
        points = outer_hexagon + triangle1 + triangle2

        # Draw a small circle at the center
        painter.setBrush(QBrush(QColor(200, 200, 240)))
        painter.drawEllipse(QPointF(center_x, center_y), 10.0, 10.0)

        # Draw the front and back side connections
        self._draw_front_connections(painter, points)
        self._draw_back_connections(painter, points)

        return points

    def _draw_front_connections(self, painter, points):
        """Draw the front side connections of the cuboctahedron."""
        # Set up the pen for front connections - solid, thicker lines
        front_pen = QPen(QColor(80, 40, 180), 2.5, Qt.PenStyle.SolidLine)
        painter.setPen(front_pen)

        # First triangle: 8 to 6, 6 to 7, 7 to 8
        # Using vertex indices (0-11) directly
        painter.drawLine(points[8], points[6])  # 8 to 6
        painter.drawLine(points[6], points[7])  # 6 to 7
        painter.drawLine(points[7], points[8])  # 7 to 8

        # Additional front connections: 5 to 6, 6 to 8, 8 to 4, 4 to 5
        painter.drawLine(points[5], points[6])  # 5 to 6
        painter.drawLine(points[6], points[8])  # 6 to 8
        painter.drawLine(points[8], points[4])  # 8 to 4
        painter.drawLine(points[4], points[5])  # 4 to 5

        # Connection: 8, 4, 3
        painter.drawLine(points[8], points[4])  # 8 to 4 (already drawn above)
        painter.drawLine(points[4], points[3])  # 4 to 3
        painter.drawLine(points[3], points[8])  # 3 to 8

        # New connections: 3 to 2, 2 to 7
        painter.drawLine(points[3], points[2])  # 3 to 2
        painter.drawLine(points[2], points[7])  # 2 to 7

        # New connections: 7 to 2, 2 to 1, 1 to 7
        # Note: 7 to 2 is already drawn above
        painter.drawLine(points[2], points[1])  # 2 to 1
        painter.drawLine(points[1], points[7])  # 1 to 7

        # New connections: 5 to 0, 0 to 6, 0 to 1
        painter.drawLine(points[5], points[0])  # 5 to 0
        painter.drawLine(points[0], points[6])  # 0 to 6
        painter.drawLine(points[0], points[1])  # 0 to 1

    def _draw_back_connections(self, painter, points):
        """Draw the back side connections of the cuboctahedron with lighter, thinner lines."""
        # Set up the pen for back connections - lighter, thinner, dashed lines
        back_pen = QPen(QColor(180, 160, 220), 1.5, Qt.PenStyle.DashLine)
        painter.setPen(back_pen)

        # First back triangle: 12-10-11 (using 0-based indices: 11-9-10)
        painter.drawLine(points[11], points[9])  # 12 to 10
        painter.drawLine(points[9], points[10])  # 10 to 11
        painter.drawLine(points[10], points[11])  # 11 to 12

        # Additional back connections
        painter.drawLine(points[11], points[4])  # 11 to 4 (12 to 5)
        painter.drawLine(points[11], points[5])  # 11 to 5 (12 to 6)
        painter.drawLine(points[10], points[3])  # 10 to 3 (11 to 4)
        painter.drawLine(points[10], points[2])  # 10 to 2 (11 to 3)
        painter.drawLine(points[9], points[0])  # 9 to 0 (10 to 1)
        painter.drawLine(points[9], points[1])  # 9 to 1 (10 to 2)

        # Draw center-crossing diagonals with a different style
        self._draw_center_diagonals(painter, points)

    def _draw_center_diagonals(self, painter, points):
        """Draw the center-crossing diagonal connections with a distinct style."""
        # Set up the pen for center diagonals - dotted, medium thickness, different color
        center_pen = QPen(QColor(100, 180, 100), 1.8, Qt.PenStyle.DotLine)
        painter.setPen(center_pen)

        # Draw the 6 center-crossing diagonals
        painter.drawLine(points[8], points[9])  # 8 to 9
        painter.drawLine(points[6], points[10])  # 6 to 10
        painter.drawLine(points[7], points[11])  # 7 to 11
        painter.drawLine(points[4], points[1])  # 4 to 1
        painter.drawLine(points[2], points[5])  # 2 to 5
        painter.drawLine(points[3], points[0])  # 3 to 0


class GeometricTransitionPanel(QFrame):
    """
    Panel for calculating ternary transitions between vertices of regular polygons.

    Allows users to:
    1. Select the number of sides for a regular polygon
    2. Visualize the polygon
    3. Calculate ternary transitions between all vertices
    4. View the transition results in a table
    """

    def __init__(self, parent=None):
        """Initialize the geometric transition panel."""
        super().__init__(parent)

        # Create the ternary transition utility
        self.transition = TernaryTransition()

        # Initialize special shape attributes
        self.special_transition_pairs = "all"  # Default to calculating all transitions

        # Set up the main layout
        self.setup_ui()

        # Set up context menus for tables
        self._setup_context_menus()

    def setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create title
        title_label = QLabel("2D Geometric Transitions")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Create description
        description = QLabel(
            "Visualize regular polygons and calculate ternary transitions between vertices."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px; color: #666;")
        main_layout.addWidget(description)

        # Create input area
        input_layout = QHBoxLayout()

        # Sides input
        sides_label = QLabel("Number of Sides:")
        self.sides_input = QSpinBox()
        self.sides_input.setMinimum(3)
        self.sides_input.setMaximum(100)
        self.sides_input.setValue(5)
        self.sides_input.valueChanged.connect(self._update_polygon)

        # Calculate button
        calculate_button = QPushButton("Calculate Transitions")
        calculate_button.clicked.connect(self._calculate_transitions)

        # Special shapes dropdown
        special_shapes_label = QLabel("Special Shape:")
        self.special_shape_combo = QComboBox()
        self.special_shape_combo.addItem("Custom", "custom")  # Default - user-defined
        self.special_shape_combo.addItem("Unicursal Hexagram", "unicursal_hexagram")
        self.special_shape_combo.addItem("The Atomic Star", "atomic_star")
        self.special_shape_combo.addItem("The Mountain Star", "mountain_star")
        self.special_shape_combo.addItem("The Lovely Star", "lovely_star")
        self.special_shape_combo.addItem("2D Cuboctahedron", "cuboctahedron")
        self.special_shape_combo.currentIndexChanged.connect(
            self._special_shape_selected
        )

        # Add widgets to input layout
        input_layout.addWidget(sides_label)
        input_layout.addWidget(self.sides_input)
        input_layout.addWidget(calculate_button)
        input_layout.addSpacing(20)  # Add some space between controls
        input_layout.addWidget(special_shapes_label)
        input_layout.addWidget(self.special_shape_combo)
        input_layout.addStretch()

        main_layout.addLayout(input_layout)

        # Create content area with 3 panes: vertex editor, polygon visualizer, and results
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)  # Add more spacing between panes

        # Left pane: Vertex editor
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        left_panel.setMinimumWidth(180)  # Set minimum width
        left_panel.setMaximumWidth(250)  # Limit maximum width
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)  # Add padding

        vertex_editor_label = QLabel("Vertex Values:")
        vertex_editor_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-bottom: 5px;"
        )
        left_layout.addWidget(vertex_editor_label)

        # Create a scrollable area for vertex inputs
        vertex_scroll = QScrollArea()
        vertex_scroll.setWidgetResizable(True)
        vertex_scroll.setFrameShape(QFrame.Shape.NoFrame)  # Remove frame
        vertex_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        # Create content widget for the scroll area
        vertex_content = QWidget()
        vertex_content_layout = QVBoxLayout(vertex_content)
        vertex_content_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        vertex_content_layout.setSpacing(8)  # Add spacing between items

        # Create header for the vertex inputs
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 0, 5, 0)  # Minimal margins

        vertex_header = QLabel("Vertex")
        vertex_header.setStyleSheet("font-weight: bold;")
        value_header = QLabel("Value")
        value_header.setStyleSheet("font-weight: bold;")

        header_layout.addWidget(vertex_header)
        header_layout.addWidget(value_header)
        vertex_content_layout.addWidget(header_widget)

        # Create a container for the vertex inputs
        inputs_container = QWidget()
        self.vertex_inputs_grid = QGridLayout(inputs_container)
        self.vertex_inputs_grid.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.vertex_inputs_grid.setSpacing(8)  # Add spacing
        self.vertex_inputs_grid.setColumnStretch(1, 1)  # Make value column stretch

        vertex_content_layout.addWidget(inputs_container)
        vertex_content_layout.addStretch()  # Add stretch at the bottom

        vertex_scroll.setWidget(vertex_content)
        left_layout.addWidget(vertex_scroll)

        # Add the left panel to the content layout
        content_layout.addWidget(left_panel, 1)

        # Middle pane: Polygon visualizer
        middle_panel = QFrame()
        middle_panel.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        middle_panel.setMinimumSize(400, 400)  # Set minimum size
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(10, 10, 10, 10)  # Add padding

        visualizer_label = QLabel("Polygon Visualization:")
        visualizer_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-bottom: 5px;"
        )
        middle_layout.addWidget(visualizer_label)

        # Create a container for the visualizer to ensure proper sizing
        visualizer_container = QWidget()
        visualizer_container.setMinimumSize(380, 380)  # Set minimum size
        visualizer_layout = QVBoxLayout(visualizer_container)
        visualizer_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        self.polygon_visualizer = PolygonVisualizerWidget()
        visualizer_layout.addWidget(self.polygon_visualizer)

        middle_layout.addWidget(visualizer_container, 1)  # Add with stretch

        # Add the middle panel to the content layout
        content_layout.addWidget(middle_panel, 2)  # Give more space to the visualizer

        # Right pane: Results area
        right_panel = QFrame()
        right_panel.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        right_panel.setMinimumWidth(500)  # Increased minimum width to fit all columns
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)  # Add padding

        results_label = QLabel("Transition Results:")
        results_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; margin-bottom: 5px;"
        )
        right_layout.addWidget(results_label)

        # Create a tab widget for different result views
        self.results_tab_widget = QTabWidget()
        self.results_tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background: white;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #c0c0c0;
                border-bottom-color: #c0c0c0;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #f0f0f0;
            }
            QTabBar::tab:selected {
                border-bottom-color: white;
            }
        """
        )

        # Tab 1: All Transitions
        all_transitions_tab = QWidget()
        all_transitions_layout = QVBoxLayout(all_transitions_tab)
        all_transitions_layout.setContentsMargins(5, 5, 5, 5)

        # Create a table for all transitions
        self.results_table = QTableWidget(0, 6)  # Rows will be added dynamically
        self.results_table.setHorizontalHeaderLabels(
            [
                "Vertex 1",
                "Value 1",
                "Vertex 2",
                "Value 2",
                "Transition (Dec)",
                "Transition (Tern)",
            ]
        )

        # Set column widths to ensure all columns are visible
        self.results_table.setColumnWidth(0, 70)  # Vertex 1
        self.results_table.setColumnWidth(1, 70)  # Value 1
        self.results_table.setColumnWidth(2, 70)  # Vertex 2
        self.results_table.setColumnWidth(3, 70)  # Value 2
        self.results_table.setColumnWidth(4, 110)  # Transition (Dec)
        self.results_table.setColumnWidth(5, 110)  # Transition (Tern)

        # Enable horizontal header stretch to use available space
        self.results_table.horizontalHeader().setStretchLastSection(True)

        # Set alternating row colors for better readability
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet(
            """
            alternate-background-color: #f0f0f0;
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                font-weight: bold;
                border: 1px solid #c0c0c0;
            }
        """
        )

        all_transitions_layout.addWidget(self.results_table)

        # Tab 2: Edge Sums
        edge_sums_tab = QWidget()
        edge_sums_layout = QVBoxLayout(edge_sums_tab)
        edge_sums_layout.setContentsMargins(5, 5, 5, 5)

        # Create a table for edge sums
        self.edge_sums_table = QTableWidget(0, 3)  # Rows will be added dynamically
        self.edge_sums_table.setHorizontalHeaderLabels(
            ["Edge Type", "Sum (Dec)", "Sum (Tern)"]
        )

        # Set column widths
        self.edge_sums_table.setColumnWidth(0, 150)  # Edge Type
        self.edge_sums_table.setColumnWidth(1, 100)  # Sum (Dec)
        self.edge_sums_table.setColumnWidth(2, 150)  # Sum (Tern)

        # Enable horizontal header stretch
        self.edge_sums_table.horizontalHeader().setStretchLastSection(True)

        # Set alternating row colors
        self.edge_sums_table.setAlternatingRowColors(True)
        self.edge_sums_table.setStyleSheet(
            """
            alternate-background-color: #f0f0f0;
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                font-weight: bold;
                border: 1px solid #c0c0c0;
            }
        """
        )

        edge_sums_layout.addWidget(self.edge_sums_table)

        # Tab 3: Diagonal Sums
        diagonal_sums_tab = QWidget()
        diagonal_sums_layout = QVBoxLayout(diagonal_sums_tab)
        diagonal_sums_layout.setContentsMargins(5, 5, 5, 5)

        # Create a table for diagonal sums
        self.diagonal_sums_table = QTableWidget(0, 3)  # Rows will be added dynamically
        self.diagonal_sums_table.setHorizontalHeaderLabels(
            ["Skip Value", "Sum (Dec)", "Sum (Tern)"]
        )

        # Set column widths
        self.diagonal_sums_table.setColumnWidth(0, 100)  # Skip Value
        self.diagonal_sums_table.setColumnWidth(1, 100)  # Sum (Dec)
        self.diagonal_sums_table.setColumnWidth(2, 150)  # Sum (Tern)

        # Enable horizontal header stretch
        self.diagonal_sums_table.horizontalHeader().setStretchLastSection(True)

        # Set alternating row colors
        self.diagonal_sums_table.setAlternatingRowColors(True)
        self.diagonal_sums_table.setStyleSheet(
            """
            alternate-background-color: #f0f0f0;
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                font-weight: bold;
                border: 1px solid #c0c0c0;
            }
        """
        )

        diagonal_sums_layout.addWidget(self.diagonal_sums_table)

        # Tab 4: Total Sum
        total_sum_tab = QWidget()
        total_sum_layout = QVBoxLayout(total_sum_tab)
        total_sum_layout.setContentsMargins(5, 5, 5, 5)

        # Create a table for the total sums
        self.total_sum_table = QTableWidget(2, 3)  # Two rows, three columns
        self.total_sum_table.setHorizontalHeaderLabels(
            ["Sum Type", "Sum (Dec)", "Sum (Tern)"]
        )

        # Set the row labels
        self.total_sum_table.setVerticalHeaderLabels(["Vertex Values", "Transitions"])

        # Set the first column values
        self.total_sum_table.setItem(0, 0, QTableWidgetItem("Sum of Vertex Values"))
        self.total_sum_table.setItem(1, 0, QTableWidgetItem("Sum of All Transitions"))

        # Set column widths
        self.total_sum_table.setColumnWidth(0, 180)  # Sum Type
        self.total_sum_table.setColumnWidth(1, 120)  # Sum (Dec)
        self.total_sum_table.setColumnWidth(2, 150)  # Sum (Tern)

        # Enable horizontal header stretch
        self.total_sum_table.horizontalHeader().setStretchLastSection(True)

        # Set alternating row colors
        self.total_sum_table.setAlternatingRowColors(True)
        self.total_sum_table.setStyleSheet(
            """
            alternate-background-color: #f0f0f0;
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                font-weight: bold;
                border: 1px solid #c0c0c0;
            }
        """
        )

        # Add a description label
        total_sum_description = QLabel(
            "This tab shows the sum of all vertex values and the sum of all transitions in the polygon. "
            "These sums can be used to analyze the relationship between vertex values and their transitions."
        )
        total_sum_description.setWordWrap(True)
        total_sum_description.setStyleSheet(
            "font-style: italic; color: #555; margin-bottom: 10px;"
        )
        total_sum_layout.addWidget(total_sum_description)

        total_sum_layout.addWidget(self.total_sum_table)

        # Add a spacer to push the content to the top
        total_sum_layout.addStretch()

        # Tab 5: Diagonal Transitions
        diagonal_transitions_tab = QWidget()
        diagonal_transitions_layout = QVBoxLayout(diagonal_transitions_tab)
        diagonal_transitions_layout.setContentsMargins(5, 5, 5, 5)

        # Add a description label
        diagonal_transitions_description = QLabel(
            "This tab shows transitions between the sums of different diagonal groups. "
            "Each diagonal group is defined by its skip value, and we calculate the transition "
            "between the sums of these groups to analyze higher-level patterns."
        )
        diagonal_transitions_description.setWordWrap(True)
        diagonal_transitions_description.setStyleSheet(
            "font-style: italic; color: #555; margin-bottom: 10px;"
        )
        diagonal_transitions_layout.addWidget(diagonal_transitions_description)

        # Create a table for diagonal transitions
        self.diagonal_transitions_table = QTableWidget(
            0, 5
        )  # Rows will be added dynamically
        self.diagonal_transitions_table.setHorizontalHeaderLabels(
            ["Skip 1", "Skip 2", "Transition (Dec)", "Transition (Tern)", "Notes"]
        )

        # Set column widths
        self.diagonal_transitions_table.setColumnWidth(0, 70)  # Skip 1
        self.diagonal_transitions_table.setColumnWidth(1, 70)  # Skip 2
        self.diagonal_transitions_table.setColumnWidth(2, 120)  # Transition (Dec)
        self.diagonal_transitions_table.setColumnWidth(3, 120)  # Transition (Tern)
        self.diagonal_transitions_table.setColumnWidth(4, 150)  # Notes

        # Enable horizontal header stretch
        self.diagonal_transitions_table.horizontalHeader().setStretchLastSection(True)

        # Set alternating row colors
        self.diagonal_transitions_table.setAlternatingRowColors(True)
        self.diagonal_transitions_table.setStyleSheet(
            """
            alternate-background-color: #f0f0f0;
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                font-weight: bold;
                border: 1px solid #c0c0c0;
            }
        """
        )

        diagonal_transitions_layout.addWidget(self.diagonal_transitions_table)

        # Add tabs to the tab widget
        self.results_tab_widget.addTab(all_transitions_tab, "All Transitions")
        self.results_tab_widget.addTab(edge_sums_tab, "Edge Sums")
        self.results_tab_widget.addTab(diagonal_sums_tab, "Diagonal Sums")
        self.results_tab_widget.addTab(diagonal_transitions_tab, "Diagonal Transitions")
        self.results_tab_widget.addTab(total_sum_tab, "Total Sum")

        # Add the tab widget to the right panel
        right_layout.addWidget(self.results_tab_widget)

        # Add the right panel to the content layout
        content_layout.addWidget(
            right_panel, 2
        )  # Increased proportion to give more space

        main_layout.addLayout(content_layout, 1)

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 5px; }")

        # Initialize the polygon
        self._update_polygon()

    def _update_polygon(self):
        """Update the polygon based on the current settings."""
        sides = self.sides_input.value()
        self.polygon_visualizer.set_sides(sides)

        # Clear existing vertex inputs
        while self.vertex_inputs_grid.count():
            item = self.vertex_inputs_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create new vertex inputs
        self.vertex_inputs = {}  # Store references to the input fields

        # Add input fields for each vertex
        for i in range(sides):
            # Create a row widget for each vertex
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
            row_layout.setSpacing(10)  # Add spacing between label and input

            # Vertex label with background color based on index
            vertex_label = QLabel(f"Vertex {i}")
            vertex_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Create a color based on the vertex index (cycle through colors)
            hue = (i * 40) % 360  # Cycle through hues
            color = QColor()
            color.setHsv(hue, 70, 240)  # Soft pastel colors

            # Style the label with the color
            vertex_label.setStyleSheet(
                f"""
                background-color: {color.name()};
                color: #000000;
                padding: 6px;
                border-radius: 4px;
                font-weight: bold;
            """
            )
            vertex_label.setFixedWidth(80)  # Fixed width for consistency

            # Value input with styling
            value_input = QLineEdit()
            value_input.setPlaceholderText(f"Value for V{i}")
            value_input.setText(str(i + 1))  # Default value is vertex index + 1
            value_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_input.setStyleSheet(
                """
                padding: 6px;
                border: 1px solid #aaa;
                border-radius: 4px;
                background-color: #ffffff;
            """
            )

            # Connect the input field to update the vertex value
            value_input.textChanged.connect(
                lambda text, idx=i: self._update_vertex_value(idx, text)
            )

            # Add widgets to the row
            row_layout.addWidget(vertex_label)
            row_layout.addWidget(value_input)

            # Add the row to the grid
            self.vertex_inputs_grid.addWidget(row_widget, i, 0)
            self.vertex_inputs[i] = value_input

            # Initialize the vertex value in the visualizer
            self._update_vertex_value(i, str(i + 1))

    def _update_vertex_value(self, vertex_index: int, text: str):
        """Update the value of a vertex based on user input.

        Args:
            vertex_index: Index of the vertex to update
            text: New value as text
        """
        try:
            value = int(text)
            self.polygon_visualizer.set_vertex_value(vertex_index, value)
        except ValueError:
            # If the input is not a valid integer, don't update the vertex value
            pass

    def _calculate_transitions(self):
        """Calculate the ternary transitions between vertices."""
        sides = self.sides_input.value()

        # We don't need the polygon calculator for the transition calculations
        # We'll just use the vertex values from the input fields

        # Calculate transitions between vertices
        transitions = {}
        transition_results = []

        # First, ensure all vertex values are valid
        for i in range(sides):
            try:
                # Try to get the value from the input field
                value = int(self.vertex_inputs[i].text())
                # Update the vertex value in the visualizer
                self.polygon_visualizer.set_vertex_value(i, value)
            except (ValueError, KeyError):
                # If the input is invalid, set a default value (vertex index + 1)
                default_value = i + 1
                if i in self.vertex_inputs:
                    self.vertex_inputs[i].setText(str(default_value))
                self.polygon_visualizer.set_vertex_value(i, default_value)

        # Check if we're using a special shape
        shape_id = self.special_shape_combo.currentData()
        using_special_shape = (
            hasattr(self, "special_transition_pairs") and shape_id != "custom"
        )

        # Determine which pairs to calculate transitions for
        if using_special_shape and self.special_transition_pairs != "all":
            # Use the predefined transition pairs for the special shape
            pairs_to_calculate = self.special_transition_pairs
        else:
            # Calculate all pairs
            pairs_to_calculate = [
                (i, j) for i in range(sides) for j in range(i + 1, sides)
            ]

        # Calculate transitions for the selected pairs
        for i, j in pairs_to_calculate:
            # Skip invalid indices
            if i >= sides or j >= sides:
                continue

            # Get the vertex values from the visualizer (guaranteed to be valid)
            v1_decimal = self.polygon_visualizer.vertex_values.get(i, i + 1)
            v2_decimal = self.polygon_visualizer.vertex_values.get(j, j + 1)

            # Convert to ternary
            v1_ternary = decimal_to_ternary(v1_decimal)
            v2_ternary = decimal_to_ternary(v2_decimal)

            # Apply transition
            result_ternary = self.transition.apply_transition(v1_ternary, v2_ternary)
            result_decimal = ternary_to_decimal(result_ternary)

            # Store the result
            transitions[(i, j)] = result_decimal
            transition_results.append(
                (i, v1_decimal, j, v2_decimal, result_decimal, result_ternary)
            )

        # Update the visualizer with transitions and special pairs if applicable
        if using_special_shape and self.special_transition_pairs != "all":
            # Pass the special pairs for highlighting
            self.polygon_visualizer.set_transitions(
                transitions, self.special_transition_pairs
            )
        else:
            # No special pairs to highlight
            self.polygon_visualizer.set_transitions(transitions)

        # Update the results table
        self.results_table.setRowCount(len(transition_results))

        for row, (v1_idx, v1_val, v2_idx, v2_val, dec, tern) in enumerate(
            transition_results
        ):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(v1_idx)))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(v1_val)))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(v2_idx)))
            self.results_table.setItem(row, 3, QTableWidgetItem(str(v2_val)))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(dec)))
            self.results_table.setItem(row, 5, QTableWidgetItem(str(tern)))

        # Calculate edge sums (adjacent vertices)
        edge_transitions = []
        edge_sum_decimal = 0

        # For special shapes, we need to directly calculate the transitions for adjacent vertices
        # because they might not be in the transition_results
        if using_special_shape:
            # Get all vertex values
            vertex_values = {}
            for i in range(sides):
                vertex_values[i] = self.polygon_visualizer.vertex_values.get(i, i + 1)

            # Calculate transitions for adjacent vertices
            for i in range(sides):
                j = (i + 1) % sides  # Next vertex (wrapping around)

                # Get vertex values
                v1_val = vertex_values[i]
                v2_val = vertex_values[j]

                # Convert to ternary
                v1_ternary = decimal_to_ternary(v1_val)
                v2_ternary = decimal_to_ternary(v2_val)

                # Calculate transition
                result_ternary = self.transition.apply_transition(
                    v1_ternary, v2_ternary
                )
                result_decimal = ternary_to_decimal(result_ternary)

                # Add to sum
                edge_sum_decimal += result_decimal
                edge_transitions.append((i, j, result_decimal, result_ternary))
        else:
            # For standard shapes, use the transition_results
            for i in range(sides):
                j = (i + 1) % sides  # Next vertex (wrapping around)
                for result in transition_results:
                    v1, _, v2, _, dec, tern = result
                    if (v1 == i and v2 == j) or (v1 == j and v2 == i):
                        edge_transitions.append((i, j, dec, tern))
                        edge_sum_decimal += dec

        # Convert the edge sum to ternary
        edge_sum_ternary = decimal_to_ternary(edge_sum_decimal)

        # Update the edge sums table
        self.edge_sums_table.setRowCount(1)
        self.edge_sums_table.setItem(0, 0, QTableWidgetItem("Adjacent Vertices"))
        self.edge_sums_table.setItem(0, 1, QTableWidgetItem(str(edge_sum_decimal)))
        self.edge_sums_table.setItem(0, 2, QTableWidgetItem(str(edge_sum_ternary)))

        # Calculate diagonal sums by skip value or special grouping
        diagonal_sums = {}

        # Check if we're using a special star with custom diagonal groupings
        if using_special_shape and shape_id in [
            "lovely_star",
            "atomic_star",
            "mountain_star",
            "unicursal_hexagram",
            "cuboctahedron",
        ]:
            # For Lovely Star, group diagonals into "short" and "long" categories
            # based on the specific transition pairs

            # Define which pairs are short and which are long based on the selected shape
            if shape_id == "lovely_star":
                # For Lovely Star: 5 short diagonals and 2 long diagonals
                short_diagonals = [(3, 1), (1, 5), (2, 5), (2, 6), (4, 6)]
                long_diagonals = [(0, 3), (0, 4)]
                short_name = "Short Diagonals (5)"
                long_name = "Long Diagonals (2)"
            elif shape_id == "atomic_star":
                # For Atomic Star: 5 short diagonals and 2 long diagonals
                short_diagonals = [(0, 5), (0, 2), (5, 3), (1, 6), (2, 4)]
                long_diagonals = [(1, 4), (3, 6)]
                short_name = "Short Diagonals (5)"
                long_name = "Long Diagonals (2)"
            elif shape_id == "mountain_star":
                # For Mountain Star: 3 short diagonals and 4 long diagonals
                short_diagonals = [(1, 6), (2, 4), (3, 5)]
                long_diagonals = [(0, 4), (0, 3), (2, 6), (1, 5)]
                short_name = "Short Diagonals (3)"
                long_name = "Long Diagonals (4)"
            elif shape_id == "unicursal_hexagram":
                # For Unicursal Hexagram: 3 short diagonals and 3 long diagonals
                short_diagonals = [(0, 2), (1, 3), (3, 5)]
                long_diagonals = [(0, 4), (1, 4), (2, 5)]
                short_name = "Short Diagonals (3)"
                long_name = "Long Diagonals (3)"
            elif shape_id == "cuboctahedron":
                # For 2D Cuboctahedron: Group by front, back, and center-crossing connections
                # Front connections
                front_diagonals = [
                    # First triangle: 8 to 6, 6 to 7, 7 to 8
                    (8, 6),
                    (6, 7),
                    (7, 8),
                    # Additional front connections: 5 to 6, 6 to 8, 8 to 4, 4 to 5
                    (5, 6),
                    (6, 8),
                    (8, 4),
                    (4, 5),
                    # Connection: 8, 4, 3
                    (4, 3),
                    (3, 8),
                    # New connections: 3 to 2, 2 to 7
                    (3, 2),
                    (2, 7),
                    # New connections: 2 to 1, 1 to 7
                    (2, 1),
                    (1, 7),
                    # New connections: 5 to 0, 0 to 6, 0 to 1
                    (5, 0),
                    (0, 6),
                    (0, 1),
                ]
                # Back connections
                back_diagonals = [
                    # First back triangle: 11-9-10
                    (11, 9),
                    (9, 10),
                    (10, 11),
                    # Additional back connections
                    (11, 4),
                    (11, 5),
                    (10, 3),
                    (10, 2),
                    (9, 0),
                    (9, 1),
                ]
                # Center-crossing diagonal connections
                center_diagonals = [
                    # Vertex lines that go through the center
                    (8, 9),
                    (6, 10),
                    (7, 11),
                    (4, 1),
                    (2, 5),
                    (3, 0),
                ]
                short_diagonals = front_diagonals
                long_diagonals = back_diagonals
                center_name = "Center-Crossing Diagonals (6)"
                short_name = "Front Connections (18)"
                long_name = "Back Connections (9)"

            # The issue is that our transition_results might not contain all the pairs we defined
            # Let's directly calculate the transitions for our specific diagonal pairs

            # Process short diagonals
            short_sum = 0
            short_transitions = []

            # Process long diagonals
            long_sum = 0
            long_transitions = []

            # Process center diagonals (for cuboctahedron)
            center_sum = 0
            center_transitions = []

            # Get all vertex values
            vertex_values = {}
            for i in range(sides):
                vertex_values[i] = self.polygon_visualizer.vertex_values.get(i, i + 1)

            # Calculate transitions for short diagonals
            for v1, v2 in short_diagonals:
                # Get vertex values
                v1_val = vertex_values[v1]
                v2_val = vertex_values[v2]

                # Convert to ternary
                v1_ternary = decimal_to_ternary(v1_val)
                v2_ternary = decimal_to_ternary(v2_val)

                # Calculate transition
                result_ternary = self.transition.apply_transition(
                    v1_ternary, v2_ternary
                )
                result_decimal = ternary_to_decimal(result_ternary)

                # Add to sum
                short_sum += result_decimal
                short_transitions.append((v1, v2, result_decimal, result_ternary))

            # Calculate transitions for long diagonals
            for v1, v2 in long_diagonals:
                # Get vertex values
                v1_val = vertex_values[v1]
                v2_val = vertex_values[v2]

                # Convert to ternary
                v1_ternary = decimal_to_ternary(v1_val)
                v2_ternary = decimal_to_ternary(v2_val)

                # Calculate transition
                result_ternary = self.transition.apply_transition(
                    v1_ternary, v2_ternary
                )
                result_decimal = ternary_to_decimal(result_ternary)

                # Add to sum
                long_sum += result_decimal
                long_transitions.append((v1, v2, result_decimal, result_ternary))

            # Calculate transitions for center diagonals (for cuboctahedron)
            if shape_id == "cuboctahedron":
                for v1, v2 in center_diagonals:
                    # Get vertex values
                    v1_val = vertex_values[v1]
                    v2_val = vertex_values[v2]

                    # Convert to ternary
                    v1_ternary = decimal_to_ternary(v1_val)
                    v2_ternary = decimal_to_ternary(v2_val)

                    # Calculate transition
                    result_ternary = self.transition.apply_transition(
                        v1_ternary, v2_ternary
                    )
                    result_decimal = ternary_to_decimal(result_ternary)

                    # Add to sum
                    center_sum += result_decimal
                    center_transitions.append((v1, v2, result_decimal, result_ternary))

            # Store the results
            diagonal_sums["short"] = {
                "decimal": short_sum,
                "transitions": short_diagonals,
                "name": short_name,
            }
            diagonal_sums["long"] = {
                "decimal": long_sum,
                "transitions": long_diagonals,
                "name": long_name,
            }

            # Add center diagonals for cuboctahedron
            if shape_id == "cuboctahedron":
                diagonal_sums["center"] = {
                    "decimal": center_sum,
                    "transitions": center_diagonals,
                    "name": center_name,
                }
        else:
            # Standard calculation for other shapes
            for i in range(sides):
                for skip in range(
                    2, sides // 2 + 1
                ):  # Skip values from 2 to half the sides
                    j = (i + skip) % sides  # Vertex with the given skip
                    for result in transition_results:
                        v1, _, v2, _, dec, tern = result
                        if (v1 == i and v2 == j) or (v1 == j and v2 == i):
                            if skip not in diagonal_sums:
                                diagonal_sums[skip] = {
                                    "decimal": 0,
                                    "transitions": [],
                                    "name": f"Skip {skip}",
                                }
                            diagonal_sums[skip]["decimal"] += dec
                            diagonal_sums[skip]["transitions"].append((i, j, dec, tern))

        # Update the diagonal sums table
        self.diagonal_sums_table.setRowCount(len(diagonal_sums))

        for row, (skip, data) in enumerate(sorted(diagonal_sums.items())):
            sum_decimal = data["decimal"]
            sum_ternary = decimal_to_ternary(sum_decimal)

            # Use the custom name if available, otherwise use the skip value
            skip_name = data.get("name", f"Skip {skip}")

            self.diagonal_sums_table.setItem(row, 0, QTableWidgetItem(skip_name))
            self.diagonal_sums_table.setItem(row, 1, QTableWidgetItem(str(sum_decimal)))
            self.diagonal_sums_table.setItem(row, 2, QTableWidgetItem(str(sum_ternary)))

        # Calculate the sum of all vertex values
        vertex_values = [
            self.polygon_visualizer.vertex_values.get(i, i + 1) for i in range(sides)
        ]
        vertex_sum_decimal = sum(vertex_values)
        vertex_sum_ternary = decimal_to_ternary(vertex_sum_decimal)

        # Calculate the total sum of all transitions
        transition_sum_decimal = sum(
            result[4] for result in transition_results
        )  # Sum of all decimal values
        transition_sum_ternary = decimal_to_ternary(transition_sum_decimal)

        # Update the total sum table
        # Row 0: Vertex Values Sum
        self.total_sum_table.setItem(0, 1, QTableWidgetItem(str(vertex_sum_decimal)))
        self.total_sum_table.setItem(0, 2, QTableWidgetItem(str(vertex_sum_ternary)))

        # Row 1: Transitions Sum
        self.total_sum_table.setItem(
            1, 1, QTableWidgetItem(str(transition_sum_decimal))
        )
        self.total_sum_table.setItem(
            1, 2, QTableWidgetItem(str(transition_sum_ternary))
        )

        # Calculate transitions between diagonal sums
        diagonal_transitions = []

        # Get all skip values with their sums
        skip_values = sorted(diagonal_sums.keys())

        # Only proceed if we have at least 2 skip values
        if len(skip_values) >= 2:
            # Calculate transitions between each pair of skip values
            for i, skip1 in enumerate(skip_values):
                for skip2 in skip_values[i + 1 :]:
                    # Get the decimal sums for each skip value
                    sum1 = diagonal_sums[skip1]["decimal"]
                    sum2 = diagonal_sums[skip2]["decimal"]

                    # Convert to ternary
                    sum1_ternary = decimal_to_ternary(sum1)
                    sum2_ternary = decimal_to_ternary(sum2)

                    # Calculate the transition
                    result_ternary = self.transition.apply_transition(
                        sum1_ternary, sum2_ternary
                    )
                    result_decimal = ternary_to_decimal(result_ternary)

                    # Add to the list of diagonal transitions
                    diagonal_transitions.append(
                        (skip1, skip2, result_decimal, result_ternary)
                    )

        # Update the diagonal transitions table
        self.diagonal_transitions_table.setRowCount(len(diagonal_transitions))

        for row, (skip1, skip2, dec, tern) in enumerate(diagonal_transitions):
            # Add a note about what this transition represents
            # Default note in case none of the conditions match
            note = f"Transition between {skip1} and {skip2}"

            if using_special_shape and shape_id in [
                "lovely_star",
                "atomic_star",
                "mountain_star",
                "unicursal_hexagram",
                "cuboctahedron",
            ]:
                # For special shapes, use more meaningful descriptions
                if shape_id == "cuboctahedron":
                    if skip1 == "short" and skip2 == "long":
                        note = "Transition between sum of Front Connections and sum of Back Connections"
                    elif skip1 == "short" and skip2 == "center":
                        note = "Transition between sum of Front Connections and sum of Center-Crossing Diagonals"
                    elif skip1 == "long" and skip2 == "center":
                        note = "Transition between sum of Back Connections and sum of Center-Crossing Diagonals"
                elif skip1 == "short" and skip2 == "long":
                    note = "Transition between sum of Short Diagonals and sum of Long Diagonals"
            elif not using_special_shape:
                # For standard shapes, use the skip value description
                note = f"Transition between sum of skip {skip1} diagonals and sum of skip {skip2} diagonals"

            self.diagonal_transitions_table.setItem(
                row, 0, QTableWidgetItem(str(skip1))
            )
            self.diagonal_transitions_table.setItem(
                row, 1, QTableWidgetItem(str(skip2))
            )
            self.diagonal_transitions_table.setItem(row, 2, QTableWidgetItem(str(dec)))
            self.diagonal_transitions_table.setItem(row, 3, QTableWidgetItem(str(tern)))
            self.diagonal_transitions_table.setItem(row, 4, QTableWidgetItem(note))

        # Resize the tables to fit the content
        self.results_table.resizeColumnsToContents()
        self.edge_sums_table.resizeColumnsToContents()
        self.diagonal_sums_table.resizeColumnsToContents()
        self.diagonal_transitions_table.resizeColumnsToContents()
        self.total_sum_table.resizeColumnsToContents()

    def _special_shape_selected(self, _):
        """Handle selection of a special shape from the dropdown.

        Args:
            index: Index of the selected item in the dropdown
        """
        # Get the selected shape identifier
        shape_id = self.special_shape_combo.currentData()

        if shape_id == "custom":
            # Custom shape - do nothing, let user define values
            return

        # Define special shapes with their properties
        special_shapes = {
            "unicursal_hexagram": {
                "sides": 6,
                "vertex_values": [1, 2, 3, 4, 5, 6],
                # For unicursal hexagram, we calculate transitions between specific vertices
                # as defined by the special pattern
                "transition_pairs": [(0, 2), (0, 4), (1, 4), (1, 3), (2, 5), (3, 5)],
            },
            "atomic_star": {
                "sides": 7,
                "vertex_values": [1, 2, 3, 4, 5, 6, 7],
                # For the Atomic Star, we calculate transitions between specific pairs
                # as defined by the special pattern
                "transition_pairs": [
                    (0, 5),
                    (0, 2),
                    (1, 6),
                    (3, 6),
                    (1, 4),
                    (2, 4),
                    (5, 3),
                ],
            },
            "mountain_star": {
                "sides": 7,
                "vertex_values": [1, 2, 3, 4, 5, 6, 7],
                # For The Mountain Star, we calculate transitions between specific pairs
                # as defined by the special pattern
                "transition_pairs": [
                    (0, 4),
                    (0, 3),
                    (2, 6),
                    (1, 5),
                    (1, 6),
                    (3, 5),
                    (2, 4),
                ],
            },
            "lovely_star": {
                "sides": 7,
                "vertex_values": [1, 2, 3, 4, 5, 6, 7],
                # For the lovely star, we calculate transitions between specific pairs
                # as defined by the special pattern
                "transition_pairs": [
                    (0, 4),
                    (0, 3),
                    (2, 5),
                    (3, 1),
                    (4, 6),
                    (2, 6),
                    (1, 5),
                ],
            },
            "cuboctahedron": {
                "sides": 12,
                "vertex_values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                # For the 2D cuboctahedron, we calculate transitions between vertices
                # that are connected in our custom drawing
                "transition_pairs": [
                    # Front connections
                    # First triangle: 8 to 6, 6 to 7, 7 to 8
                    (8, 6),
                    (6, 7),
                    (7, 8),
                    # Additional front connections: 5 to 6, 6 to 8, 8 to 4, 4 to 5
                    (5, 6),
                    (6, 8),
                    (8, 4),
                    (4, 5),
                    # Connection: 8, 4, 3
                    (4, 3),
                    (3, 8),
                    # New connections: 3 to 2, 2 to 7
                    (3, 2),
                    (2, 7),
                    # New connections: 2 to 1, 1 to 7
                    (2, 1),
                    (1, 7),
                    # New connections: 5 to 0, 0 to 6, 0 to 1
                    (5, 0),
                    (0, 6),
                    (0, 1),
                    # Back connections
                    # First back triangle: 11-9-10
                    (11, 9),
                    (9, 10),
                    (10, 11),
                    # Additional back connections
                    (11, 4),
                    (11, 5),
                    (10, 3),
                    (10, 2),
                    (9, 0),
                    (9, 1),
                ],
            },
        }

        # Get the properties for the selected shape
        shape_props = special_shapes.get(shape_id)
        if not shape_props:
            return

        # Set the number of sides
        sides = shape_props["sides"]
        self.sides_input.setValue(sides)

        # Set the vertex values
        vertex_values = shape_props["vertex_values"]
        for i, value in enumerate(vertex_values):
            if i in self.vertex_inputs:
                self.vertex_inputs[i].setText(str(value))

        # Store the transition pairs for later use in calculation
        self.special_transition_pairs = shape_props["transition_pairs"]

        # Set the special shape ID on the polygon visualizer
        self.polygon_visualizer.special_shape_id = shape_id

        # Calculate transitions with the special shape
        self._calculate_transitions()

    def _setup_context_menus(self):
        """Set up context menus for the tables."""
        # Enable context menu for all tables
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.edge_sums_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.diagonal_sums_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.total_sum_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.diagonal_transitions_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        # Connect context menu signals
        self.results_table.customContextMenuRequested.connect(
            self._show_results_context_menu
        )
        self.edge_sums_table.customContextMenuRequested.connect(
            self._show_edge_sums_context_menu
        )
        self.diagonal_sums_table.customContextMenuRequested.connect(
            self._show_diagonal_sums_context_menu
        )
        self.total_sum_table.customContextMenuRequested.connect(
            self._show_total_sum_context_menu
        )
        self.diagonal_transitions_table.customContextMenuRequested.connect(
            self._show_diagonal_transitions_context_menu
        )

    def _show_results_context_menu(self, position):
        """Show context menu for the results table.

        Args:
            position: Position where the menu should be shown
        """
        self._show_table_context_menu(
            self.results_table, position, 4
        )  # Column 4 is Transition (Dec)

    def _show_edge_sums_context_menu(self, position):
        """Show context menu for the edge sums table.

        Args:
            position: Position where the menu should be shown
        """
        self._show_table_context_menu(
            self.edge_sums_table, position, 1
        )  # Column 1 is Sum (Dec)

    def _show_diagonal_sums_context_menu(self, position):
        """Show context menu for the diagonal sums table.

        Args:
            position: Position where the menu should be shown
        """
        self._show_table_context_menu(
            self.diagonal_sums_table, position, 1
        )  # Column 1 is Sum (Dec)

    def _show_total_sum_context_menu(self, position):
        """Show context menu for the total sum table.

        Args:
            position: Position where the menu should be shown
        """
        self._show_table_context_menu(
            self.total_sum_table, position, 1
        )  # Column 1 is Sum (Dec)

    def _show_diagonal_transitions_context_menu(self, position):
        """Show context menu for the diagonal transitions table.

        Args:
            position: Position where the menu should be shown
        """
        self._show_table_context_menu(
            self.diagonal_transitions_table, position, 2
        )  # Column 2 is Transition (Dec)

    def _show_table_context_menu(self, table, position, decimal_column):
        """Show context menu for a table with decimal values.

        Args:
            table: The table widget
            position: Position where the menu should be shown
            decimal_column: The column index containing decimal values
        """
        # Get the item at the position
        item = table.itemAt(position)
        if not item or item.column() != decimal_column:
            return

        # Try to get the decimal value
        try:
            value = int(item.text())
        except (ValueError, TypeError):
            return

        # Create context menu
        menu = QMenu(self)

        # Add "Send to Quadset Analysis" option
        quadset_action = QAction(f"Send {value} to Quadset Analysis", self)
        quadset_action.triggered.connect(lambda: self._send_to_quadset_analysis(value))
        menu.addAction(quadset_action)

        # Add "Look up in Database" option
        lookup_action = QAction(f"Look up {value} in Database", self)
        lookup_action.triggered.connect(lambda: self._lookup_in_database(value))
        menu.addAction(lookup_action)

        # Add "Send to PolyCalc" option if available
        if POLYCALC_AVAILABLE:
            polycalc_action = QAction(f"Send {value} to PolyCalc", self)
            polycalc_action.triggered.connect(lambda: self._send_to_polycalc(value))
            menu.addAction(polycalc_action)

        # Show menu at the requested position
        menu.exec(table.viewport().mapToGlobal(position))

    def _send_to_quadset_analysis(self, value):
        """Send a value to the TQ Quadset Analysis tool.

        Args:
            value: Integer value to analyze in the TQ Grid
        """
        try:
            # Open the TQ Grid with this number
            analysis_service = tq_analysis_service.get_instance()
            panel = analysis_service.open_quadset_analysis(value)

            # Find the window containing this panel and ensure it's on top
            parent = panel.window()
            if parent and hasattr(parent, "ensure_on_top"):
                parent.ensure_on_top()
        except Exception as e:
            from loguru import logger

            logger.error(f"Error opening quadset analysis: {e}")

    def _lookup_in_database(self, value):
        """Look up a value in the TQ database.

        Args:
            value: Integer value to look up
        """
        try:
            from tq.ui.dialogs.number_database_window import NumberDatabaseWindow

            parent = self.window()
            if parent and hasattr(parent, "window_manager"):
                base_id = f"number_database_{value}"
                window = parent.window_manager.open_multi_window(
                    base_id,
                    NumberDatabaseWindow(value),
                    f"Number Database: {value}",
                    (800, 600),
                )

                # Explicitly ensure the new window is on top
                window.ensure_on_top()
            else:
                db_window = NumberDatabaseWindow(value)
                db_window.show()
                db_window.raise_()
                db_window.activateWindow()
        except Exception as e:
            from loguru import logger

            logger.error(f"Error looking up in database: {e}")

    def _send_to_polycalc(self, value):
        """Send a value to the Regular Polygon Calculator.

        Args:
            value: Numeric value to send to the calculator
        """
        if not POLYCALC_AVAILABLE:
            return

        try:
            # Create and show the dialog
            dialog = SendToPolygonDialog(float(value), self)
            dialog.exec()
        except Exception as e:
            from loguru import logger

            logger.error(f"Error sending to polygon calculator: {e}")


if __name__ == "__main__":
    """Simple demonstration of the geometric transition panel."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = GeometricTransitionPanel()
    panel.resize(800, 600)
    panel.show()
    sys.exit(app.exec())
