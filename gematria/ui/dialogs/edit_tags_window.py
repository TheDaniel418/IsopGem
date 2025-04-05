"""
Purpose: Provides a window for managing tags associated with calculations

This file is part of the gematria pillar and serves as a UI component.
It is responsible for allowing users to view and modify the tags associated
with a specific calculation, providing a dedicated interface for tag management.

Key components:
- EditTagsWindow: Window for viewing and editing calculation tags

Dependencies:
- PyQt6: For the graphical user interface components
- gematria.models.calculation_result: For the calculation data structure
- gematria.services.calculation_database_service: For accessing calculation and tag data
- gematria.ui.dialogs.tag_selection_dialog: For selecting tags

Related files:
- gematria/ui/panels/calculation_history_panel.py: Uses this window for tag management
- gematria/ui/dialogs/tag_selection_dialog.py: Used by this window for tag selection
- gematria/models/calculation_result.py: Defines the calculation data model
"""

from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QListWidget, QListWidgetItem, QCheckBox, QLineEdit,
    QMessageBox, QDialog
)
from PyQt6.QtCore import Qt

from loguru import logger

from gematria.models.calculation_result import CalculationResult
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.ui.dialogs.tag_selection_dialog import TagSelectionDialog


class EditTagsWindow(QMainWindow):
    """Window for editing tags for a calculation."""
    
    def __init__(self, calculation_id: str, parent=None):
        """Initialize the window.
        
        Args:
            calculation_id: ID of the calculation to edit tags for
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Tags")
        self.resize(500, 600)
        
        # Store the calculation ID
        self.calculation_id = calculation_id
        
        # Initialize the database service
        self.db_service = CalculationDatabaseService()
        
        # Initialize UI
        self._init_ui()
        
        # Load the calculation
        self._load_calculation()
        
    def _init_ui(self):
        """Initialize the UI components."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Edit Tags")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Calculation info
        self.calculation_info = QLabel()
        layout.addWidget(self.calculation_info)
        
        # Current tags
        tags_header = QLabel("Current Tags:")
        tags_header.setStyleSheet("font-weight: bold;")
        layout.addWidget(tags_header)
        
        self.tag_list = QListWidget()
        self.tag_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                min-height: 100px;
            }
            QListWidget::item {
                padding: 4px;
            }
        """)
        layout.addWidget(self.tag_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Edit tags button
        self.edit_tags_btn = QPushButton("Select Tags")
        self.edit_tags_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.edit_tags_btn.clicked.connect(self._edit_tags)
        button_layout.addWidget(self.edit_tags_btn)
        
        # Add button layout
        layout.addLayout(button_layout)
        
    def _load_calculation(self):
        """Load the calculation from the database."""
        # Get calculation
        calculation = self.db_service.get_calculation(self.calculation_id)
        if not calculation:
            QMessageBox.warning(
                self,
                "Error",
                "Could not find calculation"
            )
            self.close()
            return
            
        # Determine method name safely
        method_name = "Unknown"
        if hasattr(calculation, 'custom_method_name') and calculation.custom_method_name:
            method_name = calculation.custom_method_name
        elif hasattr(calculation.calculation_type, 'name'):
            method_name = calculation.calculation_type.name.replace("_", " ").title()
        elif isinstance(calculation.calculation_type, str):
            method_name = calculation.calculation_type.replace("_", " ").title()
            
        # Update calculation info
        self.calculation_info.setText(
            f"<b>Text:</b> {calculation.input_text}<br>"
            f"<b>Value:</b> {calculation.result_value}<br>"
            f"<b>Method:</b> {method_name}<br>"
            f"<b>Created:</b> {calculation.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # Load tags
        self._load_tags(calculation)
        
    def _load_tags(self, calculation: CalculationResult):
        """Load tags for the calculation.
        
        Args:
            calculation: Calculation to load tags for
        """
        # Clear the list
        self.tag_list.clear()
        
        # Get tags for the calculation
        if not calculation.tags:
            self.tag_list.addItem("No tags assigned to this calculation")
            return
            
        for tag_id in calculation.tags:
            tag = self.db_service.get_tag(tag_id)
            if tag:
                item = QListWidgetItem(f"{tag.name}")
                item.setData(Qt.ItemDataRole.UserRole, tag.id)
                
                # Set background color based on tag color with reduced opacity
                color = tag.color
                item.setBackground(Qt.GlobalColor.transparent)
                item.setForeground(Qt.GlobalColor.black)
                item.setToolTip(tag.description or "")
                
                self.tag_list.addItem(item)
                
    def _edit_tags(self):
        """Edit tags for the calculation."""
        # Show tag selection dialog
        dialog = TagSelectionDialog(self.calculation_id, parent=self)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reload the calculation
            self._load_calculation() 