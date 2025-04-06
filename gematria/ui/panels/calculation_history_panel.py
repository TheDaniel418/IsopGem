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
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QComboBox,
    QLineEdit,
    QGroupBox,
    QScrollArea,
    QInputDialog,
    QCheckBox,
    QMenu,
    QMessageBox,
    QSpinBox,
    QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QColor, QIcon, QAction, QFont, QPixmap

from loguru import logger
from gematria.models.calculation_result import CalculationResult
from gematria.models.tag import Tag
from gematria.models.calculation_type import CalculationType, get_calculation_type_name
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.ui.dialogs.create_tag_dialog import CreateTagDialog
from shared.services.service_locator import ServiceLocator
from shared.services.tag_service import TagService
from gematria.ui.dialogs.calculation_details_dialog import CalculationDetailsDialog
from shared.ui.base_panel import BasePanel
from shared.ui.widgets.common_widgets import CollapsibleBox

from typing import Dict, List, Optional, Set
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QComboBox,
    QLineEdit,
    QSplitter,
    QFrame,
    QCheckBox,
    QStackedWidget,
    QTextEdit,
    QGridLayout,
    QScrollArea,
    QToolButton,
    QDialog,
    QInputDialog,
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
        self.setStyleSheet(
            """
            background-color: #f0f0f0;
            border-radius: 2px;
        """
        )


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
        date = QLabel(calculation.timestamp.strftime("%Y-%m-%d %H:%M"))
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
        if (
            hasattr(calculation, "custom_method_name")
            and calculation.custom_method_name
        ):
            method_name = calculation.custom_method_name
        elif hasattr(calculation.calculation_type, "name"):
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
        self.setStyleSheet(
            """
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
        """
        )


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
        self.text_section.setStyleSheet(
            "background-color: #f8f9fa; border-radius: 4px;"
        )

        text_layout = QVBoxLayout(self.text_section)

        text_header = QLabel("Input Text:")
        text_header.setStyleSheet("font-weight: bold;")
        text_layout.addWidget(text_header)

        self.text_value = QLabel()
        self.text_value.setWordWrap(True)
        self.text_value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        text_layout.addWidget(self.text_value)

        self.content_layout.addWidget(self.text_section)

        # Value and method
        info_grid = QGridLayout()
        info_grid.setColumnStretch(1, 1)

        # Value
        info_grid.addWidget(QLabel("Value:"), 0, 0)
        self.value_label = QLabel()
        self.value_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
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
        self.notes_text.setStyleSheet(
            """
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """
        )
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
            if (
                hasattr(calculation, "custom_method_name")
                and calculation.custom_method_name
            ):
                return calculation.custom_method_name

            # Next, check calculation_type
            if hasattr(calculation, "calculation_type"):
                calc_type = calculation.calculation_type

                # Handle enum type with name attribute
                if hasattr(calc_type, "name"):
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

    def set_calculation(
        self, calculation: Optional[CalculationResult], tags: Optional[List[Tag]] = None
    ):
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
        self.created_label.setText(calculation.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        self.notes_text.setText(calculation.notes or "")

        # Update favorite button
        if calculation.favorite:
            self.favorite_btn.setText("Remove from Favorites")
            self.favorite_btn.setStyleSheet(
                """
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
            """
            )
        else:
            self.favorite_btn.setText("Mark as Favorite")
            self.favorite_btn.setStyleSheet(
                """
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
            """
            )

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
            self, "Edit Notes", "Enter notes for this calculation:", current_notes
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
                    self, "Error", "Failed to update the notes. Please try again."
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


class CalculationHistoryPanel(BasePanel):
    """Panel for viewing calculation history with pagination and filtering."""

    def __init__(self):
        """Initialize the panel."""
        super().__init__("Calculation History")
        
        # Get services
        self.calculation_service = ServiceLocator.get(CalculationDatabaseService)
        self.tag_service = ServiceLocator.get(TagService)
        
        # Pagination state
        self.current_page = 0
        self.page_size = 50
        self.total_calculations = 0
        
        # Filter state
        self.search_text = ""
        self.filter_tag = None
        self.filter_method = None
        self.favorites_only = False
        
        # UI state
        self.selected_calculation = None
        
        # Configure search debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._on_search_debounced)
        
        # Initialize UI
        self._init_ui()
        
        # Load data
        self._load_tags_and_methods()
        self._load_calculations()
        
    def _init_ui(self):
        """Initialize UI components with focus on performance and usability."""
        # Main layout
        main_layout = QVBoxLayout()
        
        # Search and filter section
        search_panel = QWidget()
        search_layout = QVBoxLayout(search_panel)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search bar with refresh button
        search_control = QWidget()
        search_control_layout = QHBoxLayout(search_control)
        search_control_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by text, value, or notes...")
        self.search_box.textChanged.connect(self._on_search_changed)
        
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setToolTip("Refresh calculations")
        self.refresh_button.clicked.connect(self._on_refresh)
        self.refresh_button.setFixedWidth(30)
        
        search_control_layout.addWidget(self.search_box)
        search_control_layout.addWidget(self.refresh_button)
        
        search_layout.addWidget(search_control)
        
        # Filters in collapsible box
        filter_box = CollapsibleBox("Filters")
        filter_content = QWidget()
        filter_layout = QGridLayout(filter_content)
        
        # Tag filter
        filter_layout.addWidget(QLabel("Tag:"), 0, 0)
        self.tag_combo = QComboBox()
        self.tag_combo.addItem("All Tags", None)
        self.tag_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.tag_combo, 0, 1)
        
        # Method filter
        filter_layout.addWidget(QLabel("Method:"), 1, 0)
        self.method_combo = QComboBox()
        self.method_combo.addItem("All Methods", None)
        self.method_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.method_combo, 1, 1)
        
        # Favorites only checkbox
        self.favorites_check = QCheckBox("Favorites Only")
        self.favorites_check.stateChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.favorites_check, 2, 0, 1, 2)
        
        filter_box.setContentLayout(filter_layout)
        search_layout.addWidget(filter_box)
        
        main_layout.addWidget(search_panel)
        
        # Pagination controls
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(0, 0, 0, 0)
        
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self._load_prev_page)
        
        self.page_label = QLabel("Page 1")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self._load_next_page)
        
        # Page size control
        page_size_widget = QWidget()
        page_size_layout = QHBoxLayout(page_size_widget)
        page_size_layout.setContentsMargins(0, 0, 0, 0)
        
        page_size_layout.addWidget(QLabel("Per page:"))
        self.page_size_combo = QComboBox()
        for size in [10, 25, 50, 100]:
            self.page_size_combo.addItem(str(size), size)
        self.page_size_combo.setCurrentIndex(2)  # Default to 50
        self.page_size_combo.currentIndexChanged.connect(self._on_page_size_changed)
        page_size_layout.addWidget(self.page_size_combo)
        
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label, 1)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addWidget(page_size_widget)
        
        main_layout.addWidget(pagination_widget)
        
        # Splitter for list and details
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Calculation list
        self.calculation_list = QListWidget()
        self.calculation_list.setAlternatingRowColors(True)
        self.calculation_list.currentItemChanged.connect(self._on_calculation_selected)
        self.calculation_list.itemDoubleClicked.connect(self._on_calculation_details)
        
        # Details panel
        self.details_panel = QWidget()
        details_layout = QVBoxLayout(self.details_panel)
        
        self.details_title = QLabel("Select a calculation to view details")
        self.details_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        details_layout.addWidget(self.details_title)
        
        self.details_value = QLabel("")
        details_layout.addWidget(self.details_value)
        
        self.details_method = QLabel("")
        details_layout.addWidget(self.details_method)
        
        self.details_tags = QLabel("")
        details_layout.addWidget(self.details_tags)
        
        self.details_notes = QLabel("")
        self.details_notes.setWordWrap(True)
        details_layout.addWidget(self.details_notes)
        
        details_layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.view_details_button = QPushButton("View Full Details")
        self.view_details_button.clicked.connect(self._on_calculation_details)
        self.view_details_button.setEnabled(False)
        button_layout.addWidget(self.view_details_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete_calculation)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        details_layout.addLayout(button_layout)
        
        splitter.addWidget(self.calculation_list)
        splitter.addWidget(self.details_panel)
        splitter.setSizes([300, 200])
        
        main_layout.addWidget(splitter, 1)
        
        self.setLayout(main_layout)
        
    def _on_search_changed(self, text):
        """Handle search text changes with debouncing."""
        self.search_text = text
        # Reset to 500ms wait before executing search
        self.search_timer.start(500)  
        
    def _on_search_debounced(self):
        """Perform the actual search after debounce delay."""
        self.current_page = 0
        self._load_calculations()
        
    def _on_filter_changed(self):
        """Handle filter changes."""
        self.filter_tag = self.tag_combo.currentData()
        self.filter_method = self.method_combo.currentData()
        self.favorites_only = self.favorites_check.isChecked()
        self.current_page = 0  # Reset to first page when filters change
        self._load_calculations()
        
    def _on_page_size_changed(self):
        """Handle page size changes."""
        self.page_size = self.page_size_combo.currentData()
        self.current_page = 0  # Reset to first page when page size changes
        self._load_calculations()
        
    def _load_prev_page(self):
        """Load the previous page of results."""
        if self.current_page > 0:
            self.current_page -= 1
            self._load_calculations()
            
    def _load_next_page(self):
        """Load the next page of results."""
        max_page = (self.total_calculations - 1) // self.page_size
        if self.current_page < max_page:
            self.current_page += 1
            self._load_calculations()
            
    def _update_pagination_controls(self):
        """Update pagination controls based on current state."""
        self.prev_button.setEnabled(self.current_page > 0)
        
        max_page = (self.total_calculations - 1) // self.page_size if self.total_calculations > 0 else 0
        self.next_button.setEnabled(self.current_page < max_page)
        
        start_item = self.current_page * self.page_size + 1 if self.total_calculations > 0 else 0
        end_item = min((self.current_page + 1) * self.page_size, self.total_calculations)
        
        self.page_label.setText(f"Page {self.current_page + 1} of {max_page + 1} ({start_item}-{end_item} of {self.total_calculations})")
        
    def _on_refresh(self):
        """Refresh the calculation list and reset filters."""
        self.search_box.clear()
        self.tag_combo.setCurrentIndex(0)
        self.method_combo.setCurrentIndex(0)
        self.favorites_check.setChecked(False)
        self.current_page = 0
        self._load_tags_and_methods()
        self._load_calculations()
        
    def _load_calculations(self):
        """Load calculations with current pagination and filtering."""
        # Get total count for pagination
        self.total_calculations = self.calculation_service.count_calculations()
        
        # Calculate offset based on current page and page size
        offset = self.current_page * self.page_size
        
        # Get calculations for current page
        calculations = self.calculation_service.get_calculations_page(
            offset=offset,
            limit=self.page_size,
            sort_by="timestamp",
            sort_order="DESC"
        )
        
        # Apply additional filtering if needed
        if self.search_text or self.filter_tag or self.filter_method or self.favorites_only:
            calculations = self._apply_filters(calculations)
        
        # Update UI
        self._populate_calculation_list(calculations)
        self._update_pagination_controls()
        
    def _apply_filters(self, calculations: List[CalculationResult]) -> List[CalculationResult]:
        """Apply filters to the calculation list.
        
        Args:
            calculations: List of calculations to filter
            
        Returns:
            Filtered list of calculations
        """
        filtered = calculations.copy()
        
        # Filter by search text
        if self.search_text:
            text = self.search_text.lower()
            filtered = [
                calc for calc in filtered 
                if (text in calc.input_text.lower() or 
                    (calc.notes and text in calc.notes.lower()) or
                    (str(calc.result_value) == text))
            ]
            
        # Filter by tag
        if self.filter_tag:
            filtered = [calc for calc in filtered if self.filter_tag in calc.tags]
            
        # Filter by method
        if self.filter_method:
            filtered = [calc for calc in filtered if calc.calculation_type == self.filter_method]
            
        # Filter by favorites
        if self.favorites_only:
            filtered = [calc for calc in filtered if calc.favorite]
            
        return filtered
        
    def _populate_calculation_list(self, calculations: List[CalculationResult]):
        """Populate the list widget with calculations.
        
        Args:
            calculations: List of calculations to display
        """
        self.calculation_list.clear()
        
        for calc in calculations:
            item = QListWidgetItem()
            
            # Format the display text
            input_text = calc.input_text
            # Truncate if too long
            if len(input_text) > 30:
                input_text = input_text[:27] + "..."
                
            display_text = f"{input_text} = {calc.result_value}"
            if calc.tags:
                tag_text = ", ".join(calc.tags[:2])
                if len(calc.tags) > 2:
                    tag_text += "..."
                display_text += f" [{tag_text}]"
                
            item.setText(display_text)
            
            # Store the calculation ID in the item's data
            item.setData(Qt.ItemDataRole.UserRole, calc.id)
            
            # Highlight favorites
            if calc.favorite:
                item.setForeground(QColor("#0066cc"))
                item.setText("★ " + item.text())
                
            self.calculation_list.addItem(item)
            
    def _on_calculation_selected(self, current, previous):
        """Handle calculation selection change."""
        if not current:
            self.selected_calculation = None
            self.view_details_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.details_title.setText("Select a calculation to view details")
            self.details_value.setText("")
            self.details_method.setText("")
            self.details_tags.setText("")
            self.details_notes.setText("")
            return
            
        calc_id = current.data(Qt.ItemDataRole.UserRole)
        calculation = self.calculation_service.get_calculation(calc_id)
        
        if calculation:
            self.selected_calculation = calculation
            self.view_details_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            
            self.details_title.setText(f"Calculation: {calculation.input_text}")
            self.details_value.setText(f"Result: {calculation.result_value}")
            self.details_method.setText(f"Method: {calculation.calculation_type}")
            
            if calculation.tags:
                self.details_tags.setText(f"Tags: {', '.join(calculation.tags)}")
            else:
                self.details_tags.setText("Tags: None")
                
            if calculation.notes:
                self.details_notes.setText(f"Notes: {calculation.notes}")
            else:
                self.details_notes.setText("Notes: None")
                
    def _on_calculation_details(self):
        """Open calculation details dialog."""
        if self.selected_calculation:
            dialog = CalculationDetailsDialog(self.selected_calculation, self)
            dialog.calculationUpdated.connect(self._load_calculations)
            dialog.exec()
            
    def _on_delete_calculation(self):
        """Delete the selected calculation."""
        if self.selected_calculation:
            # Confirm deletion
            confirm = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete this calculation?\n\n{self.selected_calculation.input_text} = {self.selected_calculation.result_value}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                # Delete and refresh
                success = self.calculation_service.delete_calculation(self.selected_calculation.id)
                if success:
                    self._load_calculations()
                    self.selected_calculation = None
                    
    def _load_tags_and_methods(self):
        """Load tags and calculation methods for filters."""
        self._load_tag_filter()
        self._load_method_filter_optimized()
                
    def _load_tag_filter(self):
        """Load tags for the tag filter."""
        self.tag_combo.clear()
        self.tag_combo.addItem("All Tags", None)
        
        tags = self.tag_service.get_all_tags()
        for tag in sorted(tags, key=lambda t: t.name):
            self.tag_combo.addItem(tag.name, tag.id)
            
    def _load_method_filter_optimized(self):
        """Load calculation methods for the method filter by querying unique methods."""
        self.method_combo.clear()
        self.method_combo.addItem("All Methods", None)
        
        # Get unique calculation methods directly from the database
        methods = self.calculation_service.get_unique_calculation_methods()
        
        # Add each unique method to the combo box
        for method_name in sorted(methods):
            self.method_combo.addItem(method_name, method_name)
