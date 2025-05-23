"""
Purpose: Service for managing TQ Grid display numbers

This file is part of the tq pillar and serves as a service component.
It stores and provides access to the four decimal numbers currently
displayed in the TQ Grid. This service does not perform calculations,
but rather serves as a central store for the already-calculated values.

Key components:
- TQGridService: Singleton service for managing TQ Grid display numbers
- TQGrid: Data class representing the four displayed numbers
"""

import logging
from dataclasses import dataclass

from shared.services.service_locator import ServiceLocator

logger = logging.getLogger(__name__)


@dataclass
class TQGrid:
    """Data class representing the four numbers displayed in the TQ Grid."""

    base_number: int
    conrune: int
    reversal: int
    reversal_conrune: int


class TQGridService:
    """
    Service for managing TQ Grid display numbers.

    This service maintains the current state of the four decimal numbers
    displayed in the TQ Grid. It does not perform calculations, but rather
    serves as a central store for numbers that have already been calculated
    and displayed.
    """

    _instance = None

    # Signal for grid updates
    grid_updated = None

    def __init__(self):
        """Initialize the service with empty grid."""
        if TQGridService._instance is not None:
            raise RuntimeError("Use get_instance() instead")
        self._current_grid = TQGrid(0, 0, 0, 0)

        # Initialize the grid_updated signal
        # We're not using PyQt signals here to avoid circular imports
        # Instead, we'll use a simple callback mechanism
        self.grid_updated = []  # List of callback functions

    @classmethod
    def get_instance(cls) -> "TQGridService":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def update_grid_display(
        self, base: int, conrune: int, reversal: int, reversal_conrune: int
    ) -> TQGrid:
        """
        Update the stored grid numbers with the values currently displayed.

        Args:
            base: The base number displayed
            conrune: The conrune number displayed
            reversal: The reversal number displayed
            reversal_conrune: The reversal conrune number displayed

        Returns:
            TQGrid object with the current display values
        """
        self._current_grid = TQGrid(
            base_number=base,
            conrune=conrune,
            reversal=reversal,
            reversal_conrune=reversal_conrune,
        )
        logger.debug(
            f"Updated grid display - Base: {base}, Conrune: {conrune}, "
            f"Reversal: {reversal}, Reversal Conrune: {reversal_conrune}"
        )

        # Notify callbacks about the update
        self._notify_callbacks()

        return self._current_grid

    def get_current_grid(self) -> TQGrid:
        """Get the current grid display values."""
        return self._current_grid

    def register_callback(self, callback):
        """Register a callback function to be called when the grid is updated.

        Args:
            callback: A function that takes no arguments
        """
        if callback not in self.grid_updated:
            self.grid_updated.append(callback)

    def unregister_callback(self, callback):
        """Unregister a callback function.

        Args:
            callback: The function to unregister
        """
        if callback in self.grid_updated:
            self.grid_updated.remove(callback)

    def _notify_callbacks(self):
        """Notify all registered callbacks that the grid has been updated."""
        for callback in self.grid_updated:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in grid update callback: {e}")


# Register service with locator
ServiceLocator.register(TQGridService, TQGridService.get_instance())
