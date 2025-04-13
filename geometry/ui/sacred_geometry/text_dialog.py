"""Text input dialog for the Sacred Geometry Explorer."""

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDialog,
    QFontComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class TextDialog(QDialog):
    """Dialog for entering and formatting text."""

    def __init__(
        self,
        parent=None,
        initial_text="",
        initial_font_family="Arial",
        initial_font_size=12,
        initial_font_style=0,
        initial_color=QColor(0, 0, 0),
        initial_auto_position=True,
        is_label=False,
    ):
        """Initialize the text dialog.

        Args:
            parent: Parent widget
            initial_text: Initial text content
            initial_font_family: Initial font family
            initial_font_size: Initial font size
            initial_font_style: Initial font style (0=normal, 1=bold, 2=italic, 3=bold+italic)
            initial_color: Initial text color
            initial_auto_position: Initial auto-position setting
            is_label: Whether this is a label for an object
        """
        super().__init__(parent)

        self.text = initial_text
        self.font_family = initial_font_family
        self.font_size = initial_font_size
        self.font_style = initial_font_style
        self.color = initial_color
        self.auto_position = initial_auto_position

        self._setup_ui(is_label)

    def _setup_ui(self, is_label):
        """Set up the dialog UI.

        Args:
            is_label: Whether this is a label for an object
        """
        # Set window title
        self.setWindowTitle("Text Properties" if not is_label else "Label Properties")

        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Text input
        text_group = QGroupBox("Text Content")
        text_layout = QVBoxLayout()
        text_group.setLayout(text_layout)

        self.text_edit = QLineEdit(self.text)
        self.text_edit.setPlaceholderText("Enter text here")
        text_layout.addWidget(self.text_edit)

        layout.addWidget(text_group)

        # Font properties
        font_group = QGroupBox("Font Properties")
        font_layout = QVBoxLayout()
        font_group.setLayout(font_layout)

        # Font family
        font_family_layout = QHBoxLayout()
        font_family_label = QLabel("Font:")
        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setCurrentText(self.font_family)
        font_family_layout.addWidget(font_family_label)
        font_family_layout.addWidget(self.font_family_combo)
        font_layout.addLayout(font_family_layout)

        # Font size
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Size:")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setValue(int(self.font_size))
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self.font_size_spin)
        font_layout.addLayout(font_size_layout)

        # Font style
        style_layout = QHBoxLayout()
        self.bold_check = QCheckBox("Bold")
        self.italic_check = QCheckBox("Italic")
        self.bold_check.setChecked(self.font_style & 1)
        self.italic_check.setChecked(self.font_style & 2)
        style_layout.addWidget(self.bold_check)
        style_layout.addWidget(self.italic_check)
        font_layout.addLayout(style_layout)

        # Color
        color_layout = QHBoxLayout()
        color_label = QLabel("Color:")
        self.color_button = QPushButton()
        self.color_button.setFixedSize(24, 24)
        self._update_color_button()
        self.color_button.clicked.connect(self._select_color)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        font_layout.addLayout(color_layout)

        layout.addWidget(font_group)

        # Auto-position (only for labels)
        if is_label:
            position_group = QGroupBox("Position")
            position_layout = QVBoxLayout()
            position_group.setLayout(position_layout)

            self.auto_position_check = QCheckBox(
                "Automatically position relative to object"
            )
            self.auto_position_check.setChecked(self.auto_position)
            position_layout.addWidget(self.auto_position_check)

            layout.addWidget(position_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Set minimum size
        self.setMinimumWidth(300)

    def _update_color_button(self):
        """Update the color button appearance."""
        style = f"background-color: {self.color.name()}; border: 1px solid #888;"
        self.color_button.setStyleSheet(style)

    def _select_color(self):
        """Show color dialog and update color."""
        color = QColorDialog.getColor(self.color, self, "Select Text Color")
        if color.isValid():
            self.color = color
            self._update_color_button()

    def get_text(self):
        """Get the entered text.

        Returns:
            Text content
        """
        return self.text_edit.text()

    def get_font_family(self):
        """Get the selected font family.

        Returns:
            Font family name
        """
        return self.font_family_combo.currentText()

    def get_font_size(self):
        """Get the selected font size.

        Returns:
            Font size
        """
        return self.font_size_spin.value()

    def get_font_style(self):
        """Get the selected font style.

        Returns:
            Font style (0=normal, 1=bold, 2=italic, 3=bold+italic)
        """
        style = 0
        if self.bold_check.isChecked():
            style |= 1
        if self.italic_check.isChecked():
            style |= 2
        return style

    def get_color(self):
        """Get the selected color.

        Returns:
            Text color
        """
        return self.color

    def get_auto_position(self):
        """Get the auto-position setting.

        Returns:
            Whether to automatically position the text
        """
        if hasattr(self, "auto_position_check"):
            return self.auto_position_check.isChecked()
        return self.auto_position

    def accept(self):
        """Handle dialog acceptance."""
        # Store values
        self.text = self.get_text()
        self.font_family = self.get_font_family()
        self.font_size = self.get_font_size()
        self.font_style = self.get_font_style()
        self.auto_position = self.get_auto_position()

        # Call parent implementation
        super().accept()
