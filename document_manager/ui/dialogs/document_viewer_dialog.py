"""
Purpose: Provides a dialog for viewing document content and metadata.

This file is part of the document_manager pillar and serves as a UI component.
It displays document content, metadata, and extracted text for different document types.

Key components:
- DocumentViewerDialog: Dialog for viewing document content and metadata

Dependencies:
- PyQt6: For UI components
- document_manager.models.document: For Document model
- document_manager.services.document_service: For document operations
- document_manager.services.category_service: For category operations
"""

import os
import subprocess
from typing import Any, Optional

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from document_manager.services.category_service import CategoryService
from document_manager.services.document_service import DocumentService
from shared.ui.components.message_box import MessageBox
from shared.ui.widgets.unicode_text_widget import UnicodeLabel, UnicodeTextEdit


class DocumentViewerDialog(QDialog):
    """Dialog for viewing document content and metadata."""

    def __init__(self, document_id: str, parent=None):
        """Initialize the document viewer dialog.

        Args:
            document_id: ID of the document to view
            parent: Parent widget
        """
        super().__init__(parent)

        # Services
        self.document_service = DocumentService()
        self.category_service = CategoryService()

        # Load document
        self.document = self.document_service.get_document(document_id)
        if not self.document:
            logger.error(f"Document not found: {document_id}")
            self.close()
            return

        # Dialog setup
        self.setWindowTitle(f"Document: {self.document.name}")
        self.resize(900, 700)

        # UI setup
        self._init_ui()

        # Load content
        self._load_document_content()
        self._load_metadata()

    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout()

        # Document title
        title_layout = QHBoxLayout()

        title_label = UnicodeLabel(
            self.document.name if self.document else "Document Not Found"
        )
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)

        # Spacer
        title_layout.addStretch()

        # Open button (opens in external program)
        self.open_ext_btn = QPushButton("Open in External Program")
        self.open_ext_btn.setIcon(QIcon.fromTheme("document-open"))
        self.open_ext_btn.clicked.connect(self._open_in_external_program)
        title_layout.addWidget(self.open_ext_btn)

        main_layout.addLayout(title_layout)

        # Main splitter (metadata and content)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Metadata
        metadata_widget = QWidget()
        metadata_layout = QVBoxLayout(metadata_widget)

        metadata_label = UnicodeLabel("Document Metadata")
        metadata_label.setStyleSheet("font-weight: bold")
        metadata_layout.addWidget(metadata_label)

        self.metadata_tree = QTreeWidget()
        self.metadata_tree.setHeaderLabels(["Property", "Value"])
        self.metadata_tree.setColumnWidth(0, 200)
        metadata_layout.addWidget(self.metadata_tree)

        splitter.addWidget(metadata_widget)

        # Right side: Content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        content_label = UnicodeLabel("Content")
        content_label.setStyleSheet("font-weight: bold")
        content_layout.addWidget(content_label)

        # Content tabs
        self.content_tabs = QTabWidget()

        # Text content tab
        self.text_content = UnicodeTextEdit()
        self.text_content.setReadOnly(True)
        self.text_content.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.content_tabs.addTab(self.text_content, "Text")

        # Preview tab will be added based on file type

        content_layout.addWidget(self.content_tabs)

        splitter.addWidget(content_widget)

        # Set initial splitter sizes (1:2 ratio)
        splitter.setSizes([300, 600])

        main_layout.addWidget(splitter)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _load_document_content(self):
        """Load document content into the viewer."""
        # Check if document is None
        if not self.document:
            self.text_content.setText("No document loaded.")
            return

        # Check if document exists
        if not os.path.exists(self.document.file_path):
            self.text_content.setText("Document file not found.")
            return

        # Load text content
        if self.document.content:
            self.text_content.setText(self.document.content)
        else:
            # Try to extract text
            if self.document_service.extract_text(self.document):
                # Reload document to get updated content
                updated_doc = self.document_service.get_document(self.document.id)
                if updated_doc and updated_doc.content:
                    self.document = updated_doc
                    self.text_content.setText(self.document.content or "")
                else:
                    self.text_content.setText(
                        "No text content available for this document."
                    )
            else:
                self.text_content.setText(
                    "Failed to extract text from this document type."
                )

    def _load_metadata(self) -> None:
        """Load document metadata into the metadata tree."""
        # Clear existing items
        self.metadata_tree.clear()

        # Check if document is None
        if not self.document:
            return

        # File information
        self._add_metadata_item("Name", self.document.name, "File Information")
        self._add_metadata_item(
            "Type", self.document.file_type.value.upper(), "File Information"
        )
        self._add_metadata_item(
            "Size", self.document.get_file_size_display(), "File Information"
        )
        self._add_metadata_item(
            "Path", str(self.document.file_path), "File Information"
        )

        # Dates
        if self.document.creation_date:
            creation_date = self.document.creation_date.strftime("%Y-%m-%d %H:%M:%S")
            self._add_metadata_item("Created", creation_date, "Dates")

        if self.document.last_modified_date:
            modified_date = self.document.last_modified_date.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self._add_metadata_item("Modified", modified_date, "Dates")

        # Organization
        if self.document.category:
            # Safe handling of category
            try:
                category = self.category_service.get_category(self.document.category)
                if category:
                    self._add_metadata_item("Category", category.name, "Organization")
            except Exception as e:
                logger.warning(f"Error loading category: {e}")

        # Tags
        if self.document.tags:
            tags_str = ", ".join(self.document.tags)
            self._add_metadata_item("Tags", tags_str, "Organization")

        # Document details
        if self.document.page_count:
            self._add_metadata_item(
                "Pages", str(self.document.page_count), "Document Details"
            )

        if self.document.word_count:
            self._add_metadata_item(
                "Words", str(self.document.word_count), "Document Details"
            )

        # Additional metadata from the metadata dictionary
        if self.document.metadata:
            for key, value in self.document.metadata.items():
                if value is not None:
                    self._add_metadata_item(
                        key.capitalize(), str(value), "Additional Metadata"
                    )

    def _add_metadata_item(
        self, name: str, value: Optional[Any], parent_name: Optional[str] = None
    ) -> None:
        """Add a metadata item to the tree.

        Args:
            name: Item name
            value: Item value
            parent_name: Name of parent group
        """
        # Ensure value is a string
        value_str = str(value) if value is not None else ""

        if parent_name:
            # Find or create parent item
            parent_items = self.metadata_tree.findItems(
                parent_name, Qt.MatchFlag.MatchExactly, 0
            )

            if parent_items:
                parent = parent_items[0]
            else:
                parent = QTreeWidgetItem(self.metadata_tree)
                parent.setText(0, parent_name)
                parent.setExpanded(True)

            # Create child item
            item = QTreeWidgetItem(parent)
            item.setText(0, name)
            item.setText(1, value_str)
        else:
            # Create root item
            item = QTreeWidgetItem(self.metadata_tree)
            item.setText(0, name)
            item.setText(1, value_str)

    def _open_in_external_program(self):
        """Open the document in an external program."""
        if not self.document:
            MessageBox.error(self, "No Document", "No document is currently loaded.")
            return

        if not os.path.exists(self.document.file_path):
            MessageBox.error(
                self, "File Not Found", "The document file could not be found."
            )
            return

        try:
            # Use platform-specific commands to open file
            file_path_str = str(self.document.file_path)
            if os.name == "nt":  # Windows
                subprocess.Popen(["start", "", file_path_str], shell=True)
            elif os.name == "posix":  # Linux, macOS
                subprocess.run(["xdg-open", file_path_str], check=True)

            logger.info(f"Opened document in external program: {file_path_str}")
        except Exception as e:
            logger.error(f"Error opening document: {e}")
            MessageBox.error(
                self,
                "Open Failed",
                f"Failed to open the document in an external program: {str(e)}",
            )
