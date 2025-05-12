"""
Purpose: Provides a standalone window for 2D Geometric Transitions functionality.

This file is part of the tq pillar and serves as a UI component.
It provides a dedicated window interface for the Geometric Transitions panel,
allowing users to visualize and calculate transitions between polygon vertices.

Key components:
- GeometricTransitionWindow: Standalone window for geometric transition calculations

Dependencies:
- PyQt6: For UI components
- shared.ui.window_management: For window management functionality
- tq.ui.panels.geometric_transition_panel: For the geometric transition panel content
"""

from typing import Optional

from loguru import logger
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget

from shared.ui.window_management import AuxiliaryWindow
from tq.ui.panels.geometric_transition_panel import GeometricTransitionPanel


class GeometricTransitionWindow(AuxiliaryWindow):
    """Standalone window for geometric transition calculations."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the geometric transition window.

        Args:
            parent: Parent widget
        """
        # Initialize with proper title and parent
        super().__init__("2D Geometric Transitions", parent)

        # Set minimum size
        self.setMinimumSize(1200, 700)

        # Create the geometric transition panel
        self.geometric_transition_panel = GeometricTransitionPanel()

        # Set the panel as the window's content
        self.set_content(self.geometric_transition_panel)

        logger.debug("GeometricTransitionWindow initialized")

    def ensure_on_top(self) -> None:
        """Ensure this window appears on top of other windows."""
        # Apply focus operations to ensure we're visible and on top
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
        self.show()
        self.raise_()
        self.activateWindow()

        # Use delayed focus to ensure window ordering is applied after other events
        QTimer.singleShot(100, self._delayed_focus)

        logger.debug("Ensuring GeometricTransitionWindow stays on top")

    def _delayed_focus(self) -> None:
        """Apply delayed focus operations to ensure window stays on top."""
        if self.isVisible():
            self.raise_()
            self.activateWindow()
            logger.debug("Applied delayed focus to GeometricTransitionWindow")
