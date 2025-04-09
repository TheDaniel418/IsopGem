import sys
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QSpinBox,
    QComboBox,
    QDialogButtonBox,
    QGroupBox,
    QColorDialog,
    QPushButton,
    QLabel,
    QDoubleSpinBox,
)
from PyQt6.QtGui import QTextTableFormat, QBrush, QColor, QTextLength
from PyQt6.QtCore import Qt


class TablePropertiesDialog(QDialog):
    """Dialog for editing table properties."""

    def __init__(self, current_format, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Table Properties")
        self.current_format = current_format

        self.setup_ui()
        self.load_current_format()

    def setup_ui(self):
        """Set up the dialog UI elements."""
        layout = QVBoxLayout(self)

        # --- General Settings ---
        general_group = QGroupBox("General")
        general_layout = QFormLayout()

        self.cell_padding_spin = QSpinBox()
        self.cell_padding_spin.setRange(0, 50)
        general_layout.addRow("Cell Padding:", self.cell_padding_spin)

        self.cell_spacing_spin = QSpinBox()
        self.cell_spacing_spin.setRange(0, 50)
        general_layout.addRow("Cell Spacing:", self.cell_spacing_spin)

        # Add Column Width control
        self.column_width_spin = QDoubleSpinBox()
        self.column_width_spin.setRange(1, 100)  # Percentage
        self.column_width_spin.setSuffix(" %")
        self.column_width_spin.setDecimals(1)
        self.column_width_spin.setSingleStep(5.0)
        self.column_width_spin.setToolTip(
            "Set a uniform width for all columns (0 to disable)."
        )
        general_layout.addRow("Uniform Column Width:", self.column_width_spin)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # --- Border Settings ---
        border_group = QGroupBox("Borders")
        border_layout = QFormLayout()

        self.border_width_spin = QSpinBox()
        self.border_width_spin.setRange(0, 10)
        border_layout.addRow("Border Width:", self.border_width_spin)

        self.border_style_combo = QComboBox()
        self.border_style_combo.addItems(
            [
                "Solid",
                "Dashed",
                "Dotted",
                "Double",
                "Groove",
                "Ridge",
                "Inset",
                "Outset",
                "None",
            ]
        )
        border_layout.addRow("Border Style:", self.border_style_combo)

        self.border_color_button = QPushButton("Choose Color...")
        self.border_color_button.clicked.connect(self.choose_border_color)
        self._border_color = QColor(Qt.GlobalColor.black)  # Default
        self.update_color_button_style(self.border_color_button, self._border_color)
        border_layout.addRow("Border Color:", self.border_color_button)

        border_group.setLayout(border_layout)
        layout.addWidget(border_group)

        # --- Buttons ---
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_current_format(self):
        """Load settings from the current table format into the UI."""
        self.cell_padding_spin.setValue(int(self.current_format.cellPadding()))
        self.cell_spacing_spin.setValue(int(self.current_format.cellSpacing()))
        self.border_width_spin.setValue(int(self.current_format.border()))

        # --- Load Column Width ---
        constraints = self.current_format.columnWidthConstraints()
        uniform_percentage = 0.0
        if constraints:
            first_constraint = constraints[0]
            if first_constraint.type() == QTextLength.Type.PercentageLength:
                # Check if all columns have the same percentage width
                is_uniform = all(
                    c.type() == QTextLength.Type.PercentageLength
                    and abs(c.rawValue() - first_constraint.rawValue()) < 0.01
                    for c in constraints
                )
                if is_uniform:
                    uniform_percentage = first_constraint.rawValue()

        self.column_width_spin.setValue(
            uniform_percentage
            if uniform_percentage > 0
            else 100.0 / self.current_format.columns()
            if self.current_format.columns() > 0
            else 25.0
        )
        self.column_width_spin.setEnabled(
            uniform_percentage > 0
        )  # Enable only if loaded uniform %

        # Border style mapping
        style_map = {
            QTextTableFormat.BorderStyle.BorderStyle_Solid: "Solid",
            QTextTableFormat.BorderStyle.BorderStyle_Dashed: "Dashed",
            QTextTableFormat.BorderStyle.BorderStyle_Dotted: "Dotted",
            QTextTableFormat.BorderStyle.BorderStyle_Double: "Double",
            QTextTableFormat.BorderStyle.BorderStyle_Groove: "Groove",
            QTextTableFormat.BorderStyle.BorderStyle_Ridge: "Ridge",
            QTextTableFormat.BorderStyle.BorderStyle_Inset: "Inset",
            QTextTableFormat.BorderStyle.BorderStyle_Outset: "Outset",
            QTextTableFormat.BorderStyle.BorderStyle_None: "None",
        }
        current_style_enum = self.current_format.borderStyle()
        self.border_style_combo.setCurrentText(
            style_map.get(current_style_enum, "Solid")
        )

        # Border color
        self._border_color = self.current_format.borderBrush().color()
        self.update_color_button_style(self.border_color_button, self._border_color)

    def choose_border_color(self):
        """Open color dialog to choose border color."""
        color = QColorDialog.getColor(self._border_color, self, "Choose Border Color")
        if color.isValid():
            self._border_color = color
            self.update_color_button_style(self.border_color_button, self._border_color)

    def update_color_button_style(self, button, color):
        """Update button background to show the selected color."""
        button.setStyleSheet(f"background-color: {color.name()};")

    def get_new_format(self):
        """Create a new QTextTableFormat based on the dialog settings."""
        new_format = QTextTableFormat()
        new_format.setCellPadding(self.cell_padding_spin.value())
        new_format.setCellSpacing(self.cell_spacing_spin.value())
        new_format.setBorder(self.border_width_spin.value())

        # --- Set Column Width ---
        num_columns = self.current_format.columns()
        if num_columns > 0:
            col_width_percent = self.column_width_spin.value()
            if col_width_percent > 0:  # Only apply if a value > 0 is set
                constraints = []
                for _ in range(num_columns):
                    constraints.append(
                        QTextLength(
                            QTextLength.Type.PercentageLength, col_width_percent
                        )
                    )
                new_format.setColumnWidthConstraints(constraints)
            # Else: Let Qt manage column widths automatically if 0 is set

        # Border style mapping (reverse)
        style_map_rev = {
            "Solid": QTextTableFormat.BorderStyle.BorderStyle_Solid,
            "Dashed": QTextTableFormat.BorderStyle.BorderStyle_Dashed,
            "Dotted": QTextTableFormat.BorderStyle.BorderStyle_Dotted,
            "Double": QTextTableFormat.BorderStyle.BorderStyle_Double,
            "Groove": QTextTableFormat.BorderStyle.BorderStyle_Groove,
            "Ridge": QTextTableFormat.BorderStyle.BorderStyle_Ridge,
            "Inset": QTextTableFormat.BorderStyle.BorderStyle_Inset,
            "Outset": QTextTableFormat.BorderStyle.BorderStyle_Outset,
            "None": QTextTableFormat.BorderStyle.BorderStyle_None,
        }
        style_text = self.border_style_combo.currentText()
        new_format.setBorderStyle(
            style_map_rev.get(
                style_text, QTextTableFormat.BorderStyle.BorderStyle_Solid
            )
        )

        # Border color
        new_format.setBorderBrush(QBrush(self._border_color))

        # Copy other properties we aren't editing yet (important!)
        new_format.setHeaderRowCount(self.current_format.headerRowCount())
        new_format.setAlignment(self.current_format.alignment())
        # Add more properties here if needed (e.g., width, background)

        return new_format


# Example Usage (for testing)
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create a dummy format for testing
    dummy_format = QTextTableFormat()
    dummy_format.setCellPadding(2)
    dummy_format.setCellSpacing(1)
    dummy_format.setBorder(1)
    dummy_format.setBorderStyle(QTextTableFormat.BorderStyle.BorderStyle_Solid)
    dummy_format.setBorderBrush(QBrush(Qt.GlobalColor.blue))

    dialog = TablePropertiesDialog(dummy_format)
    if dialog.exec():
        updated_format = dialog.get_new_format()
        print("Dialog Accepted! New format details:")
        print(
            f"Padding: {updated_format.cellPadding()}, Spacing: {updated_format.cellSpacing()}"
        )
        print(
            f"Border: {updated_format.border()}, Style: {updated_format.borderStyle()}, Color: {updated_format.borderBrush().color().name()}"
        )
    else:
        print("Dialog Cancelled.")

    sys.exit()
