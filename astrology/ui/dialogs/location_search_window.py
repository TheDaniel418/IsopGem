"""
Purpose: Provides a standalone window for searching and selecting locations.

This file is part of the astrology pillar and serves as a UI component.
It provides a window that contains the location search widget.

Key components:
- LocationSearchWindow: Standalone window for location search

Dependencies:
- PyQt6: For UI components
- astrology.ui.widgets: For the location search widget
"""

from loguru import logger
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout

from astrology.services.location_service import Location
from astrology.ui.widgets.location_search_widget import LocationSearchWidget


class LocationSearchWindow(QDialog):
    """Standalone window for location search."""

    # Signal emitted when a location is selected
    location_selected = pyqtSignal(Location)

    def __init__(self, parent=None):
        """Initialize the location search window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set window properties
        self.setWindowTitle("Location Search")
        self.setMinimumSize(800, 600)

        # Create layout
        layout = QVBoxLayout(self)

        # Create location search widget
        self.location_search_widget = LocationSearchWidget()
        self.location_search_widget.location_selected.connect(
            self._on_location_selected
        )
        layout.addWidget(self.location_search_widget)

        logger.debug("LocationSearchWindow initialized")

    def _on_location_selected(self, location):
        """Handle location selection.

        Args:
            location: Selected location
        """
        # Emit signal
        self.location_selected.emit(location)

        # Accept the dialog to close it and return accept status
        self.accept()

    def set_content(self, widget):
        """Set the content widget of the window.

        This method is required for compatibility with the window manager.

        Args:
            widget: Widget to use as the window content
        """
        # This method is not used since we create our own content
        pass
