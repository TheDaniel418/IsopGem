"""Nested heptagons calculator panel.

This module provides a panel for visualizing and calculating properties of nested heptagons.
"""

import math

from PyQt6.QtCore import QLineF, QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF, QAction
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from geometry.calculator.nested_heptagons_calculator import NestedHeptagonsCalculator
from geometry.services.polygon_service import PolygonService

# Check if TQ module is available
try:
    from tq.services import tq_analysis_service
    TQ_AVAILABLE = True
except ImportError:
    TQ_AVAILABLE = False


class NestedHeptagonsVisualization(QWidget):
    """Widget for visualizing nested heptagons."""

    def __init__(self, parent=None):
        """Initialize the visualization widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculator = NestedHeptagonsCalculator()
        self.show_incircle = True
        self.show_circumcircle = True
        self.show_outer_heptagon = True
        self.show_middle_heptagon = True
        self.show_inner_heptagon = True
        self.show_diagonals = False
        self.show_vertex_labels = True
        self.show_measurements = True

        # Set minimum size for better visualization
        self.setMinimumSize(400, 400)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(240, 240, 240))
        self.setPalette(palette)

    def set_calculator(self, calculator: NestedHeptagonsCalculator) -> None:
        """Set the calculator for the visualization.

        Args:
            calculator: Nested heptagons calculator
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

    def toggle_outer_heptagon(self, show: bool) -> None:
        """Toggle the visibility of the outer heptagon.

        Args:
            show: Whether to show the outer heptagon
        """
        self.show_outer_heptagon = show
        self.update()

    def toggle_middle_heptagon(self, show: bool) -> None:
        """Toggle the visibility of the middle heptagon.

        Args:
            show: Whether to show the middle heptagon
        """
        self.show_middle_heptagon = show
        self.update()

    def toggle_inner_heptagon(self, show: bool) -> None:
        """Toggle the visibility of the inner heptagon.

        Args:
            show: Whether to show the inner heptagon
        """
        self.show_inner_heptagon = show
        self.update()

    def toggle_diagonals(self, show: bool) -> None:
        """Toggle the visibility of the diagonals.

        Args:
            show: Whether to show the diagonals
        """
        self.show_diagonals = show
        self.update()

    def toggle_vertex_labels(self, show: bool) -> None:
        """Toggle the visibility of the vertex labels.

        Args:
            show: Whether to show the vertex labels
        """
        self.show_vertex_labels = show
        self.update()

    def toggle_measurements(self, show: bool) -> None:
        """Toggle the visibility of the measurements.

        Args:
            show: Whether to show the measurements
        """
        self.show_measurements = show
        self.update()

    def paintEvent(self, _) -> None:
        """Paint the visualization.

        Args:
            _: Paint event (not used)
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2

        # Calculate scale factor based on the minimum dimension
        min_dimension = min(width, height)
        scale_factor = min_dimension / (
            2.5 * self.calculator.calculate_outer_circumradius()
        )

        # Calculate vertices
        outer_vertices = self.calculator.calculate_outer_vertices()
        middle_vertices = self.calculator.calculate_middle_vertices()
        inner_vertices = self.calculator.calculate_inner_vertices()

        # Draw the circumcircle (outer heptagon)
        if self.show_circumcircle:
            painter.setPen(QPen(QColor(200, 200, 255), 1))
            outer_radius = self.calculator.calculate_outer_circumradius()
            painter.drawEllipse(
                QPointF(center_x, center_y),
                outer_radius * scale_factor,
                outer_radius * scale_factor,
            )

            # Draw the radius line for the circumcircle
            if self.show_measurements:
                painter.setPen(QPen(QColor(200, 200, 255), 1, Qt.PenStyle.DashLine))
                painter.drawLine(
                    QLineF(
                        QPointF(center_x, center_y),
                        QPointF(center_x, center_y - outer_radius * scale_factor),
                    )
                )

                # Add the radius label
                painter.setPen(QPen(QColor(200, 200, 255), 1))
                painter.drawText(
                    int(center_x + 10),
                    int(center_y - outer_radius * scale_factor / 2),
                    f"R = {outer_radius:.2f}",
                )

        # Draw the incircle (outer heptagon)
        if self.show_incircle:
            painter.setPen(QPen(QColor(255, 200, 200), 1))
            inradius = self.calculator.calculate_outer_inradius()
            painter.drawEllipse(
                QPointF(center_x, center_y),
                inradius * scale_factor,
                inradius * scale_factor,
            )

            # Draw the radius line for the incircle
            if self.show_measurements:
                painter.setPen(QPen(QColor(255, 200, 200), 1, Qt.PenStyle.DashLine))
                # Draw at an angle to distinguish from the circumcircle radius line
                angle = math.pi / 4
                x_offset = inradius * scale_factor * math.cos(angle)
                y_offset = inradius * scale_factor * math.sin(angle)
                painter.drawLine(
                    QLineF(
                        QPointF(center_x, center_y),
                        QPointF(center_x + x_offset, center_y - y_offset),
                    )
                )

                # Add the radius label
                painter.setPen(QPen(QColor(255, 200, 200), 1))
                painter.drawText(
                    int(center_x + x_offset / 2),
                    int(center_y - y_offset / 2),
                    f"r = {inradius:.2f}",
                )

        # Draw the outer heptagon
        if self.show_outer_heptagon:
            # Create a polygon for the outer heptagon
            polygon = QPolygonF()
            for vertex in outer_vertices:
                x = center_x + vertex.x * scale_factor
                y = center_y + vertex.y * scale_factor
                polygon.append(QPointF(x, y))

            # Draw the polygon outline
            painter.setPen(QPen(QColor(50, 50, 200), 2))
            painter.drawPolygon(polygon)

            # Draw the short diagonals (connecting vertices that skip one vertex)
            if self.show_diagonals:
                painter.setPen(QPen(QColor(100, 100, 220), 1, Qt.PenStyle.DashLine))
                for i in range(self.calculator.sides):
                    x1 = center_x + outer_vertices[i].x * scale_factor
                    y1 = center_y + outer_vertices[i].y * scale_factor

                    # Connect to vertex i+2 (skipping one vertex)
                    j = (i + 2) % self.calculator.sides
                    x2 = center_x + outer_vertices[j].x * scale_factor
                    y2 = center_y + outer_vertices[j].y * scale_factor

                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

                    # Draw the long diagonals (connecting vertices that skip two vertices)
                    painter.setPen(QPen(QColor(150, 150, 240), 1, Qt.PenStyle.DotLine))
                    # Connect to vertex i+3 (skipping two vertices)
                    k = (i + 3) % self.calculator.sides
                    x3 = center_x + outer_vertices[k].x * scale_factor
                    y3 = center_y + outer_vertices[k].y * scale_factor

                    painter.drawLine(QPointF(x1, y1), QPointF(x3, y3))

            # Draw vertex labels for outer heptagon
            if self.show_vertex_labels:
                painter.setPen(QPen(QColor(50, 50, 200), 1))
                for i, vertex in enumerate(outer_vertices):
                    x = center_x + vertex.x * scale_factor
                    y = center_y + vertex.y * scale_factor

                    # Adjust label position based on vertex position relative to center
                    dx = vertex.x
                    dy = vertex.y
                    magnitude = math.sqrt(dx * dx + dy * dy)
                    if magnitude > 0:
                        # Normalize and apply offset
                        dx = dx / magnitude * 15
                        dy = dy / magnitude * 15

                    painter.drawText(int(x + dx), int(y + dy), f"O{i + 1}")

            # Draw edge lengths for outer heptagon
            if self.show_measurements:
                painter.setPen(QPen(QColor(50, 50, 200), 1))
                edge_length = self.calculator.calculate_outer_edge_length()

                # Display the edge length on the first edge only
                i = 0
                j = (i + 1) % self.calculator.sides

                x1 = center_x + outer_vertices[i].x * scale_factor
                y1 = center_y + outer_vertices[i].y * scale_factor
                x2 = center_x + outer_vertices[j].x * scale_factor
                y2 = center_y + outer_vertices[j].y * scale_factor

                # Calculate midpoint of the edge
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                # Calculate perpendicular offset for label
                edge_dx = x2 - x1
                edge_dy = y2 - y1
                length = math.sqrt(edge_dx * edge_dx + edge_dy * edge_dy)

                if length > 0:
                    nx = -edge_dy / length * 15  # Perpendicular and scaled
                    ny = edge_dx / length * 15

                    painter.drawText(
                        int(mid_x + nx), int(mid_y + ny), f"a = {edge_length:.2f}"
                    )

        # Draw the middle heptagon
        if self.show_middle_heptagon:
            # Create a polygon for the middle heptagon
            polygon = QPolygonF()
            for vertex in middle_vertices:
                x = center_x + vertex.x * scale_factor
                y = center_y + vertex.y * scale_factor
                polygon.append(QPointF(x, y))

            # Draw the polygon outline
            painter.setPen(QPen(QColor(50, 150, 50), 2))
            painter.drawPolygon(polygon)

            # Draw vertex labels for middle heptagon
            if self.show_vertex_labels:
                painter.setPen(QPen(QColor(50, 150, 50), 1))
                for i, vertex in enumerate(middle_vertices):
                    x = center_x + vertex.x * scale_factor
                    y = center_y + vertex.y * scale_factor

                    # Adjust label position based on vertex position relative to center
                    dx = vertex.x
                    dy = vertex.y
                    magnitude = math.sqrt(dx * dx + dy * dy)
                    if magnitude > 0:
                        # Normalize and apply offset
                        dx = dx / magnitude * 15
                        dy = dy / magnitude * 15

                    painter.drawText(int(x + dx), int(y + dy), f"M{i + 1}")

            # Draw edge lengths for middle heptagon
            if self.show_measurements:
                painter.setPen(QPen(QColor(50, 150, 50), 1))
                edge_length = self.calculator.calculate_middle_edge_length()

                # Display the edge length on the first edge only
                i = 0
                j = (i + 1) % self.calculator.sides

                x1 = center_x + middle_vertices[i].x * scale_factor
                y1 = center_y + middle_vertices[i].y * scale_factor
                x2 = center_x + middle_vertices[j].x * scale_factor
                y2 = center_y + middle_vertices[j].y * scale_factor

                # Calculate midpoint of the edge
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                # Calculate perpendicular offset for label
                edge_dx = x2 - x1
                edge_dy = y2 - y1
                length = math.sqrt(edge_dx * edge_dx + edge_dy * edge_dy)

                if length > 0:
                    nx = -edge_dy / length * 15  # Perpendicular and scaled
                    ny = edge_dx / length * 15

                    painter.drawText(
                        int(mid_x + nx), int(mid_y + ny), f"b = {edge_length:.2f}"
                    )

        # Draw the inner heptagon
        if self.show_inner_heptagon:
            # Create a polygon for the inner heptagon
            polygon = QPolygonF()
            for vertex in inner_vertices:
                x = center_x + vertex.x * scale_factor
                y = center_y + vertex.y * scale_factor
                polygon.append(QPointF(x, y))

            # Draw the polygon outline
            painter.setPen(QPen(QColor(200, 50, 50), 2))
            painter.drawPolygon(polygon)

            # Draw vertex labels for inner heptagon
            if self.show_vertex_labels:
                painter.setPen(QPen(QColor(200, 50, 50), 1))
                for i, vertex in enumerate(inner_vertices):
                    x = center_x + vertex.x * scale_factor
                    y = center_y + vertex.y * scale_factor

                    # Adjust label position based on vertex position relative to center
                    dx = vertex.x
                    dy = vertex.y
                    magnitude = math.sqrt(dx * dx + dy * dy)
                    if magnitude > 0:
                        # Normalize and apply offset
                        dx = dx / magnitude * 15
                        dy = dy / magnitude * 15

                    painter.drawText(int(x + dx), int(y + dy), f"I{i + 1}")

            # Draw edge lengths for inner heptagon
            if self.show_measurements:
                painter.setPen(QPen(QColor(200, 50, 50), 1))
                edge_length = self.calculator.calculate_inner_edge_length()

                # Display the edge length on the first edge only
                i = 0
                j = (i + 1) % self.calculator.sides

                x1 = center_x + inner_vertices[i].x * scale_factor
                y1 = center_y + inner_vertices[i].y * scale_factor
                x2 = center_x + inner_vertices[j].x * scale_factor
                y2 = center_y + inner_vertices[j].y * scale_factor

                # Calculate midpoint of the edge
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                # Calculate perpendicular offset for label
                edge_dx = x2 - x1
                edge_dy = y2 - y1
                length = math.sqrt(edge_dx * edge_dx + edge_dy * edge_dy)

                if length > 0:
                    nx = -edge_dy / length * 15  # Perpendicular and scaled
                    ny = edge_dx / length * 15

                    painter.drawText(
                        int(mid_x + nx), int(mid_y + ny), f"c = {edge_length:.2f}"
                    )


class NestedHeptagonsPanel(QWidget):
    """Panel for the nested heptagons calculator."""

    def __init__(self, parent=None):
        """Initialize the nested heptagons panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculator = NestedHeptagonsCalculator()
        self.setMinimumSize(900, 650)  # Set minimum size for the panel

        # Register with the polygon service
        self.polygon_service = PolygonService()
        self.panel_id = "nested_heptagons"
        self.available_fields = [
            "Outer Edge Length",
            "Outer Perimeter",
            "Outer Area",
            "Outer Short Diagonal",
            "Outer Long Diagonal",
            "Outer Inradius",
            "Outer Circumradius",
            "Middle Edge Length",
            "Middle Perimeter",
            "Middle Area",
            "Middle Short Diagonal",
            "Middle Long Diagonal",
            "Middle Inradius",
            "Middle Circumradius",
            "Inner Edge Length",
            "Inner Perimeter",
            "Inner Area",
            "Inner Short Diagonal",
            "Inner Long Diagonal",
            "Inner Inradius",
            "Inner Circumradius",
        ]

        # Dictionary to store value labels for context menu access
        self.value_labels = {}

        self._init_ui()

        # Register with the polygon service
        self.polygon_service.register_panel(self.panel_id, self, self.available_fields)

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        # main_layout.setContentsMargins(20, 20, 20, 20)
        # main_layout.setSpacing(15)

        # Scroll Area
        scroll_area_main_controls = QScrollArea(self)  # Renamed for clarity
        scroll_area_main_controls.setWidgetResizable(True)
        scroll_area_main_controls.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        scroll_area_main_controls.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        scroll_content_main_controls = QWidget()  # Renamed for clarity
        layout_main_controls = QVBoxLayout(
            scroll_content_main_controls
        )  # Renamed for clarity

        # Input Group for Heptagon Properties
        input_group = QGroupBox("Heptagon Properties (Primary Inputs)")  # Title updated
        input_layout = QFormLayout(input_group)
        input_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        input_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        input_layout.setFormAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        input_layout.setSpacing(10)

        # Outer Heptagon Edge Length Input
        self.outer_edge_input_spin = (
            QDoubleSpinBox()
        )  # Renamed from self.edge_length_spin
        self.outer_edge_input_spin.setRange(0.01, 10000.0)
        self.outer_edge_input_spin.setValue(
            self.calculator.calculate_outer_edge_length()
        )
        self.outer_edge_input_spin.setSuffix(" units")
        self.outer_edge_input_spin.setToolTip(
            "Enter the edge length for the outer heptagon. This will update all other values."
        )
        self.outer_edge_input_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_edge", self.outer_edge_input_spin.value()
            )
        )
        input_layout.addRow(QLabel("Outer Edge:"), self.outer_edge_input_spin)

        # Middle Heptagon Edge Length Input
        self.middle_edge_input_spin = QDoubleSpinBox()
        self.middle_edge_input_spin.setRange(0.01, 10000.0)
        self.middle_edge_input_spin.setValue(
            self.calculator.calculate_middle_edge_length()
        )
        self.middle_edge_input_spin.setSuffix(" units")
        self.middle_edge_input_spin.setToolTip(
            "Enter the edge length for the middle heptagon. This will update all other values."
        )
        self.middle_edge_input_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_edge", self.middle_edge_input_spin.value()
            )
        )
        input_layout.addRow(QLabel("Middle Edge:"), self.middle_edge_input_spin)

        # Inner Heptagon Edge Length Input
        self.inner_edge_input_spin = QDoubleSpinBox()
        self.inner_edge_input_spin.setRange(0.01, 10000.0)
        self.inner_edge_input_spin.setValue(
            self.calculator.calculate_inner_edge_length()
        )
        self.inner_edge_input_spin.setSuffix(" units")
        self.inner_edge_input_spin.setToolTip(
            "Enter the edge length for the inner heptagon. This will update all other values."
        )
        self.inner_edge_input_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_edge", self.inner_edge_input_spin.value()
            )
        )
        input_layout.addRow(QLabel("Inner Edge:"), self.inner_edge_input_spin)

        # Orientation
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItem("Vertex at Top", "vertex_top")
        self.orientation_combo.addItem("Side at Top", "side_top")
        self.orientation_combo.currentIndexChanged.connect(self._update_orientation)
        input_layout.addRow("Orientation:", self.orientation_combo)

        # Add input group to left layout
        layout_main_controls.addWidget(input_group)

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

        self.outer_heptagon_check = QCheckBox("Show Outer Heptagon")
        self.outer_heptagon_check.setChecked(True)
        self.outer_heptagon_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.outer_heptagon_check, 1, 0)

        self.middle_heptagon_check = QCheckBox("Show Middle Heptagon")
        self.middle_heptagon_check.setChecked(True)
        self.middle_heptagon_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.middle_heptagon_check, 1, 1)

        self.inner_heptagon_check = QCheckBox("Show Inner Heptagon")
        self.inner_heptagon_check.setChecked(True)
        self.inner_heptagon_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.inner_heptagon_check, 2, 0)

        self.diagonals_check = QCheckBox("Show Diagonals")
        self.diagonals_check.setChecked(False)
        self.diagonals_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.diagonals_check, 2, 1)

        self.vertex_labels_check = QCheckBox("Show Vertex Labels")
        self.vertex_labels_check.setChecked(True)
        self.vertex_labels_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.vertex_labels_check, 3, 0)

        self.measurements_check = QCheckBox("Show Measurements")
        self.measurements_check.setChecked(True)
        self.measurements_check.stateChanged.connect(self._update_visualization)
        viz_layout.addWidget(self.measurements_check, 3, 1)

        # Add visualization group to left layout
        layout_main_controls.addWidget(viz_group)

        # Information group with golden trisection ratios
        info_group = QGroupBox("Golden Trisection Ratios")
        info_layout = QFormLayout(info_group)

        # Add golden trisection constants
        sigma_label = QLabel(f"{self.calculator.SIGMA:.6f}")
        sigma_label.setToolTip("Long diagonal in a unit-edge heptagon")
        info_layout.addRow("Σ (SIGMA):", sigma_label)

        rho_label = QLabel(f"{self.calculator.RHO:.6f}")
        rho_label.setToolTip("Short diagonal in a unit-edge heptagon")
        info_layout.addRow("Ρ (RHO):", rho_label)

        alpha_label = QLabel(f"{self.calculator.ALPHA:.6f}")
        alpha_label.setToolTip(
            "Edge length of nested heptagon inside unit-edge heptagon"
        )
        info_layout.addRow("α (ALPHA):", alpha_label)

        # Add info group to left layout
        layout_main_controls.addWidget(info_group)

        # Add stretch to push everything to the top
        layout_main_controls.addStretch()

        scroll_content_main_controls.setLayout(layout_main_controls)
        scroll_area_main_controls.setWidget(scroll_content_main_controls)

        # Right panel with tabs
        right_panel = QTabWidget()

        # Visualization tab
        viz_tab = QWidget()
        viz_tab_layout = QVBoxLayout(viz_tab)

        # Visualization widget
        self.viz_widget = NestedHeptagonsVisualization()
        self.viz_widget.set_calculator(self.calculator)
        viz_tab_layout.addWidget(self.viz_widget)

        # Properties tab
        calc_tab = QWidget()
        calc_layout = QVBoxLayout(calc_tab)

        # Scroll area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Outer heptagon properties group
        outer_group = QGroupBox("Outer Heptagon Properties")
        outer_layout = QFormLayout(outer_group)

        # Edge length
        self.outer_edge_spin = (
            QDoubleSpinBox()
        )  # This is for display in the calculator tab
        self.outer_edge_spin.setRange(0.01, 1e9)  # Adjusted range to match inputs
        self.outer_edge_spin.setValue(self.calculator.calculate_outer_edge_length())
        self.outer_edge_spin.setSingleStep(1.0)
        self.outer_edge_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_edge", self.outer_edge_spin.value()
            )
        )
        self.value_labels["Outer Edge Length"] = self.outer_edge_spin
        outer_layout.addRow("Edge Length:", self.outer_edge_spin)

        # Perimeter
        self.outer_perimeter_spin = QDoubleSpinBox()
        self.outer_perimeter_spin.setRange(1.0, 1e9)
        self.outer_perimeter_spin.setValue(self.calculator.calculate_outer_perimeter())
        self.outer_perimeter_spin.setSingleStep(1.0)
        self.outer_perimeter_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_perimeter", self.outer_perimeter_spin.value()
            )
        )
        self.value_labels["Outer Perimeter"] = self.outer_perimeter_spin
        outer_layout.addRow("Perimeter:", self.outer_perimeter_spin)

        # Area
        self.outer_area_spin = QDoubleSpinBox()
        self.outer_area_spin.setRange(1.0, 1e9)
        self.outer_area_spin.setValue(self.calculator.calculate_outer_area())
        self.outer_area_spin.setSingleStep(1.0)
        self.outer_area_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_area", self.outer_area_spin.value()
            )
        )
        self.value_labels["Outer Area"] = self.outer_area_spin
        outer_layout.addRow("Area:", self.outer_area_spin)

        # Short diagonal
        self.outer_short_diag_spin = QDoubleSpinBox()
        self.outer_short_diag_spin.setRange(1.0, 1e9)
        self.outer_short_diag_spin.setValue(
            self.calculator.calculate_outer_short_diagonal()
        )
        self.outer_short_diag_spin.setSingleStep(1.0)
        self.outer_short_diag_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_short_diagonal", self.outer_short_diag_spin.value()
            )
        )
        self.value_labels["Outer Short Diagonal"] = self.outer_short_diag_spin
        outer_layout.addRow("Short Diagonal:", self.outer_short_diag_spin)

        # Long diagonal
        self.outer_long_diag_spin = QDoubleSpinBox()
        self.outer_long_diag_spin.setRange(1.0, 1e9)
        self.outer_long_diag_spin.setValue(
            self.calculator.calculate_outer_long_diagonal()
        )
        self.outer_long_diag_spin.setSingleStep(1.0)
        self.outer_long_diag_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_long_diagonal", self.outer_long_diag_spin.value()
            )
        )
        self.value_labels["Outer Long Diagonal"] = self.outer_long_diag_spin
        outer_layout.addRow("Long Diagonal:", self.outer_long_diag_spin)

        # Inradius
        self.outer_inradius_spin = QDoubleSpinBox()
        self.outer_inradius_spin.setRange(0.1, 1e9)
        self.outer_inradius_spin.setValue(self.calculator.calculate_outer_inradius())
        self.outer_inradius_spin.setSingleStep(1.0)
        self.outer_inradius_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_inradius", self.outer_inradius_spin.value()
            )
        )
        self.value_labels["Outer Inradius"] = self.outer_inradius_spin
        outer_layout.addRow("Inradius:", self.outer_inradius_spin)

        # Circumradius
        self.outer_circumradius_spin = QDoubleSpinBox()
        self.outer_circumradius_spin.setRange(0.1, 1e9)
        self.outer_circumradius_spin.setValue(
            self.calculator.calculate_outer_circumradius()
        )
        self.outer_circumradius_spin.setSingleStep(1.0)
        self.outer_circumradius_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_circumradius", self.outer_circumradius_spin.value()
            )
        )
        self.value_labels["Outer Circumradius"] = self.outer_circumradius_spin
        outer_layout.addRow("Circumradius:", self.outer_circumradius_spin)

        # Incircle circumference
        self.outer_incircle_circ_spin = QDoubleSpinBox()
        self.outer_incircle_circ_spin.setRange(0.1, 1e9)
        self.outer_incircle_circ_spin.setValue(
            self.calculator.calculate_outer_incircle_circumference()
        )
        self.outer_incircle_circ_spin.setSingleStep(1.0)
        self.outer_incircle_circ_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_incircle_circ", self.outer_incircle_circ_spin.value()
            )
        )
        self.value_labels[
            "Outer Incircle Circumference"
        ] = self.outer_incircle_circ_spin
        outer_layout.addRow("Incircle Circumference:", self.outer_incircle_circ_spin)

        # Circumcircle circumference
        self.outer_circumcircle_circ_spin = QDoubleSpinBox()
        self.outer_circumcircle_circ_spin.setRange(0.1, 1e9)
        self.outer_circumcircle_circ_spin.setValue(
            self.calculator.calculate_outer_circumcircle_circumference()
        )
        self.outer_circumcircle_circ_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "outer_circumcircle_circ", self.outer_circumcircle_circ_spin.value()
            )
        )
        self.value_labels[
            "Outer Circumcircle Circumference"
        ] = self.outer_circumcircle_circ_spin
        outer_layout.addRow(
            "Circumcircle Circumference:", self.outer_circumcircle_circ_spin
        )

        # Middle heptagon properties group
        middle_group = QGroupBox("Middle Heptagon Properties")
        middle_layout = QFormLayout(middle_group)

        # Edge length
        self.middle_edge_spin = (
            QDoubleSpinBox()
        )  # This is for display in the calculator tab
        self.middle_edge_spin.setRange(0.01, 1e9)  # Adjusted range
        self.middle_edge_spin.setValue(self.calculator.calculate_middle_edge_length())
        self.middle_edge_spin.setSingleStep(1.0)
        self.middle_edge_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_edge", self.middle_edge_spin.value()
            )
        )
        self.value_labels["Middle Edge Length"] = self.middle_edge_spin
        middle_layout.addRow("Edge Length:", self.middle_edge_spin)

        # Perimeter
        self.middle_perimeter_spin = QDoubleSpinBox()
        self.middle_perimeter_spin.setRange(1.0, 1e9)
        self.middle_perimeter_spin.setValue(
            self.calculator.calculate_middle_perimeter()
        )
        self.middle_perimeter_spin.setSingleStep(1.0)
        self.middle_perimeter_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_perimeter", self.middle_perimeter_spin.value()
            )
        )
        self.value_labels["Middle Perimeter"] = self.middle_perimeter_spin
        middle_layout.addRow("Perimeter:", self.middle_perimeter_spin)

        # Area
        self.middle_area_spin = QDoubleSpinBox()
        self.middle_area_spin.setRange(1.0, 1e9)
        self.middle_area_spin.setValue(self.calculator.calculate_middle_area())
        self.middle_area_spin.setSingleStep(1.0)
        self.middle_area_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_area", self.middle_area_spin.value()
            )
        )
        self.value_labels["Middle Area"] = self.middle_area_spin
        middle_layout.addRow("Area:", self.middle_area_spin)

        # Short diagonal
        self.middle_short_diag_spin = QDoubleSpinBox()
        self.middle_short_diag_spin.setRange(1.0, 1e9)
        self.middle_short_diag_spin.setValue(
            self.calculator.calculate_middle_short_diagonal()
        )
        self.middle_short_diag_spin.setSingleStep(1.0)
        self.middle_short_diag_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_short_diagonal", self.middle_short_diag_spin.value()
            )
        )
        self.value_labels["Middle Short Diagonal"] = self.middle_short_diag_spin
        middle_layout.addRow("Short Diagonal:", self.middle_short_diag_spin)

        # Long diagonal
        self.middle_long_diag_spin = QDoubleSpinBox()
        self.middle_long_diag_spin.setRange(1.0, 1e9)
        self.middle_long_diag_spin.setValue(
            self.calculator.calculate_middle_long_diagonal()
        )
        self.middle_long_diag_spin.setSingleStep(1.0)
        self.middle_long_diag_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_long_diagonal", self.middle_long_diag_spin.value()
            )
        )
        self.value_labels["Middle Long Diagonal"] = self.middle_long_diag_spin
        middle_layout.addRow("Long Diagonal:", self.middle_long_diag_spin)

        # Inradius
        self.middle_inradius_spin = QDoubleSpinBox()
        self.middle_inradius_spin.setRange(0.1, 1e9)
        self.middle_inradius_spin.setValue(self.calculator.calculate_middle_inradius())
        self.middle_inradius_spin.setSingleStep(1.0)
        self.middle_inradius_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_inradius", self.middle_inradius_spin.value()
            )
        )
        self.value_labels["Middle Inradius"] = self.middle_inradius_spin
        middle_layout.addRow("Inradius:", self.middle_inradius_spin)

        # Circumradius
        self.middle_circumradius_spin = QDoubleSpinBox()
        self.middle_circumradius_spin.setRange(0.1, 1e9)
        self.middle_circumradius_spin.setValue(
            self.calculator.calculate_middle_circumradius()
        )
        self.middle_circumradius_spin.setSingleStep(1.0)
        self.middle_circumradius_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_circumradius", self.middle_circumradius_spin.value()
            )
        )
        self.value_labels["Middle Circumradius"] = self.middle_circumradius_spin
        middle_layout.addRow("Circumradius:", self.middle_circumradius_spin)

        # Incircle circumference
        self.middle_incircle_circ_spin = QDoubleSpinBox()
        self.middle_incircle_circ_spin.setRange(0.1, 1e9)
        self.middle_incircle_circ_spin.setValue(
            self.calculator.calculate_middle_incircle_circumference()
        )
        self.middle_incircle_circ_spin.setSingleStep(1.0)
        self.middle_incircle_circ_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_incircle_circ", self.middle_incircle_circ_spin.value()
            )
        )
        self.value_labels[
            "Middle Incircle Circumference"
        ] = self.middle_incircle_circ_spin
        middle_layout.addRow("Incircle Circumference:", self.middle_incircle_circ_spin)

        # Circumcircle circumference
        self.middle_circumcircle_circ_spin = QDoubleSpinBox()
        self.middle_circumcircle_circ_spin.setRange(0.1, 1e9)
        self.middle_circumcircle_circ_spin.setValue(
            self.calculator.calculate_middle_circumcircle_circumference()
        )
        self.middle_circumcircle_circ_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "middle_circumcircle_circ", self.middle_circumcircle_circ_spin.value()
            )
        )
        self.value_labels[
            "Middle Circumcircle Circumference"
        ] = self.middle_circumcircle_circ_spin
        middle_layout.addRow(
            "Circumcircle Circumference:", self.middle_circumcircle_circ_spin
        )

        # Inner heptagon properties group
        inner_group = QGroupBox("Inner Heptagon Properties")
        inner_layout = QFormLayout(inner_group)

        # Edge length
        self.inner_edge_spin = (
            QDoubleSpinBox()
        )  # This is for display in the calculator tab
        self.inner_edge_spin.setRange(0.01, 1e9)  # Adjusted range
        self.inner_edge_spin.setValue(self.calculator.calculate_inner_edge_length())
        self.inner_edge_spin.setSingleStep(1.0)
        self.inner_edge_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_edge", self.inner_edge_spin.value()
            )
        )
        self.value_labels["Inner Edge Length"] = self.inner_edge_spin
        inner_layout.addRow("Edge Length:", self.inner_edge_spin)

        # Perimeter
        self.inner_perimeter_spin = QDoubleSpinBox()
        self.inner_perimeter_spin.setRange(0.1, 1e9)
        self.inner_perimeter_spin.setValue(self.calculator.calculate_inner_perimeter())
        self.inner_perimeter_spin.setSingleStep(0.1)
        self.inner_perimeter_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_perimeter", self.inner_perimeter_spin.value()
            )
        )
        self.value_labels["Inner Perimeter"] = self.inner_perimeter_spin
        inner_layout.addRow("Perimeter:", self.inner_perimeter_spin)

        # Area
        self.inner_area_spin = QDoubleSpinBox()
        self.inner_area_spin.setRange(0.01, 1e9)
        self.inner_area_spin.setValue(self.calculator.calculate_inner_area())
        self.inner_area_spin.setSingleStep(0.1)
        self.inner_area_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_area", self.inner_area_spin.value()
            )
        )
        self.value_labels["Inner Area"] = self.inner_area_spin
        inner_layout.addRow("Area:", self.inner_area_spin)

        # Short diagonal
        self.inner_short_diag_spin = QDoubleSpinBox()
        self.inner_short_diag_spin.setRange(0.01, 1e9)
        self.inner_short_diag_spin.setValue(
            self.calculator.calculate_inner_short_diagonal()
        )
        self.inner_short_diag_spin.setSingleStep(0.1)
        self.inner_short_diag_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_short_diagonal", self.inner_short_diag_spin.value()
            )
        )
        self.value_labels["Inner Short Diagonal"] = self.inner_short_diag_spin
        inner_layout.addRow("Short Diagonal:", self.inner_short_diag_spin)

        # Long diagonal
        self.inner_long_diag_spin = QDoubleSpinBox()
        self.inner_long_diag_spin.setRange(0.01, 1e9)
        self.inner_long_diag_spin.setValue(
            self.calculator.calculate_inner_long_diagonal()
        )
        self.inner_long_diag_spin.setSingleStep(0.1)
        self.inner_long_diag_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_long_diagonal", self.inner_long_diag_spin.value()
            )
        )
        self.value_labels["Inner Long Diagonal"] = self.inner_long_diag_spin
        inner_layout.addRow("Long Diagonal:", self.inner_long_diag_spin)

        # Inradius
        self.inner_inradius_spin = QDoubleSpinBox()
        self.inner_inradius_spin.setRange(0.01, 1e9)
        self.inner_inradius_spin.setValue(self.calculator.calculate_inner_inradius())
        self.inner_inradius_spin.setSingleStep(0.1)
        self.inner_inradius_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_inradius", self.inner_inradius_spin.value()
            )
        )
        self.value_labels["Inner Inradius"] = self.inner_inradius_spin
        inner_layout.addRow("Inradius:", self.inner_inradius_spin)

        # Circumradius
        self.inner_circumradius_spin = QDoubleSpinBox()
        self.inner_circumradius_spin.setRange(0.01, 1e9)
        self.inner_circumradius_spin.setValue(
            self.calculator.calculate_inner_circumradius()
        )
        self.inner_circumradius_spin.setSingleStep(0.1)
        self.inner_circumradius_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_circumradius", self.inner_circumradius_spin.value()
            )
        )
        self.value_labels["Inner Circumradius"] = self.inner_circumradius_spin
        inner_layout.addRow("Circumradius:", self.inner_circumradius_spin)

        # Incircle circumference
        self.inner_incircle_circ_spin = QDoubleSpinBox()
        self.inner_incircle_circ_spin.setRange(0.01, 1e9)
        self.inner_incircle_circ_spin.setValue(
            self.calculator.calculate_inner_incircle_circumference()
        )
        self.inner_incircle_circ_spin.setSingleStep(0.1)
        self.inner_incircle_circ_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_incircle_circ", self.inner_incircle_circ_spin.value()
            )
        )
        self.value_labels[
            "Inner Incircle Circumference"
        ] = self.inner_incircle_circ_spin
        inner_layout.addRow("Incircle Circumference:", self.inner_incircle_circ_spin)

        # Circumcircle circumference
        self.inner_circumcircle_circ_spin = QDoubleSpinBox()
        self.inner_circumcircle_circ_spin.setRange(0.01, 1e9)
        self.inner_circumcircle_circ_spin.setValue(
            self.calculator.calculate_inner_circumcircle_circumference()
        )
        self.inner_circumcircle_circ_spin.editingFinished.connect(
            lambda: self._handle_input_change(
                "inner_circumcircle_circ", self.inner_circumcircle_circ_spin.value()
            )
        )
        self.value_labels[
            "Inner Circumcircle Circumference"
        ] = self.inner_circumcircle_circ_spin
        inner_layout.addRow(
            "Circumcircle Circumference:", self.inner_circumcircle_circ_spin
        )

        # Add all groups to the scroll layout
        scroll_layout.addWidget(outer_group)
        scroll_layout.addWidget(middle_group)
        scroll_layout.addWidget(inner_group)
        scroll_layout.addStretch()

        # Set up scroll area
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        calc_layout.addWidget(scroll_area)

        # Add tabs to right panel
        right_panel.addTab(viz_tab, "Visualization")
        right_panel.addTab(calc_tab, "Calculator")

        # Add panels to main layout
        main_layout.addWidget(scroll_area_main_controls, 1)  # Use renamed scroll area
        main_layout.addWidget(right_panel, 2)

        # Add context menu support to all value spinboxes and labels
        for field, widget in self.value_labels.items():
            widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            widget.customContextMenuRequested.connect(
                lambda pos, w=widget, f=field: self._show_context_menu(pos, w, f)
            )

    def _update_visualization(self) -> None:
        """Update the visualization based on checkbox states."""
        self.viz_widget.toggle_incircle(self.incircle_check.isChecked())
        self.viz_widget.toggle_circumcircle(self.circumcircle_check.isChecked())
        self.viz_widget.toggle_outer_heptagon(self.outer_heptagon_check.isChecked())
        self.viz_widget.toggle_middle_heptagon(self.middle_heptagon_check.isChecked())
        self.viz_widget.toggle_inner_heptagon(self.inner_heptagon_check.isChecked())
        self.viz_widget.toggle_diagonals(self.diagonals_check.isChecked())
        self.viz_widget.toggle_vertex_labels(self.vertex_labels_check.isChecked())
        self.viz_widget.toggle_measurements(self.measurements_check.isChecked())

    def _update_orientation(self) -> None:
        """Update the orientation of the polygons."""
        orientation = self.orientation_combo.currentData()
        self.calculator.set_orientation(orientation)
        # Ensure viz_widget is updated if it exists
        if hasattr(self, "viz_widget") and self.viz_widget:
            self.viz_widget.set_calculator(self.calculator)
            self.viz_widget.update()
        self._update_display()  # Also update display fields on orientation change

    def _handle_input_change(self, field_name: str, value: float) -> None:
        """
        Handles input changes from primary edge length fields and other editable calculator fields,
        updates the calculator, and refreshes the display.
        """
        print(
            f"Handling input change for: {field_name} with value: {value}"
        )  # Debug print

        # --- Primary Edge Length Inputs ---
        if field_name == "outer_edge":
            self.calculator.set_value_from_outer_edge(value)
        elif field_name == "middle_edge":
            self.calculator.set_middle_edge_length(value)
        elif field_name == "inner_edge":
            self.calculator.set_value_from_inner_edge(value)

        # --- Outer Heptagon Properties ---
        elif field_name == "outer_perimeter":
            self.calculator.set_value_from_outer_perimeter(value)
        elif field_name == "outer_area":
            self.calculator.set_value_from_outer_area(value)
        elif field_name == "outer_short_diagonal":
            self.calculator.set_value_from_outer_short_diagonal(value)
        elif field_name == "outer_long_diagonal":
            self.calculator.set_value_from_outer_long_diagonal(value)
        elif field_name == "outer_inradius":
            self.calculator.set_value_from_outer_inradius(value)
        elif field_name == "outer_circumradius":
            self.calculator.set_value_from_outer_circumradius(value)
        elif field_name == "outer_incircle_circ":
            self.calculator.set_value_from_outer_incircle_circumference(value)
        elif field_name == "outer_circumcircle_circ":
            self.calculator.set_value_from_outer_circumcircle_circumference(value)

        # --- Middle Heptagon Properties ---
        elif field_name == "middle_perimeter":
            self.calculator.set_value_from_middle_perimeter(value)
        elif field_name == "middle_area":
            self.calculator.set_value_from_middle_area(value)
        elif field_name == "middle_short_diagonal":
            self.calculator.set_value_from_middle_short_diagonal(value)
        elif field_name == "middle_long_diagonal":
            self.calculator.set_value_from_middle_long_diagonal(value)
        elif field_name == "middle_inradius":
            self.calculator.set_value_from_middle_inradius(value)
        elif field_name == "middle_circumradius":
            self.calculator.set_value_from_middle_circumradius(value)
        elif field_name == "middle_incircle_circ":
            self.calculator.set_value_from_middle_incircle_circumference(value)
        elif field_name == "middle_circumcircle_circ":
            self.calculator.set_value_from_middle_circumcircle_circumference(value)

        # --- Inner Heptagon Properties ---
        elif field_name == "inner_perimeter":
            self.calculator.set_value_from_inner_perimeter(value)
        elif field_name == "inner_area":
            self.calculator.set_value_from_inner_area(value)
        elif field_name == "inner_short_diagonal":
            self.calculator.set_value_from_inner_short_diagonal(value)
        elif field_name == "inner_long_diagonal":
            self.calculator.set_value_from_inner_long_diagonal(value)
        elif field_name == "inner_inradius":
            self.calculator.set_value_from_inner_inradius(value)
        elif field_name == "inner_circumradius":
            self.calculator.set_value_from_inner_circumradius(value)
        elif field_name == "inner_incircle_circ":
            self.calculator.set_value_from_inner_incircle_circumference(value)
        elif field_name == "inner_circumcircle_circ":
            self.calculator.set_value_from_inner_circumcircle_circumference(value)

        else:
            # This case should ideally not be reached if all fields are covered
            print(
                f"Warning: Field '{field_name}' was edited to {value}, but no specific handler is implemented in _handle_input_change. Display will refresh based on current calculator state."
            )

        self._update_display()
        if hasattr(self, "viz_widget") and self.viz_widget:
            self.viz_widget.set_calculator(self.calculator)
            self.viz_widget.update()

    def _update_display(self) -> None:
        """Update all displayed values from the calculator."""

        # Block signals for all input-capable spinboxes to prevent recursive updates
        spinboxes_to_block = [
            self.outer_edge_input_spin,
            self.middle_edge_input_spin,
            self.inner_edge_input_spin,  # Primary inputs
            self.outer_edge_spin,
            self.outer_perimeter_spin,
            self.outer_area_spin,  # Calculator tab displays
            self.outer_short_diag_spin,
            self.outer_long_diag_spin,
            self.outer_inradius_spin,
            self.outer_circumradius_spin,
            self.outer_incircle_circ_spin,
            self.outer_circumcircle_circ_spin,
            self.middle_edge_spin,
            self.middle_perimeter_spin,
            self.middle_area_spin,
            self.middle_short_diag_spin,
            self.middle_long_diag_spin,
            self.middle_inradius_spin,
            self.middle_circumradius_spin,
            self.middle_incircle_circ_spin,
            self.middle_circumcircle_circ_spin,
            self.inner_edge_spin,
            self.inner_perimeter_spin,
            self.inner_area_spin,
            self.inner_short_diag_spin,
            self.inner_long_diag_spin,
            self.inner_inradius_spin,
            self.inner_circumradius_spin,
            self.inner_incircle_circ_spin,
            self.inner_circumcircle_circ_spin,
        ]

        original_block_states = {
            spinbox: spinbox.signalsBlocked() for spinbox in spinboxes_to_block
        }
        for spinbox in spinboxes_to_block:
            spinbox.blockSignals(True)

        try:
            # Update "Heptagon Properties" input group (primary inputs)
            self.outer_edge_input_spin.setValue(
                self.calculator.calculate_outer_edge_length()
            )
            self.middle_edge_input_spin.setValue(
                self.calculator.calculate_middle_edge_length()
            )
            self.inner_edge_input_spin.setValue(
                self.calculator.calculate_inner_edge_length()
            )

            # Update "Calculator" tab - Outer Heptagon
            self.outer_edge_spin.setValue(self.calculator.calculate_outer_edge_length())
            self.outer_perimeter_spin.setValue(
                self.calculator.calculate_outer_perimeter()
            )
            self.outer_area_spin.setValue(self.calculator.calculate_outer_area())
            self.outer_short_diag_spin.setValue(
                self.calculator.calculate_outer_short_diagonal()
            )
            self.outer_long_diag_spin.setValue(
                self.calculator.calculate_outer_long_diagonal()
            )
            self.outer_inradius_spin.setValue(
                self.calculator.calculate_outer_inradius()
            )
            self.outer_circumradius_spin.setValue(
                self.calculator.calculate_outer_circumradius()
            )
            self.outer_incircle_circ_spin.setValue(
                self.calculator.calculate_outer_incircle_circumference()
            )
            self.outer_circumcircle_circ_spin.setValue(
                self.calculator.calculate_outer_circumcircle_circumference()
            )

            # Update "Calculator" tab - Middle Heptagon
            self.middle_edge_spin.setValue(
                self.calculator.calculate_middle_edge_length()
            )
            self.middle_perimeter_spin.setValue(
                self.calculator.calculate_middle_perimeter()
            )
            self.middle_area_spin.setValue(self.calculator.calculate_middle_area())
            self.middle_short_diag_spin.setValue(
                self.calculator.calculate_middle_short_diagonal()
            )
            self.middle_long_diag_spin.setValue(
                self.calculator.calculate_middle_long_diagonal()
            )
            self.middle_inradius_spin.setValue(
                self.calculator.calculate_middle_inradius()
            )
            self.middle_circumradius_spin.setValue(
                self.calculator.calculate_middle_circumradius()
            )
            self.middle_incircle_circ_spin.setValue(
                self.calculator.calculate_middle_incircle_circumference()
            )
            self.middle_circumcircle_circ_spin.setValue(
                self.calculator.calculate_middle_circumcircle_circumference()
            )

            # Update "Calculator" tab - Inner Heptagon
            self.inner_edge_spin.setValue(self.calculator.calculate_inner_edge_length())
            self.inner_perimeter_spin.setValue(
                self.calculator.calculate_inner_perimeter()
            )
            self.inner_area_spin.setValue(self.calculator.calculate_inner_area())
            self.inner_short_diag_spin.setValue(
                self.calculator.calculate_inner_short_diagonal()
            )
            self.inner_long_diag_spin.setValue(
                self.calculator.calculate_inner_long_diagonal()
            )
            self.inner_inradius_spin.setValue(
                self.calculator.calculate_inner_inradius()
            )
            self.inner_circumradius_spin.setValue(
                self.calculator.calculate_inner_circumradius()
            )
            self.inner_incircle_circ_spin.setValue(
                self.calculator.calculate_inner_incircle_circumference()
            )
            self.inner_circumcircle_circ_spin.setValue(
                self.calculator.calculate_inner_circumcircle_circumference()
            )
        finally:
            # Restore original signal blocking states
            for spinbox, was_blocked in original_block_states.items():
                spinbox.blockSignals(was_blocked)

    def _show_context_menu(self, pos, widget, field_name):
        """Show a context menu for a value widget."""
        menu = QMenu(self)
        value = self._get_widget_value(widget)
        if value is None:
            return
        rounded_value = round(value)
        if TQ_AVAILABLE:
            tq_action = QAction(
                f"Send {field_name} value ({rounded_value}) to Quadset Analysis", self
            )
            tq_action.triggered.connect(
                lambda: self._send_to_quadset_analysis(rounded_value)
            )
            menu.addAction(tq_action)
        menu.exec(widget.mapToGlobal(pos))

    def _get_widget_value(self, widget):
        """Get the numeric value from a widget."""
        try:
            if isinstance(widget, QDoubleSpinBox) or isinstance(widget, QSpinBox):
                return widget.value()
            elif isinstance(widget, QLabel):
                text = widget.text()
                numeric_text = "".join(c for c in text if c.isdigit() or c == ".")
                if numeric_text:
                    return float(numeric_text)
            return None
        except (ValueError, TypeError):
            return None

    def _send_to_quadset_analysis(self, value):
        """Send a value to the TQ Quadset Analysis tool."""
        if not TQ_AVAILABLE:
            QMessageBox.warning(
                self,
                "Feature Unavailable",
                "The TQ module is not available in this installation.",
            )
            return
        try:
            analysis_service = tq_analysis_service.get_instance()
            panel = analysis_service.open_quadset_analysis(value)
            parent = panel.window()
            if parent and hasattr(parent, "ensure_on_top"):
                parent.ensure_on_top()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while opening Quadset Analysis: {str(e)}",
            )

    def _get_field_value(self, field_name: str) -> float:
        """Get the value for a specific field.

        This method is used by the polygon service to retrieve values.

        Args:
            field_name: Name of the field

        Returns:
            Value of the field
        """
        if field_name == "Outer Edge Length":
            # return self.calculator.outer_edge_length # Old direct attribute access
            return self.calculator.calculate_outer_edge_length()
        elif field_name == "Outer Perimeter":
            return self.calculator.calculate_outer_perimeter()
        elif field_name == "Outer Area":
            return self.calculator.calculate_outer_area()
        elif field_name == "Outer Short Diagonal":
            return self.calculator.calculate_outer_short_diagonal()
        elif field_name == "Outer Long Diagonal":
            return self.calculator.calculate_outer_long_diagonal()
        elif field_name == "Outer Inradius":
            return self.calculator.calculate_outer_inradius()
        elif field_name == "Outer Circumradius":
            return self.calculator.calculate_outer_circumradius()
        elif field_name == "Middle Edge Length":
            return self.calculator.calculate_middle_edge_length()
        elif field_name == "Middle Perimeter":
            return self.calculator.calculate_middle_perimeter()
        elif field_name == "Middle Area":
            return self.calculator.calculate_middle_area()
        elif field_name == "Middle Short Diagonal":
            return self.calculator.calculate_middle_short_diagonal()
        elif field_name == "Middle Long Diagonal":
            return self.calculator.calculate_middle_long_diagonal()
        elif field_name == "Middle Inradius":
            return self.calculator.calculate_middle_inradius()
        elif field_name == "Middle Circumradius":
            return self.calculator.calculate_middle_circumradius()
        elif field_name == "Inner Edge Length":
            return self.calculator.calculate_inner_edge_length()
        elif field_name == "Inner Perimeter":
            return self.calculator.calculate_inner_perimeter()
        elif field_name == "Inner Area":
            return self.calculator.calculate_inner_area()
        elif field_name == "Inner Short Diagonal":
            return self.calculator.calculate_inner_short_diagonal()
        elif field_name == "Inner Long Diagonal":
            return self.calculator.calculate_inner_long_diagonal()
        elif field_name == "Inner Inradius":
            return self.calculator.calculate_inner_inradius()
        elif field_name == "Inner Circumradius":
            return self.calculator.calculate_inner_circumradius()

        return 0.0
