"""
Purpose: Widget for displaying personal sensitive points in a chart.

This file provides a visualization of personal sensitive points,
which are degrees where multiple midpoints converge.

Key components:
- SensitivePointsWidget: Widget for displaying personal sensitive points

Dependencies:
- PyQt6: For UI components
- loguru: For logging
- astrology.models: For astrological data models
"""

from collections import defaultdict
from typing import List, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from astrology.models.chart import Chart


class SensitivePointsWidget(QWidget):
    """Widget for displaying personal sensitive points."""

    def __init__(self, chart: Chart):
        """Initialize the sensitive points widget.

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
        self.orb = 1.0  # Default orb for sensitive points (in degrees)
        self.min_midpoints = (
            3  # Minimum number of midpoints to consider a degree sensitive
        )
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Add controls
        controls_layout = QHBoxLayout()

        # Orb selector
        orb_label = QLabel("Orb (degrees):")
        controls_layout.addWidget(orb_label)

        self.orb_spin = QSpinBox()
        self.orb_spin.setMinimum(1)
        self.orb_spin.setMaximum(5)
        self.orb_spin.setValue(int(self.orb))
        self.orb_spin.valueChanged.connect(self._on_orb_changed)
        controls_layout.addWidget(self.orb_spin)

        # Minimum midpoints selector
        min_midpoints_label = QLabel("Minimum midpoints:")
        controls_layout.addWidget(min_midpoints_label)

        self.min_midpoints_spin = QSpinBox()
        self.min_midpoints_spin.setMinimum(2)
        self.min_midpoints_spin.setMaximum(10)
        self.min_midpoints_spin.setValue(self.min_midpoints)
        self.min_midpoints_spin.valueChanged.connect(self._on_min_midpoints_changed)
        controls_layout.addWidget(self.min_midpoints_spin)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Add explanation
        explanation = QLabel(
            "Personal sensitive points are degrees where multiple midpoints converge. "
            "These points represent areas of heightened sensitivity in the chart, "
            "often correlating with significant life events when activated by transits."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet(
            "font-style: italic; color: #666; margin: 10px 0; padding: 5px;"
        )
        explanation.setMinimumHeight(50)  # Ensure enough height for wrapped text
        layout.addWidget(explanation)

        # Create table for sensitive points
        self.points_table = QTableWidget()
        self.points_table.setColumnCount(3)
        self.points_table.setHorizontalHeaderLabels(
            ["Degree", "Midpoints", "Interpretation"]
        )

        # Set column widths
        header = self.points_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.points_table)

        # Update the sensitive points
        self._update_sensitive_points()

    def _on_orb_changed(self, value):
        """Handle orb value change.

        Args:
            value: New orb value
        """
        self.orb = float(value)
        self._update_sensitive_points()

    def _on_min_midpoints_changed(self, value):
        """Handle minimum midpoints value change.

        Args:
            value: New minimum midpoints value
        """
        self.min_midpoints = value
        self._update_sensitive_points()

    def _update_sensitive_points(self):
        """Update the sensitive points table."""
        # Get the kerykeion subject
        subject = self.chart.kerykeion_subject
        if not subject:
            self.points_table.setRowCount(0)
            return

        # Calculate all midpoints
        all_midpoints = self._calculate_all_midpoints(subject)

        # Find sensitive points
        sensitive_points = self._find_sensitive_points(all_midpoints)

        # Set the number of rows
        self.points_table.setRowCount(len(sensitive_points))

        # Fill the table
        for i, (degree, midpoints) in enumerate(sensitive_points):
            # Degree
            degree_item = QTableWidgetItem(
                f"{int(degree)}° {self._get_sign_for_position(degree)}"
            )
            degree_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.points_table.setItem(i, 0, degree_item)

            # Midpoints
            midpoints_text = ", ".join([f"{m[0]}/{m[1]}" for m in midpoints])
            midpoints_item = QTableWidgetItem(midpoints_text)
            midpoints_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.points_table.setItem(i, 1, midpoints_item)

            # Interpretation
            interpretation = self._interpret_sensitive_point(degree, midpoints)
            interp_item = QTableWidgetItem(interpretation)
            interp_item.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            self.points_table.setItem(i, 2, interp_item)

        # Enable word wrap for the interpretation column
        self.points_table.setWordWrap(True)
        self.points_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.points_table.resizeRowsToContents()

    def _calculate_all_midpoints(self, subject) -> List[Tuple[float, Tuple[str, str]]]:
        """Calculate all midpoints between traditional planets.

        Args:
            subject: The kerykeion subject

        Returns:
            List of tuples (midpoint_position, (planet1, planet2))
        """
        midpoints = []

        # Calculate midpoints between all planet pairs
        for i, planet1_name in enumerate(self.traditional_planets):
            if not hasattr(subject, planet1_name):
                continue

            planet1 = getattr(subject, planet1_name)
            pos1 = planet1.position + (planet1.sign_num * 30)

            for j, planet2_name in enumerate(self.traditional_planets[i + 1 :], i + 1):
                if not hasattr(subject, planet2_name):
                    continue

                planet2 = getattr(subject, planet2_name)
                pos2 = planet2.position + (planet2.sign_num * 30)

                # Calculate midpoint
                midpoint_pos = self._calculate_midpoint(pos1, pos2)

                # Add to list
                midpoints.append((midpoint_pos, (planet1_name, planet2_name)))

        return midpoints

    def _find_sensitive_points(
        self, midpoints: List[Tuple[float, Tuple[str, str]]]
    ) -> List[Tuple[float, List[Tuple[str, str]]]]:
        """Find sensitive points where multiple midpoints converge.

        Args:
            midpoints: List of midpoints

        Returns:
            List of tuples (degree, list_of_midpoints)
        """
        # Group midpoints by degree (rounded to nearest degree)
        degree_groups = defaultdict(list)

        for pos, planets in midpoints:
            # Check all degrees within the orb
            for offset in range(-int(self.orb), int(self.orb) + 1):
                degree = (int(pos) + offset) % 360
                degree_groups[degree].append(planets)

        # Filter to degrees with at least min_midpoints midpoints
        sensitive_points = []
        for degree, midpoint_list in degree_groups.items():
            if len(midpoint_list) >= self.min_midpoints:
                # Remove duplicates
                unique_midpoints = list(set(midpoint_list))
                sensitive_points.append((degree, unique_midpoints))

        # Sort by degree
        return sorted(sensitive_points, key=lambda x: x[0])

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

    def _interpret_sensitive_point(
        self, degree: float, midpoints: List[Tuple[str, str]]
    ) -> str:
        """Interpret a sensitive point.

        Args:
            degree: Degree of the sensitive point
            midpoints: List of midpoints at this degree

        Returns:
            Interpretation text
        """
        # Get the sign and house information
        sign = self._get_sign_for_position(degree)

        # Create interpretation based on the number and type of midpoints
        num_midpoints = len(midpoints)

        if num_midpoints >= 5:
            intensity = "extremely"
        elif num_midpoints >= 4:
            intensity = "very"
        else:
            intensity = "significantly"

        # Check which planets are involved
        planets_involved = set()
        for p1, p2 in midpoints:
            planets_involved.add(p1)
            planets_involved.add(p2)

        # Create planet-specific interpretation
        planet_themes = []
        if "sun" in planets_involved:
            planet_themes.append("identity and vitality")
        if "moon" in planets_involved:
            planet_themes.append("emotions and instincts")
        if "mercury" in planets_involved:
            planet_themes.append("communication and thinking")
        if "venus" in planets_involved:
            planet_themes.append("relationships and values")
        if "mars" in planets_involved:
            planet_themes.append("action and drive")
        if "jupiter" in planets_involved:
            planet_themes.append("growth and expansion")
        if "saturn" in planets_involved:
            planet_themes.append("structure and responsibility")

        themes_text = ", ".join(planet_themes)

        # Create the interpretation
        interpretation = (
            f"This degree at {int(degree)}° {sign} is {intensity} sensitive in your chart. "
            f"It represents a focal point where themes of {themes_text} converge. "
            f"When activated by transits, this point may trigger significant events or realizations "
            f"related to these themes."
        )

        return interpretation
