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
    QPainterPath, QLinearGradient, QRadialGradient, QTransform
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QSize, pyqtSignal, QTimer

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
        self.cell_size = 80  # Increased from 60 to 80
        self.margin = 50    # Increased for better spacing
        self.animation_step = 0
        self.show_labels = True
        self.show_tao_lines = True
        self.show_grid = True
        
        # Zoom and pan parameters
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.panning = False
        self.last_mouse_pos = None
        self.min_zoom = 0.2
        self.max_zoom = 5.0
        
        # Visual styling
        self.background_color = QColor(240, 240, 255)
        self.grid_color = QColor(200, 200, 220)
        self.vertex_colors = [
            QColor(0, 150, 0),    # Tao/0: Green
            QColor(200, 0, 0),    # Yang/1: Red
            QColor(0, 0, 200)     # Yin/2: Blue
        ]
        
        # Label styling
        self.label_bg_color = QColor(255, 255, 255, 230)  # More opaque background
        self.label_border_color = QColor(80, 80, 80, 200) # Darker border
        self.label_offset_y = 0.35  # Distance below the vertex
        
        # Set size policy
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.setMinimumSize(600, 600)  # Larger minimum size
        
        # Initialize the cached grid positions
        self._grid_positions = {}
        self._grid_colors = {}    # Cache for vertex colors
        self._grid_radii = {}     # Cache for vertex radii
        
        # Timer for smooth transitions
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._animate_transition)
        self._animation_timer.setInterval(30)  # 30ms for smooth animation
        
        self._transitioning = False
        self._old_positions = {}
        self._transition_progress = 0.0
        
        # Enable mouse tracking for pan operations
        self.setMouseTracking(True)
        
        # Enable focus to capture key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Initialize the grid
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
        
        if dimension == self.dimension:
            return  # No change needed
        
        # Save old positions for animation
        self._old_positions = self._grid_positions.copy()
        self._transitioning = True
        self._transition_progress = 0.0
        
        # Update dimension
        self.dimension = dimension
        
        # Update grid positions
        self._update_grid_positions()
        
        # Start animation
        if not self._animation_timer.isActive():
            self._animation_timer.start()
        
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
    
    def _animate_transition(self):
        """Animate the transition between dimensions."""
        if not self._transitioning:
            self._animation_timer.stop()
            return
        
        # Update transition progress
        self._transition_progress += 0.05
        if self._transition_progress >= 1.0:
            self._transition_progress = 1.0
            self._transitioning = False
            self._animation_timer.stop()
        
        self.update()  # Trigger repaint
    
    def _update_grid_positions(self) -> None:
        """
        Update the cached grid positions based on the current dimension.
        """
        # Store old positions if transitioning
        old_positions = self._grid_positions.copy() if self._transitioning else {}
        
        # Clear the existing positions
        self._grid_positions = {}
        self._grid_colors = {}
        self._grid_radii = {}
        
        # Get available space
        width = self.width()
        height = self.height()
        
        # Skip if the widget doesn't have a valid size yet
        if width <= 1 or height <= 1:
            return
        
        # Adjust cell size based on available space and dimension
        cell_size_multiplier = {
            2: 1.0,  # 2D needs less space
            3: 0.9,  # 3D needs moderate space
            4: 0.8,  # 4D+ need progressively more space
            5: 0.7,
            6: 0.5
        }
        
        available_size = min(width, height) - 2 * self.margin
        base_cell_size = available_size / (3.5 + self.dimension * 0.5)
        self.cell_size = max(50, base_cell_size * cell_size_multiplier.get(self.dimension, 0.5))
        
        # Calculate center points for proper centering
        center_x = width / 2
        center_y = height / 2
        
        # Generate positions based on dimension
        if self.dimension == 2:
            self._generate_2d_grid(center_x, center_y)
        elif self.dimension == 3:
            self._generate_3d_grid(center_x, center_y)
        else:
            self._generate_higher_dimension_grid(self.dimension, center_x, center_y)
        
        # Generate colors and sizes for vertices
        self._generate_vertex_properties()
    
    def _generate_2d_grid(self, center_x: float, center_y: float) -> None:
        """Generate grid positions for 2D visualization (square)."""
        # Calculate grid size
        spacing = self.cell_size * 2.0
        grid_width = 2 * spacing
        grid_height = 2 * spacing
        
        # Calculate the top-left corner to center the grid
        start_x = center_x - grid_width / 2
        start_y = center_y - grid_height / 2
        
        for i in range(3):
            for j in range(3):
                # Position key is the ternary representation
                pos_key = f"{i}{j}"
                decimal_value = ternary_to_decimal(pos_key)
                
                # Calculate grid coordinates with better spacing
                x = start_x + j * spacing
                y = start_y + i * spacing
                
                self._grid_positions[decimal_value] = (x, y)
    
    def _generate_3d_grid(self, center_x: float, center_y: float) -> None:
        """Generate grid positions for 3D visualization (cube)."""
        # Calculate isometric projection parameters
        # Use these to control the cube's appearance
        horizontal_spacing = self.cell_size * 1.5
        vertical_spacing = self.cell_size * 0.9
        depth_spacing = self.cell_size * 0.7
        
        # Calculate the center of the cube in widget coordinates
        start_x = center_x
        start_y = center_y - vertical_spacing  # Shift up slightly
        
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    # Position key is the ternary representation
                    pos_key = f"{i}{j}{k}"
                    decimal_value = ternary_to_decimal(pos_key)
                    
                    # Calculate isometric projection coordinates with better spacing
                    # This creates a more spread out and visually clear 3D cube
                    x = start_x + (j - i) * horizontal_spacing
                    y = start_y + (i + j) * vertical_spacing - k * depth_spacing
                    
                    self._grid_positions[decimal_value] = (x, y)
    
    def _generate_higher_dimension_grid(self, dimension: int, center_x: float, center_y: float) -> None:
        """
        Generate grid positions for dimensions 4 and above using a specialized layout.
        """
        # For higher dimensions, we'll use a circular layout with layers
        # Each layer represents a different Tao count (number of zeros)
        
        # First, group positions by Tao count
        tao_groups = {}
        max_positions = 3 ** dimension
        
        for decimal_value in range(max_positions):
            ternary = decimal_to_ternary(decimal_value).zfill(dimension)
            tao_count = ternary.count('0')
            
            if tao_count not in tao_groups:
                tao_groups[tao_count] = []
            
            tao_groups[tao_count].append(decimal_value)
        
        # Calculate radius of the main circle
        main_radius = min(self.width(), self.height()) * 0.4
        
        # Position each Tao group in a circle, with different radius per group
        for tao_count, positions in tao_groups.items():
            # Calculate this group's circle radius
            # Largest radius for vertices (0 Tao), smallest for center (all Tao)
            group_radius_ratio = 1.0 - (tao_count / dimension)
            group_radius = main_radius * (0.2 + 0.8 * group_radius_ratio)
            
            # Distribute positions evenly around a circle
            position_count = len(positions)
            for i, decimal_value in enumerate(positions):
                if position_count > 1:
                    # Multiple positions - distribute around circle
                    angle = 2 * math.pi * i / position_count
                    x = center_x + group_radius * math.cos(angle)
                    y = center_y + group_radius * math.sin(angle)
                else:
                    # Single position (likely the center) - place at center
                    x, y = center_x, center_y
                
                self._grid_positions[decimal_value] = (x, y)
    
    def _generate_vertex_properties(self) -> None:
        """Generate colors and sizes for vertices based on their Tao count."""
        for decimal_value in self._grid_positions:
            ternary = decimal_to_ternary(decimal_value).zfill(self.dimension)
            tao_count = ternary.count('0')
            
            # Determine radius based on Tao count and dimension
            base_radius = self.cell_size * 0.25
            
            # Vertices (0 Tao) are larger
            if tao_count == 0:
                radius = base_radius * 1.5
                color = self.vertex_colors[1]  # Yang/Red
            # Center (all Tao) is largest
            elif tao_count == self.dimension:
                radius = base_radius * 2.0
                color = self.vertex_colors[0]  # Tao/Green
            # Edges, faces, etc. are in between
            else:
                # Size and color based on Tao count relative to dimension
                tao_ratio = tao_count / self.dimension
                radius = base_radius * (1.0 + tao_ratio * 1.0)
                
                # Blend between colors
                red = int(max(0, (1 - tao_ratio) * 200))
                green = int(max(0, tao_ratio * 150))
                blue = int(max(0, 100 + tao_ratio * 100))
                color = QColor(red, green, blue)
            
            self._grid_radii[decimal_value] = radius
            self._grid_colors[decimal_value] = color
    
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
        
        # Apply zoom and pan transformation
        painter.save()
        painter.translate(self.pan_offset_x, self.pan_offset_y)
        painter.scale(self.zoom_factor, self.zoom_factor)
        
        # If transitioning, interpolate positions
        positions = self._get_interpolated_positions() if self._transitioning else self._grid_positions
        
        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(painter, positions)
        
        # Draw connections (Tao lines) if enabled
        if self.show_tao_lines:
            self._draw_tao_lines(painter, positions)
        
        # Draw vertices
        self._draw_vertices(painter, positions)
        
        # Draw labels if enabled
        if self.show_labels:
            self._draw_labels(painter, positions)
        
        # Draw the current ternary number highlight
        self._highlight_current_ternary(painter, positions)
        
        # Restore original transform
        painter.restore()
        
        # Draw zoom level indicator
        zoom_text = f"Zoom: {self.zoom_factor:.1f}x"
        painter.setPen(Qt.GlobalColor.darkGray)
        painter.drawText(10, 20, zoom_text)
    
    def _get_interpolated_positions(self) -> Dict[int, Tuple[float, float]]:
        """Get interpolated positions during a dimension transition."""
        positions = {}
        
        # For each position, interpolate between old and new
        for decimal_value, (new_x, new_y) in self._grid_positions.items():
            # If this position exists in old positions, interpolate
            if decimal_value in self._old_positions:
                old_x, old_y = self._old_positions[decimal_value]
                
                # Linear interpolation
                x = old_x + (new_x - old_x) * self._transition_progress
                y = old_y + (new_y - old_y) * self._transition_progress
                
                positions[decimal_value] = (x, y)
            else:
                # New position that didn't exist before, just use the new position
                positions[decimal_value] = (new_x, new_y)
        
        return positions
    
    def _draw_grid(self, painter: QPainter, positions: Dict[int, Tuple[float, float]]) -> None:
        """
        Draw the dimensional grid.
        
        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        painter.setPen(QPen(self.grid_color, 1.0))
        
        # For 2D or 3D, draw dimension-specific grid lines
        if self.dimension <= 3:
            self._draw_dimension_specific_grid(painter)
        
        # For all dimensions, draw connecting lines between nearby points
        # This creates a network visualization of the dimensional structure
        for key1, (x1, y1) in positions.items():
            ternary1 = decimal_to_ternary(key1).zfill(self.dimension)
            
            for key2, (x2, y2) in positions.items():
                if key1 >= key2:  # Skip already processed pairs
                    continue
                    
                ternary2 = decimal_to_ternary(key2).zfill(self.dimension)
                
                # Check if they differ by exactly one digit
                diff_count = sum(a != b for a, b in zip(ternary1, ternary2))
                
                if diff_count == 1:
                    # Determine line thickness based on the positions' Tao counts
                    tao_count1 = ternary1.count('0')
                    tao_count2 = ternary2.count('0')
                    avg_tao = (tao_count1 + tao_count2) / 2
                    
                    # Thinner lines for higher dimensions
                    thickness = max(0.5, 1.0 - avg_tao / self.dimension)
                    
                    # Draw connecting grid line
                    painter.setPen(QPen(self.grid_color, thickness))
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    
    def _draw_dimension_specific_grid(self, painter: QPainter) -> None:
        """Draw grid lines specific to 2D/3D visualizations."""
        if self.dimension == 2:
            # Get grid bounds from positions
            min_x = min(x for x, _ in self._grid_positions.values())
            max_x = max(x for x, _ in self._grid_positions.values())
            min_y = min(y for _, y in self._grid_positions.values())
            max_y = max(y for _, y in self._grid_positions.values())
            
            # Draw 2D grid lines
            painter.setPen(QPen(self.grid_color, 0.5))
            
            # Horizontal and vertical lines through each position
            for i in range(3):
                x_positions = [pos[0] for key, pos in self._grid_positions.items() 
                            if decimal_to_ternary(key).zfill(2)[1] == str(i)]
                y_positions = [pos[1] for key, pos in self._grid_positions.items() 
                            if decimal_to_ternary(key).zfill(2)[0] == str(i)]
                
                if x_positions:
                    avg_x = sum(x_positions) / len(x_positions)
                    painter.drawLine(QPointF(avg_x, min_y - self.margin/2), 
                                    QPointF(avg_x, max_y + self.margin/2))
                
                if y_positions:
                    avg_y = sum(y_positions) / len(y_positions)
                    painter.drawLine(QPointF(min_x - self.margin/2, avg_y), 
                                    QPointF(max_x + self.margin/2, avg_y))
    
    def _draw_tao_lines(self, painter: QPainter, positions: Dict[int, Tuple[float, float]]) -> None:
        """
        Draw the Tao lines connecting vertices with the same Tao count.
        
        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        # Group vertices by Tao count (number of 0s in their ternary representation)
        tao_groups = {}
        
        for key in positions:
            ternary = decimal_to_ternary(key).zfill(self.dimension)
            tao_count = ternary.count('0')
            
            if tao_count not in tao_groups:
                tao_groups[tao_count] = []
            
            tao_groups[tao_count].append(key)
        
        # Draw connections between vertices in the same Tao group
        for tao_count, vertices in tao_groups.items():
            # Skip empty groups or groups with just one vertex
            if len(vertices) <= 1:
                continue
            
            # Choose color based on Tao count
            alpha = 130  # More visible
            
            # Use different colors for different Tao counts
            if tao_count == 0:  # No Tao lines (vertices)
                color = QColor(200, 0, 0, alpha)  # Red
            elif tao_count == self.dimension:  # All Tao lines (center)
                color = QColor(0, 150, 0, alpha)  # Green
            else:
                # Interpolate between colors based on Tao count ratio
                tao_ratio = tao_count / self.dimension
                red = int(max(0, (1 - tao_ratio) * 200))
                green = int(max(0, tao_ratio * 150))
                blue = int(max(0, 100 + tao_ratio * 100))
                color = QColor(red, green, blue, alpha)
            
            # Line style based on dimension and Tao count
            if self.dimension <= 3:
                # Solid line for 2D/3D
                pen = QPen(color, 2.0)
            else:
                # Dashed line for higher dimensions
                pen = QPen(color, 1.5, Qt.PenStyle.DashLine)
                
                # Customize dash pattern based on Tao count
                dash_length = 3 + tao_count
                space_length = 2 + (self.dimension - tao_count)
                pen.setDashPattern([dash_length, space_length])
            
            painter.setPen(pen)
            
            # Draw lines connecting all vertices in this Tao group
            for i in range(len(vertices)):
                for j in range(i + 1, len(vertices)):
                    v1, v2 = vertices[i], vertices[j]
                    
                    # Skip if either vertex is not in the positions dict
                    if v1 not in positions or v2 not in positions:
                        continue
                    
                    x1, y1 = positions[v1]
                    x2, y2 = positions[v2]
                    
                    # Use QPointF objects for float coordinates
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    
    def _draw_vertices(self, painter: QPainter, positions: Dict[int, Tuple[float, float]]) -> None:
        """
        Draw the vertices of the dimensional structure.
        
        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        for key, (x, y) in positions.items():
            # Get cached properties
            if key in self._grid_colors and key in self._grid_radii:
                color = self._grid_colors[key]
                radius = self._grid_radii[key]
            else:
                # Fallback if properties aren't cached (shouldn't happen normally)
                ternary = decimal_to_ternary(key).zfill(self.dimension)
                tao_count = ternary.count('0')
                
                radius = self.cell_size * 0.25 * (1.0 + 0.5 * tao_count / self.dimension)
                
                if tao_count == 0:
                    color = self.vertex_colors[1]  # Yang/Red
                elif tao_count == self.dimension:
                    color = self.vertex_colors[0]  # Tao/Green  
                else:
                    tao_ratio = tao_count / self.dimension
                    red = int(max(0, (1 - tao_ratio) * 200))
                    green = int(max(0, tao_ratio * 150))
                    blue = int(max(0, 100 + tao_ratio * 100))
                    color = QColor(red, green, blue)
            
            # Create a gradient for the vertex for a 3D effect
            gradient = QRadialGradient(x, y, radius)
            
            # Lighter center, original color at edge
            lighter_color = QColor(color)
            lighter_color.setRed(min(255, lighter_color.red() + 50))
            lighter_color.setGreen(min(255, lighter_color.green() + 50))
            lighter_color.setBlue(min(255, lighter_color.blue() + 50))
            
            gradient.setColorAt(0.0, lighter_color)
            gradient.setColorAt(1.0, color)
            
            # Draw the vertex with gradient fill
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawEllipse(QPointF(x, y), radius, radius)
            
            # Add a small highlight for 3D effect
            highlight_size = radius * 0.3
            highlight_offset = radius * 0.2
            
            highlight_gradient = QRadialGradient(
                x - highlight_offset, y - highlight_offset, 
                highlight_size
            )
            highlight_gradient.setColorAt(0.0, QColor(255, 255, 255, 180))
            highlight_gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
            
            painter.setBrush(QBrush(highlight_gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                QPointF(x - highlight_offset, y - highlight_offset), 
                highlight_size, highlight_size
            )
    
    def _draw_labels(self, painter: QPainter, positions: Dict[int, Tuple[float, float]]) -> None:
        """
        Draw labels for each position in the grid.
        
        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        painter.setPen(QPen(Qt.GlobalColor.black))
        
        # Calculate the appropriate font size based on dimension and cell size
        font_size = max(7, min(11, int(self.cell_size / 6.5)))
        
        # Adjust font size for higher dimensions (smaller text for more nodes)
        if self.dimension >= 4:
            font_size = max(6, font_size - (self.dimension - 3))
        
        font = QFont("Arial", font_size, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 98)
        painter.setFont(font)
        
        # Track label positions to avoid overlaps
        label_rects = []
        
        # Sort keys by decimal value for a consistent drawing order
        sorted_keys = sorted(positions.keys())
        
        for key in sorted_keys:
            x, y = positions[key]
            
            # Get the vertex radius
            radius = self._grid_radii.get(key, self.cell_size * 0.25)
            
            ternary = decimal_to_ternary(key).zfill(self.dimension)
            tao_count = ternary.count('0')
            
            # Create label text
            if self.dimension <= 3:
                # Show both decimal and ternary for 2D and 3D
                label = f"{key} ({ternary})"
            else:
                # Only show decimal for higher dimensions to save space
                label = f"{key}"
            
            # Adjust label size based on cell size and dimension
            label_width = max(40, min(120, self.cell_size * 0.9))
            label_height = max(14, min(30, self.cell_size * 0.25))
            
            # Position the label - adjust based on Tao count
            y_offset = radius + self.label_offset_y * self.cell_size
            text_rect = QRectF(
                x - label_width / 2,
                y + y_offset,
                label_width,
                label_height
            )
            
            # Check for overlaps
            overlap = False
            for rect in label_rects:
                if rect.intersects(text_rect):
                    overlap = True
                    break
            
            # Only draw if not overlapping
            if not overlap:
                # Adjust background color based on Tao count
                bg_opacity = 180 + min(50, tao_count * 10)
                
                # Draw with a semi-transparent background for readability
                painter.fillRect(text_rect, QColor(255, 255, 255, bg_opacity))
                
                # Add a border, with color indicating Tao count
                border_color = QColor(
                    max(50, 130 - tao_count * 20),
                    min(120, 40 + tao_count * 15),
                    min(130, 70 + tao_count * 10),
                    200
                )
                painter.setPen(QPen(border_color, 0.8))
                painter.drawRect(text_rect)
                
                # Draw text
                painter.setPen(QPen(Qt.GlobalColor.black))
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, label)
                
                # Store label rect to check for future overlaps
                label_rects.append(text_rect)
    
    def _highlight_current_ternary(self, painter: QPainter, positions: Dict[int, Tuple[float, float]]) -> None:
        """
        Highlight the position corresponding to the current ternary value.
        
        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        try:
            decimal_value = ternary_to_decimal(self.ternary_value)
            
            # Skip if the value is not in our positions
            if decimal_value not in positions:
                return
            
            x, y = positions[decimal_value]
            
            # Get the vertex radius
            radius = self._grid_radii.get(decimal_value, self.cell_size * 0.25)
            
            # Create a pulsing glow effect
            glow_size = radius * 2.0
            pulse_factor = 0.5 + 0.5 * math.sin(self.animation_step * 0.1)
            self.animation_step += 1
            
            # Create a gradient for the glow
            gradient = QRadialGradient(x, y, glow_size)
            gradient.setColorAt(0, QColor(255, 255, 0, 120 * pulse_factor))
            gradient.setColorAt(0.6, QColor(255, 215, 0, 80 * pulse_factor))
            gradient.setColorAt(1, QColor(255, 180, 0, 0))
            
            # Draw the glow
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), glow_size, glow_size)
            
            # Draw a golden ring around the vertex
            ring_width = 2.0 + pulse_factor * 1.0
            painter.setPen(QPen(QColor(255, 215, 0), ring_width))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(x, y), radius + 2, radius + 2)
            
            # Start the animation timer if not already running
            if not self._animation_timer.isActive():
                self._animation_timer.start()
        
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
        
        # Cache old size
        old_size = getattr(self, "_old_size", QSize(0, 0))
        new_size = self.size()
        
        # Only update if size changed significantly (more than 10 pixels in either dimension)
        if (abs(old_size.width() - new_size.width()) > 10 or 
                abs(old_size.height() - new_size.height()) > 10):
            self._old_size = new_size
            self._update_grid_positions()
            self.update()  # Trigger repaint
    
    def sizeHint(self) -> QSize:
        """
        Suggest an appropriate size for the widget.
        
        Returns:
            The recommended size for the widget
        """
        return QSize(600, 600)

    # Add new methods for zoom and pan
    def reset_view(self) -> None:
        """Reset zoom and pan to default values."""
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.update()
    
    def zoom_in(self) -> None:
        """Zoom in by a fixed amount."""
        self.zoom_factor = min(self.max_zoom, self.zoom_factor * 1.2)
        self.update()
    
    def zoom_out(self) -> None:
        """Zoom out by a fixed amount."""
        self.zoom_factor = max(self.min_zoom, self.zoom_factor / 1.2)
        self.update()
    
    # Mouse event handlers for pan and zoom
    def mousePressEvent(self, event) -> None:
        """Handle mouse press event for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = True
            self.last_mouse_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release event for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move event for panning."""
        if self.panning and self.last_mouse_pos is not None:
            delta = event.position() - self.last_mouse_pos
            self.pan_offset_x += delta.x()
            self.pan_offset_y += delta.y()
            self.last_mouse_pos = event.position()
            self.update()
        super().mouseMoveEvent(event)
    
    def wheelEvent(self, event) -> None:
        """Handle wheel event for zooming."""
        # Get mouse position for zoom origin
        mouse_pos = event.position()
        
        # Calculate mouse position relative to current pan offset
        mouse_x = (mouse_pos.x() - self.pan_offset_x) / self.zoom_factor
        mouse_y = (mouse_pos.y() - self.pan_offset_y) / self.zoom_factor
        
        # Calculate zoom factor change
        delta = event.angleDelta().y()
        zoom_change = 1.1 if delta > 0 else 0.9
        
        old_zoom = self.zoom_factor
        self.zoom_factor *= zoom_change
        self.zoom_factor = max(self.min_zoom, min(self.max_zoom, self.zoom_factor))
        
        # Adjust pan offset to keep point under mouse stable
        if old_zoom != self.zoom_factor:
            self.pan_offset_x = mouse_pos.x() - mouse_x * self.zoom_factor
            self.pan_offset_y = mouse_pos.y() - mouse_y * self.zoom_factor
            self.update()
        
        super().wheelEvent(event)


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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
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
        
        # Add zoom and pan controls
        zoom_layout = QHBoxLayout()
        
        # Zoom buttons
        self.zoom_in_btn = QPushButton("Zoom +")
        self.zoom_in_btn.setToolTip("Zoom in (or use mouse wheel)")
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        
        self.zoom_out_btn = QPushButton("Zoom -")
        self.zoom_out_btn.setToolTip("Zoom out (or use mouse wheel)")
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        
        self.reset_view_btn = QPushButton("Reset View")
        self.reset_view_btn.setToolTip("Reset zoom and pan to default")
        self.reset_view_btn.clicked.connect(self._reset_view)
        
        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.reset_view_btn)
        
        # Add navigation help text
        nav_label = QLabel("Drag to pan, mouse wheel to zoom")
        nav_label.setStyleSheet("font-size: 10px; color: #666;")
        
        # Add to main layout
        main_layout.addLayout(zoom_layout)
        main_layout.addWidget(nav_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Create visualizer in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(500)  # Increased from default
        scroll_area.setMinimumWidth(600)   # Set minimum width
        
        # Create container widget with layout to center the visualizer
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create the visualizer widget
        self.visualizer = PlanarExpansionVisualizer()
        self.visualizer.setMinimumSize(500, 500)  # Set minimum size
        container_layout.addWidget(self.visualizer)
        
        # Set the container as the scroll area widget
        scroll_area.setWidget(container)
        
        main_layout.addWidget(scroll_area, 1)  # Give it a stretch factor of 1
        
        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 5px; }")
        
        # Force initial visualization update after a short delay to ensure proper sizing
        QTimer.singleShot(100, self._update_visualization)
    
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
    
    # Add methods to handle zoom and pan buttons
    def _zoom_in(self) -> None:
        """Zoom in on the visualization."""
        self.visualizer.zoom_in()
    
    def _zoom_out(self) -> None:
        """Zoom out of the visualization."""
        self.visualizer.zoom_out()
    
    def _reset_view(self) -> None:
        """Reset the view to default zoom and pan."""
        self.visualizer.reset_view()


# Testing code
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    panel = PlanarExpansionPanel()
    panel.resize(800, 600)
    panel.show()
    sys.exit(app.exec()) 