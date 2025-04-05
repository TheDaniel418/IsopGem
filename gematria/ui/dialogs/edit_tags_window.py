"""
Purpose: Provides a window for managing tags associated with calculations

This file is part of the gematria pillar and serves as a UI component.
It is responsible for allowing users to view and modify the tags associated
with a specific calculation, providing a dedicated interface for tag management.

Key components:
- EditTagsWindow: Window for viewing and editing calculation tags

Dependencies:
- PyQt6: For the graphical user interface components
- gematria.models.calculation_result: For the calculation data structure
- gematria.services.calculation_database_service: For accessing calculation and tag data
- gematria.ui.dialogs.tag_selection_dialog: For selecting tags

Related files:
- gematria/ui/panels/calculation_history_panel.py: Uses this window for tag management
- gematria/ui/dialogs/tag_selection_dialog.py: Used by this window for tag selection
- gematria/models/calculation_result.py: Defines the calculation data model
"""

from typing import Set

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gematria.models.tag import Tag
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.ui.dialogs.tag_selection_dialog import TagSelectionDialog


class EditTagsWindow(QMainWindow):
    """Window for editing tags for a calculation."""

    def __init__(self, calculation_id: str, parent=None):
        """Initialize the window.

        Args:
            calculation_id: ID of the calculation to edit tags for
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Tags")
        self.resize(500, 600)

        # Store the calculation ID
        self.calculation_id = calculation_id

        # Initialize the database service
        self.db_service = CalculationDatabaseService()

        # Track selected tags
        self.selected_tags: Set[str] = set()

        # Initialize UI
        self._init_ui()

        # Load the calculation
        self._load_calculation()

    def _init_ui(self):
        """Initialize the UI components."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header
        header = QLabel("Edit Tags")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Calculation info
        self.calculation_info = QLabel()
        layout.addWidget(self.calculation_info)

        # Current tags
        tags_header = QLabel("Current Tags:")
        tags_header.setStyleSheet("font-weight: bold;")
        layout.addWidget(tags_header)

        self.tag_list = QListWidget()
        self.tag_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                min-height: 100px;
            }
            QListWidget::item {
                padding: 4px;
            }
        """
        )
        layout.addWidget(self.tag_list)

        # Buttons
        button_layout = QHBoxLayout()

        # Select tags button
        self.edit_tags_btn = QPushButton("Select Tags")
        self.edit_tags_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        self.edit_tags_btn.clicked.connect(self._edit_tags)
        button_layout.addWidget(self.edit_tags_btn)

        # Apply button
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """
        )
        self.apply_btn.clicked.connect(self._apply_changes)
        button_layout.addWidget(self.apply_btn)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )

        # Connect to a void function that calls close
        def close_window() -> None:
            self.close()

        self.close_btn.clicked.connect(close_window)
        button_layout.addWidget(self.close_btn)

        # Add button layout
        layout.addLayout(button_layout)

    def _load_calculation(self):
        """Load the calculation from the database."""
        # Get calculation
        calculation = self.db_service.get_calculation(self.calculation_id)
        if not calculation:
            QMessageBox.warning(self, "Error", "Could not find calculation")
            self.close()
            return

        # Initialize selected tags from calculation
        if calculation.tags:
            self.selected_tags = set(calculation.tags)
        else:
            self.selected_tags = set()

        # Determine method name safely
        method_name = "Unknown"
        if (
            hasattr(calculation, "custom_method_name")
            and calculation.custom_method_name
        ):
            method_name = calculation.custom_method_name
        elif hasattr(calculation.calculation_type, "name"):
            method_name = calculation.calculation_type.name.replace("_", " ").title()
        elif isinstance(calculation.calculation_type, str):
            method_name = calculation.calculation_type.replace("_", " ").title()

        # Update calculation info
        self.calculation_info.setText(
            f"<b>Text:</b> {calculation.input_text}<br>"
            f"<b>Value:</b> {calculation.result_value}<br>"
            f"<b>Method:</b> {method_name}<br>"
            f"<b>Created:</b> {calculation.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Load tags
        self._load_tags()

    def _load_tags(self):
        """Load tags for the calculation."""
        # Clear the list
        self.tag_list.clear()

        # Get tags for the calculation
        if not self.selected_tags:
            self.tag_list.addItem("No tags assigned to this calculation")
            return

        for tag_id in self.selected_tags:
            tag = self.db_service.get_tag(tag_id)
            if tag:
                item = QListWidgetItem(f"{tag.name}")
                item.setData(Qt.ItemDataRole.UserRole, tag.id)

                # Set item styling
                item.setBackground(Qt.GlobalColor.transparent)
                item.setForeground(Qt.GlobalColor.black)
                item.setToolTip(tag.description or "")

                self.tag_list.addItem(item)

    def _edit_tags(self):
        """Edit tags for the calculation."""
        # Show tag selection dialog
        dialog = TagSelectionDialog(self.calculation_id, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get the selected tags from the dialog
            self.selected_tags = dialog.get_selected_tags()

            # Reload the tags UI
            self._load_tags()

    def _toggle_tag(self, tag_id: str) -> None:
        """Toggle selection of a tag."""
        if tag_id in self.selected_tags:
            self.selected_tags.remove(tag_id)
        else:
            self.selected_tags.add(tag_id)
        self._load_tags()

    def _apply_changes(self) -> None:
        """Apply tag changes to the calculation."""
        try:
            # Update calculation
            calculation = self.db_service.get_calculation(self.calculation_id)
            if not calculation:
                QMessageBox.critical(self, "Error", "Calculation not found.")
                return
            # Set the tags
            calculation.tags = list(self.selected_tags)
            # Save changes
            if self.db_service.save_calculation(calculation):
                QMessageBox.information(self, "Success", "Tags updated successfully.")
                # Optionally close the window
                # self.close()
            else:
                QMessageBox.critical(self, "Error", "Failed to save changes.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def _create_tag(self) -> None:
        """Create a new tag."""
        # Open create tag dialog
        from gematria.ui.dialogs.create_tag_dialog import CreateTagDialog

        dialog = CreateTagDialog(self)

        # Connect to tag_created signal
        def on_tag_created(tag: Tag) -> None:
            """Handle tag created signal."""
            if tag:
                # Add to selected tags
                self.selected_tags.add(tag.id)
                # Reload tags
                self._load_tags()
                # Notify user
                QMessageBox.information(
                    self, "Success", f"Tag '{tag.name}' created successfully."
                )

        dialog.tag_created.connect(on_tag_created)
        dialog.exec()
