"""
Purpose: Provides a panel for finding conrune pairs based on difference values

This file is part of the tq pillar and serves as a UI component.
It is responsible for finding pairs of numbers whose conrune transformation
results in a specific difference value.

Key components:
- PairFinderPanel: Panel for inputting difference values and displaying conrune pairs

Dependencies:
- tq.utils.ternary_converter: For ternary number conversions
- tq.utils.ternary_transition: For conrune transformations
- tq.ui.widgets.ternary_visualizer: For visualizing the ternary numbers

Related files:
- tq/utils/ternary_converter.py: Utilities for ternary conversions
- tq/utils/ternary_transition.py: Conrune transformation utilities
- tq/ui/widgets/ternary_visualizer.py: Visualization of ternary numbers
"""

from typing import Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from tq.ui.widgets.ternary_visualizer import TernaryDigitVisualizer
from tq.utils.ternary_converter import (
    balanced_to_original,
    decimal_to_balanced_ternary,
    ternary_to_decimal,
)
from tq.utils.ternary_transition import TernaryTransition


class PairFinderPanel(QFrame):
    """
    Panel for finding conrune pairs based on difference values.

    Allows users to input a difference value and displays the corresponding
    pair of numbers that have that difference when one is transformed
    to its conrune.
    """

    def __init__(self, parent=None):
        """Initialize the pair finder panel."""
        super().__init__(parent)

        # Create the ternary transition utility
        self.transition = TernaryTransition()

        # Set up the main layout
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create title
        title_label = QLabel("Conrune Pair Finder")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Create description
        description = QLabel(
            "Enter a difference value to find the pair of numbers that have "
            "that difference when one is transformed to its conrune."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 12px; color: #666;")
        main_layout.addWidget(description)

        # Create input area
        input_layout = QHBoxLayout()

        self.difference_input = QLineEdit()
        self.difference_input.setPlaceholderText("Enter difference value")

        find_button = QPushButton("Find Pair")
        find_button.clicked.connect(self._find_pair)

        input_layout.addWidget(QLabel("Difference:"))
        input_layout.addWidget(self.difference_input)
        input_layout.addWidget(find_button)

        main_layout.addLayout(input_layout)

        # Create results area
        results_layout = QHBoxLayout()

        # Original number section
        original_layout = QVBoxLayout()
        original_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.original_label = QLabel("Original Number (A)")
        self.original_label.setStyleSheet("font-weight: bold;")

        self.original_ternary = QLabel("Ternary: ")
        self.original_decimal = QLabel("Decimal: ")

        original_layout.addWidget(self.original_label)
        original_layout.addWidget(self.original_ternary)
        original_layout.addWidget(self.original_decimal)

        self.original_visualizer = TernaryDigitVisualizer()
        original_layout.addWidget(self.original_visualizer)

        # Conrune number section
        conrune_layout = QVBoxLayout()
        conrune_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.conrune_label = QLabel("Conrune Number (B)")
        self.conrune_label.setStyleSheet("font-weight: bold;")

        self.conrune_ternary = QLabel("Ternary: ")
        self.conrune_decimal = QLabel("Decimal: ")

        conrune_layout.addWidget(self.conrune_label)
        conrune_layout.addWidget(self.conrune_ternary)
        conrune_layout.addWidget(self.conrune_decimal)

        self.conrune_visualizer = TernaryDigitVisualizer()
        conrune_layout.addWidget(self.conrune_visualizer)

        results_layout.addLayout(original_layout)
        results_layout.addLayout(conrune_layout)

        main_layout.addLayout(results_layout)

        # Add verification label
        self.verification_label = QLabel()
        self.verification_label.setStyleSheet("font-weight: bold; color: #008800;")
        self.verification_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.verification_label)

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("QFrame { background-color: #f5f5f5; border-radius: 5px; }")

    def _find_pair(self):
        """Find the conrune pair for the given difference value."""
        try:
            # Get and validate input
            difference = int(self.difference_input.text())
            if difference < 0:
                raise ValueError("Difference must be non-negative")

            # Find the pair
            original, conrune = self._calculate_pair(difference)

            # Update displays
            self._update_displays(original, conrune)

        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Input",
                str(e) or "Please enter a valid non-negative integer",
            )

    def _calculate_pair(self, difference: int) -> Tuple[str, str]:
        """
        Calculate the original and conrune numbers for a given difference.

        Args:
            difference: The target difference between the numbers

        Returns:
            Tuple[str, str]: The original and conrune numbers in ternary
        """
        # Convert difference to balanced ternary
        balanced = decimal_to_balanced_ternary(difference)

        # Convert to original ternary
        original = balanced_to_original(balanced)

        # Generate conrune
        conrune = self.transition.apply_conrune(original)

        return original, conrune

    def _update_displays(self, original: str, conrune: str):
        """
        Update all displays with the found pair.

        Args:
            original: Original number in ternary
            conrune: Conrune number in ternary
        """
        # Convert to decimals
        original_dec = ternary_to_decimal(original)
        conrune_dec = ternary_to_decimal(conrune)

        # Update labels
        self.original_ternary.setText(f"Ternary: {original}")
        self.original_decimal.setText(f"Decimal: {original_dec}")

        self.conrune_ternary.setText(f"Ternary: {conrune}")
        self.conrune_decimal.setText(f"Decimal: {conrune_dec}")

        # Update visualizers
        self.original_visualizer.set_ternary(original)
        self.conrune_visualizer.set_ternary(conrune)

        # Update verification
        difference = abs(original_dec - conrune_dec)
        self.verification_label.setText(
            f"Verification: |{original_dec} - {conrune_dec}| = {difference}"
        )


if __name__ == "__main__":
    """Simple demonstration of the pair finder panel."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = PairFinderPanel()
    panel.resize(600, 800)
    panel.show()
    sys.exit(app.exec())
