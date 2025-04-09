"""Tag Management Panel.

This module provides a panel for managing tags used to organize gematria calculations.
"""

from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QFrame,
    QSizePolicy,
    QInputDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap

from loguru import logger

from gematria.models.tag import Tag
from gematria.services.calculation_database_service import CalculationDatabaseService
from shared.ui.widgets.common_widgets import ColorSquare


class TagListItem(QWidget):
    """Widget for displaying a tag in a list."""

    def __init__(self, tag: Tag, parent=None):
        """Initialize with a tag.

        Args:
            tag: Tag to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.tag = tag

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Color square
        color_square = ColorSquare(tag.color)
        layout.addWidget(color_square)

        # Tag name label
        name_label = QLabel(tag.name)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        # Spacer
        layout.addStretch(1)

        # Description (if available)
        if tag.description:
            description_label = QLabel(tag.description)
            description_label.setStyleSheet("color: #666;")
            description_label.setMaximumWidth(300)
            description_label.setWordWrap(True)
            layout.addWidget(description_label)

        # Set the tag as the widget's data
        self.setProperty("tag_id", tag.id)


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
                logger.debug(f"Updated tag: {self.tag.name}")
                self.accept()
            else:
                logger.error(f"Failed to update tag: {self.tag.name}")
                QMessageBox.warning(self, "Error", "Failed to update tag")
        else:
            # Create new tag
            tag = self.db_service.create_tag(
                name=name, color=color, description=description or None
            )

            if tag:
                logger.debug(f"Created tag: {tag.name}")
                # Store the created tag for access by the caller
                self.tag = tag
                self.accept()
            else:
                logger.error("Failed to create tag")
                QMessageBox.warning(self, "Error", "Failed to create tag")


class TagManagementPanel(QWidget):
    """Panel for managing tags."""

    tags_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the tag management panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initialize the database service
        self.db_service = CalculationDatabaseService()

        # Initialize UI
        self._init_ui()

        # Load tags
        self._load_tags()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header = QLabel("Tag Management")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Description
        description = QLabel(
            "Create and manage tags to organize your calculations. "
            "Tags can be added to calculations and used for filtering and searching."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Tag list
        self.tag_list = QListWidget()
        self.tag_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QListWidget::item {
                border-bottom: 1px solid #eee;
                padding: 4px;
            }
            QListWidget::item:selected {
                background-color: #e0f2fe;
                color: #1a1a1a;
            }
        """
        )
        self.tag_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.tag_list.itemSelectionChanged.connect(self._selection_changed)

        layout.addWidget(self.tag_list)

        # Buttons
        button_layout = QHBoxLayout()

        self.create_btn = QPushButton("Create Tag")
        self.create_btn.setStyleSheet(
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
        self.create_btn.clicked.connect(self._create_tag)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self._edit_tag)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setEnabled(False)
        self.delete_btn.setStyleSheet(
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
        self.delete_btn.clicked.connect(self._delete_tag)

        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch(1)

        layout.addLayout(button_layout)

        # Usage stats
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.stats_label)

    def _load_tags(self):
        """Load tags from the database."""
        # Clear the list
        self.tag_list.clear()

        # Get all tags
        tags = self.db_service.get_all_tags()

        # Create default tags if none exist
        if not tags:
            self.db_service.tag_repo.create_default_tags()
            tags = self.db_service.get_all_tags()

        # Sort tags by name
        tags.sort(key=lambda t: t.name)

        # Add to list
        for tag in tags:
            # Create a custom widget for the tag
            tag_widget = TagListItem(tag)

            # Create a list item and set its size
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, tag.id)
            item.setSizeHint(tag_widget.sizeHint())

            # Add to list
            self.tag_list.addItem(item)
            self.tag_list.setItemWidget(item, tag_widget)

        # Update stats
        self._update_stats()

    def _update_stats(self):
        """Update usage statistics."""
        tags = self.db_service.get_all_tags()

        # Display number of tags and total calculations using tags
        total_tag_usages = 0
        tag_usage = {}

        for tag in tags:
            calculations = self.db_service.find_calculations_by_tag(tag.id)
            tag_usage[tag.id] = len(calculations)
            total_tag_usages += len(calculations)

        self.stats_label.setText(
            f"{len(tags)} tags defined, used in {total_tag_usages} calculations"
        )

    def _get_selected_tag(self) -> Optional[Tag]:
        """Get the currently selected tag.

        Returns:
            Selected tag or None if no tag is selected
        """
        selected_items = self.tag_list.selectedItems()
        if not selected_items:
            return None

        tag_id = selected_items[0].data(Qt.ItemDataRole.UserRole)
        return self.db_service.get_tag(tag_id)

    def _selection_changed(self):
        """Handle tag selection change."""
        tag = self._get_selected_tag()

        # Enable/disable buttons based on selection
        self.edit_btn.setEnabled(tag is not None)
        self.delete_btn.setEnabled(tag is not None)

    def _create_tag(self):
        """Create a new tag."""
        dialog = TagEditDialog(parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh the tag list
            self._load_tags()

            # Notify listeners
            self.tags_changed.emit()

    def _edit_tag(self):
        """Edit the selected tag."""
        tag = self._get_selected_tag()
        if not tag:
            return

        dialog = TagEditDialog(tag, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh the tag list
            self._load_tags()

            # Notify listeners
            self.tags_changed.emit()

    def _delete_tag(self):
        """Delete the selected tag."""
        tag = self._get_selected_tag()
        if not tag:
            return

        # Get tag usage count
        calculations = self.db_service.find_calculations_by_tag(tag.id)

        # Confirmation message with warning if tag is in use
        message = f"Are you sure you want to delete the tag '{tag.name}'?"
        if calculations:
            message += f"\n\nThis tag is used in {len(calculations)} calculations. Deleting it will remove the tag from these calculations."

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            if self.db_service.delete_tag(tag.id):
                # Refresh the tag list
                self._load_tags()

                # Notify listeners
                self.tags_changed.emit()

                QMessageBox.information(
                    self, "Success", f"Tag '{tag.name}' deleted successfully"
                )
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete tag '{tag.name}'")
