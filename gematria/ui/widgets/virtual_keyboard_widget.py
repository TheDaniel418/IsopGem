"""
@file virtual_keyboard_widget.py
@description Floating virtual keyboard widget for Hebrew/Greek input in the Word Abacus panel. Allows users to input letters, space, backspace, and clear the input field. Designed for snazzy, accessible, and user-friendly input of non-Latin scripts.
@author Daniel (AI-generated)
@created 2024-06-09
@lastModified 2024-06-09
@dependencies PyQt6
"""

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QDialog, QGridLayout, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
)
from typing import List

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

    def __init__(self, language: str = 'Hebrew', parent: QWidget = None):
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
        chars = self.get_keyboard_layout(self.language, self._shift)
        row, col = 0, 0
        for i, char in enumerate(chars):
            btn = QPushButton(char)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda _, c=char: self.key_pressed.emit(c))
            grid.addWidget(btn, row, col)
            self._letter_buttons.append(btn)
            col += 1
            if (col >= 10 and self.language == 'Hebrew') or (col >= 8 and self.language == 'Greek'):
                row += 1
                col = 0
        layout.addLayout(grid)

        # Special keys row
        specials = QHBoxLayout()
        if self.language == 'Greek':
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
        # Update all letter buttons
        chars = self.get_keyboard_layout(self.language, self._shift)
        for btn, char in zip(self._letter_buttons, chars):
            btn.setText(char)
            # Disconnect all signals first
            try:
                btn.clicked.disconnect()
            except Exception:
                pass
            btn.clicked.connect(lambda _, c=char: self.key_pressed.emit(c))

    def _update_shift_button_style(self):
        if self._shift_button:
            if self._shift:
                self._shift_button.setStyleSheet("background-color: #b0c4ff; font-weight: bold;")
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
        if language == 'Hebrew':
            # Standard Hebrew letters, including finals
            return [
                'א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט',
                'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ',
                'ק', 'ר', 'ש', 'ת', 'ך', 'ם', 'ן', 'ף', 'ץ'
            ]
        elif language == 'Greek':
            # Standard Greek letters, including final sigma
            lower = [
                'α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ',
                'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π',
                'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω', 'ς'
            ]
            upper = [
                'Α', 'Β', 'Γ', 'Δ', 'Ε', 'Ζ', 'Η', 'Θ',
                'Ι', 'Κ', 'Λ', 'Μ', 'Ν', 'Ξ', 'Ο', 'Π',
                'Ρ', 'Σ', 'Τ', 'Υ', 'Φ', 'Χ', 'Ψ', 'Ω', 'Σ'
            ]
            return upper if shift else lower
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