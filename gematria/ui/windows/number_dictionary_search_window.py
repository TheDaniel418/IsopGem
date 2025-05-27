"""
Number Dictionary Search Window.

This window provides search functionality for the Number Dictionary,
allowing users to search through all their notes and navigate to specific numbers.
"""

from typing import List, Optional
import re

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QSplitter,
    QGroupBox,
    QMessageBox,
)

from gematria.models.number_note import NumberNote
from gematria.services.number_dictionary_service import NumberDictionaryService
from shared.ui.window_management import AuxiliaryWindow


class NumberDictionarySearchWindow(AuxiliaryWindow):
    """Window for searching through Number Dictionary notes."""
    
    # Signal emitted when user wants to open a number in the dictionary
    open_number_requested = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize the search window.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Number Dictionary Search")
        self.setMinimumSize(800, 600)
        
        # Initialize service
        self.dictionary_service = NumberDictionaryService()
        
        # Current search results
        self.search_results: List[NumberNote] = []
        self.selected_note: Optional[NumberNote] = None
        
        self._setup_ui()
        self._connect_signals()
        
        # Load all notes initially
        self._load_all_notes()
    
    def _setup_ui(self):
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Search controls
        search_group = self._create_search_controls()
        layout.addWidget(search_group)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, 1)
        
        # Results table
        self.results_table = self._create_results_table()
        splitter.addWidget(self.results_table)
        
        # Preview area
        preview_widget = self._create_preview_area()
        splitter.addWidget(preview_widget)
        
        # Set splitter proportions (60% table, 40% preview)
        splitter.setSizes([480, 320])
        
        # Action buttons
        buttons_layout = self._create_action_buttons()
        layout.addLayout(buttons_layout)
    
    def _create_search_controls(self) -> QGroupBox:
        """Create the search controls group.
        
        Returns:
            QGroupBox containing search controls
        """
        group = QGroupBox("Search")
        layout = QHBoxLayout(group)
        
        # Search input
        layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in titles and content...")
        layout.addWidget(self.search_input, 1)
        
        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setDefault(True)
        layout.addWidget(self.search_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        layout.addWidget(self.clear_button)
        
        # Show all button
        self.show_all_button = QPushButton("Show All")
        layout.addWidget(self.show_all_button)
        
        return group
    
    def _create_results_table(self) -> QTableWidget:
        """Create the results table.
        
        Returns:
            QTableWidget for displaying search results
        """
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Number", "Title", "Content Preview", "Updated"])
        
        # Configure table
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(True)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        
        table.setColumnWidth(0, 80)   # Number
        table.setColumnWidth(3, 120)  # Updated
        
        return table
    
    def _create_preview_area(self) -> QGroupBox:
        """Create the preview area.
        
        Returns:
            QGroupBox containing preview controls
        """
        group = QGroupBox("Preview")
        layout = QVBoxLayout(group)
        
        # Note info
        self.note_info_label = QLabel("Select a note to preview")
        self.note_info_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(self.note_info_label)
        
        # Content preview - enhanced to show formatted content
        self.content_preview = QTextEdit()
        self.content_preview.setReadOnly(True)
        self.content_preview.setMaximumHeight(250)  # Slightly taller for better viewing
        # Enable rich text display
        self.content_preview.setAcceptRichText(True)
        layout.addWidget(self.content_preview)
        
        # Linked numbers
        linked_group = QGroupBox("Linked Numbers")
        linked_layout = QVBoxLayout(linked_group)
        
        self.linked_numbers_label = QLabel("None")
        self.linked_numbers_label.setWordWrap(True)
        linked_layout.addWidget(self.linked_numbers_label)
        
        layout.addWidget(linked_group)
        
        return group

    def _html_to_plain_text(self, html_content: str) -> str:
        """Convert HTML content to plain text for preview.
        
        Args:
            html_content: HTML content string
            
        Returns:
            Plain text version of the content
        """
        if not html_content:
            return ""
        
        # Create a temporary QTextEdit to convert HTML to plain text
        temp_edit = QTextEdit()
        temp_edit.setHtml(html_content)
        plain_text = temp_edit.toPlainText()
        temp_edit.deleteLater()
        
        return plain_text

    def _create_action_buttons(self) -> QHBoxLayout:
        """Create the action buttons layout.
        
        Returns:
            QHBoxLayout containing action buttons
        """
        layout = QHBoxLayout()
        
        # Open in Dictionary button
        self.open_button = QPushButton("Open in Dictionary")
        self.open_button.setEnabled(False)
        layout.addWidget(self.open_button)
        
        # Add spacer
        layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        return layout
    
    def _connect_signals(self):
        """Connect widget signals to their handlers."""
        # Search controls
        self.search_input.returnPressed.connect(self._perform_search)
        self.search_button.clicked.connect(self._perform_search)
        self.clear_button.clicked.connect(self._clear_search)
        self.show_all_button.clicked.connect(self._load_all_notes)
        
        # Results table
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.results_table.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Action buttons
        self.open_button.clicked.connect(self._open_selected_note)
    
    def _perform_search(self):
        """Perform search based on the current query."""
        query = self.search_input.text().strip()
        
        if not query:
            self._load_all_notes()
            return
        
        try:
            # Search using the dictionary service
            results = self.dictionary_service.search_notes(query)
            self.search_results = results
            self._update_results_table()
            
            # Update status
            count = len(results)
            if count == 0:
                self.note_info_label.setText(f"No notes found for '{query}'")
            else:
                self.note_info_label.setText(f"Found {count} note(s) for '{query}'")
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "Search Error",
                f"Error performing search: {str(e)}"
            )
    
    def _clear_search(self):
        """Clear the search input and show all notes."""
        self.search_input.clear()
        self._load_all_notes()
    
    def _load_all_notes(self):
        """Load all notes from the database."""
        try:
            all_notes = self.dictionary_service.get_all_notes()
            self.search_results = all_notes
            self._update_results_table()
            
            # Update status
            count = len(all_notes)
            if count == 0:
                self.note_info_label.setText("No notes found in the database")
            else:
                self.note_info_label.setText(f"Showing all {count} note(s)")
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "Load Error",
                f"Error loading notes: {str(e)}"
            )
    
    def _update_results_table(self):
        """Update the results table with current search results."""
        self.results_table.setRowCount(len(self.search_results))
        
        for row, note in enumerate(self.search_results):
            # Number
            number_item = QTableWidgetItem(str(note.number))
            number_item.setData(Qt.ItemDataRole.UserRole, note)
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(row, 0, number_item)
            
            # Title
            title_item = QTableWidgetItem(note.title or f"Notes for {note.number}")
            self.results_table.setItem(row, 1, title_item)
            
            # Content preview - convert HTML to plain text for table display
            plain_content = self._html_to_plain_text(note.content)
            content_preview = plain_content[:100] + "..." if len(plain_content) > 100 else plain_content
            content_preview = content_preview.replace('\n', ' ').replace('\r', ' ')
            content_item = QTableWidgetItem(content_preview)
            self.results_table.setItem(row, 2, content_item)
            
            # Updated date
            updated_str = note.updated_at.strftime("%Y-%m-%d %H:%M") if note.updated_at else "Unknown"
            updated_item = QTableWidgetItem(updated_str)
            self.results_table.setItem(row, 3, updated_item)
        
        # Clear selection and preview
        self.selected_note = None
        self._update_preview()
    
    def _on_selection_changed(self):
        """Handle table selection changes."""
        selected_items = self.results_table.selectedItems()
        if selected_items:
            # Get the note from the first column (number column)
            row = selected_items[0].row()
            number_item = self.results_table.item(row, 0)
            self.selected_note = number_item.data(Qt.ItemDataRole.UserRole)
        else:
            self.selected_note = None
        
        self._update_preview()
        self.open_button.setEnabled(self.selected_note is not None)
    
    def _on_item_double_clicked(self, item):
        """Handle double-click on table item."""
        if self.selected_note:
            self._open_selected_note()
    
    def _update_preview(self):
        """Update the preview area with the selected note."""
        if not self.selected_note:
            self.note_info_label.setText("Select a note to preview")
            self.content_preview.clear()
            self.linked_numbers_label.setText("None")
            return
        
        note = self.selected_note
        
        # Update info label
        info_text = f"Number {note.number}"
        if note.updated_at:
            info_text += f" • Updated: {note.updated_at.strftime('%Y-%m-%d %H:%M')}"
        self.note_info_label.setText(info_text)
        
        # Update content preview - display formatted HTML content
        if note.content:
            # Check if content is HTML (contains HTML tags)
            if '<' in note.content and '>' in note.content:
                # Display as formatted HTML
                self.content_preview.setHtml(note.content)
            else:
                # Display as plain text
                self.content_preview.setPlainText(note.content)
        else:
            self.content_preview.clear()
        
        # Update linked numbers
        if note.linked_numbers:
            linked_text = ", ".join(str(num) for num in sorted(note.linked_numbers))
            self.linked_numbers_label.setText(linked_text)
        else:
            self.linked_numbers_label.setText("None")
    
    def _open_selected_note(self):
        """Open the selected note in the Number Dictionary."""
        if self.selected_note:
            # Provide visual feedback
            self.note_info_label.setText(f"Opening Number Dictionary for {self.selected_note.number}...")
            
            # Emit the signal to open the number
            self.open_number_requested.emit(self.selected_note.number)
            
            # Reset the info label after a brief moment
            QTimer.singleShot(2000, lambda: self._update_preview())
            
            # Don't close the window automatically - let users keep it open for multiple searches 