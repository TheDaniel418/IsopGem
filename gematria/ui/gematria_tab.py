"""Gematria tab implementation.

This module provides the main tab for the Gematria pillar.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout
from loguru import logger

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
        from gematria.ui.widgets.word_abacus_widget import WordAbacusWidget
        from gematria.ui.panels.word_abacus_panel import WordAbacusPanel
        from gematria.ui.dialogs.word_abacus_window import WordAbacusWindow
        from gematria.ui.panels.calculation_history_panel import CalculationHistoryPanel
        from gematria.ui.panels.tag_management_panel import TagManagementPanel
        
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
        
        # Dictionary button (placeholder) - changed to use window
        dict_btn = QPushButton("Dictionary")
        dict_btn.setToolTip("Open Gematria Dictionary")
        dict_btn.clicked.connect(lambda: logger.info("Dictionary not yet implemented"))
        button_layout.addWidget(dict_btn)
        
        # Analysis button (placeholder) - changed to use window
        analysis_btn = QPushButton("Analyze")
        analysis_btn.setToolTip("Open Gematria Analysis")
        analysis_btn.clicked.connect(lambda: logger.info("Analysis not yet implemented"))
        button_layout.addWidget(analysis_btn)
        
        # Add stretch to push buttons to the left
        button_layout.addStretch()
        
        # Add button bar to main layout
        layout.addWidget(button_bar)

        # Title and welcome message
        title = QLabel("Gematria")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        welcome = QLabel("Welcome to the Gematria pillar. Please select a tool from the buttons above.")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(welcome)
        layout.addStretch() 

    def _open_word_abacus_window(self) -> None:
        """Open the Word Abacus window."""
        from gematria.ui.dialogs.word_abacus_window import WordAbacusWindow
        self.window_manager.open_window(
            "gematria_word_abacus",
            WordAbacusWindow(),
            "Gematria Word Abacus"
        )
        
    def _open_calculation_history(self) -> None:
        """Open the Calculation History panel."""
        from gematria.ui.panels.calculation_history_panel import CalculationHistoryPanel
        self.window_manager.open_window(
            "gematria_calculation_history",
            CalculationHistoryPanel(),
            "Calculation History"
        )
        
    def _open_tag_management(self) -> None:
        """Open the Tag Management panel."""
        from gematria.ui.panels.tag_management_panel import TagManagementPanel
        self.window_manager.open_window(
            "gematria_tag_management",
            TagManagementPanel(),
            "Tag Management"
        ) 