"""
Purpose: Provides a dialog for selecting and managing tags

This file is part of the gematria pillar and serves as a UI component
for selecting tags to associate with calculations. It allows users to
choose from existing tags, create new tags, and edit tag properties.

Key components:
- TagSelectionDialog: Dialog for selecting and managing tags

Dependencies:
- PyQt6: For building the graphical user interface
- shared.models: For tag data model
- shared.services: For tag service access

Related files:
- gematria/ui/dialogs/calculation_details_dialog.py: Uses this dialog for tag selection
- shared/services/tag_service.py: Service for tag operations
"""

import uuid
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QColorDialog,
    QLineEdit,
    QMessageBox,
    QGroupBox,
    QWidget,
    QTextEdit,
)

from loguru import logger
from shared.models.tag import Tag
from shared.services.service_locator import ServiceLocator
from shared.services.tag_service import TagService


class TagSelectionDialog(QDialog):
    """Dialog for selecting and managing tags."""
    
    def __init__(self, selected_tag_ids: List[str] = None, parent=None):
        """
        Initialize the dialog with optional pre-selected tags.

        Args:
            selected_tag_ids: Optional list of tag IDs that should be pre-selected
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Select Tags")

        # Store initial selected tag IDs
        self.selected_tag_ids = selected_tag_ids or []

        # Get tag service
        self.tag_service = ServiceLocator.get(TagService)

        # Initialize UI
        self._init_ui()

        # Load tags from service
        self._load_tags()
        
        # Set window properties
        self.resize(500, 400)
        self.setModal(True)

    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Tag list
        tag_group = QGroupBox("Available Tags")
        tag_layout = QVBoxLayout(tag_group)
        
        self.tag_list = QListWidget()
        self.tag_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        tag_layout.addWidget(self.tag_list)
        
        layout.addWidget(tag_group)
        
        # Tag management buttons
        button_layout = QHBoxLayout()
        
        self.create_tag_button = QPushButton("Create New Tag")
        self.create_tag_button.clicked.connect(self._on_create_tag)
        button_layout.addWidget(self.create_tag_button)
        
        self.edit_tag_button = QPushButton("Edit Selected Tag")
        self.edit_tag_button.clicked.connect(self._on_edit_tag)
        button_layout.addWidget(self.edit_tag_button)
        
        self.delete_tag_button = QPushButton("Delete Selected Tag")
        self.delete_tag_button.clicked.connect(self._on_delete_tag)
        button_layout.addWidget(self.delete_tag_button)
        
        layout.addLayout(button_layout)
        
        # Dialog buttons
        dialog_buttons = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        dialog_buttons.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        dialog_buttons.addWidget(cancel_button)
        
        layout.addLayout(dialog_buttons)
        
    def _load_tags(self):
        """Load tags from service and populate the list widget."""
        # Clear existing items
        self.tag_list.clear()
        
        # Get all tags
        tags = self.tag_service.get_all_tags()
        
        # Add tags to list widget
        for tag in tags:
            item = QListWidgetItem(tag.name)
            item.setData(Qt.ItemDataRole.UserRole, tag)
            
            # Set background color to match tag color
            item.setBackground(QColor(tag.color))
            
            # Set text color for better contrast
            color = QColor(tag.color)
            brightness = 0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()
            text_color = QColor("black") if brightness > 128 else QColor("white")
            item.setForeground(text_color)
            
            # Add tooltip with description if available
            if tag.description:
                item.setToolTip(tag.description)
            
            self.tag_list.addItem(item)
            
            # Select if in the initial selected list
            if tag.id in self.selected_tag_ids:
                item.setSelected(True)
                
    def _get_selected_tag(self) -> Optional[Tag]:
        """
        Get the currently selected tag from the list.
        
        Returns:
            The selected tag or None if no tag is selected
        """
        selected_items = self.tag_list.selectedItems()
        if not selected_items:
            return None
        
        # Use the first selected item
        return selected_items[0].data(Qt.ItemDataRole.UserRole)
        
    def _on_create_tag(self):
        """Handle create tag button click."""
        # Create tag input dialog
        dialog = TagInputDialog(parent=self)
        if dialog.exec():
            # Get tag data
            name = dialog.name_edit.text().strip()
            color = dialog.color
            description = dialog.description_edit.toPlainText().strip()
            
            if not name:
                QMessageBox.warning(self, "Invalid Input", "Tag name cannot be empty.")
                return
            
            # Create tag
            tag = self.tag_service.create_tag(name, color, description)
            if tag:
                # Reload tags and select new tag
                self.selected_tag_ids.append(tag.id)
                self._load_tags()
            else:
                QMessageBox.warning(self, "Error", "Failed to create tag.")
                
    def _on_edit_tag(self):
        """Handle edit tag button click."""
        tag = self._get_selected_tag()
        if not tag:
            QMessageBox.warning(self, "No Selection", "Please select a tag to edit.")
            return

        # Create tag input dialog with existing tag data
        dialog = TagInputDialog(tag, parent=self)
        if dialog.exec():
            # Get updated tag data
            name = dialog.name_edit.text().strip()
            color = dialog.color
            description = dialog.description_edit.toPlainText().strip()
            
            if not name:
                QMessageBox.warning(self, "Invalid Input", "Tag name cannot be empty.")
                return
            
            # Update tag
            tag.name = name
            tag.color = color
            tag.description = description
            
            success = self.tag_service.update_tag(tag)
            if success:
                # Reload tags
                self._load_tags()
            else:
                QMessageBox.warning(self, "Error", "Failed to update tag.")
                
    def _on_delete_tag(self):
        """Handle delete tag button click."""
        tag = self._get_selected_tag()
        if not tag:
            QMessageBox.warning(self, "No Selection", "Please select a tag to delete.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete the tag '{tag.name}'?\n\nThis will remove it from all entities it is associated with.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete tag
            success = self.tag_service.delete_tag(tag.id)
            if success:
                # Remove from selected IDs if present
                if tag.id in self.selected_tag_ids:
                    self.selected_tag_ids.remove(tag.id)
                
                # Reload tags
                self._load_tags()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete tag.")
                
    def accept(self):
        """Handle OK button click."""
        # Update selected tag IDs
        self.selected_tag_ids = []
        for index in range(self.tag_list.count()):
            item = self.tag_list.item(index)
            if item.isSelected():
                tag = item.data(Qt.ItemDataRole.UserRole)
                self.selected_tag_ids.append(tag.id)
        
        super().accept()


class TagInputDialog(QDialog):
    """Dialog for creating or editing a tag."""
    
    def __init__(self, tag: Optional[Tag] = None, parent=None):
        """
        Initialize the dialog with optional existing tag data.

        Args:
            tag: Optional existing tag for editing
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Tag Details")
        
        # Set initial values
        self.tag = tag
        self.color = tag.color if tag else "#3498db"  # Default to a pleasant blue

        # Initialize UI
        self._init_ui()

        # Fill fields if editing
        if tag:
            self.name_edit.setText(tag.name)
            self.description_edit.setText(tag.description)
            self._update_color_preview()
        
        # Set window properties
        self.resize(400, 300)
        self.setModal(True)

    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Name field
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        name_layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter tag name")
        name_layout.addWidget(self.name_edit)
        
        layout.addLayout(name_layout)
        
        # Color field
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        color_layout.addWidget(color_label)
        
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(24, 24)
        self._update_color_preview()
        color_layout.addWidget(self.color_preview)
        
        color_button = QPushButton("Select Color")
        color_button.clicked.connect(self._on_select_color)
        color_layout.addWidget(color_button)
        
        layout.addLayout(color_layout)
        
        # Description field
        layout.addWidget(QLabel("Description:"))
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter tag description (optional)")
        layout.addWidget(self.description_edit)
        
        # Dialog buttons
        button_layout = QHBoxLayout()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _update_color_preview(self):
        """Update the color preview label with the selected color."""
        self.color_preview.setStyleSheet(f"background-color: {self.color}; border: 1px solid gray;")
        
    def _on_select_color(self):
        """Handle select color button click."""
        color = QColorDialog.getColor(QColor(self.color), self, "Select Tag Color")
        if color.isValid():
            self.color = color.name()
            self._update_color_preview()
