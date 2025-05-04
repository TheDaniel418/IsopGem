"""
Purpose: Provides a UI panel for database maintenance tasks.

This file is part of the document_manager pillar and serves as a UI component.
It provides tools for database maintenance, including statistics, optimization,
purging, duplicate detection, and individual document deletion.

Key components:
- DocumentDatabaseUtilityPanel: Panel for database maintenance tasks

Dependencies:
- PyQt6: For UI components
- document_manager.services.document_service: For document operations
- document_manager.repositories.document_repository: For direct database access
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from document_manager.models.document import Document
from document_manager.repositories.document_repository import DocumentRepository
from document_manager.services.document_service import DocumentService
from shared.ui.components.message_box import MessageBox


class DocumentDatabaseUtilityPanel(QWidget):
    """Panel for database maintenance tasks."""

    def __init__(self, parent=None):
        """Initialize the document database utility panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Document Database Utility")

        # Create services and repositories
        self.document_service = DocumentService()
        self.document_repository = DocumentRepository()

        # Initialize UI
        self._init_ui()

        # Load initial statistics
        self._load_database_statistics()

    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title and description
        title_label = QLabel("Document Database Utility")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        main_layout.addWidget(title_label)

        description_label = QLabel(
            "Manage and maintain the document database. View statistics, optimize performance, "
            "find duplicates, and perform database maintenance tasks."
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 10pt; margin-bottom: 10px;")
        main_layout.addWidget(description_label)

        # Create a scroll area for the content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        # Create a widget to hold all the content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)

        # Database Statistics Section
        stats_group = QGroupBox("Database Statistics")
        stats_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        stats_layout = QVBoxLayout(stats_group)

        # Statistics content
        self.stats_content = QLabel("Loading statistics...")
        self.stats_content.setStyleSheet("padding: 10px;")
        self.stats_content.setWordWrap(True)
        stats_layout.addWidget(self.stats_content)

        # Refresh button
        refresh_btn = QPushButton("Refresh Statistics")
        refresh_btn.clicked.connect(self._load_database_statistics)
        stats_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)

        content_layout.addWidget(stats_group)

        # Database Optimization Section
        optimize_group = QGroupBox("Database Optimization")
        optimize_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        optimize_layout = QVBoxLayout(optimize_group)

        optimize_description = QLabel(
            "Optimize the database to improve performance and reduce file size. "
            "This process will vacuum the SQLite database, rebuild indexes, and "
            "perform other optimization tasks."
        )
        optimize_description.setWordWrap(True)
        optimize_layout.addWidget(optimize_description)

        optimize_btn = QPushButton("Optimize Database")
        optimize_btn.clicked.connect(self._optimize_database)
        optimize_layout.addWidget(optimize_btn, alignment=Qt.AlignmentFlag.AlignRight)

        content_layout.addWidget(optimize_group)

        # Database Purge Section
        purge_group = QGroupBox("Database Purge")
        purge_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        purge_layout = QVBoxLayout(purge_group)

        purge_description = QLabel(
            "Purge the entire database to start fresh. This will delete all documents, "
            "categories, and related data from the database. This action cannot be undone."
        )
        purge_description.setWordWrap(True)
        purge_description.setStyleSheet("color: #c0392b;")
        purge_layout.addWidget(purge_description)

        purge_btn = QPushButton("Purge Database")
        purge_btn.setStyleSheet("background-color: #c0392b; color: white;")
        purge_btn.clicked.connect(self._purge_database)
        purge_layout.addWidget(purge_btn, alignment=Qt.AlignmentFlag.AlignRight)

        content_layout.addWidget(purge_group)

        # Duplicate Detection Section
        duplicate_group = QGroupBox("Duplicate Detection")
        duplicate_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        duplicate_layout = QVBoxLayout(duplicate_group)

        duplicate_description = QLabel(
            "Find and manage duplicate documents in the database. This will identify documents "
            "with the same name, content, or checksum and allow you to delete duplicates."
        )
        duplicate_description.setWordWrap(True)
        duplicate_layout.addWidget(duplicate_description)

        duplicate_btn = QPushButton("Find Duplicates")
        duplicate_btn.clicked.connect(self._find_duplicates)
        duplicate_layout.addWidget(duplicate_btn, alignment=Qt.AlignmentFlag.AlignRight)

        content_layout.addWidget(duplicate_group)

        # Add the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

    def _load_database_statistics(self):
        """Load and display database statistics."""
        try:
            # Get document count
            documents = self.document_service.get_all_documents()
            document_count = len(documents)

            # Calculate total size of documents
            total_size_bytes = sum(doc.size_bytes for doc in documents)

            # Count document types
            doc_types = {}
            for doc in documents:
                doc_type = doc.file_type.value.upper()
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

            # Get database file size
            db_path = self.document_repository.db_path
            db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0

            # Get storage directory size
            storage_dir = self.document_repository.storage_dir
            storage_size_bytes = self._get_directory_size(storage_dir)

            # Format statistics text
            stats_text = f"<b>Document Count:</b> {document_count}<br><br>"
            stats_text += f"<b>Total Document Size:</b> {self._format_size(total_size_bytes)}<br><br>"
            stats_text += f"<b>Database File Size:</b> {self._format_size(db_size_bytes)}<br><br>"
            stats_text += f"<b>Storage Directory Size:</b> {self._format_size(storage_size_bytes)}<br><br>"

            if doc_types:
                stats_text += "<b>Document Types:</b><br>"
                for doc_type, count in sorted(doc_types.items()):
                    stats_text += f"&nbsp;&nbsp;• {doc_type}: {count}<br>"

            self.stats_content.setText(stats_text)

        except Exception as e:
            logger.error(f"Error loading database statistics: {e}")
            self.stats_content.setText(f"Error loading statistics: {str(e)}")

    def _get_directory_size(self, directory: Path) -> int:
        """Calculate the total size of a directory.

        Args:
            directory: Directory path

        Returns:
            Total size in bytes
        """
        total_size = 0
        if not directory.exists():
            return total_size

        for path in directory.glob('**/*'):
            if path.is_file():
                total_size += path.stat().st_size

        return total_size

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

    def _optimize_database(self):
        """Optimize the database to improve performance."""
        try:
            # Confirm optimization
            result = QMessageBox.question(
                self,
                "Confirm Optimization",
                "Are you sure you want to optimize the database? This may take a moment.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if result != QMessageBox.StandardButton.Yes:
                return

            # Get database connection
            conn = sqlite3.connect(self.document_repository.db_path)
            cursor = conn.cursor()

            # Run VACUUM to rebuild the database file
            cursor.execute("VACUUM")

            # Analyze tables for query optimization
            cursor.execute("ANALYZE")

            # Rebuild indexes
            cursor.execute("REINDEX")

            # Close connection
            conn.close()

            # Refresh statistics
            self._load_database_statistics()

            MessageBox.information(
                self, "Success", "Database optimization completed successfully."
            )

        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            MessageBox.error(
                self, "Error", f"Failed to optimize database: {str(e)}"
            )

    def _purge_database(self):
        """Purge the entire database to start fresh."""
        try:
            # Confirm purge with multiple warnings
            result = QMessageBox.question(
                self,
                "Confirm Database Purge",
                "WARNING: This will delete ALL documents and categories from the database.\n\n"
                "This action CANNOT be undone. All document files will also be deleted.\n\n"
                "Are you absolutely sure you want to proceed?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if result != QMessageBox.StandardButton.Yes:
                return

            # Double-check with a second confirmation
            result = QMessageBox.question(
                self,
                "Final Confirmation",
                "This is your last chance to cancel.\n\n"
                "Proceeding will permanently delete ALL documents and data.\n\n"
                "Are you absolutely sure?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if result != QMessageBox.StandardButton.Yes:
                return

            # Get all documents to delete their files
            documents = self.document_service.get_all_documents()

            # Delete document files
            for document in documents:
                try:
                    if document.file_path.exists():
                        os.remove(document.file_path)
                except Exception as e:
                    logger.error(f"Error deleting file {document.file_path}: {e}")

            # Get database connection
            conn = sqlite3.connect(self.document_repository.db_path)
            cursor = conn.cursor()

            # Delete all data from tables
            cursor.execute("DELETE FROM documents")
            cursor.execute("DELETE FROM document_categories")

            # Commit changes
            conn.commit()
            conn.close()

            # Optimize database after purge
            self._optimize_database()

            # Refresh statistics
            self._load_database_statistics()

            MessageBox.information(
                self, "Success", "Database purged successfully. All documents have been deleted."
            )

        except Exception as e:
            logger.error(f"Error purging database: {e}")
            MessageBox.error(
                self, "Error", f"Failed to purge database: {str(e)}"
            )

    def _find_duplicates(self):
        """Find and manage duplicate documents in the database."""
        try:
            # Get all documents
            documents = self.document_service.get_all_documents()

            # Find duplicates by name
            name_duplicates = self._find_duplicates_by_name(documents)

            # Find duplicates by content hash (if content is available)
            content_duplicates = self._find_duplicates_by_content(documents)

            # If no duplicates found
            if not name_duplicates and not content_duplicates:
                MessageBox.information(
                    self, "No Duplicates", "No duplicate documents were found in the database."
                )
                return

            # Show duplicates in a dialog
            from document_manager.ui.dialogs.duplicate_documents_dialog import DuplicateDocumentsDialog
            dialog = DuplicateDocumentsDialog(name_duplicates, content_duplicates, self)
            dialog.exec()

            # Refresh statistics after potential deletions
            self._load_database_statistics()

        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            MessageBox.error(
                self, "Error", f"Failed to find duplicates: {str(e)}"
            )

    def _find_duplicates_by_name(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """Find documents with duplicate names.

        Args:
            documents: List of documents to check

        Returns:
            Dictionary mapping names to lists of documents with that name
        """
        name_map = {}
        duplicates = {}

        for doc in documents:
            if doc.name in name_map:
                name_map[doc.name].append(doc)
                # If this is the second document with this name, add to duplicates
                if len(name_map[doc.name]) == 2:
                    duplicates[doc.name] = name_map[doc.name]
            else:
                name_map[doc.name] = [doc]

        return duplicates

    def _find_duplicates_by_content(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """Find documents with duplicate content.

        Args:
            documents: List of documents to check

        Returns:
            Dictionary mapping content hashes to lists of documents with that content
        """
        import hashlib

        content_map = {}
        duplicates = {}

        for doc in documents:
            # Skip documents without content
            if not doc.content:
                continue

            # Create a hash of the content
            content_hash = hashlib.md5(doc.content.encode()).hexdigest()

            if content_hash in content_map:
                content_map[content_hash].append(doc)
                # If this is the second document with this content, add to duplicates
                if len(content_map[content_hash]) == 2:
                    duplicates[content_hash] = content_map[content_hash]
            else:
                content_map[content_hash] = [doc]

        return duplicates
