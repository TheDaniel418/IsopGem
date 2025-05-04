"""
@file rich_text_editor_widget.py
@description Embeddable rich text editor widget for use in both standalone and embedded contexts.
@author Daniel
@created 2024-06-11
@lastModified 2024-06-11
@dependencies PyQt6

A QWidget-based rich text editor with formatting toolbar and HTML content support.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QToolBar
from PyQt6.QtGui import QAction, QIcon, QTextCharFormat, QTextCursor
from PyQt6.QtCore import pyqtSignal

class RichTextEditorWidget(QWidget):
    """
    @class RichTextEditorWidget
    @description Embeddable rich text editor with formatting toolbar and HTML support.
    """
    content_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.toolbar = QToolBar("Formatting")
        self.text_edit = QTextEdit(self)
        self.text_edit.textChanged.connect(self.content_changed.emit)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.text_edit)
        self._add_formatting_actions()
        self.setLayout(layout)

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
        fmt = QTextCharFormat()
        fmt.setFontWeight(75 if not self.text_edit.fontWeight() == 75 else 50)
        self._merge_format_on_selection(fmt)

    def _toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.text_edit.fontItalic())
        self._merge_format_on_selection(fmt)

    def _toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.text_edit.fontUnderline())
        self._merge_format_on_selection(fmt)

    def _merge_format_on_selection(self, fmt):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.text_edit.mergeCurrentCharFormat(fmt)

    def set_html(self, html: str):
        self.text_edit.setHtml(html)

    def to_html(self) -> str:
        return self.text_edit.toHtml()

    def set_plain_text(self, text: str):
        self.text_edit.setPlainText(text)

    def to_plain_text(self) -> str:
        return self.text_edit.toPlainText() 