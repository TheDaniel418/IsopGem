"""
Standalone test script for the Quadset Analysis panel.
"""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from tq.services.tq_grid_service import TQGrid, TQGridService
from tq.ui.panels.quadset_analysis_panel import QuadsetAnalysisPanel


class SimpleQuadsetTester(QWidget):
    """Simple widget to test the QuadsetAnalysisPanel."""

    def __init__(self):
        """Initialize the tester widget."""
        super().__init__()

        # Initialize the TQGridService
        if TQGridService._instance is None:
            TQGridService.get_instance()

        # Set up the main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Create title
        title_label = QLabel("Quadset Analysis Tester")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.layout.addWidget(title_label)

        # Create input section
        input_layout = QHBoxLayout()

        # Base number input
        input_layout.addWidget(QLabel("Base:"))
        self.base_input = QLineEdit("42")
        self.base_input.setMaximumWidth(100)
        input_layout.addWidget(self.base_input)

        # Conrune input
        input_layout.addWidget(QLabel("Conrune:"))
        self.conrune_input = QLineEdit("24")
        self.conrune_input.setMaximumWidth(100)
        input_layout.addWidget(self.conrune_input)

        # Reversal input
        input_layout.addWidget(QLabel("Reversal:"))
        self.reversal_input = QLineEdit("21")
        self.reversal_input.setMaximumWidth(100)
        input_layout.addWidget(self.reversal_input)

        # Reversal Conrune input
        input_layout.addWidget(QLabel("Rev. Conrune:"))
        self.rev_conrune_input = QLineEdit("12")
        self.rev_conrune_input.setMaximumWidth(100)
        input_layout.addWidget(self.rev_conrune_input)

        # Update button
        self.update_button = QPushButton("Update")
        self.update_button.clicked.connect(self._update_quadset)
        input_layout.addWidget(self.update_button)

        input_layout.addStretch()
        self.layout.addLayout(input_layout)

        # Create the quadset analysis panel
        self.analysis_panel = QuadsetAnalysisPanel()
        self.layout.addWidget(self.analysis_panel, 1)  # Give it stretch

        # Set window properties
        self.setWindowTitle("Quadset Analysis Tester")
        self.resize(800, 600)

        # Initialize with default values
        self._update_quadset()

    def _update_quadset(self):
        """Update the quadset with values from the input fields."""
        try:
            # Get values from input fields
            base = int(self.base_input.text() or "0")
            conrune = int(self.conrune_input.text() or "0")
            reversal = int(self.reversal_input.text() or "0")
            rev_conrune = int(self.rev_conrune_input.text() or "0")

            # Update the TQGridService
            grid_service = TQGridService.get_instance()
            grid_service.update_grid_display(
                base=base,
                conrune=conrune,
                reversal=reversal,
                reversal_conrune=rev_conrune,
            )

            # Update the analysis panel
            self.analysis_panel.update_analysis()

        except ValueError:
            # Handle invalid input
            print("Invalid input. Please enter valid integers.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tester = SimpleQuadsetTester()
    tester.show()
    sys.exit(app.exec())
