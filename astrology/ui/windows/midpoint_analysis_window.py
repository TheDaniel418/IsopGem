"""
Purpose: Window for advanced midpoint analysis.

This file provides a comprehensive interface for analyzing midpoints
in various ways, including harmonic analysis, midpoint trees,
planetary pictures, personal sensitive points, and midpoint patterns.

Key components:
- MidpointAnalysisWindow: Main window for midpoint analysis

Dependencies:
- PyQt6: For UI components
- loguru: For logging
- astrology.models: For astrological data models
- astrology.ui.widgets.midpoint_analysis: For midpoint analysis widgets
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget

from astrology.models.chart import Chart
from astrology.ui.widgets.midpoint_analysis.grand_fusion_widget import GrandFusionWidget
from astrology.ui.widgets.midpoint_analysis.harmonic_dial_widget import (
    HarmonicDialWidget,
)
from astrology.ui.widgets.midpoint_analysis.midpoint_patterns_widget import (
    MidpointPatternsWidget,
)
from astrology.ui.widgets.midpoint_analysis.midpoint_tree_widget import (
    MidpointTreeWidget,
)
from astrology.ui.widgets.midpoint_analysis.sensitive_points_widget import (
    SensitivePointsWidget,
)


class MidpointAnalysisWindow(QMainWindow):
    """Window for advanced midpoint analysis."""

    def __init__(self, chart: Chart):
        """Initialize the midpoint analysis window.

        Args:
            chart: The chart to analyze
        """
        super().__init__()
        self.chart = chart
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle(f"Midpoint Analysis - {self.chart.name}")
        self.resize(900, 800)  # Increased from 800x600 to 900x800

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add title
        title = QLabel(f"Midpoint Analysis for {self.chart.name}")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Add note about traditional planets
        note = QLabel(
            "Analysis limited to traditional 7 planets: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn"
        )
        note.setStyleSheet("font-style: italic; color: #666;")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(note)

        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Add tabs for different analysis types
        self._add_harmonic_dial_tab()
        self._add_midpoint_trees_tab()
        self._add_sensitive_points_tab()
        self._add_midpoint_patterns_tab()
        self._add_grand_fusion_tab()

    def _add_harmonic_dial_tab(self):
        """Add the harmonic dial tab."""
        harmonic_tab = QWidget()
        layout = QVBoxLayout(harmonic_tab)

        # Add harmonic dial widget
        harmonic_dial = HarmonicDialWidget(self.chart)
        layout.addWidget(harmonic_dial)

        self.tabs.addTab(harmonic_tab, "Harmonic Dial")

    def _add_midpoint_trees_tab(self):
        """Add the midpoint trees tab."""
        trees_tab = QWidget()
        layout = QVBoxLayout(trees_tab)

        # Add midpoint tree widget
        midpoint_tree = MidpointTreeWidget(self.chart)
        layout.addWidget(midpoint_tree)

        self.tabs.addTab(trees_tab, "Midpoint Trees")

    def _add_sensitive_points_tab(self):
        """Add the sensitive points tab."""
        sensitive_tab = QWidget()
        layout = QVBoxLayout(sensitive_tab)

        # Add sensitive points widget
        sensitive_points = SensitivePointsWidget(self.chart)
        layout.addWidget(sensitive_points)

        self.tabs.addTab(sensitive_tab, "Sensitive Points")

    def _add_midpoint_patterns_tab(self):
        """Add the midpoint patterns tab."""
        patterns_tab = QWidget()
        layout = QVBoxLayout(patterns_tab)

        # Add midpoint patterns widget
        midpoint_patterns = MidpointPatternsWidget(self.chart)
        layout.addWidget(midpoint_patterns)

        self.tabs.addTab(patterns_tab, "Midpoint Patterns")

    def _add_grand_fusion_tab(self):
        """Add the Grand Fusion Midpoint tab."""
        fusion_tab = QWidget()
        layout = QVBoxLayout(fusion_tab)

        # Add Grand Fusion widget
        grand_fusion = GrandFusionWidget(self.chart)
        layout.addWidget(grand_fusion)

        self.tabs.addTab(fusion_tab, "Grand Fusion")
