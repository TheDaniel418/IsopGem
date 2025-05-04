"""
Purpose: Provides a service for sending polygonal numbers to the visualization panel

This file is part of the geometry pillar and serves as a service component.
It facilitates cross-pillar communication by allowing other components to send
polygonal or centered polygonal numbers to the visualization panel.

Key components:
- PolygonalVisualizationService: Singleton service for managing polygonal number visualization requests

Dependencies:
- shared.services.service_locator: For registering the service in the application

Related files:
- geometry/ui/panels/polygonal_numbers_panel.py: Panel that visualizes the polygonal numbers
- tq/ui/panels/number_properties_panel.py: Panel that identifies polygonal numbers
"""

import logging
from typing import Callable, Optional

from PyQt6.QtWidgets import QMainWindow

from shared.services.service_locator import ServiceLocator

logger = logging.getLogger(__name__)


class PolygonalVisualizationService:
    """
    Service for sending polygonal numbers to the visualization panel.
    
    This service acts as a communication channel between components that identify
    polygonal numbers (like the NumberPropertiesPanel) and components that visualize
    them (like the PolygonalNumbersPanel).
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> "PolygonalVisualizationService":
        """Get the singleton instance of the service.

        Returns:
            The singleton instance
        """
        if cls._instance is None:
            cls._instance = PolygonalVisualizationService()
        return cls._instance

    def __init__(self) -> None:
        """Initialize the service.

        Raises:
            RuntimeError: If an attempt is made to create a second instance
        """
        if PolygonalVisualizationService._instance is not None:
            raise RuntimeError("Use get_instance() to get the singleton instance")

        PolygonalVisualizationService._instance = self
        
        # Initialize properties
        self._is_centered = False
        self._sides = 3  # Default to triangular
        self._index = 1  # Default to first number
        self._has_pending_visualization = False
        
        # Callbacks for notification
        self._callbacks = []
        
        # Function to open the panel (will be set by the main window)
        self._open_panel_func: Optional[Callable] = None
        
        logger.debug("PolygonalVisualizationService initialized")

    def set_polygonal_number(self, sides: int, index: int, is_centered: bool = False) -> None:
        """Set a polygonal number for visualization.

        Args:
            sides: Number of sides for the polygonal number (3=triangular, 4=square, etc.)
            index: Index of the polygonal number in the sequence
            is_centered: Whether this is a centered polygonal number
        """
        self._sides = max(3, sides)  # Minimum 3 sides
        self._index = max(1, index)  # Minimum index of 1
        self._is_centered = is_centered
        self._has_pending_visualization = True
        
        logger.debug(
            f"Set polygonal number: sides={sides}, index={index}, centered={is_centered}"
        )
        
        # Try to open the panel
        panel_opened = self.open_panel()
        
        # Notify all registered callbacks
        self._notify_callbacks()
        
        # If we couldn't open the panel, log a warning
        if not panel_opened:
            logger.warning("Could not open polygonal numbers panel - visualization will be pending")

    def get_polygonal_number(self) -> tuple[int, int, bool]:
        """Get the current polygonal number settings.

        Returns:
            Tuple of (sides, index, is_centered)
        """
        return (self._sides, self._index, self._is_centered)

    def has_pending_visualization(self) -> bool:
        """Check if there's a pending visualization request.

        Returns:
            True if there's a pending request, False otherwise
        """
        return self._has_pending_visualization

    def clear_pending_visualization(self) -> None:
        """Clear the pending visualization flag after it's been processed."""
        self._has_pending_visualization = False

    def register_callback(self, callback) -> None:
        """Register a callback function to be called when a new number is set.

        Args:
            callback: A function that takes no arguments
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback) -> None:
        """Unregister a callback function.

        Args:
            callback: The function to unregister
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks that a new number has been set."""
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in polygonal visualization callback: {e}")
                
    def register_panel_opener(self, opener_func: Callable) -> None:
        """Register a function that can open the polygonal numbers panel.
        
        Args:
            opener_func: Function that opens the polygonal numbers panel
        """
        self._open_panel_func = opener_func
        logger.debug("Panel opener function registered")
        
    def open_panel(self) -> bool:
        """Open the polygonal numbers panel if a panel opener is registered.
        
        Returns:
            True if the panel was opened, False otherwise
        """
        if self._open_panel_func is not None:
            try:
                self._open_panel_func()
                logger.debug("Opened polygonal numbers panel")
                return True
            except Exception as e:
                logger.error(f"Error opening polygonal numbers panel: {e}")
                return False
        else:
            logger.warning("No panel opener function registered")
            return False


# Register service with locator
ServiceLocator.register(PolygonalVisualizationService, PolygonalVisualizationService.get_instance())