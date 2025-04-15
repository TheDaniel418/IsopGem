import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor, QTextLength, QTextTableFormat
from PyQt6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class TablePropertiesDialog(QDialog):
    """Dialog for editing table properties.
    
    This dialog allows users to view and modify properties of a table in the document,
    including:
    - Border width, style, and color
    - Cell spacing and padding
    - Background color
    - Width and alignment
    
    It provides a user-friendly interface for configuring all aspects of table formatting.
    
    Attributes:
        current_format (QTextTableFormat): The format of the table being edited
    """

    def __init__(self, current_format, parent=None):
        """Initialize the table properties dialog.
        
        Creates a dialog for editing table properties based on the provided table format.
        Sets up the UI and loads the current format values.
        
        Args:
            current_format (QTextTableFormat): The format of the table to edit
            parent (QWidget, optional): Parent widget for this dialog
            
        Returns:
            None
        """
        super().__init__(parent)
        self.setWindowTitle("Table Properties")
        self.current_format = current_format

        self.setup_ui()
        self.load_current_format()

    def setup_ui(self):
        """Set up the dialog UI elements.
        
        Creates and configures all UI components for the dialog, including:
        - Border controls (width, style, color)
        - Cell spacing and padding controls
        - Background color selector
        - Width and alignment controls
        - OK and Cancel buttons
        
        Returns:
            None
        """
        layout = QVBoxLayout(self)

        # --- General Settings ---
        general_group = QGroupBox("General")
        general_layout = QFormLayout()

        # Cell padding with validation
        self.cell_padding_spin = QSpinBox()
        self.cell_padding_spin.setRange(0, 50)  # Reasonable limits
        self.cell_padding_spin.setToolTip("Cell padding must be between 0 and 50 pixels")
        self.cell_padding_spin.setStatusTip("Set the padding inside each cell (0-50)")
        general_layout.addRow("Cell Padding:", self.cell_padding_spin)

        # Cell spacing with validation
        self.cell_spacing_spin = QSpinBox()
        self.cell_spacing_spin.setRange(0, 50)  # Reasonable limits
        self.cell_spacing_spin.setToolTip("Cell spacing must be between 0 and 50 pixels")
        self.cell_spacing_spin.setStatusTip("Set the spacing between cells (0-50)")
        general_layout.addRow("Cell Spacing:", self.cell_spacing_spin)

        # Add Column Width control with validation
        self.column_width_spin = QDoubleSpinBox()
        self.column_width_spin.setRange(1, 100)  # Percentage (valid range)
        self.column_width_spin.setSuffix(" %")
        self.column_width_spin.setDecimals(1)
        self.column_width_spin.setSingleStep(5.0)
        self.column_width_spin.setToolTip(
            "Set a uniform width for all columns (1-100%).\nValues must be between 1% and 100%."
        )
        self.column_width_spin.setStatusTip("Set uniform column width as percentage of table width")
        general_layout.addRow("Uniform Column Width:", self.column_width_spin)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # --- Border Settings ---
        border_group = QGroupBox("Borders")
        border_layout = QFormLayout()

        # Border width with validation
        self.border_width_spin = QSpinBox()
        self.border_width_spin.setRange(0, 10)  # Reasonable limits
        self.border_width_spin.setToolTip("Border width must be between 0 and 10 pixels")
        self.border_width_spin.setStatusTip("Set the width of table borders (0-10)")
        border_layout.addRow("Border Width:", self.border_width_spin)

        # Border style with validation
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
        self.border_style_combo.setToolTip("Select the style for table borders")
        self.border_style_combo.setStatusTip("Choose border style from predefined options")
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
        """Load settings from the current table format into the UI.
        
        Retrieves all formatting properties from the current table format and
        updates the UI controls to reflect these values. Handles special cases
        like column width constraints and border styles.
        
        Returns:
            None
        """
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
        """Open color dialog to choose border color.
        
        Displays a color picker dialog and updates the border color
        if the user selects a valid color.
        
        Returns:
            None
        """
        color = QColorDialog.getColor(self._border_color, self, "Choose Border Color")
        if color.isValid():
            self._border_color = color
            self.update_color_button_style(self.border_color_button, self._border_color)

    def update_color_button_style(self, button, color):
        """Update button background to show the selected color.
        
        Changes the background color of a button to visually indicate
        the currently selected color.
        
        Args:
            button (QPushButton): The button to update
            color (QColor): The color to apply to the button background
            
        Returns:
            None
        """
        button.setStyleSheet(f"background-color: {color.name()};")

    def get_new_format(self):
        """Create a new QTextTableFormat based on the dialog settings.
        
        Builds a new QTextTableFormat object with all properties set according
        to the current values in the UI controls. This includes:
        - Cell padding and spacing
        - Border width, style, and color
        - Background color
        - Column width constraints
        - Alignment
        
        Returns:
            QTextTableFormat: A new table format with all properties set
        """
        new_format = QTextTableFormat()
        
        # Validate and apply cell padding (ensure it's within valid range)
        cell_padding = max(0, min(50, self.cell_padding_spin.value()))
        new_format.setCellPadding(cell_padding)
        
        # Validate and apply cell spacing (ensure it's within valid range)
        cell_spacing = max(0, min(50, self.cell_spacing_spin.value()))
        new_format.setCellSpacing(cell_spacing)
        
        # Validate and apply border width (ensure it's within valid range)
        border_width = max(0, min(10, self.border_width_spin.value()))
        new_format.setBorder(border_width)

        # --- Set Column Width ---
        num_columns = self.current_format.columns()
        if num_columns > 0:
            # Validate column width percentage (ensure it's within valid range)
            col_width_percent = max(1, min(100, self.column_width_spin.value()))
            
            if col_width_percent > 0:  # Only apply if a value > 0 is set
                constraints = []
                
                # Validate number of columns (prevent excessive columns)
                max_columns = 100  # Reasonable limit
                valid_columns = min(num_columns, max_columns)
                
                for _ in range(valid_columns):
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
