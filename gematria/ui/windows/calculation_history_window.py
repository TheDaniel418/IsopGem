"""
Purpose: Provides a standalone window for viewing and managing calculation history

This file is part of the gematria pillar and serves as a UI component.
It provides a dedicated window interface for the calculation history panel,
allowing users to view and manage their saved calculations.

Key components:
- CalculationHistoryWindow: Standalone window for calculation history

Dependencies:
- PyQt6: For UI components
- gematria.ui.panels.calculation_history_panel: For the calculation history panel content
"""

from typing import Optional

from loguru import logger
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from gematria.ui.panels.calculation_history_panel import CalculationHistoryPanel


class CalculationHistoryWindow(QMainWindow):
    """Standalone window for viewing and managing calculation history."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the calculation history window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Calculation History")
        self.setMinimumSize(900, 700)

        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create calculation history panel
        self.history_panel = CalculationHistoryPanel()
        layout.addWidget(self.history_panel)

        logger.debug("CalculationHistoryWindow initialized") 