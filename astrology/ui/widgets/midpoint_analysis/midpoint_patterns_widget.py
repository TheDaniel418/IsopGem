"""
Purpose: Widget for displaying midpoint aspect patterns.

This file provides a visualization of aspect patterns formed by midpoints,
such as midpoint T-squares, grand trines, and other configurations.

Key components:
- MidpointPatternsWidget: Widget for displaying midpoint aspect patterns

Dependencies:
- PyQt6: For UI components
- loguru: For logging
- astrology.models: For astrological data models
"""

import math
from typing import Dict, List, Tuple, Set
from collections import defaultdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from loguru import logger

from astrology.models.chart import Chart


class MidpointPatternsWidget(QWidget):
    """Widget for displaying midpoint aspect patterns."""

    def __init__(self, chart: Chart):
        """Initialize the midpoint patterns widget.

        Args:
            chart: The chart to display
        """
        super().__init__()
        self.chart = chart
        self.traditional_planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
        self.orb = 2.0  # Default orb for aspects (in degrees)
        self.pattern_type = "all"  # Default to show all patterns
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

        # Pattern type selector
        pattern_label = QLabel("Pattern type:")
        controls_layout.addWidget(pattern_label)

        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            "All Patterns",
            "Conjunctions",
            "Oppositions",
            "Squares",
            "T-Squares",
            "Grand Crosses"
        ])
        self.pattern_combo.currentIndexChanged.connect(self._on_pattern_changed)
        controls_layout.addWidget(self.pattern_combo)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Add explanation
        explanation = QLabel(
            "Midpoint aspect patterns reveal complex relationships between planetary energies. "
            "These patterns show how midpoints form significant geometric configurations "
            "that can indicate important themes in the chart."
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet("font-style: italic; color: #666; margin: 10px 0; padding: 5px;")
        explanation.setMinimumHeight(50)  # Ensure enough height for wrapped text
        layout.addWidget(explanation)

        # Create table for patterns
        self.patterns_table = QTableWidget()
        self.patterns_table.setColumnCount(3)
        self.patterns_table.setHorizontalHeaderLabels(["Pattern", "Planets Involved", "Interpretation"])

        # Set column widths
        header = self.patterns_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.patterns_table)

        # Update the patterns
        self._update_patterns()

    def _on_orb_changed(self, value):
        """Handle orb value change.

        Args:
            value: New orb value
        """
        self.orb = float(value)
        self._update_patterns()

    def _on_pattern_changed(self, index):
        """Handle pattern type change.

        Args:
            index: Index of the selected pattern type
        """
        pattern_types = ["all", "conjunction", "opposition", "square", "t-square", "grand-cross"]
        if 0 <= index < len(pattern_types):
            self.pattern_type = pattern_types[index]
            self._update_patterns()

    def _update_patterns(self):
        """Update the patterns table."""
        # Get the kerykeion subject
        subject = self.chart.kerykeion_subject
        if not subject:
            self.patterns_table.setRowCount(0)
            return

        # Calculate all midpoints
        all_midpoints = self._calculate_all_midpoints(subject)

        # Find patterns
        patterns = self._find_patterns(all_midpoints)

        # Filter patterns by type if needed
        if self.pattern_type != "all":
            patterns = [p for p in patterns if p[0].lower() == self.pattern_type]

        # Set the number of rows
        self.patterns_table.setRowCount(len(patterns))

        # Fill the table
        for i, (pattern_type, planets, description) in enumerate(patterns):
            # Pattern type
            type_item = QTableWidgetItem(pattern_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.patterns_table.setItem(i, 0, type_item)

            # Planets involved
            planets_item = QTableWidgetItem(planets)
            planets_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.patterns_table.setItem(i, 1, planets_item)

            # Interpretation
            interp_item = QTableWidgetItem(description)
            interp_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.patterns_table.setItem(i, 2, interp_item)

        # Enable word wrap for the interpretation column
        self.patterns_table.setWordWrap(True)
        self.patterns_table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self.patterns_table.resizeRowsToContents()

    def _calculate_all_midpoints(self, subject) -> Dict[str, float]:
        """Calculate all midpoints between traditional planets.

        Args:
            subject: The kerykeion subject

        Returns:
            Dictionary mapping midpoint names to positions
        """
        midpoints = {}

        # Calculate midpoints between all planet pairs
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
                midpoint_pos = self._calculate_midpoint(pos1, pos2)

                # Add to dictionary
                midpoint_name = f"{planet1_name.capitalize()}/{planet2_name.capitalize()}"
                midpoints[midpoint_name] = midpoint_pos

        return midpoints

    def _find_patterns(self, midpoints: Dict[str, float]) -> List[Tuple[str, str, str]]:
        """Find aspect patterns formed by midpoints.

        Args:
            midpoints: Dictionary of midpoints

        Returns:
            List of tuples (pattern_type, planets_involved, description)
        """
        patterns = []

        # Find conjunctions (midpoints at the same degree)
        conjunctions = self._find_conjunctions(midpoints)
        patterns.extend(conjunctions)

        # Find oppositions (midpoints 180° apart)
        oppositions = self._find_oppositions(midpoints)
        patterns.extend(oppositions)

        # Find squares (midpoints 90° apart)
        squares = self._find_squares(midpoints)
        patterns.extend(squares)

        # Find T-squares (three midpoints forming two squares and an opposition)
        t_squares = self._find_t_squares(midpoints)
        patterns.extend(t_squares)

        # Find grand crosses (four midpoints forming a square)
        grand_crosses = self._find_grand_crosses(midpoints)
        patterns.extend(grand_crosses)

        return patterns

    def _find_conjunctions(self, midpoints: Dict[str, float]) -> List[Tuple[str, str, str]]:
        """Find conjunctions between midpoints.

        Args:
            midpoints: Dictionary of midpoints

        Returns:
            List of tuples (pattern_type, planets_involved, description)
        """
        conjunctions = []

        # Check all pairs of midpoints
        midpoint_items = list(midpoints.items())
        for i, (name1, pos1) in enumerate(midpoint_items):
            for name2, pos2 in midpoint_items[i+1:]:
                # Check if the midpoints are conjunct
                if self._is_aspect(pos1, pos2, 0, self.orb):
                    planets_involved = f"{name1} conjunct {name2}"
                    description = (
                        f"The midpoints {name1} and {name2} are conjunct within {self.orb}°. "
                        f"This indicates a strong connection between these planetary combinations, "
                        f"suggesting that the themes represented by both midpoints are closely linked "
                        f"and mutually reinforcing."
                    )
                    conjunctions.append(("Conjunction", planets_involved, description))

        return conjunctions

    def _find_oppositions(self, midpoints: Dict[str, float]) -> List[Tuple[str, str, str]]:
        """Find oppositions between midpoints.

        Args:
            midpoints: Dictionary of midpoints

        Returns:
            List of tuples (pattern_type, planets_involved, description)
        """
        oppositions = []

        # Check all pairs of midpoints
        midpoint_items = list(midpoints.items())
        for i, (name1, pos1) in enumerate(midpoint_items):
            for name2, pos2 in midpoint_items[i+1:]:
                # Check if the midpoints are opposite
                if self._is_aspect(pos1, pos2, 180, self.orb):
                    planets_involved = f"{name1} opposite {name2}"
                    description = (
                        f"The midpoints {name1} and {name2} are in opposition within {self.orb}°. "
                        f"This indicates a dynamic tension between these planetary combinations, "
                        f"suggesting that the themes represented by both midpoints need to be "
                        f"balanced and integrated."
                    )
                    oppositions.append(("Opposition", planets_involved, description))

        return oppositions

    def _find_squares(self, midpoints: Dict[str, float]) -> List[Tuple[str, str, str]]:
        """Find squares between midpoints.

        Args:
            midpoints: Dictionary of midpoints

        Returns:
            List of tuples (pattern_type, planets_involved, description)
        """
        squares = []

        # Check all pairs of midpoints
        midpoint_items = list(midpoints.items())
        for i, (name1, pos1) in enumerate(midpoint_items):
            for name2, pos2 in midpoint_items[i+1:]:
                # Check if the midpoints are square
                if self._is_aspect(pos1, pos2, 90, self.orb):
                    planets_involved = f"{name1} square {name2}"
                    description = (
                        f"The midpoints {name1} and {name2} are in square aspect within {self.orb}°. "
                        f"This indicates creative tension between these planetary combinations, "
                        f"suggesting that the themes represented by both midpoints create friction "
                        f"that can lead to growth through resolving challenges."
                    )
                    squares.append(("Square", planets_involved, description))

        return squares

    def _find_t_squares(self, midpoints: Dict[str, float]) -> List[Tuple[str, str, str]]:
        """Find T-squares between midpoints.

        Args:
            midpoints: Dictionary of midpoints

        Returns:
            List of tuples (pattern_type, planets_involved, description)
        """
        t_squares = []

        # Check all triplets of midpoints
        midpoint_items = list(midpoints.items())
        for i, (name1, pos1) in enumerate(midpoint_items):
            for j, (name2, pos2) in enumerate(midpoint_items[i+1:], i+1):
                # Check if the first two midpoints are in opposition
                if not self._is_aspect(pos1, pos2, 180, self.orb):
                    continue

                for k, (name3, pos3) in enumerate(midpoint_items[j+1:], j+1):
                    # Check if the third midpoint is square to both others
                    if (self._is_aspect(pos1, pos3, 90, self.orb) and
                        self._is_aspect(pos2, pos3, 90, self.orb)):
                        planets_involved = f"{name1}, {name2}, {name3}"
                        description = (
                            f"The midpoints {name1}, {name2}, and {name3} form a T-square. "
                            f"This indicates a dynamic configuration of energies that creates "
                            f"tension and drive. The themes represented by these midpoints "
                            f"are interconnected in a way that demands resolution and integration."
                        )
                        t_squares.append(("T-Square", planets_involved, description))

        return t_squares

    def _find_grand_crosses(self, midpoints: Dict[str, float]) -> List[Tuple[str, str, str]]:
        """Find grand crosses between midpoints.

        Args:
            midpoints: Dictionary of midpoints

        Returns:
            List of tuples (pattern_type, planets_involved, description)
        """
        grand_crosses = []

        # Check all quartets of midpoints
        midpoint_items = list(midpoints.items())
        for i, (name1, pos1) in enumerate(midpoint_items):
            for j, (name2, pos2) in enumerate(midpoint_items[i+1:], i+1):
                # Check if the first two midpoints are square
                if not self._is_aspect(pos1, pos2, 90, self.orb):
                    continue

                for k, (name3, pos3) in enumerate(midpoint_items[j+1:], j+1):
                    # Check if the third midpoint is square to the second and opposite the first
                    if not (self._is_aspect(pos2, pos3, 90, self.orb) and
                            self._is_aspect(pos1, pos3, 180, self.orb)):
                        continue

                    for l, (name4, pos4) in enumerate(midpoint_items[k+1:], k+1):
                        # Check if the fourth midpoint completes the grand cross
                        if (self._is_aspect(pos3, pos4, 90, self.orb) and
                            self._is_aspect(pos1, pos4, 90, self.orb) and
                            self._is_aspect(pos2, pos4, 180, self.orb)):
                            planets_involved = f"{name1}, {name2}, {name3}, {name4}"
                            description = (
                                f"The midpoints {name1}, {name2}, {name3}, and {name4} form a Grand Cross. "
                                f"This indicates a powerful configuration of energies that creates "
                                f"significant tension and drive. The themes represented by these midpoints "
                                f"are interconnected in a way that demands comprehensive integration "
                                f"and balance across multiple areas of life."
                            )
                            grand_crosses.append(("Grand Cross", planets_involved, description))

        return grand_crosses

    def _is_aspect(self, pos1: float, pos2: float, aspect_angle: float, orb: float) -> bool:
        """Check if two positions form an aspect.

        Args:
            pos1: First position in degrees
            pos2: Second position in degrees
            aspect_angle: Angle of the aspect in degrees
            orb: Maximum orb in degrees

        Returns:
            True if the positions form the aspect, False otherwise
        """
        # Calculate the angular difference
        diff = abs(pos1 - pos2) % 360
        if diff > 180:
            diff = 360 - diff

        # Check if the difference is within orb of the aspect angle
        return abs(diff - aspect_angle) <= orb

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
