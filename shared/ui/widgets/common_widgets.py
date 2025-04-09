"""
Purpose: Provides common reusable widgets for use across the application.

This file is part of the shared UI components and serves as a utility component.
It provides common UI widgets that can be reused throughout the application.

Key components:
- CollapsibleBox: A widget that can be expanded and collapsed to show/hide content
- CollapsibleSection: A variant of CollapsibleBox with additional features
- ColorSquare: A simple colored square widget for color display

Dependencies:
- PyQt6: For UI components
"""

from PyQt6.QtCore import QParallelAnimationGroup, QPropertyAnimation, Qt, pyqtProperty
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class ColorSquare(QLabel):
    """Simple colored square for tag display."""

    def __init__(self, color: str, size: int = 16):
        """Initialize with a color.

        Args:
            color: Hex color code
            size: Square size in pixels
        """
        super().__init__()
        self.setFixedSize(size, size)
        self.setStyleSheet(f"background-color: {color};")


class CollapsibleBox(QWidget):
    """
    A collapsible box that can be expanded and collapsed to show/hide content.
    Useful for optional settings, filters, or other UI elements that don't need
    to be visible all the time.
    """

    def __init__(self, title="", parent=None):
        """
        Initialize the collapsible box.

        Args:
            title: Title displayed on the toggle button
            parent: Parent widget
        """
        super().__init__(parent)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Toggle button
        self.toggle_button = QToolButton()
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.clicked.connect(self.toggle)

        # Content area
        self.content_area = QScrollArea()
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        self.content_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_area.setWidgetResizable(True)

        # Add to layout
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)

        # Animation
        self.toggle_animation = QParallelAnimationGroup(self)
        self.toggle_animation.finished.connect(self.on_animation_finished)

        # Content layout will be set via setContentLayout
        self.content = None

        # Initialize internal variables
        self.collapsed_height = 0
        self.expanded_height = 0
        self.is_animating = False
        self.is_expanded = False

    def toggle(self):
        """Toggle the expanded/collapsed state."""
        if self.is_animating:
            return

        self.is_animating = True

        # Update button appearance
        self.toggle_button.setArrowType(
            Qt.ArrowType.DownArrow if not self.is_expanded else Qt.ArrowType.RightArrow
        )

        # Create animation for expanding/collapsing
        content_height = self.content_area.sizeHint().height()

        # Clear any existing animations
        self.toggle_animation.clear()

        # Create height animation
        height_animation = QPropertyAnimation(self, b"collapsible_height")
        height_animation.setDuration(200)  # Animation duration in milliseconds
        height_animation.setStartValue(0 if not self.is_expanded else content_height)
        height_animation.setEndValue(content_height if not self.is_expanded else 0)

        self.toggle_animation.addAnimation(height_animation)
        self.toggle_animation.start()

    def on_animation_finished(self):
        """Handle end of animation."""
        self.is_animating = False
        self.is_expanded = not self.is_expanded

    def set_content_layout(self, layout):
        """
        Set the layout inside the collapsible box.

        Args:
            layout: The layout to set as content
        """
        # Delete any existing content
        if self.content:
            self.content.deleteLater()

        # Create new content widget with the provided layout
        self.content = QWidget()
        self.content.setLayout(layout)
        self.content_area.setWidget(self.content)

    def setContentLayout(self, layout):
        """
        Alternative name for set_content_layout to support both naming conventions.

        Args:
            layout: The layout to set as content
        """
        self.set_content_layout(layout)

    # Properties and getters/setters for animation
    def get_collapsible_height(self):
        """Get current height of the content area."""
        return self.content_area.maximumHeight()

    def set_collapsible_height(self, height):
        """
        Set the height of the content area. Used by animation.

        Args:
            height: New height value
        """
        self.content_area.setMaximumHeight(height)

    collapsible_height = pyqtProperty(
        int, get_collapsible_height, set_collapsible_height
    )


class CollapsibleSection(QWidget):
    """
    A collapsible section with a title and optional tooltip.
    Similar to CollapsibleBox but with additional features for section organization.
    Used primarily in property panels and settings dialogs.
    """

    def __init__(self, title="", tooltip=None, parent=None):
        """
        Initialize the collapsible section.

        Args:
            title: Title displayed on the toggle button
            tooltip: Optional tooltip text
            parent: Parent widget
        """
        super().__init__(parent)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Toggle button
        self.toggle_button = QToolButton()
        self.toggle_button.setStyleSheet(
            "QToolButton { border: none; text-align: left; }"
        )
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)

        # Set tooltip if provided
        if tooltip:
            self.toggle_button.setToolTip(tooltip)

        self.toggle_button.clicked.connect(self.toggle)

        # Content area
        self.content_area = QScrollArea()
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)
        self.content_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_area.setWidgetResizable(True)

        # Add to layout
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)

        # Animation
        self.toggle_animation = QParallelAnimationGroup(self)
        self.toggle_animation.finished.connect(self.on_animation_finished)

        # Content widget and layout will be set via setContentLayout
        self.content_widget = None
        self.content_layout = None

        # Initialize internal variables
        self.is_animating = False
        self.is_expanded = False

    def toggle(self):
        """Toggle the expanded/collapsed state."""
        if self.is_animating:
            return

        self.is_animating = True

        # Update button appearance
        self.toggle_button.setArrowType(
            Qt.ArrowType.DownArrow if not self.is_expanded else Qt.ArrowType.RightArrow
        )

        # Create animation for expanding/collapsing
        content_height = self.content_area.sizeHint().height()

        # Clear any existing animations
        self.toggle_animation.clear()

        # Create height animation
        height_animation = QPropertyAnimation(self, b"collapsible_height")
        height_animation.setDuration(200)  # Animation duration in milliseconds
        height_animation.setStartValue(0 if not self.is_expanded else content_height)
        height_animation.setEndValue(content_height if not self.is_expanded else 0)

        self.toggle_animation.addAnimation(height_animation)
        self.toggle_animation.start()

    def on_animation_finished(self):
        """Handle end of animation."""
        self.is_animating = False
        self.is_expanded = not self.is_expanded

    def setContentLayout(self, layout):
        """
        Set the layout inside the collapsible section.

        Args:
            layout: The layout to set as content
        """
        # Delete any existing content
        if self.content_widget:
            self.content_widget.deleteLater()

        # Create new content widget with the provided layout
        self.content_widget = QWidget()
        self.content_widget.setLayout(layout)
        self.content_area.setWidget(self.content_widget)

    # Properties and getters/setters for animation
    def get_collapsible_height(self):
        """Get current height of the content area."""
        return self.content_area.maximumHeight()

    def set_collapsible_height(self, height):
        """
        Set the height of the content area. Used by animation.

        Args:
            height: New height value
        """
        self.content_area.setMaximumHeight(height)

    collapsible_height = pyqtProperty(
        int, get_collapsible_height, set_collapsible_height
    )
