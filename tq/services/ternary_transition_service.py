"""
Purpose: Service to manage the Ternary Transitions window and handle communication between panels.

This service follows the singleton pattern and provides methods to:
1. Get or create the Ternary Transitions window
2. Set transition numbers
3. Trigger transition calculations
"""

import logging

from PyQt6.QtCore import QObject, QTimer, Qt

from tq.ui.dialogs.ternary_transition_window import TernaryTransitionWindow

logger = logging.getLogger(__name__)


class TernaryTransitionService(QObject):
    _instance = None

    def __init__(self):
        super().__init__()
        self.window = None

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the service."""
        if cls._instance is None:
            cls._instance = TernaryTransitionService()
        return cls._instance

    def get_window(self):
        """Get or create the Ternary Transitions window."""
        if self.window is None:
            self.window = TernaryTransitionWindow()
        return self.window

    def set_transition_numbers(self, first_number: int, second_number: int):
        """Set the transition numbers and show the window.

        Args:
            first_number (int): The first number for the transition
            second_number (int): The second number for the transition
        """
        logger.debug(
            f"TernaryTransitionService: Setting numbers {first_number} and {second_number}"
        )

        # Create window if it doesn't exist
        if self.window is None:
            logger.debug("Creating new TernaryTransitionWindow")
            self.window = TernaryTransitionWindow()
        else:
            logger.debug("Using existing TernaryTransitionWindow")

        # Set the numbers and show
        logger.debug("Calling window.set_transition_numbers")
        self.window.set_transition_numbers(first_number, second_number)
        logger.debug("Window set_transition_numbers complete")

        # Ensure window is visible and focused using stronger focus methods
        self.window.show()
        
        # Use multiple methods to force the window to the front
        self.window.setWindowState(self.window.windowState() & ~Qt.WindowState.WindowMinimized)
        self.window.raise_()
        self.window.activateWindow()
        
        # If the window has an ensure_on_top method (inherits from AuxiliaryWindow), use it
        if hasattr(self.window, "ensure_on_top"):
            self.window.ensure_on_top()
        
        # Use timer to attempt focus again after event loop processes other events
        QTimer.singleShot(100, lambda: self._delayed_focus())
        
        logger.debug("Window visibility and focus operations complete")

    def _delayed_focus(self):
        """Apply delayed focus to ensure window is on top."""
        if self.window and self.window.isVisible():
            self.window.raise_()
            self.window.activateWindow()
            logger.debug("Applied delayed focus to ternary transition window")
