"""
Note Tab Widget for the Number Dictionary.

This widget provides note-taking functionality with rich text editing,
attachment management, and number linking capabilities.
"""

import os
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from gematria.models.number_note import NumberNote
from shared.ui.widgets.rtf_editor.rich_text_editor_widget import RichTextEditorWidget


class NumberLinkWidget(QWidget):
    """Widget for managing number links."""
    
    link_added = pyqtSignal(int)
    link_removed = pyqtSignal(int)
    link_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize the number link widget."""
        super().__init__(parent)
        self.linked_numbers: List[int] = []
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        layout.addWidget(QLabel("Linked Numbers:"))
        
        # Add link section
        add_layout = QHBoxLayout()
        
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Enter number to link...")
        self.number_input.setMaximumWidth(150)
        add_layout.addWidget(self.number_input)
        
        self.add_button = QPushButton("Add Link")
        self.add_button.setMaximumWidth(80)
        add_layout.addWidget(self.add_button)
        
        add_layout.addStretch()
        layout.addLayout(add_layout)
        
        # Links list
        self.links_list = QListWidget()
        self.links_list.setMaximumHeight(150)
        layout.addWidget(self.links_list)
        
        # Remove button
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setEnabled(False)
        layout.addWidget(self.remove_button)
    
    def _connect_signals(self):
        """Connect UI signals."""
        self.add_button.clicked.connect(self._on_add_link)
        self.remove_button.clicked.connect(self._on_remove_link)
        self.number_input.returnPressed.connect(self._on_add_link)
        self.links_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.links_list.itemDoubleClicked.connect(self._on_link_double_clicked)
    
    def _on_add_link(self):
        """Handle add link button click."""
        try:
            number_text = self.number_input.text().strip()
            if not number_text:
                return
            
            number = int(number_text)
            if number <= 0:
                QMessageBox.warning(self, "Invalid Number", "Please enter a positive number.")
                return
            
            if number not in self.linked_numbers:
                self.linked_numbers.append(number)
                self._update_links_list()
                self.link_added.emit(number)
                self.number_input.clear()
            else:
                QMessageBox.information(self, "Duplicate Link", f"Number {number} is already linked.")
                
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number.")
    
    def _on_remove_link(self):
        """Handle remove link button click."""
        current_item = self.links_list.currentItem()
        if current_item:
            number = int(current_item.text())
            self.linked_numbers.remove(number)
            self._update_links_list()
            self.link_removed.emit(number)
    
    def _on_selection_changed(self):
        """Handle selection change in links list."""
        self.remove_button.setEnabled(self.links_list.currentItem() is not None)
    
    def _on_link_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on a link."""
        number = int(item.text())
        self.link_clicked.emit(number)
    
    def _update_links_list(self):
        """Update the links list display."""
        self.links_list.clear()
        for number in sorted(self.linked_numbers):
            self.links_list.addItem(str(number))
    
    def set_linked_numbers(self, numbers: List[int]):
        """Set the linked numbers.
        
        Args:
            numbers: List of linked numbers
        """
        self.linked_numbers = numbers.copy()
        self._update_links_list()
    
    def get_linked_numbers(self) -> List[int]:
        """Get the current linked numbers.
        
        Returns:
            List of linked numbers
        """
        return self.linked_numbers.copy()


class AttachmentWidget(QWidget):
    """Widget for managing file attachments."""
    
    def __init__(self, parent=None):
        """Initialize the attachment widget."""
        super().__init__(parent)
        self.attachments: List[str] = []
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        layout.addWidget(QLabel("Attachments:"))
        
        # Add attachment button
        self.add_button = QPushButton("Add Attachment...")
        layout.addWidget(self.add_button)
        
        # Attachments list
        self.attachments_list = QListWidget()
        self.attachments_list.setMaximumHeight(100)
        layout.addWidget(self.attachments_list)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.open_button = QPushButton("Open")
        self.open_button.setEnabled(False)
        button_layout.addWidget(self.open_button)
        
        self.remove_button = QPushButton("Remove")
        self.remove_button.setEnabled(False)
        button_layout.addWidget(self.remove_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect UI signals."""
        self.add_button.clicked.connect(self._on_add_attachment)
        self.open_button.clicked.connect(self._on_open_attachment)
        self.remove_button.clicked.connect(self._on_remove_attachment)
        self.attachments_list.itemSelectionChanged.connect(self._on_selection_changed)
        self.attachments_list.itemDoubleClicked.connect(self._on_open_attachment)
    
    def _on_add_attachment(self):
        """Handle add attachment button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Attachment",
            "",
            "All Files (*.*)"
        )
        
        if file_path:
            if file_path not in self.attachments:
                self.attachments.append(file_path)
                self._update_attachments_list()
            else:
                QMessageBox.information(self, "Duplicate Attachment", "This file is already attached.")
    
    def _on_open_attachment(self):
        """Handle open attachment button click."""
        current_item = self.attachments_list.currentItem()
        if current_item:
            file_path = current_item.text()
            if os.path.exists(file_path):
                os.startfile(file_path)  # Windows
                # For Linux/Mac, you might want to use subprocess.run(['xdg-open', file_path])
            else:
                QMessageBox.warning(self, "File Not Found", f"The file {file_path} no longer exists.")
    
    def _on_remove_attachment(self):
        """Handle remove attachment button click."""
        current_item = self.attachments_list.currentItem()
        if current_item:
            file_path = current_item.text()
            self.attachments.remove(file_path)
            self._update_attachments_list()
    
    def _on_selection_changed(self):
        """Handle selection change in attachments list."""
        has_selection = self.attachments_list.currentItem() is not None
        self.open_button.setEnabled(has_selection)
        self.remove_button.setEnabled(has_selection)
    
    def _update_attachments_list(self):
        """Update the attachments list display."""
        self.attachments_list.clear()
        for attachment in self.attachments:
            self.attachments_list.addItem(os.path.basename(attachment))
    
    def set_attachments(self, attachments: List[str]):
        """Set the attachments.
        
        Args:
            attachments: List of attachment file paths
        """
        self.attachments = attachments.copy()
        self._update_attachments_list()
    
    def get_attachments(self) -> List[str]:
        """Get the current attachments.
        
        Returns:
            List of attachment file paths
        """
        return self.attachments.copy()


class NoteTabWidget(QWidget):
    """Tab widget for note-taking functionality."""
    
    number_link_requested = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize the note tab widget."""
        super().__init__(parent)
        
        self.current_note: Optional[NumberNote] = None
        self._is_modified = False
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Title section
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title:"))
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter note title...")
        title_layout.addWidget(self.title_edit)
        
        layout.addLayout(title_layout)
        
        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Rich text editor with enhanced features
        self.text_editor = RichTextEditorWidget(
            show_menubar=False,  # Keep clean for embedding
            show_statusbar=True,  # Show status bar for word count, etc.
            compact_mode=False   # Full toolbar for maximum functionality
        )
        splitter.addWidget(self.text_editor)
        
        # Right side: Links and attachments
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Number links
        self.link_widget = NumberLinkWidget()
        right_layout.addWidget(self.link_widget)
        
        # Attachments
        self.attachment_widget = AttachmentWidget()
        right_layout.addWidget(self.attachment_widget)
        
        right_layout.addStretch()
        splitter.addWidget(right_widget)
        
        # Set splitter proportions (70% editor, 30% sidebar)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
    
    def _connect_signals(self):
        """Connect UI signals."""
        self.title_edit.textChanged.connect(self._on_content_changed)
        self.text_editor.content_changed.connect(self._on_content_changed)
        self.link_widget.link_clicked.connect(self.number_link_requested.emit)
        self.link_widget.link_added.connect(self._on_content_changed)
        self.link_widget.link_removed.connect(self._on_content_changed)
    
    def _on_content_changed(self):
        """Handle content change."""
        self._is_modified = True
    
    def load_note(self, note: NumberNote):
        """Load a note into the widget.
        
        Args:
            note: The note to load
        """
        self.current_note = note
        
        # Load content
        self.title_edit.setText(note.title)
        self.text_editor.set_html(note.content)
        self.link_widget.set_linked_numbers(note.linked_numbers)
        self.attachment_widget.set_attachments(note.attachments)
        
        # Reset modified flag
        self._is_modified = False
    
    def get_title(self) -> str:
        """Get the current title.
        
        Returns:
            The note title
        """
        return self.title_edit.text()
    
    def get_content(self) -> str:
        """Get the current content.
        
        Returns:
            The note content as HTML
        """
        return self.text_editor.get_html()
    
    def get_linked_numbers(self) -> List[int]:
        """Get the current linked numbers.
        
        Returns:
            List of linked numbers
        """
        return self.link_widget.get_linked_numbers()
    
    def get_attachments(self) -> List[str]:
        """Get the current attachments.
        
        Returns:
            List of attachment file paths
        """
        return self.attachment_widget.get_attachments()
    
    def is_modified(self) -> bool:
        """Check if the note has been modified.
        
        Returns:
            True if modified, False otherwise
        """
        return self._is_modified
    
    def set_saved(self):
        """Mark the note as saved (not modified)."""
        self._is_modified = False

    def get_note(self) -> NumberNote:
        """Get a NumberNote object from the current widget state.
        
        Returns:
            NumberNote object with current widget data
        """
        note = NumberNote(
            title=self.get_title(),
            content=self.get_content(),
            linked_numbers=self.get_linked_numbers(),
            attachments=self.get_attachments()
        )
        
        # If we have a loaded note with an ID, preserve it
        if hasattr(self, 'current_note') and self.current_note and self.current_note.id:
            note.id = self.current_note.id
            note.created_at = self.current_note.created_at
        
        return note 