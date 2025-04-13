"""Toolbar for the Text Tool."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFontComboBox,
    QLabel,
    QPushButton,
    QSpinBox,
    QToolBar,
)


class TextToolbar(QToolBar):
    """Toolbar for the Text Tool."""

    # Signals
    mode_changed = pyqtSignal(int)
    font_family_changed = pyqtSignal(str)
    font_size_changed = pyqtSignal(float)
    font_style_changed = pyqtSignal(int)
    text_color_changed = pyqtSignal(QColor)
    auto_position_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        """Initialize the text toolbar.

        Args:
            parent: Parent widget
        """
        super().__init__("Text Tool Options", parent)
        self.setObjectName("text_toolbar")
        self.setMovable(False)
        self.setFloatable(False)
        self.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the toolbar UI."""
        # Mode selection
        self.mode_label = QLabel("Mode:")
        self.addWidget(self.mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Free Text")
        self.mode_combo.addItem("Label Object")
        self.mode_combo.setCurrentIndex(0)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.addWidget(self.mode_combo)

        self.addSeparator()

        # Font family
        self.font_family_label = QLabel("Font:")
        self.addWidget(self.font_family_label)

        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setCurrentText("Arial")
        self.font_family_combo.currentFontChanged.connect(self._on_font_family_changed)
        self.addWidget(self.font_family_combo)

        # Font size
        self.font_size_label = QLabel("Size:")
        self.addWidget(self.font_size_label)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        self.addWidget(self.font_size_spin)

        # Font style
        self.bold_check = QCheckBox("Bold")
        self.bold_check.stateChanged.connect(self._on_font_style_changed)
        self.addWidget(self.bold_check)

        self.italic_check = QCheckBox("Italic")
        self.italic_check.stateChanged.connect(self._on_font_style_changed)
        self.addWidget(self.italic_check)

        self.addSeparator()

        # Text color
        self.color_label = QLabel("Color:")
        self.addWidget(self.color_label)

        self.color_button = QPushButton()
        self.color_button.setFixedSize(24, 24)
        self.color_button.setStyleSheet(
            "background-color: #000000; border: 1px solid #888;"
        )
        self.color_button.clicked.connect(self._on_color_button_clicked)
        self.addWidget(self.color_button)

        self.addSeparator()

        # Auto-position
        self.auto_position_check = QCheckBox("Auto-position")
        self.auto_position_check.setChecked(True)
        self.auto_position_check.stateChanged.connect(self._on_auto_position_changed)
        self.addWidget(self.auto_position_check)

    def _on_mode_changed(self, index):
        """Handle mode change.

        Args:
            index: Combo box index
        """
        self.mode_changed.emit(index)

    def _on_font_family_changed(self, font):
        """Handle font family change.

        Args:
            font: Selected font
        """
        self.font_family_changed.emit(font.family())

    def _on_font_size_changed(self, size):
        """Handle font size change.

        Args:
            size: Selected font size
        """
        self.font_size_changed.emit(float(size))

    def _on_font_style_changed(self):
        """Handle font style change."""
        style = 0
        if self.bold_check.isChecked():
            style |= 1
        if self.italic_check.isChecked():
            style |= 2
        self.font_style_changed.emit(style)

    def _on_color_button_clicked(self):
        """Handle color button click."""
        # Get current color
        current_style = self.color_button.styleSheet()
        current_color = QColor("#000000")  # Default black
        for part in current_style.split(";"):
            if "background-color" in part:
                color_str = part.split(":")[1].strip()
                current_color = QColor(color_str)
                break

        # Show color dialog
        color = QColorDialog.getColor(current_color, self, "Select Text Color")
        if color.isValid():
            self.color_button.setStyleSheet(
                f"background-color: {color.name()}; border: 1px solid #888;"
            )
            self.text_color_changed.emit(color)

    def _on_auto_position_changed(self, state):
        """Handle auto-position change.

        Args:
            state: Checkbox state
        """
        self.auto_position_changed.emit(state == Qt.CheckState.Checked)

    def set_mode(self, mode):
        """Set the current mode.

        Args:
            mode: Mode index (0 = free text, 1 = label object)
        """
        self.mode_combo.setCurrentIndex(mode)

    def set_font_family(self, family):
        """Set the current font family.

        Args:
            family: Font family name
        """
        self.font_family_combo.setCurrentText(family)

    def set_font_size(self, size):
        """Set the current font size.

        Args:
            size: Font size
        """
        self.font_size_spin.setValue(int(size))

    def set_font_style(self, style):
        """Set the current font style.

        Args:
            style: Font style (0 = normal, 1 = bold, 2 = italic, 3 = bold+italic)
        """
        self.bold_check.setChecked(style & 1)
        self.italic_check.setChecked(style & 2)

    def set_text_color(self, color):
        """Set the current text color.

        Args:
            color: Text color
        """
        self.color_button.setStyleSheet(
            f"background-color: {color.name()}; border: 1px solid #888;"
        )

    def set_auto_position(self, auto_position):
        """Set the current auto-position setting.

        Args:
            auto_position: Whether to automatically position text
        """
        self.auto_position_check.setChecked(auto_position)
