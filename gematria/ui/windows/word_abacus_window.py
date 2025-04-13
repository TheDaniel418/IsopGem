"""
Purpose: Provides a standalone window for the Gematria Word Abacus functionality.

This file is part of the gematria pillar and serves as a UI component.
It provides a dedicated window interface for the Word Abacus calculator,
allowing users to perform gematria calculations in a separate window.

Key components:
- WordAbacusWindow: Standalone window for Word Abacus calculations

Dependencies:
- PyQt6: For UI components
- gematria.ui.panels.word_abacus_panel: For the Word Abacus panel content
- gematria.models.calculation_result: For calculation data structures
"""

from typing import Optional

from loguru import logger
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from gematria.models.calculation_result import CalculationResult
from gematria.ui.panels.word_abacus_panel import WordAbacusPanel


class WordAbacusWindow(QMainWindow):
    """Standalone window for Word Abacus calculations."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the Word Abacus window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Gematria Word Abacus")
        self.setMinimumSize(800, 600)

        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create Word Abacus panel (includes the help button)
        self.word_abacus_panel = WordAbacusPanel()
        layout.addWidget(self.word_abacus_panel)

        # Connect signals
        self.word_abacus_panel.calculation_performed.connect(
            self._on_calculation_performed
        )

        logger.debug("WordAbacusWindow initialized")

    def _on_calculation_performed(self, result: CalculationResult) -> None:
        """Handle when a calculation is performed.

        Args:
            result: The calculation result
        """
        # Update window title with latest calculation info
        self.setWindowTitle(
            f"Gematria Word Abacus - {result.input_text} = {result.result_value}"
        )
        logger.debug(
            f"Calculation performed: {result.input_text} = {result.result_value}"
        )

    def clear_history(self) -> None:
        """Clear the calculation history."""
        self.word_abacus_panel.clear_history()

    def reset_calculator(self) -> None:
        """Reset the calculator to its initial state."""
        self.word_abacus_panel.reset_calculator()
