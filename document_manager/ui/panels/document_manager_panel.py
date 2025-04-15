"""
Purpose: Provides the main document manager panel for the application.

This file is part of the document_manager pillar and serves as a UI component.
It integrates document browsing, viewing, and category management into a single panel.

Key components:
- DocumentManagerPanel: Main panel for the document manager functionality

Dependencies:
- PyQt6: For UI components
- document_manager.ui.panels.document_browser_panel: For document browsing
- document_manager.ui.dialogs: For document viewers and category management
"""

from typing import Optional

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from document_manager.ui.dialogs.category_manager_dialog import CategoryManagerDialog
from document_manager.ui.dialogs.document_viewer_dialog import DocumentViewerDialog
from document_manager.ui.panels.document_browser_panel import DocumentBrowserPanel


class DocumentManagerPanel(QWidget):
    """Main panel for document management functionality."""

    def __init__(self, parent=None):
        """Initialize the document manager panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Set up UI
        self._init_ui()

        # Connect signals
        self._connect_signals()

    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout()

        # Toolbar
        toolbar_layout = QHBoxLayout()

        # Categories button
        self.categories_btn = QPushButton("Manage Categories")
        self.categories_btn.setIcon(QIcon.fromTheme("folder"))
        self.categories_btn.clicked.connect(self._open_category_manager)
        toolbar_layout.addWidget(self.categories_btn)

        # Analyze button
        self.analyze_btn = QPushButton("Analyze Document")
        self.analyze_btn.setIcon(QIcon.fromTheme("edit-find"))
        self.analyze_btn.clicked.connect(self._analyze_document)
        self.analyze_btn.setEnabled(False)  # Disabled until document selected
        toolbar_layout.addWidget(self.analyze_btn)

        # Add spacer
        toolbar_layout.addStretch()

        main_layout.addLayout(toolbar_layout)

        # Document browser panel
        self.document_browser = DocumentBrowserPanel(self)
        main_layout.addWidget(self.document_browser)

        self.setLayout(main_layout)

    def _connect_signals(self):
        """Connect signals from child components."""
        self.document_browser.document_opened.connect(self._open_document)
        self.document_browser.document_selected.connect(self._view_document_details)
        # Enable analyze button when document selected
        self.document_browser.document_selected.connect(
            lambda _: self.analyze_btn.setEnabled(True)
        )

    def _open_category_manager(self):
        """Open the category manager dialog."""
        dialog = CategoryManagerDialog(self)
        if dialog.exec():
            # Refresh document browser if categories changed
            self.document_browser._refresh()

    def _open_document(self, document_id):
        """Open a document for viewing.

        Args:
            document_id: Document ID
        """
        dialog = DocumentViewerDialog(document_id, self)
        dialog.exec()

    def _view_document_details(self, document_id):
        """View document details.

        Args:
            document_id: Document ID
        """
        dialog = DocumentViewerDialog(document_id, self)
        dialog.exec()

        # Store the current document ID
        self.current_document_id = document_id

        # Enable the analyze button
        self.analyze_btn.setEnabled(True)

    def _analyze_document(self):
        """Open the document analysis panel for the selected document."""
        if not hasattr(self, "current_document_id") or not self.current_document_id:
            # No document selected
            return

        # Create a window for the document analysis
        from shared.utils.app import MainWindow

        main_window = self.window()
        current_parent: Optional[QWidget] = main_window

        # Find the MainWindow ancestor - safely with typing
        while current_parent and not isinstance(current_parent, MainWindow):
            parent_obj = current_parent.parent()
            if not parent_obj or not isinstance(parent_obj, QWidget):
                current_parent = None
                break
            current_parent = parent_obj

        # Check if we found a proper MainWindow with window_manager
        if current_parent and hasattr(current_parent, "window_manager"):
            # Get the window manager
            window_manager = getattr(current_parent, "window_manager")

            # Create the document analysis panel
            from document_manager.ui.panels.document_analysis_panel import (
                DocumentAnalysisPanel,
            )

            panel = DocumentAnalysisPanel()

            # Open window with the panel
            window_manager.open_window("document_analysis", panel)
            
            # Set the window title
            panel.setWindowTitle("Document Analysis")

            # Load the document
            panel.load_document(self.current_document_id)
        else:
            # Fallback to dialog approach if window manager not available
            # Create the analysis panel
            from document_manager.ui.panels.document_analysis_panel import (
                DocumentAnalysisPanel,
            )

            analysis_panel = DocumentAnalysisPanel(self)

            # Load the document
            if analysis_panel.load_document(self.current_document_id):
                # Create a dialog to display the panel
                from PyQt6.QtWidgets import QDialog

                dialog = QDialog(self)
                dialog.setWindowTitle("Document Analysis")
                dialog.resize(1000, 700)

                # Set the panel as the dialog's content
                layout = QVBoxLayout(dialog)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(analysis_panel)

                # Show the dialog
                dialog.exec()
