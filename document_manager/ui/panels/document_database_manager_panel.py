"""
Purpose: Provides a UI panel for managing documents in the database.

This file is part of the document_manager pillar and serves as a UI component.
It allows users to view, filter, export, and delete documents stored in the database.

Key components:
- DocumentDatabaseManagerPanel: Panel for managing documents in the database

Dependencies:
- PyQt6: For UI components
- document_manager.models.document: For Document model
- document_manager.services.document_service: For document operations
- document_manager.services.category_service: For category operations
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from document_manager.models.document import Document, DocumentType
from document_manager.services.category_service import CategoryService
from document_manager.services.document_service import DocumentService
from shared.ui.components.message_box import MessageBox


class DocumentDatabaseManagerPanel(QWidget):
    """Panel for managing documents in the database."""

    # Signal emitted when a document is selected
    document_selected = pyqtSignal(str)  # Document ID

    def __init__(self, parent=None):
        """Initialize the document database manager panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Document Database Manager")

        # Create services
        self.document_service = DocumentService()
        self.category_service = CategoryService()

        # Track current selection
        self.current_document_id = None
        self.documents: List[Document] = []
        self.categories = {}
        self.filtered_documents: List[Document] = []

        # Initialize UI
        self._init_ui()

        # Load data
        self._load_documents()
        self._load_categories()

    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Title and description
        title_label = QLabel("Document Database Manager")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        description_label = QLabel(
            "Manage documents stored in the database. View, filter, export, and delete documents."
        )
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)

        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left side - Document list and filters
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Filters
        filter_widget = QWidget()
        filter_layout = QVBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)

        # Search filter
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or content...")
        self.search_input.textChanged.connect(self._apply_filters)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        filter_layout.addLayout(search_layout)

        # Type filter
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItem("All Types", None)
        for doc_type in DocumentType:
            self.type_combo.addItem(doc_type.value.upper(), doc_type)
        self.type_combo.currentIndexChanged.connect(self._apply_filters)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        filter_layout.addLayout(type_layout)

        # Category filter
        category_layout = QHBoxLayout()
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories", None)
        self.category_combo.currentIndexChanged.connect(self._apply_filters)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        filter_layout.addLayout(category_layout)

        # Date filter
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        self.date_combo = QComboBox()
        self.date_combo.addItem("All Time", None)
        self.date_combo.addItem("Today", "today")
        self.date_combo.addItem("This Week", "week")
        self.date_combo.addItem("This Month", "month")
        self.date_combo.addItem("This Year", "year")
        self.date_combo.currentIndexChanged.connect(self._apply_filters)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_combo)
        filter_layout.addLayout(date_layout)

        # Add filter widget to left layout
        left_layout.addWidget(filter_widget)

        # Document table
        self.document_table = QTableWidget()
        self.document_table.setColumnCount(5)
        self.document_table.setHorizontalHeaderLabels(
            ["Name", "Type", "Size", "Modified", "Category"]
        )
        self.document_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.document_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.document_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.document_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.document_table.setAlternatingRowColors(True)
        self.document_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.document_table.customContextMenuRequested.connect(
            self._show_context_menu
        )
        self.document_table.itemSelectionChanged.connect(
            self._on_selection_changed
        )
        self.document_table.doubleClicked.connect(self._on_document_double_clicked)
        left_layout.addWidget(self.document_table)

        # Action buttons
        button_layout = QHBoxLayout()

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh)
        button_layout.addWidget(self.refresh_btn)

        # Export button
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self._export_document)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)

        # Delete button
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_document)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        left_layout.addLayout(button_layout)

        # Right side - Document details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Document details
        details_label = QLabel("Document Details")
        details_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        right_layout.addWidget(details_label)

        # Document metadata
        self.metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(self.metadata_widget)
        metadata_layout.setContentsMargins(0, 0, 0, 0)

        # Document name
        self.doc_name_label = QLabel()
        self.doc_name_label.setStyleSheet("font-size: 12pt; font-weight: bold;")
        metadata_layout.addWidget(self.doc_name_label)

        # Document info
        self.doc_info_label = QLabel()
        metadata_layout.addWidget(self.doc_info_label)

        # Document path
        path_layout = QHBoxLayout()
        path_label = QLabel("Path:")
        self.doc_path_label = QLabel()
        self.doc_path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.doc_path_label)
        metadata_layout.addLayout(path_layout)

        # Document category
        category_info_layout = QHBoxLayout()
        category_info_label = QLabel("Category:")
        self.doc_category_label = QLabel()
        category_info_layout.addWidget(category_info_label)
        category_info_layout.addWidget(self.doc_category_label)
        metadata_layout.addLayout(category_info_layout)

        # Document metadata
        self.metadata_label = QLabel("Additional Metadata:")
        metadata_layout.addWidget(self.metadata_label)

        # Add metadata widget to right layout
        right_layout.addWidget(self.metadata_widget)

        # Document content
        content_label = QLabel("Document Content")
        content_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        right_layout.addWidget(content_label)

        # Content preview
        self.content_preview = QTextEdit()
        self.content_preview.setReadOnly(True)
        right_layout.addWidget(self.content_preview)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])

    def _load_documents(self):
        """Load documents from the service."""
        self.documents = self.document_service.get_all_documents()
        self.filtered_documents = self.documents.copy()
        self._update_document_table()

    def _load_categories(self):
        """Load categories from the service."""
        categories = self.category_service.get_all_categories()
        self.categories = {category.id: category for category in categories}

        # Update category combo
        self.category_combo.clear()
        self.category_combo.addItem("All Categories", None)
        for category in sorted(categories, key=lambda c: c.name):
            self.category_combo.addItem(category.name, category.id)

    def _update_document_table(self):
        """Update the document table with filtered documents."""
        self.document_table.setRowCount(0)
        self.document_table.setRowCount(len(self.filtered_documents))

        for row, document in enumerate(self.filtered_documents):
            # Name
            name_item = QTableWidgetItem(document.name)
            self.document_table.setItem(row, 0, name_item)

            # Type
            type_item = QTableWidgetItem(document.file_type.value.upper())
            self.document_table.setItem(row, 1, type_item)

            # Size
            size_item = QTableWidgetItem(self._format_size(document.size_bytes))
            self.document_table.setItem(row, 2, size_item)

            # Modified date
            date_item = QTableWidgetItem(
                document.last_modified_date.strftime("%Y-%m-%d %H:%M")
            )
            self.document_table.setItem(row, 3, date_item)

            # Category
            category_name = ""
            if document.category and document.category in self.categories:
                category_name = self.categories[document.category].name
            category_item = QTableWidgetItem(category_name)
            self.document_table.setItem(row, 4, category_item)

            # Store document ID in the first column
            name_item.setData(Qt.ItemDataRole.UserRole, document.id)

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    def _apply_filters(self):
        """Apply filters to the document list."""
        # Get filter values
        search_text = self.search_input.text().lower()
        doc_type_idx = self.type_combo.currentIndex()
        doc_type = self.type_combo.itemData(doc_type_idx)
        category_idx = self.category_combo.currentIndex()
        category_id = self.category_combo.itemData(category_idx)
        date_idx = self.date_combo.currentIndex()
        date_filter = self.date_combo.itemData(date_idx)

        # Filter documents
        self.filtered_documents = []
        for document in self.documents:
            # Check search filter
            if search_text and search_text not in document.name.lower():
                if not document.content or search_text not in document.content.lower():
                    continue

            # Check type filter
            if doc_type and document.file_type != doc_type:
                continue

            # Check category filter
            if category_id and document.category != category_id:
                continue

            # Check date filter
            if date_filter:
                now = datetime.now()
                if date_filter == "today":
                    if document.last_modified_date.date() != now.date():
                        continue
                elif date_filter == "week":
                    # Check if within the last 7 days
                    delta = now - document.last_modified_date
                    if delta.days > 7:
                        continue
                elif date_filter == "month":
                    # Check if same month and year
                    if (document.last_modified_date.month != now.month or
                            document.last_modified_date.year != now.year):
                        continue
                elif date_filter == "year":
                    # Check if same year
                    if document.last_modified_date.year != now.year:
                        continue

            # Document passed all filters
            self.filtered_documents.append(document)

        # Update table
        self._update_document_table()

    def _on_selection_changed(self):
        """Handle selection change in the document table."""
        selected_items = self.document_table.selectedItems()
        if not selected_items:
            self.current_document_id = None
            self._clear_document_details()
            self.export_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return

        # Get document ID from the first column
        row = selected_items[0].row()
        document_id = self.document_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.current_document_id = document_id

        # Enable buttons
        self.export_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

        # Load document details
        self._load_document_details(document_id)

    def _on_document_double_clicked(self, index):
        """Handle double-click on a document in the table.

        Args:
            index: Index of the clicked item
        """
        row = index.row()
        document_id = self.document_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self._view_document(document_id)

    def _load_document_details(self, document_id: str):
        """Load document details into the right panel.

        Args:
            document_id: Document ID
        """
        document = self.document_service.get_document(document_id)
        if not document:
            self._clear_document_details()
            return

        # Update document details
        self.doc_name_label.setText(document.name)

        # Document info
        info_text = f"Type: {document.file_type.value.upper()} | Size: {self._format_size(document.size_bytes)}"
        if document.word_count:
            info_text += f" | Words: {document.word_count}"
        if document.page_count:
            info_text += f" | Pages: {document.page_count}"
        self.doc_info_label.setText(info_text)

        # Document path
        self.doc_path_label.setText(str(document.file_path))

        # Document category
        category_name = "None"
        if document.category and document.category in self.categories:
            category_name = self.categories[document.category].name
        self.doc_category_label.setText(category_name)

        # Document metadata
        metadata_text = ""
        if document.metadata:
            for key, value in document.metadata.items():
                if value is not None:
                    metadata_text += f"{key}: {value}\n"

        if metadata_text:
            self.metadata_label.setText("Additional Metadata:\n" + metadata_text)
        else:
            self.metadata_label.setText("Additional Metadata: None")

        # Document content
        if document.content:
            # Limit preview to first 10,000 characters to avoid performance issues
            preview_text = document.content[:10000]
            if len(document.content) > 10000:
                preview_text += "\n\n[Content truncated for preview...]"
            self.content_preview.setText(preview_text)
        else:
            self.content_preview.setText("No content available for this document.")

    def _clear_document_details(self):
        """Clear document details panel."""
        self.doc_name_label.setText("")
        self.doc_info_label.setText("")
        self.doc_path_label.setText("")
        self.doc_category_label.setText("")
        self.metadata_label.setText("Additional Metadata: None")
        self.content_preview.setText("")

    def _show_context_menu(self, position):
        """Show context menu for document table.

        Args:
            position: Position where the menu should be shown
        """
        selected_items = self.document_table.selectedItems()
        if not selected_items:
            return

        # Get document ID from the first column
        row = selected_items[0].row()
        document_id = self.document_table.item(row, 0).data(Qt.ItemDataRole.UserRole)

        # Create context menu
        menu = QMenu()

        # Add actions
        view_action = QAction("View Document", self)
        view_action.triggered.connect(lambda: self._view_document(document_id))
        menu.addAction(view_action)

        export_action = QAction("Export Document", self)
        export_action.triggered.connect(lambda: self._export_document(document_id))
        menu.addAction(export_action)

        delete_action = QAction("Delete Document", self)
        delete_action.triggered.connect(lambda: self._delete_document(document_id))
        menu.addAction(delete_action)

        # Show menu
        menu.exec(self.document_table.mapToGlobal(position))

    def _view_document(self, document_id: str = None):
        """View document details in a separate dialog.

        Args:
            document_id: Document ID, uses current selection if None
        """
        if document_id is None:
            document_id = self.current_document_id

        if not document_id:
            return

        # Emit signal to open document viewer
        self.document_selected.emit(document_id)

    def _export_document(self, document_id: str = None):
        """Export document to a file.

        Args:
            document_id: Document ID, uses current selection if None
        """
        if document_id is None:
            document_id = self.current_document_id

        if not document_id:
            return

        document = self.document_service.get_document(document_id)
        if not document:
            MessageBox.error(self, "Error", "Document not found.")
            return

        # Check if original file exists
        if not document.file_path.exists():
            MessageBox.error(
                self, "Error", "Original document file not found."
            )
            return

        # Ask for destination
        file_name = document.name
        if not file_name.endswith(f".{document.file_type.value}"):
            file_name += f".{document.file_type.value}"

        destination, _ = QFileDialog.getSaveFileName(
            self,
            "Export Document",
            file_name,
            f"{document.file_type.value.upper()} Files (*.{document.file_type.value})",
        )

        if not destination:
            return

        try:
            # Copy file to destination
            import shutil
            shutil.copy2(document.file_path, destination)
            MessageBox.information(
                self, "Success", f"Document exported to {destination}"
            )
        except Exception as e:
            logger.error(f"Error exporting document: {e}")
            MessageBox.error(
                self, "Error", f"Failed to export document: {str(e)}"
            )

    def _delete_document(self, document_id: str = None):
        """Delete document from the database.

        Args:
            document_id: Document ID, uses current selection if None
        """
        if document_id is None:
            document_id = self.current_document_id

        if not document_id:
            return

        document = self.document_service.get_document(document_id)
        if not document:
            MessageBox.error(self, "Error", "Document not found.")
            return

        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{document.name}'?\n\n"
            "This will remove the document from the database and delete the file.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        # Delete document
        if self.document_service.delete_document(document_id):
            # Refresh document list
            self._refresh()
            MessageBox.information(
                self, "Success", "Document deleted successfully."
            )
        else:
            MessageBox.error(
                self, "Error", "Failed to delete document."
            )

    def _refresh(self):
        """Refresh document list and categories."""
        self._load_documents()
        self._load_categories()
        self._apply_filters()

        # Clear selection
        self.document_table.clearSelection()
        self.current_document_id = None
        self._clear_document_details()
        self.export_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
