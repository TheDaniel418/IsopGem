"""Gematria tab implementation.

This module provides the main tab for the Gematria pillar.
"""

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from shared.ui.window_management import TabManager, WindowManager


class GematriaTab(QWidget):
    """Main tab for the Gematria pillar."""

    def __init__(self, tab_manager: TabManager, window_manager: WindowManager) -> None:
        """Initialize the Gematria tab.

        Args:
            tab_manager: Application tab manager
            window_manager: Application window manager
        """
        super().__init__()
        self.tab_manager = tab_manager
        self.window_manager = window_manager
        self._init_ui()
        logger.debug("GematriaTab initialized")

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Button bar
        button_bar = QWidget()
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(5)

        # Create button

        # Word Abacus button
        word_abacus_btn = QPushButton("Word Abacus")
        word_abacus_btn.setToolTip("Open Gematria Word Abacus")
        word_abacus_btn.clicked.connect(lambda: self._open_word_abacus_window())
        button_layout.addWidget(word_abacus_btn)

        # Calculation History button
        history_btn = QPushButton("Calculation History")
        history_btn.setToolTip("Open Calculation History")
        history_btn.clicked.connect(lambda: self._open_calculation_history())
        button_layout.addWidget(history_btn)

        # Tag Management button
        tags_btn = QPushButton("Manage Tags")
        tags_btn.setToolTip("Open Tag Management")
        tags_btn.clicked.connect(lambda: self._open_tag_management())
        button_layout.addWidget(tags_btn)

        # Search button (replaces Dictionary button)
        search_btn = QPushButton("Search")
        search_btn.setToolTip("Search Gematria Calculations")
        search_btn.clicked.connect(lambda: self._open_search_panel())
        button_layout.addWidget(search_btn)

        # Add stretch to push buttons to the left
        button_layout.addStretch()

        # Help button (right-aligned)
        help_btn = QPushButton("Help")
        help_btn.setToolTip("Show Gematria calculation methods help")
        help_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        help_btn.clicked.connect(self._show_help)
        button_layout.addWidget(help_btn)

        # Add button bar to main layout
        layout.addWidget(button_bar)

        # Title and welcome message
        title = QLabel("Gematria")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        welcome = QLabel(
            "Welcome to the Gematria pillar. Please select a tool from the buttons above."
        )
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(welcome)
        layout.addStretch()

    def _open_word_abacus_window(self) -> None:
        """Open the Word Abacus window."""
        from gematria.ui.dialogs.word_abacus_window import WordAbacusWindow

        self.window_manager.open_window(
            "gematria_word_abacus", WordAbacusWindow(), "Gematria Word Abacus"
        )

    def _open_calculation_history(self) -> None:
        """Open the Calculation History panel."""
        from gematria.ui.panels.calculation_history_panel import CalculationHistoryPanel

        self.window_manager.open_window(
            "gematria_calculation_history",
            CalculationHistoryPanel(),
            "Calculation History",
        )

    def _open_tag_management(self) -> None:
        """Open the Tag Management panel."""
        from gematria.ui.panels.tag_management_panel import TagManagementPanel

        self.window_manager.open_window(
            "gematria_tag_management", TagManagementPanel(), "Tag Management"
        )

    def _open_search_panel(self) -> None:
        """Open the Search panel."""
        from gematria.services.calculation_database_service import (
            CalculationDatabaseService,
        )
        from gematria.services.custom_cipher_service import CustomCipherService
        from gematria.ui.panels.search_panel import SearchPanel

        # Create services needed by the search panel
        db_service = CalculationDatabaseService()
        cipher_service = CustomCipherService()

        # Create and open search panel
        self.window_manager.open_window(
            "gematria_search",
            SearchPanel(db_service, cipher_service, self.window_manager),
            "Gematria Search",
        )

    def _show_help(self) -> None:
        """Show the Gematria help dialog."""
        from gematria.ui.dialogs.gematria_help_dialog import GematriaHelpDialog

        # Create non-modal help dialog
        dialog = GematriaHelpDialog(self)
        dialog.setModal(False)
        dialog.show()
