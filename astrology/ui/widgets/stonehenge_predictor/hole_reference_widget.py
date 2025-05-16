"""
Displays a table of all Stonehenge hole markers with their degree numbers and zodiacal positions.

Author: IsopGemini
Created: 2024-08-08
Last Modified: 2024-08-08
Dependencies: PyQt6
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class HoleReferenceWidget(QWidget):
    """
    A widget that displays a table of all 56 holes with their degree numbers and zodiacal positions.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._hole_zodiac_positions = {}  # Store zodiacal positions for each hole
        self._marker_positions = {}  # Store marker positions

    def _init_ui(self):
        """Initialize the widget UI components."""
        layout = QVBoxLayout(self)

        # Add title and description
        title_label = QLabel("Stonehenge Hole Reference")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")

        description_label = QLabel(
            "This table shows all 56 Aubrey Holes with their numerical degrees and zodiacal positions. "
            "The zodiacal positions are calculated based on the Galactic Center alignment, "
            "with Hole 0 aligned to the Galactic Center position."
        )
        description_label.setWordWrap(True)

        # Create marker legend
        legend_layout = QHBoxLayout()
        legend_label = QLabel("Markers: ")
        legend_label.setStyleSheet("font-weight: bold;")

        marker_labels = {"S": "Sun", "M": "Moon", "N": "North Node", "N'": "South Node"}

        for marker, description in marker_labels.items():
            marker_text = QLabel(f"{marker} = {description}")
            marker_text.setStyleSheet("padding-right: 15px;")
            legend_layout.addWidget(marker_text)

        legend_layout.addStretch()

        # Add to layout
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addLayout(legend_layout)

        # Create table widget
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)  # Added marker column
        self.table.setHorizontalHeaderLabels(
            ["Hole Number", "Degree", "Zodiacal Position", "Marker"]
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)  # Enable sorting

        # Set column stretching
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # Initialize with empty rows
        self._populate_hole_numbers()

        layout.addWidget(self.table)

    def _populate_hole_numbers(self):
        """Populate the table with hole numbers (0-55) and their degrees."""
        hole_count = 56  # Number of Aubrey Holes at Stonehenge
        degrees_per_hole = (
            360 / hole_count
        )  # Each hole represents this many degrees of the circle

        self.table.setRowCount(hole_count)

        for i in range(hole_count):
            # Hole number
            hole_item = QTableWidgetItem(str(i))
            hole_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, hole_item)

            # Degree (0-360)
            degree = i * degrees_per_hole
            degree_item = QTableWidgetItem(f"{degree:.2f}°")
            degree_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Store raw degree value for proper sorting
            degree_item.setData(Qt.ItemDataRole.UserRole, degree)
            self.table.setItem(i, 1, degree_item)

            # Zodiacal position (empty until set)
            position_item = QTableWidgetItem("Not set")
            position_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, position_item)

            # Marker (empty by default)
            marker_item = QTableWidgetItem("")
            marker_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 3, marker_item)

    def update_marker_positions(self, marker_positions):
        """
        Update the table to show which holes have markers.

        Args:
            marker_positions (dict): Dictionary mapping marker names (S, M, N, N') to hole numbers.
        """
        self._marker_positions = marker_positions

        # First clear all marker cells
        for i in range(self.table.rowCount()):
            self.table.item(i, 3).setText("")

        # Then set the marker names
        for marker, hole_num in marker_positions.items():
            if 0 <= hole_num < self.table.rowCount():
                self.table.item(hole_num, 3).setText(marker)

                # Highlight rows with markers
                for col in range(self.table.columnCount()):
                    item = self.table.item(hole_num, col)
                    if item:
                        item.setBackground(
                            QColor(230, 230, 250, 100)
                        )  # Subtle highlight

    def update_zodiacal_positions(self, hole_zodiac_positions):
        """
        Update the table with zodiacal positions for all holes.

        Args:
            hole_zodiac_positions (dict): Dictionary mapping hole numbers to zodiacal positions.
        """
        self._hole_zodiac_positions = hole_zodiac_positions

        for hole_num, position in hole_zodiac_positions.items():
            if 0 <= hole_num < self.table.rowCount():
                position_item = QTableWidgetItem(position)
                position_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(hole_num, 2, position_item)

                # Color code by zodiac sign
                if position and " " in position:
                    sign = position.split(" ")[0]
                    background_color = self._get_zodiac_color(sign)
                    position_item.setBackground(background_color)

                    # Store zodiac sign for sorting
                    zodiac_order = self._get_zodiac_order(sign)
                    degree = float(position.split(" ")[1].replace("°", ""))
                    sort_value = zodiac_order + (degree / 30.0)
                    position_item.setData(Qt.ItemDataRole.UserRole, sort_value)

    def _get_zodiac_order(self, sign):
        """Return numerical order (0-11) of zodiac sign for sorting."""
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
        try:
            return signs.index(sign)
        except ValueError:
            return 0

    def _get_zodiac_color(self, sign):
        """Return a color associated with each zodiac sign."""
        colors = {
            "Aries": QColor(255, 100, 100, 80),
            "Taurus": QColor(100, 200, 100, 80),
            "Gemini": QColor(255, 255, 100, 80),
            "Cancer": QColor(200, 200, 255, 80),
            "Leo": QColor(255, 160, 50, 80),
            "Virgo": QColor(200, 230, 150, 80),
            "Libra": QColor(210, 180, 255, 80),
            "Scorpio": QColor(150, 60, 150, 80),
            "Sagittarius": QColor(255, 150, 80, 80),
            "Capricorn": QColor(100, 100, 100, 80),
            "Aquarius": QColor(100, 180, 255, 80),
            "Pisces": QColor(150, 210, 255, 80),
        }
        return colors.get(
            sign, QColor(200, 200, 200, 80)
        )  # Default gray if sign not found
