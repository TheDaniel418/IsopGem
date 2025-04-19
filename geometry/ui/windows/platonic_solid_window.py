"""
Platonic Solid Calculator Window.

This module provides a window for the Platonic Solid Calculator.
"""


from geometry.ui.panels.platonic_solid_panel import PlatonicSolidPanel
from shared.ui.window_management import AuxiliaryWindow


class PlatonicSolidWindow(AuxiliaryWindow):
    """Window for the Platonic Solid Calculator."""

    def __init__(self, window_id: str, parent=None):
        """Initialize the window.

        Args:
            window_id: Unique identifier for the window
            parent: Parent widget
        """
        # Call the parent constructor with the title and parent
        super().__init__("Platonic Solid Calculator", parent)

        # Store the window_id
        self.window_id = window_id

        # Create the panel
        self.platonic_solid_panel = PlatonicSolidPanel()

        # Set the panel as the content
        self.set_content(self.platonic_solid_panel)

        # Set window properties
        self.resize(900, 600)
