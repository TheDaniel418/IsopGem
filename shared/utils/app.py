"""Main application entry point.

This module initializes and starts the PyQt6 application.
"""

import sys
from typing import List, Optional

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from shared.ui.window_management import TabManager, WindowManager
from shared.utils.config import get_config


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        config = get_config()
        window_config = config.ui.window

        # Set window properties
        self.setWindowTitle(window_config.title)
        self.resize(window_config.width, window_config.height)

        # Get enabled pillars
        self.enabled_pillars = []
        if config.pillars.gematria.enabled:
            self.enabled_pillars.append("gematria")
        if config.pillars.geometry.enabled:
            self.enabled_pillars.append("geometry")
        if config.pillars.document_manager.enabled:
            self.enabled_pillars.append("document_manager")
        if config.pillars.astrology.enabled:
            self.enabled_pillars.append("astrology")
        if config.pillars.tq.enabled:
            self.enabled_pillars.append("tq")

        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Set up UI components
        self._init_menubar()
        self._init_toolbar()
        self._init_tabs()
        self._init_statusbar()

        # Create window manager
        self.window_manager = WindowManager(self)
        self.window_manager.set_tab_manager(self.tab_manager)

        # Initialize pillar components
        self._init_pillars()

        # Maximize window if configured
        if window_config.maximize_on_start:
            self.showMaximized()

    def _init_menubar(self) -> None:
        """Initialize the main menu bar."""
        self.menubar = self.menuBar()

        # File menu
        self.file_menu = self.menubar.addMenu("&File")

        # Add file actions
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self._close_application)
        self.file_menu.addAction(exit_action)

        # View menu
        self.view_menu = self.menubar.addMenu("&View")

        # Tools menu
        self.tools_menu = self.menubar.addMenu("&Tools")

        # Help menu
        self.help_menu = self.menubar.addMenu("&Help")

    def _init_toolbar(self) -> None:
        """Initialize the main toolbar."""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setObjectName("mainToolbar")
        self.addToolBar(self.toolbar)
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)

        # Add toolbar actions
        # This will be populated based on active pillar

    def _init_tabs(self) -> None:
        """Initialize the tab manager."""
        self.tab_manager = TabManager()
        self.main_layout.addWidget(self.tab_manager)

    def _init_statusbar(self) -> None:
        """Initialize the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Add status elements
        self.status_label = QLabel("Ready")
        self.statusbar.addWidget(self.status_label)

    def _init_pillars(self) -> None:
        """Initialize the pillar components based on configuration."""
        config = get_config()

        # Initialize tabs and panels for each enabled pillar
        if config.pillars.gematria.enabled:
            self._init_gematria_pillar()

        if config.pillars.geometry.enabled:
            self._init_geometry_pillar()

        if config.pillars.document_manager.enabled:
            self._init_document_manager_pillar()

        if config.pillars.astrology.enabled:
            self._init_astrology_pillar()

        if config.pillars.tq.enabled:
            self._init_tq_pillar()

    def _init_gematria_pillar(self) -> None:
        """Initialize the Gematria pillar components.

        This includes word abacus, dictionaries, and analyzers.
        """
        if "gematria" not in self.enabled_pillars:
            logger.debug("Gematria pillar is disabled")
            return

        logger.info("Initializing Gematria pillar")

        # Import the GematriaTab class
        from gematria.ui.gematria_tab import GematriaTab

        # Create and add the tab
        gematria_tab = GematriaTab(self.tab_manager, self.window_manager)
        self.tab_manager.addTab(gematria_tab, "Gematria")

        logger.debug("Gematria pillar initialized")

    def _init_geometry_pillar(self) -> None:
        """Initialize the Geometry pillar components."""
        if "geometry" not in self.enabled_pillars:
            logger.debug("Geometry pillar is disabled")
            return

        logger.info("Initializing Geometry pillar")

        # Add the tab
        geometry_tab = self.tab_manager.add_tab("Geometry")

        # Add shapes window button (placeholder for now)
        self.tab_manager.add_window_button(
            geometry_tab,
            "Shapes",
            "Open Sacred Geometry Shapes",
            lambda: self._show_geometry_shapes(),
        )

        # Add calculator window button (placeholder for now)
        self.tab_manager.add_window_button(
            geometry_tab,
            "Calculator",
            "Open Geometry Calculator",
            lambda: self._show_geometry_calculator(),
        )

        logger.debug("Geometry pillar initialized with placeholders")

    def _show_geometry_shapes(self) -> None:
        """Show the Geometry Shapes window."""
        # Create a placeholder window
        window = self.window_manager.create_auxiliary_window(
            "geometry_shapes", "Sacred Geometry Shapes"
        )

        # Create placeholder content
        content = QWidget()
        layout = QVBoxLayout(content)
        label = QLabel("Sacred Geometry Shapes will be implemented soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Set the content
        window.set_content(content)
        logger.debug("Using placeholder for Geometry Shapes window")

    def _show_geometry_calculator(self) -> None:
        """Show the Geometry Calculator window."""
        # Create a placeholder window
        window = self.window_manager.create_auxiliary_window(
            "geometry_calculator", "Geometry Calculator"
        )

        # Create placeholder content
        content = QWidget()
        layout = QVBoxLayout(content)
        label = QLabel("Geometry Calculator will be implemented soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Set the content
        window.set_content(content)
        logger.debug("Using placeholder for Geometry Calculator window")

    def _init_document_manager_pillar(self) -> None:
        """Initialize the Document Manager pillar components."""
        if "document_manager" not in self.enabled_pillars:
            logger.debug("Document Manager pillar is disabled")
            return

        logger.info("Initializing Document Manager pillar")

        # Add the tab
        doc_tab = self.tab_manager.add_tab("Documents")

        # Add placeholder button
        self.tab_manager.add_window_button(
            doc_tab,
            "Documents",
            "Open Document Manager",
            lambda: logger.info("Document Manager not yet implemented"),
        )

        logger.debug("Document Manager pillar initialized with placeholders")

    def _init_astrology_pillar(self) -> None:
        """Initialize the Astrology pillar components."""
        if "astrology" not in self.enabled_pillars:
            logger.debug("Astrology pillar is disabled")
            return

        logger.info("Initializing Astrology pillar")

        # Add the tab
        astro_tab = self.tab_manager.add_tab("Astrology")

        # Add placeholder button
        self.tab_manager.add_window_button(
            astro_tab,
            "Chart",
            "Open Astrology Chart",
            lambda: logger.info("Astrology Chart not yet implemented"),
        )

        logger.debug("Astrology pillar initialized with placeholders")

    def _init_tq_pillar(self) -> None:
        """Initialize the TQ pillar components."""
        if "tq" not in self.enabled_pillars:
            logger.debug("TQ pillar is disabled")
            return

        logger.info("Initializing TQ pillar")

        # Add the tab
        tq_tab = self.tab_manager.add_tab("TQ")

        # Add placeholder button
        self.tab_manager.add_window_button(
            tq_tab,
            "Analyzer",
            "Open TQ Analyzer",
            lambda: logger.info("TQ Analyzer not yet implemented"),
        )

        logger.debug("TQ pillar initialized with placeholders")

    def _close_application(self) -> None:
        """Close the application."""
        self.close()

    def closeEvent(self, event):
        """Handle window close event.

        Save window states before closing.
        """
        # Save window states
        self.window_manager.save_window_state()

        # Close all windows
        self.window_manager.close_all_windows()

        # Accept the close event
        event.accept()


def start_application(args: Optional[List[str]] = None) -> int:
    """Start the PyQt6 application.

    Args:
        args: Command-line arguments (uses sys.argv if None).

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    try:
        app = QApplication(args or sys.argv)

        # Set application name and organization
        config = get_config()
        app.setApplicationName(config.application.name)
        app.setApplicationVersion(config.application.version)
        app.setOrganizationName("IsopGem")

        # Set stylesheet based on theme
        theme = config.application.theme
        logger.debug(f"Using theme: {theme}")

        main_window = MainWindow()
        main_window.show()

        # Restore window state after showing
        main_window.window_manager.restore_window_state()

        logger.info("Application started successfully")
        return app.exec()
    except Exception as e:
        logger.exception(f"Failed to start application: {e}")
        return 1
