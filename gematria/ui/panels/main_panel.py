"""
Purpose: Provides the main panel for the Gematria functionality

This file is part of the gematria pillar and serves as a UI component.
It is responsible for organizing and presenting the main interface for
Gematria calculations and related features, acting as a container for
various sub-panels and components.

Key components:
- MainPanel: Primary panel class that integrates different Gematria features

Dependencies:
- PyQt6: For the graphical user interface components
- gematria.ui.panels: Sub-panels that compose the main interface

Related files:
- gematria/ui/panels/word_abacus_panel.py: Calculator panel included in the main panel
- gematria/ui/panels/calculation_history_panel.py: History panel included in the main panel
- gematria/ui/panels/tag_management_panel.py: Tag management panel included in the main panel
"""

from typing import Optional

from loguru import logger
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from gematria.ui.panels.calculation_history_panel import CalculationHistoryPanel
from gematria.ui.panels.tag_management_panel import TagManagementPanel
from gematria.ui.panels.word_abacus_panel import WordAbacusPanel


class MainPanel(QWidget):
    """Main panel for Gematria functionality.

    This panel serves as the container for all Gematria-related UI components,
    organizing them in a tabbed interface for easy navigation.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the main panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initialize UI
        self._init_ui()

        logger.debug("MainPanel initialized")

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # Create and add panels
        self.word_abacus_panel = WordAbacusPanel()
        self.history_panel = CalculationHistoryPanel()
        self.tag_panel = TagManagementPanel()

        # Add tabs
        self.tab_widget.addTab(self.word_abacus_panel, "Calculator")
        self.tab_widget.addTab(self.history_panel, "History")
        self.tab_widget.addTab(self.tag_panel, "Tags")

        # Add tab widget to layout
        layout.addWidget(self.tab_widget)

        # Connect signals
        self.word_abacus_panel.calculation_performed.connect(
            self._on_calculation_performed
        )

    def _on_calculation_performed(self, result):
        """Handle when a calculation is performed.

        Args:
            result: The calculation result
        """
        # Switch to the history tab to show the new calculation
        self.tab_widget.setCurrentWidget(self.history_panel)
