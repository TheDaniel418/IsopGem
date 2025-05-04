"""
Group Selection Dialog.

This module provides a dialog for saving and managing selection groups.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QLineEdit, QFormLayout, QDialogButtonBox,
    QColorDialog, QFrame, QGroupBox, QRadioButton
)


class GroupSelectionDialog(QDialog):
    """Dialog for saving and managing selection groups."""

    def __init__(self, parent=None, existing_groups=None, selected_count=0):
        """Initialize the dialog.

        Args:
            parent: Parent widget
            existing_groups: List of existing group names
            selected_count: Number of dots in the current selection
        """
        super().__init__(parent)
        self.existing_groups = existing_groups or ["Default"]
        self.selected_count = selected_count
        self.result_group = None
        self.result_color = None
        self.result_mode = "save"  # "save" or "add"

        self.setWindowTitle("Save Selection")
        self.setMinimumWidth(400)
        self.setModal(True)

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Selection info
        info_label = QLabel(f"<b>{self.selected_count} dots selected</b>")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Mode selection
        mode_group = QGroupBox("Save Mode")
        mode_layout = QVBoxLayout(mode_group)

        self.save_radio = QRadioButton("Replace group contents with current selection")
        self.save_radio.setChecked(True)
        self.save_radio.toggled.connect(self._update_description)
        mode_layout.addWidget(self.save_radio)

        self.add_radio = QRadioButton("Add current selection to existing group contents")
        self.add_radio.toggled.connect(self._update_description)
        mode_layout.addWidget(self.add_radio)

        layout.addWidget(mode_group)

        # Group selection
        group_group = QGroupBox("Select Group")
        group_layout = QVBoxLayout(group_group)

        # Existing group option
        self.existing_radio = QRadioButton("Use existing group:")
        self.existing_radio.setChecked(True)
        self.existing_radio.toggled.connect(self._toggle_group_options)
        group_layout.addWidget(self.existing_radio)

        # Existing group combo
        self.group_combo = QComboBox()
        for group in self.existing_groups:
            self.group_combo.addItem(group)
        group_layout.addWidget(self.group_combo)

        # New group option
        self.new_radio = QRadioButton("Create new group:")
        self.new_radio.toggled.connect(self._toggle_group_options)
        group_layout.addWidget(self.new_radio)

        # New group name
        self.new_group_edit = QLineEdit()
        self.new_group_edit.setPlaceholderText("Enter new group name")
        self.new_group_edit.setEnabled(False)
        group_layout.addWidget(self.new_group_edit)

        layout.addWidget(group_group)

        # Color selection
        color_group = QGroupBox("Group Color")
        color_layout = QHBoxLayout(color_group)

        # Color preview
        self.color_preview = QFrame()
        self.color_preview.setFrameShape(QFrame.Shape.Box)
        self.color_preview.setMinimumSize(30, 30)
        self.color_preview.setMaximumSize(30, 30)
        self.color_preview.setStyleSheet("background-color: #3498db;")
        color_layout.addWidget(self.color_preview)

        # Color button
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self._choose_color)
        color_layout.addWidget(self.color_button)

        layout.addWidget(color_group)

        # Description of what will happen
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #555; font-style: italic;")
        layout.addWidget(self.description_label)

        # Update the description initially
        self._update_description()

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set the current color
        self.result_color = QColor(52, 152, 219)  # Default blue color

    def _toggle_group_options(self, checked):
        """Toggle between existing and new group options.

        Args:
            checked: Whether the radio button is checked
        """
        if self.sender() == self.existing_radio:
            self.group_combo.setEnabled(checked)
            self.new_group_edit.setEnabled(not checked)
        elif self.sender() == self.new_radio:
            self.group_combo.setEnabled(not checked)
            self.new_group_edit.setEnabled(checked)

        self._update_description()

    def _choose_color(self):
        """Open color dialog to choose a color."""
        color = QColorDialog.getColor(self.result_color, self, "Choose Group Color")
        if color.isValid():
            self.result_color = color
            self.color_preview.setStyleSheet(f"background-color: {color.name()};")

    def _update_description(self):
        """Update the description based on current selections."""
        # Determine the group name
        if self.existing_radio.isChecked():
            group_name = self.group_combo.currentText()
        else:
            group_name = self.new_group_edit.text() or "[new group]"

        # Determine the mode
        if self.save_radio.isChecked():
            mode_text = f"replace the contents of group '{group_name}'"
            self.result_mode = "save"
        else:
            mode_text = f"add to the existing contents of group '{group_name}'"
            self.result_mode = "add"

        # Update the description
        self.description_label.setText(
            f"This will {mode_text} with the current selection of {self.selected_count} dots."
        )

    def get_result(self):
        """Get the dialog result.

        Returns:
            Tuple of (group_name, color, mode)
        """
        # Determine the group name
        if self.existing_radio.isChecked():
            group_name = self.group_combo.currentText()
        else:
            group_name = self.new_group_edit.text()

        return group_name, self.result_color, self.result_mode

    def accept(self):
        """Handle dialog acceptance."""
        # Validate input
        if self.new_radio.isChecked() and not self.new_group_edit.text():
            self.description_label.setText(
                "<span style='color: red;'>Please enter a name for the new group.</span>"
            )
            return

        # Store the result
        self.result_group, self.result_color, self.result_mode = self.get_result()

        # Call parent accept
        super().accept()
