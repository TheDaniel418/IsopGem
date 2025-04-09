"""
Purpose: Provides a standalone window for birth chart creation and analysis.

This file is part of the astrology pillar and serves as a UI component.
It provides a window that contains the birth chart widget.

Key components:
- BirthChartWindow: Standalone window for birth chart creation and analysis

Dependencies:
- PyQt6: For UI components
- astrology.ui.widgets: For the birth chart widget
"""

from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from loguru import logger

from astrology.ui.widgets.birth_chart_widget import BirthChartWidget


class BirthChartWindow(QMainWindow):
    """Standalone window for birth chart creation and analysis."""

    def __init__(self, parent=None):
        """Initialize the birth chart window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set window properties
        self.setWindowTitle("Birth Chart")
        self.setMinimumSize(900, 700)

        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Create birth chart widget
        self.birth_chart_widget = BirthChartWidget()
        layout.addWidget(self.birth_chart_widget)

        logger.debug("BirthChartWindow initialized")

    def set_content(self, widget):
        """Set the content widget of the window.

        This method is required for compatibility with the window manager.

        Args:
            widget: Widget to use as the window content
        """
        # This method is not used since we create our own content
        pass

    def set_chart(self, chart):
        """Set the chart to display.

        Args:
            chart: Chart to display
        """
        # Update the window title
        self.setWindowTitle(f"Chart: {chart.name}")

        # Store the chart in the birth chart widget
        self.birth_chart_widget.current_chart = chart

        # Update the chart display
        self.birth_chart_widget._update_chart_display()

        logger.debug(f"Set chart {chart.name} in BirthChartWindow")
