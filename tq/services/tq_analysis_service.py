"""
Purpose: Provides services for TQ (Ternary Qabala) analysis operations

This file is part of the tq pillar and serves as a service component.
It is responsible for providing analysis functions for ternary numbers,
including quadset analysis and other TQ operations.

Key components:
- TQAnalysisService: Main service class for TQ analysis operations
- open_quadset_analysis: Function to open the TQ Grid for a specific number

Dependencies:
- PyQt6: For UI integration
- tq.utils.ternary_converter: For number system conversions
- tq.utils.ternary_transition: For ternary transformations
- tq.ui.panels.tq_grid_panel: For the TQ Grid visualization widget

Related files:
- tq/ui/tq_tab.py: Main tab that can launch these analysis tools
- tq/ui/panels/tq_grid_panel.py: The TQ Grid panel implementation
"""

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal

from shared.ui.window_management import WindowManager
from tq.ui.panels.tq_grid_panel import TQGridPanel


class TQAnalysisService(QObject):
    """Service for TQ (Ternary Qabala) analysis operations."""

    # Signal emitted when a quadset analysis is opened
    quadset_analysis_opened = pyqtSignal(int)

    # Track singleton instance
    _instance = None

    def __init__(self, window_manager: WindowManager):
        """Initialize the TQ Analysis Service.

        Args:
            window_manager: The application window manager for creating windows
        """
        super().__init__()
        self.window_manager = window_manager
        self._active_quadset_panels = {}  # Track active panels by number

    @classmethod
    def get_instance(cls) -> "TQAnalysisService":
        """Get the TQ Analysis Service singleton instance.

        Returns:
            The singleton TQAnalysisService instance

        Raises:
            RuntimeError: If the service has not been initialized
        """
        if cls._instance is None:
            # Delegate to the module-level get_instance
            cls._instance = get_instance()
        return cls._instance

    def open_quadset_analysis(self, number: int) -> TQGridPanel:
        """Open the TQ Grid (Quadset Analysis) for a specific number.

        This will create a new window with the TQ Grid panel pre-populated
        with the specified number, or focus an existing window if one
        already exists for this number.

        Args:
            number: The decimal number to analyze

        Returns:
            The TQ Grid panel instance
        """
        # Check if a panel for this number already exists
        window_id = f"tq_grid_{number}"

        # If window already exists, bring it to front and return
        existing_window = self.window_manager.get_auxiliary_window(window_id)
        if existing_window and existing_window.isVisible():
            existing_window.show()
            existing_window.raise_()

            # Return the existing panel
            return self._active_quadset_panels.get(number)

        # Create a new panel
        grid_panel = TQGridPanel()

        # Set the number in the panel
        grid_panel.number_input.setText(str(number))
        grid_panel._process_number()  # Process the number immediately

        # Open the window
        window = self.window_manager.open_window(
            window_id, grid_panel, f"TQ Grid Explorer - {number}", (1000, 800)
        )

        # Store reference to the panel
        self._active_quadset_panels[number] = grid_panel

        # Connect to window close event to clean up reference
        window.destroyed.connect(lambda: self._cleanup_panel(number))

        # Emit signal that we opened a quadset analysis
        self.quadset_analysis_opened.emit(number)

        return grid_panel

    def _cleanup_panel(self, number: int) -> None:
        """Clean up panel reference when its window is closed.

        Args:
            number: The number associated with the panel
        """
        if number in self._active_quadset_panels:
            del self._active_quadset_panels[number]


# Singleton instance to be created during application initialization
instance: Optional[TQAnalysisService] = None


def get_instance() -> TQAnalysisService:
    """Get the TQ Analysis Service instance.

    Returns:
        The singleton TQAnalysisService instance

    Raises:
        RuntimeError: If the service has not been initialized
    """
    if instance is None:
        raise RuntimeError("TQAnalysisService has not been initialized")
    return instance


def initialize(window_manager: WindowManager) -> TQAnalysisService:
    """Initialize the TQ Analysis Service.

    Args:
        window_manager: The application window manager

    Returns:
        The initialized TQAnalysisService instance
    """
    global instance
    if instance is None:
        instance = TQAnalysisService(window_manager)
        TQAnalysisService._instance = instance
    return instance
