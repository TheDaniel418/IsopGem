"""
Purpose: Provides visualization tools for exploring the planar expansion of ternary numbers

This file is part of the tq pillar and serves as a UI component.
It is responsible for visualizing how ternary numbers expand across dimensional planes,
helping users understand the geometric interpretations of ternary digits within the TQ system.

Key components:
- PlanarExpansionVisualizer: Widget to display the planar expansion visually
- PlanarExpansionPanel: Container panel with controls for the visualizer

Dependencies:
- tq.utils.ternary_converter: For converting between decimal and ternary representations
- tq.utils.ternary_transition: For applying transformations to ternary patterns
- PyQt6: For UI components and visualization rendering

Related files:
- tq/ui/tq_tab.py: Main tab that launches this visualization
- tq/utils/ternary_converter.py: Utilities for working with ternary numbers
- tq/ui/widgets/ternary_visualizer.py: Another visualization tool for the TQ system
"""

from typing import List, Dict, Tuple, Optional
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QScrollArea, QSizePolicy, QFrame, QComboBox,
    QSlider, QGridLayout, QSpinBox, QColorDialog, QTabWidget
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QPixmap, QFont, 
    QPainterPath, QLinearGradient, QRadialGradient
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QSize, pyqtSignal

from tq.utils.ternary_converter import (
    decimal_to_ternary, ternary_to_decimal, 
    split_ternary_digits, get_ternary_digit_positions
)
from tq.utils.ternary_transition import TernaryTransition


class PlanarExpansionVisualizer(QWidget):
    """
    Widget that visualizes the planar expansion of ternary numbers.
    
    This visualizer shows how ternary digits map to different dimensional planes,
    revealing the geometric structure inherent in the TQ system.
    """
    
    def __init__(self, parent=None):
        """Initialize the planar expansion visualizer."""
        super().__init__(parent)
        
        # Configuration
        self.ternary_value = "0"
        self.dimension = 3  # 3D cube by default
        self.cell_size = 40
        self.margin = 20
        self.animation_step = 0
        self.show_labels = True
        self.show_tao_lines = True
        self.show_grid = True
        
        # Visual styling
        self.background_color = QColor(240, 240, 255)
        self.grid_color = QColor(200, 200, 220)
        self.vertex_colors = [
            QColor(0, 150, 0),    # Tao/0: Green
            QColor(200, 0, 0),    # Yang/1: Red
            QColor(0, 0, 200)     # Yin/2: Blue
        ]
        
        # Set size policy
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.setMinimumSize(400, 400)
        
        # Initialize the cached grid positions
        self._grid_positions = {}
        self._update_grid_positions()
    
    def set_ternary(self, value: str) -> None:
        """
        Set the ternary number to visualize.
        
        Args:
            value: A valid ternary string
        """
        if not all(digit in '012' for digit in value):
            raise ValueError(f"Invalid ternary string: {value}")
        
        self.ternary_value = value
        self.update()
    
    def set_dimension(self, dimension: int) -> None:
        """
        Set the dimension for visualization (2D, 3D, etc).
        
        Args:
            dimension: The dimension (2 for square, 3 for cube, etc.)
        """
        if dimension < 2 or dimension > 6:
            raise ValueError(f"Dimension must be between 2 and 6, got {dimension}")
        
        self.dimension = dimension
        self._update_grid_positions()
        self.update()
    
    def toggle_labels(self, show: bool) -> None:
        """
        Toggle the display of position labels.
        
        Args:
            show: Whether to show labels
        """
        self.show_labels = show
        self.update()
    
    def toggle_tao_lines(self, show: bool) -> None:
        """
        Toggle the display of Tao lines (connections between positions).
        
        Args:
            show: Whether to show Tao lines
        """
        self.show_tao_lines = show
        self.update()
    
    def toggle_grid(self, show: bool) -> None:
        """
        Toggle the display of the background grid.
        
        Args:
            show: Whether to show the grid
        """
        self.show_grid = show
        self.update()
    
    def _update_grid_positions(self) -> None:
        """
        Update the cached grid positions based on the current dimension.
        """
        # Clear the existing positions
        self._grid_positions = {}
        
        # Generate positions for each cell in the grid
        if self.dimension == 2:
            # 2D grid (square)
            for i in range(3):
                for j in range(3):
                    # Position key is the ternary representation
                    pos_key = f"{i}{j}"
                    decimal_value = ternary_to_decimal(pos_key)
                    
                    # Calculate grid coordinates
                    x = self.margin + j * self.cell_size * 1.5
                    y = self.margin + i * self.cell_size * 1.5
                    
                    self._grid_positions[decimal_value] = (x, y)
        
        elif self.dimension == 3:
            # 3D grid (cube)
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        # Position key is the ternary representation
                        pos_key = f"{i}{j}{k}"
                        decimal_value = ternary_to_decimal(pos_key)
                        
                        # Calculate isometric projection coordinates
                        # This creates a simple 3D cube projection
                        x = self.margin + (j - i) * self.cell_size
                        y = self.margin + (i + j) * self.cell_size * 0.5 + (2 - k) * self.cell_size * 0.8
                        
                        self._grid_positions[decimal_value] = (x, y)
        
        else:
            # Higher dimensions - use a dimensional mapping approach
            # For dimensions > 3, we'll use a recursive subdivision approach
            # This creates a fractal-like representation of higher dimensions
            self._generate_higher_dimension_grid(self.dimension)
    
    def _generate_higher_dimension_grid(self, dimension: int) -> None:
        """
        Generate grid positions for higher dimensions using recursive subdivision.
        
        Args:
            dimension: The dimension to generate (4+)
        """
        # Base case position and size
        base_x = self.width() / 2
        base_y = self.height() / 2
        base_size = min(self.width(), self.height()) - 2 * self.margin
        
        # Generate all ternary numbers of length=dimension
        self._recursive_generate_positions(dimension, "", base_x, base_y, base_size)
    
    def _recursive_generate_positions(self, remaining_dims: int, prefix: str, 
                                     center_x: float, center_y: float, size: float) -> None:
        """
        Recursively generate positions for higher dimensions.
        
        Args:
            remaining_dims: Number of dimensions left to process
            prefix: Current ternary digit prefix
            center_x: X-coordinate of the current subdivision center
            center_y: Y-coordinate of the current subdivision center
            size: Size of the current subdivision
        """
        if remaining_dims == 0:
            # Base case: store the position
            decimal_value = ternary_to_decimal(prefix)
            self._grid_positions[decimal_value] = (center_x, center_y)
            return
        
        # Recursive case: subdivide the space into 3x3 grid
        new_size = size / 3
        offsets = [-new_size, 0, new_size]
        
        for i, x_offset in enumerate(offsets):
            for j, y_offset in enumerate(offsets):
                new_digit = str((i + j) % 3)  # Simple mapping of position to ternary digit
                new_prefix = prefix + new_digit
                
                new_x = center_x + x_offset
                new_y = center_y + y_offset
                
                self._recursive_generate_positions(
                    remaining_dims - 1, new_prefix, new_x, new_y, new_size
                )
    
    def paintEvent(self, event):
        """
        Paint the planar expansion visualization.
        
        Args:
            event: The paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), self.background_color)
        
        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(painter)
        
        # Draw connections (Tao lines) if enabled
        if self.show_tao_lines:
            self._draw_tao_lines(painter)
        
        # Draw vertices
        self._draw_vertices(painter)
        
        # Draw labels if enabled
        if self.show_labels:
            self._draw_labels(painter)
        
        # Draw the current ternary number highlight
        self._highlight_current_ternary(painter)
    
    def _draw_grid(self, painter: QPainter) -> None:
        """
        Draw the dimensional grid.
        
        Args:
            painter: The QPainter to use
        """
        painter.setPen(QPen(self.grid_color, 0.5))
        
        # For 2D or 3D, draw explicit grid lines
        if self.dimension <= 3:
            if self.dimension == 2:
                # Draw 2D grid
                for i in range(4):
                    # Horizontal lines
                    y = self.margin + i * self.cell_size * 1.5
                    painter.drawLine(
                        QPointF(self.margin, y), 
                        QPointF(self.margin + 3 * self.cell_size * 1.5, y)
                    )
                    
                    # Vertical lines
                    x = self.margin + i * self.cell_size * 1.5
                    painter.drawLine(
                        QPointF(x, self.margin), 
                        QPointF(x, self.margin + 3 * self.cell_size * 1.5)
                    )
            
            elif self.dimension == 3:
                # Draw 3D grid (simplified)
                for key, (x, y) in self._grid_positions.items():
                    # Draw a small grid point
                    painter.drawEllipse(QPointF(x, y), 1, 1)
        
        else:
            # For higher dimensions, draw connecting lines between nearby points
            # This creates a network visualization of the dimensional structure
            for key1, (x1, y1) in self._grid_positions.items():
                ternary1 = decimal_to_ternary(key1).zfill(self.dimension)
                
                for key2, (x2, y2) in self._grid_positions.items():
                    ternary2 = decimal_to_ternary(key2).zfill(self.dimension)
                    
                    # Check if they differ by only one digit
                    diff_count = sum(a != b for a, b in zip(ternary1, ternary2))
                    if diff_count == 1:
                        # Draw a connecting line
                        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    
    def _draw_tao_lines(self, painter: QPainter) -> None:
        """
        Draw the Tao lines connecting vertices with the same Tao count.
        
        Args:
            painter: The QPainter to use
        """
        # Group vertices by Tao count (number of 0s in their ternary representation)
        tao_groups = {}
        
        for key in self._grid_positions:
            ternary = decimal_to_ternary(key).zfill(self.dimension)
            tao_count = ternary.count('0')
            
            if tao_count not in tao_groups:
                tao_groups[tao_count] = []
            
            tao_groups[tao_count].append(key)
        
        # Draw connections between vertices in the same Tao group
        for tao_count, vertices in tao_groups.items():
            # Skip empty groups
            if not vertices:
                continue
            
            # Choose color based on Tao count
            alpha = 100  # Semitransparent
            
            # Use different colors for different Tao counts
            if tao_count == 0:  # No Tao lines (vertices)
                color = QColor(200, 0, 0, alpha)  # Red
            elif tao_count == self.dimension:  # All Tao lines (center)
                color = QColor(0, 150, 0, alpha)  # Green
            else:
                # Interpolate between blue and purple for intermediate values
                blue_component = 255 - (tao_count * 40)
                red_component = min(tao_count * 40, 150)
                color = QColor(red_component, 0, blue_component, alpha)
            
            painter.setPen(QPen(color, 2, Qt.PenStyle.DashLine))
            
            # Draw lines connecting all vertices in this Tao group
            for i in range(len(vertices)):
                for j in range(i + 1, len(vertices)):
                    v1, v2 = vertices[i], vertices[j]
                    x1, y1 = self._grid_positions[v1]
                    x2, y2 = self._grid_positions[v2]
                    
                    # Use QPointF objects instead of raw float coordinates
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    
    def _draw_vertices(self, painter: QPainter) -> None:
        """
        Draw the vertices of the dimensional structure.
        
        Args:
            painter: The QPainter to use
        """
        for key, (x, y) in self._grid_positions.items():
            ternary = decimal_to_ternary(key).zfill(self.dimension)
            tao_count = ternary.count('0')
            
            # Determine vertex size and color based on Tao count
            radius = self.cell_size * 0.25
            
            # Adjust size based on Tao count
            if tao_count == 0:  # Vertices (no Tao lines)
                radius *= 1.3
            elif tao_count == self.dimension:  # Center (all Tao lines)
                radius *= 1.5
            else:
                # Size increases with Tao count
                radius *= (1 + 0.1 * tao_count)
            
            # Color based on Tao count
            if tao_count == 0:  # Vertices
                color = self.vertex_colors[1]  # Yang/1: Red
            elif tao_count == self.dimension:  # Center
                color = self.vertex_colors[0]  # Tao/0: Green
            else:
                # Edges and faces use a blend of colors
                color = QColor(
                    0,
                    0,
                    180 + min(tao_count * 15, 75)  # More blue for higher Tao count
                )
            
            # Draw the vertex
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawEllipse(QPointF(x, y), radius, radius)
    
    def _draw_labels(self, painter: QPainter) -> None:
        """
        Draw labels for each position in the grid.
        
        Args:
            painter: The QPainter to use
        """
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.setFont(QFont("Arial", 8))
        
        for key, (x, y) in self._grid_positions.items():
            ternary = decimal_to_ternary(key).zfill(self.dimension)
            tao_count = ternary.count('0')
            
            # Create label text
            label = f"{key} ({ternary})"
            
            # Position the label
            text_rect = QRectF(
                x - self.cell_size * 0.4,
                y + self.cell_size * 0.3,
                self.cell_size * 0.8,
                self.cell_size * 0.3
            )
            
            # Draw with a white background for readability
            painter.fillRect(text_rect, QColor(255, 255, 255, 180))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, label)
    
    def _highlight_current_ternary(self, painter: QPainter) -> None:
        """
        Highlight the position corresponding to the current ternary value.
        
        Args:
            painter: The QPainter to use
        """
        try:
            decimal_value = ternary_to_decimal(self.ternary_value)
            
            # Skip if the value is not in our grid
            if decimal_value not in self._grid_positions:
                return
            
            x, y = self._grid_positions[decimal_value]
            
            # Draw a highlight circle
            highlight_radius = self.cell_size * 0.4
            
            # Create a glow effect
            gradient = QRadialGradient(x, y, highlight_radius * 1.5)
            gradient.setColorAt(0, QColor(255, 255, 0, 150))
            gradient.setColorAt(1, QColor(255, 255, 0, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), highlight_radius * 1.5, highlight_radius * 1.5)
            
            # Draw a golden ring around the vertex
            painter.setPen(QPen(QColor(255, 215, 0), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(x, y), highlight_radius, highlight_radius)
        
        except (ValueError, KeyError):
            # Invalid ternary value or not in our grid
            pass
    
    def resizeEvent(self, event):
        """
        Handle the resize event to update grid positions.
        
        Args:
            event: The resize event
        """
        super().resizeEvent(event)
        self._update_grid_positions()


class PlanarExpansionPanel(QFrame):
    """
    Panel container for the planar expansion visualizer with controls.
    """
    
    def __init__(self, parent=None):
        """Initialize the planar expansion panel."""
        super().__init__(parent)
        
        # Set up the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Create title
        title_label = QLabel("Planar Expansion Visualizer")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Create description
        description = QLabel(
            "This visualizer shows how ternary digits expand across dimensional planes in the "
            "TQ system, with the number of Tao lines (0s) determining geometric roles."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description)
        
        # Create input controls
        controls_layout = QHBoxLayout()
        
        # Ternary input
        self.ternary_input = QLineEdit()
        self.ternary_input.setPlaceholderText("Enter ternary number (e.g. 120)")
        self.ternary_input.setText("0")
        self.ternary_input.textChanged.connect(self._validate_input)
        
        # Display button
        self.display_button = QPushButton("Visualize")
        self.display_button.clicked.connect(self._update_visualization)
        
        controls_layout.addWidget(QLabel("Ternary:"))
        controls_layout.addWidget(self.ternary_input)
        controls_layout.addWidget(self.display_button)
        
        main_layout.addLayout(controls_layout)
        
        # Dimension selector
        dimension_layout = QHBoxLayout()
        
        dimension_layout.addWidget(QLabel("Dimension:"))
        
        self.dimension_selector = QComboBox()
        for dim in range(2, 7):
            self.dimension_selector.addItem(f"{dim}D", dim)
        self.dimension_selector.setCurrentIndex(1)  # Default to 3D
        self.dimension_selector.currentIndexChanged.connect(self._change_dimension)
        
        dimension_layout.addWidget(self.dimension_selector)
        main_layout.addLayout(dimension_layout)
        
        # Display options
        options_layout = QHBoxLayout()
        
        # Checkboxes for display options
        self.show_labels_checkbox = QPushButton("Show Labels")
        self.show_labels_checkbox.setCheckable(True)
        self.show_labels_checkbox.setChecked(True)
        self.show_labels_checkbox.clicked.connect(self._toggle_labels)
        
        self.show_tao_lines_checkbox = QPushButton("Show Tao Lines")
        self.show_tao_lines_checkbox.setCheckable(True)
        self.show_tao_lines_checkbox.setChecked(True)
        self.show_tao_lines_checkbox.clicked.connect(self._toggle_tao_lines)
        
        self.show_grid_checkbox = QPushButton("Show Grid")
        self.show_grid_checkbox.setCheckable(True)
        self.show_grid_checkbox.setChecked(True)
        self.show_grid_checkbox.clicked.connect(self._toggle_grid)
        
        options_layout.addWidget(self.show_labels_checkbox)
        options_layout.addWidget(self.show_tao_lines_checkbox)
        options_layout.addWidget(self.show_grid_checkbox)
        
        main_layout.addLayout(options_layout)
        
        # Create visualizer in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Create the visualizer widget
        self.visualizer = PlanarExpansionVisualizer()
        scroll_area.setWidget(self.visualizer)
        
        main_layout.addWidget(scroll_area, 1)  # Give it a stretch factor of 1
        
        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 5px; }")
    
    def _validate_input(self) -> None:
        """Validate the ternary input and update UI accordingly."""
        text = self.ternary_input.text()
        valid = all(digit in '012' for digit in text) if text else True
        
        if valid:
            self.ternary_input.setStyleSheet("")
            self.display_button.setEnabled(True)
        else:
            self.ternary_input.setStyleSheet("background-color: #ffdddd;")
            self.display_button.setEnabled(False)
    
    def _update_visualization(self) -> None:
        """Update the visualizer with the current input value."""
        text = self.ternary_input.text()
        if text and all(digit in '012' for digit in text):
            self.visualizer.set_ternary(text)
    
    def _change_dimension(self) -> None:
        """Change the visualizer dimension."""
        dimension = self.dimension_selector.currentData()
        self.visualizer.set_dimension(dimension)
    
    def _toggle_labels(self) -> None:
        """Toggle the display of labels."""
        show = self.show_labels_checkbox.isChecked()
        self.visualizer.toggle_labels(show)
    
    def _toggle_tao_lines(self) -> None:
        """Toggle the display of Tao lines."""
        show = self.show_tao_lines_checkbox.isChecked()
        self.visualizer.toggle_tao_lines(show)
    
    def _toggle_grid(self) -> None:
        """Toggle the display of the grid."""
        show = self.show_grid_checkbox.isChecked()
        self.visualizer.toggle_grid(show)


# Testing code
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    panel = PlanarExpansionPanel()
    panel.resize(800, 600)
    panel.show()
    sys.exit(app.exec()) 