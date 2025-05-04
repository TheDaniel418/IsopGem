"""
Purpose: Provides a dialog for managing duplicate documents.

This file is part of the document_manager pillar and serves as a UI component.
It displays duplicate documents and allows the user to select which ones to delete.

Key components:
- DuplicateDocumentsDialog: Dialog for managing duplicate documents

Dependencies:
- PyQt6: For UI components
- document_manager.models.document: For Document model
- document_manager.services.document_service: For document operations
"""

from typing import Dict, List

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from document_manager.models.document import Document
from document_manager.services.document_service import DocumentService
from shared.ui.components.message_box import MessageBox


class DuplicateDocumentsDialog(QDialog):
    """Dialog for managing duplicate documents."""

    def __init__(
        self,
        name_duplicates: Dict[str, List[Document]],
        content_duplicates: Dict[str, List[Document]],
        parent=None
    ):
        """Initialize the duplicate documents dialog.

        Args:
            name_duplicates: Dictionary mapping names to lists of documents with that name
            content_duplicates: Dictionary mapping content hashes to lists of documents with that content
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Duplicate Documents")
        self.resize(800, 600)

        self.name_duplicates = name_duplicates
        self.content_duplicates = content_duplicates
        self.document_service = DocumentService()

        # Track selected documents for deletion
        self.documents_to_delete = set()

        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)

        # Title and description
        title_label = QLabel("Duplicate Documents")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        description_label = QLabel(
            "The following duplicate documents were found in the database. "
            "Select the documents you want to delete and click 'Delete Selected'."
        )
        description_label.setWordWrap(True)
        main_layout.addWidget(description_label)

        # Create tabs for different duplicate types
        tab_widget = QTabWidget()

        # Name duplicates tab
        name_tab = QWidget()
        name_layout = QVBoxLayout(name_tab)

        if self.name_duplicates:
            name_scroll = QScrollArea()
            name_scroll.setWidgetResizable(True)

            name_content = QWidget()
            name_content_layout = QVBoxLayout(name_content)

            for name, docs in self.name_duplicates.items():
                group = self._create_duplicate_group(name, docs, "name")
                name_content_layout.addWidget(group)

            name_content_layout.addStretch()
            name_scroll.setWidget(name_content)
            name_layout.addWidget(name_scroll)
        else:
            name_layout.addWidget(QLabel("No documents with duplicate names were found."))

        tab_widget.addTab(name_tab, f"Duplicate Names ({len(self.name_duplicates)})")

        # Content duplicates tab
        content_tab = QWidget()
        content_layout = QVBoxLayout(content_tab)

        if self.content_duplicates:
            content_scroll = QScrollArea()
            content_scroll.setWidgetResizable(True)

            content_content = QWidget()
            content_content_layout = QVBoxLayout(content_content)

            for content_hash, docs in self.content_duplicates.items():
                # Use the first document's name as the group title
                title = f"Documents with identical content: {docs[0].name}"
                group = self._create_duplicate_group(title, docs, "content")
                content_content_layout.addWidget(group)

            content_content_layout.addStretch()
            content_scroll.setWidget(content_content)
            content_layout.addWidget(content_scroll)
        else:
            content_layout.addWidget(QLabel("No documents with duplicate content were found."))

        tab_widget.addTab(content_tab, f"Duplicate Content ({len(self.content_duplicates)})")

        main_layout.addWidget(tab_widget)

        # Action buttons
        button_box = QDialogButtonBox()

        # Delete selected button
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        self.delete_btn.clicked.connect(self._delete_selected)
        button_box.addButton(self.delete_btn, QDialogButtonBox.ButtonRole.ActionRole)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_box.addButton(close_btn, QDialogButtonBox.ButtonRole.RejectRole)

        main_layout.addWidget(button_box)

    def _create_duplicate_group(self, title: str, documents: List[Document], duplicate_type: str) -> QGroupBox:
        """Create a group box for a set of duplicate documents.

        Args:
            title: Group title
            documents: List of duplicate documents
            duplicate_type: Type of duplicate ("name" or "content")

        Returns:
            Group box widget
        """
        group = QGroupBox(title)
        group_layout = QVBoxLayout(group)

        # Add a checkbox for each document
        for doc in documents:
            doc_layout = QHBoxLayout()

            # Checkbox for selection
            checkbox = QCheckBox()
            checkbox.setProperty("document_id", doc.id)
            checkbox.setProperty("duplicate_type", duplicate_type)
            checkbox.stateChanged.connect(self._on_checkbox_changed)
            doc_layout.addWidget(checkbox)

            # Document info
            info_text = (
                f"{doc.name} - {doc.file_type.value.upper()} - "
                f"{self._format_size(doc.size_bytes)} - "
                f"Last modified: {doc.last_modified_date.strftime('%Y-%m-%d %H:%M')}"
            )
            info_label = QLabel(info_text)
            info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            doc_layout.addWidget(info_label)

            group_layout.addLayout(doc_layout)

        return group

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

    def _on_checkbox_changed(self, state):
        """Handle checkbox state changes.

        Args:
            state: Checkbox state
        """
        checkbox = self.sender()
        document_id = checkbox.property("document_id")

        if state == Qt.CheckState.Checked:
            self.documents_to_delete.add(document_id)
        else:
            self.documents_to_delete.discard(document_id)

        # Update delete button state
        self.delete_btn.setEnabled(len(self.documents_to_delete) > 0)

    def _delete_selected(self):
        """Delete selected documents."""
        if not self.documents_to_delete:
            return

        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(self.documents_to_delete)} selected documents?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        # Delete documents
        success_count = 0
        error_count = 0

        for document_id in self.documents_to_delete:
            try:
                if self.document_service.delete_document(document_id):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Error deleting document {document_id}: {e}")
                error_count += 1

        # Show results
        if error_count == 0:
            MessageBox.information(
                self, "Success", f"Successfully deleted {success_count} documents."
            )
            self.accept()  # Close dialog on success
        else:
            MessageBox.warning(
                self,
                "Partial Success",
                f"Deleted {success_count} documents, but failed to delete {error_count} documents."
            )
