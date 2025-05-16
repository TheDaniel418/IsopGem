"""
Defines the CircleViewWidget for visualizing the Stonehenge Aubrey Holes and markers.

Author: IsopGemini
Created: 2024-07-29
Last Modified: 2024-08-06
Dependencies: PyQt6
"""

import math
from typing import Dict, Optional

from PyQt6.QtCore import QPointF, QRectF, QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen, QRadialGradient
from PyQt6.QtWidgets import QSizePolicy, QWidget

from astrology.models.stonehenge_circle_config import NUM_HOLES


class CircleViewWidget(QWidget):
    """
    A widget that visually represents the 56 Aubrey Holes, markers,
    and cardinal direction lines (Solstices/Equinoxes).
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
        # NEW: Add zodiac position information for each marker
        self._marker_zodiac_positions: dict[str, str] = {
            "S": None,
            "M": None,
            "N": None,
            "N'": None,
        }
        self._hole_positions_cache = []
        self._azimuth_offset_deg = 0.0  # Orientation of Hole 0 from North
        self._gc_azimuth_for_drawing: Optional[
            float
        ] = None  # NEW: Explicit GC azimuth for line drawing
        self._gc_zodiac_label: Optional[
            str
        ] = None  # NEW: Zodiac sign and degree for Galactic Center

        # NEW: Add zodiac data for all holes
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

        # New attributes for cardinal points
        self._cardinal_point_azimuths: Optional[Dict[str, float]] = None
        self._cardinal_point_colors: Dict[str, QColor] = {
            "VE_az": QColor("green"),
            "SS_az": QColor("red"),
            "AE_az": QColor("orange"),
            "WS_az": QColor("blue"),
        }
        self._cardinal_point_labels: Dict[str, str] = {
            "VE_az": "VE",
            "SS_az": "SS",
            "AE_az": "AE",
            "WS_az": "WS",
        }
        # NEW: Zodiac labels for cardinal points
        self._cardinal_point_zodiac_labels: Dict[str, Optional[str]] = {
            "VE_az": None,
            "SS_az": None,
            "AE_az": None,
            "WS_az": None,
        }

        # For maintaining aspect ratio
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def resizeEvent(self, event):
        """Handle widget resize events to maintain proper circle size and position."""
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
        Sets the orientation of the circle so that Hole 0 points to the given azimuth (degrees from north).
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

    def set_cardinal_point_azimuths(self, azimuths: Optional[Dict[str, float]]):
        """
        Sets the azimuths for the cardinal points (Solstices/Equinoxes).

        Args:
            azimuths (Optional[Dict[str, float]]): A dictionary mapping cardinal point keys
                                                 (e.g., 'VE_az') to their azimuths in degrees,
                                                 or None to clear them.
        """
        self._cardinal_point_azimuths = azimuths
        self.update()  # Trigger a repaint

    def set_cardinal_point_zodiac_labels(self, zodiac_labels: Dict[str, str]):
        """
        Sets the zodiac labels for cardinal points.

        Args:
            zodiac_labels (Dict[str, str]): Dictionary mapping cardinal point keys
                                           (e.g., 'VE_az') to zodiac labels.
        """
        for key, label in zodiac_labels.items():
            if key in self._cardinal_point_zodiac_labels:
                self._cardinal_point_zodiac_labels[key] = label
        self.update()  # Trigger a repaint

    def _calculate_geometry(
        self, width: int, height: int
    ) -> tuple[QPointF, float, float]:
        """
        Calculates the center, radius, and hole radius based on widget size.
        Ensures the circle fits entirely within the visible area regardless of window size.
        """
        # Calculate the maximum possible radius that will fit in the widget
        padding = 40  # Increased padding to ensure labels fit
        size = min(width, height) - 2 * padding

        # Ensure we don't try to draw a negative-sized circle
        if size <= 0:
            size = max(200, min(width, height) - 20)

        radius = size / 2

        # Center the circle precisely in the widget
        center = QPointF(width / 2, height / 2)

        # Adjust hole radius proportionally to the circle size
        hole_radius = max(3.0, radius / 40) + 3.0

        return center, radius, hole_radius

    def _calculate_hole_positions(self, center: QPointF, radius: float):
        """
        Pre-calculates and caches the QPointF for each of the 56 hole centers.
        Hole 0 is at the azimuth offset (default: top/North), positions increase anticlockwise.
        This is now cache-aware for performance but will recalculate when size changes.
        """
        if (
            not self._hole_positions_cache
            or len(self._hole_positions_cache) != NUM_HOLES
        ):
            self._hole_positions_cache = []
            az_offset_rad = math.radians(self._azimuth_offset_deg)
            for i in range(NUM_HOLES):
                angle_rad = (
                    (i / NUM_HOLES) * 2 * math.pi - (math.pi / 2) + az_offset_rad
                )
                x = center.x() + radius * math.cos(angle_rad)
                y = center.y() + radius * math.sin(angle_rad)
                self._hole_positions_cache.append(QPointF(x, y))
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
        Draws the Aubrey Holes circle, the markers, and the cardinal direction lines (Solstices/Equinoxes).
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center, radius, hole_rad = self._calculate_geometry(self.width(), self.height())
        if radius <= 0:
            return

        # --- DEBUG: Draw a dot at the calculated center ---
        painter.setPen(QPen(QColor("lime"), 5))  # Bright green, thick pen
        painter.setBrush(QBrush(QColor("lime")))
        painter.drawEllipse(center, 3, 3)  # Draw a small circle (dot) at 'center'
        # --- END DEBUG ---

        hole_coords = self._calculate_hole_positions(center, radius)

        # 1. Draw the main circle with a subtle gradient background
        background_gradient = QRadialGradient(center, radius)
        background_gradient.setColorAt(
            0, QColor(20, 20, 30)
        )  # Dark blue-gray at center
        background_gradient.setColorAt(1, QColor(10, 10, 20))  # Darker at edges
        painter.setBrush(QBrush(background_gradient))
        painter.setPen(QPen(QColor(60, 60, 80), 2))  # Subtle border
        painter.drawEllipse(center, radius, radius)

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
        hole_font = QFont(
            "Arial", max(6, int(hole_rad * 1.2))
        )  # Reduced font size for numbers
        number_font = QFont(
            "Arial", max(6, int(hole_rad * 1.0)), QFont.Weight.Bold
        )  # Even smaller for inside dots
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

        # Draw Cardinal Point Lines and Labels
        if self._cardinal_point_azimuths:
            self._draw_cardinal_points(painter, center, radius)

        # Draw Galactic Center Line and Label
        if self._gc_azimuth_for_drawing is not None:
            self._draw_galactic_center(painter, center, radius)

        # Draw the Markers with zodiac labels
        self._draw_markers(painter, center, radius, hole_coords, hole_rad)

        painter.end()

    def _draw_cardinal_points(self, painter, center, radius):
        """Draw the cardinal points with their zodiac labels."""
        cardinal_label_font = QFont("Arial", 10, QFont.Weight.Bold)
        zodiac_label_font = QFont("Arial", 8, QFont.Weight.Normal)
        label_offset_from_edge = 15  # Pixels outside the main radius for labels

        for key, azimuth_deg in self._cardinal_point_azimuths.items():
            if (
                key in self._cardinal_point_colors
                and key in self._cardinal_point_labels
            ):
                color = self._cardinal_point_colors[key]
                label_text = self._cardinal_point_labels[key]
                zodiac_text = self._cardinal_point_zodiac_labels.get(key)

                # Convert Azimuth to Cartesian angle for drawing
                angle_rad = math.radians(90.0 - azimuth_deg)

                # Line endpoint on the circle circumference
                line_end_x = center.x() + radius * math.cos(angle_rad)
                line_end_y = center.y() - radius * math.sin(
                    angle_rad
                )  # Y is inverted in painter coords

                painter.setPen(QPen(color, 2, Qt.PenStyle.DashLine))
                painter.drawLine(center, QPointF(line_end_x, line_end_y))

                # Main label position
                label_x = center.x() + (radius + label_offset_from_edge) * math.cos(
                    angle_rad
                )
                label_y = center.y() - (radius + label_offset_from_edge) * math.sin(
                    angle_rad
                )

                painter.setPen(color)  # Label color same as line

                # Draw primary label
                painter.setFont(cardinal_label_font)
                painter.drawText(QPointF(label_x - 10, label_y), label_text)

                # Draw zodiac label if available
                if zodiac_text:
                    painter.setFont(zodiac_label_font)
                    painter.drawText(QPointF(label_x - 10, label_y + 15), zodiac_text)

    def _draw_galactic_center(self, painter, center, radius):
        """Draw the Galactic Center line and label."""
        gc_color = QColor("gold")
        gc_label_text = "GC"
        gc_label_font = QFont("Arial", 10, QFont.Weight.Bold)
        zodiac_label_font = QFont("Arial", 8, QFont.Weight.Normal)
        label_offset_from_edge = 15

        # Convert Azimuth to Cartesian angle
        angle_rad_gc = math.radians(90.0 - self._gc_azimuth_for_drawing)

        # Line endpoint on the circle circumference
        line_end_x_gc = center.x() + radius * math.cos(angle_rad_gc)
        line_end_y_gc = center.y() - radius * math.sin(angle_rad_gc)  # Y is inverted

        painter.setPen(QPen(gc_color, 2, Qt.PenStyle.SolidLine))  # Solid line for GC
        painter.drawLine(center, QPointF(line_end_x_gc, line_end_y_gc))

        # Label position
        label_x_gc = center.x() + (radius + label_offset_from_edge) * math.cos(
            angle_rad_gc
        )
        label_y_gc = center.y() - (radius + label_offset_from_edge) * math.sin(
            angle_rad_gc
        )

        painter.setPen(gc_color)

        # Draw GC label
        painter.setFont(gc_label_font)
        painter.drawText(QPointF(label_x_gc - 10, label_y_gc), gc_label_text)

        # Draw zodiac label if available
        if self._gc_zodiac_label:
            painter.setFont(zodiac_label_font)
            painter.drawText(
                QPointF(label_x_gc - 10, label_y_gc + 15), self._gc_zodiac_label
            )

    def _draw_markers(self, painter, center, radius, hole_coords, hole_rad):
        """Draw the markers with their zodiac labels."""
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

            for hole_num, position in self._hole_zodiac_positions.items():
                if hole_num in self._marker_positions.values():
                    # Skip holes with markers - they'll get their own labels later
                    continue

                # Use the exact hole position from the pre-calculated coordinates
                hole_point = hole_coords[hole_num]

                # Calculate the angle from the circle center (same center used for drawing the holes)
                angle = math.atan2(
                    hole_point.y() - center.y(), hole_point.x() - center.x()
                )

                # Calculate label position based on the same center and angle
                label_radius = (
                    radius + 25
                )  # Increased distance from circle edge for better separation
                label_x = center.x() + label_radius * math.cos(angle)
                label_y = center.y() + label_radius * math.sin(angle)

                # Draw a connecting line from hole to label - straight from hole position to label
                line_color = QColor(150, 150, 150, 80)  # More transparent line
                painter.setPen(QPen(line_color, 0.5, Qt.PenStyle.DotLine))
                painter.drawLine(hole_point, QPointF(label_x, label_y))

                # Draw a small background for zodiac text
                text_width = painter.fontMetrics().horizontalAdvance(position)
                text_height = painter.fontMetrics().height()

                # Show all hole labels
                text_bg = QColor(20, 20, 40, 150)  # More transparent background
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(text_bg))
                painter.drawRoundedRect(
                    QRectF(
                        label_x - 3,
                        label_y - text_height + 3,
                        text_width + 6,
                        text_height + 2,
                    ),
                    3,
                    3,
                )

                # Draw the text
                painter.setPen(QColor(200, 200, 220))
                painter.drawText(QPointF(label_x, label_y), position)

                # Draw the hole number at a slight offset to prevent overlap
                hole_num_text = f"{hole_num}"
                painter.setPen(QColor(150, 150, 170))
                painter.drawText(QPointF(label_x - 15, label_y), hole_num_text)

        # Now draw markers and their zodiacal labels
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
                    # Calculate angle from center to marker - using the same center as for holes
                    angle = math.atan2(
                        marker_qpoint.y() - center.y(), marker_qpoint.x() - center.x()
                    )

                    # Position label outward from marker using the calculated angle
                    offset_distance = marker_radius * 2.5
                    label_x = marker_qpoint.x() + math.cos(angle) * offset_distance
                    label_y = marker_qpoint.y() + math.sin(angle) * offset_distance

                    # Create background for better readability
                    painter.setFont(zodiac_font)
                    text_metrics = painter.fontMetrics()
                    text_width = text_metrics.horizontalAdvance(zodiac_position)
                    text_height = text_metrics.height()

                    # Draw text background
                    bg_rect = QRectF(
                        label_x - 5,
                        label_y - text_height + 5,
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
                    painter.drawText(QPointF(label_x, label_y), zodiac_position)
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

    # Example cardinal points (Azimuths: N=0, E=90, S=180, W=270)
    test_cardinal_azimuths = {
        "VE_az": 90.0,  # Vernal Equinox (East)
        "SS_az": 0.0,  # Summer Solstice (North - for Northern Hemisphere typically)
        "AE_az": 270.0,  # Autumnal Equinox (West)
        "WS_az": 180.0,  # Winter Solstice (South)
    }
    circle_view.set_cardinal_point_azimuths(test_cardinal_azimuths)

    # Example zodiac labels
    circle_view.set_cardinal_point_zodiac_labels(
        {
            "VE_az": "Aries 0.0°",
            "SS_az": "Cancer 0.0°",
            "AE_az": "Libra 0.0°",
            "WS_az": "Capricorn 0.0°",
        }
    )

    # Set GC zodiac
    circle_view.set_galactic_center_zodiac("Sagittarius 26.4°")

    circle_view.set_orientation(45)  # Test with an offset orientation for Hole 0

    window.setGeometry(100, 100, 500, 500)
    window.setWindowTitle(
        "Stonehenge Circle View Test with Cardinal Lines and Zodiac Labels"
    )
    window.show()
    sys.exit(app.exec())
