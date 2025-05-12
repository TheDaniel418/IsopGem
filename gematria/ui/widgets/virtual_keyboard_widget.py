"""
@file virtual_keyboard_widget.py
@description Floating virtual keyboard widget for Hebrew/Greek input in the Word Abacus panel. Allows users to input letters, space, backspace, and clear the input field. Designed for snazzy, accessible, and user-friendly input of non-Latin scripts.
@author Daniel (AI-generated)
@created 2024-06-09
@lastModified 2024-06-09
@dependencies PyQt6
"""

from typing import List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class VirtualKeyboardWidget(QDialog):
    """
    @class VirtualKeyboardWidget
    @description Floating virtual keyboard for Hebrew/Greek input. Emits key_pressed(str) when a key is pressed. Supports Shift for Greek capitals.
    @param QDialog parent - Parent widget
    @returns None
    @example
    vk = VirtualKeyboardWidget(language='Hebrew')
    vk.key_pressed.connect(lambda c: print(f"Pressed: {c}"))
    vk.exec()
    """

    key_pressed = pyqtSignal(str)

    def __init__(self, language: str = "Hebrew", parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle(f"{language} Virtual Keyboard")
        self.setModal(False)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(self._snazzy_stylesheet())
        self.language = language
        self._shift = False  # Only used for Greek
        self._letter_buttons = []
        self._shift_button = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        title = QLabel(f"{self.language} Keyboard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)

        grid = QGridLayout()
        self._letter_buttons = []
        chars_with_breaks = self.get_keyboard_layout(self.language, self._shift)

        row, col = 0, 0
        default_max_cols = 10  # Default for layouts without <br>
        if self.language == "Hebrew":
            max_cols = 10
        elif self.language == "Greek":
            max_cols = 8
        elif self.language == "Coptic":
            max_cols = 8  # Coptic uses <br>, this is a fallback/reference
        elif self.language == "Arabic":
            max_cols = (
                11  # Arabic layout will use <br> tags, this is a fallback/reference
            )
        else:
            max_cols = default_max_cols

        uses_br_tags = any(item == "<br>" for item in chars_with_breaks)

        for item in chars_with_breaks:
            if item == "<br>":
                row += 1
                col = 0
                continue

            char = item
            btn = QPushButton(char)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, c=char: self.key_pressed.emit(c))
            grid.addWidget(btn, row, col)
            self._letter_buttons.append(btn)
            col += 1

            if not uses_br_tags and col >= max_cols:
                row += 1
                col = 0
        layout.addLayout(grid)

        # Special keys row
        specials = QHBoxLayout()
        if self.language == "Greek":
            self._shift_button = QPushButton("Shift")
            self._shift_button.setCheckable(True)
            self._shift_button.setChecked(self._shift)
            self._update_shift_button_style()
            self._shift_button.clicked.connect(self._toggle_shift)
            specials.addWidget(self._shift_button)
        space_btn = QPushButton("Space")
        space_btn.clicked.connect(lambda: self.key_pressed.emit(" "))
        specials.addWidget(space_btn)
        back_btn = QPushButton("⌫")
        back_btn.clicked.connect(lambda: self.key_pressed.emit("<BACKSPACE>"))
        specials.addWidget(back_btn)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(lambda: self.key_pressed.emit("<CLEAR>"))
        specials.addWidget(clear_btn)
        layout.addLayout(specials)

        self.setLayout(layout)
        self.setFixedSize(self.sizeHint())

    def _toggle_shift(self):
        self._shift = not self._shift
        self._shift_button.setChecked(self._shift)
        self._update_shift_button_style()

        current_chars_with_breaks = self.get_keyboard_layout(self.language, self._shift)
        button_chars = [ch for ch in current_chars_with_breaks if ch != "<br>"]

        if len(self._letter_buttons) != len(button_chars):
            # This should ideally not happen if layouts are consistent
            print(
                f"Warning: Button/char mismatch in _toggle_shift. Buttons: {len(self._letter_buttons)}, Chars: {len(button_chars)}"
            )
            # Attempt to rebuild UI if mismatch is severe, or just log and proceed if minor
            # For now, just proceed, but this indicates a potential issue.
            # Fallback: Re-initialize the grid part of the UI. This is a bit heavy.
            # A lighter approach might be needed, or ensure layouts are always correct.
            # For simplicity here, we'll assume the button count doesn't change with shift.
            # If it does, the UI needs a more dynamic rebuild.

        for btn, char_for_button in zip(self._letter_buttons, button_chars):
            btn.setText(char_for_button)
            try:
                btn.clicked.disconnect()
            except TypeError:  # No connections
                pass
            except Exception as e:  # Catch-all for other potential errors
                print(f"Error disconnecting signal: {e}")
            # Capture char_for_button by value for the new connection
            btn.clicked.connect(
                lambda checked, c=char_for_button: self.key_pressed.emit(c)
            )

    def _update_shift_button_style(self):
        if self._shift_button:
            if self._shift:
                self._shift_button.setStyleSheet(
                    "background-color: #b0c4ff; font-weight: bold;"
                )
            else:
                self._shift_button.setStyleSheet("")

    @staticmethod
    def get_keyboard_layout(language: str, shift: bool = False) -> List[str]:
        """
        @function get_keyboard_layout
        @description Returns the list of characters for the specified language's keyboard. For Greek, shift toggles capitals.
        @param str language - 'Hebrew' or 'Greek'
        @param bool shift - If True, use uppercase for Greek
        @returns List[str] - List of characters
        @example
        VirtualKeyboardWidget.get_keyboard_layout('Greek', True)
        """
        if language == "Hebrew":
            # Standard Hebrew letters, including finals
            return [
                "א",
                "ב",
                "ג",
                "ד",
                "ה",
                "ו",
                "ז",
                "ח",
                "ט",
                "י",
                "כ",
                "ל",
                "מ",
                "נ",
                "ס",
                "ע",
                "פ",
                "צ",
                "ק",
                "ר",
                "ש",
                "ת",
                "ך",
                "ם",
                "ן",
                "ף",
                "ץ",
            ]
        elif language == "Greek":
            # Standard Greek letters, including final sigma
            lower = [
                "α",
                "β",
                "γ",
                "δ",
                "ε",
                "ζ",
                "η",
                "θ",
                "ι",
                "κ",
                "λ",
                "μ",
                "ν",
                "ξ",
                "ο",
                "π",
                "ρ",
                "σ",
                "τ",
                "υ",
                "φ",
                "χ",
                "ψ",
                "ω",
                "ς",
            ]
            upper = [
                "Α",
                "Β",
                "Γ",
                "Δ",
                "Ε",
                "Ζ",
                "Η",
                "Θ",
                "Ι",
                "Κ",
                "Λ",
                "Μ",
                "Ν",
                "Ξ",
                "Ο",
                "Π",
                "Ρ",
                "Σ",
                "Τ",
                "Υ",
                "Φ",
                "Χ",
                "Ψ",
                "Ω",
                "Σ",
            ]
            return upper if shift else lower
        elif language == "Coptic":
            # ⲁ ⲃ ⲅ ⲇ ⲉ ⲋ ⲍ ⲏ ⲑ ⲓ ⲕ ⲗ ⲙ ⲛ ⲝ ⲟ ⲡ ⲣ ⲥ ⲧ ⲩ ⲫ ⲭ ⲯ ⲱ ϣ ϥ ϧ ϩ ϫ ϭ ϯ
            return [
                "ⲁ",
                "ⲃ",
                "ⲅ",
                "ⲇ",
                "ⲉ",
                "ⲋ",
                "ⲍ",
                "ⲏ",
                "<br>",
                "ⲑ",
                "ⲓ",
                "ⲕ",
                "ⲗ",
                "ⲙ",
                "ⲛ",
                "ⲝ",
                "ⲟ",
                "<br>",
                "ⲡ",
                "ⲣ",
                "ⲥ",
                "ⲧ",
                "ⲩ",
                "ⲫ",
                "ⲭ",
                "ⲯ",
                "<br>",
                "ⲱ",
                "ϣ",
                "ϥ",
                "ϧ",
                "ϩ",
                "ϫ",
                "ϭ",
                "ϯ",
            ]
        elif language == "Arabic":
            # Based on a standard Arabic (101) PC keyboard layout
            return [
                "ذ",
                "١",
                "٢",
                "٣",
                "٤",
                "٥",
                "٦",
                "٧",
                "٨",
                "٩",
                "٠",
                "-",
                "=",
                "<br>",
                "ض",
                "ص",
                "ث",
                "ق",
                "ف",
                "غ",
                "ع",
                "ه",
                "خ",
                "ح",
                "ج",
                "د",
                "<br>",
                "ش",
                "س",
                "ي",
                "ب",
                "ل",
                "ا",
                "ت",
                "ن",
                "م",
                "ك",
                "ط",
                "<br>",
                "ئ",
                "ء",
                "ؤ",
                "ر",
                "لا",
                "ى",
                "ة",
                "و",
                "ز",
                "ظ",
                "<br>",
                "َ",
                "ً",
                "ُ",
                "ٌ",
                "ِ",
                "ٍ",
                "ْ",
                "~",  # Common diacritics and tilde
            ]
        else:
            return []

    def _snazzy_stylesheet(self) -> str:
        return """
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8fafc, stop:1 #e0e7ef);
            border-radius: 12px;
        }
        QPushButton {
            background: #fff;
            border: 2px solid #b0b8c1;
            border-radius: 8px;
            font-size: 16px;
            min-width: 32px;
            min-height: 32px;
            margin: 2px;
        }
        QPushButton:hover {
            background: #e0e7ef;
            border-color: #7b8fa1;
        }
        QPushButton:pressed {
            background: #c7d0e0;
        }
        QLabel {
            color: #2c3e50;
        }
        """
