"""
Purpose: Provides a standalone window for Word Group Chain Calculator functionality.

This file is part of the gematria pillar and serves as a UI component.
It provides a dedicated window interface for organizing words into groups
and creating calculation chains between words from different groups.

Key components:
- WordGroupChainWindow: Standalone window for Word Group Chain calculations

Dependencies:
- PyQt6: For UI components
- gematria.ui.panels.word_group_chain_panel: For the Word Group Chain panel content
"""

from typing import List, Optional

from loguru import logger
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from gematria.models.calculation_result import CalculationResult
from gematria.ui.panels.word_group_chain_panel import WordGroupChainPanel
from shared.ui.window_management import WindowManager


class WordGroupChainWindow(QMainWindow):
    """Standalone window for Word Group Chain calculations."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        window_manager: Optional[WindowManager] = None,
    ) -> None:
        """Initialize the Word Group Chain window.

        Args:
            parent: Parent widget
            window_manager: Window manager instance
        """
        super().__init__(parent)
        self.setWindowTitle("Gematria Word Group & Chain Calculator")
        self.setMinimumSize(1000, 700)
        self.window_manager = window_manager

        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create Word Group Chain panel with window manager
        self.word_group_chain_panel = WordGroupChainPanel(
            window_manager=self.window_manager
        )
        layout.addWidget(self.word_group_chain_panel)

        logger.debug("WordGroupChainWindow initialized")

    def import_calculation_results(self, results: List[CalculationResult]) -> bool:
        """Import calculation results into the panel.

        Args:
            results: List of calculation results

        Returns:
            True if imported successfully, False otherwise
        """
        return self.word_group_chain_panel.import_calculation_results(results)

    def add_calculation_result(self, result: CalculationResult) -> bool:
        """Add a single calculation result to the selected group.

        Args:
            result: The calculation result to add

        Returns:
            True if added successfully, False otherwise
        """
        return self.word_group_chain_panel.add_calculation_result(result)

    def reset(self) -> None:
        """Reset the Word Group Chain to its initial state."""
        self.word_group_chain_panel.reset()
