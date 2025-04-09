"""
Purpose: Provides a window for the Series Transition feature

This file is part of the tq pillar and serves as a window component.
It provides a floating window that hosts the SeriesTransitionWidget
and manages its lifecycle.

Key components:
- SeriesTransitionWindow: Main window class for series transition analysis

Dependencies:
- PyQt6: For window components
- tq.ui.widgets.series_transition_widget: For the main widget
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from typing import List

from loguru import logger

from tq.ui.widgets.series_transition_widget import SeriesTransitionWidget


class SeriesTransitionWindow(QMainWindow):
    """Window for analyzing transitions between series of numbers."""
    
    def __init__(self, parent=None):
        """Initialize the window."""
        super().__init__(parent)
        self.setWindowTitle("Series Transition Analysis")
        self.setMinimumSize(600, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create and add the series transition widget
        self.transition_widget = SeriesTransitionWidget()
        layout.addWidget(self.transition_widget)
        
        logger.debug("SeriesTransitionWindow initialized") 

    def set_series_numbers(self, numbers: List[int]):
        """Set the series numbers and calculate transitions.
        
        Args:
            numbers: List of numbers to set in pairs. Must be an even number of values
                    as they will be processed as pairs (a1,b1,a2,b2,...).
        """
        logger.debug(f"Setting series numbers: {numbers}")
        
        if len(numbers) % 2 != 0:
            raise ValueError("Must provide an even number of values for pairs")
        
        # Show and raise the window first to ensure widget is initialized
        self.show()
        self.raise_()
        logger.debug("Window shown and raised")
        
        # Clear existing pairs and add new ones
        logger.debug("Clearing existing pairs")
        self.transition_widget.clear_pairs()
        
        # Add pairs
        for i in range(0, len(numbers), 2):
            logger.debug(f"Adding pair: {numbers[i]}, {numbers[i+1]}")
            self.transition_widget.add_number_pair(numbers[i], numbers[i+1])
        
        # Calculate transitions
        logger.debug("Calculating transitions")
        self.transition_widget._calculate_transitions()
        
        # Process events and update UI
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
        
        # Force UI update
        self.transition_widget.update()
        self.update()
        logger.debug("Series transitions calculated and UI updated") 