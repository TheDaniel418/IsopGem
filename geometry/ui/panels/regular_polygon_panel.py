"""Regular polygon calculator panel.

This module provides a panel for calculating properties of regular polygons.
"""

import math

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from geometry.calculator.regular_polygon_calculator import RegularPolygonCalculator
from geometry.services.polygon_service import PolygonService


class RegularPolygonVisualization(QWidget):
    """Widget for visualizing a regular polygon."""

    def __init__(self, parent=None):
        """Initialize the visualization widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculator = RegularPolygonCalculator()
        self.show_incircle = True
        self.show_circumcircle = True
        self.show_apothem = True
        self.show_diagonals = False
        self.show_central_angles = False
        self.show_interior_angles = False
        self.show_exterior_angles = False
        self.show_vertex_labels = True
        self.show_edge_labels = False
        self.show_measurements = True

        # Set minimum size for better visualization
        self.setMinimumSize(400, 400)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(240, 240, 240))
        self.setPalette(palette)

    def set_calculator(self, calculator: RegularPolygonCalculator) -> None:
        """Set the calculator for the visualization.

        Args:
            calculator: Regular polygon calculator
        """
        self.calculator = calculator
        self.update()

    def toggle_incircle(self, show: bool) -> None:
        """Toggle the visibility of the incircle.

        Args:
            show: Whether to show the incircle
        """
        self.show_incircle = show
        self.update()

    def toggle_circumcircle(self, show: bool) -> None:
        """Toggle the visibility of the circumcircle.

        Args:
            show: Whether to show the circumcircle
        """
        self.show_circumcircle = show
        self.update()

    def toggle_apothem(self, show: bool) -> None:
        """Toggle the visibility of the apothem.

        Args:
            show: Whether to show the apothem
        """
        self.show_apothem = show
        self.update()

    def toggle_diagonals(self, show: bool) -> None:
        """Toggle the visibility of the diagonals.

        Args:
            show: Whether to show the diagonals
        """
        self.show_diagonals = show
        self.update()

    def toggle_central_angles(self, show: bool) -> None:
        """Toggle the visibility of the central angles.

        Args:
            show: Whether to show the central angles
        """
        self.show_central_angles = show
        self.update()

    def toggle_interior_angles(self, show: bool) -> None:
        """Toggle the visibility of the interior angles.

        Args:
            show: Whether to show the interior angles
        """
        self.show_interior_angles = show
        self.update()

    def toggle_exterior_angles(self, show: bool) -> None:
        """Toggle the visibility of the exterior angles.

        Args:
            show: Whether to show the exterior angles
        """
        self.show_exterior_angles = show
        self.update()

    def toggle_vertex_labels(self, show: bool) -> None:
        """Toggle the visibility of the vertex labels.

        Args:
            show: Whether to show the vertex labels
        """
        self.show_vertex_labels = show
        self.update()

    def toggle_edge_labels(self, show: bool) -> None:
        """Toggle the visibility of the edge labels.

        Args:
            show: Whether to show the edge labels
        """
        self.show_edge_labels = show
        self.update()

    def toggle_measurements(self, show: bool) -> None:
        """Toggle the visibility of the measurements.

        Args:
            show: Whether to show the measurements
        """
        self.show_measurements = show
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the visualization.

        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate the center and scale
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        # Calculate the maximum radius that fits in the widget
        max_radius = min(width, height) / 2 - 20

        # Scale the radius
        scaled_radius = min(max_radius, self.calculator.radius)
        scale_factor = scaled_radius / self.calculator.radius

        # Draw the circumcircle
        if self.show_circumcircle:
            painter.setPen(QPen(QColor(100, 100, 255, 150), 1, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(200, 200, 255, 50)))
            painter.drawEllipse(
                QPointF(center_x, center_y), scaled_radius, scaled_radius
            )

            # Draw the circumcircle label
            if self.show_measurements:
                painter.setPen(QPen(QColor(100, 100, 255), 1))
                painter.drawText(
                    int(center_x + scaled_radius / 2),
                    int(center_y - scaled_radius / 2),
                    f"R = {self.calculator.radius:.2f}",
                )

        # Get the vertices
        vertices = self.calculator.get_vertices(0, 0)

        # Create a polygon for drawing
        polygon = QPolygonF()
        for vertex in vertices:
            # Scale and translate the vertex
            x = center_x + vertex.x * scale_factor
            y = center_y + vertex.y * scale_factor
            polygon.append(QPointF(x, y))

        # Draw the polygon
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.setBrush(QBrush(QColor(200, 200, 200, 100)))
        painter.drawPolygon(polygon)

        # Draw the incircle
        if self.show_incircle:
            inradius = self.calculator.calculate_inradius() * scale_factor
            painter.setPen(QPen(QColor(255, 100, 100, 150), 1, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(255, 200, 200, 50)))
            painter.drawEllipse(QPointF(center_x, center_y), inradius, inradius)

            # Draw the incircle label
            if self.show_measurements:
                painter.setPen(QPen(QColor(255, 100, 100), 1))
                painter.drawText(
                    int(center_x - inradius / 2),
                    int(center_y),
                    f"r = {self.calculator.calculate_inradius():.2f}",
                )

        # Draw the apothems
        if self.show_apothem:
            apothem = self.calculator.calculate_apothem() * scale_factor
            painter.setPen(QPen(QColor(100, 255, 100), 1, Qt.PenStyle.DashLine))

            # Draw an apothem to each side
            for i in range(self.calculator.sides):
                # Calculate the midpoint of the side
                j = (i + 1) % self.calculator.sides
                x1 = center_x + vertices[i].x * scale_factor
                y1 = center_y + vertices[i].y * scale_factor
                x2 = center_x + vertices[j].x * scale_factor
                y2 = center_y + vertices[j].y * scale_factor
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                # Draw the apothem
                painter.drawLine(QPointF(center_x, center_y), QPointF(mid_x, mid_y))

                # Draw the apothem label for the first side only
                if i == 0 and self.show_measurements:
                    painter.setPen(QPen(QColor(100, 255, 100), 1))
                    painter.drawText(
                        int((center_x + mid_x) / 2),
                        int((center_y + mid_y) / 2),
                        f"a = {self.calculator.calculate_apothem():.2f}",
                    )

        # Draw the diagonals
        if self.show_diagonals:
            painter.setPen(QPen(QColor(150, 150, 150), 1, Qt.PenStyle.DotLine))

            # Draw all diagonals
            for i in range(self.calculator.sides):
                x1 = center_x + vertices[i].x * scale_factor
                y1 = center_y + vertices[i].y * scale_factor

                for j in range(i + 2, i + self.calculator.sides - 1):
                    j_mod = j % self.calculator.sides
                    x2 = center_x + vertices[j_mod].x * scale_factor
                    y2 = center_y + vertices[j_mod].y * scale_factor

                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Draw the vertex labels
        if self.show_vertex_labels:
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            for i, vertex in enumerate(vertices):
                x = center_x + vertex.x * scale_factor
                y = center_y + vertex.y * scale_factor

                # Adjust label position based on vertex position
                label_offset_x = 0
                label_offset_y = 0

                if vertex.x < 0:
                    label_offset_x = -15
                elif vertex.x > 0:
                    label_offset_x = 5

                if vertex.y < 0:
                    label_offset_y = -15
                elif vertex.y > 0:
                    label_offset_y = 15

                painter.drawText(
                    int(x + label_offset_x), int(y + label_offset_y), f"{i + 1}"
                )

        # Draw the edge labels
        if self.show_edge_labels:
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            edge_length = self.calculator.calculate_edge_length()

            for i in range(self.calculator.sides):
                j = (i + 1) % self.calculator.sides
                x1 = center_x + vertices[i].x * scale_factor
                y1 = center_y + vertices[i].y * scale_factor
                x2 = center_x + vertices[j].x * scale_factor
                y2 = center_y + vertices[j].y * scale_factor

                # Draw the edge label at the midpoint
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                # Calculate the normal vector to the edge
                dx = x2 - x1
                dy = y2 - y1
                length = math.sqrt(dx * dx + dy * dy)
                nx = -dy / length * 15  # Perpendicular and scaled
                ny = dx / length * 15

                painter.drawText(int(mid_x + nx), int(mid_y + ny), f"{edge_length:.2f}")

        # Draw the central angles
        if self.show_central_angles:
            painter.setPen(QPen(QColor(255, 150, 0), 1))
            central_angle = self.calculator.calculate_central_angle()

            for i in range(self.calculator.sides):
                # Draw an arc for each central angle
                angle1 = math.atan2(vertices[i].y, vertices[i].x) * 180 / math.pi
                if angle1 < 0:
                    angle1 += 360

                # Draw the central angle label
                if i == 0 and self.show_measurements:
                    # Calculate a point halfway between center and vertex
                    x = center_x + vertices[i].x * scale_factor * 0.5
                    y = center_y + vertices[i].y * scale_factor * 0.5

                    painter.drawText(int(x), int(y), f"{central_angle:.2f}°")

        # Draw the interior angles
        if self.show_interior_angles:
            painter.setPen(QPen(QColor(0, 150, 255), 1))
            interior_angle = self.calculator.calculate_interior_angle()

            for i in range(self.calculator.sides):
                # Draw the interior angle label
                if i == 0 and self.show_measurements:
                    x = center_x + vertices[i].x * scale_factor
                    y = center_y + vertices[i].y * scale_factor

                    # Adjust label position
                    label_offset_x = 20 if vertices[i].x >= 0 else -40
                    label_offset_y = 20 if vertices[i].y >= 0 else -10

                    painter.drawText(
                        int(x + label_offset_x),
                        int(y + label_offset_y),
                        f"{interior_angle:.2f}°",
                    )

        # Draw the exterior angles
        if self.show_exterior_angles:
            painter.setPen(QPen(QColor(255, 0, 150), 1))
            exterior_angle = self.calculator.calculate_exterior_angle()

            for i in range(self.calculator.sides):
                # Draw the exterior angle label
                if i == 0 and self.show_measurements:
                    x = center_x + vertices[i].x * scale_factor
                    y = center_y + vertices[i].y * scale_factor

                    # Adjust label position
                    label_offset_x = -40 if vertices[i].x >= 0 else 20
                    label_offset_y = -10 if vertices[i].y >= 0 else 20

                    painter.drawText(
                        int(x + label_offset_x),
                        int(y + label_offset_y),
                        f"{exterior_angle:.2f}°",
                    )


class RegularPolygonPanel(QWidget):
    """Panel for the regular polygon calculator."""

    def __init__(self, parent=None):
        """Initialize the regular polygon panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculator = RegularPolygonCalculator()
        self.setMinimumSize(800, 600)  # Set minimum size for the panel

        # Register with the polygon service
        self.polygon_service = PolygonService()
        self.panel_id = "regular_polygon"
        self.available_fields = [
            "Sides",
            "Radius",
            "Edge Length",
            "Perimeter",
            "Area",
            "Inradius",
            "Incircle Circumference",
            "Incircle Area",
            "Circumcircle Circumference",
            "Circumcircle Area",
        ]

        # We'll register with the polygon service after the UI is initialized
        # This ensures that all the UI components are created before we try to use them
        self.panel_id = "regular_polygon"
        self.available_fields = [
            "Sides",
            "Radius",
            "Edge Length",
            "Perimeter",
            "Area",
            "Inradius",
            "Incircle Circumference",
            "Incircle Area",
            "Circumcircle Circumference",
            "Circumcircle Area",
        ]

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        main_layout = QHBoxLayout(self)

        # Left panel for controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Input group
        input_group = QGroupBox("Polygon Parameters")
        input_layout = QFormLayout(input_group)

        # Number of sides
        self.sides_spin = QSpinBox()
        self.sides_spin.setRange(3, 100)
        self.sides_spin.setValue(self.calculator.sides)
        self.sides_spin.valueChanged.connect(self._update_polygon)
        input_layout.addRow("Number of Sides:", self.sides_spin)

        # Radius
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(1.0, 1000.0)
        self.radius_spin.setValue(self.calculator.radius)
        self.radius_spin.setSingleStep(10.0)
        self.radius_spin.valueChanged.connect(self._update_polygon)
        input_layout.addRow("Radius:", self.radius_spin)

        # Orientation
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItem("Vertex at Top", "vertex_top")
        self.orientation_combo.addItem("Side at Top", "side_top")
        self.orientation_combo.currentIndexChanged.connect(self._update_polygon)
        input_layout.addRow("Orientation:", self.orientation_combo)

        # Add input group to left layout
        left_layout.addWidget(input_group)

        # Visualization options group
        viz_group = QGroupBox("Visualization Options")
        viz_layout = QGridLayout(viz_group)

        # Checkboxes for visualization options
        self.incircle_check = QCheckBox("Show Incircle")
        self.incircle_check.setChecked(True)
        self.incircle_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.incircle_check, 0, 0)

        self.circumcircle_check = QCheckBox("Show Circumcircle")
        self.circumcircle_check.setChecked(True)
        self.circumcircle_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.circumcircle_check, 0, 1)

        self.apothem_check = QCheckBox("Show Apothem")
        self.apothem_check.setChecked(True)
        self.apothem_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.apothem_check, 1, 0)

        self.diagonals_check = QCheckBox("Show Diagonals")
        self.diagonals_check.setChecked(False)
        self.diagonals_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.diagonals_check, 1, 1)

        self.central_angles_check = QCheckBox("Show Central Angles")
        self.central_angles_check.setChecked(False)
        self.central_angles_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.central_angles_check, 2, 0)

        self.interior_angles_check = QCheckBox("Show Interior Angles")
        self.interior_angles_check.setChecked(False)
        self.interior_angles_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.interior_angles_check, 2, 1)

        self.exterior_angles_check = QCheckBox("Show Exterior Angles")
        self.exterior_angles_check.setChecked(False)
        self.exterior_angles_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.exterior_angles_check, 3, 0)

        self.vertex_labels_check = QCheckBox("Show Vertex Labels")
        self.vertex_labels_check.setChecked(True)
        self.vertex_labels_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.vertex_labels_check, 3, 1)

        self.edge_labels_check = QCheckBox("Show Edge Labels")
        self.edge_labels_check.setChecked(False)
        self.edge_labels_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.edge_labels_check, 4, 0)

        self.measurements_check = QCheckBox("Show Measurements")
        self.measurements_check.setChecked(True)
        self.measurements_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.measurements_check, 4, 1)

        # Add visualization group to left layout
        left_layout.addWidget(viz_group)

        # Preset polygons group
        preset_group = QGroupBox("Preset Polygons")
        preset_layout = QGridLayout(preset_group)

        # Buttons for preset polygons
        presets = [
            ("Triangle", 3),
            ("Square", 4),
            ("Pentagon", 5),
            ("Hexagon", 6),
            ("Heptagon", 7),
            ("Octagon", 8),
            ("Nonagon", 9),
            ("Decagon", 10),
            ("Dodecagon", 12),
            ("Icosagon", 20),
        ]

        row, col = 0, 0
        for name, sides in presets:
            button = QPushButton(name)
            button.clicked.connect(lambda checked, s=sides: self._set_preset(s))
            preset_layout.addWidget(button, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        # Add preset group to left layout
        left_layout.addWidget(preset_group)

        # Add stretch to push everything to the top
        left_layout.addStretch()

        # Right panel with tabs
        right_panel = QTabWidget()

        # Visualization tab
        viz_tab = QWidget()
        viz_tab_layout = QVBoxLayout(viz_tab)

        # Visualization widget
        self.viz_widget = RegularPolygonVisualization()
        self.viz_widget.set_calculator(self.calculator)
        viz_tab_layout.addWidget(self.viz_widget)

        # Properties tab
        properties_tab = QWidget()
        properties_layout = QVBoxLayout(properties_tab)

        # Scroll area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Basic properties group
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)

        # Number of sides - read-only display of the spinner value
        self.sides_label = QLabel()
        basic_layout.addRow("Number of Sides:", self.sides_label)

        # Interior angle - calculated value
        self.interior_angle_label = QLabel()
        basic_layout.addRow("Interior Angle:", self.interior_angle_label)

        # Exterior angle - calculated value
        self.exterior_angle_label = QLabel()
        basic_layout.addRow("Exterior Angle:", self.exterior_angle_label)

        # Central angle - calculated value
        self.central_angle_label = QLabel()
        basic_layout.addRow("Central Angle:", self.central_angle_label)

        # Edge length - editable field
        self.edge_length_spin = QDoubleSpinBox()
        self.edge_length_spin.setRange(0.1, 1000.0)
        self.edge_length_spin.setDecimals(4)
        self.edge_length_spin.setSingleStep(1.0)
        self.edge_length_spin.editingFinished.connect(self._edge_length_changed)
        basic_layout.addRow("Edge Length:", self.edge_length_spin)

        # Perimeter - editable field
        self.perimeter_spin = QDoubleSpinBox()
        self.perimeter_spin.setRange(0.1, 10000.0)
        self.perimeter_spin.setDecimals(4)
        self.perimeter_spin.setSingleStep(10.0)
        self.perimeter_spin.editingFinished.connect(self._perimeter_changed)
        basic_layout.addRow("Perimeter:", self.perimeter_spin)

        # Area - editable field
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(0.1, 1000000.0)
        self.area_spin.setDecimals(4)
        self.area_spin.setSingleStep(100.0)
        self.area_spin.editingFinished.connect(self._area_changed)
        basic_layout.addRow("Area:", self.area_spin)

        scroll_layout.addWidget(basic_group)

        # Circle properties group
        circle_group = QGroupBox("Circle Properties")
        circle_layout = QFormLayout(circle_group)

        # Circumradius - editable field
        self.radius_spin_display = QDoubleSpinBox()
        self.radius_spin_display.setRange(0.1, 1000.0)
        self.radius_spin_display.setDecimals(4)
        self.radius_spin_display.setSingleStep(10.0)
        self.radius_spin_display.setValue(self.calculator.radius)
        self.radius_spin_display.editingFinished.connect(self._radius_changed)
        circle_layout.addRow("Circumradius:", self.radius_spin_display)

        # Circumcircle circumference - editable field
        self.circumcircle_circumference_spin = QDoubleSpinBox()
        self.circumcircle_circumference_spin.setRange(0.1, 10000.0)
        self.circumcircle_circumference_spin.setDecimals(4)
        self.circumcircle_circumference_spin.setSingleStep(10.0)
        self.circumcircle_circumference_spin.editingFinished.connect(
            self._circumcircle_circumference_changed
        )
        circle_layout.addRow(
            "Circumcircle Circumference:", self.circumcircle_circumference_spin
        )

        # Circumcircle area - editable field
        self.circumcircle_area_spin = QDoubleSpinBox()
        self.circumcircle_area_spin.setRange(0.1, 1000000.0)
        self.circumcircle_area_spin.setDecimals(4)
        self.circumcircle_area_spin.setSingleStep(100.0)
        self.circumcircle_area_spin.editingFinished.connect(
            self._circumcircle_area_changed
        )
        circle_layout.addRow("Circumcircle Area:", self.circumcircle_area_spin)

        # Inradius - editable field
        self.inradius_spin = QDoubleSpinBox()
        self.inradius_spin.setRange(0.1, 1000.0)
        self.inradius_spin.setDecimals(4)
        self.inradius_spin.setSingleStep(10.0)
        self.inradius_spin.editingFinished.connect(self._inradius_changed)
        circle_layout.addRow("Inradius:", self.inradius_spin)

        # Incircle circumference - editable field
        self.incircle_circumference_spin = QDoubleSpinBox()
        self.incircle_circumference_spin.setRange(0.1, 10000.0)
        self.incircle_circumference_spin.setDecimals(4)
        self.incircle_circumference_spin.setSingleStep(10.0)
        self.incircle_circumference_spin.editingFinished.connect(
            self._incircle_circumference_changed
        )
        circle_layout.addRow(
            "Incircle Circumference:", self.incircle_circumference_spin
        )

        # Incircle area - editable field
        self.incircle_area_spin = QDoubleSpinBox()
        self.incircle_area_spin.setRange(0.1, 1000000.0)
        self.incircle_area_spin.setDecimals(4)
        self.incircle_area_spin.setSingleStep(100.0)
        self.incircle_area_spin.editingFinished.connect(self._incircle_area_changed)
        circle_layout.addRow("Incircle Area:", self.incircle_area_spin)

        # Apothem - calculated value
        self.apothem_label = QLabel()
        circle_layout.addRow("Apothem:", self.apothem_label)

        scroll_layout.addWidget(circle_group)

        # Advanced properties group
        advanced_group = QGroupBox("Advanced Properties")
        advanced_layout = QFormLayout(advanced_group)

        self.diagonals_count_label = QLabel()
        advanced_layout.addRow("Total Diagonals:", self.diagonals_count_label)

        self.polygon_to_circle_ratio_label = QLabel()
        advanced_layout.addRow(
            "Polygon/Circumcircle Area Ratio:", self.polygon_to_circle_ratio_label
        )

        self.circle_to_polygon_ratio_label = QLabel()
        advanced_layout.addRow(
            "Incircle/Polygon Area Ratio:", self.circle_to_polygon_ratio_label
        )

        self.constructible_label = QLabel()
        advanced_layout.addRow(
            "Constructible with Compass and Straightedge:", self.constructible_label
        )

        scroll_layout.addWidget(advanced_group)

        # Diagonals group
        diagonals_group = QGroupBox("Diagonals")
        diagonals_layout = QVBoxLayout(diagonals_group)

        # Add a label explaining diagonals
        diagonals_info = QLabel(
            "Diagonals are grouped by skip pattern. The skip pattern indicates "
            "how many vertices are skipped when drawing a diagonal. "
            "You can edit the length of any diagonal to recalculate the polygon."
        )
        diagonals_info.setWordWrap(True)
        diagonals_layout.addWidget(diagonals_info)

        # Create a container for diagonal inputs
        self.diagonals_container = QWidget()
        self.diagonals_container_layout = QVBoxLayout(self.diagonals_container)
        self.diagonals_container_layout.setContentsMargins(0, 0, 0, 0)
        diagonals_layout.addWidget(self.diagonals_container)

        # We'll dynamically add diagonal input fields in _update_ui

        scroll_layout.addWidget(diagonals_group)

        # Add stretch to push everything to the top
        scroll_layout.addStretch()

        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        properties_layout.addWidget(scroll_area)

        # Add tabs to the right panel
        right_panel.addTab(viz_tab, "Visualization")
        right_panel.addTab(properties_tab, "Properties")

        # Add panels to the main layout
        main_layout.addWidget(left_panel, 1)  # 1/3 of the width
        main_layout.addWidget(right_panel, 2)  # 2/3 of the width

        # Update the UI with initial values
        self._update_ui()

        # Now that the UI is initialized, register with the polygon service
        # Use a timer to ensure the panel is fully initialized before registering
        from PyQt6.QtCore import QTimer

        def register_panel():
            print(
                f"Registering panel {self.panel_id} with fields: {self.available_fields}"
            )
            self.polygon_service.register_panel(
                self.panel_id, self, self.available_fields
            )
            print(
                f"Panel registered. Available panels: {self.polygon_service.get_available_panels()}"
            )

        # Register after a short delay to ensure the panel is fully initialized
        QTimer.singleShot(100, register_panel)

    def _update_polygon(self) -> None:
        """Update the polygon based on UI inputs."""
        # Get values from UI
        sides = self.sides_spin.value()
        radius = self.radius_spin.value()
        orientation = self.orientation_combo.currentData()

        # Update calculator
        self.calculator.set_sides(sides)
        self.calculator.set_radius(radius)
        self.calculator.set_orientation(orientation)

        # Update visualization
        self.viz_widget.set_calculator(self.calculator)

        # Update UI
        self._update_ui()

    def _update_visualization(self) -> None:
        """Update the visualization based on UI inputs."""
        # Update visualization options
        self.viz_widget.toggle_incircle(self.incircle_check.isChecked())
        self.viz_widget.toggle_circumcircle(self.circumcircle_check.isChecked())
        self.viz_widget.toggle_apothem(self.apothem_check.isChecked())
        self.viz_widget.toggle_diagonals(self.diagonals_check.isChecked())
        self.viz_widget.toggle_central_angles(self.central_angles_check.isChecked())
        self.viz_widget.toggle_interior_angles(self.interior_angles_check.isChecked())
        self.viz_widget.toggle_exterior_angles(self.exterior_angles_check.isChecked())
        self.viz_widget.toggle_vertex_labels(self.vertex_labels_check.isChecked())
        self.viz_widget.toggle_edge_labels(self.edge_labels_check.isChecked())
        self.viz_widget.toggle_measurements(self.measurements_check.isChecked())

    def _update_ui(self) -> None:
        """Update the UI with calculated values."""
        # Block signals to prevent recursive updates
        self._block_signals(True)

        try:
            # Basic properties
            self.sides_label.setText(str(self.calculator.sides))
            self.interior_angle_label.setText(
                f"{self.calculator.calculate_interior_angle():.2f}°"
            )
            self.exterior_angle_label.setText(
                f"{self.calculator.calculate_exterior_angle():.2f}°"
            )
            self.central_angle_label.setText(
                f"{self.calculator.calculate_central_angle():.2f}°"
            )

            # Update edge length spin box
            edge_length = self.calculator.calculate_edge_length()
            self.edge_length_spin.setValue(edge_length)

            # Update perimeter spin box
            perimeter = self.calculator.calculate_perimeter()
            self.perimeter_spin.setValue(perimeter)

            # Update area spin box
            area = self.calculator.calculate_area()
            self.area_spin.setValue(area)

            # Circle properties
            # Update radius spin box
            self.radius_spin_display.setValue(self.calculator.radius)

            # Update inradius spin box
            inradius = self.calculator.calculate_inradius()
            self.inradius_spin.setValue(inradius)

            # Apothem (calculated value)
            self.apothem_label.setText(f"{self.calculator.calculate_apothem():.4f}")

            # Update incircle area spin box
            incircle_area = self.calculator.calculate_incircle_area()
            self.incircle_area_spin.setValue(incircle_area)

            # Update circumcircle area spin box
            circumcircle_area = self.calculator.calculate_circumcircle_area()
            self.circumcircle_area_spin.setValue(circumcircle_area)

            # Update incircle circumference spin box
            incircle_circumference = self.calculator.calculate_incircle_circumference()
            self.incircle_circumference_spin.setValue(incircle_circumference)

            # Update circumcircle circumference spin box
            circumcircle_circumference = (
                self.calculator.calculate_circumcircle_circumference()
            )
            self.circumcircle_circumference_spin.setValue(circumcircle_circumference)
        finally:
            # Unblock signals
            self._block_signals(False)

        # Advanced properties
        self.diagonals_count_label.setText(
            str(self.calculator.calculate_total_diagonals_count())
        )
        self.polygon_to_circle_ratio_label.setText(
            f"{self.calculator.calculate_polygon_to_circle_area_ratio():.4f}"
        )
        self.circle_to_polygon_ratio_label.setText(
            f"{self.calculator.calculate_circle_to_polygon_area_ratio():.4f}"
        )

        constructible = self.calculator.is_constructible_with_compass_and_straightedge()
        self.constructible_label.setText("Yes" if constructible else "No")

        # Clear existing diagonal inputs
        while self.diagonals_container_layout.count():
            item = self.diagonals_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Diagonals inputs
        diagonals = self.calculator.calculate_diagonals()

        # Get total diagonals count
        total_diagonals = self.calculator.calculate_total_diagonals_count()

        if diagonals:
            # Create a header
            header = QWidget()
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(5, 5, 5, 5)

            skip_label = QLabel("Skip Pattern")
            skip_label.setStyleSheet("font-weight: bold;")
            header_layout.addWidget(skip_label, 1)

            count_label = QLabel("Count")
            count_label.setStyleSheet("font-weight: bold;")
            header_layout.addWidget(count_label, 1)

            length_label = QLabel("Length")
            length_label.setStyleSheet("font-weight: bold;")
            header_layout.addWidget(length_label, 1)

            self.diagonals_container_layout.addWidget(header)

            # Add a row for each diagonal type
            for i, (skip, count, length) in enumerate(diagonals):
                row = QWidget()
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(5, 5, 5, 5)

                # Skip pattern label
                skip_label = QLabel(f"Skip {skip}")
                row_layout.addWidget(skip_label, 1)

                # Count label
                count_label = QLabel(str(count))
                row_layout.addWidget(count_label, 1)

                # Length spinner
                length_spin = QDoubleSpinBox()
                length_spin.setRange(0.1, 10000.0)
                length_spin.setDecimals(4)
                length_spin.setSingleStep(1.0)
                length_spin.setValue(length)
                length_spin.setProperty("skip", skip)  # Store skip value for reference
                length_spin.editingFinished.connect(self._diagonal_length_changed)
                row_layout.addWidget(length_spin, 1)

                self.diagonals_container_layout.addWidget(row)

            # Add a stretch at the end
            self.diagonals_container_layout.addStretch()
        elif self.calculator.sides == 3:
            # Special message for triangles
            no_diagonals = QLabel("A triangle has no diagonals")
            no_diagonals.setStyleSheet("color: #666;")
            self.diagonals_container_layout.addWidget(no_diagonals)
            self.diagonals_container_layout.addStretch()
        elif self.calculator.sides < 3:
            # Invalid polygon
            no_diagonals = QLabel("Not a valid polygon (needs at least 3 sides)")
            no_diagonals.setStyleSheet("color: #666;")
            self.diagonals_container_layout.addWidget(no_diagonals)
            self.diagonals_container_layout.addStretch()
        else:
            # This should not happen with our fixes, but just in case
            no_diagonals = QLabel(
                f"No diagonals found for this {self.calculator.sides}-sided polygon"
            )
            no_diagonals.setStyleSheet("color: #666;")
            self.diagonals_container_layout.addWidget(no_diagonals)
            self.diagonals_container_layout.addStretch()

    def _block_signals(self, block: bool) -> None:
        """Block or unblock signals from all input widgets.

        Args:
            block: True to block signals, False to unblock
        """
        widgets = [
            self.edge_length_spin,
            self.perimeter_spin,
            self.area_spin,
            self.radius_spin_display,
            self.inradius_spin,
            self.incircle_circumference_spin,
            self.circumcircle_circumference_spin,
            self.incircle_area_spin,
            self.circumcircle_area_spin,
        ]

        # Also block any diagonal spinners if they exist
        for i in range(self.diagonals_container_layout.count()):
            item = self.diagonals_container_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                # Find any QDoubleSpinBox in the widget
                for child in widget.findChildren(QDoubleSpinBox):
                    widgets.append(child)

        for widget in widgets:
            widget.blockSignals(block)

    def _edge_length_changed(self) -> None:
        """Handle edge length change."""
        edge_length = self.edge_length_spin.value()

        # Calculate the radius from the edge length
        # edge_length = 2 * radius * sin(pi/sides)
        # radius = edge_length / (2 * sin(pi/sides))
        radius = edge_length / (2 * math.sin(math.pi / self.calculator.sides))

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _perimeter_changed(self) -> None:
        """Handle perimeter change."""
        perimeter = self.perimeter_spin.value()

        # Calculate the edge length from the perimeter
        # perimeter = sides * edge_length
        # edge_length = perimeter / sides
        edge_length = perimeter / self.calculator.sides

        # Calculate the radius from the edge length
        # edge_length = 2 * radius * sin(pi/sides)
        # radius = edge_length / (2 * sin(pi/sides))
        radius = edge_length / (2 * math.sin(math.pi / self.calculator.sides))

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _area_changed(self) -> None:
        """Handle area change."""
        area = self.area_spin.value()

        # Calculate the radius from the area
        # area = 0.5 * sides * radius^2 * sin(2*pi/sides)
        # radius^2 = area / (0.5 * sides * sin(2*pi/sides))
        # radius = sqrt(area / (0.5 * sides * sin(2*pi/sides)))
        radius_squared = area / (
            0.5 * self.calculator.sides * math.sin(2 * math.pi / self.calculator.sides)
        )
        radius = math.sqrt(radius_squared)

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _radius_changed(self) -> None:
        """Handle radius change."""
        radius = self.radius_spin_display.value()

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the main radius spinner to match
        self.radius_spin.setValue(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _inradius_changed(self) -> None:
        """Handle inradius change."""
        inradius = self.inradius_spin.value()

        # Calculate the radius from the inradius
        # inradius = radius * cos(pi/sides)
        # radius = inradius / cos(pi/sides)
        radius = inradius / math.cos(math.pi / self.calculator.sides)

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _incircle_circumference_changed(self) -> None:
        """Handle incircle circumference change."""
        circumference = self.incircle_circumference_spin.value()

        # Calculate the inradius from the circumference
        # circumference = 2 * pi * inradius
        # inradius = circumference / (2 * pi)
        inradius = circumference / (2 * math.pi)

        # Calculate the radius from the inradius
        # inradius = radius * cos(pi/sides)
        # radius = inradius / cos(pi/sides)
        radius = inradius / math.cos(math.pi / self.calculator.sides)

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _incircle_area_changed(self) -> None:
        """Handle incircle area change."""
        area = self.incircle_area_spin.value()

        # Calculate the inradius from the area
        # area = pi * inradius^2
        # inradius = sqrt(area / pi)
        inradius = math.sqrt(area / math.pi)

        # Calculate the radius from the inradius
        # inradius = radius * cos(pi/sides)
        # radius = inradius / cos(pi/sides)
        radius = inradius / math.cos(math.pi / self.calculator.sides)

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _circumcircle_circumference_changed(self) -> None:
        """Handle circumcircle circumference change."""
        circumference = self.circumcircle_circumference_spin.value()

        # Calculate the radius from the circumference
        # circumference = 2 * pi * radius
        # radius = circumference / (2 * pi)
        radius = circumference / (2 * math.pi)

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _circumcircle_area_changed(self) -> None:
        """Handle circumcircle area change."""
        area = self.circumcircle_area_spin.value()

        # Calculate the radius from the area
        # area = pi * radius^2
        # radius = sqrt(area / pi)
        radius = math.sqrt(area / math.pi)

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _diagonal_length_changed(self) -> None:
        """Handle diagonal length change."""
        # Get the sender (the spin box that was changed)
        spin_box = self.sender()
        if not spin_box:
            return

        # Get the skip value and the new length
        skip = spin_box.property("skip")
        length = spin_box.value()

        if not skip:
            return

        # Calculate the radius from the diagonal length
        # diagonal_length = 2 * radius * sin(skip * pi / sides)
        # radius = diagonal_length / (2 * sin(skip * pi / sides))
        radius = length / (2 * math.sin(skip * math.pi / self.calculator.sides))

        # Update the calculator
        self.calculator.set_radius(radius)

        # Update the visualization and UI
        self.viz_widget.set_calculator(self.calculator)
        self._update_ui()

    def _set_preset(self, sides: int) -> None:
        """Set a preset polygon.

        Args:
            sides: Number of sides for the preset polygon
        """
        self.sides_spin.setValue(sides)
        # Keep the current radius and orientation

    def receive_value(self, field_name: str, value: float) -> None:
        """Receive a value from another pillar.

        Args:
            field_name: Name of the field to receive the value
            value: Value to set
        """
        print(
            f"RegularPolygonPanel.receive_value called with field_name={field_name}, value={value}"
        )

        # Map field names to methods
        field_handlers = {
            "Sides": self._set_sides,
            "Radius": self._set_radius,
            "Edge Length": self._set_edge_length,
            "Perimeter": self._set_perimeter,
            "Area": self._set_area,
            "Inradius": self._set_inradius,
            "Incircle Circumference": self._set_incircle_circumference,
            "Incircle Area": self._set_incircle_area,
            "Circumcircle Circumference": self._set_circumcircle_circumference,
            "Circumcircle Area": self._set_circumcircle_area,
        }

        # Call the appropriate handler
        if field_name in field_handlers:
            print(f"Calling handler for field {field_name}")
            try:
                field_handlers[field_name](value)
                print(f"Successfully set {field_name} to {value}")
            except Exception as e:
                print(f"Error setting {field_name} to {value}: {e}")
        else:
            print(f"No handler found for field {field_name}")
            print(f"Available handlers: {list(field_handlers.keys())}")

    def _set_sides(self, value: float) -> None:
        """Set the number of sides.

        Args:
            value: Number of sides
        """
        print(f"_set_sides called with value={value}")
        try:
            sides = int(value)
            print(f"Converted to sides={sides}")
            if sides >= 3:
                print(f"Setting sides_spin to {sides}")
                self.sides_spin.setValue(sides)
                print("Calling _sides_changed()")
                self._sides_changed()
                print("_sides_changed() completed")
            else:
                print(f"Sides value {sides} is less than 3, ignoring")
        except Exception as e:
            print(f"Error in _set_sides: {e}")

    def _set_radius(self, value: float) -> None:
        """Set the radius.

        Args:
            value: Radius
        """
        if value > 0:
            self.radius_spin_display.setValue(value)
            self._radius_changed()

    def _set_edge_length(self, value: float) -> None:
        """Set the edge length.

        Args:
            value: Edge length
        """
        if value > 0:
            self.edge_length_spin.setValue(value)
            self._edge_length_changed()

    def _set_perimeter(self, value: float) -> None:
        """Set the perimeter.

        Args:
            value: Perimeter
        """
        if value > 0:
            self.perimeter_spin.setValue(value)
            self._perimeter_changed()

    def _set_area(self, value: float) -> None:
        """Set the area.

        Args:
            value: Area
        """
        if value > 0:
            self.area_spin.setValue(value)
            self._area_changed()

    def _set_inradius(self, value: float) -> None:
        """Set the inradius.

        Args:
            value: Inradius
        """
        if value > 0:
            self.inradius_spin.setValue(value)
            self._inradius_changed()

    def _set_incircle_circumference(self, value: float) -> None:
        """Set the incircle circumference.

        Args:
            value: Incircle circumference
        """
        if value > 0:
            self.incircle_circumference_spin.setValue(value)
            self._incircle_circumference_changed()

    def _set_incircle_area(self, value: float) -> None:
        """Set the incircle area.

        Args:
            value: Incircle area
        """
        if value > 0:
            self.incircle_area_spin.setValue(value)
            self._incircle_area_changed()

    def _set_circumcircle_circumference(self, value: float) -> None:
        """Set the circumcircle circumference.

        Args:
            value: Circumcircle circumference
        """
        if value > 0:
            self.circumcircle_circumference_spin.setValue(value)
            self._circumcircle_circumference_changed()

    def _set_circumcircle_area(self, value: float) -> None:
        """Set the circumcircle area.

        Args:
            value: Circumcircle area
        """
        if value > 0:
            self.circumcircle_area_spin.setValue(value)
            self._circumcircle_area_changed()

    def closeEvent(self, event):
        """Handle the panel being closed.

        Args:
            event: Close event
        """
        # Unregister from the polygon service
        print(f"Unregistering panel {self.panel_id}")
        self.polygon_service.unregister_panel(self.panel_id)
        print(
            f"Panel unregistered. Available panels: {self.polygon_service.get_available_panels()}"
        )

        # Call the parent class's closeEvent method
        super().closeEvent(event)
