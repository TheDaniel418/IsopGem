"""
Purpose: Provides a standalone window for managing gematria calculation tags

This file is part of the gematria pillar and serves as a UI component.
It provides a dedicated window interface for the tag management panel,
allowing users to create, edit, and organize tags for their calculations.

Key components:
- TagManagementWindow: Standalone window for tag management

Dependencies:
- PyQt6: For UI components
- gematria.ui.panels.tag_management_panel: For the tag management panel content
"""

from typing import Optional

from loguru import logger
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from gematria.ui.panels.tag_management_panel import TagManagementPanel


class TagManagementWindow(QMainWindow):
    """Standalone window for managing calculation tags."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the tag management window.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Tag Management")
        self.setMinimumSize(800, 600)

        # Set up central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create tag management panel
        self.tag_panel = TagManagementPanel()
        layout.addWidget(self.tag_panel)

        logger.debug("TagManagementWindow initialized")
