"""
Purpose: Provides a dialog for creating and editing tags for gematria calculations

This file is part of the gematria pillar and serves as a UI component.
It is responsible for providing a user interface for creating new tags or
editing existing ones, with options to set the tag name, color, and description.

Key components:
- CreateTagDialog: Dialog for creating or editing tags with customizable attributes

Dependencies:
- PyQt6: For building the graphical user interface
- gematria.models.tag: For the Tag data model
- gematria.services.calculation_database_service: For storing created tags

Related files:
- gematria/ui/panels/calculation_history_panel.py: Uses this dialog to create tags
- gematria/ui/dialogs/save_calculation_dialog.py: Uses this dialog for tag creation
- gematria/models/tag.py: Provides the data model for tags
"""

from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QColorDialog, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from loguru import logger

from gematria.models.tag import Tag
from gematria.services.calculation_database_service import CalculationDatabaseService


class CreateTagDialog(QDialog):
    """Dialog for creating a new tag."""
    
    tag_created = pyqtSignal(Tag)
    
    def __init__(self, parent=None):
        """Initialize the create tag dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Create Tag")
        self.setMinimumWidth(350)
        
        self.db_service = CalculationDatabaseService()
        
        # Default color
        self._selected_color = "#3498db"  # Nice blue color
        
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI elements."""
        layout = QVBoxLayout(self)
        
        # Tag name
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter tag name")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Tag color
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet(f"background-color: {self._selected_color}; border: 1px solid #ccc;")
        
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self._choose_color)
        
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_preview)
        color_layout.addWidget(self.color_button)
        layout.addLayout(color_layout)
        
        # Tag description
        desc_label = QLabel("Description (optional):")
        layout.addWidget(desc_label)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Enter tag description")
        self.desc_edit.setMaximumHeight(100)
        layout.addWidget(self.desc_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        self.create_button = QPushButton("Create Tag")
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self._create_tag)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.create_button)
        layout.addLayout(button_layout)
        
    def _choose_color(self):
        """Open the color dialog to choose a tag color."""
        color = QColorDialog.getColor(QColor(self._selected_color), self, "Choose Tag Color")
        
        if color.isValid():
            self._selected_color = color.name()
            self.color_preview.setStyleSheet(f"background-color: {self._selected_color}; border: 1px solid #ccc;")
            
    def _create_tag(self):
        """Create a new tag with the provided information."""
        # Validate input
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Tag name cannot be empty.")
            return
            
        # Get description
        description = self.desc_edit.toPlainText().strip()
        if not description:
            description = ""
            
        # Create the tag
        try:
            tag = self.db_service.create_tag(
                name=name,
                color=self._selected_color,
                description=description
            )
            
            if tag:
                logger.debug(f"Created tag: {tag.name}")
                self.tag_created.emit(tag)
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to create tag. Please try again.")
                
        except Exception as e:
            logger.error(f"Error creating tag: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while creating the tag: {e}")
            
    def set_edit_mode(self, tag: Tag):
        """Set the dialog to edit mode to update an existing tag.
        
        Args:
            tag: The tag to edit
        """
        self.setWindowTitle("Edit Tag")
        
        # Pre-fill fields
        self.name_edit.setText(tag.name)
        
        self._selected_color = tag.color
        self.color_preview.setStyleSheet(f"background-color: {self._selected_color}; border: 1px solid #ccc;")
        
        if tag.description:
            self.desc_edit.setText(tag.description)
            
        # Change button text
        self.create_button.setText("Update Tag") 