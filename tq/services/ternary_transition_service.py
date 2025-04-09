"""
Purpose: Service to manage the Ternary Transitions window and handle communication between panels.

This service follows the singleton pattern and provides methods to:
1. Get or create the Ternary Transitions window
2. Set transition numbers
3. Trigger transition calculations
"""

import logging

from PyQt6.QtCore import QObject

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

        # Ensure window is visible and updated
        self.window.show()
        self.window.raise_()
        self.window.update()
