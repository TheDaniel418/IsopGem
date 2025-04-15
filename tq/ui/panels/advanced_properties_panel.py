"""
Purpose: Provides a panel for displaying advanced properties and calculations for TQ Grid numbers

This file is part of the tq pillar and serves as a UI component.
It is responsible for displaying advanced calculations and relationships between
the numbers in a TQ Grid quadset, including differential transitions.

Key components:
- AdvancedPropertiesPanel: Panel for displaying advanced quadset properties

Dependencies:
- PyQt6: For the user interface components
- tq.services.tq_grid_service: For accessing the current quadset values
- tq.utils.ternary_transition: For calculating transitions between numbers

Related files:
- tq/ui/panels/tq_grid_panel.py: Main panel that hosts this advanced properties panel
- tq/services/tq_grid_service.py: Service that provides the quadset data
- tq/utils/ternary_transition.py: Utility for calculating ternary transitions
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from tq.services.tq_grid_service import TQGridService
from tq.ui.styles.tq_colors import apply_tq_styles
from tq.utils.ternary_converter import (
    decimal_to_ternary,
    format_ternary,
    ternary_to_decimal,
)
from tq.utils.ternary_transition import TernaryTransition


class AdvancedPropertiesPanel(QFrame):
    """Panel for displaying advanced properties of quadset numbers."""

    def __init__(self, parent=None):
        """Initialize the advanced properties panel.

        Args:
            parent: The parent widget
        """
        super().__init__(parent)

        # Apply TQ styling
        apply_tq_styles(self)

        # Create the ternary transition utility
        self.transition = TernaryTransition()

        # Set up the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # Create title
        title_label = QLabel("Advanced Properties")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setProperty("isTitle", "true")
        self.layout.addWidget(title_label)

        # Create content widget
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(15)

        # Create the differential trans section
        self.create_differential_trans_section()

        # Add the content widget to the main layout
        self.layout.addWidget(content_widget, 1)  # Give it stretch factor of 1

        # Set frame style
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(300)  # Set minimum width to match the 2:3:2 ratio

        # Get the grid service and register for updates
        self.grid_service = TQGridService.get_instance()
        self.grid_service.register_callback(self.update_properties)

        # Initialize with current grid values
        self.update_properties()

    def create_differential_trans_section(self):
        """Create the section for displaying differential transitions and septad."""
        # Create a container for the advanced properties
        advanced_layout = QVBoxLayout()
        advanced_layout.setContentsMargins(10, 10, 10, 10)
        advanced_layout.setSpacing(15)

        # Create layout for the differential trans
        diff_trans_layout = QHBoxLayout()
        diff_trans_layout.setContentsMargins(0, 0, 0, 0)
        diff_trans_layout.setSpacing(10)

        # Add label for the differential trans
        diff_trans_label = QLabel("Differential Trans:")
        diff_trans_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        diff_trans_layout.addWidget(diff_trans_label)

        # Add value label
        self.diff_trans_value = QLabel("--")
        self.diff_trans_value.setFont(QFont("Segoe UI", 12))
        self.diff_trans_value.setStyleSheet(
            "font-weight: bold; color: #1976D2;"
        )  # Blue color for emphasis
        diff_trans_layout.addWidget(self.diff_trans_value)

        # Add stretch to push everything to the left
        diff_trans_layout.addStretch(1)

        # Add the differential trans layout to the advanced layout
        advanced_layout.addLayout(diff_trans_layout)

        # Create layout for the septad
        septad_layout = QHBoxLayout()
        septad_layout.setContentsMargins(0, 0, 0, 0)
        septad_layout.setSpacing(10)

        # Add label for the septad
        septad_label = QLabel("Septad:")
        septad_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        septad_layout.addWidget(septad_label)

        # Add value label
        self.septad_value = QLabel("--")
        self.septad_value.setFont(QFont("Segoe UI", 12))
        self.septad_value.setStyleSheet(
            "font-weight: bold; color: #D81B60;"
        )  # Pink color for emphasis
        septad_layout.addWidget(self.septad_value)

        # Add stretch to push everything to the left
        septad_layout.addStretch(1)

        # Add the septad layout to the advanced layout
        advanced_layout.addLayout(septad_layout)

        # Add the advanced layout to the content layout
        self.content_layout.addLayout(advanced_layout)

        # Add stretch to push everything to the top
        self.content_layout.addStretch(1)

    def update_properties(self):
        """Update the properties with current quadset values."""
        # Get the current grid values
        grid = self.grid_service.get_current_grid()

        # Extract the values
        values = [grid.base_number, grid.conrune, grid.reversal, grid.reversal_conrune]

        # Calculate the differences
        base_conrune_diff = abs(values[0] - values[1])
        reversal_conrune_diff = abs(values[2] - values[3])

        # Calculate the actual transition using the TernaryTransition utility
        # Convert the differences to ternary strings
        first_ternary = decimal_to_ternary(base_conrune_diff)
        second_ternary = decimal_to_ternary(reversal_conrune_diff)

        # Ensure both ternary strings have the same length
        max_length = max(len(first_ternary), len(second_ternary))
        first_ternary_padded = format_ternary(first_ternary, pad_length=max_length)
        second_ternary_padded = format_ternary(second_ternary, pad_length=max_length)

        # Calculate the transition
        try:
            transition_ternary = self.transition.apply_transition(
                first_ternary_padded, second_ternary_padded
            )
            # Convert the ternary transition back to decimal
            transition_decimal = ternary_to_decimal(transition_ternary)
            # Display only the decimal value
            self.diff_trans_value.setText(str(transition_decimal))

            # Calculate the Septad
            # Sum of all 4 quadset numbers + 2 absolute differences + differential trans
            septad = (
                sum(values)
                + base_conrune_diff
                + reversal_conrune_diff
                + transition_decimal
            )
            self.septad_value.setText(str(septad))
        except Exception as e:
            # Handle any errors in the calculation
            self.diff_trans_value.setText(f"Error: {str(e)}")
            self.septad_value.setText("Error")

    def closeEvent(self, event):
        """Handle the panel being closed.

        Args:
            event: The close event
        """
        # Unregister the callback when the panel is closed
        self.grid_service.unregister_callback(self.update_properties)
        super().closeEvent(event)


if __name__ == "__main__":
    """Simple demonstration of the Advanced Properties panel."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = AdvancedPropertiesPanel()
    panel.resize(800, 600)
    panel.show()
    sys.exit(app.exec())
