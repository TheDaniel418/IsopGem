"""
Polygonal Numbers Visualization Widget.

This module provides a widget for visualizing polygonal and centered polygonal numbers.
"""

import math
from typing import List, Tuple, Set, Dict, Optional, Any, Callable, Union
import random
import colorsys
import logging

from PyQt6.QtCore import Qt, QPointF, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QMouseEvent, QWheelEvent, QPaintEvent, QPainterPath
from PyQt6.QtWidgets import QWidget, QSizePolicy, QToolTip

from geometry.calculator.polygonal_numbers_calculator import PolygonalNumbersCalculator


class PolygonalNumbersVisualization(QWidget):
    """Widget for visualizing polygonal and centered polygonal numbers."""

    # Signals
    selection_changed = pyqtSignal(list)  # Emitted when selection changes

    # Selection modes
    MODE_SELECT = "select"
    MODE_PAN = "pan"

    def __init__(self, parent=None):
        """Initialize the visualization widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculator = PolygonalNumbersCalculator()
        self.show_grid = False  # Default to False to match the checkbox state
        self.show_labels = True
        self.show_layers = True
        self.show_dot_numbers = False  # New option for showing number labels on dots
        self.zoom_level = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.dot_size = 10.0

        # Selection mode and state
        self.selection_mode = self.MODE_SELECT  # Current interaction mode
        self.selected_dots = []  # List of selected dot indices
        self.connections = []  # List of tuples (dot1, dot2) representing connected dots
        self.show_connections = False  # Whether to show connections between dots (off by default)

        # Selection rectangle for multi-select
        self.selection_rect_active = False
        self.selection_rect_start = None
        self.selection_rect_current = None

        # For selection groups
        self.selection_groups = {}  # Dict of {group_name: [dot_ids]}
        self.current_group = "Default"  # Current active group
        self.selection_groups[self.current_group] = []  # Initialize default group
        self.show_only_active_group = False  # Whether to show only the active group

        # Group colors - add a default color palette
        self.group_colors = {
            "": QColor(255, 255, 0),         # Yellow for default selection
            "Default": QColor(255, 215, 0),  # Gold
            "Group 1": QColor(0, 120, 215),  # Blue
            "Group 2": QColor(0, 180, 0),    # Green
            "Group 3": QColor(215, 0, 120),  # Purple/Magenta
            "Group 4": QColor(255, 120, 0),  # Orange
            "Group 5": QColor(120, 0, 215),  # Violet
        }

        # Layer colors - colors for different layers/gnomons
        self.layer_colors = {}  # Will be populated dynamically
        self.color_scheme = "rainbow"  # Default color scheme: rainbow, pastel, monochrome, custom
        self._generate_layer_colors()

        # Last selection for undo
        self.last_selection = []

        # Screen positions of dots for hit detection (updated during paintEvent)
        self.dot_positions = {}  # Maps dot number to (screen_x, screen_y)

        # Debug control
        self._debug_output = False  # Set to True to enable debug output
        self._last_output_time = 0  # Last time debug output was printed
        self._selection_changed = False  # Flag to indicate selection changed

        # Mouse tracking for dragging
        self.setMouseTracking(True)
        self.dragging = False
        self.last_mouse_pos = None

        # Set minimum size for better visualization
        self.setMinimumSize(400, 400)

        # Set maximum size to prevent overflow
        self.setMaximumWidth(650)

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(240, 240, 240))
        self.setPalette(palette)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Set focus policy to enable keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Calculated positions for dots
        self.dot_positions = {}  # dot_index -> (x, y) position
        self.update_dot_positions()

        # Hover state
        self.hover_dot = None  # Index of dot being hovered over

    def set_calculator(self, calculator: PolygonalNumbersCalculator) -> None:
        """Set the calculator for the visualization.

        Args:
            calculator: Polygonal numbers calculator
        """
        self.calculator = calculator
        self.update()

    def toggle_grid(self, show: bool) -> None:
        """Toggle grid visibility.

        Args:
            show: Whether to show the grid
        """
        self.show_grid = show
        self.update()

    def toggle_labels(self, show: bool) -> None:
        """Toggle label visibility.

        Args:
            show: Whether to show labels
        """
        self.show_labels = show
        self.update()

    def toggle_layers(self, show: bool) -> None:
        """Toggle layer coloring.

        Args:
            show: Whether to show different layers with different colors
        """
        self.show_layers = show
        self.update()

    def toggle_dot_numbers(self, show: bool) -> None:
        """Toggle dot number labels.

        Args:
            show: Whether to show number labels on dots
        """
        self.show_dot_numbers = show
        self.update()

    def set_zoom(self, zoom: float) -> None:
        """Set the zoom level.

        Args:
            zoom: Zoom level (1.0 = 100%)
        """
        self.zoom_level = max(0.1, min(5.0, zoom))
        self.update()

    def set_pan(self, x: float, y: float) -> None:
        """Set the pan position.

        Args:
            x: Horizontal pan
            y: Vertical pan
        """
        self.pan_x = x
        self.pan_y = y
        self.update()

    def set_dot_size(self, size: float) -> None:
        """Set the dot size.

        Args:
            size: Size of dots
        """
        self.dot_size = max(2.0, min(20.0, size))
        self.update()

    def set_selection_mode(self, enabled: bool) -> None:
        """Toggle between selection mode and pan mode.

        Args:
            enabled: True for selection mode, False for pan mode
        """
        self.selection_mode = self.MODE_SELECT if enabled else self.MODE_PAN
        # Set cursor based on mode
        if enabled:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.update()

    def toggle_connections(self, show: bool) -> None:
        """Toggle the visibility of connections between dots.

        Args:
            show: Whether to show connections
        """
        self.show_connections = show
        self.update()

    def clear_selections(self) -> None:
        """Clear all selected dots and connections."""
        # Always store current selection for undo, even if empty
        self.last_selection = self.selected_dots.copy()

        # Only proceed with clearing if there's something to clear
        if self.selected_dots or self.connections:
            self._selection_changed = True
            self.selected_dots = []
            self.connections = []

            # Also clear the current selection group
            if self.current_group in self.selection_groups:
                self.selection_groups[self.current_group] = []

            # Force a redraw
            self.update()

            # Emit signal to notify listeners
            self.selection_changed.emit(self.selected_dots)

            # Debug output
            self._debug_print("Cleared all selections")

    def undo_selection(self) -> None:
        """Restore the last selection state."""
        if self.last_selection:
            self._selection_changed = True
            self.selected_dots = self.last_selection.copy()
            self.selection_groups[self.current_group] = self.selected_dots.copy()
            self.last_selection = []
            self.update()

            # Emit signal
            self.selection_changed.emit(self.selected_dots)

            self._debug_print(f"Restored selection: {self.selected_dots}")

    def add_connection(self, dot1: int, dot2: int) -> None:
        """Add a connection between two dots.

        Args:
            dot1: Index of first dot (1-based)
            dot2: Index of second dot (1-based)
        """
        # Don't add duplicate connections
        if (dot1, dot2) not in self.connections and (dot2, dot1) not in self.connections:
            self.connections.append((dot1, dot2))
            self.update()

    def connect_selected_dots(self) -> None:
        """Connect all selected dots in order of selection."""
        if len(self.selected_dots) < 2:
            return

        # Connect dots in order of selection
        for i in range(len(self.selected_dots) - 1):
            dot1 = self.selected_dots[i]
            dot2 = self.selected_dots[i + 1]
            self.add_connection(dot1, dot2)

        # Optionally connect last dot to first to close the shape
        # Uncomment if you want this behavior
        # if len(self.selected_dots) > 2:
        #     self.add_connection(self.selected_dots[-1], self.selected_dots[0])

    def close_polygon(self) -> None:
        """Close the polygon by connecting the last selected dot to the first."""
        if len(self.selected_dots) > 2:
            self.add_connection(self.selected_dots[-1], self.selected_dots[0])
            self.update()

    def set_selection_group(self, group_name: str) -> None:
        """Set the current selection group.

        Args:
            group_name: Name of the selection group to set
        """
        # Create the group if it doesn't exist
        if group_name not in self.selection_groups:
            self.selection_groups[group_name] = []

        # Change to the selected group
        self.current_group = group_name

        # Change the current selection to match the group
        self.selected_dots = self.selection_groups[group_name].copy()
        self._selection_changed = True
        self._debug_print(f"Changed to group '{group_name}' with {len(self.selected_dots)} dots")

        # Update the display
        self.selection_changed.emit(self.selected_dots)
        self.update()

    def get_selection_groups(self) -> Dict[str, List[int]]:
        """Get all selection groups.

        Returns:
            Dictionary of group names to lists of dot indices
        """
        return self.selection_groups

    def get_selected_sum(self) -> int:
        """Calculate the sum of selected dot numbers.

        Returns:
            Sum of the selected dot numbers
        """
        # Dots are numbered 1-based, and the value is the same as the dot number
        if not self.selected_dots:
            return 0

        # We need to sum the actual dot numbers
        total = sum(self.selected_dots)

        # Only debug log when selection changes
        if self._selection_changed:
            self._debug_print(f"Calculating sum of {self.selected_dots} = {total}")
            self._selection_changed = False

        return total

    def get_selected_count(self) -> int:
        """Get the count of selected dots.

        Returns:
            Number of selected dots
        """
        return len(self.selected_dots)

    def get_selected_dots(self) -> list:
        """Get the current list of selected dots.

        Returns:
            List of selected dot indices
        """
        return self.selected_dots.copy()

    def get_dot_positions(self) -> Dict[int, Tuple[float, float]]:
        """Get the screen positions of all dots.

        Returns:
            Dictionary mapping dot indices to (x, y) screen coordinates
        """
        return self.dot_positions.copy()

    def select_dots_by_indices(self, indices: List[int], replace: bool = True) -> None:
        """Select dots by their indices.

        Args:
            indices: List of dot indices to select
            replace: Whether to replace the current selection (True) or add to it (False)
        """
        # Store current selection for undo
        self.last_selection = self.selected_dots.copy()

        # Clear current selection if replacing
        if replace:
            self.selected_dots = []

        # Add new dots, avoiding duplicates
        valid_indices = []
        for idx in indices:
            if idx in self.dot_positions and idx not in self.selected_dots:
                self.selected_dots.append(idx)
                valid_indices.append(idx)

        # Sort for consistent selection order
        self.selected_dots.sort()

        # Update the current selection group
        if self.current_group in self.selection_groups:
            if replace:
                self.selection_groups[self.current_group] = self.selected_dots.copy()
            else:
                # Add to existing group
                for idx in valid_indices:
                    if idx not in self.selection_groups[self.current_group]:
                        self.selection_groups[self.current_group].append(idx)
                self.selection_groups[self.current_group].sort()

        # Set the selection changed flag
        self._selection_changed = True

        # Update the display
        self.update()

        # Signal that the selection has changed
        self.selection_changed.emit(self.selected_dots)

        # Update the selection status in the control panel
        if hasattr(self.parent(), 'controls'):
            ctrl = self.parent().controls
            if hasattr(ctrl, 'selection_status_label'):
                ctrl.selection_status_label.setText(f"Selected: {len(self.selected_dots)} dots")

        # Debug output
        self._debug_print(f"Selected {len(valid_indices)} dots, total: {len(self.selected_dots)}")

    def select_dots_by_layer(self, layer: int) -> None:
        """Select all dots in a specific layer.

        Args:
            layer: Layer number to select (1-indexed from UI)
        """
        # Convert from 1-indexed (UI) to 0-indexed (calculator) if needed
        calculator_layer = layer

        # Get all coordinates from the calculator
        all_coordinates = self.calculator.get_coordinates()

        # Check if this is a centered polygonal number
        # For centered polygonal numbers, layer 0 is the center dot
        # For regular polygonal numbers, layers start at 1
        has_center_dot = False
        for coord in all_coordinates:
            if coord[2] == 0:  # Layer 0 exists
                has_center_dot = True
                break

        # Debug output
        self._debug_print(f"Selecting layer {layer} (UI), has center dot: {has_center_dot}")

        # If this is a centered polygonal number, adjust the layer
        if has_center_dot:
            # UI layer 1 corresponds to calculator layer 0
            calculator_layer = layer - 1
            self._debug_print(f"Adjusted to calculator layer {calculator_layer}")

        # Collect all dots in the given layer
        indices = []
        dot_layers = {coord[3]: coord[2] for coord in all_coordinates}

        for dot_idx, _ in self.dot_positions.items():
            if dot_idx in dot_layers and dot_layers[dot_idx] == calculator_layer:
                indices.append(dot_idx)

        if indices:
            self.select_dots_by_indices(indices)
            self._debug_print(f"Selected {len(indices)} dots in layer {layer} (UI) / {calculator_layer} (calculator)")
        else:
            self._debug_print(f"No dots found in layer {layer} (UI) / {calculator_layer} (calculator)")

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle paint events for the visualization.

        Args:
            event: The paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set clipping to ensure drawing stays within widget boundaries
        painter.setClipRect(self.rect())

        # Fill background
        painter.fillRect(event.rect(), QColor(240, 240, 240))

        # Update dot positions if needed
        self.update_dot_positions()

        # Draw coordinate grid
        self._draw_grid(painter)

        # Draw selection groups (behind dots)
        for group_name, dots in self.selection_groups.items():
            # Skip empty group name or empty groups
            if not group_name or not dots:
                continue

            # If show_only_active_group is enabled, only draw the current group
            if self.show_only_active_group and group_name != self.current_group:
                continue

            # Get or create color for this group
            if group_name not in self.group_colors:
                # Generate a new color
                hue = random.random()
                rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
                self.group_colors[group_name] = QColor(
                    int(rgb[0] * 255),
                    int(rgb[1] * 255),
                    int(rgb[2] * 255),
                    200  # Alpha
                )

            color = self.group_colors[group_name]

            # Make the current group more prominent
            if group_name == self.current_group:
                # Use a more opaque version of the color for the active group
                active_color = QColor(color)
                active_color.setAlpha(240)  # More opaque

                # Draw selections for the active group with a more prominent color
                self._draw_selections(painter, dots, active_color)
            else:
                # Draw selections for other groups with normal color
                self._draw_selections(painter, dots, color)

        # Draw dots
        self._draw_dots(painter)

        # Draw connections (if any)
        self._draw_connections(painter)

        # Draw current selection (on top of everything)
        # Only draw the current selection if it's not already shown as part of the active group
        # or if we're not in show_only_active_group mode
        if self.selected_dots and (not self.show_only_active_group or
                                  self.selected_dots != self.selection_groups.get(self.current_group, [])):
            self._draw_selections(painter, self.selected_dots, self.group_colors[""])

        # Draw hover effect
        if self.hover_dot is not None:
            self._draw_hover(painter, self.hover_dot)

        painter.end()

    def _draw_grid(self, painter: QPainter) -> None:
        """Draw the coordinate grid.

        Args:
            painter: The QPainter to use
        """
        # Get visible area
        viewport_width = self.width()
        viewport_height = self.height()

        # Calculate center coordinates
        center_x = viewport_width / 2 + self.pan_x
        center_y = viewport_height / 2 + self.pan_y

        # Always draw the axes, regardless of grid visibility
        axes_pen = QPen(QColor(100, 100, 100))
        axes_pen.setWidth(2)
        painter.setPen(axes_pen)

        # Draw x-axis
        painter.drawLine(0, int(center_y), viewport_width, int(center_y))

        # Draw y-axis
        painter.drawLine(int(center_x), 0, int(center_x), viewport_height)

        # Only draw the grid if show_grid is True
        if self.show_grid:
            # Set up pen for grid lines
            grid_pen = QPen(QColor(200, 200, 200))
            grid_pen.setWidth(1)
            painter.setPen(grid_pen)

            # Draw horizontal grid lines
            y = center_y % self.dot_size
            while y < viewport_height:
                painter.drawLine(0, int(y), viewport_width, int(y))
                y += self.dot_size

            # Draw vertical grid lines
            x = center_x % self.dot_size
            while x < viewport_width:
                painter.drawLine(int(x), 0, int(x), viewport_height)
                x += self.dot_size

    def _draw_dots(self, painter: QPainter) -> None:
        """Draw all dots in the visualization.

        Args:
            painter: The QPainter to use
        """
        # Set up pen for dots
        dot_pen = QPen(Qt.PenStyle.NoPen)
        painter.setPen(dot_pen)

        # Get layer information for each dot
        dot_layers = {}
        for x, y, layer, dot_number in self.calculator.get_coordinates():
            if dot_number > 0:  # Skip non-numeric positions
                dot_layers[dot_number] = layer

        # Draw each dot
        for dot_idx, (x, y) in self.dot_positions.items():
            # Skip if out of view
            if (x < -self.dot_size / 2 or x > self.width() + self.dot_size / 2 or
                y < -self.dot_size / 2 or y > self.height() + self.dot_size / 2):
                continue

            # Determine dot color based on layer
            if self.show_layers and dot_idx in dot_layers:
                layer = dot_layers[dot_idx]
                # Use layer color if available, otherwise generate one
                if layer not in self.layer_colors:
                    self._generate_layer_color(layer)
                dot_color = self.layer_colors[layer]
            else:
                # Default color if not showing layers or layer info not available
                dot_color = QColor(50, 50, 50)

            # Set brush for this dot
            painter.setBrush(QBrush(dot_color))

            # Draw the dot
            painter.drawEllipse(QPointF(x, y), self.dot_size / 2, self.dot_size / 2)

            # Draw dot number if enabled or zoomed in enough
            if self.show_dot_numbers or self.zoom_level > 20:
                # Use contrasting text color based on dot color brightness
                if dot_color.lightness() > 128:
                    text_color = QColor(0, 0, 0)  # Black text on light background
                else:
                    text_color = QColor(255, 255, 255)  # White text on dark background

                # Set up font for dot numbers
                number_font = QFont()
                number_font.setPointSize(max(8, int(self.dot_size / 2)))  # Scale font with dot size
                painter.setFont(number_font)

                # Get text metrics to center the text
                text = str(dot_idx)
                metrics = painter.fontMetrics()
                text_width = metrics.horizontalAdvance(text)
                text_height = metrics.height()

                # Calculate centered position
                text_x = x - text_width / 2
                text_y = y + text_height / 4  # Slight vertical adjustment for better centering

                # Draw text with a small outline for better visibility
                text_pen = QPen(text_color)
                painter.setPen(text_pen)
                painter.drawText(QPointF(text_x, text_y), text)
                painter.setPen(dot_pen)  # Reset to dot pen

    def _draw_selections(self, painter: QPainter, dots: List[int], color: QColor) -> None:
        """Draw selection indicators for the given dots.

        Args:
            painter: The QPainter to use
            dots: List of dot indices to highlight
            color: Color to use for highlighting
        """
        # Check if this is the active group
        is_active_group = dots == self.selection_groups.get(self.current_group, [])

        # Set up pen for selection circles
        selection_pen = QPen(color)
        selection_pen.setWidth(3 if is_active_group else 2)  # Thicker line for active group
        painter.setPen(selection_pen)

        # For active group, use a semi-transparent fill to make it more distinct
        if is_active_group and self.show_only_active_group:
            # Create a more transparent version of the color for the fill
            fill_color = QColor(color)
            fill_color.setAlpha(40)  # Very transparent
            painter.setBrush(QBrush(fill_color))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)

        # Draw selection circle around each selected dot
        selection_radius = self.dot_size * (1.3 if is_active_group else 1.25)  # Slightly larger for active group
        for dot_idx in dots:
            if dot_idx in self.dot_positions:
                x, y = self.dot_positions[dot_idx]
                painter.drawEllipse(QPointF(x, y), selection_radius, selection_radius)

    def _draw_hover(self, painter: QPainter, dot_idx: int) -> None:
        """Draw hover effect for the given dot.

        Args:
            painter: The QPainter to use
            dot_idx: Index of the dot to highlight
        """
        if dot_idx in self.dot_positions:
            # Set up pen for hover effect
            hover_pen = QPen(QColor(0, 150, 255))
            hover_pen.setWidth(1)
            painter.setPen(hover_pen)
            painter.setBrush(QBrush(QColor(200, 230, 255, 100)))

            # Draw hover circle
            x, y = self.dot_positions[dot_idx]
            hover_radius = self.dot_size * 1.5
            painter.drawEllipse(QPointF(x, y), hover_radius, hover_radius)

    def _draw_connections(self, painter: QPainter) -> None:
        """Draw connections between selected dots.

        Args:
            painter: The QPainter to use
        """
        # Only show connections if:
        # 1. The show_connections flag is enabled
        # 2. Multiple dots are selected
        if not self.show_connections or len(self.selected_dots) < 2:
            return

        # Set up pen for connections
        connection_pen = QPen(QColor(100, 100, 255, 150))
        connection_pen.setWidth(2)
        painter.setPen(connection_pen)

        # Draw lines between consecutive dots
        path = QPainterPath()

        # Start at the first selected dot
        first_dot = self.selected_dots[0]
        if first_dot in self.dot_positions:
            x, y = self.dot_positions[first_dot]
            path.moveTo(x, y)

            # Connect to each subsequent dot
            for dot_idx in self.selected_dots[1:]:
                if dot_idx in self.dot_positions:
                    x, y = self.dot_positions[dot_idx]
                    path.lineTo(x, y)

            # Draw the connection path
            painter.drawPath(path)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events for selection and panning.

        Args:
            event: The mouse event
        """
        self.dragging = True
        self.last_mouse_pos = event.position()

        if self.selection_mode == self.MODE_SELECT:
            # Try to select a dot
            clicked_dot = self._find_dot_at_position(event.position())

            if clicked_dot is not None:
                # Store current selection for undo
                self.last_selection = self.selected_dots.copy()

                # Handle different selection behaviors
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    # Ctrl+click: Toggle selection
                    if clicked_dot in self.selected_dots:
                        self.selected_dots.remove(clicked_dot)
                    else:
                        self.selected_dots.append(clicked_dot)
                elif event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    # Shift+click: Add to selection
                    if clicked_dot not in self.selected_dots:
                        self.selected_dots.append(clicked_dot)
                else:
                    # Regular click: Replace selection
                    self.selected_dots = [clicked_dot]

                # Sort for consistent display
                self.selected_dots.sort()

                # Update display
                self.update()

                # Emit selection changed signal
                self.selection_changed.emit(self.selected_dots)
            else:
                # Clicked on empty space, clear selection unless modifier key is pressed
                if not (event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)):
                    # Store current selection for undo
                    self.last_selection = self.selected_dots.copy()

                    # Clear selection
                    self.selected_dots = []

                    # Update display
                    self.update()

                    # Emit selection changed signal
                    self.selection_changed.emit(self.selected_dots)

        # Accept the event
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events for panning and hover effects.

        Args:
            event: The mouse event
        """
        if self.dragging:
            if self.selection_mode == self.MODE_PAN:
                # Pan the view
                delta = event.position() - self.last_mouse_pos
                self.pan_x += delta.x()
                self.pan_y += delta.y()

                # Update the view
                self.update()

            self.last_mouse_pos = event.position()
        else:
            # Handle hover effect
            hover_dot = self._find_dot_at_position(event.position())

            if hover_dot != self.hover_dot:
                self.hover_dot = hover_dot
                self.update()  # Redraw with new hover effect

                # Show tooltip with dot information
                if hover_dot is not None:
                    QToolTip.showText(
                        event.globalPosition().toPoint(),
                        f"Dot: {hover_dot}",
                        self
                    )

        # Accept the event
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events.

        Args:
            event: The mouse event
        """
        self.dragging = False

        # Accept the event
        event.accept()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle wheel events for zooming.

        Args:
            event: The wheel event
        """
        # Get mouse position
        mouse_pos = event.position()

        # Calculate old world coordinates of the mouse
        old_world_x = (mouse_pos.x() - self.width() / 2 - self.pan_x) / self.dot_size
        old_world_y = (mouse_pos.y() - self.height() / 2 - self.pan_y) / self.dot_size

        # Adjust scale factor
        zoom_factor = 1.1
        if event.angleDelta().y() > 0:
            # Zoom in
            self.zoom_level *= zoom_factor
            self.dot_size *= zoom_factor**0.5  # Scale dot size more slowly
        else:
            # Zoom out
            self.zoom_level /= zoom_factor
            self.dot_size /= zoom_factor**0.5  # Scale dot size more slowly

        # Enforce minimum and maximum scale
        self.zoom_level = max(0.5, min(5.0, self.zoom_level))
        self.dot_size = max(2.0, min(20.0, self.dot_size))

        # Calculate new world coordinates of the mouse
        new_world_x = (mouse_pos.x() - self.width() / 2 - self.pan_x) / self.dot_size
        new_world_y = (mouse_pos.y() - self.height() / 2 - self.pan_y) / self.dot_size

        # Adjust pan to keep mouse point fixed
        self.pan_x += (new_world_x - old_world_x) * self.dot_size
        self.pan_y += (new_world_y - old_world_y) * self.dot_size

        # Update the display
        self.update()

        # Accept the event
        event.accept()

    def _calculate_scale_factor(self, coordinates: List[Tuple[float, float, int, int]]) -> float:
        """Calculate an appropriate scale factor based on the coordinates.

        Args:
            coordinates: List of (x, y, layer, dot_number) coordinates

        Returns:
            Scale factor for rendering
        """
        if not coordinates:
            return 30.0

        # Find the maximum distance from origin
        max_distance = 0.0
        for x, y, _, _ in coordinates:
            distance = math.sqrt(x * x + y * y)
            max_distance = max(max_distance, distance)

        # Calculate scale factor to fit within the widget
        # Use the smaller dimension of the widget
        widget_size = min(self.width(), self.height()) - 40  # Leave some margin

        # Avoid division by zero
        if max_distance < 0.001:
            return 30.0

        return widget_size / (2 * max_distance)

    def _draw_labels(self, painter: QPainter) -> None:
        """Draw title and formula labels.

        Args:
            painter: QPainter object
        """
        # Set up font
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)

        formula_font = QFont()
        formula_font.setPointSize(10)

        # Draw title
        painter.setFont(title_font)
        painter.setPen(QColor(0, 0, 0))
        title_text = self.calculator.get_polygonal_name() + f" Number: {self.calculator.calculate_value()}"
        painter.drawText(10, 25, title_text)

        # Draw formula
        painter.setFont(formula_font)
        formula_text = self.calculator.get_formula_string()
        painter.drawText(10, 50, formula_text)

        # Draw index
        index_text = f"Index: {self.calculator.index}"
        painter.drawText(10, 75, index_text)

        # No longer showing dot count information

        # Draw drag hint
        hint_font = QFont()
        hint_font.setPointSize(8)
        hint_font.setItalic(True)
        painter.setFont(hint_font)
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(10, 125, "Drag to pan, scroll to zoom")

    def _find_dot_at_position(self, pos: QPointF) -> Optional[int]:
        """Find the dot at the given position.

        Args:
            pos: The position to check

        Returns:
            The index of the dot at the position, or None if no dot is found
        """
        # Check each dot
        for dot_idx, (x, y) in self.dot_positions.items():
            # Calculate squared distance to dot center
            dist_sq = (pos.x() - x) ** 2 + (pos.y() - y) ** 2

            # Check if within dot radius (with some extra margin for easier selection)
            selection_radius = self.dot_size
            if dist_sq <= selection_radius ** 2:
                return dot_idx

        # No dot found
        return None

    def _debug_print(self, message: str) -> None:
        """Print debug message with rate limiting to avoid console spam.

        Args:
            message: Message to print
        """
        # Check if debug output is enabled (default to False if not set)
        if not hasattr(self, '_debug_output') or not self._debug_output:
            return

        import time
        current_time = time.time()

        # Initialize _last_output_time if not set
        if not hasattr(self, '_last_output_time'):
            self._last_output_time = 0

        # Only print at most once per second
        if current_time - self._last_output_time > 1.0:
            logger = logging.getLogger(__name__)
            logger.debug(f"[PolygonalNumbersVisualization] {message}")
            # Also print to console for immediate feedback
            print(f"[PolygonalNumbersVisualization] {message}")
            self._last_output_time = current_time

    def keyPressEvent(self, event) -> None:
        """Handle key press events for navigation and selection operations.

        Args:
            event: Key event
        """
        # Arrow keys for panning
        if event.key() == Qt.Key.Key_Left:
            self.pan_x += 20
            self.update()
        elif event.key() == Qt.Key.Key_Right:
            self.pan_x -= 20
            self.update()
        elif event.key() == Qt.Key.Key_Up:
            self.pan_y += 20
            self.update()
        elif event.key() == Qt.Key.Key_Down:
            self.pan_y -= 20
            self.update()
        # Plus/minus for zooming
        elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            self.zoom_level *= 1.1
            self.zoom_level = min(5.0, self.zoom_level)
            self.update()
        elif event.key() == Qt.Key.Key_Minus:
            self.zoom_level /= 1.1
            self.zoom_level = max(0.1, self.zoom_level)
            self.update()
        # Space to reset view
        elif event.key() == Qt.Key.Key_Space:
            self.pan_x = 0.0
            self.pan_y = 0.0
            self.zoom_level = 1.0
            self.update()
        # Selection operations
        elif event.key() == Qt.Key.Key_A and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+A to select all dots
            all_dots = list(self.dot_positions.keys())
            self.select_dots_by_indices(all_dots)
        elif event.key() == Qt.Key.Key_Z and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+Z to undo selection
            self.undo_selection()
        elif event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+C to close the polygon
            self.close_polygon()
        elif event.key() == Qt.Key.Key_Escape:
            # Esc to clear selection
            self.clear_selections()
        elif event.key() == Qt.Key.Key_S and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+S to toggle selection mode
            self.set_selection_mode(not self.selection_mode)
        else:
            # Pass unhandled keys to parent
            super().keyPressEvent(event)

    def set_group_color(self, group_name: str, color: QColor) -> None:
        """Set the display color for a group.

        Args:
            group_name: Name of the group
            color: Color to use for the group
        """
        self.group_colors[group_name] = color
        self.update()

    def get_group_color(self, group_name: str) -> QColor:
        """Get the display color for a group.

        Returns:
            Color used for the group
        """
        # Return the color if defined, or generate a new one if not
        if group_name in self.group_colors:
            return self.group_colors[group_name]
        else:
            # Generate a color based on the hash of the group name
            hue = hash(group_name) % 360
            return QColor.fromHsv(hue, 200, 220)

    def _generate_layer_colors(self) -> None:
        """Generate colors for all layers based on the current color scheme."""
        # Clear existing colors
        self.layer_colors = {}

        # Get all unique layers from the calculator
        layers = set()
        for _, _, layer, _ in self.calculator.get_coordinates():
            layers.add(layer)

        # Generate colors for each layer
        for layer in layers:
            self._generate_layer_color(layer)

    def _generate_layer_color(self, layer: int) -> None:
        """Generate a color for a specific layer based on the current color scheme.

        Args:
            layer: Layer number to generate color for
        """
        if layer in self.layer_colors:
            return  # Color already exists

        if self.color_scheme == "rainbow":
            # Rainbow colors - evenly distributed hues
            hue = (layer * 137.5) % 360  # Golden angle to get good distribution
            saturation = 200 + (layer % 3) * 20  # Slight variation in saturation
            value = 200 + (layer % 2) * 30  # Slight variation in value
            self.layer_colors[layer] = QColor.fromHsv(int(hue), saturation, value)

        elif self.color_scheme == "pastel":
            # Pastel colors - high value, low saturation
            hue = (layer * 137.5) % 360
            saturation = 100 + (layer % 5) * 20
            value = 220 + (layer % 3) * 10
            self.layer_colors[layer] = QColor.fromHsv(int(hue), saturation, value)

        elif self.color_scheme == "monochrome":
            # Monochrome - single hue, varying saturation and value
            base_hue = 210  # Blue
            saturation = 150 + (layer % 3) * 30
            value = 150 + (layer * 10) % 100
            self.layer_colors[layer] = QColor.fromHsv(base_hue, saturation, value)

        elif self.color_scheme == "custom":
            # Custom colors - defined by the user
            # For now, fall back to rainbow
            hue = (layer * 137.5) % 360
            saturation = 200 + (layer % 3) * 20
            value = 200 + (layer % 2) * 30
            self.layer_colors[layer] = QColor.fromHsv(int(hue), saturation, value)

    def set_color_scheme(self, scheme: str) -> None:
        """Set the color scheme for layers.

        Args:
            scheme: Color scheme name ("rainbow", "pastel", "monochrome", "custom")
        """
        if scheme in ["rainbow", "pastel", "monochrome", "custom"]:
            self.color_scheme = scheme
            self._generate_layer_colors()
            self.update()

    def perform_group_operation(self, operation: str, groups: list, result_group: str = None) -> None:
        """Perform set operations between multiple groups.

        Args:
            operation: The operation to perform ('union', 'intersection', 'difference', 'symmetric_difference')
            groups: List of group names to operate on
            result_group: Name of the group to store the result (if None, a name will be generated)
        """
        # Validate groups
        if not groups:
            self._debug_print("No groups provided for operation")
            return

        # Check if all groups exist
        missing_groups = [g for g in groups if g not in self.selection_groups]
        if missing_groups:
            self._debug_print(f"Cannot perform operation - groups do not exist: {missing_groups}")
            return

        # Generate a default result group name if not provided
        if not result_group:
            # Create a name based on the operation and groups
            op_symbol = {
                'union': '∪',
                'intersection': '∩',
                'difference': '−',
                'symmetric_difference': '⊕'
            }.get(operation, operation)

            # Limit the number of groups in the name to keep it reasonable
            group_names = groups[:3]
            if len(groups) > 3:
                group_names.append("...")

            result_group = f"{op_symbol}({', '.join(group_names)})"

            # Ensure the name is unique
            base_name = result_group
            counter = 1
            while result_group in self.selection_groups:
                result_group = f"{base_name}_{counter}"
                counter += 1

        # Get the dot sets for each group
        group_dots = [set(self.selection_groups[g]) for g in groups]

        if not group_dots:
            self._debug_print("No valid groups to operate on")
            return

        # Perform the requested operation
        if operation == 'union':
            # Union of all groups
            result = set().union(*group_dots)
            self._debug_print(f"Union of {len(groups)} groups = {len(result)} dots")

        elif operation == 'intersection':
            # Intersection of all groups
            if group_dots:
                result = group_dots[0].copy()
                for dots in group_dots[1:]:
                    result &= dots
                self._debug_print(f"Intersection of {len(groups)} groups = {len(result)} dots")
            else:
                result = set()
                self._debug_print("No groups to intersect")

        elif operation == 'difference':
            # Difference: First group minus all others
            if group_dots:
                result = group_dots[0].copy()
                for dots in group_dots[1:]:
                    result -= dots
                self._debug_print(f"Difference: {groups[0]} minus {len(groups)-1} other groups = {len(result)} dots")
            else:
                result = set()
                self._debug_print("No groups for difference operation")

        elif operation == 'symmetric_difference':
            # Symmetric difference of all groups
            result = set()
            # Count occurrences of each dot across all groups
            dot_counts = {}
            for dots in group_dots:
                for dot in dots:
                    dot_counts[dot] = dot_counts.get(dot, 0) + 1

            # Keep dots that appear an odd number of times
            result = {dot for dot, count in dot_counts.items() if count % 2 == 1}
            self._debug_print(f"Symmetric difference of {len(groups)} groups = {len(result)} dots")

        else:
            self._debug_print(f"Unknown operation: {operation}")
            return

        # Store the result in the result group
        self.selection_groups[result_group] = list(result)

        # If the result group is the current group, update the selection
        if result_group == self.current_group:
            self.selected_dots = list(result)
            self._selection_changed = True
            self.selection_changed.emit(self.selected_dots)

        # Update the display
        self.update()

    def create_preset_selection(self, preset_type: str, params: Dict = None) -> List[int]:
        """Create a selection based on a preset pattern.

        Args:
            preset_type: The type of preset ("primes", "even", "odd", etc.)
            params: Additional parameters for the preset

        Returns:
            List of dot indices in the selection
        """
        if params is None:
            params = {}

        result = []
        all_dots = list(self.dot_positions.keys())

        # Make sure we have dots to work with
        if not all_dots:
            self._debug_print("No dots available for pattern selection")
            return []

        max_dot = max(all_dots)
        self._debug_print(f"Creating preset selection of type '{preset_type}' with {len(all_dots)} dots (max: {max_dot})")

        if preset_type == "primes":
            # Select prime numbers
            result = [i for i in all_dots if self._is_prime(i)]
            self._debug_print(f"Found {len(result)} prime numbers")

        elif preset_type == "even":
            # Select even numbers (divisible by 2)
            result = [i for i in all_dots if i % 2 == 0]
            self._debug_print(f"Found {len(result)} even numbers")

        elif preset_type == "odd":
            # Select odd numbers (not divisible by 2)
            result = [i for i in all_dots if i % 2 != 0]
            self._debug_print(f"Found {len(result)} odd numbers")

        elif preset_type == "divisible":
            # Select numbers divisible by n
            n = params.get('n', 2)
            result = [i for i in all_dots if i % n == 0]
            self._debug_print(f"Found {len(result)} numbers divisible by {n}")

        elif preset_type == "not_divisible":
            # Select numbers NOT divisible by n
            n = params.get('n', 2)
            result = [i for i in all_dots if i % n != 0]
            self._debug_print(f"Found {len(result)} numbers NOT divisible by {n}")

        elif preset_type == "fibonacci":
            # Select Fibonacci numbers
            fibs = self._generate_fibonacci(max_dot)
            result = [i for i in all_dots if i in fibs]
            self._debug_print(f"Found {len(result)} Fibonacci numbers")

        elif preset_type == "triangular":
            # Select triangular numbers (n*(n+1)/2)
            triangular_numbers = []
            n = 1
            while True:
                triangular = n * (n + 1) // 2
                if triangular > max_dot:
                    break
                triangular_numbers.append(triangular)
                n += 1

            result = [i for i in all_dots if i in triangular_numbers]
            self._debug_print(f"Found {len(result)} triangular numbers")

        elif preset_type == "square":
            # Select square numbers (n²)
            result = [i for i in all_dots if int(i**0.5)**2 == i]
            self._debug_print(f"Found {len(result)} square numbers")

        elif preset_type == "pentagonal":
            # Select pentagonal numbers (n*(3n-1)/2)
            pentagonal_numbers = []
            n = 1
            while True:
                pentagonal = n * (3*n - 1) // 2
                if pentagonal > max_dot:
                    break
                pentagonal_numbers.append(pentagonal)
                n += 1

            result = [i for i in all_dots if i in pentagonal_numbers]
            self._debug_print(f"Found {len(result)} pentagonal numbers")

        return result

    def _is_prime(self, n: int) -> bool:
        """Check if a number is prime.

        Args:
            n: The number to check

        Returns:
            True if the number is prime, False otherwise
        """
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        return True

    def _generate_fibonacci(self, n: int) -> List[int]:
        """Generate a list of Fibonacci numbers up to n.

        Args:
            n: The upper limit of the Fibonacci sequence

        Returns:
            List of Fibonacci numbers up to n
        """
        fibs = [0, 1]
        while fibs[-1] < n:
            fibs.append(fibs[-1] + fibs[-2])
        return fibs

    def update_dot_positions(self) -> None:
        """Calculate the positions of all dots based on the current view settings."""
        self.dot_positions = {}

        # Get all dots from the calculator
        coordinates = self.calculator.get_coordinates()

        for x, y, _, dot_number in coordinates:  # Ignore layer here, we only need position
            if dot_number > 0:  # Skip non-numeric positions
                # Convert grid coordinates to screen coordinates
                screen_x = self.width() / 2 + (x * self.dot_size * self.zoom_level) + self.pan_x
                screen_y = self.height() / 2 - (y * self.dot_size * self.zoom_level) + self.pan_y  # Flip y-axis

                # Store the position
                self.dot_positions[dot_number] = (screen_x, screen_y)
