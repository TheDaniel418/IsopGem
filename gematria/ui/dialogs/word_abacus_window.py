"""Gematria Word Abacus window.

This module provides a standalone window for the Gematria Word Abacus.
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
