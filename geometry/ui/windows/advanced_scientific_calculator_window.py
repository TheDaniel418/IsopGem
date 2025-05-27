"""
Advanced Scientific Calculator Window for IsopGem's Geometry module.

This module provides a standalone window for the Advanced Scientific Calculator,
allowing users to perform complex mathematical calculations in a separate window.
"""

from typing import Optional

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget

from geometry.ui.widgets.advanced_scientific_calculator_widget import AdvancedScientificCalculatorWidget
from shared.ui.window_management import AuxiliaryWindow


class AdvancedScientificCalculatorWindow(AuxiliaryWindow):
    """Standalone window for the Advanced Scientific Calculator."""

    def __init__(self, window_id: str, parent: Optional[QWidget] = None) -> None:
        """Initialize the calculator window.

        Args:
            window_id: Unique identifier for this window instance
            parent: Parent widget
        """
        # Initialize with proper title
        super().__init__("Advanced Scientific Calculator", parent)
        
        # Store the window ID
        self.window_id = window_id
        
        # Create the calculator widget
        self.calculator_widget = AdvancedScientificCalculatorWidget()
        
        # Set the widget as content
        self.set_content(self.calculator_widget)
        
        # Configure window appearance
        self.setMinimumSize(550, 700)
        
        # Connect signals
        self.calculator_widget.calculation_performed.connect(self._on_calculation_performed)
        
        logger.debug(f"AdvancedScientificCalculatorWindow initialized with ID {window_id}")
        
    def _on_calculation_performed(self, expression: str, result: float) -> None:
        """Handle when a calculation is performed.

        Args:
            expression: The expression that was calculated
            result: The result of the calculation
        """
        # Update the window title with the calculation
        self.setWindowTitle(f"Advanced Calculator - {expression} = {result}")
        logger.debug(f"Calculation performed: {expression} = {result}")
        
    def ensure_on_top(self) -> None:
        """Ensure this window appears on top of other windows."""
        # Apply focus operations to ensure we're visible and on top
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Use delayed focus to ensure window ordering is applied after other events
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._delayed_focus)
        
        logger.debug("Ensuring AdvancedScientificCalculatorWindow stays on top")
        
    def _delayed_focus(self) -> None:
        """Apply delayed focus operations to ensure window stays on top."""
        if self.isVisible():
            self.raise_()
            self.activateWindow()
            logger.debug("Applied delayed focus to AdvancedScientificCalculatorWindow")
