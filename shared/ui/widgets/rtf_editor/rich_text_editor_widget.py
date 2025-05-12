"""
@file rich_text_editor_widget.py
@description Embeddable rich text editor widget for use in both standalone and embedded contexts.
@author Daniel
@created 2024-06-11
@lastModified 2024-05-05
@dependencies PyQt6

A QWidget-based rich text editor with formatting toolbar and HTML content support.
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QTextEdit, QToolBar, QVBoxLayout, QWidget

# Import for type checking only
from shared.ui.widgets.rtf_editor.utils import TextFormattingUtils


class RichTextEditorWidget(QWidget):  # No longer inherits from BaseRTFEditor
    """
    @class RichTextEditorWidget
    @description Embeddable rich text editor with formatting toolbar and HTML support.

    This is a lightweight widget that can be embedded in other widgets or windows.
    It provides basic text editing capabilities with a simple formatting toolbar.
    It implements the BaseRTFEditor protocol for consistent API across different
    editor implementations.
    """

    content_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._is_modified = False

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.toolbar = QToolBar("Formatting")
        self.text_edit = QTextEdit(self)
        self.text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_edit)
        self._add_formatting_actions()
        self.setLayout(layout)

    def _on_text_changed(self):
        """Handle text change events."""
        self._is_modified = True
        self.content_changed.emit()

    def _add_formatting_actions(self):
        bold_action = QAction(QIcon(), "Bold", self)
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self._toggle_bold)
        self.toolbar.addAction(bold_action)

        italic_action = QAction(QIcon(), "Italic", self)
        italic_action.setCheckable(True)
        italic_action.triggered.connect(self._toggle_italic)
        self.toolbar.addAction(italic_action)

        underline_action = QAction(QIcon(), "Underline", self)
        underline_action.setCheckable(True)
        underline_action.triggered.connect(self._toggle_underline)
        self.toolbar.addAction(underline_action)

    def _toggle_bold(self):
        TextFormattingUtils.toggle_bold(self.text_edit)

    def _toggle_italic(self):
        TextFormattingUtils.toggle_italic(self.text_edit)

    def _toggle_underline(self):
        TextFormattingUtils.toggle_underline(self.text_edit)

    # Implementation of BaseRTFEditor protocol

    def set_html(self, html: str) -> None:
        """Set the content of the editor as HTML.

        Args:
            html: HTML content to set
        """
        self.text_edit.setHtml(html)
        self._is_modified = False

    def get_html(self) -> str:
        """Get the content of the editor as HTML.

        Returns:
            HTML content as string
        """
        return self.text_edit.toHtml()

    def set_plain_text(self, text: str) -> None:
        """Set the content of the editor as plain text.

        Args:
            text: Plain text content to set
        """
        self.text_edit.setPlainText(text)
        self._is_modified = False

    def get_plain_text(self) -> str:
        """Get the content of the editor as plain text.

        Returns:
            Plain text content as string
        """
        return self.text_edit.toPlainText()

    def is_modified(self) -> bool:
        """Check if the content has been modified since last save.

        Returns:
            True if modified, False otherwise
        """
        return self._is_modified

    def set_modified(self, modified: bool = True) -> None:
        """Set the modified state.

        Args:
            modified: True to mark as modified, False otherwise
        """
        self._is_modified = modified

    def get_text_edit(self):
        """Get the QTextEdit widget.

        Returns:
            QTextEdit widget
        """
        return self.text_edit
