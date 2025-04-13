"""
Purpose: Provides a widget for performing ternary transitions between decimal numbers

This file is part of the tq pillar and serves as a UI component.
It is responsible for allowing users to input two decimal numbers, calculate
their ternary transition, and view or send the results to other components.

Key components:
- TernaryTransitionWidget: Widget for ternary transition calculations
- decimal_input handlers: Methods for validating and processing decimal inputs
- transition_calculation: Methods to perform the transition operation

Dependencies:
- PyQt6: For the user interface components
- tq.utils.ternary_converter: For converting between decimal and ternary
- tq.utils.ternary_transition: For applying the transition operation
- tq.services import tq_analysis_service: For opening quadset analysis with the result
- tq.services import tq_database_service: For looking up numbers in the database

Related files:
- tq/ui/dialogs/ternary_transition_window.py: Window that hosts this widget
- tq/ui/dialogs/number_database_window.py: Window for displaying database lookups
- tq/ui/tq_tab.py: Tab that provides a button to open this widget
- tq/utils/ternary_transition.py: Core transition functionality
"""

import uuid
from typing import Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tq.services import tq_analysis_service, tq_database_service
from tq.utils.ternary_converter import decimal_to_ternary, ternary_to_decimal
from tq.utils.ternary_transition import TernaryTransition


class TernaryTransitionWidget(QWidget):
    """Widget for performing ternary transitions between two decimal numbers."""

    # Signal emitted when a transition is calculated
    transition_calculated = pyqtSignal(
        int, int, int
    )  # first_decimal, second_decimal, result_decimal

    def __init__(self, parent=None):
        """Initialize the Ternary Transition widget.

        Args:
            parent: The parent widget
        """
        super().__init__(parent)

        # Initialize the TernaryTransition utility
        self.transition = TernaryTransition()

        # Initialize the TQ Database service if needed
        try:
            tq_database_service.initialize()
        except:
            # Database service might already be initialized
            pass

        # Initialize the UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Set up the main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title and description
        title_label = QLabel("Ternary Transition Calculator")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(title_label)

        description = QLabel(
            "This calculator performs a transition operation between two decimal numbers "
            "using the Ternary Transition System. The system converts the numbers to base-3 "
            "and applies the transition mapping to each corresponding digit pair."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(description)

        # Input section
        input_group = QGroupBox("Input Numbers")
        input_layout = QGridLayout(input_group)

        # First number input
        input_layout.addWidget(QLabel("First Number:"), 0, 0)
        self.first_number_input = QLineEdit()
        self.first_number_input.setValidator(QIntValidator(0, 999999))
        self.first_number_input.setPlaceholderText("Enter decimal number")
        self.first_number_input.setText("0")
        input_layout.addWidget(self.first_number_input, 0, 1)

        # First number ternary display
        input_layout.addWidget(QLabel("Ternary:"), 0, 2)
        self.first_ternary_display = QLabel("0")
        self.first_ternary_display.setStyleSheet(
            "font-family: monospace; font-weight: bold;"
        )
        input_layout.addWidget(self.first_ternary_display, 0, 3)

        # Second number input
        input_layout.addWidget(QLabel("Second Number:"), 1, 0)
        self.second_number_input = QLineEdit()
        self.second_number_input.setValidator(QIntValidator(0, 999999))
        self.second_number_input.setPlaceholderText("Enter decimal number")
        self.second_number_input.setText("0")
        input_layout.addWidget(self.second_number_input, 1, 1)

        # Second number ternary display
        input_layout.addWidget(QLabel("Ternary:"), 1, 2)
        self.second_ternary_display = QLabel("0")
        self.second_ternary_display.setStyleSheet(
            "font-family: monospace; font-weight: bold;"
        )
        input_layout.addWidget(self.second_ternary_display, 1, 3)

        # Add input group to main layout
        main_layout.addWidget(input_group)

        # Calculate button
        calculate_button = QPushButton("Calculate Transition")
        calculate_button.clicked.connect(self._calculate_transition)
        main_layout.addWidget(calculate_button)

        # Result section
        result_group = QGroupBox("Transition Result")
        result_layout = QGridLayout(result_group)

        # Result display
        result_layout.addWidget(QLabel("Decimal:"), 0, 0)
        self.result_decimal_display = QLabel("0")
        self.result_decimal_display.setStyleSheet("font-size: 16px; font-weight: bold;")
        result_layout.addWidget(self.result_decimal_display, 0, 1)

        # Add buttons for the main result
        result_actions = QHBoxLayout()
        self.result_grid_button = QPushButton("Open in TQ Grid")
        self.result_grid_button.setToolTip(
            "Open the result in TQ Grid for detailed analysis"
        )
        self.result_grid_button.clicked.connect(
            lambda: self._open_in_tq_grid(self.result_decimal_display.text())
        )
        result_actions.addWidget(self.result_grid_button)

        self.result_lookup_button = QPushButton("Look up in Database")
        self.result_lookup_button.setToolTip(
            "Search for this number in the TQ database"
        )
        self.result_lookup_button.clicked.connect(
            lambda: self._lookup_in_database(self.result_decimal_display.text())
        )
        result_actions.addWidget(self.result_lookup_button)

        result_layout.addLayout(result_actions, 0, 2)

        result_layout.addWidget(QLabel("Ternary:"), 1, 0)
        self.result_ternary_display = QLabel("0")
        self.result_ternary_display.setStyleSheet(
            "font-family: monospace; font-size: 16px; font-weight: bold;"
        )
        result_layout.addWidget(self.result_ternary_display, 1, 1, 1, 2)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        result_layout.addWidget(separator, 2, 0, 1, 3)

        # Add Amalgam section (transition of sum through absolute difference)
        result_layout.addWidget(QLabel("Amalgam:"), 3, 0)
        self.amalgam_decimal_display = QLabel("0")
        self.amalgam_decimal_display.setStyleSheet(
            "font-size: 16px; font-weight: bold;"
        )
        result_layout.addWidget(self.amalgam_decimal_display, 3, 1)

        # Add buttons for the Amalgam result
        amalgam_actions = QHBoxLayout()
        self.amalgam_grid_button = QPushButton("Open in TQ Grid")
        self.amalgam_grid_button.setToolTip(
            "Open the Amalgam result in TQ Grid for detailed analysis"
        )
        self.amalgam_grid_button.clicked.connect(
            lambda: self._open_in_tq_grid(self.amalgam_decimal_display.text())
        )
        amalgam_actions.addWidget(self.amalgam_grid_button)

        self.amalgam_lookup_button = QPushButton("Look up in Database")
        self.amalgam_lookup_button.setToolTip(
            "Search for this Amalgam number in the TQ database"
        )
        self.amalgam_lookup_button.clicked.connect(
            lambda: self._lookup_in_database(self.amalgam_decimal_display.text())
        )
        amalgam_actions.addWidget(self.amalgam_lookup_button)

        result_layout.addLayout(amalgam_actions, 3, 2)

        result_layout.addWidget(QLabel("Ternary:"), 4, 0)
        self.amalgam_ternary_display = QLabel("0")
        self.amalgam_ternary_display.setStyleSheet(
            "font-family: monospace; font-size: 16px; font-weight: bold;"
        )
        result_layout.addWidget(self.amalgam_ternary_display, 4, 1, 1, 2)

        # Add informational displays for sum and difference
        result_layout.addWidget(QLabel("Sum:"), 5, 0)
        self.sum_display = QLabel("0")
        result_layout.addWidget(self.sum_display, 5, 1, 1, 2)

        result_layout.addWidget(QLabel("Difference:"), 6, 0)
        self.diff_display = QLabel("0")
        result_layout.addWidget(self.diff_display, 6, 1, 1, 2)

        # Add result group to main layout
        main_layout.addWidget(result_group)

        # Add stretch to bottom for better layout
        main_layout.addStretch()

        # Connect text changed signals to update ternary displays
        self.first_number_input.textChanged.connect(self._update_first_ternary)
        self.second_number_input.textChanged.connect(self._update_second_ternary)

        # Initialize the ternary displays
        self._update_first_ternary()
        self._update_second_ternary()

        # Initially disable action buttons until a calculation is performed
        self.result_grid_button.setEnabled(False)
        self.result_lookup_button.setEnabled(False)
        self.amalgam_grid_button.setEnabled(False)
        self.amalgam_lookup_button.setEnabled(False)

    def _update_first_ternary(self):
        """Update the ternary display for the first number."""
        try:
            decimal_value = int(self.first_number_input.text() or "0")
            ternary_str = decimal_to_ternary(decimal_value)
            self.first_ternary_display.setText(ternary_str)
        except ValueError:
            self.first_ternary_display.setText("Invalid input")

    def _update_second_ternary(self):
        """Update the ternary display for the second number."""
        try:
            decimal_value = int(self.second_number_input.text() or "0")
            ternary_str = decimal_to_ternary(decimal_value)
            self.second_ternary_display.setText(ternary_str)
        except ValueError:
            self.second_ternary_display.setText("Invalid input")

    def _calculate_transition(self):
        """Calculate the transition between the two input numbers."""
        try:
            # Get input values
            first_decimal = int(self.first_number_input.text() or "0")
            second_decimal = int(self.second_number_input.text() or "0")

            # Standard transition
            # Convert to ternary
            first_ternary = decimal_to_ternary(first_decimal)
            second_ternary = decimal_to_ternary(second_decimal)

            # Apply transition
            result_ternary = self.transition.apply_transition(
                first_ternary, second_ternary
            )

            # Convert result back to decimal
            result_decimal = ternary_to_decimal(result_ternary)

            # Update standard result displays
            self.result_decimal_display.setText(str(result_decimal))
            self.result_ternary_display.setText(result_ternary)

            # Enable result action buttons
            self.result_grid_button.setEnabled(True)
            self.result_lookup_button.setEnabled(True)

            # Calculate Amalgam (transition of sum through absolute difference)
            sum_decimal = first_decimal + second_decimal
            diff_decimal = abs(first_decimal - second_decimal)

            # Convert to ternary
            sum_ternary = decimal_to_ternary(sum_decimal)
            diff_ternary = decimal_to_ternary(diff_decimal)

            # Apply transition
            amalgam_ternary = self.transition.apply_transition(
                sum_ternary, diff_ternary
            )

            # Convert result back to decimal
            amalgam_decimal = ternary_to_decimal(amalgam_ternary)

            # Update Amalgam displays
            self.amalgam_decimal_display.setText(str(amalgam_decimal))
            self.amalgam_ternary_display.setText(amalgam_ternary)

            # Update intermediate displays
            self.sum_display.setText(f"{sum_decimal} (Ternary: {sum_ternary})")
            self.diff_display.setText(f"{diff_decimal} (Ternary: {diff_ternary})")

            # Enable Amalgam action buttons
            self.amalgam_grid_button.setEnabled(True)
            self.amalgam_lookup_button.setEnabled(True)

            # Emit signal with standard result
            self.transition_calculated.emit(
                first_decimal, second_decimal, result_decimal
            )

        except ValueError as e:
            self.result_decimal_display.setText("Error")
            self.result_ternary_display.setText(str(e))
            self.amalgam_decimal_display.setText("Error")
            self.amalgam_ternary_display.setText(str(e))
            self.sum_display.setText("")
            self.diff_display.setText("")
            self.result_grid_button.setEnabled(False)
            self.result_lookup_button.setEnabled(False)
            self.amalgam_grid_button.setEnabled(False)
            self.amalgam_lookup_button.setEnabled(False)
        except KeyError as e:
            self.result_decimal_display.setText("Transition Error")
            self.result_ternary_display.setText(str(e))
            self.amalgam_decimal_display.setText("Transition Error")
            self.amalgam_ternary_display.setText(str(e))
            self.sum_display.setText("")
            self.diff_display.setText("")
            self.result_grid_button.setEnabled(False)
            self.result_lookup_button.setEnabled(False)
            self.amalgam_grid_button.setEnabled(False)
            self.amalgam_lookup_button.setEnabled(False)

    def _open_in_tq_grid(self, number_text):
        """Open a number in the TQ Grid for detailed analysis.

        Args:
            number_text: The decimal number text to open
        """
        try:
            number = int(number_text)

            # Get the TQ Analysis Service instance
            analysis_service = tq_analysis_service.get_instance()

            # Open the quadset analysis with the number
            analysis_service.open_quadset_analysis(number)

        except (ValueError, AttributeError, RuntimeError):
            # Handle errors - no action needed as button should be disabled if no valid number
            pass

    def _lookup_in_database(self, number_text):
        """Look up a number in the database.

        Args:
            number_text: The decimal number text to look up
        """
        try:
            number = int(number_text)

            # Import the window class here to avoid circular imports
            from tq.ui.dialogs.number_database_window import NumberDatabaseWindow

            # Create window manager function to open a window
            # This should be called in a window context, so try to get a window
            parent = self.window()
            if parent and hasattr(parent, "window_manager"):
                # If we can get the window manager from the parent, use it
                base_id = f"number_database_{number}"
                window_id = f"{base_id}_{uuid.uuid4().hex[:8]}"
                parent.window_manager.open_multi_window(
                    window_id,
                    NumberDatabaseWindow(number),
                    f"Number Database: {number}",
                    (800, 600),
                )
            else:
                # Otherwise just create a new window directly
                db_window = NumberDatabaseWindow(number)
                db_window.show()

        except (ValueError, AttributeError, RuntimeError, ImportError):
            # Handle errors - could show a message dialog here
            pass

    def get_result(self) -> Tuple[int, str]:
        """Get the current result as both decimal and ternary.

        Returns:
            A tuple containing (decimal_result, ternary_result)
        """
        try:
            decimal = int(self.result_decimal_display.text())
            ternary = self.result_ternary_display.text()
            return decimal, ternary
        except ValueError:
            return 0, "0"


if __name__ == "__main__":
    """Simple demonstration of the Ternary Transition widget."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = TernaryTransitionWidget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
