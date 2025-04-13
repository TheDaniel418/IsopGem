"""
Purpose: Provides a standalone window for gematria search functionality

This file is part of the gematria pillar and serves as a UI component.
It provides a dedicated window interface for the search panel,
allowing users to search for gematria values and patterns.

Key components:
- SearchWindow: Standalone window for gematria search

Dependencies:
- PyQt6: For UI components
- gematria.ui.panels.search_panel: For the search panel content
- gematria.services: For the database and cipher services
"""

from typing import Optional

from loguru import logger
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.ui.panels.search_panel import SearchPanel
from shared.ui.window_management import WindowManager


class SearchWindow(QMainWindow):
    """Standalone window for gematria search functionality."""

    def __init__(
        self,
        window_manager: Optional[WindowManager] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the search window.

        Args:
            window_manager: Application window manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Gematria Search")
        self.setMinimumSize(900, 700)

        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create services needed by the search panel
        db_service = CalculationDatabaseService()
        cipher_service = CustomCipherService()

        # Create the search panel
        self.search_panel = SearchPanel(db_service, cipher_service, window_manager)
        layout.addWidget(self.search_panel)

        logger.debug("SearchWindow initialized")
