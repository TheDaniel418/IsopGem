"""
Purpose: Provides a dialog for selecting tags to apply to calculation results

This file is part of the gematria pillar and serves as a UI component.
It is responsible for allowing users to select, filter, and manage tags
for their gematria calculations, providing a clean interface for tag management.

Key components:
- TagSelectionDialog: Dialog for selecting and managing tags
- ColorSquare: Visual component for displaying tag colors

Dependencies:
- PyQt6: For the graphical user interface components
- gematria.models.tag: For the Tag data model
- gematria.services.calculation_database_service: For accessing tag and calculation data

Related files:
- gematria/ui/panels/calculation_history_panel.py: Uses this dialog for tag management
- gematria/ui/dialogs/save_calculation_dialog.py: Uses this dialog for tagging calculations
- gematria/models/tag.py: Defines the Tag data model
"""

from typing import Optional, Set

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gematria.models.tag import Tag
from gematria.services.calculation_database_service import CalculationDatabaseService


# Import the ColorSquare class
# Define ColorSquare here to avoid circular imports
class ColorSquare(QLabel):
    """Simple colored square for tag display."""

    def __init__(self, color: str, size: int = 16):
        """Initialize with a color.

        Args:
            color: Hex color code
            size: Square size in pixels
        """
        super().__init__()
        self.setFixedSize(size, size)
        self.setStyleSheet(f"background-color: {color};")


# Define TagEditDialog here to avoid circular imports
class TagEditDialog(QDialog):
    """Dialog for editing a tag."""

    def __init__(self, tag: Optional[Tag] = None, parent=None):
        """Initialize the dialog.

        Args:
            tag: Tag to edit, or None for a new tag
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Create Tag" if tag is None else "Edit Tag")
        self.resize(400, 250)

        # Store the tag
        self.tag = tag

        # Initialize the database service
        self.db_service = CalculationDatabaseService()

        # Initialize UI
        self._init_ui()

        # If editing, populate with tag data
        if self.tag:
            self._populate_fields()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Tag properties form
        form_layout = QFormLayout()

        # Name field
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter tag name")
        form_layout.addRow("Name:", self.name_edit)

        # Color selection
        self.color_combo = QComboBox()

        # Add some preset colors
        colors = [
            ("#3498db", "Blue"),
            ("#e74c3c", "Red"),
            ("#2ecc71", "Green"),
            ("#f39c12", "Orange"),
            ("#9b59b6", "Purple"),
            ("#1abc9c", "Turquoise"),
            ("#34495e", "Dark Blue"),
            ("#7f8c8d", "Gray"),
            ("#d35400", "Pumpkin"),
            ("#27ae60", "Emerald"),
        ]

        for color_hex, color_name in colors:
            # Create a color square icon
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(color_hex))

            self.color_combo.addItem(QIcon(pixmap), color_name, color_hex)

        form_layout.addRow("Color:", self.color_combo)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter tag description (optional)")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)

        layout.addLayout(form_layout)

        # Preview
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        preview_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 4px;")

        preview_layout = QVBoxLayout(preview_frame)

        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(preview_label)

        self.preview_widget = QWidget()
        self.preview_layout = QHBoxLayout(self.preview_widget)
        self.preview_layout.setContentsMargins(5, 5, 5, 5)

        # Initial preview
        preview_color = ColorSquare("#3498db")
        self.preview_layout.addWidget(preview_color)

        self.preview_name = QLabel("Tag Name")
        self.preview_name.setStyleSheet("font-weight: bold;")
        self.preview_layout.addWidget(self.preview_name)

        preview_layout.addWidget(self.preview_widget)
        layout.addWidget(preview_frame)

        # Connect signals to update preview
        self.name_edit.textChanged.connect(self._update_preview)
        self.color_combo.currentIndexChanged.connect(self._update_preview)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Save" if self.tag else "Create")
        save_btn.setStyleSheet(
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
        save_btn.clicked.connect(self._save_tag)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch(1)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _populate_fields(self):
        """Populate the fields with tag data."""
        if not self.tag:
            return

        self.name_edit.setText(self.tag.name)
        self.description_edit.setText(self.tag.description or "")

        # Find and select the color
        for i in range(self.color_combo.count()):
            if self.color_combo.itemData(i) == self.tag.color:
                self.color_combo.setCurrentIndex(i)
                break

        # Update preview
        self._update_preview()

    def _update_preview(self):
        """Update the tag preview."""
        # Clear the preview layout
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get current values
        name = self.name_edit.text() or "Tag Name"
        color = self.color_combo.currentData() or "#3498db"

        # Create preview
        preview_color = ColorSquare(color)
        self.preview_layout.addWidget(preview_color)

        preview_name = QLabel(name)
        preview_name.setStyleSheet("font-weight: bold;")
        self.preview_layout.addWidget(preview_name)

    def _save_tag(self):
        """Save the tag."""
        # Get tag data
        name = self.name_edit.text().strip()
        color = self.color_combo.currentData()
        description = self.description_edit.toPlainText().strip()

        # Validate
        if not name:
            QMessageBox.warning(self, "Validation Error", "Tag name cannot be empty")
            return

        # If editing existing tag
        if self.tag:
            self.tag.name = name
            self.tag.color = color
            self.tag.description = description or None

            # Update in database
            if self.db_service.update_tag(self.tag):
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to update tag")
        else:
            # Create new tag
            tag = self.db_service.create_tag(
                name=name, color=color, description=description or None
            )

            if tag:
                # Store the created tag for access by the caller
                self.tag = tag
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to create tag")


class TagSelectionDialog(QDialog):
    """Dialog for selecting tags to add to a calculation."""

    def __init__(self, calculation_id: str, parent=None):
        """Initialize the dialog.

        Args:
            calculation_id: ID of the calculation to add tags to
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Select Tags")
        self.resize(400, 500)

        # Store the calculation ID
        self.calculation_id = calculation_id

        # Initialize the database service
        self.db_service = CalculationDatabaseService()

        # Current selection
        self.selected_tags: Set[str] = set()

        # Initialize UI
        self._init_ui()

        # Load tags
        self._load_tags()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header
        header = QLabel("Select Tags")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Explanation
        explanation = QLabel(
            "Select tags to add to this calculation. "
            "You can select multiple tags or create new ones."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tags...")
        self.search_input.textChanged.connect(self._filter_tags)
        layout.addWidget(self.search_input)

        # Tag list
        self.tag_list = QListWidget()
        self.tag_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 4px;
            }
        """
        )
        layout.addWidget(self.tag_list)

        # Buttons for managing tags
        manage_layout = QHBoxLayout()

        # Create button
        create_btn = QPushButton("Create New Tag")
        create_btn.clicked.connect(self._create_tag)
        manage_layout.addWidget(create_btn)

        manage_layout.addStretch(1)

        layout.addLayout(manage_layout)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(
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
        save_btn.clicked.connect(self._save_tags)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch(1)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def _load_tags(self):
        """Load tags from the database."""
        # Clear the list
        self.tag_list.clear()

        # Get all tags
        all_tags = self.db_service.get_all_tags()

        # Get tags for the calculation
        calculation = self.db_service.get_calculation(self.calculation_id)
        if calculation and calculation.tags:
            self.selected_tags = set(calculation.tags)
        else:
            self.selected_tags = set()

        # Sort tags by name
        all_tags.sort(key=lambda t: t.name)

        # Add to list
        for tag in all_tags:
            self._add_tag_to_list(tag)

    def _add_tag_to_list(self, tag: Tag):
        """Add a tag to the list.

        Args:
            tag: Tag to add
        """
        # Create widget
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(tag.id in self.selected_tags)
        checkbox.stateChanged.connect(
            lambda state, tid=tag.id: self._on_tag_checked(tid, state)
        )
        layout.addWidget(checkbox)

        # Color square
        color_square = ColorSquare(tag.color)
        layout.addWidget(color_square)

        # Tag name
        name_label = QLabel(tag.name)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        # Description (if available)
        if tag.description:
            # Spacer
            layout.addStretch(1)

            description_label = QLabel(tag.description)
            description_label.setStyleSheet("color: #666;")
            description_label.setWordWrap(True)
            layout.addWidget(description_label)

        # Create item
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, tag.id)
        item.setSizeHint(widget.sizeHint())

        # Add to list
        self.tag_list.addItem(item)
        self.tag_list.setItemWidget(item, widget)

    def _filter_tags(self):
        """Filter tags based on search input."""
        search_text = self.search_input.text().strip().lower()

        # No search text, show all
        if not search_text:
            for i in range(self.tag_list.count()):
                self.tag_list.item(i).setHidden(False)
            return

        # Filter items
        for i in range(self.tag_list.count()):
            item = self.tag_list.item(i)
            widget = self.tag_list.itemWidget(item)

            # Get tag name from the label (third widget in layout)
            tag_name = ""
            layout = widget.layout()
            for j in range(layout.count()):
                widget_item = layout.itemAt(j).widget()
                if isinstance(widget_item, QLabel):
                    tag_name = widget_item.text().lower()
                    break

            # Show/hide based on search
            item.setHidden(search_text not in tag_name)

    def _on_tag_checked(self, tag_id: str, state: int):
        """Handle tag checkbox state change.

        Args:
            tag_id: ID of the tag
            state: Checkbox state
        """
        if state == Qt.CheckState.Checked.value:
            self.selected_tags.add(tag_id)
        else:
            self.selected_tags.discard(tag_id)

    def _create_tag(self):
        """Create a new tag."""
        # Use the local TagEditDialog class
        dialog = TagEditDialog(parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.tag:
            # Add to selected tags
            self.selected_tags.add(dialog.tag.id)

            # Refresh the list
            self._load_tags()

    def _save_tags(self):
        """Save the selected tags."""
        # Get the calculation
        calculation = self.db_service.get_calculation(self.calculation_id)
        if not calculation:
            QMessageBox.warning(self, "Error", "Could not find calculation")
            return

        # Update calculation in-memory with the selected tags
        calculation.tags = list(self.selected_tags)

        # Save to database for immediate effect
        # This updates the database but the parent window will handle the final save
        if self.db_service.save_calculation(calculation):
            self.accept()  # Close dialog with accept status
        else:
            QMessageBox.warning(self, "Error", "Failed to save tags")

    def get_selected_tags(self) -> Set[str]:
        """Get the currently selected tags.

        Returns:
            Set of selected tag IDs
        """
        return self.selected_tags.copy()
