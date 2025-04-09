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

import math
import time
from typing import Dict, Tuple

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QRadialGradient
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QGridLayout,
)

from tq.utils.ternary_converter import decimal_to_ternary, ternary_to_decimal


class PlanarExpansionVisualizer(QWidget):
    """
    Widget that visualizes the planar expansion of ternary numbers.

    This visualizer shows how ternary digits map to different dimensional planes,
    revealing the geometric structure inherent in the TQ system.
    """

    # Signal emitted when a ternary digit is clicked
    digit_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        """Initialize the planar expansion visualizer."""
        super().__init__(parent)
        
        # Set up basic properties
        self.dimension = 2
        self.ternary_value = ""
        self.vertex_count = 9  # Number of vertices in the 2D grid
        self.cell_size = 50.0  # Base size for grid cells
        self.zoom_factor = 1.0  # Zoom level
        self.min_zoom = 0.2    # Minimum zoom level
        self.max_zoom = 5.0    # Maximum zoom level
        self.margin = 50       # Margin around the visualization
        
        # Set the size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Initialize the grid
        self._grid_positions = {}
        self._3d_points = {}
        self._grid_colors = {}
        self._grid_radii = {}
        self._animation_progress = 0.0  # 0.0 to 1.0
        self._animating = False
        self._highlighted_vertices = set()
        
        # Rotation angles (in degrees) for 3D visualization
        self.x_rotation = 20
        self.y_rotation = 30
        self.z_rotation = 0
        
        # Set up colors
        self.background_color = QColor(255, 255, 255)
        self.grid_color = QColor(200, 200, 200)
        self.text_color = QColor(0, 0, 0)
        
        # Define colors for each ternary value
        self.vertex_colors = {
            0: QColor(50, 220, 50),    # Tao/0 - Green
            1: QColor(220, 50, 50),    # Yang/1 - Red
            2: QColor(50, 50, 220)     # Yin/2 - Blue
        }
        
        # Initialize tracking variables
        self.mouse_x = 0
        self.mouse_y = 0
        self.dragging = False
        self.last_click_position = QPointF(0, 0)
        
        # Toggle flags
        self.show_labels = True
        self.show_tao_lines = True
        self.show_grid = True
        self.debug_mode = False
        self.pure_yang_mode = False
        self.debug_verbosity = 1  # 0: minimal, 1: normal, 2: verbose
        self.cube_within_cube_style = True  # Default to the new visualization style
        
        # Label styling
        self.label_offset_y = 0.35  # Distance below the vertex
        self.label_bg_color = QColor(255, 255, 255, 230)  # Background color for labels
        self.label_border_color = QColor(80, 80, 80, 200)  # Border color for labels
        
        # Initialize pan offset
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        
        # Set up animation timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._animate_transition)
        self._timer.setInterval(16)  # ~60 FPS
        
        # Set focus policy to receive keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Enable mouse tracking for panning
        self.setMouseTracking(True)
        
        # Initialize the positions
        self._update_grid_positions()
        
        # Generate vertex properties (colors and sizes)
        self._generate_vertex_properties()

    def set_ternary(self, value: str) -> None:
        """
        Set the ternary number to visualize.

        Args:
            value: A valid ternary string
        """
        if not all(digit in "012" for digit in value):
            raise ValueError(f"Invalid ternary string: {value}")

        self.ternary_value = value
        self.update()

    def set_dimension(self, dimension: int) -> None:
        """
        Set the dimension of the visualization.

        Args:
            dimension: The dimension to set (2-6)
        """
        # Validate dimension range
        if dimension < 2 or dimension > 6:
            print(f"Invalid dimension: {dimension}, must be between 2 and 6")
            return

        # If same dimension, do nothing
        if dimension == self.dimension:
            return

        # Store current positions for animation
        self._start_dimension = self.dimension
        self._start_positions = self._grid_positions.copy()

        # Set new dimension
        old_dimension = self.dimension
        self.dimension = dimension

        # Generate positions for the new dimension
        old_vertex_count = len(self._grid_positions)
        self._update_grid_positions()

        # Start transition animation
        self._animation_progress = 0.0
        self._animating = True
        self._start_time = time.time()

        # Print debug info
        print(f"Transitioning from {old_dimension}D to {dimension}D")
        print(
            f"Previous vertex count: {old_vertex_count}, New vertex count: {len(self._grid_positions)}"
        )

        # Update the view
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
        Toggle debug mode on or off.

        Args:
            enabled: Whether to enable debug mode
        """
        self.debug_mode = enabled
        
        # When enabling debug mode, set verbosity to at least 1
        if enabled and self.debug_verbosity == 0:
            self.debug_verbosity = 1
            print("Debug mode enabled with verbosity level 1")
        elif enabled:
            print(f"Debug mode enabled with verbosity level {self.debug_verbosity}")
        else:
            print("Debug mode disabled")
            
        # Update the visualization
        self.update()

    def toggle_pure_yang_mode(self, enabled: bool) -> None:
        """
        Toggle pure Yang mode where all vertices are rendered as Yang (red).
        
        Args:
            enabled: Whether to enable pure Yang mode
        """
        self.pure_yang_mode = enabled
        self._update_grid_positions()
        self.update()

    def _animate_transition(self):
        """Animate the transition between dimensions."""
        if not self._animating:
            self._timer.stop()
            return

        # Update transition progress
        self._animation_progress += 0.05
        if self._animation_progress >= 1.0:
            self._animation_progress = 1.0
            self._animating = False
            self._timer.stop()

        self.update()  # Trigger repaint

    def _update_grid_positions(self) -> None:
        """
        Update the cached grid positions based on the current dimension.
        """
        # Store old positions if animating
        old_positions = self._grid_positions.copy() if self._animating else {}

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
            4: 0.7,  # 4D needs more space than 3D
            5: 0.6,
            6: 0.5,
        }

        available_size = min(width, height) - 2 * self.margin
        base_cell_size = available_size / (3.5 + self.dimension * 0.5)
        self.cell_size = max(
            50, base_cell_size * cell_size_multiplier.get(self.dimension, 0.5)
        )

        # Calculate center points for proper centering
        center_x = width / 2
        center_y = height / 2

        # Generate positions based on dimension
        if self.dimension == 2:
            self._generate_square(center_x, center_y)
        elif self.dimension == 3:
            self._generate_cube(center_x, center_y)
        elif self.dimension == 4:
            self._generate_tesseract(center_x, center_y)
        else:
            self._generate_hypercube(self.dimension, center_x, center_y)

        # Generate colors and sizes for vertices
        self._generate_vertex_properties()

        # For debugging - ensure we have the right number of vertices
        # Only show warning when not in an animation
        expected_count = 2**self.dimension
        actual_count = len(self._grid_positions)

        if actual_count != expected_count and not self._animating:
            print(
                f"WARNING: Mismatch in vertex count for {self.dimension}D. "
                f"Expected {expected_count}, got {actual_count}"
            )

    def _generate_square(self, center_x: float, center_y: float) -> None:
        """Generate grid positions for a proper 2D square."""
        # A square has 4 vertices, with coordinates:
        # (-1,-1), (1,-1), (1,1), (-1,1)

        print("\n=== 2D SQUARE GEOMETRY DEBUG ===")

        # Calculate size
        size = self.cell_size * 3.0

        # Generate binary vertices (00, 01, 10, 11)
        # Note: Binary 00 (decimal 0) will be our "origin" point at the center
        # and maps other vertices relative to this central point
        vertices = []
        for i in range(2):
            for j in range(2):
                # Binary encoding of vertices
                binary = f"{i}{j}"
                decimal = int(binary, 2)

                # Instead of mapping to (-1,1) range, we'll use (0,1) range
                # This places the origin (0,0) at the center
                # and maps other vertices relative to this central point
                x = -0.5 + i
                y = -0.5 + j

                print(f"2D Vertex: binary={binary}, decimal={decimal}")
                print(f"  Coordinates in 2D space: ({x}, {y})")

                vertices.append((decimal, (x, y)))

        # Place vertices in the widget
        for decimal, (x, y) in vertices:
            # Scale and center
            widget_x = center_x + x * size
            widget_y = center_y + y * size

            print(
                f"2D Vertex {decimal}: Final screen coordinates: ({widget_x:.1f}, {widget_y:.1f})"
            )

            # Convert decimal to ternary for mapping
            binary = bin(decimal)[2:].zfill(2)
            ternary = "".join("1" if bit == "1" else "0" for bit in binary)
            ternary_decimal = int(ternary, 3)

            print(
                f"  Binary: {binary}, Mapped to ternary: {ternary}, Ternary decimal: {ternary_decimal}"
            )

            self._grid_positions[ternary_decimal] = (widget_x, widget_y)

        print("=== END 2D SQUARE GEOMETRY DEBUG ===\n")

    def _generate_cube(self, center_x: float, center_y: float) -> None:
        """Generate grid positions for a proper 3D cube with ternary vertices (no-Tao n-grams only)."""
        # A cube has 8 vertices, but we're using ternary no-Tao n-grams (only 1s and 2s)
        # This means we're representing vertices with ternary numbers that have no 0s

        print("\n=== 3D TERNARY CUBE GEOMETRY DEBUG ===")

        # Calculate size
        size = self.cell_size * 3.0

        # Generate ternary vertices with no 0s (only 1s and 2s)
        # For 3D cube, we need 8 vertices which are represented by 3-digit ternary numbers
        # Binary cube vertices are: 000, 001, 010, 011, 100, 101, 110, 111
        # We map these to ternary no-Tao vertices (using only 1 and 2): 111, 112, 121, 122, 211, 212, 221, 222
        
        # Create a mapping from binary positions to no-Tao ternary values
        binary_to_ternary_mapping = {
            0: "111",  # 000 → 111 (all Yang)
            1: "112",  # 001 → 112
            2: "121",  # 010 → 121
            3: "122",  # 011 → 122
            4: "211",  # 100 → 211
            5: "212",  # 101 → 212
            6: "221",  # 110 → 221
            7: "222",  # 111 → 222 (all Yin)
        }

        # Verify that opposite vertices are conrunes of each other
        print("Verifying that opposite vertices are conrunes:")
        from tq.utils.ternary_transition import TernaryTransition
        transition = TernaryTransition()
        
        for i in range(8):
            for j in range(i+1, 8):
                # Check if these are opposite vertices in the cube
                # In binary, opposite vertices have all bits flipped (i ^ j == 7)
                if i ^ j == 7:  # XOR equals 7 means these are opposite vertices
                    ternary_i = binary_to_ternary_mapping[i]
                    ternary_j = binary_to_ternary_mapping[j]
                    
                    # Check if j is conrune of i (0→0, 1→2, 2→1)
                    conrune_i = ''.join(['0' if d == '0' else '2' if d == '1' else '1' for d in ternary_i])
                    
                    print(f"  Opposite vertices: {i}({ternary_i}) and {j}({ternary_j})")
                    print(f"  Conrune of {ternary_i} is {conrune_i}")
                    if conrune_i == ternary_j:
                        print(f"  ✓ Verified: Opposite vertices are conrunes")
                    else:
                        print(f"  ✗ Error: Opposite vertices are NOT conrunes")

        # Generate vertices with their spatial coordinates
        vertices = []
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    # Binary encoding of vertices
                    binary = f"{i}{j}{k}"
                    decimal = int(binary, 2)
                    
                    # Get the no-Tao ternary representation for this vertex
                    ternary = binary_to_ternary_mapping[decimal]
                    
                    # We'll use the binary decimal value as the key internally, but
                    # print the ternary representation for clarity
                    print(f"Vertex: binary={binary}, decimal={decimal}, ternary={ternary}")
                    print(f"  Coordinates in 3D space: ({-0.5 + i}, {-0.5 + j}, {-0.5 + k})")

                    # Map to x,y,z coordinates centered around the origin
                    x = -0.5 + i
                    y = -0.5 + j
                    z = -0.5 + k

                    vertices.append((decimal, ternary, (x, y, z)))

        # Calculate rotation matrices
        sin_x = math.sin(math.radians(self.x_rotation))
        cos_x = math.cos(math.radians(self.x_rotation))
        sin_y = math.sin(math.radians(self.y_rotation))
        cos_y = math.cos(math.radians(self.y_rotation))
        sin_z = math.sin(math.radians(self.z_rotation))
        cos_z = math.cos(math.radians(self.z_rotation))

        print(f"  3D Rotation angles: X={self.x_rotation}°, Y={self.y_rotation}°, Z={self.z_rotation}°")

        # Place vertices in the widget with rotation
        for decimal, ternary, (x, y, z) in vertices:
            # Store the 3D point (using original binary decimal as key)
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

            print(f"Vertex {decimal}: After rotation: ({x4:.2f}, {y4:.2f}, {z3:.2f})")

            # Scale, apply perspective, and center
            scale = size
            perspective = 1 + z3 * 0.2  # Perspective effect

            widget_x = center_x + x4 * scale * perspective
            widget_y = center_y + y4 * scale * perspective

            print(f"  Final screen coordinates: ({widget_x:.1f}, {widget_y:.1f}), perspective={perspective:.2f}")
            print(f"  Using ternary: {ternary}")

            # Create a unique ID for this vertex by using the position in the binary sequence (0-7)
            # This ensures we have 8 unique vertices in the visualizer
            vertex_id = 1000 + decimal  # Add 1000 to ensure it doesn't collide with other IDs
            self._grid_positions[vertex_id] = (widget_x, widget_y)
            
            # Also store the ternary representation for later use
            self._ternary_values = getattr(self, '_ternary_values', {})
            self._ternary_values[vertex_id] = ternary

        # Check edge transitions
        print("\nChecking edge transitions (vertices connected by edges):")
        # In a cube, edges connect vertices that differ in exactly one binary digit
        for i, (dec_i, tern_i, _) in enumerate(vertices):
            for j, (dec_j, tern_j, _) in enumerate(vertices[i+1:], i+1):
                # Calculate binary Hamming distance (number of different bits)
                bin_i = bin(dec_i)[2:].zfill(3)
                bin_j = bin(dec_j)[2:].zfill(3)
                hamming_distance = sum(bit_i != bit_j for bit_i, bit_j in zip(bin_i, bin_j))
                
                # Edges connect vertices with Hamming distance of 1
                if hamming_distance == 1:
                    # Calculate the transition between these ternary values
                    transition_result = transition.apply_transition(tern_i, tern_j)
                    print(f"  Edge: {dec_i}({tern_i}) to {dec_j}({tern_j}) → Transition: {transition_result}")

        print("=== END 3D TERNARY CUBE GEOMETRY DEBUG ===\n")

    def _generate_tesseract(
        self, center_x: float, center_y: float
    ) -> None:
        """
        Generate the positions for a 4D tesseract (4-dimensional hypercube).
        
        This implementation uses either a cube-within-cube style or 4D projections
        based on the cube_within_cube_style flag.

        Args:
            center_x: The center x coordinate for the visualization
            center_y: The center y coordinate for the visualization
        """
        # Clear existing positions and 3D points
        self._grid_positions.clear()
        self._3d_points = {}
        
        # Define ternary values for each vertex of the tesseract
        ternary_mapping = {}
        print("\n=== 4D TERNARY TESSERACT GEOMETRY DEBUG ===")
        print("Tesseract vertex mapping (binary decimal → ternary):")
        
        # Create a mapping from binary to ternary for the tesseract
        for i in range(16):  # 16 vertices for a 4D tesseract
            binary = format(i, '04b')  # 4 bits for 4D
            # For 4D tesseract, we'll use 1 and 2 (instead of 0 and 1) for clarity
            ternary = ''.join('2' if bit == '1' else '1' for bit in binary)
            ternary_mapping[i] = ternary
            print(f"  {i} ({binary}) → {ternary}")
        
        print("\nVerifying that opposite vertices are conrunes:")
        # Verify that opposite vertices are conrunes in a tesseract
        for i in range(8):
            opposite_vertex = 15 - i  # In a 4D tesseract, opposite vertex has all bits flipped
            ternary_i = ternary_mapping[i]
            ternary_opposite = ternary_mapping[opposite_vertex]
            
            conrune_i = self._calculate_conrune(ternary_i)
            
            print(f"  Opposite vertices: {i}({ternary_i}) and {opposite_vertex}({ternary_opposite})")
            print(f"  Conrune of {ternary_i} is {conrune_i}")
            
            # Verify that the opposite vertex is the conrune
            if conrune_i == ternary_opposite:
                print(f"  ✓ Verified: Opposite vertices are conrunes")
            else:
                print(f"  ✗ ERROR: Opposite vertices are NOT conrunes")
        
        # Create mappings for vertex indices
        index_to_key = {}
        key_to_index = {}
        self._ternary_values = getattr(self, '_ternary_values', {})
        
        # Check which visualization style to use
        if hasattr(self, 'cube_within_cube_style') and self.cube_within_cube_style:
            # CUBE-WITHIN-CUBE STYLE
            # Size parameters for inner and outer cubes
            outer_size = 150.0
            inner_size = outer_size * 0.6  # Inner cube is 60% the size of outer cube
            
            # First, place vertices in a "cube within a cube" layout
            for i in range(16):
                binary = format(i, '04b')  # 4 bits for 4D
                
                # The first bit (MSB) determines whether vertex is in inner or outer cube
                is_inner_cube = binary[0] == '1'
                
                # The last 3 bits determine position within the cube (000 to 111)
                cube_position = binary[1:]
                
                # Convert binary to coordinates within cube (-1 or 1)
                x_offset = 1 if cube_position[0] == '1' else -1
                y_offset = 1 if cube_position[1] == '1' else -1
                z_offset = 1 if cube_position[2] == '1' else -1
                
                # Scale based on whether it's inner or outer cube
                size = inner_size if is_inner_cube else outer_size
                
                # Apply perspective adjustment for z-axis
                perspective = 1.0 + (z_offset * 0.2)  # Adjust multiplier for stronger/weaker effect
                
                # Calculate final coordinates
                x = center_x + (x_offset * size * 0.5 * perspective)
                y = center_y + (y_offset * size * 0.5 * perspective)
                
                # Store vertex position
                vertex_id = 2000 + i  # Start at 2000 to avoid collision with 3D cube vertices
                self._grid_positions[vertex_id] = (x, y)
                
                # Store mappings
                index_to_key[i] = vertex_id
                key_to_index[vertex_id] = i
                
                # Store the ternary representation
                self._ternary_values[vertex_id] = ternary_mapping[i]
                
                # Store 3D coordinates for later use
                self._3d_points[vertex_id] = (x_offset, y_offset, z_offset)
                
                # Print debug info
                size_label = "Inner" if is_inner_cube else "Outer"
                print(f"Vertex {i}: {size_label} cube, position {cube_position}")
                print(f"  Binary: {binary}, Ternary: {ternary_mapping[i]}")
                print(f"  Coordinates: ({x_offset}, {y_offset}, {z_offset})")
                print(f"  Final screen coordinates: ({x:.1f}, {y:.1f}), perspective={perspective:.2f}")
        else:
            # 4D PROJECTION STYLE
            # Vertices of 4D tesseract in model space
            vertices_4d = []
            for i in range(16):
                binary = format(i, '04b')
                
                # Convert binary to coordinates (-0.5 or 0.5)
                x = 0.5 if binary[0] == '1' else -0.5
                y = 0.5 if binary[1] == '1' else -0.5
                z = 0.5 if binary[2] == '1' else -0.5
                w = 0.5 if binary[3] == '1' else -0.5
                
                vertices_4d.append((x, y, z, w))
                
                # Print vertex info
                print(f"Vertex: binary={binary}, decimal={i}, ternary={ternary_mapping[i]}")
                print(f"  Coordinates in 4D space: ({x}, {y}, {z}, {w})")
            
            # Apply 4D rotations
            # We'll use simple rotations in the wx, wy, and wz planes
            wx_angle = math.radians(30)  # 30-degree rotation in the wx plane
            wy_angle = math.radians(30)  # 30-degree rotation in the wy plane
            wz_angle = math.radians(0)   # No rotation in the wz plane
            
            print(f"  4D Rotation angles: WX={int(math.degrees(wx_angle))}°, WY={int(math.degrees(wy_angle))}°, WZ={int(math.degrees(wz_angle))}°")
            
            for i, (x, y, z, w) in enumerate(vertices_4d):
                # Apply wx rotation
                x1 = x * math.cos(wx_angle) - w * math.sin(wx_angle)
                w1 = x * math.sin(wx_angle) + w * math.cos(wx_angle)
                y1 = y
                z1 = z
                
                # Apply wy rotation
                y2 = y1 * math.cos(wy_angle) - w1 * math.sin(wy_angle)
                w2 = y1 * math.sin(wy_angle) + w1 * math.cos(wy_angle)
                x2 = x1
                z2 = z1
                
                # Apply wz rotation
                z3 = z2 * math.cos(wz_angle) - w2 * math.sin(wz_angle)
                w3 = z2 * math.sin(wz_angle) + w2 * math.cos(wz_angle)
                x3 = x2
                y3 = y2
                
                # Project 4D to 3D using perspective projection from the w-axis
                # We'll use w3 to create a scaling factor for perspective
                distance = 2.0  # Distance from 4D viewer to hyperplane
                scale = distance / (distance + w3)
                
                x4 = x3 * scale
                y4 = y3 * scale
                z4 = z3 * scale
                
                # Now project from 3D to 2D for screen display
                # Use standard perspective projection
                perspective = 1.0 + z4 * 0.2  # Adjust multiplier for stronger/weaker effect
                
                # Scale and translate to screen coordinates
                scaling_factor = 150.0 * perspective
                widget_x = center_x + x4 * scaling_factor
                widget_y = center_y - y4 * scaling_factor  # Flip y for screen coordinates
                
                # Create a unique ID for this vertex
                vertex_id = 2000 + i  # Start at 2000 to avoid collision with 3D cube vertices
                self._grid_positions[vertex_id] = (widget_x, widget_y)
                
                # Store mappings
                index_to_key[i] = vertex_id
                key_to_index[vertex_id] = i
                
                # Store the ternary representation
                self._ternary_values[vertex_id] = ternary_mapping[i]
                
                # Also store the 3D projected point for edge calculations
                self._3d_points[vertex_id] = (x4, y4, z3)
                
                # Print debug info
                print(f"Vertex {i}: After 4D-3D-2D projection: ({x4:.2f}, {y4:.2f}, {z3:.2f})")
                print(f"  Final screen coordinates: ({widget_x:.1f}, {widget_y:.1f}), perspective={perspective:.2f}")
                print(f"  Using ternary: {ternary_mapping[i]}")
        
        # Check edge transitions
        print("\nChecking 4D hypercube edge connections:")
        edge_count = 0
        
        # A 4D hypercube has 16 vertices, and each vertex connects to exactly 4 others
        # (one for each dimension). This means there are 16 * 4 / 2 = 32 edges total
        # (dividing by 2 because each edge connects 2 vertices)
        for i in range(16):
            binary_i = format(i, '04b')
            
            # For each bit position (dimension)
            for bit_pos in range(4):
                # Flip the bit at this position to find the connected vertex
                bin_j_list = list(binary_i)
                bin_j_list[bit_pos] = '1' if binary_i[bit_pos] == '0' else '0'
                bin_j = ''.join(bin_j_list)
                j = int(bin_j, 2)
                
                # Only process if j > i to avoid duplicate edges
                if j > i:
                    # These vertices should be connected with an edge
                    if i in index_to_key and j in index_to_key:
                        start_key = index_to_key[i]
                        end_key = index_to_key[j]
                        
                        # Print the edge transition
                        if start_key in self._ternary_values and end_key in self._ternary_values:
                            start_ternary = self._ternary_values[start_key]
                            end_ternary = self._ternary_values[end_key]
                            
                            # Calculate transition digits
                            transition = self._calculate_transition(start_ternary, end_ternary)
                            print(f"  Edge: {i}({start_ternary}) to {j}({end_ternary}) → Transition: {transition}")
                            edge_count += 1
        
        print(f"  Total edges found: {edge_count} (expected: 32)")
        print("=== END 4D TERNARY TESSERACT GEOMETRY DEBUG ===\n")
        
    def toggle_tesseract_style(self) -> None:
        """Toggle between cube-within-cube and 4D projection visualization styles for the tesseract."""
        if not hasattr(self, 'cube_within_cube_style'):
            self.cube_within_cube_style = True
        else:
            self.cube_within_cube_style = not self.cube_within_cube_style
        
        # Only regenerate if we're currently in 4D mode
        if self.dimension == 4:
            self._update_grid_positions()
            self.update()  # Trigger repaint

    def _generate_hypercube(
        self, dimension: int, center_x: float, center_y: float
    ) -> None:
        """
        Generate the positions for an n-dimensional hypercube where n > 4.
        This is a fallback for higher dimensions where the number of vertices becomes too large
        for a ternary-based approach.

        Args:
            dimension: The dimension of the hypercube

        Returns:
            A dictionary mapping vertex indices to (x, y) coordinates
        """
        # For 4D, use the tesseract implementation
        if dimension == 4:
            self._generate_tesseract(center_x, center_y)
            return
        
        # For higher dimensions, use the existing implementation
        # ... existing hypercube code ...

    def _generate_vertex_properties(self) -> None:
        """Generate colors and sizes for vertices based on their ternary composition."""
        # Check if we're in pure Yang mode
        pure_yang_mode = self.pure_yang_mode or (self.ternary_value and all(digit == '1' for digit in self.ternary_value))
        
        # Access ternary values if available
        ternary_values = getattr(self, '_ternary_values', {})
        
        for decimal_value in self._grid_positions:
            # Get ternary representation - either from stored values or calculate it
            if decimal_value in ternary_values:
                ternary = ternary_values[decimal_value]
            else:
                # Fall back to old method for other dimensions
                ternary = decimal_to_ternary(decimal_value).zfill(self.dimension)
            
            tao_count = ternary.count("0")  # Number of 0s
            yang_count = ternary.count("1")  # Number of 1s
            yin_count = ternary.count("2")   # Number of 2s

            # Determine radius based on composition and dimension
            base_radius = self.cell_size * 0.25
            
            # Increase the radius of vertices with more significant meaning
            if self.dimension == 3:
                # Make vertices slightly larger for the 3D cube
                radius = base_radius * 1.3
                
                # If this is an all-Yang, all-Yin or all-Tao vertex, make it even larger
                if yang_count == self.dimension or yin_count == self.dimension or tao_count == self.dimension:
                    radius *= 1.2
            else:
                # Hypercube vertices all have the same size
                radius = base_radius * 1.2

            # Determine color based on ternary composition and mode
            if pure_yang_mode:
                # In pure Yang mode, all vertices are Yang/Red
                color = self.vertex_colors[1]  # Yang/Red
            elif yang_count == self.dimension:
                # All Yang/1s - should be pure red
                color = self.vertex_colors[1]  # Red
            elif tao_count == self.dimension:
                # All Tao/0s - should be pure green
                color = self.vertex_colors[0]  # Green
            elif yin_count == self.dimension:
                # All Yin/2s - should be pure blue
                color = self.vertex_colors[2]  # Blue
            else:
                # Mixed values - blend colors based on composition
                tao_ratio = tao_count / self.dimension
                yang_ratio = yang_count / self.dimension
                yin_ratio = yin_count / self.dimension
                
                # Calculate RGB components based on ratios - enhance saturation for better visibility
                red = int(min(255, yang_ratio * 230))
                green = int(min(255, tao_ratio * 180))
                blue = int(min(255, yin_ratio * 230))
                
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

        # If animating, interpolate positions
        positions = (
            self._get_interpolated_positions()
            if self._animating
            else self._grid_positions
        )

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
            self._draw_debug_panel(painter, self.size())

    def _get_interpolated_positions(self) -> Dict[int, Tuple[float, float]]:
        """
        Get interpolated positions between transitions.

        Returns:
            A dictionary of interpolated positions
        """
        # If not animating, just return the current grid positions
        if not self._animating:
            return self._grid_positions

        # Create a dictionary for the interpolated positions
        interpolated = {}

        # Get the old and new positions
        old_positions = self._start_positions

        # For each position in the new grid
        for decimal_value, new_pos in self._grid_positions.items():
            # If this position exists in both old and new grids, interpolate it
            if decimal_value in old_positions:
                old_x, old_y = old_positions[decimal_value]
                new_x, new_y = new_pos

                # Linear interpolation
                interp_x = old_x + (new_x - old_x) * self._animation_progress
                interp_y = old_y + (new_y - old_y) * self._animation_progress

                interpolated[decimal_value] = (interp_x, interp_y)
            else:
                # For new positions, fade them in (start from center and move to final position)
                new_x, new_y = new_pos
                center_x = self.width() / 2
                center_y = self.height() / 2

                # Start from center and move to final position
                interp_x = center_x + (new_x - center_x) * self._animation_progress
                interp_y = center_y + (new_y - center_y) * self._animation_progress

                interpolated[decimal_value] = (interp_x, interp_y)

        # For positions that exist in old but not in new, fade them out
        for decimal_value, old_pos in old_positions.items():
            if decimal_value not in self._grid_positions:
                old_x, old_y = old_pos
                center_x = self.width() / 2
                center_y = self.height() / 2

                # Move from current position toward center
                interp_x = old_x + (center_x - old_x) * self._animation_progress
                interp_y = old_y + (center_y - old_y) * self._animation_progress

                interpolated[decimal_value] = (interp_x, interp_y)

        return interpolated

    def _draw_grid(
        self, painter: QPainter, positions: Dict[int, Tuple[float, float]]
    ) -> None:
        """
        Draw the dimensional grid.

        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        # Access ternary values if available
        ternary_values = getattr(self, '_ternary_values', {})

        # For the 3D cube, use a special grid drawing that shows the cube edges more clearly
        if self.dimension == 3 and hasattr(self, '_ternary_values') and len(ternary_values) > 0:
            self._draw_3d_cube_grid(painter, positions)
            return
            
        # For the 4D tesseract, use a special grid drawing
        if self.dimension == 4 and hasattr(self, '_ternary_values') and len(ternary_values) > 0:
            self._draw_4d_tesseract_grid(painter, positions)
            return

        # Standard grid drawing for other dimensions
        painter.setPen(QPen(self.grid_color, 1.0))

        # For all dimensions, draw connecting lines between adjacent vertices
        # Two vertices are adjacent if their binary representations differ by exactly one bit
        position_keys = list(positions.keys())

        for i, key1 in enumerate(position_keys):
            # Convert to binary to check connectivity
            binary1 = bin(
                int(
                    "".join(
                        "1" if d == "1" else "0"
                        for d in decimal_to_ternary(key1).zfill(self.dimension)
                    ),
                    3,
                )
            )[2:].zfill(self.dimension)

            for j, key2 in enumerate(position_keys[i + 1 :], i + 1):
                binary2 = bin(
                    int(
                        "".join(
                            "1" if d == "1" else "0"
                            for d in decimal_to_ternary(key2).zfill(self.dimension)
                        ),
                        3,
                    )
                )[2:].zfill(self.dimension)

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

    def _draw_3d_cube_grid(
        self, painter: QPainter, positions: Dict[int, Tuple[float, float]]
    ) -> None:
        """
        Draw a clearer grid for the 3D cube case.

        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        from tq.utils.ternary_transition import TernaryTransition
        transition = TernaryTransition()
        
        # Get ternary values
        ternary_values = self._ternary_values
        
        # Define cube edges based on the binary representation
        # Each vertex in a cube is connected to 3 others (along each axis)
        cube_edges = [
            # Connecting vertices that differ by 1 bit in binary
            (0, 1), (0, 2), (0, 4),  # Edges from 000
            (1, 3), (1, 5),          # Edges from 001 
            (2, 3), (2, 6),          # Edges from 010
            (3, 7),                  # Edges from 011
            (4, 5), (4, 6),          # Edges from 100
            (5, 7),                  # Edges from 101
            (6, 7)                   # Edges from 110
        ]
        
        # First make a mapping from the original keys to 0-7 indices
        key_to_index = {}
        index_to_key = {}
        
        # Sort by the embedded decimal value, which should be 1000, 1001, etc. for the cube
        sorted_keys = sorted(positions.keys())
        if len(sorted_keys) == 8:  # Ensure we have the correct number of vertices
            for i, key in enumerate(sorted_keys):
                key_to_index[key] = i
                index_to_key[i] = key

        # Draw the edges
        for start, end in cube_edges:
            if start in index_to_key and end in index_to_key:
                start_key = index_to_key[start]
                end_key = index_to_key[end]
                
                # Get positions
                x1, y1 = positions[start_key]
                x2, y2 = positions[end_key]
                
                # Get ternary values
                if start_key in ternary_values and end_key in ternary_values:
                    start_ternary = ternary_values[start_key]
                    end_ternary = ternary_values[end_key]
                    
                    # Determine the type of transition
                    diff_positions = [i for i in range(len(start_ternary)) if start_ternary[i] != end_ternary[i]]
                    if len(diff_positions) == 1:
                        position = diff_positions[0]
                        
                        # Determine the specific digit transition (0→1, 0→2, 1→2, etc.)
                        from_digit = start_ternary[position]
                        to_digit = end_ternary[position]
                        
                        transition_type = f"{from_digit}{to_digit}"
                        
                        # Set color and style based on transition type
                        if transition_type == "01" or transition_type == "10":
                            # Tao-Yang transition - use a green-red gradient
                            pen = QPen(QColor(180, 90, 60), 1.8)
                        elif transition_type == "02" or transition_type == "20":
                            # Tao-Yin transition - use a green-blue gradient
                            pen = QPen(QColor(60, 90, 180), 1.8)
                        elif transition_type == "12" or transition_type == "21":
                            # Yang-Yin transition - use a purple gradient
                            pen = QPen(QColor(140, 60, 140), 1.8)
                        else:
                            # Fallback for any other transitions
                            pen = QPen(self.grid_color, 1.5)
                            
                        # Set the pen
                        painter.setPen(pen)
                        
                        # Draw the line
                        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                    
                else:
                    # Fallback if we don't have ternary values
                    painter.setPen(QPen(self.grid_color, 1.5))
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _draw_4d_tesseract_grid(
        self, painter: QPainter, positions: Dict[int, Tuple[float, float]]
    ) -> None:
        """
        Draw a clearer grid for the 4D tesseract case.

        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        from tq.utils.ternary_transition import TernaryTransition
        transition = TernaryTransition()
        
        # Get ternary values
        ternary_values = self._ternary_values
        
        # For a 4D hypercube, each vertex connects to 4 others (one for each dimension)
        # Vertices are connected if they differ by exactly one bit in their binary representation
        
        # First make a mapping from our display keys (2000+) back to 0-15 indices
        key_to_index = {}
        index_to_key = {}
        edge_count = 0
        
        # Sort by the embedded decimal value, which should be 2000, 2001, etc. for 4D
        sorted_keys = sorted(positions.keys())
        
        if len(sorted_keys) == 16:  # Ensure we have the correct number of vertices
            # Create mappings between display keys and indices
            for i, key in enumerate(sorted_keys):
                key_to_index[key] = i
                index_to_key[i] = key
            
            # A 4D hypercube has 16 vertices, and each vertex connects to exactly 4 others
            # (one for each dimension). This means there are 16 * 4 / 2 = 32 edges total
            # (dividing by 2 because each edge connects 2 vertices)
            for i in range(16):
                binary_i = format(i, '04b')
                
                # For each bit position (dimension)
                for bit_pos in range(4):
                    # Flip the bit at this position to find the connected vertex
                    bin_j_list = list(binary_i)
                    bin_j_list[bit_pos] = '1' if binary_i[bit_pos] == '0' else '0'
                    bin_j = ''.join(bin_j_list)
                    j = int(bin_j, 2)
                    
                    # Only process if j > i to avoid duplicate edges
                    if j > i:
                        # These vertices should be connected with an edge
                        if i in index_to_key and j in index_to_key:
                            start_key = index_to_key[i]
                            end_key = index_to_key[j]
                            
                            # Get positions
                            x1, y1 = positions[start_key]
                            x2, y2 = positions[end_key]
                            
                            # Get ternary values
                            if start_key in ternary_values and end_key in ternary_values:
                                start_ternary = ternary_values[start_key]
                                end_ternary = ternary_values[end_key]
                                
                                # The changed position is bit_pos (we already know it)
                                changed_position = bit_pos
                                
                                # Determine color and style based on which dimension the edge traverses
                                line_width = 2.0  # Thicker lines for better visibility
                                
                                if changed_position == 0:  # First dimension (W)
                                    color = QColor(200, 50, 50, 220)  # Red-ish with more opacity
                                    pen = QPen(color, line_width, Qt.PenStyle.SolidLine)
                                elif changed_position == 1:  # Second dimension (X)
                                    color = QColor(50, 200, 50, 220)  # Green-ish with more opacity
                                    pen = QPen(color, line_width, Qt.PenStyle.SolidLine)
                                elif changed_position == 2:  # Third dimension (Y)
                                    color = QColor(50, 50, 200, 220)  # Blue-ish with more opacity
                                    pen = QPen(color, line_width, Qt.PenStyle.SolidLine)
                                elif changed_position == 3:  # Fourth dimension (Z)
                                    color = QColor(200, 200, 40, 220)  # Yellow-ish with more opacity
                                    pen = QPen(color, line_width, Qt.PenStyle.SolidLine)
                                else:
                                    # Fallback (shouldn't happen)
                                    pen = QPen(self.grid_color, line_width)
                                
                                # Add different dash patterns for different dimensions to help
                                # distinguish the connections in the visual projection
                                if changed_position == 0:
                                    # Solid line for first dimension
                                    pass
                                elif changed_position == 1:
                                    # Dashed line for second dimension
                                    pen.setDashPattern([8, 4])
                                elif changed_position == 2:
                                    # Dotted line for third dimension
                                    pen.setDashPattern([2, 2])
                                elif changed_position == 3:
                                    # Dash-dot line for fourth dimension
                                    pen.setDashPattern([8, 4, 2, 4])
                                
                                # Set the pen
                                painter.setPen(pen)
                                
                                # Draw the line
                                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                                edge_count += 1
                                
                                # Optionally, add a small dimension indicator at the midpoint
                                midx = (x1 + x2) / 2
                                midy = (y1 + y2) / 2
                                
                                # Draw a small indicator of the dimension
                                dim_colors = [
                                    QColor(255, 100, 100),  # W - Red
                                    QColor(100, 255, 100),  # X - Green
                                    QColor(100, 100, 255),  # Y - Blue
                                    QColor(255, 255, 100)   # Z - Yellow
                                ]
                                
                                if changed_position >= 0 and changed_position < 4:
                                    painter.setBrush(QBrush(dim_colors[changed_position]))
                                    painter.setPen(Qt.PenStyle.NoPen)
                                    radius = min(5, line_width + 3)  # Small circle
                                    painter.drawEllipse(QPointF(midx, midy), radius, radius)
                            else:
                                # Fallback if we don't have ternary values
                                painter.setPen(QPen(self.grid_color, 1.5))
                                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                                edge_count += 1
        else:
            # Fallback if we don't have the right number of vertices
            # Use the standard grid drawing (not via super since this isn't an override method)
            painter.setPen(QPen(self.grid_color, 1.0))
            
            # Draw connecting lines between adjacent vertices
            position_keys = list(positions.keys())
            
            for i, key1 in enumerate(position_keys):
                for j, key2 in enumerate(position_keys[i + 1 :], i + 1):
                    x1, y1 = positions[key1]
                    x2, y2 = positions[key2]
                    
                    # Draw a simple line for fallback case
                    painter.setPen(QPen(self.grid_color, 1.0))
                    painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _generate_hypercube(
        self, dimension: int, center_x: float, center_y: float
    ) -> None:
        """
        Generate the positions for an n-dimensional hypercube where n > 4.
        This is a fallback for higher dimensions where the number of vertices becomes too large
        for a ternary-based approach.

        Args:
            dimension: The dimension of the hypercube

        Returns:
            A dictionary mapping vertex indices to (x, y) coordinates
        """
        # For 4D, use the tesseract implementation
        if dimension == 4:
            self._generate_tesseract(center_x, center_y)
            return
        
        # For higher dimensions, use the existing implementation
        # ... existing hypercube code ...

    def _draw_tao_lines(
        self, painter: QPainter, positions: Dict[int, Tuple[float, float]]
    ) -> None:
        """
        Draw the Tao lines connecting vertices with the same Tao count.

        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        # Group vertices by Tao count (number of 0s in their ternary representation)
        tao_groups = {}
        yang_groups = {}
        yin_groups = {}

        # Access ternary values if available
        ternary_values = getattr(self, '_ternary_values', {})
        
        # Check if we're in pure Yang mode
        pure_yang_mode = self.pure_yang_mode or (self.ternary_value and all(digit == '1' for digit in self.ternary_value))

        for key in positions:
            # Get ternary representation - either from stored values or calculate it
            if key in ternary_values:
                ternary = ternary_values[key]
            else:
                ternary = decimal_to_ternary(key).zfill(self.dimension)
            
            tao_count = ternary.count("0")
            yang_count = ternary.count("1")
            yin_count = ternary.count("2")

            # Group by Tao count (0s)
            if tao_count not in tao_groups:
                tao_groups[tao_count] = []
            tao_groups[tao_count].append(key)

            # Additional grouping by yang count (for future use)
            if yang_count not in yang_groups:
                yang_groups[yang_count] = []
            yang_groups[yang_count].append(key)
            
            # Additional grouping by yin count (for future use)
            if yin_count not in yin_groups:
                yin_groups[yin_count] = []
            yin_groups[yin_count].append(key)

        # For 3D cube, draw connections based on digit groups
        if self.dimension == 3 and hasattr(self, '_ternary_values') and len(ternary_values) > 0:
            # In 3D cube, draw special pattern connections
            groups_to_draw = []
            
            # Draw by Tao count
            for count, vertices in tao_groups.items():
                if len(vertices) > 1:
                    groups_to_draw.append((vertices, 'tao', count))
                    
            # Draw by Yang count
            for count, vertices in yang_groups.items():
                if len(vertices) > 1:
                    groups_to_draw.append((vertices, 'yang', count))
                    
            # Draw by Yin count
            for count, vertices in yin_groups.items():
                if len(vertices) > 1:
                    groups_to_draw.append((vertices, 'yin', count))
                    
            # Draw all groups with appropriate styling
            for vertices, type_name, count in groups_to_draw:
                # Choose color based on group type
                alpha = 100  # More transparent for less visual clutter
                
                if pure_yang_mode:
                    # In pure Yang mode, all lines are red
                    color = QColor(200, 0, 0, alpha)
                elif type_name == 'tao':
                    # Tao-based groups - green
                    green_intensity = min(220, 100 + count * 40)
                    color = QColor(0, green_intensity, 0, alpha)
                elif type_name == 'yang':
                    # Yang-based groups - red
                    red_intensity = min(220, 100 + count * 40)
                    color = QColor(red_intensity, 0, 0, alpha)
                elif type_name == 'yin':
                    # Yin-based groups - blue
                    blue_intensity = min(220, 100 + count * 40)
                    color = QColor(0, 0, blue_intensity, alpha)
                    
                # Set up the pen - use dashed line for 3D cube groups
                pen = QPen(color, 1.0, Qt.PenStyle.DashLine)
                dash_length = 5
                space_length = 3
                pen.setDashPattern([dash_length, space_length])
                
                painter.setPen(pen)
                
                # Draw lines connecting vertices in this group, but only if more than one
                if len(vertices) > 1:
                    # Draw as a polygon for complete groups
                    if len(vertices) >= 3 and (count == 0 or count == self.dimension):
                        # For complete groups, draw a polygon
                        points = [QPointF(*positions[v]) for v in vertices]
                        painter.setPen(pen)
                        painter.setBrush(Qt.BrushStyle.NoBrush)
                        painter.drawPolygon(points)
                    else:
                        # Otherwise draw individual lines
                        for i in range(len(vertices)):
                            for j in range(i + 1, len(vertices)):
                                v1, v2 = vertices[i], vertices[j]
                                
                                # Skip if either vertex is not in positions
                                if v1 not in positions or v2 not in positions:
                                    continue
                                    
                                x1, y1 = positions[v1]
                                x2, y2 = positions[v2]
                                
                                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        
        return  # Skip the standard rendering for 3D cube
                
        # Standard rendering for other dimensions
        # Draw connections between vertices in the same Tao group
        for tao_count, vertices in tao_groups.items():
            # Skip empty groups or groups with just one vertex
            if len(vertices) <= 1:
                continue

            # Choose color based on Tao count
            alpha = 130  # More visible

            # Use different colors for different Tao counts
            if pure_yang_mode:
                # In pure Yang mode, all lines are red (Yang color)
                color = QColor(200, 0, 0, alpha)  # Red
            elif tao_count == 0:  # No Tao (all 1s or 2s)
                color = QColor(200, 0, 0, alpha)  # Red
            elif tao_count == self.dimension:  # All Tao (all 0s)
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

    def _draw_vertices(
        self, painter: QPainter, positions: Dict[int, Tuple[float, float]]
    ) -> None:
        """
        Draw the vertices of the visualization.

        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        # Access ternary values if available
        ternary_values = getattr(self, '_ternary_values', {})
        
        # Get the ordered list of keys sorted by increasing value
        position_keys = sorted(positions.keys())
        
        for key in position_keys:
            x, y = positions[key]
            
            # Get the ternary representation
            if key in ternary_values:
                ternary = ternary_values[key]
            else:
                ternary = decimal_to_ternary(key).zfill(self.dimension)
            
            # Get the color and size from cache if available
            if key in self._grid_colors:
                color = self._grid_colors[key]
            else:
                # Determine color based on ternary representation
                # Default to pure Yang (red) in pure Yang mode
                if self.pure_yang_mode:
                    color = self.vertex_colors[1]  # Yang color
                else:
                    # Count the occurrences of each ternary value
                    tao_count = ternary.count("0")
                    yang_count = ternary.count("1")
                    yin_count = ternary.count("2")
                    
                    # Normalize the counts to get color ratios
                    total = self.dimension
                    tao_ratio = tao_count / total
                    yang_ratio = yang_count / total
                    yin_ratio = yin_count / total
                    
                    # Create a blended color based on the ratios
                    red = int(yang_ratio * 255)
                    green = int(tao_ratio * 255)
                    blue = int(yin_ratio * 255)
                    
                    # Enhance saturation for better visibility
                    # For cases where there's no strong dominance, boost the primary colors
                    max_ratio = max(tao_ratio, yang_ratio, yin_ratio)
                    
                    if max_ratio < 0.5:  # No strong dominance
                        if tao_ratio > 0:
                            green = min(255, green * 2)
                        if yang_ratio > 0:
                            red = min(255, red * 2)
                        if yin_ratio > 0:
                            blue = min(255, blue * 2)
                    
                    color = QColor(red, green, blue)
                
                # Cache the color
                self._grid_colors[key] = color
            
            # Get the radius from cache if available
            if key in self._grid_radii:
                radius = self._grid_radii[key]
            else:
                # Determine radius based on composition
                base_radius = self.cell_size * 0.25
                
                # For 3D vertices, make them larger - especially for "pure" vertices 
                # that are all Yang, all Yin, or all Tao
                if key >= 1000 and key < 2000:  # 3D cube vertices
                    tao_count = ternary.count("0")
                    yang_count = ternary.count("1")
                    yin_count = ternary.count("2")
                    
                    # For vertices that are all of one type, make them larger
                    if tao_count == 3 or yang_count == 3 or yin_count == 3:
                        radius = base_radius * 1.4
                    else:
                        radius = base_radius * 1.2
                # For 4D tesseract vertices, make them even more distinct
                elif key >= 2000 and key < 3000:  # 4D tesseract vertices
                    tao_count = ternary.count("0")
                    yang_count = ternary.count("1")
                    yin_count = ternary.count("2")
                    
                    # For vertices that are all of one type, make them larger
                    if tao_count == 4 or yang_count == 4 or yin_count == 4:
                        radius = base_radius * 1.6
                    else:
                        radius = base_radius * 1.3
                else:
                    radius = base_radius
                
                # Scale with zoom factor
                radius *= self.zoom_factor
                
                # Cache the radius
                self._grid_radii[key] = radius
            
            # Draw the vertex with a gradient fill for 3D effect
            gradient = QRadialGradient(x, y, radius * 1.2)
            gradient.setColorAt(0, QColor(255, 255, 255))  # White at center
            gradient.setColorAt(0.7, color)  # Base color
            gradient.setColorAt(1, color.darker(150))  # Darker at edge
            
            # Draw the filled circle
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), radius, radius)
            
            # Draw highlight to enhance 3D effect
            highlight_size = radius * 0.4
            highlight_offset = radius * 0.25
            highlight_color = QColor(255, 255, 255, 180)  # Semi-transparent white
            
            painter.setBrush(QBrush(highlight_color))
            painter.drawEllipse(
                QPointF(x - highlight_offset, y - highlight_offset),
                highlight_size,
                highlight_size
            )
            
            # Draw a small indicator of the ternary value for 3D cube vertices
            if key >= 1000 and key < 2000 and radius > 10:  # 3D cube vertices and reasonably sized
                # For 3D cube, we draw the ternary digits in a triangular formation
                digit_radius = radius * 0.25
                
                ternary_digits = ternary[-3:]  # Take the last three digits for 3D
                
                # Draw each ternary digit as a colored circle
                for idx, digit in enumerate(ternary_digits):
                    # Position digits in a triangular formation inside the vertex
                    if idx == 0:  # First digit at top
                        dx, dy = 0, -digit_radius * 1.5
                    elif idx == 1:  # Second digit at bottom left
                        dx, dy = -digit_radius * 1.5, digit_radius * 1.5
                    else:  # Third digit at bottom right
                        dx, dy = digit_radius * 1.5, digit_radius * 1.5
                    
                    # Color based on the ternary value
                    if digit == '0':  # Tao
                        painter.setBrush(QBrush(QColor(0, 180, 0)))
                    elif digit == '1':  # Yang
                        painter.setBrush(QBrush(QColor(220, 0, 0)))
                    else:  # Yin
                        painter.setBrush(QBrush(QColor(0, 0, 220)))
                    
                    # Draw the digit indicator
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(QPointF(x + dx, y + dy), digit_radius, digit_radius)
                    
                    # For larger vertices, add digit labels
                    if radius > 20:
                        painter.setPen(QPen(QColor(255, 255, 255)))
                        font = painter.font()
                        font.setPointSizeF(digit_radius * 1.2)
                        painter.setFont(font)
                        painter.drawText(
                            QRectF(
                                x + dx - digit_radius,
                                y + dy - digit_radius,
                                digit_radius * 2,
                                digit_radius * 2
                            ),
                            Qt.AlignmentFlag.AlignCenter,
                            digit
                        )
            
            # Draw a small indicator of the ternary value for 4D tesseract vertices
            elif key >= 2000 and key < 3000 and radius > 10:  # 4D tesseract vertices and reasonably sized
                # For 4D tesseract, we draw the ternary digits in a square formation
                digit_radius = radius * 0.23
                
                ternary_digits = ternary[-4:]  # Take the last four digits for 4D
                
                # Draw each ternary digit as a colored circle
                for idx, digit in enumerate(ternary_digits):
                    # Position digits in a square formation inside the vertex
                    if idx == 0:  # Top left
                        dx, dy = -digit_radius * 1.2, -digit_radius * 1.2
                    elif idx == 1:  # Top right
                        dx, dy = digit_radius * 1.2, -digit_radius * 1.2
                    elif idx == 2:  # Bottom left
                        dx, dy = -digit_radius * 1.2, digit_radius * 1.2
                    else:  # Bottom right (idx == 3)
                        dx, dy = digit_radius * 1.2, digit_radius * 1.2
                    
                    # Color based on the ternary value
                    if digit == '0':  # Tao
                        painter.setBrush(QBrush(QColor(0, 180, 0)))
                    elif digit == '1':  # Yang
                        painter.setBrush(QBrush(QColor(220, 0, 0)))
                    else:  # Yin
                        painter.setBrush(QBrush(QColor(0, 0, 220)))
                    
                    # Draw the digit indicator
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(QPointF(x + dx, y + dy), digit_radius, digit_radius)
                    
                    # For larger vertices, add digit labels
                    if radius > 20:
                        painter.setPen(QPen(QColor(255, 255, 255)))
                        font = painter.font()
                        font.setPointSizeF(digit_radius * 1.2)
                        painter.setFont(font)
                        painter.drawText(
                            QRectF(
                                x + dx - digit_radius,
                                y + dy - digit_radius,
                                digit_radius * 2,
                                digit_radius * 2
                            ),
                            Qt.AlignmentFlag.AlignCenter,
                            digit
                        )
                        
            # Skip drawing for performance reasons if dimension is large and we have many positions
            elif self.dimension > 4 and len(positions) > 100:
                pass

    def _draw_labels(
        self, painter: QPainter, positions: Dict[int, Tuple[float, float]]
    ) -> None:
        """
        Draw the labels for each position in the grid.

        Args:
            painter: The QPainter to use
            positions: The positions to use for drawing
        """
        if not self.show_labels:
            return

        # Ensure _grid_radii is initialized
        if not hasattr(self, '_grid_radii') or self._grid_radii is None:
            self._grid_radii = {}

        # Initialize list to track drawn label rectangles
        drawn_rects = []
        
        # Access ternary values if available
        ternary_values = getattr(self, '_ternary_values', {})
        
        # Get sorted keys to ensure consistent drawing order
        sorted_keys = sorted(positions.keys())
        
        for key in sorted_keys:
            x, y = positions[key]
            
            # Get ternary representation - either from stored values or calculate it
            if key in ternary_values:
                ternary = ternary_values[key]
            else:
                ternary = decimal_to_ternary(key).zfill(self.dimension)
            
            # Get Tao count for coloring
            tao_count = ternary.count('0')
            yang_count = ternary.count('1')
            yin_count = ternary.count('2')
            
            # Create the label text based on dimension and value
            if self.dimension == 3 and key in ternary_values:
                # For 3D, only show ternary if available
                label_text = f"{ternary}"
            elif self.dimension in [2, 3]:
                # For 2D and 3D cases, show both decimal and ternary
                if key >= 1000:  # 3D cube vertex
                    decimal_value = key - 1000
                else:
                    decimal_value = key
                label_text = f"{decimal_value} ({ternary})"
            elif self.dimension == 4 and key in ternary_values and key >= 2000:
                # For 4D tesseract vertices, format differently
                decimal_value = key - 2000
                # Display in a compact 2x2 format to show the 4D orientation
                # First find the binary representation (0-15)
                binary = format(decimal_value, '04b')
                label_text = f"{decimal_value}\n{binary}\n{ternary}"
            else:
                # For higher dimensions, just show decimal to keep it simple
                label_text = str(key)
            
            # Calculate position - below the vertex
            label_x = x
            label_y = y + self.cell_size * self.label_offset_y

            # Get width and height for the label background
            font_metrics = painter.fontMetrics()
            lines = label_text.split('\n')
            text_width = max(font_metrics.horizontalAdvance(line) for line in lines)
            text_height = font_metrics.height() * len(lines)
            
            # Add padding around the text
            padding = 6 if len(lines) > 1 else 4
            rect_width = text_width + padding * 2
            rect_height = text_height + padding * 2
            
            # Create label rectangle
            label_rect = QRectF(
                label_x - rect_width / 2,
                label_y - padding,
                rect_width,
                rect_height
            )
            
            # Check for overlap with previously drawn labels and adjust if needed
            overlap = True
            max_adjustments = 10
            adjustments = 0
            
            original_y = label_rect.y()
            
            while overlap and adjustments < max_adjustments:
                overlap = False
                for rect in drawn_rects:
                    if label_rect.intersects(rect):
                        overlap = True
                        # Move this label down slightly to avoid overlap
                        label_rect.moveTop(label_rect.y() + rect_height * 0.4)
                        adjustments += 1
                        break
                
                # Avoid moving too far from the original position
                if label_rect.y() > original_y + rect_height * 2:
                    break
            
            # For 4D vertices, color the label background based on ternary pattern
            if key >= 2000 and key < 3000 and key in ternary_values:  # 4D tesseract vertex
                # Blend colors based on Yang/Yin/Tao counts
                tao_ratio = tao_count / 4
                yang_ratio = yang_count / 4
                yin_ratio = yin_count / 4
                
                # Create a pastel version of the ternary color blend
                red = int(180 * yang_ratio + 230 * (1 - yang_ratio))
                green = int(180 * tao_ratio + 230 * (1 - tao_ratio))
                blue = int(180 * yin_ratio + 230 * (1 - yin_ratio))
                
                bg_color = QColor(red, green, blue, 230)
                border_color = QColor(min(red-50, 255), min(green-50, 255), min(blue-50, 255), 220)
            # For 3D vertices, color the label background based on ternary pattern
            elif key >= 1000 and key < 2000 and key in ternary_values:  # 3D cube vertex
                # Blend colors based on Yang/Yin/Tao counts
                tao_ratio = tao_count / 3
                yang_ratio = yang_count / 3
                yin_ratio = yin_count / 3
                
                # Create a pastel version of the ternary color blend
                red = int(180 * yang_ratio + 230 * (1 - yang_ratio))
                green = int(180 * tao_ratio + 230 * (1 - tao_ratio))
                blue = int(180 * yin_ratio + 230 * (1 - yin_ratio))
                
                bg_color = QColor(red, green, blue, 230)
                border_color = QColor(min(red-50, 255), min(green-50, 255), min(blue-50, 255), 220)
            else:
                # Default label styling for other dimensions
                bg_color = self.label_bg_color
                border_color = self.label_border_color

            # Draw label background
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(border_color, 1.0))
            painter.drawRoundedRect(label_rect, 4, 4)
            
            # Draw the text
            painter.setPen(QPen(Qt.GlobalColor.black))
            if '\n' in label_text:
                # Multi-line text (for 4D tesseract)
                y_offset = label_rect.y() + padding
                for line in lines:
                    text_rect = QRectF(
                        label_rect.x(),
                        y_offset,
                        label_rect.width(),
                        font_metrics.height()
                    )
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, line)
                    y_offset += font_metrics.height()
            else:
                # Single line text
                painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label_text)
            
            # Add to the list of drawn rectangles
            drawn_rects.append(label_rect)

    def _highlight_current_ternary(
        self, painter: QPainter, positions: Dict[int, Tuple[float, float]]
    ) -> None:
        """
        Highlight the current ternary number in the visualization.

        Args:
            painter: The QPainter to use
            positions: The positions dictionary
        """
        # Skip if no ternary value is set
        if not self.ternary_value or self.ternary_value == "0":
            return

        # Convert ternary to decimal
        decimal = ternary_to_decimal(self.ternary_value)

        # Skip if the value doesn't exist in our positions
        if decimal not in positions:
            return

        # Get the position
        x, y = positions[decimal]
        
        # Ensure _grid_radii is initialized
        if not hasattr(self, '_grid_radii') or self._grid_radii is None:
            self._grid_radii = {}
        
        # Get the vertex radius
        radius = self._grid_radii.get(decimal, self.cell_size * 0.25)
        
        # Calculate a pulse effect (0.7 to 1.0)
        pulse_factor = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(time.time() * 5))
        
        # Create a gradient for the glow effect
        highlight_size = radius * 3.0 * pulse_factor
        gradient = QRadialGradient(x, y, highlight_size)
        
        # Add yellow glow with pulse effect (using int for alpha)
        gradient.setColorAt(0, QColor(255, 255, 0, int(120 * pulse_factor)))
        gradient.setColorAt(1, QColor(255, 255, 0, 0))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(x, y), highlight_size, highlight_size)

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
        if (
            abs(old_size.width() - new_size.width()) > 10
            or abs(old_size.height() - new_size.height()) > 10
        ):
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
        """Zoom in on the visualization."""
        self.zoom_factor = min(self.zoom_factor * 1.2, self.max_zoom)
        self.update()

    def zoom_out(self) -> None:
        """Zoom out of the visualization."""
        self.zoom_factor = max(self.zoom_factor / 1.2, self.min_zoom)
        self.update()

    # Mouse event handlers for pan and zoom
    def mousePressEvent(self, event) -> None:
        """Handle mouse press event for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_click_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """Handle mouse release event for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Handle mouse move event for panning."""
        if self.dragging and self.last_click_position is not None:
            delta = event.position() - self.last_click_position
            self.pan_offset_x += delta.x()
            self.pan_offset_y += delta.y()
            self.last_click_position = event.position()
            self.update()
        super().mouseMoveEvent(event)

    def wheelEvent(self, event) -> None:
        """Handle mouse wheel events for zooming."""
        # Delta is typically +/- 120, normalize it
        delta = event.angleDelta().y() / 120.0
        
        # Apply zoom
        if delta > 0:
            # Zoom in
            self.zoom_factor = min(self.zoom_factor * (1.0 + 0.1 * delta), self.max_zoom)
        else:
            # Zoom out
            self.zoom_factor = max(self.zoom_factor / (1.0 - 0.1 * delta), self.min_zoom)
            
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

    def _apply_3d_rotation_to_points(
        self,
        point_dict: Dict[int, Tuple[float, float, float]],
        center_x: float,
        center_y: float,
        size: float,
    ) -> None:
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

    def _draw_debug_panel(self, painter, size):
        """Draw debug information panel"""
        if not self.debug_mode:
            return

        # Create a semi-transparent background for the debug panel
        panel_rect = QRectF(10, 10, 330, 180)
        panel_color = QColor(0, 0, 0, 180)
        painter.setBrush(QBrush(panel_color))
        painter.setPen(QPen(QColor(255, 255, 255, 200), 1))
        painter.drawRect(panel_rect)

        # Setup text drawing
        painter.setPen(QPen(QColor(255, 255, 255, 255), 1))
        font = QFont("Monospace", 9)
        painter.setFont(font)
        y_offset = 25

        # Draw basic debug info - always shown regardless of verbosity
        painter.drawText(20, y_offset, f"Dimension: {self.dimension}")
        y_offset += 15

        vertex_count = len(self._grid_positions)
        expected_vertices = (
            3**self.dimension if self.dimension <= 4 else 2**self.dimension
        )

        # Draw vertex information
        painter.drawText(20, y_offset, f"Vertices: {vertex_count}")
        y_offset += 15

        # During transitions, show simplified info
        if self._animating:
            painter.drawText(20, y_offset, "Animating between dimensions...")
            y_offset += 15
            painter.drawText(20, y_offset, f"Progress: {self._animation_progress:.2f}")
            y_offset += 15
            if hasattr(self, "_start_dimension"):
                painter.drawText(
                    20,
                    y_offset,
                    f"From dimension {self._start_dimension} to {self.dimension}",
                )
            else:
                painter.drawText(20, y_offset, "Dimension transition in progress")
            y_offset += 20

            # Skip detailed debug output during transitions
            if self.debug_verbosity <= 1:
                painter.drawText(
                    20, y_offset, "Detailed debug output paused during transition"
                )
                return

        # Show mismatch in vertex count
        if vertex_count != expected_vertices:
            painter.setPen(QPen(QColor(255, 100, 100, 255), 1))
            painter.drawText(
                20, y_offset, f"MISMATCH: Expected {expected_vertices} vertices"
            )
            y_offset += 15
            painter.setPen(QPen(QColor(255, 255, 255, 255), 1))

        # Only show detailed vertex info if verbosity > 0
        if self.debug_verbosity > 0:
            painter.drawText(20, y_offset, f"Current Ternary: {self.ternary_value}")
            y_offset += 15

            # Display camera/rotation info
            painter.drawText(
                20,
                y_offset,
                f"Rotation X: {self.x_rotation:.1f}, Y: {self.y_rotation:.1f}, Z: {self.z_rotation:.1f}",
            )
            y_offset += 15

            # Display scaling info
            painter.drawText(20, y_offset, f"Scale: {self.zoom_factor:.2f}")
            y_offset += 15

        # Only show vertex position data if verbosity > 1
        if self.debug_verbosity > 1 and not self._animating and vertex_count < 30:
            painter.drawText(20, y_offset, "Vertex Positions:")
            y_offset += 15

            for i, (x, y) in enumerate(self._grid_positions.values()):
                if i < 5:  # Show first 5 vertices only
                    painter.drawText(20, y_offset, f"  V{i}: ({x:.1f}, {y:.1f})")
                    y_offset += 15

            if vertex_count > 5:
                painter.drawText(20, y_offset, f"  ... {vertex_count-5} more vertices")

    def _map_ternary_values(self):
        """Map between binary and ternary space for TQ functionality."""
        if not self._grid_positions:
            return

        # For a 3D cube, we don't need to remap - we're already using the correct ternary representation
        if self.dimension == 3:
            if self.debug_mode and self.debug_verbosity > 1 and not self._animating:
                print("Using direct ternary mapping for 3D cube (no remapping needed)")
            return

        # For other dimensions, use the existing logic
        # Create a new positions dict to hold the ternary mappings
        ternary_positions = {}
        ternary_3d_points = {}

        # Determine if we're visualizing pure Yang trigrams (all 1s)
        pure_yang_mode = self.pure_yang_mode or (self.ternary_value and all(digit == '1' for digit in self.ternary_value))
        
        # For debugging
        if self.debug_mode and pure_yang_mode and not self._animating:
            print("\nPure Yang Mode detected - mapping all vertices to Yang (1) values")

        # For each binary vertex, create a ternary equivalent
        for binary_decimal, (x, y) in self._grid_positions.items():
            # Get binary representation
            binary = bin(binary_decimal)[2:].zfill(self.dimension)
            
            if pure_yang_mode:
                # If we're in pure Yang mode, map everything to Yang (1)
                ternary = "1" * self.dimension
                ternary_decimal = int(ternary, 3)
            else:
                # Default mapping: binary 0->0, binary 1->1
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
        
        # Regenerate vertex colors with the new mapping
        self._generate_vertex_properties()

    def set_debug_mode(self, enable: bool) -> None:
        """
        Set the debug mode.
        
        Args:
            enable: Whether to enable debug mode
        """
        self.debug_mode = enable
        self.update()

    def set_debug_verbosity(self, level: int) -> None:
        """
        Set the verbosity level for debug output.

        Args:
            level: The verbosity level (0=minimal, 1=normal, 2=verbose)
        """
        self.debug_verbosity = max(0, min(2, level))  # Clamp between 0-2
        self.update()

    def _calculate_conrune(self, ternary_value: str) -> str:
        """
        Calculate the conrune of a ternary value.

        Args:
            ternary_value: The ternary value to calculate the conrune for

        Returns:
            The conrune of the ternary value
        """
        # Conrune transformation: 1->2, 2->1
        return ''.join('2' if d == '1' else '1' if d == '2' else '0' for d in ternary_value)
    
    def _calculate_transition(self, start_ternary: str, end_ternary: str) -> str:
        """
        Calculate the transition between two ternary values.

        Args:
            start_ternary: The starting ternary value
            end_ternary: The ending ternary value

        Returns:
            The transition value
        """
        result = []
        for a, b in zip(start_ternary, end_ternary):
            if a == b:
                result.append(a)
            else:
                # For transitions, use the transition digit representing the change
                if (a == '1' and b == '2') or (a == '2' and b == '1'):
                    result.append('0')  # Transition between Yang and Yin is Tao
                elif a == '0' or b == '0':
                    # Tao transitions with Yang or Yin
                    result.append('1' if b == '2' else '2')
        return ''.join(result)


class PlanarExpansionPanel(QFrame):
    """
    Panel container for the planar expansion visualizer with controls.
    """

    def __init__(self, parent=None):
        """Initialize the planar expansion panel."""
        super().__init__(parent)
        
        # Set up the layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create a title label
        title_label = QLabel("Planar Expansion Visualizer")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.main_layout.addWidget(title_label)
        
        # Create the visualizer
        self.visualizer = PlanarExpansionVisualizer(self)
        
        # Create a horizontal layout for dimension selection and input
        self.input_layout = QHBoxLayout()
        
        # Dimension selector
        self.dimension_selector = QComboBox()
        self.dimension_selector.addItems(["2D (Planar)", "3D (Cube)", "4D (Tesseract)"])
        self.dimension_selector.setCurrentIndex(1)  # Start with 3D
        self.dimension_selector.currentIndexChanged.connect(self._change_dimension)
        self.input_layout.addWidget(QLabel("Dimension:"))
        self.input_layout.addWidget(self.dimension_selector)
        
        # Ternary input field
        self.ternary_input = QLineEdit()
        self.ternary_input.setPlaceholderText("Enter ternary value")
        self.ternary_input.textChanged.connect(self._validate_input)
        self.input_layout.addWidget(QLabel("Value:"))
        self.input_layout.addWidget(self.ternary_input)
        
        # Add the input layout to the main layout
        self.main_layout.addLayout(self.input_layout)
        
        # Add the visualizer to the main layout
        self.main_layout.addWidget(self.visualizer)
        
        # Create a layout for visualization controls
        self.controls_layout = QHBoxLayout()
        
        # Toggle buttons for various display options
        self.labels_toggle = QCheckBox("Show Labels")
        self.labels_toggle.setChecked(True)
        self.labels_toggle.stateChanged.connect(self._toggle_labels)
        self.controls_layout.addWidget(self.labels_toggle)
        
        self.tao_lines_toggle = QCheckBox("Show Tao Lines")
        self.tao_lines_toggle.setChecked(True)
        self.tao_lines_toggle.stateChanged.connect(self._toggle_tao_lines)
        self.controls_layout.addWidget(self.tao_lines_toggle)
        
        self.grid_toggle = QCheckBox("Show Grid")
        self.grid_toggle.setChecked(True)
        self.grid_toggle.stateChanged.connect(self._toggle_grid)
        self.controls_layout.addWidget(self.grid_toggle)
        
        self.debug_toggle = QCheckBox("Debug Mode")
        self.debug_toggle.setChecked(False)
        self.debug_toggle.stateChanged.connect(self._toggle_debug)
        self.controls_layout.addWidget(self.debug_toggle)
        
        self.pure_yang_toggle = QCheckBox("Pure Yang Mode")
        self.pure_yang_toggle.setChecked(False)
        self.pure_yang_toggle.stateChanged.connect(self._toggle_pure_yang_mode)
        self.controls_layout.addWidget(self.pure_yang_toggle)
        
        # Add tesseract style toggle button - only enabled when in 4D mode
        self.tesseract_style_toggle = QPushButton("Switch 4D Style")
        self.tesseract_style_toggle.setEnabled(False)  # Disabled until 4D is selected
        self.tesseract_style_toggle.clicked.connect(self._toggle_tesseract_style)
        self.controls_layout.addWidget(self.tesseract_style_toggle)
        
        # Add the controls layout to the main layout
        self.main_layout.addLayout(self.controls_layout)
        
        # Create a layout for zoom controls
        self.zoom_layout = QHBoxLayout()
        
        # Zoom controls
        zoom_in_button = QPushButton("+")
        zoom_in_button.setFixedSize(30, 30)
        zoom_in_button.clicked.connect(self._zoom_in)
        self.zoom_layout.addWidget(zoom_in_button)
        
        zoom_out_button = QPushButton("-")
        zoom_out_button.setFixedSize(30, 30)
        zoom_out_button.clicked.connect(self._zoom_out)
        self.zoom_layout.addWidget(zoom_out_button)
        
        reset_button = QPushButton("Reset View")
        reset_button.clicked.connect(self._reset_view)
        self.zoom_layout.addWidget(reset_button)
        
        # Add the zoom layout to the main layout
        self.main_layout.addLayout(self.zoom_layout)
        
        # Create a layout for rotation controls (only active for 3D and 4D)
        self.rotation_layout = QGridLayout()
        
        # X rotation
        self.rotation_layout.addWidget(QLabel("X Rotation:"), 0, 0)
        self.x_rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.x_rotation_slider.setRange(0, 360)
        self.x_rotation_slider.setValue(30)
        self.x_rotation_slider.valueChanged.connect(self._x_rotation_changed)
        self.rotation_layout.addWidget(self.x_rotation_slider, 0, 1)
        
        # Y rotation
        self.rotation_layout.addWidget(QLabel("Y Rotation:"), 1, 0)
        self.y_rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.y_rotation_slider.setRange(0, 360)
        self.y_rotation_slider.setValue(30)
        self.y_rotation_slider.valueChanged.connect(self._y_rotation_changed)
        self.rotation_layout.addWidget(self.y_rotation_slider, 1, 1)
        
        # Z rotation
        self.rotation_layout.addWidget(QLabel("Z Rotation:"), 2, 0)
        self.z_rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.z_rotation_slider.setRange(0, 360)
        self.z_rotation_slider.setValue(0)
        self.z_rotation_slider.valueChanged.connect(self._z_rotation_changed)
        self.rotation_layout.addWidget(self.z_rotation_slider, 2, 1)
        
        # Reset rotation button
        reset_rotation_button = QPushButton("Reset Rotation")
        reset_rotation_button.clicked.connect(self._reset_rotation)
        self.rotation_layout.addWidget(reset_rotation_button, 3, 0, 1, 2)
        
        # Add the rotation layout to the main layout
        self.main_layout.addLayout(self.rotation_layout)
        
        # Initialize any other attributes that might be used elsewhere
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        
        # Set the initial dimension
        self._change_dimension(1)  # 3D cube

    def _validate_input(self) -> None:
        """Validate the ternary input and update UI accordingly."""
        # Get the current text
        text = self.ternary_input.text().strip()
        
        # If the text is empty, clear any error styling and return
        if not text:
            self.ternary_input.setStyleSheet("")
            return
            
        # Get the current dimension
        dimension = self.dimension_selector.currentIndex() + 2  # 0->2D, 1->3D, 2->4D
        
        # Check if the text contains only valid ternary digits (0, 1, 2)
        is_valid = all(c in "012" for c in text)
        
        # Apply appropriate styling
        if is_valid:
            # Valid input - clear error styling
            self.ternary_input.setStyleSheet("")
            
            # Auto-update visualization when input is valid
            self._update_visualization()
        else:
            # Invalid input - apply error styling
            self.ternary_input.setStyleSheet("background-color: #ffcccc;")
            
        # Optionally truncate if longer than the current dimension
        if len(text) > dimension:
            self.ternary_input.setText(text[:dimension])

    def _update_visualization(self) -> None:
        """Update the visualization based on current input values."""
        # Get the ternary value from the input field
        ternary_value = self.ternary_input.text().strip()
        
        # Only update if we have a valid ternary value
        if ternary_value:
            # Update the visualizer
            self.visualizer.set_ternary(ternary_value)
        
        # Force a repaint
        self.visualizer.update()

    def _change_dimension(self, index):
        """Handle dimension change from the combo box."""
        # Map index to dimension
        dimension = index + 2  # 0->2D, 1->3D, 2->4D
        
        # Update the visualizer
        self.visualizer.set_dimension(dimension)
        
        # Enable/disable rotation controls based on dimension
        rotation_enabled = dimension > 2
        if hasattr(self, 'rotation_layout'):
            for i in range(self.rotation_layout.rowCount()):
                for j in range(self.rotation_layout.columnCount()):
                    item = self.rotation_layout.itemAtPosition(i, j)
                    if item and item.widget():
                        item.widget().setEnabled(rotation_enabled)
        
        # Enable/disable tesseract style toggle based on dimension
        if hasattr(self, 'tesseract_style_toggle'):
            self.tesseract_style_toggle.setEnabled(dimension == 4)
            
            # Update the button text based on current style
            if dimension == 4:
                if hasattr(self.visualizer, 'cube_within_cube_style') and self.visualizer.cube_within_cube_style:
                    self.tesseract_style_toggle.setText("Switch to 4D Projection")
                else:
                    self.tesseract_style_toggle.setText("Switch to Cube-in-Cube")

    def _toggle_labels(self) -> None:
        """Toggle the display of labels."""
        show = self.labels_toggle.isChecked()
        self.visualizer.toggle_labels(show)

    def _toggle_tao_lines(self) -> None:
        """Toggle the display of Tao lines."""
        show = self.tao_lines_toggle.isChecked()
        self.visualizer.toggle_tao_lines(show)

    def _toggle_grid(self) -> None:
        """Toggle the display of the grid."""
        show = self.grid_toggle.isChecked()
        self.visualizer.toggle_grid(show)

    def _toggle_debug(self) -> None:
        """Toggle the debug information display."""
        enabled = self.debug_toggle.isChecked()
        self.visualizer.toggle_debug_mode(enabled)

        # Update button appearance
        if enabled:
            self.debug_toggle.setText("Debug Mode (ON)")
        else:
            self.debug_toggle.setText("Debug Mode")

    def _toggle_pure_yang_mode(self) -> None:
        """Toggle pure Yang mode."""
        enabled = self.pure_yang_toggle.isChecked()
        self.visualizer.toggle_pure_yang_mode(enabled)

        # Update button appearance
        if enabled:
            self.pure_yang_toggle.setText("Pure Yang Mode (ON)")
            self.pure_yang_toggle.setToolTip("All vertices shown as Yang (red)")
        else:
            self.pure_yang_toggle.setText("Pure Yang Mode")
            self.pure_yang_toggle.setToolTip("Show normal ternary coloring")

    # Add methods to handle zoom and pan buttons
    def _zoom_in(self) -> None:
        """Zoom in on the visualization."""
        self.visualizer.zoom_in()

    def _zoom_out(self) -> None:
        """Zoom out of the visualization."""
        self.visualizer.zoom_out()

    def _reset_view(self) -> None:
        """Reset the view to the default settings."""
        self.visualizer.reset_view()

    def _x_rotation_changed(self, value):
        """Handle changes to the X rotation slider."""
        self.visualizer.set_x_rotation(value)
        # Update display label if exists
        if hasattr(self, 'x_rotation_value'):
            self.x_rotation_value.setText(f"{value}°")

    def _y_rotation_changed(self, value):
        """Handle changes to the Y rotation slider."""
        self.visualizer.set_y_rotation(value)
        # Update display label if exists
        if hasattr(self, 'y_rotation_value'):
            self.y_rotation_value.setText(f"{value}°")

    def _z_rotation_changed(self, value):
        """Handle changes to the Z rotation slider."""
        self.visualizer.set_z_rotation(value)
        # Update display label if exists
        if hasattr(self, 'z_rotation_value'):
            self.z_rotation_value.setText(f"{value}°")

    def _reset_rotation(self):
        """Reset all rotation angles to their default values."""
        self.x_rotation_slider.setValue(30)
        self.y_rotation_slider.setValue(30)
        self.z_rotation_slider.setValue(0)
        self.visualizer.set_x_rotation(30)
        self.visualizer.set_y_rotation(30)
        self.visualizer.set_z_rotation(0)

    def _toggle_tesseract_style(self) -> None:
        """Toggle the tesseract visualization style between cube-within-cube and 4D projection."""
        if hasattr(self.visualizer, 'toggle_tesseract_style'):
            self.visualizer.toggle_tesseract_style()
            
            # Update button text to reflect current style
            if hasattr(self.visualizer, 'cube_within_cube_style') and self.visualizer.cube_within_cube_style:
                self.tesseract_style_toggle.setText("Switch to 4D Projection")
            else:
                self.tesseract_style_toggle.setText("Switch to Cube-in-Cube")
                
    def _change_dimension(self, index):
        """Handle dimension change from the combo box."""
        # Map index to dimension
        dimension = index + 2  # 0->2D, 1->3D, 2->4D
        
        # Update the visualizer
        self.visualizer.set_dimension(dimension)
        
        # Enable/disable rotation controls based on dimension
        rotation_enabled = dimension > 2
        if hasattr(self, 'rotation_layout'):
            for i in range(self.rotation_layout.rowCount()):
                for j in range(self.rotation_layout.columnCount()):
                    item = self.rotation_layout.itemAtPosition(i, j)
                    if item and item.widget():
                        item.widget().setEnabled(rotation_enabled)
        
        # Enable/disable tesseract style toggle based on dimension
        if hasattr(self, 'tesseract_style_toggle'):
            self.tesseract_style_toggle.setEnabled(dimension == 4)
            
            # Update the button text based on current style
            if dimension == 4:
                if hasattr(self.visualizer, 'cube_within_cube_style') and self.visualizer.cube_within_cube_style:
                    self.tesseract_style_toggle.setText("Switch to 4D Projection")
                else:
                    self.tesseract_style_toggle.setText("Switch to Cube-in-Cube")


# Testing code
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = PlanarExpansionPanel()
    panel.resize(900, 1000)  # Increased from 800x600 to 900x1000
    panel.show()
    sys.exit(app.exec())
