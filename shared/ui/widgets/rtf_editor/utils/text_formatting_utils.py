"""
@file text_formatting_utils.py
@description Shared text formatting utilities for rich text editors
@created 2024-05-05
@dependencies PyQt6

Provides common text formatting operations that can be used by both the lightweight
RichTextEditorWidget and the full-featured RTFEditorWindow.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import QTextEdit


class TextFormattingUtils:
    """Utility class for common text formatting operations."""

    @staticmethod
    def toggle_bold(editor: QTextEdit) -> QTextCharFormat:
        """Toggle bold formatting for the current selection.

        Args:
            editor: The text edit widget

        Returns:
            The applied format
        """
        format = QTextCharFormat()
        # Check current state to toggle
        current_weight = editor.fontWeight()
        format.setFontWeight(
            QFont.Weight.Normal
            if current_weight >= QFont.Weight.Bold
            else QFont.Weight.Bold
        )
        TextFormattingUtils.apply_format_to_selection(editor, format)
        return format

    @staticmethod
    def toggle_italic(editor: QTextEdit) -> QTextCharFormat:
        """Toggle italic formatting for the current selection.

        Args:
            editor: The text edit widget

        Returns:
            The applied format
        """
        format = QTextCharFormat()
        format.setFontItalic(not editor.fontItalic())
        TextFormattingUtils.apply_format_to_selection(editor, format)
        return format

    @staticmethod
    def toggle_underline(editor: QTextEdit) -> QTextCharFormat:
        """Toggle underline formatting for the current selection.

        Args:
            editor: The text edit widget

        Returns:
            The applied format
        """
        format = QTextCharFormat()
        format.setFontUnderline(not editor.fontUnderline())
        TextFormattingUtils.apply_format_to_selection(editor, format)
        return format

    @staticmethod
    def set_font_family(editor: QTextEdit, family: str) -> QTextCharFormat:
        """Set font family for the current selection.

        Args:
            editor: The text edit widget
            family: Font family name

        Returns:
            The applied format
        """
        format = QTextCharFormat()
        format.setFontFamily(family)
        TextFormattingUtils.apply_format_to_selection(editor, format)
        return format

    @staticmethod
    def set_font_size(editor: QTextEdit, size: float) -> QTextCharFormat:
        """Set font size for the current selection.

        Args:
            editor: The text edit widget
            size: Font point size

        Returns:
            The applied format
        """
        format = QTextCharFormat()
        format.setFontPointSize(size)
        TextFormattingUtils.apply_format_to_selection(editor, format)
        return format

    @staticmethod
    def set_text_color(editor: QTextEdit, color: QColor) -> QTextCharFormat:
        """Set text color for the current selection.

        Args:
            editor: The text edit widget
            color: Text color

        Returns:
            The applied format
        """
        format = QTextCharFormat()
        format.setForeground(color)
        TextFormattingUtils.apply_format_to_selection(editor, format)
        return format

    @staticmethod
    def set_text_alignment(editor: QTextEdit, alignment: Qt.AlignmentFlag) -> None:
        """Set text alignment for the current paragraph.

        Args:
            editor: The text edit widget
            alignment: Text alignment flag
        """
        cursor = editor.textCursor()
        block_format = QTextBlockFormat()
        block_format.setAlignment(alignment)
        cursor.mergeBlockFormat(block_format)
        editor.setTextCursor(cursor)

    @staticmethod
    def apply_format_to_selection(editor: QTextEdit, format: QTextCharFormat) -> None:
        """Apply format to the current selection or word under cursor.

        Args:
            editor: The text edit widget
            format: The text format to apply
        """
        cursor = editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(format)
        editor.mergeCurrentCharFormat(format)

    @staticmethod
    def get_current_format(editor: QTextEdit) -> QTextCharFormat:
        """Get the current character format at cursor position.

        Args:
            editor: The text edit widget

        Returns:
            Current text format
        """
        return editor.textCursor().charFormat()

    @staticmethod
    def get_current_block_format(editor: QTextEdit) -> QTextBlockFormat:
        """Get the current block format at cursor position.

        Args:
            editor: The text edit widget

        Returns:
            Current block format
        """
        return editor.textCursor().blockFormat()
