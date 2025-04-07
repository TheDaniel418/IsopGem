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
        self.debug_mode = False  # Debug mode toggle
        
        # Zoom and pan parameters
        self.zoom_factor = 1.0
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.panning = False
        self.last_mouse_pos = None
        self.min_zoom = 0.2
        self.max_zoom = 5.0
        
        # 3D rotation parameters
        self.x_rotation = 30  # Degrees
        self.y_rotation = 30  # Degrees
        self.z_rotation = 0   # Degrees
        
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
        
        # Cache for 3D points before projection
        self._3d_points = {}
        
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
    
    def toggle_debug_mode(self, enabled: bool) -> None:
        """
        Toggle debug mode to show vertex count information.
        
        Args:
            enabled: Whether to enable debug mode
        """
        self.debug_mode = enabled
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
        self._3d_points = {}
        
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
            self._generate_square(center_x, center_y)
        elif self.dimension == 3:
            self._generate_cube(center_x, center_y)
        else:
            self._generate_hypercube(self.dimension, center_x, center_y)
        
        # Generate colors and sizes for vertices
        self._generate_vertex_properties()
        
        # For debugging - ensure we have the right number of vertices
        expected_count = 2**self.dimension
        actual_count = len(self._grid_positions)
        
        if actual_count != expected_count:
            print(f"WARNING: Mismatch in vertex count for {self.dimension}D. "
                  f"Expected {expected_count}, got {actual_count}")
    
    def _generate_square(self, center_x: float, center_y: float) -> None:
        """Generate grid positions for a proper 2D square."""
        # A square has 4 vertices, with coordinates:
        # (-1,-1), (1,-1), (1,1), (-1,1)
        
        # Calculate size
        size = self.cell_size * 3.0
        
        # Generate binary vertices (00, 01, 10, 11)
        vertices = []
        for i in range(2):
            for j in range(2):
                # Binary encoding of vertices
                binary = f"{i}{j}"
                decimal = int(binary, 2)
                
                # Map to x,y coordinates (-1 or 1 for each dimension)
                x = -1 + 2 * i
                y = -1 + 2 * j
                
                vertices.append((decimal, (x, y)))
        
        # Place vertices in the widget
        for decimal, (x, y) in vertices:
            # Scale and center
            widget_x = center_x + x * size / 2
            widget_y = center_y + y * size / 2
            
            # Convert decimal to ternary
            # For mapping binary vertices to ternary space, we'll use a specific mapping
            # This ensures compatibility with the existing ternary system
            # Simple approach: use binary digits and convert to ternary
            binary = bin(decimal)[2:].zfill(2)
            ternary = "".join("1" if bit == "1" else "0" for bit in binary)
            ternary_decimal = int(ternary, 3)
            
            self._grid_positions[ternary_decimal] = (widget_x, widget_y)
    
    def _generate_cube(self, center_x: float, center_y: float) -> None:
        """Generate grid positions for a proper 3D cube with rotation."""
        # A cube has 8 vertices, with coordinates:
        # (-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
        # (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)
        
        # Calculate size
        size = self.cell_size * 3.0
        
        # Generate binary vertices (000, 001, 010, ..., 111)
        vertices = []
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    # Binary encoding of vertices
                    binary = f"{i}{j}{k}"
                    decimal = int(binary, 2)
                    
                    # Map to x,y,z coordinates (-1 or 1 for each dimension)
                    x = -1 + 2 * i
                    y = -1 + 2 * j
                    z = -1 + 2 * k
                    
                    vertices.append((decimal, (x, y, z)))
        
        # Calculate rotation matrices
        sin_x = math.sin(math.radians(self.x_rotation))
        cos_x = math.cos(math.radians(self.x_rotation))
        sin_y = math.sin(math.radians(self.y_rotation))
        cos_y = math.cos(math.radians(self.y_rotation))
        sin_z = math.sin(math.radians(self.z_rotation))
        cos_z = math.cos(math.radians(self.z_rotation))
        
        # Place vertices in the widget with rotation
        for decimal, (x, y, z) in vertices:
            # Store the 3D point
            self._3d_points[decimal] = (x, y, z)
            
            # Apply rotations
            # Rotate around X axis
            y2 = y * cos_x - z * sin_x
            z2 = y * sin_x + z * cos_x
            
            # Rotate around Y axis
            x3 = x * cos_y + z2 * sin_y
            z3 = -x * sin_y + z2 * cos_y
            
            # Rotate around Z axis
            x4 = x3 * cos_z - y2 * sin_z
            y4 = x3 * sin_z + y2 * cos_z
            
            # Scale, apply perspective, and center
            scale = size / 3
            perspective = 1 + z3 * 0.2  # Perspective effect
            
            widget_x = center_x + x4 * scale * perspective
            widget_y = center_y + y4 * scale * perspective
            
            # Convert binary to ternary mapping
            binary = bin(decimal)[2:].zfill(3)
            ternary = "".join("1" if bit == "1" else "0" for bit in binary)
            ternary_decimal = int(ternary, 3)
            
            self._grid_positions[ternary_decimal] = (widget_x, widget_y)
    
    def _generate_hypercube(self, dimension: int, center_x: float, center_y: float) -> None:
        """Generate grid positions for higher dimensional hypercubes."""
        # Calculate size
        size = self.cell_size * (4 - dimension * 0.4)  # Shrink for higher dimensions
        
        # Generate all possible binary vertices (2^dimension vertices)
        vertices = []
        
        # Calculate projections for all vertices (0 to 2^dimension-1)
        for i in range(2**dimension):
            # Get binary representation of i
            binary = bin(i)[2:].zfill(dimension)
            
            # Calculate coordinates in n-dimensional space (-1 or 1 for each dimension)
            coords = []
            for bit in binary:
                coords.append(-1 + 2 * int(bit))
            
            vertices.append((i, coords))
        
        # Project vertices to 2D using dimension-specific methods
        if dimension == 4:
            self._generate_tesseract(vertices, center_x, center_y, size)
        elif dimension == 5:
            self._generate_5cube(vertices, center_x, center_y, size)
        elif dimension == 6:
            self._generate_6cube(vertices, center_x, center_y, size)
        else:
            # Fallback generic projection for other dimensions
            self._generate_generic_projection(vertices, dimension, center_x, center_y, size)
        
        # For TQ system - we need to maintain a method to map between binary and ternary
        # We do this separately to ensure all vertices are created first
        self._map_ternary_values()
    
    def _generate_tesseract(self, vertices, center_x: float, center_y: float, size: float) -> None:
        """
        Generate a tesseract (4D hypercube) visualization using the "cube within cube" projection.
        
        This is a standard way to visualize a tesseract in 2D, representing it as
        a small cube inside a larger cube, with corresponding vertices connected.
        """
        # Size adjustments for inner and outer cubes
        inner_scale = 0.4
        
        # Store all 3D points for each vertex before rotation
        unrotated_points = {}
        
        for decimal, coords in vertices:
            # Get 4D coordinates
            x4d, y4d, z4d, w4d = coords
            
            # Use the 4th dimension (w) to control the scale of the inner/outer cube
            # This creates a "cube within cube" effect
            scale_factor = inner_scale + (1.0 - inner_scale) * ((w4d + 1) / 2)
            
            # Project to 3D first - this is the essential step for tesseract visualization
            x = x4d * scale_factor
            y = y4d * scale_factor
            z = z4d * scale_factor
            
            # Store the unrotated 3D point
            unrotated_points[decimal] = (x, y, z)
        
        # Apply the 3D rotation to all points
        self._apply_3d_rotation_to_points(unrotated_points, center_x, center_y, size)
    
    def _generate_5cube(self, vertices, center_x: float, center_y: float, size: float) -> None:
        """
        Generate a 5D hypercube visualization using a tesseract-pair projection.
        
        A 5D hypercube can be visualized as a pair of tesseracts (4D hypercubes)
        with corresponding vertices connected.
        """
        # Size adjustments
        inner_scale = 0.35
        pair_separation = 0.3  # Controls separation between the two tesseract projections
        
        # Store all 3D points for each vertex before rotation
        unrotated_points = {}
        
        for decimal, coords in vertices:
            # Get 5D coordinates
            x5d, y5d, z5d, w5d, v5d = coords
            
            # Use the 5th dimension (v) to control pair separation
            # This creates two connected tesseracts, shifted apart
            pair_offset = v5d * pair_separation
            
            # Use 4th dimension (w) for the cube-within-cube effect
            scale_factor = inner_scale + (1.0 - inner_scale) * ((w5d + 1) / 2)
            
            # Project 5D to 3D space first
            x = x5d * scale_factor + pair_offset
            y = y5d * scale_factor 
            z = z5d * scale_factor
            
            # Store the unrotated 3D point
            unrotated_points[decimal] = (x, y, z)
        
        # Apply the 3D rotation to all points
        self._apply_3d_rotation_to_points(unrotated_points, center_x, center_y, size)
    
    def _generate_6cube(self, vertices, center_x: float, center_y: float, size: float) -> None:
        """
        Generate a 6D hypercube visualization using a three-layer projection.
        
        A 6D hypercube can be visualized as multiple 4D projections (tesseracts)
        arranged in a triangular pattern to show the additional dimensions.
        """
        # Size adjustments
        inner_scale = 0.3
        layer_offset = 0.4  # Controls separation between the layers
        
        # Store all 3D points for each vertex before rotation
        unrotated_points = {}
        
        for decimal, coords in vertices:
            # Get 6D coordinates
            x6d, y6d, z6d, w6d, v5d, u6d = coords
            
            # Use the 5th and 6th dimensions for layer positioning
            # This creates a triangular arrangement of tesseract projections
            layer_x_offset = v5d * layer_offset
            layer_y_offset = u6d * layer_offset * 0.8  # Slightly reduce vertical spread
            
            # Use 4th dimension for the cube-within-cube effect
            scale_factor = inner_scale + (1.0 - inner_scale) * ((w6d + 1) / 2)
            
            # Project 6D to 3D space first 
            x = x6d * scale_factor + layer_x_offset
            y = y6d * scale_factor + layer_y_offset
            z = z6d * scale_factor
            
            # Store the unrotated 3D point
            unrotated_points[decimal] = (x, y, z)
        
        # Apply the 3D rotation to all points
        self._apply_3d_rotation_to_points(unrotated_points, center_x, center_y, size)
    
    def _generate_generic_projection(self, vertices, dimension: int, center_x: float, center_y: float, size: float) -> None:
        """
        Generate a generic projection for dimensions not specifically handled.
        
        This is a fallback method that projects higher dimensional coordinates to 2D.
        """
        for decimal, coords in vertices:
            # Store multi-dimensional point if dimension <= 4
            if dimension <= 4:
                self._3d_points[decimal] = tuple(coords[:3]) if len(coords) >= 3 else tuple(coords + [0] * (3 - len(coords)))
            
            # Project to 2D using a balanced linear combination of coordinates
            # Split dimensions into two groups for X and Y projection
            half_dim = dimension // 2
            
            # Weight the dimensions with decreasing importance
            weights = [1.0 / (i + 2) for i in range(dimension)]
            
            # Calculate weighted averages for x and y
            x = sum(c * weights[i] for i, c in enumerate(coords[:half_dim]))
            y = sum(c * weights[i + half_dim] for i, c in enumerate(coords[half_dim:]))
            
            # Scale and center
            widget_x = center_x + x * size
            widget_y = center_y + y * size
            
            # Store the projected position
            self._grid_positions[decimal] = (widget_x, widget_y)
    
    def _generate_vertex_properties(self) -> None:
        """Generate colors and sizes for vertices based on their Tao count."""
        for decimal_value in self._grid_positions:
            ternary = decimal_to_ternary(decimal_value).zfill(self.dimension)
            tao_count = ternary.count('0')
            
            # Determine radius based on Tao count and dimension
            base_radius = self.cell_size * 0.25
            
            # Hypercube vertices all have the same size
            radius = base_radius * 1.2
            
            # But color can be based on Tao count
            if tao_count == 0:
                color = self.vertex_colors[1]  # Yang/Red
            elif tao_count == self.dimension:
                color = self.vertex_colors[0]  # Tao/Green
            else:
                # Blend between colors based on Tao count
                tao_ratio = tao_count / self.dimension
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
        
        # Draw debug information if debug mode is enabled
        if self.debug_mode:
            self._draw_debug_info(painter, positions)
    
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
        
        # For all dimensions, draw connecting lines between adjacent vertices
        # Two vertices are adjacent if their binary representations differ by exactly one bit
        position_keys = list(positions.keys())
        
        for i, key1 in enumerate(position_keys):
            # Convert to binary to check connectivity
            binary1 = bin(int("".join("1" if d == "1" else "0" for d in decimal_to_ternary(key1).zfill(self.dimension)), 3))[2:].zfill(self.dimension)
            
            for j, key2 in enumerate(position_keys[i+1:], i+1):
                binary2 = bin(int("".join("1" if d == "1" else "0" for d in decimal_to_ternary(key2).zfill(self.dimension)), 3))[2:].zfill(self.dimension)
                
                # Count bit differences
                diff_count = sum(a != b for a, b in zip(binary1, binary2))
                
                # Vertices are connected if they differ by exactly one bit
                if diff_count == 1:
                    x1, y1 = positions[key1]
                    x2, y2 = positions[key2]
                    
                    # Thinner lines for higher dimensions
                    thickness = max(0.5, 1.5 - self.dimension * 0.2)
                    
                    # Draw connecting grid line
                    painter.setPen(QPen(self.grid_color, thickness))
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
    
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
            
            # Convert float to int for alpha values - fix the conversion issue
            alpha1 = int(120 * pulse_factor)
            alpha2 = int(80 * pulse_factor)
            
            gradient.setColorAt(0, QColor(255, 255, 0, alpha1))
            gradient.setColorAt(0.6, QColor(255, 215, 0, alpha2))
            gradient.setColorAt(1, QColor(255, 180, 0, 0))
            
            # Draw the glow
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), glow_size, glow_size)
            
            # Draw a golden ring around the vertex
            ring_width = 2.0 + pulse_factor * 1.0
            
            # Convert float to int for pen width
            painter.setPen(QPen(QColor(255, 215, 0), int(ring_width)))
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

    def set_x_rotation(self, angle: int) -> None:
        """Set the X rotation angle."""
        self.x_rotation = angle
        self._update_grid_positions()
        self.update()
        
    def set_y_rotation(self, angle: int) -> None:
        """Set the Y rotation angle."""
        self.y_rotation = angle
        self._update_grid_positions()
        self.update()
        
    def set_z_rotation(self, angle: int) -> None:
        """Set the Z rotation angle."""
        self.z_rotation = angle
        self._update_grid_positions()
        self.update()

    def _apply_3d_rotation_to_points(self, point_dict: Dict[int, Tuple[float, float, float]], 
                                    center_x: float, center_y: float, size: float) -> None:
        """
        Apply 3D rotation to a dictionary of points and store the results in _grid_positions and _3d_points.
        
        Args:
            point_dict: Dictionary mapping decimal values to 3D coordinates before rotation
            center_x: X center of the display area
            center_y: Y center of the display area
            size: Size scaling factor for display
        """
        # Calculate rotation matrices
        sin_x = math.sin(math.radians(self.x_rotation))
        cos_x = math.cos(math.radians(self.x_rotation))
        sin_y = math.sin(math.radians(self.y_rotation))
        cos_y = math.cos(math.radians(self.y_rotation))
        sin_z = math.sin(math.radians(self.z_rotation))
        cos_z = math.cos(math.radians(self.z_rotation))
        
        # Apply rotations to all points
        for decimal, (x, y, z) in point_dict.items():
            # Store the unrotated 3D point
            self._3d_points[decimal] = (x, y, z)
            
            # Apply rotations
            # Rotate around X axis
            y2 = y * cos_x - z * sin_x
            z2 = y * sin_x + z * cos_x
            
            # Rotate around Y axis
            x3 = x * cos_y + z2 * sin_y
            z3 = -x * sin_y + z2 * cos_y
            
            # Rotate around Z axis
            x4 = x3 * cos_z - y2 * sin_z
            y4 = x3 * sin_z + y2 * cos_z
            
            # Scale, apply perspective, and center
            perspective = 1.0 + z3 * 0.2  # Perspective effect
            
            widget_x = center_x + x4 * size * perspective
            widget_y = center_y + y4 * size * perspective
            
            # Store the projected 2D position
            self._grid_positions[decimal] = (widget_x, widget_y)

    def _draw_debug_info(self, painter: QPainter, positions: Dict[int, Tuple[float, float]]) -> None:
        """
        Draw debug information about vertex counts.
        
        Args:
            painter: The QPainter to use
            positions: The positions dictionary
        """
        # Set up text formatting
        painter.setFont(QFont("Monospace", 10))
        painter.setPen(QPen(Qt.GlobalColor.black))
        
        # Calculate the mathematically correct number of vertices for each dimension
        correct_counts = {
            2: 4,    # Square: 2^2
            3: 8,    # Cube: 2^3
            4: 16,   # Tesseract: 2^4
            5: 32,   # 5-cube: 2^5
            6: 64    # 6-cube: 2^6
        }
        
        # Get the actual count
        actual_count = len(positions)
        correct_count = correct_counts.get(self.dimension, 2**self.dimension)
        
        # Prepare debug text
        debug_info = [
            f"DEBUG INFO:",
            f"Dimension: {self.dimension}D",
            f"Actual vertices: {actual_count}",
            f"Expected vertices: {correct_count}",
        ]
        
        if actual_count != correct_count:
            debug_info.append(f"MISMATCH! Difference: {correct_count - actual_count}")
        
        # Draw a semi-transparent background for the debug panel
        panel_width = 250
        panel_height = (len(debug_info) + 1) * 20
        panel_rect = QRectF(10, 40, panel_width, panel_height)
        
        painter.fillRect(panel_rect, QColor(255, 255, 200, 200))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawRect(panel_rect)
        
        # Draw each line of debug info
        for i, line in enumerate(debug_info):
            y_pos = 60 + i * 20
            painter.setPen(QPen(Qt.GlobalColor.black))
            if "MISMATCH" in line:
                painter.setPen(QPen(Qt.GlobalColor.red))
            painter.drawText(20, y_pos, line)
        
        # Add vertex details if there's a mismatch
        if actual_count != correct_count and self.dimension <= 6:
            y_pos = 60 + len(debug_info) * 20
            painter.setPen(QPen(Qt.GlobalColor.black))
            painter.drawText(20, y_pos, "Checking vertex indexes...")
            
            # Create an array of all expected vertices for this dimension
            expected_vertices = set(range(2**self.dimension))
            actual_vertices = set(positions.keys())
            
            # Find missing vertices
            missing = expected_vertices - actual_vertices
            if missing:
                missing_list = sorted(list(missing))
                missing_text = f"Missing {len(missing)} vertices: "
                if len(missing_list) > 5:
                    missing_text += ", ".join(str(v) for v in missing_list[:5]) + f", ... (+{len(missing_list)-5} more)"
                else:
                    missing_text += ", ".join(str(v) for v in missing_list)
                    
                y_pos += 20
                painter.setPen(QPen(Qt.GlobalColor.red))
                painter.drawText(20, y_pos, missing_text)
                
            # Find extra vertices
            extra = actual_vertices - expected_vertices
            if extra:
                extra_list = sorted(list(extra))
                extra_text = f"Extra {len(extra)} vertices: "
                if len(extra_list) > 5:
                    extra_text += ", ".join(str(v) for v in extra_list[:5]) + f", ... (+{len(extra_list)-5} more)"
                else:
                    extra_text += ", ".join(str(v) for v in extra_list)
                    
                y_pos += 20
                painter.setPen(QPen(Qt.GlobalColor.blue))
                painter.drawText(20, y_pos, extra_text)

    def _map_ternary_values(self):
        """Map between binary and ternary space for TQ functionality."""
        if not self._grid_positions:
            return
        
        # Create a new positions dict to hold the ternary mappings
        ternary_positions = {}
        ternary_3d_points = {}
        
        # For each binary vertex, create a ternary equivalent
        for binary_decimal, (x, y) in self._grid_positions.items():
            # Get binary representation
            binary = bin(binary_decimal)[2:].zfill(self.dimension)
            
            # Create corresponding ternary string (0->0, 1->1)
            ternary = "".join("1" if bit == "1" else "0" for bit in binary)
            ternary_decimal = int(ternary, 3)
            
            # Store positions under ternary decimal key
            ternary_positions[ternary_decimal] = (x, y)
            
            # Also map 3D points
            if binary_decimal in self._3d_points:
                ternary_3d_points[ternary_decimal] = self._3d_points[binary_decimal]
        
        # Switch to ternary mapping for TQ compatibility
        self._grid_positions = ternary_positions
        self._3d_points = ternary_3d_points


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
            "This visualizer shows hypercubes in different dimensions (2D-6D), "
            "displaying the correct geometric structure with proper vertex mapping."
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
        
        # 3D Rotation controls (only visible for 3D)
        self.rotation_group = QFrame()
        self.rotation_group.setFrameStyle(QFrame.Shape.StyledPanel)
        self.rotation_group.setStyleSheet("background-color: #f0f0f8; border-radius: 5px; padding: 5px;")
        rotation_layout = QVBoxLayout(self.rotation_group)
        
        rotation_title = QLabel("3D Rotation Controls")
        rotation_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rotation_title.setStyleSheet("font-weight: bold;")
        rotation_layout.addWidget(rotation_title)
        
        # X rotation
        x_rotation_layout = QHBoxLayout()
        x_rotation_layout.addWidget(QLabel("X:"))
        self.x_rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_rotation_slider.setRange(0, 360)
        self.x_rotation_slider.setValue(30)
        self.x_rotation_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.x_rotation_slider.setTickInterval(45)
        self.x_rotation_slider.valueChanged.connect(self._x_rotation_changed)
        x_rotation_layout.addWidget(self.x_rotation_slider)
        self.x_rotation_value = QLabel("30°")
        x_rotation_layout.addWidget(self.x_rotation_value, 0, Qt.AlignmentFlag.AlignRight)
        rotation_layout.addLayout(x_rotation_layout)
        
        # Y rotation
        y_rotation_layout = QHBoxLayout()
        y_rotation_layout.addWidget(QLabel("Y:"))
        self.y_rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_rotation_slider.setRange(0, 360)
        self.y_rotation_slider.setValue(30)
        self.y_rotation_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.y_rotation_slider.setTickInterval(45)
        self.y_rotation_slider.valueChanged.connect(self._y_rotation_changed)
        y_rotation_layout.addWidget(self.y_rotation_slider)
        self.y_rotation_value = QLabel("30°")
        y_rotation_layout.addWidget(self.y_rotation_value, 0, Qt.AlignmentFlag.AlignRight)
        rotation_layout.addLayout(y_rotation_layout)
        
        # Z rotation
        z_rotation_layout = QHBoxLayout()
        z_rotation_layout.addWidget(QLabel("Z:"))
        self.z_rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.z_rotation_slider.setRange(0, 360)
        self.z_rotation_slider.setValue(0)
        self.z_rotation_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.z_rotation_slider.setTickInterval(45)
        self.z_rotation_slider.valueChanged.connect(self._z_rotation_changed)
        z_rotation_layout.addWidget(self.z_rotation_slider)
        self.z_rotation_value = QLabel("0°")
        z_rotation_layout.addWidget(self.z_rotation_value, 0, Qt.AlignmentFlag.AlignRight)
        rotation_layout.addLayout(z_rotation_layout)
        
        # Reset rotation button
        reset_rotation_btn = QPushButton("Reset Rotation")
        reset_rotation_btn.clicked.connect(self._reset_rotation)
        rotation_layout.addWidget(reset_rotation_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(self.rotation_group)
        # Hide rotation controls initially if not in 3D
        self.rotation_group.setVisible(self.dimension_selector.currentData() == 3)
        
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
        
        self.debug_mode_checkbox = QPushButton("Debug Mode")
        self.debug_mode_checkbox.setCheckable(True)
        self.debug_mode_checkbox.setChecked(False)
        self.debug_mode_checkbox.clicked.connect(self._toggle_debug)
        self.debug_mode_checkbox.setStyleSheet("QPushButton:checked { background-color: #ffcc66; }")
        
        options_layout.addWidget(self.show_labels_checkbox)
        options_layout.addWidget(self.show_tao_lines_checkbox)
        options_layout.addWidget(self.show_grid_checkbox)
        options_layout.addWidget(self.debug_mode_checkbox)
        
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
    
    def _change_dimension(self, index):
        """Change the dimension of the visualization."""
        dimension = self.dimension_selector.currentData()
        
        # Show rotation controls for all dimensions, not just 3D
        self.rotation_group.setVisible(True)
        
        # Update title of rotation group based on dimension
        rotation_title = self.rotation_group.findChild(QLabel)
        if rotation_title:
            rotation_title.setText(f"{dimension}D Rotation Controls")
        
        # Update ternary input length hint
        self.ternary_input.setPlaceholderText(f"Enter ternary number (e.g. {'0' * dimension})")
        
        # Ensure ternary input has the right length
        current_text = self.ternary_input.text()
        if len(current_text) > dimension:
            self.ternary_input.setText(current_text[:dimension])
        
        # Update visualizer
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
    
    def _toggle_debug(self) -> None:
        """Toggle the debug information display."""
        enabled = self.debug_mode_checkbox.isChecked()
        self.visualizer.toggle_debug_mode(enabled)
        
        # Update button appearance
        if enabled:
            self.debug_mode_checkbox.setText("Debug Mode (ON)")
        else:
            self.debug_mode_checkbox.setText("Debug Mode")
    
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
    
    def _x_rotation_changed(self, value):
        """Handle X rotation slider change."""
        self.x_rotation_value.setText(f"{value}°")
        self.visualizer.set_x_rotation(value)
    
    def _y_rotation_changed(self, value):
        """Handle Y rotation slider change."""
        self.y_rotation_value.setText(f"{value}°")
        self.visualizer.set_y_rotation(value)
    
    def _z_rotation_changed(self, value):
        """Handle Z rotation slider change."""
        self.z_rotation_value.setText(f"{value}°")
        self.visualizer.set_z_rotation(value)
    
    def _reset_rotation(self):
        """Reset all rotation angles to default values."""
        self.x_rotation_slider.setValue(30)
        self.y_rotation_slider.setValue(30)
        self.z_rotation_slider.setValue(0)
        
        self.visualizer.set_x_rotation(30)
        self.visualizer.set_y_rotation(30)
        self.visualizer.set_z_rotation(0)


# Testing code
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    panel = PlanarExpansionPanel()
    panel.resize(800, 600)
    panel.show()
    sys.exit(app.exec()) 