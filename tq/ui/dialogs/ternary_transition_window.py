"""
Purpose: Provides a standalone window for the Ternary Transition Calculator

This file is part of the tq pillar and serves as a UI component.
It is responsible for creating a standalone window that hosts the
TernaryTransitionWidget for calculating ternary transitions.

Key components:
- TernaryTransitionWindow: Main window class for hosting the ternary transition widget

Dependencies:
- PyQt6: For the user interface components
- tq.ui.widgets.ternary_transition_widget: The core widget this window hosts
- shared.ui.window_management: For access to the window manager

Related files:
- tq/ui/widgets/ternary_transition_widget.py: The core widget this window hosts
- tq/ui/tq_tab.py: Tab that provides a button to open this window
"""

from loguru import logger
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from shared.ui.window_management import AuxiliaryWindow
from tq.ui.widgets.ternary_transition_widget import TernaryTransitionWidget


class TernaryTransitionWindow(AuxiliaryWindow):
    """Standalone window for the Ternary Transition Calculator."""

    def __init__(self, window_manager=None, parent=None):
        """Initialize the Ternary Transition window.

        Args:
            window_manager: Application window manager (optional)
            parent: The parent widget
        """
        super().__init__("Ternary Transition Calculator", parent)

        # Store the window manager for use by child widgets
        self.window_manager = window_manager

        # Set window properties
        self.setMinimumSize(800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create and add the transition widget
        self.widget = TernaryTransitionWidget()
        layout.addWidget(self.widget)

        logger.debug("TernaryTransitionWindow initialized")

    def get_widget(self) -> TernaryTransitionWidget:
        """Get the transition widget instance.

        Returns:
            The TernaryTransitionWidget instance
        """
        return self.widget

    def set_transition_numbers(self, first_number: int, second_number: int):
        """Set the transition numbers and calculate the transition.

        Args:
            first_number (int): The first number for the transition
            second_number (int): The second number for the transition
        """
        logger.debug(
            f"Setting transition numbers: first={first_number}, second={second_number}"
        )

        # Show and raise the window first to ensure widget is initialized
        self.show()
        self.raise_()
        logger.debug("Window shown and raised")

        # Block signals temporarily to prevent premature calculations
        self.widget.first_number_input.blockSignals(True)
        self.widget.second_number_input.blockSignals(True)
        logger.debug("Signals blocked")

        # Set the values in the inputs
        logger.debug("Setting input values...")
        self.widget.first_number_input.setText(str(first_number))
        self.widget.second_number_input.setText(str(second_number))
        logger.debug(
            f"Input values set. First input text: {self.widget.first_number_input.text()}, Second input text: {self.widget.second_number_input.text()}"
        )

        # Re-enable signals
        self.widget.first_number_input.blockSignals(False)
        self.widget.second_number_input.blockSignals(False)
        logger.debug("Signals unblocked")

        # Update ternary displays
        logger.debug("Updating ternary displays...")
        self.widget._update_first_ternary()
        self.widget._update_second_ternary()
        logger.debug(
            f"Ternary displays updated. First: {self.widget.first_ternary_display.text()}, Second: {self.widget.second_ternary_display.text()}"
        )

        # Process events to ensure UI is updated
        from PyQt6.QtCore import QCoreApplication

        QCoreApplication.processEvents()

        # Force a calculation
        logger.debug("Forcing calculation...")
        self.widget._calculate_transition()

        # Process events again to ensure calculation updates are shown
        QCoreApplication.processEvents()

        # Force UI update
        self.widget.update()
        self.update()
        logger.debug("Calculation complete and UI updated")


if __name__ == "__main__":
    """Simple demonstration of the Ternary Transition window."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = TernaryTransitionWindow()
    window.show()
    sys.exit(app.exec())
