"""
Purpose: Provides a base panel widget for consistent panel styling and behavior.

This file is part of the shared UI components and serves as a base class.
It provides common functionality and consistent styling for panels throughout the application.

Key components:
- Panel: Base class for panel widgets

Dependencies:
- PyQt6: For UI components
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget
from typing import Optional


class Panel(QWidget):
    """Base panel widget with common functionality.

    All panels in the application should inherit from this class
    to ensure consistent styling and behavior.
    """

    def __init__(self, title: str, parent: Optional[QWidget] = None):
        """Initialize the panel.

        Args:
            title: Panel title
            parent: Parent widget
        """
        super().__init__(parent)

        # Store properties
        self.title = title

        # Set up the panel layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Add title frame if title provided
        if title:
            self._setup_title_frame()

    def _setup_title_frame(self):
        """Set up the title frame at the top of the panel."""
        # Create title frame
        title_frame = QFrame()
        title_frame.setObjectName("panelTitleFrame")
        title_frame.setFrameShape(QFrame.Shape.StyledPanel)
        title_frame.setAutoFillBackground(True)

        # Create title label
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel(self.title)
        title_label.setObjectName("panelTitleLabel")
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # Add title label to frame
        title_layout.addWidget(title_label)

        # Add title frame to panel
        self.main_layout.addWidget(title_frame)

        # Content layout will be added after title
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

    def set_title(self, title: str) -> None:
        """Set the panel title.

        Args:
            title: New panel title
        """
        self.title = title
        title_label = self.findChild(QLabel, "panelTitleLabel")
        if title_label and hasattr(title_label, "setText"):
            title_label.setText(title)
