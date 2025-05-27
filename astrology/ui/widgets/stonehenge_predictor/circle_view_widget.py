"""
Defines the CircleViewWidget for visualizing the Stonehenge Aubrey Holes in a heptagon shape.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-08-09
Dependencies: PyQt6
"""

import math
from typing import List, Optional

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
    QLinearGradient,
)
from PyQt6.QtWidgets import QSizePolicy, QWidget

from astrology.models.stonehenge_circle_config import NUM_HOLES


class CircleViewWidget(QWidget):
    """
    A widget that visually represents the 56 Aubrey Holes in a heptagon shape.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self._marker_positions: dict[str, int] = {}
        self._marker_colors: dict[str, QColor] = {
            "S": QColor("yellow"),
            "M": QColor("lightgray"),
            "N": QColor("cyan"),
            "N'": QColor("magenta"),
        }
        # Add zodiac position information for each marker
        self._marker_zodiac_positions: dict[str, str] = {
            "S": None,
            "M": None,
            "N": None,
            "N'": None,
        }
        # Track which markers should be visible
        self._visible_markers: dict[str, bool] = {
            "S": True,  # Sun initially visible
            "M": True,  # Moon initially visible
            "N": True,  # Node marker initially visible
            "N'": True, # Node marker initially visible
        }
        self._hole_positions_cache = []
        self._azimuth_offset_deg = 0.0  # Orientation of Hole 0 from North
        self._gc_azimuth_for_drawing: Optional[
            float
        ] = None  # Explicit GC azimuth for line drawing
        self._gc_zodiac_label: Optional[
            str
        ] = None  # Zodiac sign and degree for Galactic Center

        # Add zodiac data for all holes
        self._display_zodiac_degrees = True  # Flag to control visibility
        self._zodiac_signs = [
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
        ]
        self._hole_zodiac_positions = {}  # Will hold the zodiacal degree for each hole

        # Number of sides for the heptagon
        self._num_sides = 7

        # For maintaining aspect ratio
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # REMOVED: Cardinal point attributes have been removed as we're using a heptagon now

        # Add zoom and pan controls
        self._zoom_factor = 1.0
        self._min_zoom = 0.5
        self._max_zoom = 5.0
        self._zoom_step = 0.1

        # Pan/drag variables
        self._pan_offset_x = 0.0
        self._pan_offset_y = 0.0
        self._is_panning = False
        self._last_pan_pos = QPointF(0, 0)

        # Enable mouse tracking and make the widget focusable
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)

    def resizeEvent(self, event):
        """Handle widget resize events to maintain proper shape size and position."""
        super().resizeEvent(event)

        # Clear the hole positions cache so they will be recalculated for the new size
        self._hole_positions_cache = []

    def sizeHint(self):
        """Provide a preferred size that maintains a square aspect ratio."""
        return QSize(600, 600)

    def minimumSizeHint(self):
        """Provide a minimum size that ensures all elements are visible."""
        return QSize(400, 400)

    def set_orientation(self, azimuth_deg: float = 0.0):
        """
        Stores the Galactic Center azimuth for reference but maintains a fixed heptagon orientation.
        The heptagon remains in its default orientation, with the GC line aligned to the y-axis.

        Args:
            azimuth_deg (float): The azimuth is stored for reference but doesn't affect visual orientation.
        """
        # We don't change the orientation of the heptagon, but we store the azimuth
        # for reference and drawing the GC line along the y-axis
        self._azimuth_offset_deg = 0  # Fixed value - no rotation allowed
        self._gc_azimuth_for_drawing = azimuth_deg  # Store only for drawing reference
        self._hole_positions_cache = []  # Clear cache to force recalculation
        # Update zodiacal positions
        self._calculate_hole_zodiac_positions()
        self.update()

    def set_galactic_center_zodiac(self, zodiac_label: str):
        """
        Sets the zodiac label for the Galactic Center.

        Args:
            zodiac_label (str): The zodiac sign and degree (e.g. "Sagittarius 25.5°")
        """
        self._gc_zodiac_label = zodiac_label
        # Now calculate and update zodiacal positions for all holes
        self._calculate_hole_zodiac_positions()
        self.update()

    def update_marker_positions(self, positions: dict[str, int]):
        """
        Updates the positions of the markers to be drawn.

        Args:
            positions (dict[str, int]): A dictionary mapping marker names
                                        (e.g., 'S', 'M') to their hole numbers (0-55).
        """
        self._marker_positions = positions
        self.update()  # Trigger a repaint to show new marker positions

    def update_marker_zodiac_positions(self, zodiac_positions: dict[str, str]):
        """
        Updates the zodiac positions for each marker.

        Args:
            zodiac_positions (dict[str, str]): A dictionary mapping marker names
                                             (e.g., 'S', 'M') to zodiac positions
                                             (e.g., 'Leo 15.3°')
        """
        for marker, position in zodiac_positions.items():
            if marker in self._marker_zodiac_positions:
                self._marker_zodiac_positions[marker] = position
        self.update()  # Trigger a repaint

    # REMOVED: Cardinal point methods have been removed as we're using a heptagon now
    # Original methods were:
    # - set_cardinal_point_azimuths: Set azimuths for solstices/equinoxes
    # - set_cardinal_point_zodiac_labels: Set zodiac labels for cardinal points

    def _calculate_geometry(self, center):
        """
        Calculates the radius and hole radius based on widget size.
        Ensures the heptagon fits entirely within the visible area regardless of window size.

        Args:
            center (QPointF): The center point of the drawing
            
        Returns:
            tuple: (radius, hole_radius, square_size)
        """
        # Calculate the maximum possible radius that will fit in the widget
        padding = 40  # Increased padding to ensure labels fit
        size = min(self.width(), self.height()) - 2 * padding

        # Ensure we don't try to draw a negative-sized shape
        if size <= 0:
            size = max(200, min(self.width(), self.height()) - 20)

        radius = size / 2

        # Adjust hole radius proportionally to the heptagon size
        hole_radius = max(3.0, radius / 40) + 3.0
        
        # Calculate square size for holes - ensure squares don't overlap at vertices
        # We know there are 8 holes per side, so each square should be approximately
        # 1/8 of the side length, but slightly smaller to prevent overlap
        # For a regular heptagon, estimate the side length
        side_length = 2 * radius * math.sin(math.pi / 7)  # Side length of regular heptagon
        
        # Make squares slightly smaller than 1/8 of side length
        # This ensures squares touch at corners but don't overlap
        square_size = (side_length / 8) * 0.95  # Reduce size by 5% to prevent overlap

        return radius, hole_radius, square_size

    def _calculate_heptagon_points(
        self, center: QPointF, radius: float
    ) -> List[QPointF]:
        """
        Calculate the vertices of the heptagon with a fixed orientation.
        Places a flat edge at the bottom of the heptagon, with hole 28 at the center
        of that edge, aligned with the vertical y-axis.
        """
        points = []

        # For a regular polygon with a flat bottom edge, we need to start at the bottom-right vertex
        # and move counterclockwise
        num_sides = self._num_sides

        # Start angle is directly at the bottom of the circle (270 degrees)
        # and then adjusted to the right end of the flat bottom edge
        angle_per_side = 360.0 / num_sides
        start_angle = (
            270 - angle_per_side / 2
        )  # Bottom-right vertex of the flat bottom edge

        for i in range(num_sides):
            # Calculate angle, moving counterclockwise
            angle_rad = math.radians(start_angle + i * angle_per_side)

            # Calculate point position
            x = center.x() + radius * math.cos(angle_rad)
            y = center.y() + radius * math.sin(angle_rad)
            points.append(QPointF(x, y))

        return points

    def _calculate_hole_positions(self, center: QPointF, radius: float):
        """
        Pre-calculates and caches the QPointF for each of the 56 hole centers.
        Ensures that hole 28 (index 27) is positioned at the bottom center of the heptagon,
        aligned with the vertical y-axis.
        """
        if (
            not self._hole_positions_cache
            or len(self._hole_positions_cache) != NUM_HOLES
        ):
            self._hole_positions_cache = []

            # Get the heptagon vertices
            heptagon_points = self._calculate_heptagon_points(center, radius)

            # We want 8 holes per side of the heptagon (56/7 = 8)
            holes_per_side = NUM_HOLES // self._num_sides

            # For hole 28 (index 27) to be at the bottom center, it should be at the
            # middle of the bottom edge (side 0 in our heptagon construction)
            # The bottom edge contains indices 0 to 7, with the middle being at index 4
            # So hole 28 (index 27) should be at position 4 on side 0
            # Therefore: first_hole_of_bottom_edge = 28 - 4 = 24
            first_hole_of_bottom_edge = 24

            # Temporary storage for all hole positions
            temp_positions = [None] * NUM_HOLES

            # Place holes on each side of the heptagon
            for side_index in range(self._num_sides):
                # Get the vertices for this side
                start_vertex = heptagon_points[side_index]
                end_vertex = heptagon_points[(side_index + 1) % self._num_sides]

                # Place 8 holes evenly along this side
                for i in range(holes_per_side):
                    # Calculate position along this side (0 to 1)
                    # Modify t to ensure squares don't overlap at vertices
                    # Instead of evenly distributing across the full side, we'll use 95% of the side
                    # and distribute the holes within that space
                    t = (i + 0.5) / holes_per_side  # Base position (0.5 to center each hole)
                    
                    # Scale t to use only 95% of the side length to prevent vertex overlap
                    t = 0.025 + (t * 0.95)  # Shift slightly from start and end vertices
                    
                    # Calculate the coordinates of the hole
                    x = start_vertex.x() + t * (end_vertex.x() - start_vertex.x())
                    y = start_vertex.y() + t * (end_vertex.y() - start_vertex.y())

                    # Calculate which hole number goes at this position
                    hole_index = (
                        first_hole_of_bottom_edge + (side_index * holes_per_side) + i
                    ) % NUM_HOLES

                    # Store position for this hole
                    temp_positions[hole_index] = QPointF(x, y)

            # Set the cache to our calculated positions
            self._hole_positions_cache = temp_positions

        return self._hole_positions_cache

    def _calculate_hole_zodiac_positions(self):
        """
        Calculate zodiacal positions for all holes based on GC orientation.
        Assumes the Galactic Center is positioned between holes 28 and 29.
        """
        # Only proceed if we have the Galactic Center zodiac position
        if not self._gc_zodiac_label:
            return

        try:
            # Parse the GC zodiac position
            gc_sign, gc_degree_str = self._gc_zodiac_label.split(" ", 1)
            gc_degree = float(gc_degree_str.replace("°", ""))

            # Find the index of the GC sign in our zodiac signs list
            if gc_sign in self._zodiac_signs:
                gc_sign_index = self._zodiac_signs.index(gc_sign)
            else:
                # Default to Sagittarius (where GC is traditionally located)
                gc_sign_index = self._zodiac_signs.index("Sagittarius")
                gc_degree = 26.0  # Traditional GC position

            # Each hole represents 360/56 = ~6.43 degrees of the zodiac
            degrees_per_hole = 360 / NUM_HOLES
            # The half_hole_offset is applied directly in the calculation below (27.5 instead of 27)

            # Initialize dictionary to hold zodiacal position for each hole
            self._hole_zodiac_positions = {}

            # Calculate starting absolute degree (0-360 scale)
            # GC is between holes 28 and 29, so we need to adjust by half_hole_offset
            gc_absolute_degree = (gc_sign_index * 30) + gc_degree

            for hole_num in range(NUM_HOLES):
                # Calculate offset from the GC position (between holes 28 and 29)
                # The midpoint between holes 28-29 is at 27.5, so we use that as reference
                offset_holes = (hole_num - 27.5) % NUM_HOLES
                offset_degrees = offset_holes * degrees_per_hole

                # Calculate the absolute degree (0-360) for this hole
                # We subtract because we're going counterclockwise from GC position
                absolute_degree = (gc_absolute_degree - offset_degrees) % 360

                # Convert to zodiacal coordinates
                sign_index = int(absolute_degree / 30)
                degree_in_sign = absolute_degree % 30

                # Format as "Sign Degree°"
                sign = self._zodiac_signs[sign_index]
                self._hole_zodiac_positions[hole_num] = f"{sign} {degree_in_sign:.1f}°"

        except Exception as e:
            print(f"Error calculating hole zodiac positions: {e}")

    def toggle_zodiac_degrees_display(self, display: bool):
        """
        Toggle the display of zodiacal degrees for all holes.

        Args:
            display (bool): Whether to display zodiacal degrees
        """
        self._display_zodiac_degrees = display
        self.update()
        
    def toggle_nodes_visibility(self, visible: bool):
        """
        Toggle the visibility of Node markers (N and N').

        Args:
            visible (bool): Whether the node markers should be visible
        """
        self._visible_markers["N"] = visible
        self._visible_markers["N'"] = visible
        self.update()  # Trigger a repaint
        
    def toggle_sun_moon_visibility(self, visible: bool):
        """
        Toggle the visibility of Sun and Moon markers (S and M).

        Args:
            visible (bool): Whether the Sun and Moon markers should be visible
        """
        self._visible_markers["S"] = visible
        self._visible_markers["M"] = visible
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        """
        Handles the painting of the widget.
        Draws the Aubrey Holes on a heptagon, and markers.
        Applies zoom and pan transformations to the drawing.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate the center and radius based on the widget size
        widget_center = QPointF(self.width() / 2, self.height() / 2)
        
        # Calculate base geometry 
        base_radius, hole_rad, square_size = self._calculate_geometry(widget_center)
        if base_radius <= 0:
            painter.end()
            return
            
        # Save the original state
        painter.save()
        
        # Apply pan and zoom transformations centered on the widget center
        painter.translate(widget_center)
        painter.scale(self._zoom_factor, self._zoom_factor)
        painter.translate(self._pan_offset_x / self._zoom_factor, self._pan_offset_y / self._zoom_factor)
        painter.translate(-widget_center.x(), -widget_center.y())
        
        # Draw a dot at the center
        painter.setPen(QPen(QColor("lime"), 5 / self._zoom_factor))
        painter.setBrush(QBrush(QColor("lime")))
        painter.drawEllipse(widget_center, 3 / self._zoom_factor, 3 / self._zoom_factor)
        
        # Calculate heptagon points and hole positions
        heptagon_points = self._calculate_heptagon_points(widget_center, base_radius)
        hole_coords = self._calculate_hole_positions(widget_center, base_radius)

        # 1. Draw the heptagon with a gradient background and more prominent edges
        # First create a polygon to fill
        polygon_path = QPainterPath()
        polygon_path.moveTo(heptagon_points[0])
        for i in range(1, len(heptagon_points)):
            polygon_path.lineTo(heptagon_points[i])
        polygon_path.closeSubpath()
        
        # Fill with gradient
        background_gradient = QRadialGradient(widget_center, base_radius)
        background_gradient.setColorAt(0, QColor(115, 115, 255))  # Lighter blue center
        background_gradient.setColorAt(1, QColor(97, 97, 248))    # The specified RGB color (97,97,248)
        painter.setBrush(QBrush(background_gradient))
        painter.setPen(Qt.PenStyle.NoPen)  # No pen for the fill
        painter.drawPath(polygon_path)
        
        # Draw the edges with a glowing effect
        edge_pen = QPen(QColor(150, 150, 255), 2.5 / self._zoom_factor)  # Lighter blue for the edge
        painter.setPen(edge_pen)
        painter.drawPolygon(heptagon_points)
        
        # Also draw a subtle outer glow
        glow_pen = QPen(QColor(130, 130, 255, 60), 5 / self._zoom_factor)  # Matching blue glow
        painter.setPen(glow_pen)
        painter.drawPolygon(heptagon_points)

        # Draw center alignment marker
        painter.setPen(QPen(QColor(80, 80, 100), 1 / self._zoom_factor, Qt.PenStyle.DashLine))
        painter.drawLine(
            QPointF(widget_center.x() - base_radius, widget_center.y()),
            QPointF(widget_center.x() + base_radius, widget_center.y()),
        )
        painter.drawLine(
            QPointF(widget_center.x(), widget_center.y() - base_radius),
            QPointF(widget_center.x(), widget_center.y() + base_radius),
        )

        # 2. Draw the 56 Aubrey Holes as squares that touch each other
        # Adjust font sizes based on zoom
        number_font = QFont("Arial", int(max(6 / self._zoom_factor, int(hole_rad * 1.0))), QFont.Weight.Bold)
        half_square = square_size / 2
        
        for i, pos_qpoint in enumerate(hole_coords):
            # Calculate the angle to the center for this hole
            dx = pos_qpoint.x() - widget_center.x()
            dy = pos_qpoint.y() - widget_center.y()
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            
            # Determine which side of the heptagon this hole is on based on angle
            # The heptagon has 7 sides with 360/7 ≈ 51.43 degrees per side
            angle_per_side = 360.0 / self._num_sides
            
            # Normalize angle to 0-360 range
            normalized_angle = (angle_deg + 360) % 360
            
            # Calculate side index from angle
            # Adjust by 270-(angle_per_side/2) to match our heptagon orientation with flat edge at bottom
            adjusted_angle = (normalized_angle - (270 - angle_per_side/2) + 360) % 360
            side_index = int(adjusted_angle / angle_per_side)
            
            # For a perfect alignment of squares to the heptagon edge, 
            # we need to calculate the actual edge angle of that side
            start_vertex = heptagon_points[side_index]
            end_vertex = heptagon_points[(side_index + 1) % self._num_sides]
            
            # Calculate the angle of the edge based on its endpoints
            edge_dx = end_vertex.x() - start_vertex.x()
            edge_dy = end_vertex.y() - start_vertex.y()
            edge_angle = math.degrees(math.atan2(edge_dy, edge_dx))
            
            # To get a flat edge of the square aligned with the heptagon edge,
            # we set the rotation to exactly match the edge angle
            # This will make one edge of the square parallel to the heptagon edge
            tangent_angle = edge_angle
            
            # Draw square with gradient for 3D effect
            # Use linear gradient for squares instead of radial
            gradient = QLinearGradient(0, -half_square, 0, half_square)
            gradient.setColorAt(0, QColor(150, 150, 150))  # Lighter top
            gradient.setColorAt(1, QColor(100, 100, 100))  # Darker bottom

            painter.setPen(QPen(QColor(40, 40, 40), 1.5 / self._zoom_factor))
            painter.setBrush(QBrush(gradient))
            
            # Save current state, translate to hole position and rotate to align with edge
            painter.save()
            painter.translate(pos_qpoint)
            # Rotate square to align with the heptagon edge
            # Use the tangent angle to make the square align with the heptagon edge
            painter.rotate(tangent_angle)
            
            # Draw square centered at origin (0,0) since we've translated to hole position
            square_rect = QRectF(-half_square, -half_square, square_size, square_size)
            painter.drawRect(square_rect)

            # Draw hole numbers (smaller font, always visible)
            painter.setPen(QColor("white"))
            painter.setFont(number_font)
            text = str(i + 1)  # Add 1 to display as 1-56 instead of 0-55
            painter.drawText(square_rect, Qt.AlignmentFlag.AlignCenter, text)
            
            # Restore painter state
            painter.restore()

        # Draw Galactic Center Line and Label - align to the middle of a side
        if self._gc_azimuth_for_drawing is not None:
            self._draw_galactic_center(painter, widget_center, base_radius, heptagon_points)

        # Draw the Markers with zodiac labels
        self._draw_markers(painter, widget_center, base_radius, hole_coords, hole_rad, square_size)
        
        # Restore original state
        painter.restore()
        
        # Draw zoom level indicator
        self._draw_zoom_indicator(painter)
        
        painter.end()

    def _draw_galactic_center(self, painter, center, radius, heptagon_points):
        """
        Draw the Galactic Center line as the midpoint between holes 28 and 29,
        aligned with the vertical y-axis.
        """
        gc_color = QColor("gold")
        gc_label_text = "GC"
        gc_label_font = QFont(
            "Arial", int(max(10 / self._zoom_factor, 6)), QFont.Weight.Bold
        )
        zodiac_label_font = QFont(
            "Arial", int(max(8 / self._zoom_factor, 5)), QFont.Weight.Normal
        )
        label_offset = 20 / self._zoom_factor  # Adjust offset with zoom

        # Get hole positions
        hole_coords = self._calculate_hole_positions(center, radius)

        # Check if we have enough holes
        if len(hole_coords) > 28:
            # Draw line from center along y-axis
            # Use negative y value to point UPWARD instead of downward
            y_axis_vector = QPointF(0, -radius * 1.2)  # Point ABOVE center along y-axis
            painter.setPen(QPen(gc_color, 3 / self._zoom_factor, Qt.PenStyle.SolidLine))
            painter.drawLine(center, center + y_axis_vector)

            # Draw glow effect for the line
            glow_pen = QPen(QColor(255, 215, 0, 60), 8 / self._zoom_factor)
            painter.setPen(glow_pen)
            painter.drawLine(center, center + y_axis_vector)

            # Calculate position for GC label
            # Place the GC label at the end of the line (now at the top)
            label_x = center.x()  # Centered on x-axis
            label_y = (
                center.y() - radius * 1.2 - label_offset
            )  # ABOVE the end of the line

            # Draw GC label with background
            painter.setFont(gc_label_font)
            gc_text_width = painter.fontMetrics().horizontalAdvance(gc_label_text)
            gc_text_height = painter.fontMetrics().height()

            # Background for GC label
            gc_bg_rect = QRectF(
                label_x - gc_text_width / 2 - 5,
                label_y - gc_text_height - 2,
                gc_text_width + 10,
                gc_text_height + 4,
            )
            painter.setBrush(QBrush(QColor(40, 40, 40, 180)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                gc_bg_rect, 4 / self._zoom_factor, 4 / self._zoom_factor
            )

            # Draw GC text
            painter.setPen(gc_color)
            painter.drawText(
                QPointF(label_x - gc_text_width / 2, label_y - 2), gc_label_text
            )

            # Draw zodiac label if available
            if self._gc_zodiac_label:
                painter.setFont(zodiac_label_font)
                zodiac_text_width = painter.fontMetrics().horizontalAdvance(
                    self._gc_zodiac_label
                )

                # Background for zodiac label
                zodiac_bg_rect = QRectF(
                    label_x - zodiac_text_width / 2 - 5,
                    label_y - gc_text_height - 15,  # Position above the GC label
                    zodiac_text_width + 10,
                    gc_text_height,
                )
                painter.setBrush(QBrush(QColor(40, 40, 40, 180)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(
                    zodiac_bg_rect, 4 / self._zoom_factor, 4 / self._zoom_factor
                )

                # Draw zodiac text
                painter.setPen(gc_color)
                painter.drawText(
                    QPointF(
                        label_x - zodiac_text_width / 2, label_y - gc_text_height - 5
                    ),
                    self._gc_zodiac_label,
                )

    def _draw_markers(self, painter, center, radius, hole_coords, hole_rad, square_size=None):
        """Draw the markers with their zodiac labels radiating outward."""
        # Use square_size if provided, otherwise calculate marker size based on hole_rad
        if square_size is None:
            marker_radius = hole_rad * 1.8  # Markers slightly larger than holes
            is_square = False
        else:
            marker_radius = square_size * 0.7  # Size marker relative to the squares
            is_square = True
            
        marker_font = QFont(
            "Arial", int(max(7 / self._zoom_factor, int(marker_radius * 0.8))), QFont.Weight.Bold
        )
        zodiac_font = QFont("Arial", int(max(9 / self._zoom_factor, 6)))

        # First, draw zodiacal positions for all holes if enabled
        if self._display_zodiac_degrees and self._hole_zodiac_positions:
            # Use a smaller font for all hole labels to avoid overlap
            small_zodiac_font = QFont("Arial", int(max(7 / self._zoom_factor, 5)))
            painter.setFont(small_zodiac_font)

            for hole_num, position in self._hole_zodiac_positions.items():
                if hole_num in self._marker_positions.values():
                    # Skip holes with markers - they'll get their own labels later
                    continue

                # Use the exact hole position from the pre-calculated coordinates
                hole_point = hole_coords[hole_num]
                
                # Calculate vector from center to hole point (for outward direction)
                dx = hole_point.x() - center.x()
                dy = hole_point.y() - center.y()
                
                # Normalize the vector
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    dx /= length
                    dy /= length
                
                # Position label OUTSIDE from the hole along this vector
                # Use fixed distance for consistency
                label_x = hole_point.x() + dx * 50
                label_y = hole_point.y() + dy * 50

                # Draw a connecting line from hole to label
                line_color = QColor(150, 150, 150, 80)  # More transparent line
                painter.setPen(
                    QPen(line_color, 0.5 / self._zoom_factor, Qt.PenStyle.DotLine)
                )
                painter.drawLine(hole_point, QPointF(label_x, label_y))

                # Draw a small background for zodiac text
                text_width = painter.fontMetrics().horizontalAdvance(position)
                text_height = painter.fontMetrics().height()

                # Calculate angle for text alignment (using the center-to-hole vector)
                text_angle = math.atan2(dy, dx) * 180 / math.pi

                # Show all hole labels with rotated text background
                text_bg = QColor(20, 20, 40, 150)  # More transparent background
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(text_bg))
                
                # Draw text background
                painter.save()  # Save current painter state
                painter.translate(label_x, label_y)
                
                # Adjust rotation so text is legible (not upside down)
                if 90 < text_angle < 270:
                    text_angle += 180  # Flip text to be readable
                
                painter.rotate(text_angle)
                painter.drawRoundedRect(
                    QRectF(
                        -text_width/2 - 3,
                        -text_height/2 - 1,
                        text_width + 6,
                        text_height + 2,
                    ),
                    3,
                    3,
                )

                # Draw the text
                painter.setPen(QColor(200, 200, 220))
                painter.drawText(QPointF(-text_width/2, text_height/2 - 3), position)

                # Draw the hole number
                hole_num_text = f"{hole_num + 1}"  # Add 1 to display as 1-56
                painter.setPen(QColor(150, 150, 170))
                painter.drawText(QPointF(-text_width/2 - 15, text_height/2 - 3), hole_num_text)
                
                painter.restore()  # Restore painter state

        # Now draw markers and their zodiacal labels with improved orientation
        for name, hole_num in self._marker_positions.items():
            # Skip markers that should not be visible
            if not self._visible_markers.get(name, True):
                continue
                
            if 0 <= hole_num < NUM_HOLES:
                marker_qpoint = hole_coords[hole_num]

                # Get marker color with more vibrant options
                base_color = self._marker_colors.get(name, QColor("red"))

                # Calculate angle from center to marker for rotation
                dx = marker_qpoint.x() - center.x()
                dy = marker_qpoint.y() - center.y()
                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)

                if is_square:
                    # Draw square marker with rotation
                    half_size = marker_radius
                    
                    # Save painter state for rotation
                    painter.save()
                    painter.translate(marker_qpoint)
                    
                    # Rotate square to align with angle toward center
                    # Use the angle directly to make a flat edge face inward
                    painter.rotate(angle_deg)
                    
                    # Create a glowing effect for markers
                    glow_size = half_size * 1.4
                    glow_rect = QRectF(-glow_size, -glow_size, glow_size * 2, glow_size * 2)
                    
                    glow_color = QColor(base_color)
                    glow_color.setAlpha(100)  # Semi-transparent for glow
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(glow_color))
                    painter.drawRect(glow_rect)
                    
                    # Use linear gradient for square
                    marker_gradient = QLinearGradient(0, -half_size, 0, half_size)
                    light_color = QColor(base_color)
                    light_color = light_color.lighter(150)  # Lighten for 3D effect
                    marker_gradient.setColorAt(0, light_color)
                    marker_gradient.setColorAt(1, base_color)

                    marker_rect = QRectF(-half_size, -half_size, half_size * 2, half_size * 2)
                    painter.setBrush(QBrush(marker_gradient))
                    painter.setPen(QPen(QColor("black"), 1.5 / self._zoom_factor))
                    painter.drawRect(marker_rect)
                    
                    # Draw marker name (e.g., S, M) in the center of the marker
                    painter.setPen(QColor("black"))
                    painter.setFont(marker_font)
                    painter.drawText(marker_rect, Qt.AlignmentFlag.AlignCenter, name)
                    
                    painter.restore()
                else:
                    # Original circular marker code
                    # Create a glowing effect for markers
                    glow_radius = marker_radius * 1.4
                    glow_gradient = QRadialGradient(marker_qpoint, glow_radius)
                    glow_color = QColor(base_color)
                    glow_color.setAlpha(100)  # Semi-transparent for glow
                    glow_gradient.setColorAt(0, glow_color)
                    glow_color.setAlpha(0)  # Fully transparent at edge of glow
                    glow_gradient.setColorAt(1, glow_color)

                    # Draw the glow effect
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QBrush(glow_gradient))
                    painter.drawEllipse(marker_qpoint, glow_radius, glow_radius)
                    
                    # Draw circular marker
                    marker_gradient = QRadialGradient(marker_qpoint, marker_radius)
                    light_color = QColor(base_color)
                    light_color = light_color.lighter(150)  # Lighten for 3D effect
                    marker_gradient.setColorAt(0, light_color)
                    marker_gradient.setColorAt(1, base_color)

                    painter.setBrush(QBrush(marker_gradient))
                    painter.setPen(QPen(QColor("black"), 1.5 / self._zoom_factor))
                    painter.drawEllipse(marker_qpoint, marker_radius, marker_radius)
                    
                    # Draw marker name (e.g., S, M) in the center of the marker
                    painter.setPen(QColor("black"))
                    painter.setFont(marker_font)
                    text_rect_size = marker_radius * 1.5
                    text_rect = painter.boundingRect(
                        int(marker_qpoint.x() - text_rect_size / 2),
                        int(marker_qpoint.y() - text_rect_size / 2),
                        int(text_rect_size),
                        int(text_rect_size),
                        Qt.AlignmentFlag.AlignCenter,
                        name,
                    )
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, name)

                # Draw zodiac position from calculated hole positions or from marker-specific positions
                zodiac_position = self._marker_zodiac_positions.get(name)
                if (
                    not zodiac_position
                    and self._hole_zodiac_positions
                    and hole_num in self._hole_zodiac_positions
                ):
                    zodiac_position = self._hole_zodiac_positions[hole_num]

                if zodiac_position:
                    # Calculate vector from center to marker for outward direction
                    vector_x = marker_qpoint.x() - center.x()
                    vector_y = marker_qpoint.y() - center.y()

                    # Normalize the vector
                    length = math.sqrt(vector_x * vector_x + vector_y * vector_y)
                    if length > 0:
                        vector_x /= length
                        vector_y /= length

                    # Position label FAR OUTSIDE from marker using the vector
                    # Adjust offset with zoom factor
                    offset_distance = 65
                    label_x = marker_qpoint.x() + vector_x * offset_distance
                    label_y = marker_qpoint.y() + vector_y * offset_distance

                    # Calculate angle for text alignment (using the center-to-marker vector)
                    text_angle = math.atan2(vector_y, vector_x) * 180 / math.pi

                    # Create background for better readability
                    painter.setFont(zodiac_font)
                    text_metrics = painter.fontMetrics()
                    text_width = text_metrics.horizontalAdvance(zodiac_position)
                    text_height = text_metrics.height()

                    # Save painter state before rotating
                    painter.save()
                    painter.translate(label_x, label_y)

                    # Adjust rotation so text is legible (not upside down)
                    if 90 < text_angle < 270:
                        text_angle += 180  # Flip text to be readable

                    painter.rotate(text_angle)

                    # Draw text background
                    bg_rect = QRectF(
                        -text_width / 2 - 5,
                        -text_height / 2 - 2,
                        text_width + 10,
                        text_height + 4,
                    )
                    bg_color = QColor(20, 20, 30, 200)  # Semi-transparent background
                    painter.setBrush(QBrush(bg_color))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRoundedRect(bg_rect, 4, 4)

                    # Draw the zodiac text
                    painter.setPen(
                        QColor(base_color).lighter(180)
                    )  # Brighter text for visibility
                    painter.drawText(
                        QPointF(-text_width / 2, text_height / 2 - 2), zodiac_position
                    )

                    # Restore painter state
                    painter.restore()
            else:
                print(f"Warning: Marker '{name}' has invalid position {hole_num}.")

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        delta = event.angleDelta().y()

        # Calculate zoom center (mouse position)
        zoom_point = event.position()

        # Determine zoom direction
        zoom_direction = 1 if delta > 0 else -1

        # Store old zoom for calculation
        old_zoom = self._zoom_factor

        # Calculate new zoom factor with bounds
        self._zoom_factor += zoom_direction * self._zoom_step
        self._zoom_factor = max(self._min_zoom, min(self._max_zoom, self._zoom_factor))

        # Only proceed if zoom actually changed
        if old_zoom != self._zoom_factor:
            # Get widget center
            widget_center_x = self.width() / 2
            widget_center_y = self.height() / 2

            # Calculate how far the mouse is from center in the view coordinates
            dx = (zoom_point.x() - widget_center_x) / old_zoom
            dy = (zoom_point.y() - widget_center_y) / old_zoom

            # Adjust pan offset to keep the point under mouse in the same relative position
            scale_change = self._zoom_factor / old_zoom
            new_dx = dx * scale_change
            new_dy = dy * scale_change

            # Update pan offset to compensate for the zoom change
            self._pan_offset_x += (dx - new_dx) * self._zoom_factor
            self._pan_offset_y += (dy - new_dy) * self._zoom_factor

            # Force a repaint
            self.update()

    def mousePressEvent(self, event):
        """Handle mouse press events for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = True
            self._last_pan_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """Handle mouse move events for panning."""
        if self._is_panning:
            current_pos = event.position()
            dx = current_pos.x() - self._last_pan_pos.x()
            dy = current_pos.y() - self._last_pan_pos.y()

            self._pan_offset_x += dx
            self._pan_offset_y += dy

            self._last_pan_pos = current_pos
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events for panning."""
        if event.button() == Qt.MouseButton.LeftButton and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click events for resetting zoom and pan."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._zoom_factor = 1.0
            self._pan_offset_x = 0.0
            self._pan_offset_y = 0.0
            self.update()
            # Emit a custom signal or log message about view reset
            print("View reset to default (zoom: 1.0x, pan: 0,0)")

    def _draw_zoom_indicator(self, painter):
        """Draw a zoom level indicator in the bottom-right corner."""
        zoom_text = f"Zoom: {self._zoom_factor:.1f}x"

        # Use a fixed font size regardless of zoom
        font = QFont("Arial", 10)
        painter.setFont(font)

        # Calculate text dimensions
        text_rect = painter.fontMetrics().boundingRect(zoom_text)
        text_width = text_rect.width() + 20
        text_height = text_rect.height() + 10

        # Position in bottom-right corner with padding
        padding = 10
        x = self.width() - text_width - padding
        y = self.height() - text_height - padding

        # Draw background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 150)))
        painter.drawRoundedRect(x, y, text_width, text_height, 5, 5)

        # Draw text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(x + 10, y + text_height - 5, zoom_text)

        # Draw reset hint
        hint_text = "Double-click to reset view"
        hint_rect = painter.fontMetrics().boundingRect(hint_text)
        hint_width = hint_rect.width() + 20
        hint_height = hint_rect.height() + 10

        hint_x = self.width() - hint_width - padding
        hint_y = y - hint_height - 5

        # Draw background for hint
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))
        painter.drawRoundedRect(hint_x, hint_y, hint_width, hint_height, 5, 5)

        # Draw hint text
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(hint_x + 10, hint_y + hint_height - 5, hint_text)


# Example usage for testing this widget directly
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget

    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    circle_view = CircleViewWidget()
    layout.addWidget(circle_view)

    # Example marker positions
    test_positions = {
        "S": 0,  # Sun at hole 0 (North)
        "M": NUM_HOLES // 4,  # Moon at hole 14 (East)
        "N": NUM_HOLES // 2,  # Node N at hole 28 (South)
        "N'": (NUM_HOLES * 3) // 4,  # Node N' at hole 42 (West)
    }
    circle_view.update_marker_positions(test_positions)

    # REMOVED: Cardinal point testing code - this functionality is not needed with heptagon view

    # Set GC zodiac
    circle_view.set_galactic_center_zodiac("Sagittarius 26.4°")

    circle_view.set_orientation(45)  # Test with an offset orientation for Hole 0

    window.setGeometry(100, 100, 500, 500)
    window.setWindowTitle("Stonehenge Heptagon View Test")
    window.show()
    sys.exit(app.exec())
