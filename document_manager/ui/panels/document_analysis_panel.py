"""
Purpose: Provides a UI panel for gematric analysis of documents.

This file is part of the document_manager pillar and serves as a UI component.
It displays document content and provides tools for gematric analysis of the text,
including searching for words/phrases with specific gematria values and calculating
gematria values of selected text.

Key components:
- DocumentAnalysisPanel: Panel for analyzing documents from a gematric perspective

Dependencies:
- PyQt6: For UI components
- document_manager.models.document: For Document model
- document_manager.services.document_service: For document operations
- gematria.services.gematria_service: For gematria calculations
"""

import re
from datetime import datetime
from typing import List, Optional, Tuple

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QIcon, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from document_manager.models.document import Document
from document_manager.services.category_service import CategoryService
from document_manager.services.document_service import DocumentService
from gematria.models.calculation_type import CalculationType
from gematria.services.gematria_service import GematriaService
from shared.ui.components.message_box import MessageBox
from shared.ui.widgets.panel import Panel
from shared.ui.widgets.unicode_text_widget import UnicodeTextEdit

# Import the TQ analysis service for sending numbers to Quadset Analysis
try:
    from tq.services import tq_analysis_service

    TQ_AVAILABLE = True
except ImportError:
    TQ_AVAILABLE = False


class DocumentAnalysisPanel(Panel):
    """Panel for analyzing documents from a gematric perspective."""

    # Signals for document operations
    gematria_value_calculated = pyqtSignal(str, int)  # (text, value)
    document_content_updated = pyqtSignal(str)  # Document ID

    def __init__(self, parent=None):
        """Initialize the document analysis panel.

        Args:
            parent: Parent widget
        """
        # Initialize with empty title to remove the header completely
        super().__init__("", parent)

        # Create services
        self.document_service = DocumentService()
        self.gematria_service = GematriaService()
        self.category_service = CategoryService()

        # Current document
        self.current_document: Optional[Document] = None

        # Search results storage
        self.text_search_results: List[Tuple[str, int]] = []  # (text, position)
        self.value_search_results: List[Tuple[str, int]] = []  # (text, position)

        # Track content modification state
        self._content_is_modified = False

        # Initialize UI
        self._init_ui()

        # Load categories and document list
        self._refresh_categories()

        # Auto-load first document if available
        if self.document_combo.count() > 0:
            self.document_combo.setCurrentIndex(0)
            # self._load_selected_document() # Loading is now handled by _on_category_changed or explicit load

    def _init_ui(self):
        """Initialize the UI components."""
        # We don't need to create a new layout - use the one from Panel base class
        # Clear any default margins
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Main splitter for search/tools and content
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Tools panel
        tools_widget = QWidget()
        tools_layout = QVBoxLayout(tools_widget)
        tools_layout.setContentsMargins(5, 5, 5, 5)
        tools_layout.setSpacing(5)  # Reduce spacing between elements

        # Document category selector
        category_layout = QVBoxLayout()
        category_layout.setSpacing(3)  # Tight spacing

        category_header = QLabel("Category")
        category_header.setStyleSheet("font-weight: bold; font-size: 11px;")
        category_layout.addWidget(category_header)

        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(130)
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        category_layout.addWidget(self.category_combo)

        tools_layout.addLayout(category_layout)

        # Document selector
        selector_layout = QHBoxLayout()
        selector_layout.setSpacing(4)  # Tighter spacing for compact layout
        selector_layout.addWidget(QLabel("Document:"))

        self.document_combo = QComboBox()
        self.document_combo.setMinimumWidth(
            130
        )  # Reduced width, will expand with the panel
        selector_layout.addWidget(self.document_combo, 1)  # Give it stretch factor

        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)  # Very tight spacing for buttons

        self.load_btn = QPushButton("Load")
        self.load_btn.setMaximumWidth(50)  # Make button narrower
        self.load_btn.clicked.connect(self._load_selected_document)
        button_layout.addWidget(self.load_btn)

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setMaximumWidth(60)  # Make button narrower
        self.refresh_btn.clicked.connect(self._refresh_categories)
        button_layout.addWidget(self.refresh_btn)

        selector_layout.addLayout(button_layout)
        tools_layout.addLayout(selector_layout)

        # Document info section (much more compact)
        info_layout = QHBoxLayout()
        info_layout.setSpacing(4)

        self.doc_title_label = QLabel("No document loaded")
        self.doc_title_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.doc_title_label.setWordWrap(True)

        self.doc_info_label = QLabel("")
        self.doc_info_label.setStyleSheet("font-size: 10px;")

        info_layout.addWidget(self.doc_title_label)
        info_layout.addWidget(self.doc_info_label)
        tools_layout.addLayout(info_layout)

        # Separator
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #cccccc;")
        tools_layout.addWidget(separator)

        # Gematria calculation section
        calc_layout = QVBoxLayout()
        calc_layout.setSpacing(3)  # Tighter spacing

        # Header
        calc_header = QLabel("Gematria Tools")
        calc_header.setStyleSheet("font-weight: bold; font-size: 11px;")
        calc_layout.addWidget(calc_header)

        # Select calculation method
        method_layout = QHBoxLayout()
        method_layout.setSpacing(4)  # Tighter spacing
        method_layout.addWidget(QLabel("Method:"), 0)  # No stretch

        self.method_combo = QComboBox()
        self.method_combo.setStyleSheet("font-size: 10px;")
        # Add gematria methods
        self.method_combo.addItem(
            "Standard (Mispar Hechrachi)", CalculationType.HEBREW_STANDARD_VALUE
        )
        self.method_combo.addItem(
            "Ordinal (Mispar Siduri)", CalculationType.HEBREW_ORDINAL_VALUE
        )
        self.method_combo.addItem("Atbash", CalculationType.HEBREW_ATBASH_SUBSTITUTION)
        self.method_combo.addItem("Albam", CalculationType.HEBREW_ALBAM_SUBSTITUTION)
        # More methods can be added here

        # Removed deprecated method Mispar Neelam

        # Add Greek methods
        self.method_combo.insertSeparator(self.method_combo.count())
        self.method_combo.addItem(
            "Greek Isopsophy", CalculationType.GREEK_STANDARD_VALUE
        )  # Standard Greek is Isopsophy
        self.method_combo.addItem("Greek Ordinal", CalculationType.GREEK_ORDINAL_VALUE)
        self.method_combo.addItem(
            "Greek Alpha-Mu", CalculationType.GREEK_ALPHAMU_SUBSTITUTION
        )
        self.method_combo.addItem(
            "Greek Alpha-Omega", CalculationType.GREEK_ALPHAOMEGA_SUBSTITUTION
        )

        # Add English methods
        self.method_combo.insertSeparator(self.method_combo.count())
        self.method_combo.addItem(
            "TQ Method", CalculationType.ENGLISH_TQ_STANDARD_VALUE
        )

        method_layout.addWidget(self.method_combo)

        # Default to TQ Method since documents are typically in English
        # Find the index of the TQ Method and set it as default
        tq_index = self.method_combo.findData(CalculationType.ENGLISH_TQ_STANDARD_VALUE)
        if tq_index >= 0:
            self.method_combo.setCurrentIndex(tq_index)

        calc_layout.addLayout(method_layout)

        # Calculate selection button and result in same row
        calc_result_layout = QHBoxLayout()
        calc_result_layout.setSpacing(4)  # Tighter spacing

        self.calc_btn = QPushButton("Calculate")
        self.calc_btn.setMaximumWidth(70)  # Narrower button
        self.calc_btn.setEnabled(False)
        self.calc_btn.clicked.connect(self._calculate_selection)
        calc_result_layout.addWidget(self.calc_btn)

        # Result display
        calc_result_layout.addWidget(QLabel("Value:"))
        self.result_label = QLabel("--")
        self.result_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        calc_result_layout.addWidget(self.result_label)
        calc_layout.addLayout(calc_result_layout)

        tools_layout.addLayout(calc_layout)

        # Separator
        separator2 = QWidget()
        separator2.setFixedHeight(1)
        separator2.setStyleSheet("background-color: #cccccc;")
        tools_layout.addWidget(separator2)

        # Search section
        search_layout = QVBoxLayout()
        search_layout.setSpacing(3)  # Tighter spacing

        # Header
        search_header = QLabel("Search")
        search_header.setStyleSheet("font-weight: bold; font-size: 11px;")
        search_layout.addWidget(search_header)

        # Value search
        value_search_layout = QVBoxLayout()
        value_search_layout.setSpacing(3)

        value_search_header = QLabel("Search by Value")
        value_search_header.setStyleSheet("font-weight: bold; font-size: 11px;")
        value_search_layout.addWidget(value_search_header)

        # Input and search button
        value_search_input_layout = QHBoxLayout()
        value_search_input_layout.setSpacing(4)

        self.value_search_input = QSpinBox()
        self.value_search_input.setRange(1, 9999)
        self.value_search_input.setValue(26)
        value_search_input_layout.addWidget(self.value_search_input, 1)

        self.search_value_btn = QPushButton("Search")
        self.search_value_btn.setMaximumWidth(60)
        self.search_value_btn.clicked.connect(self._search_by_value)
        value_search_input_layout.addWidget(self.search_value_btn)

        value_search_layout.addLayout(value_search_input_layout)

        # Add phrase search mode toggle
        self.phrase_search_mode = QCheckBox("Search for phrases")
        self.phrase_search_mode.setToolTip(
            "Search for consecutive words that match the target value"
        )
        value_search_layout.addWidget(self.phrase_search_mode)

        tools_layout.addLayout(value_search_layout)

        # Text search
        text_search_layout = QHBoxLayout()
        text_search_layout.setSpacing(4)  # Tighter spacing
        text_search_layout.addWidget(QLabel("Text:"), 0)  # No stretch

        self.text_search_input = QLineEdit()
        self.text_search_input.setPlaceholderText("Search text...")
        text_search_layout.addWidget(self.text_search_input)

        self.search_text_btn = QPushButton("Search")
        self.search_text_btn.setMaximumWidth(60)  # Narrower button
        self.search_text_btn.setEnabled(False)
        self.search_text_btn.clicked.connect(self._search_by_text)
        text_search_layout.addWidget(self.search_text_btn)

        search_layout.addLayout(text_search_layout)

        # Search results area with header
        results_header = QLabel("Results")
        results_header.setStyleSheet("font-weight: bold; font-size: 11px;")
        search_layout.addWidget(results_header)

        # Results count label
        self.results_label = QLabel("No search results")
        self.results_label.setStyleSheet("font-size: 10px;")
        search_layout.addWidget(self.results_label)

        # Results list in a scroll area
        self.results_list = QListWidget()
        self.results_list.setMaximumHeight(150)  # Limit height
        self.results_list.itemDoubleClicked.connect(self._on_result_double_clicked)

        # Add to search layout
        search_layout.addWidget(self.results_list)

        # Add search section to tools layout
        tools_layout.addLayout(search_layout)

        # Add stretch to push everything up
        tools_layout.addStretch()

        # Right side - Document content
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)  # Store as instance member
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(5)

        self.doc_content_display = UnicodeTextEdit()
        self.doc_content_display.setReadOnly(False)  # Ensure it's editable
        self.doc_content_display.setAcceptRichText(False)  # Prefer plain text
        self.doc_content_display.textChanged.connect(self._handle_content_modification)
        # Connect existing context menu and selection changed if they were on the original text_edit
        self.doc_content_display.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.doc_content_display.customContextMenuRequested.connect(
            self._show_context_menu
        )
        self.doc_content_display.selectionChanged.connect(
            self._handle_doc_content_selection_changed
        )

        self.content_layout.addWidget(self.doc_content_display, 1)  # Give it stretch

        # Add a "Save Changes" button below the text display
        self._save_edited_content_button = QPushButton("Save Text Changes")
        self._save_edited_content_button.setIcon(QIcon.fromTheme("document-save"))
        self._save_edited_content_button.setEnabled(False)  # Initially disabled
        self._save_edited_content_button.clicked.connect(
            self._save_document_content_changes
        )
        self.content_layout.addWidget(self._save_edited_content_button)

        # Set up the splitter
        main_splitter.addWidget(tools_widget)
        main_splitter.addWidget(content_widget)

        # Set initial sizes - tools panel should be narrower
        main_splitter.setSizes([250, 750])

        # Add splitter to main layout
        self.main_layout.addWidget(main_splitter)

        # No need to set the layout as it's already set by the Panel base class

    def _refresh_categories(self):
        """Refresh the categories and document list."""
        # Save current selection if any
        current_category_id = (
            self.category_combo.currentData()
            if self.category_combo.count() > 0
            else None
        )
        current_doc_id = (
            self.document_combo.currentData()
            if self.document_combo.count() > 0
            else None
        )

        # Clear the comboboxes
        self.category_combo.clear()
        self.document_combo.clear()

        # Add "All Documents" option
        self.category_combo.addItem("All Documents", None)

        # Get all categories
        categories = self.category_service.get_all_categories()

        # Sort by name
        categories.sort(key=lambda cat: cat.name)

        # Add to category combobox
        for category in categories:
            self.category_combo.addItem(category.name, category.id)

        # Restore category selection if possible, otherwise select "All Documents"
        if current_category_id:
            index = self.category_combo.findData(current_category_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentIndex(0)  # "All Documents"

        # Load documents for the selected category
        self._refresh_document_list()

        # Restore document selection if possible
        if current_doc_id:
            index = self.document_combo.findData(current_doc_id)
            if index >= 0:
                self.document_combo.setCurrentIndex(index)

    def _on_category_changed(self, index):
        """Handle category selection change.

        Args:
            index: New selected index
        """
        # Refresh document list for the selected category
        self._refresh_document_list()

        # Auto-select first document if available
        if self.document_combo.count() > 0:
            self.document_combo.setCurrentIndex(0)

    def _refresh_document_list(self):
        """Refresh the document list in the selector based on selected category."""
        # Save current selection
        current_id = self.document_combo.currentData()

        # Clear the combobox
        self.document_combo.clear()

        # Get the selected category
        category_id = self.category_combo.currentData()

        # Get all documents or documents by category
        if category_id is None:
            # "All Documents" selected
            documents = self.document_service.get_all_documents()
        else:
            # Specific category selected
            documents = self.document_service.get_documents_by_category(category_id)

        # Sort by name
        documents.sort(key=lambda doc: doc.name)

        # Add to combobox
        for document in documents:
            self.document_combo.addItem(document.name, document.id)

        # Restore selection if possible
        if current_id:
            index = self.document_combo.findData(current_id)
            if index >= 0:
                self.document_combo.setCurrentIndex(index)

    def _on_result_double_clicked(self, item):
        """Handle double-click on search result item.

        Args:
            item: Selected QListWidgetItem
        """
        # Get the position from item data
        position = item.data(Qt.ItemDataRole.UserRole)
        if position is not None:
            # Set cursor to that position
            cursor = self.doc_content_display.textCursor()
            cursor.setPosition(position)
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len(item.text().split(":")[0]),
            )  # Select the matched text
            self.doc_content_display.setTextCursor(cursor)

            # Ensure visible
            self.doc_content_display.ensureCursorVisible()

    def _load_selected_document(self):
        """Load the currently selected document."""
        document_id = self.document_combo.currentData()
        if document_id:
            self.load_document(document_id)
            # State reset is handled in load_document

    def load_document(self, document_id: str) -> bool:
        """Load a document for analysis.

        Args:
            document_id: Document ID

        Returns:
            True if document loaded successfully, False otherwise
        """
        document = self.document_service.get_document(document_id)
        if not document:
            logger.error(f"Document not found: {document_id}")
            # Clear UI if document not found
            self.current_document = None
            self.doc_title_label.setText("No document loaded")
            self.doc_info_label.setText("")
            self.doc_content_display.setPlainText("")
            self._content_is_modified = False
            self._save_edited_content_button.setEnabled(False)
            self.calc_btn.setEnabled(False)
            self.result_label.setText("--")
            self.search_value_btn.setEnabled(False)
            self.search_text_btn.setEnabled(False)
            self.results_list.clear()
            self.results_label.setText("No search results")
            return False

        self.current_document = document

        # Update combobox selection
        index = self.document_combo.findData(document_id)
        if index >= 0:
            self.document_combo.setCurrentIndex(index)

        # Update UI with document info
        self.doc_title_label.setText(document.name)
        doc_info = (
            f"{document.file_type.value.upper()} | {document.get_file_size_display()}"
        )
        if document.word_count:
            doc_info += f" | {document.word_count} words"
        if document.page_count:
            doc_info += f" | {document.page_count} pages"
        self.doc_info_label.setText(doc_info)

        doc_content_to_display = ""
        if document.extracted_text:  # Prioritize extracted_text
            doc_content_to_display = document.extracted_text
        elif document.content:  # Fallback to content
            doc_content_to_display = document.content

        if (
            not doc_content_to_display and document.file_path
        ):  # If still no content, try to extract
            logger.info(
                f"No pre-extracted text for {document.id}, attempting extraction."
            )
            if self.document_service.extract_text(document):  # This saves the document
                updated_doc = self.document_service.get_document(
                    document_id
                )  # Re-fetch
                if updated_doc and updated_doc.extracted_text:
                    self.current_document = (
                        updated_doc  # Update current_document with fresh data
                    )
                    doc_content_to_display = updated_doc.extracted_text
                elif updated_doc and updated_doc.content:
                    self.current_document = updated_doc
                    doc_content_to_display = updated_doc.content
                else:
                    doc_content_to_display = (
                        "No text content could be extracted for this document."
                    )
            else:
                doc_content_to_display = (
                    "Failed to extract text from this document type."
                )

        self.doc_content_display.setPlainText(doc_content_to_display)
        self._content_is_modified = False  # Reset modified flag
        self._save_edited_content_button.setEnabled(False)  # Disable save button

        # Enable buttons
        self.search_value_btn.setEnabled(True)
        self.search_text_btn.setEnabled(
            True
        )  # Assuming text search input is always available
        self.calc_btn.setEnabled(False)  # Disable calc until selection
        self.result_label.setText("--")
        self._clear_highlights()
        self.results_list.clear()
        self.results_label.setText("No search results")

        return True

    def _handle_doc_content_selection_changed(self):
        """Handle text selection change in the document content display."""
        has_selection = self.doc_content_display.textCursor().hasSelection()
        self.calc_btn.setEnabled(has_selection)
        # Optionally, calculate gematria on selection change without showing full result message:
        # if has_selection:
        #     self._calculate_selection(show_result=False)

    def _handle_content_modification(self):
        """Mark content as modified and enable save button."""
        if not self.current_document:  # Don't mark as modified if no document is loaded
            return
        if not self._content_is_modified:  # Only set if not already true
            self._content_is_modified = True
        self._save_edited_content_button.setEnabled(True)

    def _save_document_content_changes(self):
        """Save the changes made to the document's parsed text content."""
        if not self.current_document:
            MessageBox.warning(self, "No Document", "No document is currently loaded.")
            return

        if not self._content_is_modified:
            # MessageBox.information(self, "No Changes", "No changes to save.")
            return

        edited_text = self.doc_content_display.toPlainText()

        try:
            success = self.document_service.update_parsed_text(
                self.current_document.id, edited_text
            )
            if success:
                MessageBox.information(
                    self, "Success", "Document content updated successfully."
                )
                # Update local document object to reflect changes
                self.current_document.extracted_text = edited_text
                self.current_document.last_modified_date = datetime.now()
                # Potentially update word count if it's stored and affected
                # self.current_document.word_count = len(edited_text.split())
                # self.load_document(self.current_document.id) # Option 1: Full reload
                # Option 2: Just update modified state and button
                self._content_is_modified = False
                self._save_edited_content_button.setEnabled(False)
                self.document_content_updated.emit(
                    self.current_document.id
                )  # Emit signal
            else:
                MessageBox.critical(
                    self, "Error", "Failed to update document content in the database."
                )
        except Exception as e:
            logger.error(f"Error saving document content changes: {e}")
            MessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def _calculate_selection(self, show_result: bool = True) -> None:
        """Calculate gematria value of selected text.

        Args:
            show_result: Whether to show a message box with the result
        """
        cursor = self.doc_content_display.textCursor()
        if not cursor.hasSelection():
            return

        # Get selected text
        selected_text = cursor.selectedText()
        if not selected_text:
            return

        # Get selected calculation method
        method = self.method_combo.currentData()

        try:
            # Extract any numbers from the text and sum them
            number_sum = 0
            text_without_numbers = ""

            # Process text to handle numbers at face value
            i = 0
            while i < len(selected_text):
                if selected_text[i].isdigit():
                    # Found a digit, extract the full number
                    num_start = i
                    while i < len(selected_text) and selected_text[i].isdigit():
                        i += 1
                    # Add the number to our sum
                    number = int(selected_text[num_start:i])
                    number_sum += number
                    # We don't add the number to text_without_numbers as we've handled it directly
                else:
                    # Add non-digit characters to the clean text
                    text_without_numbers += selected_text[i]
                    i += 1

            # Calculate gematria value for the text without numbers
            if text_without_numbers.strip():
                text_value = self.gematria_service.calculate(
                    text_without_numbers, method
                )
            else:
                text_value = 0

            # Add the number sum to get total value
            value = text_value + number_sum

            # Update result label
            self.result_label.setText(str(value))

            # Show result if requested
            if show_result:
                if number_sum > 0:
                    # Provide a breakdown of the calculation
                    MessageBox.information(
                        self,
                        "Gematria Value",
                        f"The gematria value of '{selected_text}' is {value}\n\n"
                        f"Breakdown:\n"
                        f"- Text value: {text_value}\n"
                        f"- Numbers face value: {number_sum}\n"
                        f"- Total: {value}",
                    )
                else:
                    MessageBox.information(
                        self,
                        "Gematria Value",
                        f"The gematria value of '{selected_text}' is {value}",
                    )

            # Emit signal
            self.gematria_value_calculated.emit(selected_text, value)

        except Exception as e:
            logger.error(f"Error calculating gematria: {e}")
            self.result_label.setText("Error")

            if show_result:
                MessageBox.error(
                    self,
                    "Calculation Error",
                    f"Error calculating gematria value: {str(e)}",
                )

    def _search_by_value(self) -> None:
        """Search for words/phrases with a specific gematria value."""
        if not self.current_document or not self.current_document.content:
            return

        # Check if we should use phrase search mode
        if self.phrase_search_mode and self.phrase_search_mode.isChecked():
            self._search_by_phrase_value()
            return

        # Get parameters
        target_value = self.value_search_input.value()
        method = self.method_combo.currentData()

        # Clear previous highlights and results
        self._clear_highlights()
        self.results_list.clear()
        self.value_search_results = []

        # Simple algorithm: tokenize text and calculate gematria for each token
        content = self.current_document.content

        # Find word positions first for later reference
        word_positions = []
        for match in re.finditer(r"\b\w+\b", content):
            word_positions.append((match.group(0), match.start()))

        # Now search for matching words
        matches = []

        for word, position in word_positions:
            try:
                # Check if the word is a number
                if word.isdigit():
                    # If it's a number, use its face value
                    value = int(word)
                    if value == target_value:
                        matches.append((word, position))
                    continue

                # Extract numbers from word (like "AI10" -> "AI" + 10)
                number_sum = 0
                text_without_numbers = ""

                i = 0
                while i < len(word):
                    if word[i].isdigit():
                        # Found a digit, extract the full number
                        num_start = i
                        while i < len(word) and word[i].isdigit():
                            i += 1
                        # Add the number to our sum
                        number = int(word[num_start:i])
                        number_sum += number
                    else:
                        # Add non-digit characters to the clean text
                        text_without_numbers += word[i]
                        i += 1

                # Calculate gematria value for the text without numbers
                if text_without_numbers.strip():
                    text_value = self.gematria_service.calculate(
                        text_without_numbers, method
                    )
                else:
                    text_value = 0

                # Add the number sum to get total value
                value = text_value + number_sum

                if value == target_value:
                    matches.append((word, position))
            except Exception:
                continue

        # Store search results for later reference
        self.value_search_results = matches

        # Highlight matches
        if matches:
            cursor = self.doc_content_display.textCursor()
            cursor.setPosition(0)
            self.doc_content_display.setTextCursor(cursor)

            # Create format for highlighting
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor(255, 255, 0, 100))  # Light yellow

            # Find and highlight all occurrences
            for word, position in matches:
                # Create a cursor at the specific position
                cursor = self.doc_content_display.textCursor()
                cursor.setPosition(position)
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    len(word),
                )

                # Apply highlight
                cursor.mergeCharFormat(highlight_format)

                # Get some context (10 chars before and after)
                start_context = max(0, position - 10)
                end_context = min(len(content), position + len(word) + 10)
                context = content[start_context:end_context].replace("\n", " ")

                # Add the match to the results list
                item = QListWidgetItem(f"{word}: ...{context}...")
                item.setData(Qt.ItemDataRole.UserRole, position)
                self.results_list.addItem(item)

            # Update results label
            self.results_label.setText(
                f"Found {len(matches)} matches for value {target_value}"
            )
        else:
            self.results_label.setText(f"No matches found for value {target_value}")

    def _search_by_phrase_value(self) -> None:
        """Search for consecutive words with a specific combined gematria value."""
        # Validate document is loaded
        if not self.current_document or not self.current_document.content:
            return

        # Get the search value and method
        target_value = self.value_search_input.value()
        method = self.method_combo.currentData()

        # Clear previous highlights and results
        self._clear_highlights()
        self.results_list.clear()
        self.value_search_results = []

        # Extract content
        content = self.current_document.content

        # Compile the regex pattern once (more efficient)
        word_pattern = re.compile(r"\b\w+\b")

        # Find all words with their positions
        words_with_positions = [
            (match.group(0), match.start(), match.end())
            for match in word_pattern.finditer(content)
        ]

        # Create highlight format for matches
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 255, 0, 100))  # Light yellow

        # Track matches to avoid duplicates
        matches = []

        # Maximum allowed gap between consecutive words (in characters)
        max_gap = 20

        # Cache for word gematria values to avoid recalculating
        word_values_cache = {}

        # Process all possible consecutive word sequences
        for i in range(len(words_with_positions)):
            # Start with the first word and its value
            word = words_with_positions[i][0]
            phrase_start = words_with_positions[i][1]

            # Use cache for word value calculation
            if word not in word_values_cache:
                try:
                    # Check if the word is a number
                    if word.isdigit():
                        word_values_cache[word] = int(word)
                    else:
                        # Extract numbers from word (like "AI10" -> "AI" + 10)
                        number_sum = 0
                        text_without_numbers = ""
                        j = 0
                        while j < len(word):
                            if word[j].isdigit():
                                # Found a digit, extract the full number
                                num_start = j
                                while j < len(word) and word[j].isdigit():
                                    j += 1
                                # Add the number to our sum
                                number = int(word[num_start:j])
                                number_sum += number
                            else:
                                # Add non-digit characters to the clean text
                                text_without_numbers += word[j]
                                j += 1

                        # Calculate gematria value for the text without numbers
                        if text_without_numbers.strip():
                            text_value = self.gematria_service.calculate(
                                text_without_numbers, method
                            )
                        else:
                            text_value = 0

                        # Add the number sum to get total value
                        word_values_cache[word] = text_value + number_sum
                except Exception as e:
                    logger.error(f"Error calculating value for word '{word}': {e}")
                    word_values_cache[word] = 0

            # Check if single word matches target value
            phrase_value = word_values_cache[word]
            if phrase_value == target_value:
                phrase_text = word
                phrase_end = words_with_positions[i][2]

                # Only add if not a duplicate
                if (phrase_text, phrase_start, phrase_end, phrase_value) not in matches:
                    matches.append(
                        (phrase_text, phrase_start, phrase_end, phrase_value)
                    )

            # If single word exceeds target by too much, skip multi-word phrases
            if phrase_value > target_value * 2:
                continue

            # Try adding more words to the phrase
            current_phrase = [word]
            current_value = phrase_value

            for j in range(i + 1, len(words_with_positions)):
                # Check if words are too far apart
                prev_end = words_with_positions[j - 1][2]
                curr_start = words_with_positions[j][1]

                if curr_start - prev_end > max_gap:
                    break  # Words too far apart

                # Add the next word to phrase
                next_word = words_with_positions[j][0]
                current_phrase.append(next_word)

                # Get and cache word value if needed
                if next_word not in word_values_cache:
                    try:
                        if next_word.isdigit():
                            word_values_cache[next_word] = int(next_word)
                        else:
                            # Calculate word value using the same logic as above
                            number_sum = 0
                            text_without_numbers = ""
                            k = 0
                            while k < len(next_word):
                                if next_word[k].isdigit():
                                    num_start = k
                                    while k < len(next_word) and next_word[k].isdigit():
                                        k += 1
                                    number = int(next_word[num_start:k])
                                    number_sum += number
                                else:
                                    text_without_numbers += next_word[k]
                                    k += 1

                            if text_without_numbers.strip():
                                text_value = self.gematria_service.calculate(
                                    text_without_numbers, method
                                )
                            else:
                                text_value = 0

                            word_values_cache[next_word] = text_value + number_sum
                    except Exception as e:
                        logger.error(
                            f"Error calculating value for word '{next_word}': {e}"
                        )
                        word_values_cache[next_word] = 0

                # Add to phrase value
                current_value += word_values_cache[next_word]

                # If we've exceeded the target, no point continuing this phrase
                if current_value > target_value * 1.5 and target_value > 0:
                    break

                # Check if we hit the target value exactly
                if current_value == target_value:
                    phrase_text = " ".join(current_phrase)
                    phrase_end = words_with_positions[j][2]

                    # Only add if not a duplicate
                    if (
                        phrase_text,
                        phrase_start,
                        phrase_end,
                        current_value,
                    ) not in matches:
                        matches.append(
                            (phrase_text, phrase_start, phrase_end, current_value)
                        )

        # Store search results for later reference - maintain format expected by other methods
        self.value_search_results = [(text, pos) for text, pos, _, _ in matches]

        # Highlight matches and populate results list
        if matches:
            for phrase_text, start_pos, end_pos, phrase_value in matches:
                # Create a cursor at the specific position
                cursor = self.doc_content_display.textCursor()
                cursor.setPosition(start_pos)
                cursor.movePosition(
                    QTextCursor.MoveOperation.Right,
                    QTextCursor.MoveMode.KeepAnchor,
                    end_pos - start_pos,
                )

                # Apply highlight
                cursor.mergeCharFormat(highlight_format)

                # Get some context
                start_context = max(0, start_pos - 10)
                end_context = min(len(content), end_pos + 10)
                context = content[start_context:end_context].replace("\n", " ")

                # Add to results list
                item = QListWidgetItem(
                    f"{phrase_text} ({phrase_value}): ...{context}..."
                )
                item.setData(Qt.ItemDataRole.UserRole, start_pos)
                self.results_list.addItem(item)

            # Update results label
            self.results_label.setText(
                f"Found {len(matches)} phrase matches for value {target_value}"
            )
        else:
            self.results_label.setText(
                f"No phrase matches found for value {target_value}"
            )

    def _search_by_text(self):
        """Search for text in the document."""
        if not self.current_document or not self.current_document.content:
            return

        # Get search text
        search_text = self.text_search_input.text().strip()
        if not search_text:
            return

        # Clear previous highlights and results
        self._clear_highlights()
        self.results_list.clear()
        self.text_search_results = []

        # Create format for highlighting
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(173, 216, 230, 100))  # Light blue

        # Find all occurrences with positions
        content = self.current_document.content
        matches = []

        for match in re.finditer(re.escape(search_text), content, re.IGNORECASE):
            matches.append((match.group(0), match.start()))

            # Create a cursor at the specific position
            cursor = self.doc_content_display.textCursor()
            cursor.setPosition(match.start())
            cursor.movePosition(
                QTextCursor.MoveOperation.Right,
                QTextCursor.MoveMode.KeepAnchor,
                len(match.group(0)),
            )

            # Apply highlight
            cursor.mergeCharFormat(highlight_format)

            # Get some context (15 chars before and after)
            start_context = max(0, match.start() - 15)
            end_context = min(len(content), match.end() + 15)
            context = content[start_context:end_context].replace("\n", " ")

            # Add the match to the results list
            item = QListWidgetItem(f"{match.group(0)}: ...{context}...")
            item.setData(Qt.ItemDataRole.UserRole, match.start())
            self.results_list.addItem(item)

        # Store search results for later reference
        self.text_search_results = matches

        # Update results label
        if matches:
            self.results_label.setText(
                f"Found {len(matches)} occurrences of '{search_text}'"
            )
        else:
            self.results_label.setText(f"No occurrences found for '{search_text}'")

        # Reset cursor to start
        cursor = self.doc_content_display.textCursor()
        cursor.setPosition(0)
        self.doc_content_display.setTextCursor(cursor)

    def _highlight_text(self, text: str, format: QTextCharFormat) -> int:
        """Highlight all occurrences of text in the document.

        Args:
            text: Text to highlight
            format: Text format to apply

        Returns:
            Number of occurrences highlighted
        """
        # Reset cursor to start
        cursor = self.doc_content_display.textCursor()
        cursor.setPosition(0)
        self.doc_content_display.setTextCursor(cursor)

        # Count occurrences
        count = 0

        # Find and highlight all occurrences
        while self.doc_content_display.find(text):
            cursor = self.doc_content_display.textCursor()
            cursor.mergeCharFormat(format)
            count += 1

        # Reset cursor to start
        cursor = self.doc_content_display.textCursor()
        cursor.setPosition(0)
        self.doc_content_display.setTextCursor(cursor)

        return count

    def _clear_highlights(self):
        """Clear all highlights in the document."""
        # Create default format
        default_format = QTextCharFormat()

        # Apply to entire document
        cursor = self.doc_content_display.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(default_format)

        # Reset cursor
        cursor.clearSelection()
        self.doc_content_display.setTextCursor(cursor)

    def _show_context_menu(self, position):
        """Show context menu for text operations.

        Args:
            position: Position where menu should appear
        """
        # Create context menu
        menu = QMenu()

        cursor = self.doc_content_display.textCursor()
        has_selection = cursor.hasSelection()

        # If there's a selection, add calculation options
        if has_selection:
            # Get selected text
            selected_text = cursor.selectedText()
            if not selected_text:
                return

            # Add actions for selection
            calc_action = QAction("Calculate Gematria Value", self)
            calc_action.triggered.connect(self._calculate_selection)
            menu.addAction(calc_action)

            # Calculate and display the current value
            method = self.method_combo.currentData()
            try:
                value = self.gematria_service.calculate(selected_text, method)

                # Add action to search for this value
                search_action = QAction(f"Find Words with Value {value}", self)
                search_action.triggered.connect(lambda: self._search_for_value(value))
                menu.addAction(search_action)

                # Add action to save to database
                save_action = QAction("Save to Gematria Database", self)
                save_action.triggered.connect(
                    lambda: self._save_to_database(selected_text, value)
                )
                menu.addAction(save_action)

                # Add action to send to Quadset Analysis if TQ is available and value is an integer
                if TQ_AVAILABLE:
                    # Only add the option if the value is a valid integer
                    # (should always be the case with gematria values, but check to be safe)
                    try:
                        int_value = int(value)
                        tq_action = QAction(
                            f"Send {int_value} to Quadset Analysis", self
                        )
                        tq_action.triggered.connect(
                            lambda: self._send_to_quadset_analysis(int_value)
                        )
                        menu.addAction(tq_action)
                    except (ValueError, TypeError):
                        pass

            except Exception:
                pass

            # Check if the selection is a pure number that can be sent to Quadset Analysis
            if TQ_AVAILABLE and selected_text.strip().isdigit():
                try:
                    int_value = int(selected_text.strip())
                    tq_action = QAction(f"Send {int_value} to Quadset Analysis", self)
                    tq_action.triggered.connect(
                        lambda: self._send_to_quadset_analysis(int_value)
                    )
                    menu.addAction(tq_action)
                except (ValueError, TypeError):
                    pass

            # Add separator
            menu.addSeparator()

        # Add document-level actions (available regardless of selection)

        # Check if document has been flagged as having Greek text
        if self.current_document and self.current_document.metadata.get(
            "has_greek_text"
        ):
            revert_action = QAction("Revert Greek Text Conversion", self)
            revert_action.triggered.connect(self._revert_greek_conversion)
            menu.addAction(revert_action)

        # Show menu only if it has actions
        if not menu.isEmpty():
            menu.exec(self.doc_content_display.viewport().mapToGlobal(position))

    def _search_for_value(self, value: int):
        """Search for words with the specified gematria value.

        Args:
            value: Gematria value to search for
        """
        self.value_search_input.setValue(value)
        self._search_by_value()

    def _save_to_database(self, text: str, value: int) -> None:
        """Save a calculation to the gematria database.

        Args:
            text: Text that was calculated
            value: Gematria value
        """
        method = self.method_combo.currentData()

        try:
            # We need to recalculate with our number-handling approach to ensure consistency
            # Extract any numbers from the text and sum them
            number_sum = 0
            text_without_numbers = ""

            # Process text to handle numbers at face value
            i = 0
            while i < len(text):
                if text[i].isdigit():
                    # Found a digit, extract the full number
                    num_start = i
                    while i < len(text) and text[i].isdigit():
                        i += 1
                    # Add the number to our sum
                    number = int(text[num_start:i])
                    number_sum += number
                    # We don't add the number to text_without_numbers as we've handled it directly
                else:
                    # Add non-digit characters to the clean text
                    text_without_numbers += text[i]
                    i += 1

            # In the database notes, we'll add information about the number handling
            notes = None
            if number_sum > 0:
                # If there are numbers in the text, add a note explaining the calculation
                text_value = value - number_sum
                notes = (
                    f"Numbers face value: {number_sum}, Text value: {text_value}. "
                    f"Numbers in text are calculated at their face value."
                )

            # Calculate and save to database with the notes
            self.gematria_service.calculate_and_save(
                text, method, value=value, notes=notes
            )

            MessageBox.information(
                self,
                "Saved to Database",
                f"The calculation for '{text}' with value {value} has been saved to the database.",
            )

        except Exception as e:
            logger.error(f"Error saving calculation: {e}")

            MessageBox.error(
                self, "Save Error", f"Error saving calculation to database: {str(e)}"
            )

    def _revert_greek_conversion(self):
        """Revert Greek text conversion for the current document."""
        if not self.current_document:
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Revert Greek Conversion",
            "This will attempt to revert the Greek character conversion for this document. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.document_service.revert_greek_conversion(
                    self.current_document.id
                )

                if success:
                    MessageBox.information(
                        self,
                        "Conversion Reverted",
                        "The Greek text conversion has been reverted. Reloading document...",
                    )

                    # Reload the document to show the changes
                    self.load_document(self.current_document.id)
                else:
                    MessageBox.warning(
                        self,
                        "Revert Failed",
                        "Could not revert the Greek text conversion. See logs for details.",
                    )
            except Exception as e:
                MessageBox.error(self, "Error", f"An error occurred: {str(e)}")

    def _send_to_quadset_analysis(self, value: int) -> None:
        """Send a value to the TQ Quadset Analysis tool.

        Args:
            value: Integer value to analyze in the TQ Grid
        """
        if not TQ_AVAILABLE:
            MessageBox.warning(
                self,
                "Feature Unavailable",
                "The TQ module is not available in this installation.",
            )
            return

        try:
            # Open the TQ Grid with this number
            tq_analysis_service.get_instance().open_quadset_analysis(value)

        except Exception as e:
            logger.error(f"Error opening quadset analysis: {e}")
            MessageBox.error(
                self,
                "Error",
                f"An error occurred while opening Quadset Analysis: {str(e)}",
            )
