"""
Purpose: Provides a UI panel for browsing and managing documents.

This file is part of the document_manager pillar and serves as a UI component.
It displays documents in a filterable list with operations for viewing, editing, and managing documents.

Key components:
- DocumentBrowserPanel: Panel for browsing and managing documents

Dependencies:
- PyQt6: For UI components
- document_manager.models.document: For Document model
- document_manager.services.document_service: For document operations
- document_manager.services.category_service: For category operations
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Set, Union
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal, QModelIndex
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from loguru import logger

from document_manager.models.document import Document, DocumentType
from document_manager.services.category_service import CategoryService
from document_manager.services.document_service import DocumentService
from shared.ui.components.message_box import MessageBox
from shared.ui.widgets.panel import Panel


class BatchImportDialog(QDialog):
    """Dialog for batch importing documents with options."""
    
    def __init__(self, parent=None, categories=None):
        """Initialize the batch import dialog.
        
        Args:
            parent: Parent widget
            categories: List of category objects
        """
        super().__init__(parent)
        
        self.setWindowTitle("Batch Import Options")
        self.resize(400, 250)
        self.categories = categories or []
        
        # Initialize UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        
        # Source selection
        self.import_files_radio = QCheckBox("Import specific files")
        self.import_files_radio.setChecked(True)
        layout.addWidget(self.import_files_radio)
        
        self.import_dir_radio = QCheckBox("Import from directory")
        layout.addWidget(self.import_dir_radio)
        
        # Recursive import option
        recursive_layout = QHBoxLayout()
        recursive_layout.addSpacing(20)
        self.recursive_check = QCheckBox("Include subdirectories")
        self.recursive_check.setEnabled(False)
        recursive_layout.addWidget(self.recursive_check)
        layout.addLayout(recursive_layout)
        
        # Connect checks to enable/disable recursive option
        self.import_dir_radio.toggled.connect(self.recursive_check.setEnabled)
        
        # Category selection
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Assign category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("None", None)
        
        # Add available categories
        for category in self.categories:
            self.category_combo.addItem(category.name, category.id)
            
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)
        
        # Thread count
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("Max parallel imports:"))
        self.thread_count = QSpinBox()
        self.thread_count.setMinimum(1)
        self.thread_count.setMaximum(16)
        self.thread_count.setValue(4)
        thread_layout.addWidget(self.thread_count)
        layout.addLayout(thread_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_options(self):
        """Get the selected import options.
        
        Returns:
            Dictionary with import options
        """
        category_idx = self.category_combo.currentIndex()
        return {
            "import_files": self.import_files_radio.isChecked(),
            "import_dir": self.import_dir_radio.isChecked(),
            "recursive": self.recursive_check.isChecked(),
            "max_workers": self.thread_count.value(),
            "category_id": self.category_combo.itemData(category_idx)
        }


class DocumentBrowserPanel(Panel):
    """Panel for browsing and managing documents."""
    
    # Signals for document operations
    document_selected = pyqtSignal(str)  # Document ID
    document_opened = pyqtSignal(str)    # Document ID
    
    def __init__(self, parent=None):
        """Initialize the document browser panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__("Document Browser", parent)
        
        # Create services
        self.document_service = DocumentService()
        self.category_service = CategoryService()
        
        # Initialize UI
        self._init_ui()
        
        # Load data
        self._load_documents()
        self._load_categories()
    
    def _init_ui(self):
        """Initialize the UI components."""
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Import button
        self.import_btn = QPushButton("Import")
        self.import_btn.setIcon(QIcon.fromTheme("document-open"))
        self.import_btn.clicked.connect(self._import_document)
        toolbar_layout.addWidget(self.import_btn)
        
        # Batch Import button
        self.batch_import_btn = QPushButton("Batch Import")
        self.batch_import_btn.setIcon(QIcon.fromTheme("folder-open"))
        self.batch_import_btn.clicked.connect(self._batch_import_documents)
        toolbar_layout.addWidget(self.batch_import_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_btn.clicked.connect(self._refresh)
        toolbar_layout.addWidget(self.refresh_btn)
        
        # Spacer
        toolbar_layout.addStretch()
        
        # Search input
        toolbar_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search documents...")
        self.search_input.textChanged.connect(self._apply_filters)
        toolbar_layout.addWidget(self.search_input)
        
        self.content_layout.addLayout(toolbar_layout)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        
        # Category filter
        filter_layout.addWidget(QLabel("Category:"))
        self.category_filter = QComboBox()
        self.category_filter.currentIndexChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.category_filter)
        
        # Type filter
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types", None)
        for doc_type in DocumentType:
            self.type_filter.addItem(doc_type.name, doc_type)
        self.type_filter.currentIndexChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        self.content_layout.addLayout(filter_layout)
        
        # Document tree
        self.document_tree = QTreeWidget()
        self.document_tree.setHeaderLabels(["Name", "Type", "Size", "Modified", "Category"])
        self.document_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.document_tree.customContextMenuRequested.connect(self._show_context_menu)
        self.document_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.document_tree.setColumnWidth(0, 300)  # Name column width
        self.content_layout.addWidget(self.document_tree)
    
    def _load_documents(self):
        """Load documents from the service."""
        self.documents = self.document_service.get_all_documents()
        self._update_document_tree()
    
    def _load_categories(self):
        """Load categories for the filter dropdown."""
        # Clear existing categories
        self.category_filter.clear()
        
        # Add "All Categories" option
        self.category_filter.addItem("All Categories", None)
        
        # Add categories from service
        categories = self.category_service.get_all_categories()
        for category in categories:
            self.category_filter.addItem(category.name, category.id)
    
    def _update_document_tree(self):
        """Update the document tree with current documents."""
        # Clear current items
        self.document_tree.clear()
        
        # Apply filters (this will repopulate the tree)
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply filters to the document list."""
        # Clear current items
        self.document_tree.clear()
        
        # Get filter values
        search_text = self.search_input.text().lower()
        category_idx = self.category_filter.currentIndex()
        category_id = self.category_filter.itemData(category_idx) if category_idx > 0 else None
        type_idx = self.type_filter.currentIndex()
        doc_type = self.type_filter.itemData(type_idx) if type_idx > 0 else None
        
        # Get categories map for display
        categories = {cat.id: cat for cat in self.category_service.get_all_categories()}
        
        # Add filtered documents to tree
        for document in self.documents:
            # Check search filter
            if search_text and search_text not in document.name.lower():
                if not document.content or search_text not in document.content.lower():
                    continue
            
            # Check category filter
            if category_id and document.category != category_id:
                continue
            
            # Check type filter
            if doc_type and document.file_type != doc_type:
                continue
            
            # Create tree item
            item = QTreeWidgetItem([
                document.name,
                document.file_type.value.upper(),
                document.get_file_size_display(),
                document.last_modified_date.strftime("%Y-%m-%d %H:%M"),
            ])
            
            # Store document ID in the item
            item.setData(0, Qt.ItemDataRole.UserRole, document.id)
            
            # Get category name
            if document.category and document.category in categories:
                category_name = categories[document.category].name
            else:
                category_name = ""
            item.setText(4, category_name)
            
            # Add to tree
            self.document_tree.addTopLevelItem(item)
    
    def _refresh(self):
        """Refresh the document list."""
        self._load_documents()
        self._load_categories()
    
    def _import_document(self):
        """Import a document from file."""
        # Open file dialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        
        # Get supported file types
        supported_extensions = [f"*.{t.value}" for t in DocumentType]
        file_types = f"Documents ({' '.join(supported_extensions)})"
        
        file_paths, _ = file_dialog.getOpenFileNames(
            self, "Import Documents", "", file_types
        )
        
        if file_paths:
            imported_count = 0
            for file_path in file_paths:
                document = self.document_service.import_document(file_path)
                if document:
                    imported_count += 1
            
            # Show success message
            if imported_count > 0:
                MessageBox.information(
                    self,
                    "Import Complete",
                    f"Successfully imported {imported_count} document(s)."
                )
                
                # Refresh document list
                self._refresh()
    
    def _batch_import_documents(self):
        """Import documents in batch mode."""
        # Show batch import options dialog
        options_dialog = BatchImportDialog(self, self.category_service.get_all_categories())
        if not options_dialog.exec():
            return
        
        # Get import options
        options = options_dialog.get_options()
        max_workers = options["max_workers"]
        category_id = options["category_id"]
        
        # Determine import method
        imported_documents = []
        
        if options["import_files"]:
            # Import specific files
            file_dialog = QFileDialog()
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
            
            # Get supported file types
            supported_extensions = [f"*.{t.value}" for t in DocumentType]
            file_types = f"Documents ({' '.join(supported_extensions)})"
            
            file_paths, _ = file_dialog.getOpenFileNames(
                self, "Select Documents to Import", "", file_types
            )
            
            if file_paths:
                # Convert file paths to compatible type with explicit Union type
                from typing import Union, List
                # Create list of Union type for compatibility with DocumentService's batch_import_documents
                file_paths_compatible: List[Union[str, Path]] = [str(path) for path in file_paths]
                imported_documents = self.document_service.batch_import_documents(
                    file_paths_compatible, max_workers=max_workers, category_id=category_id
                )
        else:
            # Import from directory
            dir_dialog = QFileDialog()
            dir_dialog.setFileMode(QFileDialog.FileMode.Directory)
            dir_path = dir_dialog.getExistingDirectory(
                self, "Select Directory to Import From"
            )
            
            if dir_path:
                # Use directory import method
                recursive = options["recursive"]
                imported_documents = self.document_service.import_documents_from_directory(
                    dir_path, recursive=recursive, max_workers=max_workers, category_id=category_id
                )
        
        # Show results
        if imported_documents:
            # Show category info in message if assigned
            category_info = ""
            if category_id:
                category = next((c for c in self.category_service.get_all_categories() if c.id == category_id), None)
                if category:
                    category_info = f" and assigned to category '{category.name}'"
                
            MessageBox.information(
                self,
                "Batch Import Complete",
                f"Successfully imported {len(imported_documents)} document(s){category_info}."
            )
            
            # Refresh document list
            self._refresh()
    
    def _show_context_menu(self, position):
        """Show context menu for document operations.
        
        Args:
            position: Position where menu should appear
        """
        item = self.document_tree.itemAt(position)
        if not item:
            return
        
        # Get document ID
        document_id = item.data(0, Qt.ItemDataRole.UserRole)
        if not document_id:
            return
        
        # Create context menu
        menu = QMenu()
        
        # Add actions
        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self._open_document(document_id))
        menu.addAction(open_action)
        
        # Add Edit in RTF Editor action
        edit_rtf_action = QAction("Edit in RTF Editor", self)
        edit_rtf_action.triggered.connect(lambda: self._edit_document_in_rtf(document_id))
        menu.addAction(edit_rtf_action)
        
        view_action = QAction("View Details", self)
        view_action.triggered.connect(lambda: self._view_document(document_id))
        menu.addAction(view_action)
        
        # Category submenu
        category_menu = QMenu("Set Category", self)
        
        # Add "None" option
        none_action = QAction("None", self)
        none_action.triggered.connect(lambda: self._set_document_category(document_id, None))
        category_menu.addAction(none_action)
        
        # Add categories
        for category in self.category_service.get_all_categories():
            cat_action = QAction(category.name, self)
            cat_action.triggered.connect(
                lambda checked, cat_id=category.id: self._set_document_category(document_id, cat_id)
            )
            category_menu.addAction(cat_action)
        
        menu.addMenu(category_menu)
        
        # Delete action
        menu.addSeparator()
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self._delete_document(document_id))
        menu.addAction(delete_action)
        
        # Show menu
        menu.exec(self.document_tree.viewport().mapToGlobal(position))
    
    def _on_item_double_clicked(self, item, column):
        """Handle double-click on a document.
        
        Args:
            item: Tree item clicked
            column: Column clicked
        """
        document_id = item.data(0, Qt.ItemDataRole.UserRole)
        if document_id:
            self._open_document(document_id)
    
    def _edit_document_in_rtf(self, document_id: str):
        """Open a document in the RTF Editor for editing.
        
        Args:
            document_id: Document ID
        """
        # Import needed services and components
        from document_manager.services.qgem_document_service import QGemDocumentService
        from document_manager.models.qgem_document import QGemDocument
        from shared.ui.widgets.rtf_editor.rtf_editor_window import RTFEditorWindow
        from shared.ui.widgets.rtf_editor.models.document_format import DocumentFormat
        from loguru import logger
        
        # Get the document service to retrieve the document
        document_service = DocumentService()
        qgem_document_service = QGemDocumentService(document_service)
        
        # Try to get the document as a QGemDocument or convert it
        document = document_service.get_document(document_id)
        
        if not document:
            logger.error(f"Document not found: {document_id}")
            MessageBox.error(self, "Error", f"Document with ID {document_id} not found.")
            return
        
        # Check if document is a QGemDocument or can be converted to one
        qgem_document = None
        
        if isinstance(document, QGemDocument):
            qgem_document = document
        else:
            # Try to convert to QGemDocument if it's not already
            try:
                # Create a new QGemDocument from the existing document
                from document_manager.models.qgem_document import QGemDocumentType
                qgem_document = QGemDocument(
                    id=document.id,
                    name=document.name,
                    content=document.content or "",
                    html_content=document.content or "",  # Use plain content as HTML initially
                    creation_date=document.creation_date,
                    last_modified_date=document.last_modified_date,
                    file_path=document.file_path,
                    file_type=document.file_type,
                    category=document.category,
                    tags=document.tags,
                    metadata=document.metadata,
                    size_bytes=document.size_bytes,
                    qgem_type=QGemDocumentType.RICHTEXT
                )
                
                # Save the converted document
                success = document_service.update_document(qgem_document)
                if not success:
                    logger.error(f"Failed to convert document {document_id} to QGemDocument")
                    MessageBox.error(self, "Error", "Failed to convert document for editing.")
                    return
                    
            except Exception as e:
                logger.error(f"Error converting document to QGemDocument: {e}")
                MessageBox.error(self, "Error", f"Cannot edit this document type in RTF Editor: {e}")
                return
        
        # Get document as DocumentFormat for the RTF editor
        doc_format = None
        try:
            # First try direct conversion if it's a QGemDocument
            if qgem_document and hasattr(qgem_document, 'to_document_format'):
                doc_format = qgem_document.to_document_format()
            else:
                # Fall back to using the service
                doc_format = qgem_document_service.get_document_as_format(document_id)
            
            if not doc_format:
                logger.error(f"Failed to convert document {document_id} to DocumentFormat")
                MessageBox.error(self, "Error", "Failed to prepare document for editing.")
                return
                
        except Exception as e:
            logger.error(f"Error preparing document for RTF editor: {e}")
            MessageBox.error(self, "Error", f"Cannot open document in RTF Editor: {e}")
            return
        
        # Find the main window to get the window manager
        from shared.utils.app import MainWindow
        main_window = self.window()
        current_parent = main_window
        
        # Find the MainWindow ancestor with the window_manager
        while current_parent and not isinstance(current_parent, MainWindow):
            parent_obj = current_parent.parent()
            if not parent_obj or not isinstance(parent_obj, QWidget):
                current_parent = None
                break
            current_parent = parent_obj
            
        if not current_parent or not hasattr(current_parent, 'window_manager'):
            logger.error("Cannot find window manager to open RTF editor")
            MessageBox.error(self, "Error", "Cannot open RTF editor window.")
            return
            
        # Get the window manager
        window_manager = getattr(current_parent, 'window_manager')
            
        # Create RTF editor window
        editor = RTFEditorWindow()
        
        # Open RTF editor window
        window_manager.open_window(
            f"rtf_editor_{document_id}", 
            editor, 
            f"Editing: {document.name}"
        )
        
        # Set up a handler to save documents back to the database when editor is closed
        def on_editor_closed(window_id):
            # Only handle if this is our window being closed
            if window_id == f"rtf_editor_{document_id}":
                # Get the document from the editor and save it back to the database
                if hasattr(editor, 'document_manager') and editor.document_manager:
                    try:
                        # Get the current document from the editor
                        current_format = editor.document_manager.get_document_format()
                        if current_format:
                            # Save document back to database
                            qgem_document_service.save_document_format(current_format)
                            # Refresh document browser
                            self._refresh()
                            logger.info(f"Saved changes to document {document_id}")
                    except Exception as e:
                        logger.error(f"Error saving document changes: {e}")
        
        # Connect to window closed signal
        window_manager.window_closed.connect(on_editor_closed)
        
        # Load the document into the editor
        if hasattr(editor, 'document_manager'):
            # Load the document format into the editor
            editor.document_manager.load_document_format(doc_format)
            logger.info(f"Opened document {document_id} in RTF Editor")
        else:
            logger.error("RTF Editor instance has no document_manager attribute")
            MessageBox.error(self, "Error", "Failed to load document in RTF Editor.")
    
    def _open_document(self, document_id: str):
        """Open a document for viewing.
        
        Args:
            document_id: Document ID
        """
        self.document_opened.emit(document_id)
    
    def _view_document(self, document_id: str):
        """View document details.
        
        Args:
            document_id: Document ID
        """
        self.document_selected.emit(document_id)
    
    def _set_document_category(self, document_id: str, category_id: Optional[str]):
        """Set the category for a document.
        
        Args:
            document_id: Document ID
            category_id: Category ID, or None to clear
        """
        if self.document_service.set_document_category(document_id, category_id):
            # Refresh to update the UI
            self._refresh()
    
    def _delete_document(self, document_id: str):
        """Delete a document.
        
        Args:
            document_id: Document ID
        """
        # Get document details for confirmation
        document = self.document_service.get_document(document_id)
        if not document:
            return
        
        # Confirm with user
        result = MessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{document.name}'? This action cannot be undone."
        )
        
        if result:
            # Delete document
            if self.document_service.delete_document(document_id):
                # Refresh document list
                self._refresh()
            else:
                MessageBox.error(
                    self,
                    "Delete Failed",
                    "Failed to delete the document. Please try again."
                ) 