"""
Purpose: Service to manage opening the Geometric Transition panel from other pillars.

This file is part of the TQ pillar and serves as a service component.
It provides a singleton service for opening the Geometric Transition panel
from other parts of the application through cross-pillar communication.

Key components:
- GeometricTransitionService: Service for opening the Geometric Transition panel

Dependencies:
- PyQt6: For UI components
- tq.ui.panels.geometric_transition_panel: For the Geometric Transition panel
"""

from typing import List, Optional

from loguru import logger
from PyQt6.QtCore import QObject, pyqtSignal

from shared.ui.window_management import WindowManager


class GeometricTransitionService(QObject):
    """Service for managing the Geometric Transition panel.

    This service provides methods for opening the Geometric Transition panel
    from other parts of the application. It follows the singleton pattern to
    ensure only one instance exists across the application.
    """

    # Signal emitted when a geometric transition window is opened
    geometric_transition_opened = pyqtSignal()

    # Track singleton instance
    _instance = None

    def __init__(self, window_manager: WindowManager):
        """Initialize the service.

        Args:
            window_manager: The application window manager
        """
        super().__init__()
        self.window_manager = window_manager
        logger.debug("GeometricTransitionService initialized with window manager")

    @classmethod
    def get_instance(cls) -> "GeometricTransitionService":
        """Get the singleton instance of the service.

        Returns:
            The singleton instance

        Raises:
            RuntimeError: If the service has not been initialized
        """
        if cls._instance is None:
            # Delegate to the module-level get_instance
            cls._instance = get_instance()
        return cls._instance

    def open_geometric_transition(
        self, values: List[int], labels: List[str], title: str = "Geometric Transitions"
    ) -> None:
        """Open the Geometric Transition panel with the given values.

        This method creates a new Geometric Transition panel and displays it in a
        window. It also sets up the panel with the given values and labels.

        Args:
            values: List of numeric values for the polygon vertices
            labels: List of labels for the polygon vertices
            title: Title for the window
        """
        from tq.ui.panels.geometric_transition_panel import GeometricTransitionPanel

        # Create the panel
        panel = GeometricTransitionPanel()

        # Set up the polygon with the provided values
        panel.set_polygon_values(values, labels)

        # Open in a new window using the window manager
        window = self.window_manager.open_multi_window(
            "tq_geometric_transitions",
            panel,
            title,
            (1200, 700),
        )

        # Ensure the window is shown and raised to the front
        window.show()
        window.raise_()
        window.activateWindow()

        # Emit signal that we opened a geometric transition
        self.geometric_transition_opened.emit()

        logger.debug(f"Opened Geometric Transitions window with {len(values)} vertices")

    def open_window(self):
        """Open the Geometric Transition panel in a new window.

        This creates a new panel without initial values.
        """
        from tq.ui.panels.geometric_transition_panel import GeometricTransitionPanel

        # Create the panel
        panel = GeometricTransitionPanel()

        # Open in a new window using the window manager
        window = self.window_manager.open_multi_window(
            "tq_geometric_transitions",
            panel,
            "Geometric Transitions",
            (1200, 700),
        )

        # Ensure the window is shown and raised to the front
        window.show()
        window.raise_()
        window.activateWindow()

        # Emit signal that we opened a geometric transition
        self.geometric_transition_opened.emit()

        logger.debug("Opened Geometric Transitions window")


# Singleton instance to be created during application initialization
instance: Optional[GeometricTransitionService] = None


def get_instance() -> GeometricTransitionService:
    """Get the Geometric Transition Service instance.

    Returns:
        The singleton GeometricTransitionService instance

    Raises:
        RuntimeError: If the service has not been initialized
    """
    if instance is None:
        raise RuntimeError("GeometricTransitionService has not been initialized")
    return instance


def initialize(window_manager: WindowManager) -> GeometricTransitionService:
    """Initialize the Geometric Transition Service.

    Args:
        window_manager: The application window manager

    Returns:
        The initialized GeometricTransitionService instance
    """
    global instance
    if instance is None:
        instance = GeometricTransitionService(window_manager)
        GeometricTransitionService._instance = instance
    return instance
