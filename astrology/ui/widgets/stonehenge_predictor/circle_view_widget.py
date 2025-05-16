"""
Defines the CircleViewWidget for visualizing the Stonehenge Aubrey Holes in a heptagon shape.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-08-09
Dependencies: PyQt6
"""

import math
from typing import Dict, List, Optional, Tuple

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QRadialGradient, QPainterPath
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
        self._hole_positions_cache = []
        self._azimuth_offset_deg = 0.0  # Orientation of Hole 0 from North
        self._gc_azimuth_for_drawing: Optional[float] = None  # Explicit GC azimuth for line drawing
        self._gc_zodiac_label: Optional[str] = None  # Zodiac sign and degree for Galactic Center

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
        Sets the orientation of the heptagon so that Hole 0 points to the given azimuth.
        Args:
            azimuth_deg (float): The azimuth (in degrees) to which Hole 0 should point. 0 = north, 90 = east, etc.
        """
        self._azimuth_offset_deg = azimuth_deg % 360
        self._gc_azimuth_for_drawing = azimuth_deg  # Store it for drawing the GC line
        self._hole_positions_cache = []  # Clear cache so positions are recalculated
        # Calculate zodiacal positions when orientation changes
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

    def _calculate_geometry(
        self, width: int, height: int
    ) -> tuple[QPointF, float, float]:
        """
        Calculates the center, radius, and hole radius based on widget size.
        Ensures the heptagon fits entirely within the visible area regardless of window size.
        """
        # Calculate the maximum possible radius that will fit in the widget
        padding = 40  # Increased padding to ensure labels fit
        size = min(width, height) - 2 * padding

        # Ensure we don't try to draw a negative-sized shape
        if size <= 0:
            size = max(200, min(width, height) - 20)

        radius = size / 2

        # Center the heptagon precisely in the widget
        center = QPointF(width / 2, height / 2)

        # Adjust hole radius proportionally to the heptagon size
        hole_radius = max(3.0, radius / 40) + 3.0

        return center, radius, hole_radius

    def _calculate_heptagon_points(self, center: QPointF, radius: float) -> List[QPointF]:
        """
        Calculate the vertices of the heptagon.
        Position each vertex to be between hole positions, so each side has exactly 8 holes.
        """
        points = []
        
        # With 56 holes total and 7 sides, we need 8 holes per side
        # For 7 vertices, we'll place them between holes at positions 0, 8, 16, 24, 32, 40, 48
        holes_per_side = NUM_HOLES // self._num_sides  # Should be 8
        
        # Apply the azimuth offset to rotate the heptagon
        az_offset_rad = math.radians(self._azimuth_offset_deg)
        
        for i in range(self._num_sides):
            # Calculate the position halfway between the holes at the corners
            # For example, vertex 0 should be between hole 55 and hole 0 (or hole 7 and hole 8)
            hole_index = i * holes_per_side
            angle_before = ((hole_index - 0.5) / NUM_HOLES) * 2 * math.pi - (math.pi / 2) + az_offset_rad
            
            # Calculate point position
            x = center.x() + radius * math.cos(angle_before)
            y = center.y() + radius * math.sin(angle_before)
            points.append(QPointF(x, y))
            
        return points

    def _calculate_hole_positions(self, center: QPointF, radius: float):
        """
        Pre-calculates and caches the QPointF for each of the 56 hole centers.
        Holes are distributed along the edges of the heptagon with 8 holes per side.
        """
        if not self._hole_positions_cache or len(self._hole_positions_cache) != NUM_HOLES:
            self._hole_positions_cache = []
            
            # Get the heptagon vertices
            heptagon_points = self._calculate_heptagon_points(center, radius)
            
            # We want 8 holes per side of the heptagon
            holes_per_side = NUM_HOLES // self._num_sides  # Should be 8
            
            # Keep track of the holes we've placed
            holes_placed = 0
            
            # Distribute holes along the sides of the heptagon
            for side_index in range(self._num_sides):
                # Get the start and end vertices of this side
                start_vertex = heptagon_points[side_index]
                end_vertex = heptagon_points[(side_index + 1) % self._num_sides]
                
                # Place 8 holes evenly along this side
                for i in range(holes_per_side):
                    # Calculate position along this side (0 to 1)
                    t = i / holes_per_side
                    
                    # Calculate the coordinates of the hole
                    x = start_vertex.x() + t * (end_vertex.x() - start_vertex.x())
                    y = start_vertex.y() + t * (end_vertex.y() - start_vertex.y())
                    
                    # Add the hole position
                    self._hole_positions_cache.append(QPointF(x, y))
                    holes_placed += 1
            
            # Ensure we've placed all 56 holes
            assert holes_placed == NUM_HOLES, f"Expected {NUM_HOLES} holes, placed {holes_placed}"
                
        return self._hole_positions_cache

    def _calculate_hole_zodiac_positions(self):
        """
        Calculate zodiacal positions for all holes based on GC orientation.
        Assumes Hole 0 is aligned with the Galactic Center.
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

            # Starting from hole 0 (GC), calculate degrees for each hole
            # Each hole represents 360/56 = ~6.43 degrees of the zodiac
            degrees_per_hole = 360 / NUM_HOLES

            # Initialize dictionary to hold zodiacal position for each hole
            self._hole_zodiac_positions = {}

            # Calculate starting absolute degree (0-360 scale)
            # GC at hole 0, so hole 0 = GC position in absolute degrees
            gc_absolute_degree = (gc_sign_index * 30) + gc_degree

            for hole_num in range(NUM_HOLES):
                # Calculate offset from the GC hole (counterclockwise)
                # Since holes are arranged counterclockwise, we need to go backwards in the zodiac
                offset_degrees = hole_num * degrees_per_hole

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

    def paintEvent(self, event):
        """
        Handles the painting of the widget.
        Draws the Aubrey Holes on a heptagon, and markers.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center, radius, hole_rad = self._calculate_geometry(self.width(), self.height())
        if radius <= 0:
            return

        # Draw a dot at the calculated center
        painter.setPen(QPen(QColor("lime"), 5))
        painter.setBrush(QBrush(QColor("lime")))
        painter.drawEllipse(center, 3, 3)
        
        # Calculate heptagon points and hole positions
        heptagon_points = self._calculate_heptagon_points(center, radius)
        hole_coords = self._calculate_hole_positions(center, radius)

        # 1. Draw the heptagon with a gradient background and more prominent edges
        # First create a polygon to fill
        polygon_path = QPainterPath()
        polygon_path.moveTo(heptagon_points[0])
        for i in range(1, len(heptagon_points)):
            polygon_path.lineTo(heptagon_points[i])
        polygon_path.closeSubpath()
        
        # Fill with gradient
        background_gradient = QRadialGradient(center, radius)
        background_gradient.setColorAt(0, QColor(30, 30, 45))  # Slightly lighter center
        background_gradient.setColorAt(1, QColor(15, 15, 30))  # Darker edges
        painter.setBrush(QBrush(background_gradient))
        painter.setPen(Qt.PenStyle.NoPen)  # No pen for the fill
        painter.drawPath(polygon_path)
        
        # Draw the edges with a glowing effect
        edge_pen = QPen(QColor(80, 80, 120), 2.5)
        painter.setPen(edge_pen)
        painter.drawPolygon(heptagon_points)
        
        # Also draw a subtle outer glow
        glow_pen = QPen(QColor(100, 100, 160, 40), 5)
        painter.setPen(glow_pen)
        painter.drawPolygon(heptagon_points)

        # Draw center alignment marker
        painter.setPen(QPen(QColor(80, 80, 100), 1, Qt.PenStyle.DashLine))
        painter.drawLine(
            QPointF(center.x() - radius, center.y()),
            QPointF(center.x() + radius, center.y()),
        )
        painter.drawLine(
            QPointF(center.x(), center.y() - radius),
            QPointF(center.x(), center.y() + radius),
        )

        # 2. Draw the 56 Aubrey Holes and their numbers
        hole_font = QFont("Arial", max(6, int(hole_rad * 1.2)))
        number_font = QFont("Arial", max(6, int(hole_rad * 1.0)), QFont.Weight.Bold)
        for i, pos_qpoint in enumerate(hole_coords):
            # Draw hole with gradient for 3D effect
            gradient = QRadialGradient(pos_qpoint, hole_rad)
            gradient.setColorAt(0, QColor(150, 150, 150))  # Lighter center
            gradient.setColorAt(1, QColor(100, 100, 100))  # Darker edge

            painter.setPen(QPen(QColor(40, 40, 40), 1.5))
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(pos_qpoint, hole_rad, hole_rad)

            # Draw hole numbers (smaller font, always visible)
            painter.setPen(QColor("white"))
            painter.setFont(number_font)
            text = str(i)
            text_rect = painter.boundingRect(
                int(pos_qpoint.x() - hole_rad),
                int(pos_qpoint.y() - hole_rad),
                int(hole_rad * 2),
                int(hole_rad * 2),
                Qt.AlignmentFlag.AlignCenter,
                text,
            )
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

        # Draw Galactic Center Line and Label - align to the middle of a side
        if self._gc_azimuth_for_drawing is not None:
            self._draw_galactic_center(painter, center, radius, heptagon_points)

        # Draw the Markers with zodiac labels
        self._draw_markers(painter, center, radius, hole_coords, hole_rad)

        painter.end()

    def _draw_galactic_center(self, painter, center, radius, heptagon_points):
        """
        Draw the Galactic Center line aligned to the middle of a heptagon side.
        """
        gc_color = QColor("gold")
        gc_label_text = "GC"
        gc_label_font = QFont("Arial", 10, QFont.Weight.Bold)
        zodiac_label_font = QFont("Arial", 8, QFont.Weight.Normal)
        label_offset_from_edge = 15

        # Find the side closest to the GC azimuth
        closest_side_index = 0
        min_angle_diff = 360.0
        
        # The azimuth angle needs to be converted to the heptagon's coordinate system
        gc_angle_rad = math.radians(90.0 - self._gc_azimuth_for_drawing)
        
        for i in range(self._num_sides):
            # Calculate the middle point of the side
            start_point = heptagon_points[i]
            end_point = heptagon_points[(i + 1) % self._num_sides]
            
            # Find middle of this side
            mid_x = (start_point.x() + end_point.x()) / 2
            mid_y = (start_point.y() + end_point.y()) / 2
            
            # Calculate angle of midpoint from center
            side_angle = math.atan2(mid_y - center.y(), mid_x - center.x())
            
            # Calculate angle difference (in radians)
            angle_diff = abs(side_angle - gc_angle_rad)
            while angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
                
            # If this is closer to the GC angle than previous best, update
            if angle_diff < min_angle_diff:
                min_angle_diff = angle_diff
                closest_side_index = i
        
        # Get the middle point of the closest side
        start_point = heptagon_points[closest_side_index]
        end_point = heptagon_points[(closest_side_index + 1) % self._num_sides]
        
        mid_x = (start_point.x() + end_point.x()) / 2
        mid_y = (start_point.y() + end_point.y()) / 2
        
        # Draw line from center to middle of the side with glowing effect
        # Main line
        painter.setPen(QPen(gc_color, 3, Qt.PenStyle.SolidLine))
        painter.drawLine(center, QPointF(mid_x, mid_y))
        
        # Glow effect
        glow_pen = QPen(QColor(255, 215, 0, 60), 8)  # Transparent gold for glow
        painter.setPen(glow_pen)
        painter.drawLine(center, QPointF(mid_x, mid_y))
        
        # Calculate position for label - slightly outside the heptagon side
        # Calculate vector from center to midpoint
        dx = mid_x - center.x()
        dy = mid_y - center.y()
        
        # Normalize the vector
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx /= length
            dy /= length
            
        # Position the label a bit outside the heptagon side
        label_x = mid_x + dx * label_offset_from_edge
        label_y = mid_y + dy * label_offset_from_edge
        
        # Calculate angle for text rotation
        text_angle = math.atan2(dy, dx) * 180 / math.pi
        
        # Save painter state
        painter.save()
        painter.translate(label_x, label_y)
        
        # Adjust rotation so text is legible (not upside down)
        if 90 < text_angle < 270:
            text_angle += 180  # Flip text to be readable
        
        painter.rotate(text_angle)
        
        # Draw GC label with background
        painter.setFont(gc_label_font)
        gc_text_width = painter.fontMetrics().horizontalAdvance(gc_label_text)
        gc_text_height = painter.fontMetrics().height()
        
        # Background for GC label
        gc_bg_rect = QRectF(
            -gc_text_width/2 - 5,
            -gc_text_height/2 - 2,
            gc_text_width + 10,
            gc_text_height + 4
        )
        painter.setBrush(QBrush(QColor(40, 40, 40, 180)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(gc_bg_rect, 4, 4)
        
        # Draw GC text
        painter.setPen(gc_color)
        painter.drawText(QPointF(-gc_text_width/2, gc_text_height/2 - 2), gc_label_text)
        
        # Draw zodiac label if available
        if self._gc_zodiac_label:
            painter.setFont(zodiac_label_font)
            zodiac_text_width = painter.fontMetrics().horizontalAdvance(self._gc_zodiac_label)
            
            # Background for zodiac label
            zodiac_bg_rect = QRectF(
                -zodiac_text_width/2 - 5,
                gc_text_height/2 + 2,
                zodiac_text_width + 10,
                gc_text_height
            )
            painter.setBrush(QBrush(QColor(40, 40, 40, 180)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(zodiac_bg_rect, 4, 4)
            
            # Draw zodiac text
            painter.setPen(gc_color)
            painter.drawText(QPointF(-zodiac_text_width/2, gc_text_height*1.5), self._gc_zodiac_label)
        
        # Restore painter state
        painter.restore()

    def _draw_markers(self, painter, center, radius, hole_coords, hole_rad):
        """Draw the markers with their zodiac labels radiating outward."""
        marker_radius = hole_rad * 1.8  # Markers slightly larger than holes
        marker_font = QFont(
            "Arial", max(7, int(marker_radius * 0.8)), QFont.Weight.Bold
        )
        zodiac_font = QFont("Arial", 9)

        # First, draw zodiacal positions for all holes if enabled
        if self._display_zodiac_degrees and self._hole_zodiac_positions:
            # Use a smaller font for all hole labels to avoid overlap
            small_zodiac_font = QFont("Arial", 7)
            painter.setFont(small_zodiac_font)

            # Get the heptagon points to determine which side each hole is on
            heptagon_points = self._calculate_heptagon_points(center, radius)
            holes_per_side = NUM_HOLES // self._num_sides  # Should be 8

            for hole_num, position in self._hole_zodiac_positions.items():
                if hole_num in self._marker_positions.values():
                    # Skip holes with markers - they'll get their own labels later
                    continue

                # Use the exact hole position from the pre-calculated coordinates
                hole_point = hole_coords[hole_num]

                # Determine which side of the heptagon this hole is on
                side_index = hole_num // holes_per_side

                # Get the start and end vertices of this side
                start_vertex = heptagon_points[side_index]
                end_vertex = heptagon_points[(side_index + 1) % self._num_sides]

                # Calculate the normal vector to this side (perpendicular outward)
                side_dx = end_vertex.x() - start_vertex.x()
                side_dy = end_vertex.y() - start_vertex.y()
                
                # Rotate 90 degrees to get normal vector (outward facing)
                normal_dx = -side_dy
                normal_dy = side_dx
                
                # Normalize the normal vector
                length = math.sqrt(normal_dx*normal_dx + normal_dy*normal_dy)
                if length > 0:
                    normal_dx /= length
                    normal_dy /= length

                # Position label outward from the hole along the normal vector
                label_distance = radius * 0.15  # Adjust to control label distance
                label_x = hole_point.x() + normal_dx * label_distance
                label_y = hole_point.y() + normal_dy * label_distance

                # Draw a connecting line from hole to label
                line_color = QColor(150, 150, 150, 80)  # More transparent line
                painter.setPen(QPen(line_color, 0.5, Qt.PenStyle.DotLine))
                painter.drawLine(hole_point, QPointF(label_x, label_y))

                # Draw a small background for zodiac text
                text_width = painter.fontMetrics().horizontalAdvance(position)
                text_height = painter.fontMetrics().height()

                # Calculate angle for text alignment (perpendicular to side)
                text_angle = math.atan2(normal_dy, normal_dx) * 180 / math.pi

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
                hole_num_text = f"{hole_num}"
                painter.setPen(QColor(150, 150, 170))
                painter.drawText(QPointF(-text_width/2 - 15, text_height/2 - 3), hole_num_text)
                
                painter.restore()  # Restore painter state

        # Now draw markers and their zodiacal labels with improved orientation
        for name, hole_num in self._marker_positions.items():
            if 0 <= hole_num < NUM_HOLES:
                marker_qpoint = hole_coords[hole_num]

                # Get marker color with more vibrant options
                base_color = self._marker_colors.get(name, QColor("red"))

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

                # Draw the marker with 3D effect
                marker_gradient = QRadialGradient(marker_qpoint, marker_radius)
                light_color = QColor(base_color)
                light_color = light_color.lighter(150)  # Lighten for 3D effect
                marker_gradient.setColorAt(0, light_color)
                marker_gradient.setColorAt(1, base_color)

                painter.setBrush(QBrush(marker_gradient))
                painter.setPen(QPen(QColor("black"), 1.5))  # Thicker border for markers
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
                    # Determine which side of the heptagon this marker is on
                    side_index = hole_num // holes_per_side
                    
                    # Get the start and end vertices of this side
                    heptagon_points = self._calculate_heptagon_points(center, radius)
                    start_vertex = heptagon_points[side_index]
                    end_vertex = heptagon_points[(side_index + 1) % self._num_sides]
                    
                    # Calculate normal vector to this side (perpendicular outward)
                    side_dx = end_vertex.x() - start_vertex.x()
                    side_dy = end_vertex.y() - start_vertex.y()
                    
                    # Rotate 90 degrees to get normal vector (outward facing)
                    normal_dx = -side_dy
                    normal_dy = side_dx
                    
                    # Normalize the normal vector
                    length = math.sqrt(normal_dx*normal_dx + normal_dy*normal_dy)
                    if length > 0:
                        normal_dx /= length
                        normal_dy /= length
                    
                    # Position label outward from marker using the normal vector
                    offset_distance = marker_radius * 3.0  # Further out for markers
                    label_x = marker_qpoint.x() + normal_dx * offset_distance
                    label_y = marker_qpoint.y() + normal_dy * offset_distance
                    
                    # Calculate angle for text alignment (perpendicular to side)
                    text_angle = math.atan2(normal_dy, normal_dx) * 180 / math.pi
                    
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
                        -text_width/2 - 5,
                        -text_height/2 - 2,
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
                    painter.drawText(QPointF(-text_width/2, text_height/2 - 2), zodiac_position)
                    
                    # Restore painter state
                    painter.restore()
            else:
                print(f"Warning: Marker '{name}' has invalid position {hole_num}.")


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
    window.setWindowTitle(
        "Stonehenge Heptagon View Test"
    )
    window.show()
    sys.exit(app.exec())
