"""
Purpose: Widget for displaying harmonic dials.

This file provides a visualization of midpoints in harmonic format,
allowing users to see patterns that might be missed in a traditional chart.

Key components:
- HarmonicDialWidget: Widget for displaying harmonic dials

Dependencies:
- PyQt6: For UI components
- loguru: For logging
- astrology.models: For astrological data models
"""

import math
from typing import List, Dict, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QFrame, QSpinBox, QToolTip
)
from PyQt6.QtCore import Qt, QRectF, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush, QMouseEvent

from loguru import logger

from astrology.models.chart import Chart


class HarmonicDialWidget(QWidget):
    """Widget for displaying harmonic dials."""

    def __init__(self, chart: Chart):
        """Initialize the harmonic dial widget.

        Args:
            chart: The chart to display
        """
        super().__init__()
        self.chart = chart
        self.harmonic = 4  # Default to 90° dial (4th harmonic)
        self.traditional_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
        self.planet_colors = {
            "sun": QColor("#FFD700"),      # Gold
            "moon": QColor("#C0C0C0"),     # Silver
            "mercury": QColor("#708090"),  # Slate Gray
            "venus": QColor("#00FF7F"),    # Spring Green
            "mars": QColor("#FF4500"),     # Orange Red
            "jupiter": QColor("#4169E1"),  # Royal Blue
            "saturn": QColor("#708090")    # Slate Gray
        }

        # Store planet and midpoint positions for tooltips
        self.planet_positions = {}
        self.midpoint_positions = {}

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Add controls
        controls_layout = QHBoxLayout()

        # Harmonic selector
        harmonic_label = QLabel("Harmonic:")
        controls_layout.addWidget(harmonic_label)

        self.harmonic_spin = QSpinBox()
        self.harmonic_spin.setMinimum(1)
        self.harmonic_spin.setMaximum(360)
        self.harmonic_spin.setValue(4)  # Default to 4th harmonic (90° dial)
        self.harmonic_spin.valueChanged.connect(self._on_harmonic_changed)
        controls_layout.addWidget(self.harmonic_spin)

        # Common harmonic presets
        preset_label = QLabel("Presets:")
        controls_layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "90° Dial (4th Harmonic)",
            "45° Dial (8th Harmonic)",
            "30° Dial (12th Harmonic)",
            "22.5° Dial (16th Harmonic)",
            "15° Dial (24th Harmonic)",
            "10° Dial (36th Harmonic)"
        ])
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        controls_layout.addWidget(self.preset_combo)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Add explanation
        explanation = QLabel(
            "Harmonic dials compress the chart into a smaller arc, "
            "making it easier to see midpoint structures. "
            "Points that align vertically form significant midpoint relationships."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet("font-style: italic; color: #666; margin: 10px 0; padding: 5px;")
        explanation.setMinimumHeight(50)  # Ensure enough height for wrapped text
        layout.addWidget(explanation)

        # Add dial display
        self.dial_frame = QFrame()
        self.dial_frame.setMinimumHeight(500)  # Increased from 400 to 500
        self.dial_frame.setMinimumWidth(500)  # Added minimum width to ensure circular display
        self.dial_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.dial_frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.dial_frame.setMouseTracking(True)  # Enable mouse tracking for tooltips
        self.dial_frame.paintEvent = self._paint_dial
        self.dial_frame.mouseMoveEvent = self._handle_mouse_move
        layout.addWidget(self.dial_frame)

    def _on_harmonic_changed(self, value):
        """Handle harmonic value change.

        Args:
            value: New harmonic value
        """
        self.harmonic = value
        self.dial_frame.update()

    def _on_preset_changed(self, index):
        """Handle preset selection change.

        Args:
            index: Index of the selected preset
        """
        # Map preset index to harmonic value
        harmonic_values = [4, 8, 12, 16, 24, 36]
        if 0 <= index < len(harmonic_values):
            self.harmonic_spin.setValue(harmonic_values[index])

    def _paint_dial(self, event):
        """Paint the harmonic dial.

        Args:
            event: Paint event
        """
        painter = QPainter(self.dial_frame)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get frame dimensions
        width = self.dial_frame.width()
        height = self.dial_frame.height()

        # Calculate center and radius
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 40

        # Draw outer circle
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawEllipse(QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2))

        # Draw degree markings
        self._draw_degree_markings(painter, center_x, center_y, radius)

        # Draw planets
        self._draw_planets(painter, center_x, center_y, radius)

        # Draw midpoints
        self._draw_midpoints(painter, center_x, center_y, radius)

        painter.end()

    def _draw_degree_markings(self, painter, center_x, center_y, radius):
        """Draw degree markings on the dial.

        Args:
            painter: QPainter object
            center_x: X coordinate of the center
            center_y: Y coordinate of the center
            radius: Radius of the dial
        """
        # Set up pens - increased widths
        major_pen = QPen(QColor("#000000"), 3)  # Increased from 2 to 3
        minor_pen = QPen(QColor("#666666"), 2)  # Increased from 1 to 2
        text_pen = QPen(QColor("#000000"), 2)  # Increased from 1 to 2

        # Calculate degree increment based on harmonic
        increment = 360 / self.harmonic
        degrees_per_mark = max(1, int(increment / 10))  # Adjust mark frequency based on harmonic

        # Draw markings
        for i in range(0, int(increment) + 1, degrees_per_mark):
            angle = i * (360 / increment) / 360 * 2 * math.pi

            # Calculate start and end points
            start_x = center_x + (radius - 10) * math.sin(angle)
            start_y = center_y - (radius - 10) * math.cos(angle)

            # Major markings at multiples of 10 or 5 depending on harmonic
            if i % (degrees_per_mark * 2) == 0:
                painter.setPen(major_pen)
                end_x = center_x + radius * math.sin(angle)
                end_y = center_y - radius * math.cos(angle)

                # Add text for major markings
                text_x = center_x + (radius + 15) * math.sin(angle)
                text_y = center_y - (radius + 15) * math.cos(angle)

                painter.setPen(text_pen)
                painter.setFont(QFont("Arial", 10))  # Increased from 8 to 10
                painter.drawText(int(text_x - 12), int(text_y + 6), f"{i}°")
            else:
                painter.setPen(minor_pen)
                end_x = center_x + (radius - 5) * math.sin(angle)
                end_y = center_y - (radius - 5) * math.cos(angle)

            painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))

    def _draw_planets(self, painter, center_x, center_y, radius):
        """Draw planets on the dial.

        Args:
            painter: QPainter object
            center_x: X coordinate of the center
            center_y: Y coordinate of the center
            radius: Radius of the dial
        """
        # Get the kerykeion subject
        subject = self.chart.kerykeion_subject
        if not subject:
            return

        # Clear previous planet positions
        self.planet_positions = {}

        # Draw each planet
        for planet_name in self.traditional_planets:
            if hasattr(subject, planet_name):
                planet = getattr(subject, planet_name)

                # Get position and convert to harmonic position
                position = planet.position + (planet.sign_num * 30)
                harmonic_position = position % (360 / self.harmonic)

                # Calculate coordinates
                angle = harmonic_position / (360 / self.harmonic) * 2 * math.pi
                x = center_x + radius * 0.8 * math.sin(angle)
                y = center_y - radius * 0.8 * math.cos(angle)

                # Get planet color
                planet_color = self.planet_colors.get(planet_name, QColor("#000000"))

                # Draw planet symbol - increased size
                painter.setPen(QPen(QColor("#000000"), 2))
                painter.setBrush(QBrush(planet_color))
                painter.drawEllipse(int(x - 15), int(y - 15), 30, 30)  # Size: 30x30

                # Draw planet label - increased font size
                painter.setPen(QPen(QColor("#FFFFFF"), 1))
                painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
                painter.drawText(int(x - 7), int(y + 7), planet_name[0].upper())

                # Store planet position and info for tooltip
                self.planet_positions[planet_name] = {
                    "x": x,
                    "y": y,
                    "radius": 15,
                    "label": planet_name.capitalize(),
                    "position": f"{position:.2f}° {self._get_sign_for_position(position)}",
                    "harmonic_position": f"{harmonic_position:.2f}°",
                    "color": planet_color
                }

    def _draw_midpoints(self, painter, center_x, center_y, radius):
        """Draw midpoints on the dial.

        Args:
            painter: QPainter object
            center_x: X coordinate of the center
            center_y: Y coordinate of the center
            radius: Radius of the dial
        """
        # Get the kerykeion subject
        subject = self.chart.kerykeion_subject
        if not subject:
            return

        # Clear previous midpoint positions
        self.midpoint_positions = {}

        # Calculate and draw midpoints
        for i, planet1_name in enumerate(self.traditional_planets):
            if not hasattr(subject, planet1_name):
                continue

            planet1 = getattr(subject, planet1_name)
            pos1 = planet1.position + (planet1.sign_num * 30)

            for j, planet2_name in enumerate(self.traditional_planets[i+1:], i+1):
                if not hasattr(subject, planet2_name):
                    continue

                planet2 = getattr(subject, planet2_name)
                pos2 = planet2.position + (planet2.sign_num * 30)

                # Calculate midpoint
                midpoint = self._calculate_midpoint(pos1, pos2)

                # Convert to harmonic position
                harmonic_midpoint = midpoint % (360 / self.harmonic)

                # Calculate coordinates
                angle = harmonic_midpoint / (360 / self.harmonic) * 2 * math.pi
                x = center_x + radius * 0.7 * math.sin(angle)
                y = center_y - radius * 0.7 * math.cos(angle)

                # Determine color based on planets involved
                # Use a blend of the two planet colors
                color1 = self.planet_colors.get(planet1_name, QColor("#FF00FF"))
                color2 = self.planet_colors.get(planet2_name, QColor("#FF00FF"))
                blended_color = QColor(
                    (color1.red() + color2.red()) // 2,
                    (color1.green() + color2.green()) // 2,
                    (color1.blue() + color2.blue()) // 2
                )

                # Draw connection line
                painter.setPen(QPen(QColor(blended_color.red(), blended_color.green(), blended_color.blue(), 100), 1, Qt.PenStyle.DashLine))
                painter.drawLine(int(center_x), int(center_y), int(x), int(y))

                # Draw midpoint marker with planet-specific color
                painter.setPen(QPen(QColor("#000000"), 1))
                painter.setBrush(QBrush(blended_color))
                painter.drawEllipse(int(x - 5), int(y - 5), 10, 10)  # Size: 10x10

                # Store midpoint position and info for tooltip
                midpoint_key = f"{planet1_name}_{planet2_name}"
                self.midpoint_positions[midpoint_key] = {
                    "x": x,
                    "y": y,
                    "radius": 5,
                    "label": f"{planet1_name.capitalize()}/{planet2_name.capitalize()}",
                    "position": f"{midpoint:.2f}° {self._get_sign_for_position(midpoint)}",
                    "harmonic_position": f"{harmonic_midpoint:.2f}°",
                    "color": blended_color
                }

    def _calculate_midpoint(self, pos1: float, pos2: float) -> float:
        """Calculate the midpoint between two positions.

        Args:
            pos1: First position in degrees
            pos2: Second position in degrees

        Returns:
            The midpoint in degrees
        """
        # Calculate the difference
        diff = abs(pos1 - pos2)

        # If the difference is more than 180 degrees, use the shorter arc
        if diff > 180:
            # Calculate midpoint in the opposite direction
            if pos1 > pos2:
                midpoint = (pos2 + 360 + pos1) / 2
            else:
                midpoint = (pos1 + 360 + pos2) / 2

            # Normalize to 0-360
            midpoint = midpoint % 360
        else:
            # Simple average
            midpoint = (pos1 + pos2) / 2

        return midpoint

    def _get_sign_for_position(self, position: float) -> str:
        """Get the zodiac sign for a position.

        Args:
            position: Position in degrees (0-360)

        Returns:
            The zodiac sign as a string
        """
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

        sign_index = int(position / 30)
        return signs[sign_index]

    def _handle_mouse_move(self, event: QMouseEvent):
        """Handle mouse movement for tooltips.

        Args:
            event: Mouse event
        """
        # Get mouse position
        mouse_x = event.position().x()
        mouse_y = event.position().y()

        # Check if mouse is over any planet
        for planet_name, planet_info in self.planet_positions.items():
            x = planet_info["x"]
            y = planet_info["y"]
            radius = planet_info["radius"]

            # Calculate distance from mouse to planet
            distance = math.sqrt((mouse_x - x) ** 2 + (mouse_y - y) ** 2)

            if distance <= radius:
                # Show tooltip for planet
                tooltip_text = f"<b>{planet_info['label']}</b><br>"
                tooltip_text += f"Position: {planet_info['position']}<br>"
                tooltip_text += f"Harmonic Position: {planet_info['harmonic_position']}"
                QToolTip.showText(self.dial_frame.mapToGlobal(QPoint(int(mouse_x), int(mouse_y))), tooltip_text)
                return

        # Check if mouse is over any midpoint
        for midpoint_key, midpoint_info in self.midpoint_positions.items():
            x = midpoint_info["x"]
            y = midpoint_info["y"]
            radius = midpoint_info["radius"]

            # Calculate distance from mouse to midpoint
            distance = math.sqrt((mouse_x - x) ** 2 + (mouse_y - y) ** 2)

            if distance <= radius:
                # Show tooltip for midpoint
                tooltip_text = f"<b>{midpoint_info['label']}</b><br>"
                tooltip_text += f"Position: {midpoint_info['position']}<br>"
                tooltip_text += f"Harmonic Position: {midpoint_info['harmonic_position']}"
                QToolTip.showText(self.dial_frame.mapToGlobal(QPoint(int(mouse_x), int(mouse_y))), tooltip_text)
                return

        # If not over any point, hide tooltip
        QToolTip.hideText()
