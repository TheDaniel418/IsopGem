"""
Purpose: Provides a widget for analyzing transitions between series of number pairs

This file is part of the tq pillar and serves as a UI widget component.
It provides an interface for entering pairs of numbers and analyzing
their transitions, including series sums, closed loop sums, and amalgams.

Key components:
- SeriesTransitionWidget: Main widget for series transition analysis
- NumberPairWidget: Custom widget for entering pairs of numbers
- TransitionDisplay: Widget showing transition results

Dependencies:
- PyQt6: For UI components
- tq.utils.ternary_converter: For ternary representations
- tq.utils.ternary_transition: For transition calculations
- shared.services.number_properties_service: For number analysis
"""

from typing import Optional, Tuple

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from tq.utils.ternary_converter import decimal_to_ternary


class NumberPairWidget(QWidget):
    """Widget for entering a pair of numbers with ternary display."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # First number
        layout.addWidget(QLabel("First:"), 0, 0)
        self.first_number = QLineEdit()
        self.first_number.setValidator(QIntValidator(0, 999999))
        self.first_number.setPlaceholderText("Enter number")
        self.first_number.setFixedWidth(120)
        layout.addWidget(self.first_number, 0, 1)

        # First number ternary display
        layout.addWidget(QLabel("Ternary:"), 0, 2)
        self.first_ternary = QLabel("0")
        self.first_ternary.setStyleSheet("font-family: monospace; font-weight: bold;")
        layout.addWidget(self.first_ternary, 0, 3)

        # Arrow between inputs
        arrow_label = QLabel("→")
        arrow_label.setStyleSheet("font-weight: bold; padding: 0 10px;")
        layout.addWidget(arrow_label, 0, 4)

        # Second number
        layout.addWidget(QLabel("Second:"), 0, 5)
        self.second_number = QLineEdit()
        self.second_number.setValidator(QIntValidator(0, 999999))
        self.second_number.setPlaceholderText("Enter number")
        self.second_number.setFixedWidth(120)
        layout.addWidget(self.second_number, 0, 6)

        # Second number ternary display
        layout.addWidget(QLabel("Ternary:"), 0, 7)
        self.second_ternary = QLabel("0")
        self.second_ternary.setStyleSheet("font-family: monospace; font-weight: bold;")
        layout.addWidget(self.second_ternary, 0, 8)

        # Result section
        layout.addWidget(QLabel("Transition:"), 1, 0)

        # Decimal result with label
        decimal_layout = QHBoxLayout()
        decimal_layout.addWidget(QLabel("Decimal:"))
        self.result_decimal = QLabel("0")
        self.result_decimal.setStyleSheet("font-weight: bold;")
        decimal_layout.addWidget(self.result_decimal)
        decimal_layout.addStretch()
        layout.addLayout(decimal_layout, 1, 1, 1, 2)

        # Ternary result with label
        ternary_layout = QHBoxLayout()
        ternary_layout.addWidget(QLabel("Ternary:"))
        self.result_ternary = QLabel("0")
        self.result_ternary.setStyleSheet("font-family: monospace; font-weight: bold;")
        ternary_layout.addWidget(self.result_ternary)
        ternary_layout.addStretch()
        layout.addLayout(ternary_layout, 1, 3, 1, 5)

        # Action buttons for the pair result
        button_layout = QHBoxLayout()
        self.grid_button = QPushButton("Open in TQ Grid")
        self.grid_button.setEnabled(False)
        self.lookup_button = QPushButton("Look up in Database")
        self.lookup_button.setEnabled(False)
        button_layout.addWidget(self.grid_button)
        button_layout.addWidget(self.lookup_button)
        layout.addLayout(button_layout, 1, 8)

        # Connect signals
        self.first_number.textChanged.connect(self._update_first_ternary)
        self.second_number.textChanged.connect(self._update_second_ternary)
        self.grid_button.clicked.connect(
            lambda: self._open_in_tq_grid(self.result_decimal.text())
        )
        self.lookup_button.clicked.connect(
            lambda: self._lookup_in_database(self.result_decimal.text())
        )

        # Initialize ternary displays
        self._update_first_ternary()
        self._update_second_ternary()

    def _update_first_ternary(self):
        """Update the ternary display for the first number."""
        try:
            decimal_value = int(self.first_number.text() or "0")
            ternary_str = decimal_to_ternary(decimal_value)
            self.first_ternary.setText(ternary_str)
        except ValueError:
            self.first_ternary.setText("Invalid input")

    def _update_second_ternary(self):
        """Update the ternary display for the second number."""
        try:
            decimal_value = int(self.second_number.text() or "0")
            ternary_str = decimal_to_ternary(decimal_value)
            self.second_ternary.setText(ternary_str)
        except ValueError:
            self.second_ternary.setText("Invalid input")

    def get_numbers(self) -> Optional[Tuple[int, int]]:
        """Get the current pair of numbers.

        Returns:
            Tuple of (first_number, second_number) or None if invalid
        """
        try:
            first = int(self.first_number.text() or "0")
            second = int(self.second_number.text() or "0")
            return first, second
        except ValueError:
            return None

    def update_result(self, decimal_result: int, ternary_result: str):
        """Update the transition result display.

        Args:
            decimal_result: The decimal form of the result
            ternary_result: The ternary form of the result
        """
        self.result_decimal.setText(str(decimal_result))
        self.result_ternary.setText(ternary_result)
        self.grid_button.setEnabled(True)
        self.lookup_button.setEnabled(True)

    def _open_in_tq_grid(self, number_text: str):
        """Open the result number in TQ Grid."""
        try:
            from tq.services import tq_analysis_service

            number = int(number_text)
            analysis_service = tq_analysis_service.get_instance()
            analysis_service.open_quadset_analysis(number)
        except Exception as e:
            logger.error(f"Error opening TQ Grid: {e}")

    def _lookup_in_database(self, number_text: str):
        """Look up the result number in the database."""
        try:
            number = int(number_text)
            from tq.ui.dialogs.number_database_window import NumberDatabaseWindow

            parent = self.window()
            if parent and hasattr(parent, "window_manager"):
                window_id = f"number_database_{number}"
                parent.window_manager.open_window(
                    window_id,
                    NumberDatabaseWindow(number),
                    f"Number Database: {number}",
                    (800, 600),
                )
            else:
                db_window = NumberDatabaseWindow(number)
                db_window.show()
        except Exception as e:
            logger.error(f"Error looking up in database: {e}")


class SeriesTransitionWidget(QWidget):
    """Widget for analyzing transitions between series of number pairs."""

    def __init__(self, parent=None):
        """Initialize the widget."""
        super().__init__(parent)

        self._init_ui()
        logger.debug("SeriesTransitionWidget initialized")

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title and description
        title = QLabel("Series Transition Analysis")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        description = QLabel(
            "This calculator performs transition operations between pairs of numbers "
            "and analyzes the series results. Enter pairs of numbers to calculate "
            "their individual transitions and series properties."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)

        # Pairs input section
        pairs_group = QGroupBox("Number Pairs")
        pairs_layout = QVBoxLayout(pairs_group)

        # Scrollable area for pairs
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        self.pairs_layout = QVBoxLayout(scroll_content)
        self.pairs_layout.setSpacing(10)

        self.pair_inputs = []
        self._add_number_pair()  # Start with one pair
        self._add_number_pair()  # Add second pair

        scroll.setWidget(scroll_content)
        pairs_layout.addWidget(scroll)

        # Add/Remove buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Pair")
        add_btn.clicked.connect(self._add_number_pair)
        remove_btn = QPushButton("Remove Pair")
        remove_btn.clicked.connect(self._remove_number_pair)
        button_layout.addWidget(add_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addStretch()
        pairs_layout.addLayout(button_layout)

        layout.addWidget(pairs_group)

        # Calculate button
        calc_btn = QPushButton("Calculate Series Transitions")
        calc_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        calc_btn.clicked.connect(self._calculate_transitions)
        layout.addWidget(calc_btn)

        # Results section
        results_group = QGroupBox("Series Results")
        results_layout = QGridLayout(results_group)

        # Transition Sum
        results_layout.addWidget(QLabel("Series Sum:"), 0, 0)
        self.series_sum_decimal = QLabel("0")
        self.series_sum_decimal.setStyleSheet("font-size: 16px; font-weight: bold;")
        results_layout.addWidget(self.series_sum_decimal, 0, 1)

        series_sum_actions = QHBoxLayout()
        self.series_sum_grid = QPushButton("Open in TQ Grid")
        self.series_sum_lookup = QPushButton("Look up in Database")
        series_sum_actions.addWidget(self.series_sum_grid)
        series_sum_actions.addWidget(self.series_sum_lookup)
        results_layout.addLayout(series_sum_actions, 0, 2)

        results_layout.addWidget(QLabel("Ternary:"), 1, 0)
        self.series_sum_ternary = QLabel("0")
        self.series_sum_ternary.setStyleSheet(
            "font-family: monospace; font-size: 16px; font-weight: bold;"
        )
        results_layout.addWidget(self.series_sum_ternary, 1, 1, 1, 2)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        results_layout.addWidget(separator, 2, 0, 1, 3)

        # Closed Loop Sum
        results_layout.addWidget(QLabel("Closed Loop Sum:"), 3, 0)
        self.closed_loop_decimal = QLabel("0")
        self.closed_loop_decimal.setStyleSheet("font-size: 16px; font-weight: bold;")
        results_layout.addWidget(self.closed_loop_decimal, 3, 1)

        closed_loop_actions = QHBoxLayout()
        self.closed_loop_grid = QPushButton("Open in TQ Grid")
        self.closed_loop_lookup = QPushButton("Look up in Database")
        closed_loop_actions.addWidget(self.closed_loop_grid)
        closed_loop_actions.addWidget(self.closed_loop_lookup)
        results_layout.addLayout(closed_loop_actions, 3, 2)

        results_layout.addWidget(QLabel("Ternary:"), 4, 0)
        self.closed_loop_ternary = QLabel("0")
        self.closed_loop_ternary.setStyleSheet(
            "font-family: monospace; font-size: 16px; font-weight: bold;"
        )
        results_layout.addWidget(self.closed_loop_ternary, 4, 1, 1, 2)

        # Add separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        results_layout.addWidget(separator2, 5, 0, 1, 3)

        # Amalgam
        results_layout.addWidget(QLabel("Amalgam:"), 6, 0)
        self.amalgam_decimal = QLabel("0")
        self.amalgam_decimal.setStyleSheet("font-size: 16px; font-weight: bold;")
        results_layout.addWidget(self.amalgam_decimal, 6, 1)

        amalgam_actions = QHBoxLayout()
        self.amalgam_grid = QPushButton("Open in TQ Grid")
        self.amalgam_lookup = QPushButton("Look up in Database")
        amalgam_actions.addWidget(self.amalgam_grid)
        amalgam_actions.addWidget(self.amalgam_lookup)
        results_layout.addLayout(amalgam_actions, 6, 2)

        results_layout.addWidget(QLabel("Ternary:"), 7, 0)
        self.amalgam_ternary = QLabel("0")
        self.amalgam_ternary.setStyleSheet(
            "font-family: monospace; font-size: 16px; font-weight: bold;"
        )
        results_layout.addWidget(self.amalgam_ternary, 7, 1, 1, 2)

        layout.addWidget(results_group)

        # Initially disable action buttons
        self._set_buttons_enabled(False)

        # Connect action buttons
        self.series_sum_grid.clicked.connect(
            lambda: self._open_in_tq_grid(self.series_sum_decimal.text())
        )
        self.series_sum_lookup.clicked.connect(
            lambda: self._lookup_in_database(self.series_sum_decimal.text())
        )
        self.closed_loop_grid.clicked.connect(
            lambda: self._open_in_tq_grid(self.closed_loop_decimal.text())
        )
        self.closed_loop_lookup.clicked.connect(
            lambda: self._lookup_in_database(self.closed_loop_decimal.text())
        )
        self.amalgam_grid.clicked.connect(
            lambda: self._open_in_tq_grid(self.amalgam_decimal.text())
        )
        self.amalgam_lookup.clicked.connect(
            lambda: self._lookup_in_database(self.amalgam_decimal.text())
        )

    def _add_number_pair(self):
        """Add a new number pair input."""
        input_widget = NumberPairWidget()
        self.pair_inputs.append(input_widget)
        self.pairs_layout.addWidget(input_widget)

    def _remove_number_pair(self):
        """Remove the last number pair input."""
        if len(self.pair_inputs) > 2:  # Keep at least 2 pairs
            input_widget = self.pair_inputs.pop()
            input_widget.deleteLater()

    def add_number_pair(self, first: int, second: int):
        """Add a new number pair with pre-filled values.

        Args:
            first: The first number of the pair
            second: The second number of the pair
        """
        logger.debug(f"Adding number pair: {first} → {second}")

        # Create new pair widget
        input_widget = NumberPairWidget()

        # Set the values
        input_widget.first_number.setText(str(first))
        input_widget.second_number.setText(str(second))

        # Add to layout
        self.pair_inputs.append(input_widget)
        self.pairs_layout.addWidget(input_widget)

        logger.debug("Number pair added successfully")

    def clear_pairs(self):
        """Clear all existing pairs and reset to initial state with two pairs."""
        logger.debug("Clearing all number pairs")

        # Remove all existing pairs
        while self.pair_inputs:
            input_widget = self.pair_inputs.pop()
            input_widget.deleteLater()

        # Add back two empty pairs
        self._add_number_pair()
        self._add_number_pair()
        logger.debug("Reset to two empty pairs")

    def _calculate_transitions(self):
        """Calculate transitions between all number pairs."""
        try:
            # Import and initialize the service
            from tq.services.series_transition_service import SeriesTransitionService

            # Get or create service instance (this will register it with ServiceLocator)
            service = SeriesTransitionService.get_instance()
            logger.debug("Initialized SeriesTransitionService singleton")

            # Get all number pairs
            pairs = []
            for pair_widget in self.pair_inputs:
                numbers = pair_widget.get_numbers()
                if numbers:
                    pairs.extend(numbers)

            if not pairs:
                return

            # Calculate transitions using the service
            result = service.calculate_series_transitions(pairs)
            if not result:
                return

            # Update each pair widget with its transition result
            for i, (decimal_result, ternary_result) in enumerate(
                zip(result.transitions, result.transition_ternaries)
            ):
                if i < len(self.pair_inputs):
                    self.pair_inputs[i].update_result(decimal_result, ternary_result)

            # Update the overall results display
            self._update_results_display(result)

        except Exception as e:
            logger.error(f"Error calculating transitions: {e}")
            QMessageBox.warning(
                self, "Error", f"Could not calculate transitions: {str(e)}"
            )

    def _update_results_display(self, result):
        """Update the display with calculation results.

        Args:
            result: SeriesTransitionResult containing the calculation results
        """
        logger.debug("Updating results display")

        # Update series sum
        self.series_sum_decimal.setText(str(result.transition_sum))
        self.series_sum_ternary.setText(decimal_to_ternary(result.transition_sum))

        # Update closed loop sum
        self.closed_loop_decimal.setText(str(result.closed_loop_sum))
        self.closed_loop_ternary.setText(decimal_to_ternary(result.closed_loop_sum))

        # Update amalgam
        self.amalgam_decimal.setText(str(result.amalgam))
        self.amalgam_ternary.setText(decimal_to_ternary(result.amalgam))

        # Enable all action buttons
        self._set_buttons_enabled(True)

        logger.debug("Results display updated")

    def _set_buttons_enabled(self, enabled: bool):
        """Enable or disable all action buttons.

        Args:
            enabled: Whether to enable or disable the buttons
        """
        self.series_sum_grid.setEnabled(enabled)
        self.series_sum_lookup.setEnabled(enabled)
        self.closed_loop_grid.setEnabled(enabled)
        self.closed_loop_lookup.setEnabled(enabled)
        self.amalgam_grid.setEnabled(enabled)
        self.amalgam_lookup.setEnabled(enabled)

    def _open_in_tq_grid(self, number_text: str):
        """Open a number in TQ Grid."""
        try:
            from tq.services import tq_analysis_service

            number = int(number_text)
            analysis_service = tq_analysis_service.get_instance()
            analysis_service.open_quadset_analysis(number)
        except Exception as e:
            logger.error(f"Error opening TQ Grid: {e}")

    def _lookup_in_database(self, number_text: str):
        """Look up a number in the database."""
        try:
            number = int(number_text)
            from tq.ui.dialogs.number_database_window import NumberDatabaseWindow

            parent = self.window()
            if parent and hasattr(parent, "window_manager"):
                window_id = f"number_database_{number}"
                parent.window_manager.open_window(
                    window_id,
                    NumberDatabaseWindow(number),
                    f"Number Database: {number}",
                    (800, 600),
                )
            else:
                db_window = NumberDatabaseWindow(number)
                db_window.show()
        except Exception as e:
            logger.error(f"Error looking up in database: {e}")


if __name__ == "__main__":
    """Simple demonstration of the Series Transition widget."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = SeriesTransitionWidget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
