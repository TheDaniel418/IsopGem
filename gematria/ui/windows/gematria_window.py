"""
Purpose: Provides the main window for the Gematria functionality

This file is part of the gematria pillar and serves as a UI component.
It is responsible for creating and managing the main Gematria window
that hosts all the Gematria-related panels and functionality.

Key components:
- GematriaWindow: Main window class for the Gematria pillar

Dependencies:
- PyQt6: For the graphical user interface components
- shared.ui.window_management: For window management functionality
- gematria.ui.gematria_tab: For the main Gematria tab component

Related files:
- gematria/ui/gematria_tab.py: Main tab component hosted in this window
- shared/ui/window_management.py: Window management system
"""

from typing import Optional
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QDockWidget
from PyQt6.QtCore import Qt

from loguru import logger

from shared.ui.window_management import TabManager, WindowManager
from gematria.ui.gematria_tab import GematriaTab


class GematriaWindow(QMainWindow):
    """Main window for the Gematria pillar.

    This window serves as the container for all Gematria-related UI components,
    organizing them in a tabbed interface and providing docking capabilities.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the Gematria window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set window properties
        self.setWindowTitle("IsopGem - Gematria")
        self.resize(1200, 800)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        # Create window components
        self._tab_manager = TabManager(self)
        self._window_manager = WindowManager(self)
        self._window_manager.set_tab_manager(self._tab_manager)

        # Set the tab manager as the central widget
        self.setCentralWidget(self._tab_manager)

        # Initialize the UI
        self._init_ui()

        logger.debug("GematriaWindow initialized")

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Create the main tab for Gematria
        self._gematria_tab = GematriaTab(self._tab_manager, self._window_manager)

        # Add the tab to the tab manager
        self._tab_manager.addTab(self._gematria_tab, "Gematria")
