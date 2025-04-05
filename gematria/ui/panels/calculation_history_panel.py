"""
Purpose: Provides a user interface for viewing and managing calculation history

This file is part of the gematria pillar and serves as a UI component.
It is responsible for displaying saved calculation results, allowing users to
view, filter, sort, and manage their calculation history with features for
tagging, favoriting, and searching.

Key components:
- CalculationHistoryPanel: Main UI panel for viewing calculation history
- CalculationListItem: UI component for displaying individual calculation items
- CalculationDetailWidget: UI component for displaying detailed information about a calculation
- TagWidget/TagListWidget: UI components for displaying and managing tags

Dependencies:
- PyQt6: For building the graphical user interface
- gematria.models: For working with calculation results and tags
- gematria.services: For retrieving calculation data

Related files:
- gematria/models/calculation_result.py: Provides the data model for calculations
- gematria/models/tag.py: Provides the data model for tags
- gematria/services/calculation_database_service.py: Provides data access
- gematria/ui/dialogs/create_tag_dialog.py: Dialog for creating new tags
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QSplitter, QComboBox, 
    QLineEdit, QGroupBox, QScrollArea, QInputDialog,
    QCheckBox, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QIcon, QAction, QFont, QPixmap

from loguru import logger
from gematria.models.calculation_result import CalculationResult
from gematria.models.tag import Tag
from gematria.models.calculation_type import CalculationType, get_calculation_type_name
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.ui.dialogs.create_tag_dialog import CreateTagDialog

from typing import Dict, List, Optional, Set
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QComboBox,
    QLineEdit, QSplitter, QFrame, QCheckBox, QStackedWidget,
    QTextEdit, QGridLayout, QScrollArea, QToolButton, QDialog,
    QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap

from loguru import logger

from gematria.models.calculation_result import CalculationResult
from gematria.models.tag import Tag
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.ui.dialogs.tag_selection_dialog import TagSelectionDialog


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


class TagWidget(QWidget):
    """Widget for displaying a tag."""
    
    def __init__(self, tag: Tag, parent=None):
        """Initialize with a tag.
        
        Args:
            tag: Tag to display
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Store the tag
        self.tag = tag
        
        # Initialize UI
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)
        
        # Color square
        color_square = ColorSquare(tag.color, size=12)
        layout.addWidget(color_square)
        
        # Tag name
        name_label = QLabel(tag.name)
        name_label.setStyleSheet("font-size: 10px;")
        layout.addWidget(name_label)
        
        # Style the widget
        self.setStyleSheet("""
            background-color: #f0f0f0;
            border-radius: 2px;
        """)


class TagListWidget(QWidget):
    """Widget for displaying a list of tags horizontally."""
    
    def __init__(self, tags: List[Tag], parent=None):
        """Initialize with tags.
        
        Args:
            tags: Tags to display
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize UI
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Add tags
        for tag in tags:
            tag_widget = TagWidget(tag)
            layout.addWidget(tag_widget)
            
        # Add stretch to push tags to the left
        layout.addStretch(1)


class CalculationListItem(QWidget):
    """List item widget for a calculation in the history panel."""
    
    def __init__(self, calculation: CalculationResult, tags: List[Tag], parent=None):
        """Initialize the calculation list item.
        
        Args:
            calculation: The calculation to display
            tags: Tags associated with the calculation
            parent: Parent widget
        """
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Top row: value and date
        top_row = QHBoxLayout()
        
        # Value
        value = QLabel(f"<b>{calculation.result_value}</b>")
        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        top_row.addWidget(value)
        
        top_row.addStretch(1)
        
        # Favorite indicator
        if calculation.favorite:
            favorite = QLabel("★")
            favorite.setStyleSheet("color: gold; font-size: 16px;")
            top_row.addWidget(favorite)
        
        # Date
        date = QLabel(calculation.timestamp.strftime('%Y-%m-%d %H:%M'))
        date.setStyleSheet("color: #666;")
        top_row.addWidget(date)
        
        layout.addLayout(top_row)
        
        # Middle row: input text
        text = QLabel(calculation.input_text)
        text.setWordWrap(True)
        text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(text)
        
        # Bottom row: method
        bottom_row = QHBoxLayout()
        
        # Determine method name
        method_name = "Unknown"
        if hasattr(calculation, 'custom_method_name') and calculation.custom_method_name:
            method_name = calculation.custom_method_name
        elif hasattr(calculation.calculation_type, 'name'):
            method_name = calculation.calculation_type.name.replace("_", " ").title()
        elif isinstance(calculation.calculation_type, str):
            method_name = calculation.calculation_type.replace("_", " ").title()
        
        method = QLabel(f"<b>Method:</b> {method_name}")
        bottom_row.addWidget(method)
        
        layout.addLayout(bottom_row)
        
        # Add tags if present
        if tags:
            tag_layout = QHBoxLayout()
            tag_layout.setSpacing(5)
            
            for tag in tags[:3]:  # Limit to 3 tags to save space
                tag_widget = TagWidget(tag)
                tag_layout.addWidget(tag_widget)
                
            tag_layout.addStretch(1)
            layout.addLayout(tag_layout)
            
        # Set a border and styling
        self.setStyleSheet("""
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
        """)


class CalculationDetailWidget(QWidget):
    """Widget for displaying calculation details."""
    
    edit_tags_clicked = pyqtSignal(str)  # calculation_id
    edit_notes_clicked = pyqtSignal(str)  # calculation_id
    toggle_favorite_clicked = pyqtSignal(str)  # calculation_id
    
    def __init__(self, parent=None):
        """Initialize the widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize the database service
        self.db_service = CalculationDatabaseService()
        
        # Current calculation
        self.calculation = None
        
        # Initialize UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header - "Calculation Details"
        header = QLabel("Calculation Details")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Placeholder message when no calculation is selected
        self.placeholder = QLabel("Select a calculation to view details")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("color: #666; font-style: italic;")
        
        # Content widget (shown when a calculation is selected)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(15)
        
        # Input text
        self.text_section = QFrame()
        self.text_section.setFrameShape(QFrame.Shape.StyledPanel)
        self.text_section.setStyleSheet("background-color: #f8f9fa; border-radius: 4px;")
        
        text_layout = QVBoxLayout(self.text_section)
        
        text_header = QLabel("Input Text:")
        text_header.setStyleSheet("font-weight: bold;")
        text_layout.addWidget(text_header)
        
        self.text_value = QLabel()
        self.text_value.setWordWrap(True)
        self.text_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        text_layout.addWidget(self.text_value)
        
        self.content_layout.addWidget(self.text_section)
        
        # Value and method
        info_grid = QGridLayout()
        info_grid.setColumnStretch(1, 1)
        
        # Value
        info_grid.addWidget(QLabel("Value:"), 0, 0)
        self.value_label = QLabel()
        self.value_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.value_label.setStyleSheet("font-weight: bold;")
        info_grid.addWidget(self.value_label, 0, 1)
        
        # Method
        info_grid.addWidget(QLabel("Method:"), 1, 0)
        self.method_label = QLabel()
        info_grid.addWidget(self.method_label, 1, 1)
        
        # Created date
        info_grid.addWidget(QLabel("Created:"), 2, 0)
        self.created_label = QLabel()
        info_grid.addWidget(self.created_label, 2, 1)
        
        self.content_layout.addLayout(info_grid)
        
        # Tags section
        tags_layout = QHBoxLayout()
        
        tags_label = QLabel("Tags:")
        tags_label.setFixedWidth(80)
        tags_layout.addWidget(tags_label)
        
        self.tags_widget = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_widget)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(5)
        tags_layout.addWidget(self.tags_widget, 1)
        
        self.edit_tags_btn = QPushButton("Edit")
        self.edit_tags_btn.clicked.connect(self._on_edit_tags)
        tags_layout.addWidget(self.edit_tags_btn)
        
        self.content_layout.addLayout(tags_layout)
        
        # Notes section
        notes_layout = QVBoxLayout()
        
        notes_header = QHBoxLayout()
        notes_label = QLabel("Notes:")
        notes_header.addWidget(notes_label)
        
        notes_header.addStretch(1)
        
        self.edit_notes_btn = QPushButton("Edit")
        self.edit_notes_btn.clicked.connect(self._on_edit_notes)
        notes_header.addWidget(self.edit_notes_btn)
        
        notes_layout.addLayout(notes_header)
        
        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.notes_text.setFixedHeight(120)
        notes_layout.addWidget(self.notes_text)
        
        self.content_layout.addLayout(notes_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        self.favorite_btn = QPushButton("Mark as Favorite")
        self.favorite_btn.clicked.connect(self._on_toggle_favorite)
        buttons_layout.addWidget(self.favorite_btn)
        
        buttons_layout.addStretch(1)
        
        self.content_layout.addLayout(buttons_layout)
        
        # Stacked widget to switch between placeholder and content
        self.stack = QStackedWidget()
        self.stack.addWidget(self.placeholder)
        self.stack.addWidget(self.content)
        
        layout.addWidget(self.stack)
        
    def _get_method_name(self, calculation: CalculationResult) -> str:
        """Get a readable method name for the calculation.
        
        Args:
            calculation: The calculation result containing the calculation type.
            
        Returns:
            A formatted string representation of the calculation method name.
        """
        # Default fallback value
        method_name = "Unknown"
        
        # Use defensive programming to avoid crashes and unreachable code
        try:
            # Custom method name takes precedence if it exists
            if hasattr(calculation, 'custom_method_name') and calculation.custom_method_name:
                return calculation.custom_method_name
            
            # Next, check calculation_type
            if hasattr(calculation, 'calculation_type'):
                calc_type = calculation.calculation_type
                
                # Handle enum type with name attribute
                if hasattr(calc_type, 'name'):
                    return calc_type.name.replace("_", " ").title()
                
                # Handle string type
                if isinstance(calc_type, str):
                    return calc_type.replace("_", " ").title()
        except AttributeError:
            # Handle any attribute access errors
            pass
        except Exception:
            # Catch any other unexpected errors
            logger.exception("Error determining method name")
            
        # Return the fallback value
        return method_name

    def set_calculation(self, calculation: Optional[CalculationResult], tags: Optional[List[Tag]] = None):
        """Set the calculation to display.
        
        Args:
            calculation: Calculation to display or None to show placeholder
            tags: Tags for the calculation
        """
        self.calculation = calculation
        
        if not calculation:
            self.stack.setCurrentIndex(0)  # Show placeholder
            return
            
        # Show content
        self.stack.setCurrentIndex(1)
        
        # Update fields
        self.text_value.setText(calculation.input_text)
        self.value_label.setText(str(calculation.result_value))
        
        # Use the method name helper
        self.method_label.setText(self._get_method_name(calculation))
        self.created_label.setText(calculation.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        self.notes_text.setText(calculation.notes or "")
        
        # Update favorite button
        if calculation.favorite:
            self.favorite_btn.setText("Remove from Favorites")
            self.favorite_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """)
        else:
            self.favorite_btn.setText("Mark as Favorite")
            self.favorite_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2ecc71;
                    color: white;
                    font-weight: bold;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #27ae60;
                }
            """)
            
        # Clear tags
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Add tags
        if tags:
            for tag in tags:
                tag_widget = TagWidget(tag)
                self.tags_layout.addWidget(tag_widget)
                
        self.tags_layout.addStretch(1)
        
    def _on_edit_tags(self, calc_id: str):
        """Handle edit tags button click.
        
        Args:
            calc_id: ID of the calculation to edit
        """
        # Get calculation
        calculation = self.db_service.get_calculation(calc_id)
        if not calculation:
            return
            
        # Show edit tags window
        from gematria.ui.dialogs.edit_tags_window import EditTagsWindow
        window = EditTagsWindow(calc_id, parent=self)
        window.show()
        
        # Connect to window close event to refresh the UI
        window.destroyed.connect(lambda: self._refresh_calculation_display(calc_id))
        
    def _on_edit_notes(self, calc_id: str):
        """Handle edit notes button click.
        
        Args:
            calc_id: ID of the calculation to edit
        """
        # Get the current calculation
        calculation = self.db_service.get_calculation(calc_id)
        if not calculation:
            logger.warning(f"Calculation not found: {calc_id}")
            return
            
        # Show an input dialog to get the new notes
        current_notes = calculation.notes or ""
        new_notes, ok = QInputDialog.getMultiLineText(
            self,
            "Edit Notes",
            "Enter notes for this calculation:",
            current_notes
        )
        
        if ok:
            # Update the notes
            if self.db_service.update_calculation_notes(calc_id, new_notes):
                logger.debug(f"Updated notes for calculation: {calc_id}")
                
                # Refresh the calculation display to show the updated notes
                self._refresh_calculation_display(calc_id)
            else:
                logger.error(f"Failed to update notes for calculation: {calc_id}")
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to update the notes. Please try again."
                )
        
    def _on_toggle_favorite(self):
        """Handle toggle favorite button click."""
        if self.calculation:
            self.toggle_favorite_clicked.emit(self.calculation.id)

    def _refresh_calculation_display(self, calc_id: str):
        """Refresh the calculation display.
        
        Args:
            calc_id: ID of the calculation to refresh
        """
        if self.calculation and self.calculation.id == calc_id:
            # Get the updated calculation
            calculation = self.db_service.get_calculation(calc_id)
            if not calculation:
                return
                
            # Get tags
            tags = []
            if calculation.tags:
                for tag_id in calculation.tags:
                    tag = self.db_service.get_tag(tag_id)
                    if tag:
                        tags.append(tag)
                        
            # Update the display
            self.set_calculation(calculation, tags)


class CalculationHistoryPanel(QWidget):
    """Panel for displaying calculation history."""
    
    def __init__(self, parent=None):
        """Initialize the calculation history panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize the database service
        self.db_service = CalculationDatabaseService()
        
        # Initialize UI
        self._init_ui()
        
        # Load calculations
        self._load_calculations()
        
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Calculation History")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by text or value...")
        self.search_input.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_input, 1)
        
        # Tag filter
        filter_layout.addWidget(QLabel("Tag:"))
        
        self.tag_combo = QComboBox()
        self.tag_combo.addItem("All Tags", None)
        filter_layout.addWidget(self.tag_combo)
        
        # Method filter
        filter_layout.addWidget(QLabel("Method:"))
        
        self.method_combo = QComboBox()
        self.method_combo.addItem("All Methods", None)
        filter_layout.addWidget(self.method_combo)
        
        # Favorites only
        self.favorites_check = QCheckBox("Favorites Only")
        self.favorites_check.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.favorites_check)
        
        layout.addLayout(filter_layout)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Calculation list
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.calc_list = QListWidget()
        self.calc_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 2px;
            }
            QListWidget::item:selected {
                background-color: #e0f2fe;
                color: #1a1a1a;
            }
        """)
        self.calc_list.currentItemChanged.connect(self._on_item_selected)
        
        list_layout.addWidget(self.calc_list)
        
        # Delete button
        delete_button = QPushButton("Delete Selected")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_button.clicked.connect(self._delete_selected)
        list_layout.addWidget(delete_button)
        
        splitter.addWidget(list_widget)
        
        # Detail view
        self.detail_view = CalculationDetailWidget()
        self.detail_view.edit_tags_clicked.connect(self._on_edit_tags)
        self.detail_view.edit_notes_clicked.connect(self._on_edit_notes)
        self.detail_view.toggle_favorite_clicked.connect(self._on_toggle_favorite)
        
        splitter.addWidget(self.detail_view)
        
        # Set initial sizes
        splitter.setSizes([300, 400])
        
        layout.addWidget(splitter, 1)
        
        # Connect signals for filters
        self.tag_combo.currentIndexChanged.connect(self._apply_filters)
        self.method_combo.currentIndexChanged.connect(self._apply_filters)
        
    def _load_calculations(self):
        """Load calculations from the database."""
        # Clear the list
        self.calc_list.clear()
        
        # Get all calculations
        calculations = self.db_service.get_all_calculations()
        
        # Sort by created date, newest first
        calculations.sort(key=lambda c: c.timestamp, reverse=True)
        
        # Populate the calculation list
        for calc in calculations:
            self._add_calculation_to_list(calc)
            
        # Load tags for tag filter
        self._load_tag_filter()
        
        # Load methods for method filter
        self._load_method_filter()
        
    def _add_calculation_to_list(self, calculation: CalculationResult):
        """Add a calculation to the list.
        
        Args:
            calculation: Calculation to add
        """
        # Get tags for the calculation
        tags = []
        if calculation.tags:
            for tag_id in calculation.tags:
                tag = self.db_service.get_tag(tag_id)
                if tag:
                    tags.append(tag)
                    
        # Create the widget
        widget = CalculationListItem(calculation, tags)
        
        # Create list item
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, calculation.id)
        item.setSizeHint(widget.sizeHint())
        
        # Add to list
        self.calc_list.addItem(item)
        self.calc_list.setItemWidget(item, widget)
        
    def _load_tag_filter(self):
        """Load tags for the tag filter."""
        # Store current selection
        current_tag_id = self.tag_combo.currentData()
        
        # Clear the combo box
        self.tag_combo.clear()
        
        # Add "All Tags" option
        self.tag_combo.addItem("All Tags", None)
        
        # Get all tags
        tags = self.db_service.get_all_tags()
        
        # Sort by name
        tags.sort(key=lambda t: t.name)
        
        # Add tags
        for tag in tags:
            self.tag_combo.addItem(tag.name, tag.id)
            
        # Restore selection if possible
        if current_tag_id:
            for i in range(self.tag_combo.count()):
                if self.tag_combo.itemData(i) == current_tag_id:
                    self.tag_combo.setCurrentIndex(i)
                    break
            
    def _load_method_filter(self):
        """Load method filter options."""
        # Save current selection
        current_method = self.method_combo.currentData()
        
        # Clear the combo box
        self.method_combo.clear()
        
        # Add "All Methods" option
        self.method_combo.addItem("All Methods", None)
        
        # Get unique methods from calculations
        methods = set()
        for calc in self.db_service.get_all_calculations():
            if hasattr(calc, 'custom_method_name') and calc.custom_method_name:
                methods.add(calc.custom_method_name)
            elif isinstance(calc.calculation_type, CalculationType):
                methods.add(calc.calculation_type.name)
            elif isinstance(calc.calculation_type, str):
                methods.add(calc.calculation_type)
            
        # Sort methods - convert to list first for sorting
        method_list = sorted(list(methods))
        
        # Add methods
        for method in method_list:
            self.method_combo.addItem(method, method)
            
        # Restore selection if possible
        if current_method:
            for i in range(self.method_combo.count()):
                if self.method_combo.itemData(i) == current_method:
                    self.method_combo.setCurrentIndex(i)
                    break
            
    def _apply_filters(self):
        """Apply filters to the calculation list."""
        # Get filter values
        search_text = self.search_input.text().strip().lower()
        tag_id = self.tag_combo.currentData()
        method = self.method_combo.currentData()
        favorites_only = self.favorites_check.isChecked()
        
        # Get all calculations
        calculations = self.db_service.get_all_calculations()
        
        # Filter by search text
        if search_text:
            filtered = []
            for calc in calculations:
                if (search_text in calc.input_text.lower() or 
                    search_text in str(calc.result_value).lower()):
                    filtered.append(calc)
            calculations = filtered
            
        # Filter by tag
        if tag_id:
            filtered = []
            for calc in calculations:
                if calc.tags and tag_id in calc.tags:
                    filtered.append(calc)
            calculations = filtered
            
        # Filter by method
        if method:
            filtered = []
            for calc in calculations:
                method_name = None
                
                # Check in order of priority
                if hasattr(calc, 'custom_method_name') and calc.custom_method_name:
                    method_name = calc.custom_method_name
                elif isinstance(calc.calculation_type, CalculationType):
                    method_name = calc.calculation_type.name
                elif isinstance(calc.calculation_type, str):
                    method_name = calc.calculation_type
                    
                if method_name == method:
                    filtered.append(calc)
            calculations = filtered
            
        # Filter by favorites
        if favorites_only:
            filtered = []
            for calc in calculations:
                if calc.favorite:
                    filtered.append(calc)
            calculations = filtered
            
        # Sort by created date, newest first
        calculations.sort(key=lambda c: c.timestamp, reverse=True)
        
        # Clear the list
        self.calc_list.clear()
        
        # Add filtered calculations
        for calc in calculations:
            self._add_calculation_to_list(calc)
            
    def _on_item_selected(self, current, previous):
        """Handle item selection change.
        
        Args:
            current: Currently selected item
            previous: Previously selected item
        """
        if not current:
            self.detail_view.set_calculation(None)
            return
            
        # Get calculation ID
        calc_id = current.data(Qt.ItemDataRole.UserRole)
        
        # Get calculation
        calculation = self.db_service.get_calculation(calc_id)
        if not calculation:
            return
            
        # Get tags
        tags = []
        if calculation.tags:
            for tag_id in calculation.tags:
                tag = self.db_service.get_tag(tag_id)
                if tag:
                    tags.append(tag)
                    
        # Display calculation
        self.detail_view.set_calculation(calculation, tags)
        
    def _delete_selected(self):
        """Delete the selected calculation."""
        current_item = self.calc_list.currentItem()
        if not current_item:
            return
            
        # Get calculation ID
        calc_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Get calculation
        calculation = self.db_service.get_calculation(calc_id)
        if not calculation:
            return
            
        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the calculation for '{calculation.input_text}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.db_service.delete_calculation(calc_id):
                # Remove from list
                row = self.calc_list.row(current_item)
                self.calc_list.takeItem(row)
                
                # Clear detail view
                self.detail_view.set_calculation(None)
                
                # Refresh method filter
                self._load_method_filter()
                
                QMessageBox.information(
                    self,
                    "Success",
                    "Calculation deleted successfully"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to delete calculation"
                )
                
    def _on_edit_tags(self, calc_id: str):
        """Handle edit tags button click.
        
        Args:
            calc_id: ID of the calculation to edit
        """
        # Get calculation
        calculation = self.db_service.get_calculation(calc_id)
        if not calculation:
            return
            
        # Show edit tags window
        from gematria.ui.dialogs.edit_tags_window import EditTagsWindow
        window = EditTagsWindow(calc_id, parent=self)
        window.show()
        
        # Connect to window close event to refresh the UI
        window.destroyed.connect(lambda: self._refresh_calculation_display(calc_id))
    
    def _on_edit_notes(self, calc_id: str):
        """Handle edit notes button click.
        
        Args:
            calc_id: ID of the calculation to edit
        """
        # Get the current calculation
        calculation = self.db_service.get_calculation(calc_id)
        if not calculation:
            logger.warning(f"Calculation not found: {calc_id}")
            return
            
        # Show an input dialog to get the new notes
        current_notes = calculation.notes or ""
        new_notes, ok = QInputDialog.getMultiLineText(
            self,
            "Edit Notes",
            "Enter notes for this calculation:",
            current_notes
        )
        
        if ok:
            # Update the notes
            if self.db_service.update_calculation_notes(calc_id, new_notes):
                logger.debug(f"Updated notes for calculation: {calc_id}")
                
                # Refresh the calculation display to show the updated notes
                self._refresh_calculation_display(calc_id)
            else:
                logger.error(f"Failed to update notes for calculation: {calc_id}")
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to update the notes. Please try again."
                )
                
    def _on_toggle_favorite(self, calc_id: str):
        """Handle toggle favorite button click.
        
        Args:
            calc_id: ID of the calculation to toggle
        """
        # Get calculation
        calculation = self.db_service.get_calculation(calc_id)
        if not calculation:
            return
            
        # Toggle favorite status
        if self.db_service.toggle_favorite_calculation(calc_id):
            # Refresh the detail view
            self._on_item_selected(self.calc_list.currentItem(), None)
            
            # Refresh the list item
            current_item = self.calc_list.currentItem()
            if current_item:
                calc = self.db_service.get_calculation(calc_id)
                if calc:
                    # Get tags
                    tags = []
                    if calc.tags:
                        for tag_id in calc.tags:
                            tag = self.db_service.get_tag(tag_id)
                            if tag:
                                tags.append(tag)
                                
                    # Update widget
                    widget = CalculationListItem(calc, tags)
                    current_item.setSizeHint(widget.sizeHint())
                    self.calc_list.setItemWidget(current_item, widget)
        else:
            QMessageBox.warning(
                self,
                "Error",
                "Failed to update favorite status"
            )
            
    def refresh(self):
        """Refresh the calculation list."""
        # Refresh the list
        self._load_calculations()
        
        # Apply filters
        self._apply_filters()
        
    def _refresh_calculation_display(self, calc_id: str):
        """Refresh the calculation display after tags or other data has changed.
        
        Args:
            calc_id: ID of the calculation to refresh
        """
        # Refresh the detail view if this calculation is selected
        current_item = self.calc_list.currentItem()
        if current_item and current_item.data(Qt.ItemDataRole.UserRole) == calc_id:
            self._on_item_selected(current_item, None)
        
        # Refresh the list item
        for i in range(self.calc_list.count()):
            item = self.calc_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == calc_id:
                calc = self.db_service.get_calculation(calc_id)
                if calc:
                    # Get tags
                    tags = []
                    if calc.tags:
                        for tag_id in calc.tags:
                            tag = self.db_service.get_tag(tag_id)
                            if tag:
                                tags.append(tag)
                                
                    # Update widget
                    widget = CalculationListItem(calc, tags)
                    item.setSizeHint(widget.sizeHint())
                    self.calc_list.setItemWidget(item, widget)
                    break
        
        # Refresh tag filter as tags may have changed
        self._load_tag_filter() 