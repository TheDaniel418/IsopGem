"""
Database Entries Tab Widget for Number Dictionary.

This widget displays all calculation entries from the database that match
the current number value, showing phrase/word, language, method, and tags.
Users can double-click entries to open the calculation details dialog.
"""

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)

from gematria.models.calculation_result import CalculationResult
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.ui.dialogs.calculation_details_dialog import CalculationDetailsDialog
from shared.services.service_locator import ServiceLocator


class DatabaseEntriesTabWidget(QWidget):
    """Tab widget for displaying database entries for a specific number."""

    def __init__(self, parent=None):
        """Initialize the Database Entries tab widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Get the calculation database service
        self.calculation_service = ServiceLocator.get(CalculationDatabaseService)
        
        # Current number being displayed
        self.current_number = None
        
        # Current entries
        self.entries: List[CalculationResult] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header label
        self.header_label = QLabel("Database Entries")
        self.header_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.header_label)
        
        # Info label
        self.info_label = QLabel("Select a number to view database entries")
        self.info_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.info_label)
        
        # Entries table
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(4)
        self.entries_table.setHorizontalHeaderLabels([
            "Phrase/Word", "Language", "Method", "Tags"
        ])
        
        # Configure table
        header = self.entries_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Phrase/Word
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Language
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Method
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Tags
        
        # Enable sorting
        self.entries_table.setSortingEnabled(True)
        
        # Set selection behavior
        self.entries_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.entries_table.setAlternatingRowColors(True)
        
        # Connect double-click signal
        self.entries_table.itemDoubleClicked.connect(self._on_entry_double_clicked)
        
        layout.addWidget(self.entries_table)
    
    def load_number(self, number: int):
        """Load database entries for the specified number.
        
        Args:
            number: The number to load entries for
        """
        self.current_number = number
        self.header_label.setText(f"Database Entries for {number}")
        
        # Get all calculations with this result value
        try:
            self.entries = self.calculation_service.find_calculations_by_value(number)
            self._populate_table()
            
            # Update info label
            count = len(self.entries)
            if count == 0:
                self.info_label.setText(f"No database entries found for {number}")
            elif count == 1:
                self.info_label.setText(f"Found 1 database entry for {number}")
            else:
                self.info_label.setText(f"Found {count} database entries for {number}")
                
        except Exception as e:
            self.info_label.setText(f"Error loading entries: {str(e)}")
            self.entries = []
            self._populate_table()
    
    def _populate_table(self):
        """Populate the table with current entries."""
        # Clear existing rows
        self.entries_table.setRowCount(0)
        
        if not self.entries:
            return
        
        # Add rows for each entry
        self.entries_table.setRowCount(len(self.entries))
        
        for row, entry in enumerate(self.entries):
            # Phrase/Word column
            phrase_item = QTableWidgetItem(entry.input_text)
            phrase_item.setData(Qt.ItemDataRole.UserRole, entry)  # Store the full entry
            self.entries_table.setItem(row, 0, phrase_item)
            
            # Language column (determine from calculation type or custom method)
            language = self._determine_language(entry)
            language_item = QTableWidgetItem(language)
            self.entries_table.setItem(row, 1, language_item)
            
            # Method column
            method = self._get_method_name(entry)
            method_item = QTableWidgetItem(method)
            self.entries_table.setItem(row, 2, method_item)
            
            # Tags column
            tags = self._get_tags_display(entry)
            tags_item = QTableWidgetItem(tags)
            self.entries_table.setItem(row, 3, tags_item)
    
    def _determine_language(self, entry: CalculationResult) -> str:
        """Determine the language for a calculation entry.
        
        Args:
            entry: The calculation result entry
            
        Returns:
            Language string
        """
        # Check if it's a custom method first
        if hasattr(entry, 'custom_method_name') and entry.custom_method_name:
            method_name = entry.custom_method_name.lower()
            
            # Check for language indicators in custom method names
            if 'hebrew' in method_name or 'gematria' in method_name:
                return "Hebrew"
            elif 'greek' in method_name:
                return "Greek"
            elif 'latin' in method_name or 'english' in method_name:
                return "English"
            else:
                return "Custom"
        
        # Check standard calculation types
        if hasattr(entry.calculation_type, 'name'):
            calc_type = entry.calculation_type.name.lower()
        else:
            calc_type = str(entry.calculation_type).lower()
        
        # Map calculation types to languages
        if any(keyword in calc_type for keyword in ['hebrew', 'gematria', 'mispar']):
            return "Hebrew"
        elif any(keyword in calc_type for keyword in ['greek', 'isopsephy']):
            return "Greek"
        elif any(keyword in calc_type for keyword in ['english', 'simple', 'ordinal', 'reduction']):
            return "English"
        else:
            return "Unknown"
    
    def _get_method_name(self, entry: CalculationResult) -> str:
        """Get a readable method name for the calculation entry.
        
        Args:
            entry: The calculation result entry
            
        Returns:
            Readable method name
        """
        # Check for custom method first
        if hasattr(entry, 'custom_method_name') and entry.custom_method_name:
            return entry.custom_method_name
        
        # Handle standard calculation types
        if hasattr(entry.calculation_type, 'value'):
            # It's an enum with a value tuple (name, description, language)
            if isinstance(entry.calculation_type.value, tuple) and len(entry.calculation_type.value) >= 1:
                return entry.calculation_type.value[0]  # Just the name part
        
        if hasattr(entry.calculation_type, 'name'):
            # It's an enum, use its name and clean it up
            return entry.calculation_type.name.replace("_", " ").title()
        
        # It's a string, make it readable
        method_str = str(entry.calculation_type)
        
        # If it looks like a tuple representation, try to extract the first element
        if method_str.startswith("(") and "," in method_str:
            try:
                # Extract the first quoted string from the tuple representation
                start = method_str.find("'") + 1
                end = method_str.find("'", start)
                if start > 0 and end > start:
                    return method_str[start:end]
            except:
                pass
        
        # Fallback: clean up the string representation
        return method_str.replace("_", " ").title()
    
    def _get_tags_display(self, entry: CalculationResult) -> str:
        """Get a display string for the entry's tags.
        
        Args:
            entry: The calculation result entry
            
        Returns:
            Comma-separated tag names or "No tags"
        """
        if not hasattr(entry, 'tags') or not entry.tags:
            return "No tags"
        
        try:
            # Get tag names from the calculation service
            tag_names = self.calculation_service.get_calculation_tag_names(entry)
            return ", ".join(tag_names) if tag_names else "No tags"
        except Exception:
            return "No tags"
    
    def _on_entry_double_clicked(self, item: QTableWidgetItem):
        """Handle double-click on an entry to open calculation details.
        
        Args:
            item: The table item that was double-clicked
        """
        # Get the calculation entry from the first column of the row
        row = item.row()
        phrase_item = self.entries_table.item(row, 0)
        
        if phrase_item:
            entry = phrase_item.data(Qt.ItemDataRole.UserRole)
            if entry:
                self._open_calculation_details(entry)
    
    def _open_calculation_details(self, entry: CalculationResult):
        """Open the calculation details dialog for an entry.
        
        Args:
            entry: The calculation result entry to show details for
        """
        try:
            # Ensure entry has all required attributes
            if not hasattr(entry, 'notes'):
                entry.notes = ""
            
            if not hasattr(entry, 'tags'):
                entry.tags = []
            
            # Create and show the calculation details dialog
            dialog = CalculationDetailsDialog(
                entry, 
                self.calculation_service, 
                self
            )
            
            # Connect to update signal if needed
            dialog.calculationUpdated.connect(self._on_calculation_updated)
            
            dialog.exec()
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to open calculation details: {str(e)}"
            )
    
    def _on_calculation_updated(self):
        """Handle when a calculation is updated in the details dialog."""
        # Reload the current number to refresh the display
        if self.current_number is not None:
            self.load_number(self.current_number) 