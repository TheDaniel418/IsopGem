"""
@file unicode_text_widget.py
@description Unicode-aware text widgets for proper script display
@author Assistant
@created 2024-01-20
@lastModified 2024-01-20
@dependencies PyQt6, shared.ui.utils.font_manager
"""


from loguru import logger
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QLineEdit, QTextEdit

from shared.ui.utils.font_manager import get_font_manager


class UnicodeLabel(QLabel):
    """Label widget with automatic Unicode font selection."""

    def __init__(self, text: str = "", parent=None):
        """Initialize the Unicode label.

        Args:
            text: Initial text to display
            parent: Parent widget
        """
        super().__init__(text, parent)
        self._font_manager = get_font_manager()
        self._base_size = 12
        self._base_weight = QFont.Weight.Normal

        # Apply appropriate font for the initial text
        if text:
            self._update_font_for_text(text)

    def setText(self, text: str):
        """Set text and update font accordingly.

        Args:
            text: Text to display
        """
        super().setText(text)
        self._update_font_for_text(text)

    def setFontSize(self, size: int):
        """Set the base font size.

        Args:
            size: Font size in points
        """
        self._base_size = size
        self._update_font_for_text(self.text())

    def setFontWeight(self, weight: QFont.Weight):
        """Set the base font weight.

        Args:
            weight: Font weight
        """
        self._base_weight = weight
        self._update_font_for_text(self.text())

    def _update_font_for_text(self, text: str):
        """Update font based on text content.

        Args:
            text: Text to analyze for font selection
        """
        try:
            if text:
                font = self._font_manager.get_font_for_text(
                    text, self._base_size, self._base_weight
                )
                self.setFont(font)
                logger.debug(f"Applied font '{font.family()}' to UnicodeLabel")
        except Exception as e:
            logger.error(f"Error updating font for UnicodeLabel: {e}")


class UnicodeTextEdit(QTextEdit):
    """Text edit widget with automatic Unicode font selection."""

    def __init__(self, parent=None):
        """Initialize the Unicode text edit.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._font_manager = get_font_manager()
        self._base_size = 12
        self._base_weight = QFont.Weight.Normal

        # Set initial universal font
        self._apply_universal_font()

        # Connect to text changes to update font as needed
        self.textChanged.connect(self._on_text_changed)

    def setPlainText(self, text: str):
        """Set plain text and update font accordingly.

        Args:
            text: Text to display
        """
        super().setPlainText(text)
        self._update_font_for_text(text)

    def setHtml(self, html: str):
        """Set HTML content and update font accordingly.

        Args:
            html: HTML content to display
        """
        super().setHtml(html)
        # Extract plain text for font analysis
        plain_text = self.toPlainText()
        self._update_font_for_text(plain_text)

    def insertPlainText(self, text: str):
        """Insert plain text with appropriate font.

        Args:
            text: Text to insert
        """
        # Get font for the new text
        font = self._font_manager.get_font_for_text(
            text, self._base_size, self._base_weight
        )

        # Apply font to current cursor position
        cursor = self.textCursor()
        char_format = cursor.charFormat()
        char_format.setFont(font)
        cursor.setCharFormat(char_format)

        # Insert the text
        cursor.insertText(text)

    def setFontSize(self, size: int):
        """Set the base font size.

        Args:
            size: Font size in points
        """
        self._base_size = size
        self._update_font_for_text(self.toPlainText())

    def setFontWeight(self, weight: QFont.Weight):
        """Set the base font weight.

        Args:
            weight: Font weight
        """
        self._base_weight = weight
        self._update_font_for_text(self.toPlainText())

    def _apply_universal_font(self):
        """Apply a universal Unicode font."""
        try:
            font = self._font_manager.get_mixed_script_font(
                self._base_size, self._base_weight
            )
            self.setFont(font)
            logger.debug(f"Applied universal font '{font.family()}' to UnicodeTextEdit")
        except Exception as e:
            logger.error(f"Error applying universal font to UnicodeTextEdit: {e}")

    def _update_font_for_text(self, text: str):
        """Update font based on text content.

        Args:
            text: Text to analyze for font selection
        """
        try:
            if text:
                font = self._font_manager.get_font_for_text(
                    text, self._base_size, self._base_weight
                )
                self.setFont(font)
                logger.debug(f"Applied font '{font.family()}' to UnicodeTextEdit")
            else:
                self._apply_universal_font()
        except Exception as e:
            logger.error(f"Error updating font for UnicodeTextEdit: {e}")

    def _on_text_changed(self):
        """Handle text changes to update font if needed."""
        # Only update font if there's significant text change
        text = self.toPlainText()
        if len(text) > 10:  # Only check for longer texts to avoid constant updates
            current_font = self.font()
            new_font = self._font_manager.get_font_for_text(
                text, self._base_size, self._base_weight
            )

            # Only update if font family changes
            if current_font.family() != new_font.family():
                self.setFont(new_font)
                logger.debug(
                    f"Updated font from '{current_font.family()}' to '{new_font.family()}'"
                )


class UnicodeLineEdit(QLineEdit):
    """Line edit widget with automatic Unicode font selection."""

    def __init__(self, text: str = "", parent=None):
        """Initialize the Unicode line edit.

        Args:
            text: Initial text to display
            parent: Parent widget
        """
        super().__init__(text, parent)
        self._font_manager = get_font_manager()
        self._base_size = 12
        self._base_weight = QFont.Weight.Normal

        # Apply appropriate font for the initial text
        if text:
            self._update_font_for_text(text)
        else:
            self._apply_universal_font()

        # Connect to text changes
        self.textChanged.connect(self._on_text_changed)

    def setText(self, text: str):
        """Set text and update font accordingly.

        Args:
            text: Text to display
        """
        super().setText(text)
        self._update_font_for_text(text)

    def setFontSize(self, size: int):
        """Set the base font size.

        Args:
            size: Font size in points
        """
        self._base_size = size
        self._update_font_for_text(self.text())

    def setFontWeight(self, weight: QFont.Weight):
        """Set the base font weight.

        Args:
            weight: Font weight
        """
        self._base_weight = weight
        self._update_font_for_text(self.text())

    def _apply_universal_font(self):
        """Apply a universal Unicode font."""
        try:
            font = self._font_manager.get_mixed_script_font(
                self._base_size, self._base_weight
            )
            self.setFont(font)
            logger.debug(f"Applied universal font '{font.family()}' to UnicodeLineEdit")
        except Exception as e:
            logger.error(f"Error applying universal font to UnicodeLineEdit: {e}")

    def _update_font_for_text(self, text: str):
        """Update font based on text content.

        Args:
            text: Text to analyze for font selection
        """
        try:
            if text:
                font = self._font_manager.get_font_for_text(
                    text, self._base_size, self._base_weight
                )
                self.setFont(font)
                logger.debug(f"Applied font '{font.family()}' to UnicodeLineEdit")
            else:
                self._apply_universal_font()
        except Exception as e:
            logger.error(f"Error updating font for UnicodeLineEdit: {e}")

    def _on_text_changed(self, text: str):
        """Handle text changes to update font if needed.

        Args:
            text: New text content
        """
        if len(text) > 5:  # Only check for longer texts
            current_font = self.font()
            new_font = self._font_manager.get_font_for_text(
                text, self._base_size, self._base_weight
            )

            # Only update if font family changes
            if current_font.family() != new_font.family():
                self.setFont(new_font)
                logger.debug(
                    f"Updated font from '{current_font.family()}' to '{new_font.family()}'"
                )


class UnicodeDisplayWidget:
    """Utility class for applying Unicode fonts to existing widgets."""

    @staticmethod
    def apply_unicode_font(
        widget,
        text: str = "",
        size: int = 12,
        weight: QFont.Weight = QFont.Weight.Normal,
    ):
        """Apply appropriate Unicode font to any widget.

        Args:
            widget: Qt widget to apply font to
            text: Text that will be displayed (for script detection)
            size: Font size in points
            weight: Font weight
        """
        font_manager = get_font_manager()
        font_manager.apply_unicode_font_to_widget(widget, text, size, weight)

    @staticmethod
    def detect_and_apply_font(widget, text: str):
        """Detect text script and apply appropriate font.

        Args:
            widget: Qt widget to apply font to
            text: Text to analyze and display
        """
        font_manager = get_font_manager()
        script = font_manager.detect_text_script(text)

        # Get current font size and weight
        current_font = widget.font()
        size = current_font.pointSize() if current_font.pointSize() > 0 else 12
        weight = current_font.weight()

        # Apply script-specific font
        if script == "mixed":
            font = font_manager.get_mixed_script_font(size, weight)
        else:
            font = font_manager.get_best_font_for_script(script, size, weight)

        widget.setFont(font)
        logger.info(f"Applied {script} font '{font.family()}' to widget")

    @staticmethod
    def get_script_info(text: str) -> dict:
        """Get information about the scripts used in text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with script information
        """
        font_manager = get_font_manager()
        script = font_manager.detect_text_script(text)

        return {
            "primary_script": script,
            "available_fonts": font_manager.get_available_fonts_for_script(script),
            "recommended_font": font_manager.get_best_font_for_script(script).family(),
        }
