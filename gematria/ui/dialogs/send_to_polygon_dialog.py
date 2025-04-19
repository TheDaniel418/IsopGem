"""Send to Polygon Calculator dialog.

This module provides a dialog for sending values to the Regular Polygon Calculator.
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SendToPolygonDialog(QDialog):
    """Dialog for sending values to the Regular Polygon Calculator."""

    def __init__(self, value: float, parent: Optional[QWidget] = None) -> None:
        """Initialize the dialog.

        Args:
            value: The value to send
            parent: Parent widget
        """
        super().__init__(parent)
        self.value = value
        self.selected_field = ""
        self.selected_sides = 3  # Default to triangle

        # Define the available fields in the Regular Polygon Calculator
        self.available_fields = [
            "Radius",
            "Edge Length",
            "Perimeter",
            "Area",
            "Inradius",
            "Incircle Circumference",
            "Incircle Area",
            "Circumradius",
            "Circumcircle Circumference",
            "Circumcircle Area",
        ]

        # Define the available polygon types
        self.polygon_types = [
            ("Triangle", 3),
            ("Square", 4),
            ("Pentagon", 5),
            ("Hexagon", 6),
            ("Heptagon", 7),
            ("Octagon", 8),
            ("Nonagon", 9),
            ("Decagon", 10),
            ("Hendecagon", 11),
            ("Dodecagon", 12),
            ("Triskaidecagon", 13),
            ("Tetrakaidecagon", 14),
            ("Pentakaidecagon", 15),
            ("Hexakaidecagon", 16),
            ("Heptakaidecagon", 17),
            ("Octakaidecagon", 18),
            ("Enneakaidecagon", 19),
            ("Icosagon", 20),
        ]

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        self.setWindowTitle("Send to Polygon Calculator")
        self.setMinimumWidth(350)

        # Create the main layout
        layout = QVBoxLayout(self)

        # Add a label explaining the dialog
        info_label = QLabel(
            f"Send the value {self.value} to the Regular Polygon Calculator."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Create a form layout for the selections
        form_layout = QFormLayout()

        # Polygon type selection
        self.polygon_combo = QComboBox()
        for name, sides in self.polygon_types:
            self.polygon_combo.addItem(name, sides)
        form_layout.addRow("Polygon Type:", self.polygon_combo)

        # Field selection
        self.field_combo = QComboBox()
        for field in self.available_fields:
            self.field_combo.addItem(field)
        form_layout.addRow("Field:", self.field_combo)

        layout.addLayout(form_layout)

        # Add custom buttons
        from PyQt6.QtWidgets import QHBoxLayout, QPushButton

        button_layout = QHBoxLayout()

        # Create OK button
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet(
            "background-color: #3498db; color: white; font-weight: bold;"
        )
        ok_button.clicked.connect(self._on_ok_clicked)

        # Create Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def _on_ok_clicked(self) -> None:
        """Handle OK button click."""
        print("_on_ok_clicked called")
        self.selected_field = self.field_combo.currentText()
        self.selected_sides = self.polygon_combo.currentData()
        print(
            f"Selected field: {self.selected_field}, selected sides: {self.selected_sides}"
        )

        # Call our custom implementation
        self._create_polygon_calculator()

        # Close the dialog
        self.accept()

    def accept(self) -> None:
        """Handle dialog acceptance."""
        print("SendToPolygonDialog.accept called")
        super().accept()

    def _create_polygon_calculator(self) -> None:
        """Create a new Regular Polygon Calculator window and set the values."""
        print("_create_polygon_calculator called")

        # Import required modules
        import uuid

        from PyQt6.QtWidgets import QApplication

        from geometry.ui.panels.regular_polygon_panel import RegularPolygonPanel

        try:
            # Get the main application instance
            app = QApplication.instance()

            # Get the main window
            main_window = None
            for widget in app.topLevelWidgets():
                if widget.__class__.__name__ == "MainWindow":
                    main_window = widget
                    print(f"Found main window: {main_window}")
                    break

            if not main_window:
                print("Could not find main window")
                return

            # Get the window manager
            if hasattr(main_window, "window_manager"):
                window_manager = main_window.window_manager
                print(f"Found window manager: {window_manager}")
            else:
                print("Could not find window_manager attribute")
                return

            # Create a unique ID for the window
            window_id = f"regular_polygon_{uuid.uuid4().hex[:8]}"

            # Create the calculator panel
            calculator_panel = RegularPolygonPanel()

            # Create a window using the window manager
            window = window_manager.create_auxiliary_window(
                window_id, "Regular Polygon Calculator"
            )
            window.set_content(calculator_panel)
            window.setMinimumSize(900, 600)
            window.show()

            # Directly set the values in the calculator panel
            try:
                # First set the number of sides
                print(f"Setting sides to {self.selected_sides}")
                calculator_panel.sides_spin.setValue(self.selected_sides)

                # Then set the value in the selected field
                print(f"Setting {self.selected_field} to {self.value}")
                if self.selected_field == "Radius":
                    calculator_panel.radius_spin.setValue(self.value)
                elif self.selected_field == "Edge Length":
                    calculator_panel.edge_length_spin.setValue(self.value)
                elif self.selected_field == "Perimeter":
                    calculator_panel.perimeter_spin.setValue(self.value)
                elif self.selected_field == "Area":
                    calculator_panel.area_spin.setValue(self.value)
                elif self.selected_field == "Inradius":
                    calculator_panel.inradius_spin.setValue(self.value)
                elif self.selected_field == "Incircle Circumference":
                    calculator_panel.incircle_circumference_spin.setValue(self.value)
                elif self.selected_field == "Incircle Area":
                    calculator_panel.incircle_area_spin.setValue(self.value)
                elif self.selected_field == "Circumradius":
                    calculator_panel.radius_spin_display.setValue(self.value)
                elif self.selected_field == "Circumcircle Circumference":
                    calculator_panel.circumcircle_circumference_spin.setValue(
                        self.value
                    )
                elif self.selected_field == "Circumcircle Area":
                    calculator_panel.circumcircle_area_spin.setValue(self.value)
                print("Successfully set values")
            except Exception as e:
                print(f"Error setting values: {e}")

            print(
                f"Set {self.selected_sides} sides and value {self.value} to {self.selected_field}"
            )

        except Exception as e:
            print(f"Error creating window or panel: {e}")
