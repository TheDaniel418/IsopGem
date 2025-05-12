"""
Purpose: Provides a standalone window for the Gematria Word List Abacus functionality.

This file is part of the gematria pillar and serves as a UI component.
It provides a dedicated window interface for the Word List Abacus,
allowing users to calculate gematria values for lists of words.

Key components:
- WordListAbacusWindow: Standalone window for Word List Abacus calculations

Dependencies:
- PyQt6: For UI components
- gematria.ui.panels.word_list_abacus_panel: For the Word List Abacus panel content
"""

from typing import Optional

from loguru import logger
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from gematria.ui.panels.word_list_abacus_panel import WordListAbacusPanel
from shared.ui.window_management import WindowManager


class WordListAbacusWindow(QMainWindow):
    """Standalone window for Word List Abacus calculations."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        window_manager: Optional[WindowManager] = None,
    ) -> None:
        """Initialize the Word List Abacus window.

        Args:
            parent: Parent widget
            window_manager: Window manager instance
        """
        super().__init__(parent)
        self.setWindowTitle("Gematria Word List Abacus")
        self.setMinimumSize(900, 700)
        self.window_manager = window_manager

        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create Word List Abacus panel with window manager
        self.word_list_abacus_panel = WordListAbacusPanel(
            window_manager=self.window_manager
        )
        layout.addWidget(self.word_list_abacus_panel)

        logger.debug("WordListAbacusWindow initialized")

    def reset(self) -> None:
        """Reset the Word List Abacus to its initial state."""
        self.word_list_abacus_panel.reset()
