"""
Purpose: Widget for displaying midpoints in a chart.

This file is part of the astrology pillar and provides a UI component.
It displays a table of midpoints between planets in a chart.

Key components:
- MidpointsWidget: Widget for displaying midpoints

Dependencies:
- PyQt6: For UI components
- loguru: For logging
- astrology.models: For astrological data models
"""

from typing import List

from kerykeion import AstrologicalSubject
from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from astrology.models.chart import Chart


class MidpointsWidget(QWidget):
    """Widget for displaying midpoints in a chart."""

    def __init__(self, parent=None):
        """Initialize the midpoints widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.chart = None
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel("Traditional Planetary Midpoints")
        title_label.setStyleSheet("color: #333; font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Planets", "Midpoint", "Sign"])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        # Set minimum size for the table
        self.table.setMinimumHeight(300)
        self.table.setMinimumWidth(500)

        # Add table to layout
        layout.addWidget(self.table)

        # Add a note about midpoints
        note = QLabel(
            "Midpoints represent the halfway point between two planets (showing traditional 7 planets only)"
        )
        note.setStyleSheet("font-style: italic; color: #666;")
        layout.addWidget(note)

        # Debug: Add row count label
        self.row_count_label = QLabel("Rows: 0")
        self.row_count_label.setStyleSheet("color: red;")
        layout.addWidget(self.row_count_label)

    def set_chart(self, chart: Chart):
        """Set the chart and update the table.

        Args:
            chart: The chart to display
        """
        self.chart = chart
        self._update_table()

    def _update_table(self):
        """Update the table with the current chart data."""
        if not self.chart or not self.chart.kerykeion_subject:
            self.table.setRowCount(0)
            self.row_count_label.setText("No chart data available")
            return

        # Get the kerykeion subject directly
        subject = self.chart.kerykeion_subject
        logger.debug(f"Updating midpoints table from kerykeion subject: {subject.name}")

        # Calculate midpoints
        midpoints = self._calculate_midpoints(subject)

        # Set the number of rows
        self.table.setRowCount(len(midpoints))
        self.row_count_label.setText(f"Rows: {self.table.rowCount()}")

        # Fill the table
        for i, (planets, midpoint_pos, sign) in enumerate(midpoints):
            # Planets
            planets_item = QTableWidgetItem(planets)
            planets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, planets_item)

            # Midpoint position
            # Format as degrees, minutes, seconds
            degrees = int(midpoint_pos)
            minutes = int((midpoint_pos - degrees) * 60)
            seconds = int(((midpoint_pos - degrees) * 60 - minutes) * 60)

            position_str = f"{degrees}° {minutes:02d}' {seconds:02d}\""

            position_item = QTableWidgetItem(position_str)
            position_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, position_item)

            # Sign
            sign_item = QTableWidgetItem(sign)
            sign_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, sign_item)

    def _calculate_midpoints(self, subject: AstrologicalSubject) -> List[tuple]:
        """Calculate midpoints between planets.

        Args:
            subject: The kerykeion subject

        Returns:
            A list of tuples (planet_pair, midpoint_position, sign)
        """
        # Define the traditional 7 planets to use for midpoints
        planet_names = [
            "sun",
            "moon",
            "mercury",
            "venus",
            "mars",
            "jupiter",
            "saturn",
        ]  # Traditional 7 planets only

        # Get all available planets from the subject
        planets = []
        for planet_name in planet_names:
            if hasattr(subject, planet_name):
                planet = getattr(subject, planet_name)
                planets.append((planet_name, planet))
                logger.debug(
                    f"Found planet {planet_name}: {planet.sign} at {planet.position}°"
                )

        # Calculate midpoints
        midpoints = []
        for i, (name1, planet1) in enumerate(planets):
            for j, (name2, planet2) in enumerate(planets):
                if j <= i:  # Skip duplicates and reverse pairs
                    continue

                # Calculate absolute positions (0-360)
                abs_pos1 = self._get_absolute_position(planet1)
                abs_pos2 = self._get_absolute_position(planet2)

                # Calculate midpoint
                midpoint = self._calculate_midpoint(abs_pos1, abs_pos2)

                # Get sign for the midpoint
                sign = self._get_sign_for_position(midpoint)

                # Format planet names
                planet_pair = f"{name1.capitalize()}-{name2.capitalize()}"

                # Calculate position within sign (0-30)
                pos_in_sign = midpoint % 30

                midpoints.append((planet_pair, pos_in_sign, sign))

        return midpoints

    def _get_absolute_position(self, planet) -> float:
        """Get the absolute position (0-360) of a planet.

        Args:
            planet: The planet object

        Returns:
            The absolute position in degrees
        """
        # If the planet has abs_pos attribute, use it
        if hasattr(planet, "abs_pos"):
            return planet.abs_pos

        # Otherwise calculate from sign and position
        sign_num = planet.sign_num if hasattr(planet, "sign_num") else 0
        position = planet.position if hasattr(planet, "position") else 0

        return (sign_num * 30) + position

    def _calculate_midpoint(self, pos1: float, pos2: float) -> float:
        """Calculate the midpoint between two positions.

        Args:
            pos1: First position in degrees (0-360)
            pos2: Second position in degrees (0-360)

        Returns:
            The midpoint in degrees (0-360)
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
            "Ari",
            "Tau",
            "Gem",
            "Can",
            "Leo",
            "Vir",
            "Lib",
            "Sco",
            "Sag",
            "Cap",
            "Aqu",
            "Pis",
        ]

        sign_index = int(position / 30)
        return signs[sign_index]
