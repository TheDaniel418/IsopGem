"""Main application entry point.

This module initializes and starts the PyQt6 application.
"""

import sys
from typing import List, Optional, cast

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QCloseEvent
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
        # Initialize with flags that ensure it doesn't stay on top
        flags = Qt.WindowType.Window & ~Qt.WindowType.WindowStaysOnTopHint
        super().__init__(None, flags)

        logger.debug("Main window configured with normal window flags")

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

        # Add database maintenance action
        database_maintenance_action = QAction("Database &Maintenance", self)
        database_maintenance_action.setStatusTip("Maintain and optimize database")
        database_maintenance_action.triggered.connect(self._show_database_maintenance)
        self.tools_menu.addAction(database_maintenance_action)

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
            self._init_document_pillar()

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

        # Register services in the ServiceLocator
        from gematria.services.calculation_database_service import (
            CalculationDatabaseService,
        )
        from gematria.services.custom_cipher_service import CustomCipherService
        from gematria.services.search_service import SearchService
        from shared.repositories.tag_repository import TagRepository
        from shared.services.service_locator import ServiceLocator
        from shared.services.tag_service import TagService

        # Create service instances
        db_service = CalculationDatabaseService()
        custom_cipher_service = CustomCipherService()
        search_service = SearchService(
            db_service
        )  # SearchService depends on CalculationDatabaseService

        # Get the tag repository from the database service
        tag_repository = db_service.tag_repo

        # Create and register the tag service - cast to ensure correct type is passed
        tag_service = TagService(cast(TagRepository, tag_repository))

        # Register services
        ServiceLocator.register(CalculationDatabaseService, db_service)
        ServiceLocator.register(CustomCipherService, custom_cipher_service)
        ServiceLocator.register(SearchService, search_service)
        ServiceLocator.register(TagService, tag_service)

        # Import and create the GematriaTab
        from gematria.ui.gematria_tab import GematriaTab

        # Create and add the tab
        gematria_tab = GematriaTab(self.tab_manager, self.window_manager)
        self.tab_manager.addTab(gematria_tab, "Gematria")
        self.gematria_tab = gematria_tab

        logger.debug("Gematria pillar initialized")

    def _init_geometry_pillar(self) -> None:
        """Initialize the Geometry pillar components."""
        if "geometry" not in self.enabled_pillars:
            logger.debug("Geometry pillar is disabled")
            return

        logger.info("Initializing Geometry pillar")

        # Import the GeometryTab class
        from geometry.ui.geometry_tab import GeometryTab

        # Create the Geometry tab content
        geometry_tab = GeometryTab(self.tab_manager, self.window_manager)

        # Add the Geometry tab with the content
        self.tab_manager.addTab(geometry_tab, "Geometry")

        logger.debug("Geometry pillar initialized")

    def _init_document_pillar(self) -> None:
        """Initialize the Document Manager pillar components."""
        if "document_manager" not in self.enabled_pillars:
            logger.debug("Document Manager pillar is disabled")
            return

        logger.info("Initializing Document Manager pillar")

        # Import the DocumentTab class
        from document_manager.ui.document_tab import DocumentTab

        # Create the Document tab content
        document_tab = DocumentTab(self.tab_manager, self.window_manager)

        # Add the Document Manager tab with the content
        self.tab_manager.addTab(document_tab, "Documents")

        logger.debug("Document Manager pillar initialized")

    def _init_astrology_pillar(self) -> None:
        """Initialize the Astrology pillar components."""
        if "astrology" not in self.enabled_pillars:
            logger.debug("Astrology pillar is disabled")
            return

        logger.info("Initializing Astrology pillar")

        # Import the AstrologyTab class
        from astrology.ui.astrology_tab import AstrologyTab

        # Create the Astrology tab content
        astrology_tab = AstrologyTab(self.tab_manager, self.window_manager)

        # Add the Astrology tab with the content
        self.tab_manager.addTab(astrology_tab, "Astrology")

        logger.debug("Astrology pillar initialized")

    def _init_tq_pillar(self) -> None:
        """Initialize the Text Quest (TQ) pillar."""
        if "tq" not in self.enabled_pillars:
            logger.debug("TQ pillar is disabled")
            return

        logger.info("Initializing TQ pillar")

        try:
            # First initialize the NumberPropertiesService
            # Use relative import to avoid missing imports error
            from shared.services.number_properties_service import (
                NumberPropertiesService,
            )

            NumberPropertiesService()  # Creates the singleton instance

            # Then initialize other services that depend on it
            from tq.services.tq_analysis_service import initialize as init_tq_service

            # Initialize TQAnalysisService using the proper initialize function
            self.tq_analysis_service = init_tq_service(self.window_manager)

            # Import and create the TQ tab
            from tq.ui.tq_tab import TQTab

            tq_tab = TQTab(self.tab_manager, self.window_manager)
            self.tab_manager.addTab(tq_tab, "TQ")

            # Log successful initialization
            logger.debug("TQ pillar initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing TQ pillar: {e}")
            raise

    def _close_application(self) -> None:
        """Close the application."""
        self.close()

    def _show_database_maintenance(self) -> None:
        """Show the Database Maintenance window."""
        from shared.ui.dialogs.database_maintenance_window import (
            DatabaseMaintenanceWindow,
        )

        # Create the content and open the window
        content = DatabaseMaintenanceWindow()
        self.window_manager.open_window(
            "database_maintenance", content
        )

        logger.debug("Opened Database Maintenance window")

    # Window management is now handled through window flags
    # No need for custom window positioning methods

    def closeEvent(self, event: "QCloseEvent") -> None:
        """Handle window close event.

        Save window states before closing.

        Args:
            event: The close event
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
        return int(app.exec())
    except Exception as e:
        logger.exception(f"Failed to start application: {e}")
        return 1
