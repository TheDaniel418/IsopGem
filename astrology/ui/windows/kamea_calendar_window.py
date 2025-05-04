"""
Purpose: Window for the Kamea Cosmic Calendar visualization.

This file provides a comprehensive interface for visualizing the Kamea Cosmic Calendar,
which maps the mathematically elegant structure of the Kamea system to calendar days.

Key components:
- KameaCalendarWindow: Main window for the Kamea Cosmic Calendar visualization

Dependencies:
- PyQt6: For UI components
- loguru: For logging
- astrology.ui.widgets.kamea_calendar: For Kamea Calendar visualization widgets
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget

from astrology.ui.widgets.kamea_calendar.calendar_visualization_widget import (
    CalendarVisualizationWidget,
)
from astrology.ui.widgets.kamea_calendar.conrune_pair_widget import (
    ConrunePairWidget,
)


class KameaCalendarWindow(QMainWindow):
    """Window for Kamea Cosmic Calendar visualization."""

    def __init__(self):
        """Initialize the Kamea Cosmic Calendar window."""
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle("Kamea Cosmic Calendar")
        self.resize(1000, 900)  # Increased height from 800 to 900

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Add title
        title = QLabel("Kamea Cosmic Calendar")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Add description
        description = QLabel(
            "A calendar system based on the mathematical structure of the Kamea. "
            "Each day corresponds to a unique conrune differential value."
        )
        description.setStyleSheet("font-style: italic; color: #666;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description)

        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Add tabs for different visualizations
        self._add_circular_visualization_tab()
        self._add_conrune_pairs_tab()

    def _add_circular_visualization_tab(self):
        """Add the circular visualization tab."""
        visualization_tab = QWidget()
        layout = QVBoxLayout(visualization_tab)

        # Add calendar visualization widget
        calendar_visualization = CalendarVisualizationWidget()
        layout.addWidget(calendar_visualization)

        self.tabs.addTab(visualization_tab, "Calendar Visualization")

    def _add_conrune_pairs_tab(self):
        """Add the conrune pairs tab."""
        pairs_tab = QWidget()
        layout = QVBoxLayout(pairs_tab)

        # Add conrune pair widget
        conrune_pairs = ConrunePairWidget()
        layout.addWidget(conrune_pairs)

        self.tabs.addTab(pairs_tab, "Conrune Pairs")