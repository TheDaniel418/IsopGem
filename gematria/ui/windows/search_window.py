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
        exact_value: Optional[int] = None,
    ) -> None:
        """Initialize the search window.

        Args:
            window_manager: Application window manager
            parent: Parent widget
            exact_value: Optional exact value to search for immediately
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

        # If an exact value was provided, set it and perform search
        if exact_value is not None:
            self.set_exact_value(exact_value)

        logger.debug("SearchWindow initialized")

    def set_exact_value(self, value: int) -> None:
        """Set the exact value field and perform a search.

        Args:
            value: The value to search for
        """
        # Set the exact value in the search panel
        self.search_panel.exact_value.setText(str(value))

        # Clear other value fields to avoid conflicts
        self.search_panel.value_min.setValue(0)
        self.search_panel.value_max.setValue(0)

        # Perform the search
        self.search_panel._perform_search()
