"""
Purpose: Widget for displaying midpoint trees and planetary pictures.

This file provides a visualization of midpoint trees for each planet,
showing all midpoints that involve that planet and their interpretations.

Key components:
- MidpointTreeWidget: Widget for displaying midpoint trees and planetary pictures

Dependencies:
- PyQt6: For UI components
- loguru: For logging
- astrology.models: For astrological data models
"""

from typing import Dict, List, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from astrology.models.chart import Chart


class MidpointTreeWidget(QWidget):
    """Widget for displaying midpoint trees and planetary pictures."""

    def __init__(self, chart: Chart):
        """Initialize the midpoint tree widget.

        Args:
            chart: The chart to display
        """
        super().__init__()
        self.chart = chart
        self.traditional_planets = [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
        ]
        self.selected_planet = "sun"  # Default selected planet
        self.midpoint_interpretations = self._initialize_interpretations()
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Add controls
        controls_layout = QHBoxLayout()

        # Planet selector
        planet_label = QLabel("Select Planet:")
        controls_layout.addWidget(planet_label)

        self.planet_combo = QComboBox()
        self.planet_combo.addItems([p.capitalize() for p in self.traditional_planets])
        self.planet_combo.currentIndexChanged.connect(self._on_planet_changed)
        controls_layout.addWidget(self.planet_combo)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Add explanation
        explanation = QLabel(
            "Midpoint trees show all midpoints involving the selected planet. "
            "These combinations reveal deeper patterns in the chart that may not be "
            "visible through traditional aspect analysis."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet(
            "font-style: italic; color: #666; margin: 10px 0; padding: 5px;"
        )
        explanation.setMinimumHeight(50)  # Ensure enough height for wrapped text
        layout.addWidget(explanation)

        # Create scroll area for the tree
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Create container for the tree
        self.tree_container = QWidget()
        self.tree_layout = QVBoxLayout(self.tree_container)
        scroll_area.setWidget(self.tree_container)

        # Create table for midpoint tree
        self.tree_table = QTableWidget()
        self.tree_table.setColumnCount(3)
        self.tree_table.setHorizontalHeaderLabels(
            ["Midpoint", "Position", "Interpretation"]
        )

        # Set column widths
        header = self.tree_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.tree_layout.addWidget(self.tree_table)

        # Update the tree for the default planet
        self._update_tree()

    def _on_planet_changed(self, index):
        """Handle planet selection change.

        Args:
            index: Index of the selected planet
        """
        if 0 <= index < len(self.traditional_planets):
            self.selected_planet = self.traditional_planets[index]
            self._update_tree()

    def _update_tree(self):
        """Update the midpoint tree for the selected planet."""
        # Get the kerykeion subject
        subject = self.chart.kerykeion_subject
        if not subject or not hasattr(subject, self.selected_planet):
            self.tree_table.setRowCount(0)
            return

        # Calculate midpoints for the selected planet
        midpoints = self._calculate_midpoints_for_planet(subject, self.selected_planet)

        # Set the number of rows
        self.tree_table.setRowCount(len(midpoints))

        # Fill the table
        for i, (midpoint_name, position, sign, interpretation) in enumerate(midpoints):
            # Midpoint name
            name_item = QTableWidgetItem(midpoint_name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tree_table.setItem(i, 0, name_item)

            # Position
            position_item = QTableWidgetItem(f"{position:.2f}° {sign}")
            position_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tree_table.setItem(i, 1, position_item)

            # Interpretation
            interp_item = QTableWidgetItem(interpretation)
            interp_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.tree_table.setItem(i, 2, interp_item)

        # Enable word wrap for the interpretation column
        self.tree_table.setWordWrap(True)
        self.tree_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.tree_table.resizeRowsToContents()

    def _calculate_midpoints_for_planet(
        self, subject, planet_name: str
    ) -> List[Tuple[str, float, str, str]]:
        """Calculate midpoints involving the selected planet.

        Args:
            subject: The kerykeion subject
            planet_name: Name of the selected planet

        Returns:
            List of tuples (midpoint_name, position, sign, interpretation)
        """
        midpoints = []

        # Get the selected planet
        if not hasattr(subject, planet_name):
            return midpoints

        selected_planet = getattr(subject, planet_name)
        selected_pos = selected_planet.position + (selected_planet.sign_num * 30)

        # Calculate midpoints with other planets
        for other_name in self.traditional_planets:
            if other_name == planet_name or not hasattr(subject, other_name):
                continue

            other_planet = getattr(subject, other_name)
            other_pos = other_planet.position + (other_planet.sign_num * 30)

            # Calculate midpoint
            midpoint_pos = self._calculate_midpoint(selected_pos, other_pos)

            # Get sign for the midpoint
            sign = self._get_sign_for_position(midpoint_pos)

            # Get position within sign (0-30)
            pos_in_sign = midpoint_pos % 30

            # Get interpretation
            interpretation = self._get_midpoint_interpretation(planet_name, other_name)

            # Format midpoint name
            midpoint_name = f"{planet_name.capitalize()}/{other_name.capitalize()}"

            midpoints.append((midpoint_name, pos_in_sign, sign, interpretation))

        return sorted(midpoints, key=lambda x: x[1])  # Sort by position

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

        sign_index = int(position / 30)
        return signs[sign_index]

    def _get_midpoint_interpretation(self, planet1: str, planet2: str) -> str:
        """Get the interpretation for a midpoint.

        Args:
            planet1: First planet name
            planet2: Second planet name

        Returns:
            Interpretation text
        """
        # Sort planet names to ensure consistent lookup
        planets = sorted([planet1, planet2])
        key = f"{planets[0]}_{planets[1]}"

        return self.midpoint_interpretations.get(key, "No interpretation available.")

    def _initialize_interpretations(self) -> Dict[str, str]:
        """Initialize midpoint interpretations.

        Returns:
            Dictionary of midpoint interpretations
        """
        interpretations = {
            "sun_moon": "The integration of conscious will and emotional needs. Represents core identity and emotional fulfillment.",
            "sun_mercury": "The integration of identity and communication. Represents self-expression and intellectual identity.",
            "sun_venus": "The integration of identity and values. Represents creative expression, love nature, and aesthetic sensibility.",
            "sun_mars": "The integration of will and action. Represents drive, ambition, and how one asserts oneself.",
            "sun_jupiter": "The integration of identity and expansion. Represents growth, optimism, and personal philosophy.",
            "sun_saturn": "The integration of identity and structure. Represents discipline, responsibility, and life purpose.",
            "moon_mercury": "The integration of emotions and communication. Represents emotional expression and intuitive thinking.",
            "moon_venus": "The integration of emotions and values. Represents emotional harmony, nurturing relationships, and aesthetic sensitivity.",
            "moon_mars": "The integration of emotions and action. Represents emotional drive, passion, and instinctive reactions.",
            "moon_jupiter": "The integration of emotions and expansion. Represents emotional growth, nurturing abundance, and emotional wisdom.",
            "moon_saturn": "The integration of emotions and structure. Represents emotional maturity, emotional boundaries, and inner security.",
            "mercury_venus": "The integration of communication and values. Represents artistic expression, diplomatic communication, and aesthetic thinking.",
            "mercury_mars": "The integration of communication and action. Represents decisive thinking, debate skills, and intellectual courage.",
            "mercury_jupiter": "The integration of communication and expansion. Represents broad thinking, teaching ability, and philosophical communication.",
            "mercury_saturn": "The integration of communication and structure. Represents disciplined thinking, serious communication, and practical planning.",
            "venus_mars": "The integration of values and action. Represents creative drive, romantic passion, and artistic initiative.",
            "venus_jupiter": "The integration of values and expansion. Represents social grace, artistic growth, and relationship abundance.",
            "venus_saturn": "The integration of values and structure. Represents enduring relationships, artistic discipline, and mature values.",
            "mars_jupiter": "The integration of action and expansion. Represents ambitious drive, entrepreneurial spirit, and expansive energy.",
            "mars_saturn": "The integration of action and structure. Represents disciplined effort, strategic action, and enduring strength.",
            "jupiter_saturn": "The integration of expansion and structure. Represents balanced growth, practical wisdom, and sustainable success.",
        }

        return interpretations
