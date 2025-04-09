"""
Purpose: Provides a widget for displaying planetary positions in a table format.

This file is part of the astrology pillar and serves as a UI component.
It provides a widget for displaying planetary positions, signs, houses,
and other information in a tabular format.

Key components:
- PlanetaryPositionsWidget: Widget for displaying planetary positions

Dependencies:
- PyQt6: For UI components
- astrology.models: For astrological data models
"""

from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel
)
from PyQt6.QtGui import QFont, QColor

from loguru import logger

from astrology.models.chart import Chart
from astrology.models.zodiac import Planet

# Import kerykeion for direct access to its data structures
from kerykeion import AstrologicalSubject


class PlanetaryPositionsWidget(QWidget):
    """Widget for displaying planetary positions in a table format."""

    def __init__(self, parent=None):
        """Initialize the planetary positions widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Chart data
        self.chart = None

        # Initialize UI
        self._init_ui()

        logger.debug("PlanetaryPositionsWidget initialized")

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Planet", "Sign", "Position", "Retrograde", "House", "Speed"
        ])

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        # Add table to layout
        layout.addWidget(self.table)

        # Add a note about retrograde motion
        note = QLabel("R = Retrograde motion (planet appears to move backward)")
        note.setStyleSheet("font-style: italic; color: #666;")
        layout.addWidget(note)

    def set_chart(self, chart: Chart) -> None:
        """Set the chart to display.

        Args:
            chart: The chart to display
        """
        self.chart = chart
        self._update_table()

    def _update_table(self):
        """Update the table with the current chart data."""
        if not self.chart or not self.chart.kerykeion_subject:
            self.table.setRowCount(0)
            return

        # Get the kerykeion subject directly
        subject = self.chart.kerykeion_subject
        logger.debug(f"Updating planet table from kerykeion subject: {subject.name}")

        # Define the planets to display in order
        # Check if we're in heliocentric mode
        is_heliocentric = hasattr(subject, 'perspective_type') and subject.perspective_type == "Heliocentric"
        logger.debug(f"Perspective type: {getattr(subject, 'perspective_type', 'Unknown')}")

        if is_heliocentric:
            # In heliocentric mode, Earth is shown instead of Sun, and Moon is not shown
            planet_names = [
                "earth", "mercury", "venus", "mars",
                "jupiter", "saturn", "uranus", "neptune", "pluto",
                "mean_node", "true_node", "chiron"
            ]
            logger.debug("Using heliocentric planet list (Earth instead of Sun, no Moon)")
        else:
            # Standard geocentric mode
            planet_names = [
                "sun", "moon", "mercury", "venus", "mars",
                "jupiter", "saturn", "uranus", "neptune", "pluto",
                "mean_node", "true_node", "chiron"
            ]

        # Get all available planets from the subject
        planets = []
        for planet_name in planet_names:
            if hasattr(subject, planet_name):
                planet = getattr(subject, planet_name)
                planets.append((planet_name, planet))
                logger.debug(f"Found planet {planet_name}: {planet.sign} at {planet.position}°")

        # Set the number of rows
        self.table.setRowCount(len(planets))

        # Fill the table
        for i, (planet_name, planet) in enumerate(planets):
            # Planet name (capitalize and format)
            display_name = planet_name.replace('_', ' ').title()
            name_item = QTableWidgetItem(display_name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, name_item)

            # Sign
            sign_item = QTableWidgetItem(planet.sign)
            sign_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 1, sign_item)

            # Position
            # Format as degrees, minutes, seconds
            degrees = int(planet.position)
            minutes = int((planet.position - degrees) * 60)
            seconds = int(((planet.position - degrees) * 60 - minutes) * 60)

            position_str = f"{degrees}° {minutes:02d}' {seconds:02d}\""

            position_item = QTableWidgetItem(position_str)
            position_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, position_item)

            # Retrograde
            is_retrograde = hasattr(planet, 'retrograde') and planet.retrograde
            retrograde_item = QTableWidgetItem("R" if is_retrograde else "")
            retrograde_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_retrograde:
                retrograde_item.setForeground(QColor(255, 0, 0))  # Red for retrograde
            self.table.setItem(i, 3, retrograde_item)

            # House
            if hasattr(planet, 'house'):
                house_display = planet.house
                if isinstance(house_display, str) and "_" in house_display:
                    # Format like "First_House" to "1"
                    house_display = house_display.split('_')[0]
                    # Convert "First" to "1", etc.
                    house_map = {
                        "First": "1", "Second": "2", "Third": "3", "Fourth": "4",
                        "Fifth": "5", "Sixth": "6", "Seventh": "7", "Eighth": "8",
                        "Ninth": "9", "Tenth": "10", "Eleventh": "11", "Twelfth": "12"
                    }
                    if house_display in house_map:
                        house_display = house_map[house_display]

                house_item = QTableWidgetItem(str(house_display))
                house_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 4, house_item)
            else:
                self.table.setItem(i, 4, QTableWidgetItem(""))

            # Speed
            if hasattr(planet, 'speed'):
                speed_str = f"{planet.speed:.2f}°/day"
                speed_item = QTableWidgetItem(speed_str)
                speed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, 5, speed_item)
            else:
                self.table.setItem(i, 5, QTableWidgetItem(""))

    def sizeHint(self):
        """Get the suggested size for the widget.

        Returns:
            Suggested size
        """
        return QSize(600, 400)

    def minimumSizeHint(self):
        """Get the minimum suggested size for the widget.

        Returns:
            Minimum suggested size
        """
        return QSize(400, 300)
