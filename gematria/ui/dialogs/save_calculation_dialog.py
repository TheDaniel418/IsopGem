"""Save Calculation Dialog.

This module provides a dialog for saving calculations with tags, notes, and favorite status.
"""


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gematria.models.tag import Tag
from gematria.services.calculation_database_service import CalculationDatabaseService
from shared.ui.widgets.common_widgets import ColorSquare


class TagWidget(QWidget):
    """Widget for displaying a tag."""

    def __init__(self, tag: Tag, parent=None):
        """Initialize with a tag.

        Args:
            tag: Tag to display
            parent: Parent widget
        """
        super().__init__(parent)

        # Store the tag
        self.tag = tag

        # Initialize UI
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        # Color square
        color_square = ColorSquare(tag.color, size=12)
        layout.addWidget(color_square)

        # Tag name
        name_label = QLabel(tag.name)
        name_label.setStyleSheet("font-size: 10px;")
        layout.addWidget(name_label)

        # Style the widget
        self.setStyleSheet(
            """
            background-color: #f0f0f0;
            border-radius: 2px;
        """
        )


class SaveCalculationDialog(QDialog):
    """Dialog for saving calculations."""

    def __init__(self, calculation_value, input_text, method_name, parent=None):
        """Initialize the dialog.

        Args:
            calculation_value: The calculated value
            input_text: The input text
            method_name: The calculation method used
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Save Calculation")
        self.resize(500, 500)

        # Store parameters
        self.calculation_value = calculation_value
        self.input_text = input_text
        self.method_name = method_name

        # Initialize the database service for accessing tags
        self.db_service = CalculationDatabaseService()

        # Dialog result values
        self.selected_tags = []
        self.notes = ""
        self.is_favorite = False

        # Initialize UI
        self._init_ui()

        # Load existing tags
        self._load_tags()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Header
        header = QLabel("Save Calculation")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Input summary group
        summary_group = QGroupBox("Calculation Summary")
        summary_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        summary_layout = QVBoxLayout(summary_group)

        # Display the input text, value, and method
        text_label = QLabel(f"<b>Input:</b> {self.input_text}")
        text_label.setWordWrap(True)
        summary_layout.addWidget(text_label)

        value_label = QLabel(f"<b>Value:</b> {self.calculation_value}")
        summary_layout.addWidget(value_label)

        method_label = QLabel(f"<b>Method:</b> {self.method_name}")
        summary_layout.addWidget(method_label)

        layout.addWidget(summary_group)

        # Notes group
        notes_group = QGroupBox("Notes")
        notes_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        notes_layout = QVBoxLayout(notes_group)

        # Notes text area
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText(
            "Enter notes about this calculation (optional)"
        )
        notes_layout.addWidget(self.notes_edit)

        layout.addWidget(notes_group)

        # Tags group
        tags_group = QGroupBox("Tags")
        tags_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        tags_layout = QVBoxLayout(tags_group)

        # Tags display area
        self.tags_container = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(5)
        self.tags_layout.addStretch(1)  # Push tags to the left

        tags_layout.addWidget(self.tags_container)

        # Add button to open tag selection
        tags_button_layout = QHBoxLayout()

        select_tags_btn = QPushButton("Select Tags")
        select_tags_btn.setStyleSheet(
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
        select_tags_btn.clicked.connect(self._select_tags)
        tags_button_layout.addWidget(select_tags_btn)

        # Add new tag button
        new_tag_btn = QPushButton("Create New Tag")
        new_tag_btn.clicked.connect(self._create_tag)
        tags_button_layout.addWidget(new_tag_btn)

        tags_button_layout.addStretch(1)  # Push buttons to the left

        tags_layout.addLayout(tags_button_layout)

        layout.addWidget(tags_group)

        # Favorite checkbox
        self.favorite_check = QCheckBox("Mark as Favorite")
        self.favorite_check.setStyleSheet(
            """
            QCheckBox {
                font-weight: bold;
            }
            QCheckBox::indicator:checked {
                background-color: #f39c12;
            }
        """
        )
        layout.addWidget(self.favorite_check)

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
        save_btn.clicked.connect(self._save_calculation)

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
        """Load existing tags to display in the dialog."""
        # Clear existing tags
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add label if no tags
        if not self.selected_tags:
            label = QLabel("No tags selected")
            label.setStyleSheet("color: #666; font-style: italic;")
            self.tags_layout.addWidget(label)
        else:
            # Add tag widgets
            for tag_id in self.selected_tags:
                tag = self.db_service.get_tag(tag_id)
                if tag:
                    tag_widget = TagWidget(tag)
                    self.tags_layout.addWidget(tag_widget)

        # Add stretch to push tags to the left
        self.tags_layout.addStretch(1)

    def _select_tags(self):
        """Open the tag selection interface."""
        # Import here to avoid circular imports

        # Create a list to store selected tags
        selected_tags = set(self.selected_tags)

        # Get all available tags
        all_tags = self.db_service.get_all_tags()

        # Create dialog with checkboxes for each tag
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Tags")
        dialog.resize(400, 500)

        layout = QVBoxLayout(dialog)

        # Explanation
        explanation = QLabel("Select tags to associate with this calculation:")
        layout.addWidget(explanation)

        # Tag list
        tag_list = QListWidget()
        layout.addWidget(tag_list)

        # Add tags to list
        for tag in all_tags:
            item = QListWidgetItem()

            # Create checkbox widget
            checkbox = QCheckBox(tag.name)
            checkbox.setChecked(tag.id in selected_tags)

            # Create the widget to hold the checkbox and color indicator
            widget = QWidget()
            widget_layout = QHBoxLayout(widget)
            widget_layout.setContentsMargins(5, 2, 5, 2)

            # Add color square
            color_square = ColorSquare(tag.color)
            widget_layout.addWidget(color_square)

            # Add checkbox
            widget_layout.addWidget(checkbox)

            # Add stretch
            widget_layout.addStretch()

            # Set up the list item
            item.setSizeHint(widget.sizeHint())
            tag_list.addItem(item)
            tag_list.setItemWidget(item, widget)

            # Store tag ID in the checkbox
            checkbox.setProperty("tag_id", tag.id)

            # Connect the checkbox change signal
            checkbox.stateChanged.connect(
                lambda state, tid=tag.id: selected_tags.add(tid)
                if state == Qt.CheckState.Checked.value
                else selected_tags.discard(tid)
            )

        # Button to create new tag
        create_btn = QPushButton("Create New Tag")
        create_btn.clicked.connect(
            lambda: self._create_tag_from_dialog(dialog, tag_list, selected_tags)
        )
        layout.addWidget(create_btn)

        # OK/Cancel buttons
        button_layout = QHBoxLayout()

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)

        button_layout.addStretch(1)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update selected tags
            self.selected_tags = list(selected_tags)

            # Refresh tag display
            self._load_tags()

    def _create_tag(self):
        """Create a new tag."""
        # Import here to avoid circular imports
        from gematria.ui.panels.tag_management_panel import TagEditDialog

        dialog = TagEditDialog(parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.tag:
            # Add to selected tags
            if dialog.tag.id not in self.selected_tags:
                self.selected_tags.append(dialog.tag.id)

            # Refresh tag display
            self._load_tags()

    def _create_tag_from_dialog(self, parent_dialog, tag_list, selected_tags):
        """Create a tag from the dialog and add it to the tag list.

        Args:
            parent_dialog: Parent dialog
            tag_list: Tag list widget
            selected_tags: Set of selected tag IDs
        """
        # Use TagEditDialog from tag_selection_dialog
        from gematria.ui.dialogs.tag_selection_dialog import TagEditDialog

        # Create dialog
        dialog = TagEditDialog(parent=parent_dialog)

        # Show dialog and check result
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.tag is not None:
            # Create widget for the new tag
            widget = TagWidget(dialog.tag)

            # Create list item
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())

            # Get checkbox and make it checked
            checkbox = widget.findChild(QCheckBox)
            # Type check before using
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(True)

            # Add to list
            tag_list.addItem(item)
            tag_list.setItemWidget(item, widget)

            # Store tag ID in the checkbox only if it's a QCheckBox
            if dialog.tag is not None and isinstance(checkbox, QCheckBox):
                # We've already checked that dialog.tag is not None, but mypy needs this check
                tag_id = dialog.tag.id
                checkbox.setProperty("tag_id", tag_id)

                # Connect the checkbox change signal
                checkbox.stateChanged.connect(
                    lambda state, tid=tag_id: selected_tags.add(tid)
                    if state == Qt.CheckState.Checked.value
                    else selected_tags.discard(tid)
                )

    def _save_calculation(self):
        """Save the calculation and close the dialog."""
        # Get notes
        self.notes = self.notes_edit.toPlainText().strip()

        # Get favorite status
        self.is_favorite = self.favorite_check.isChecked()

        # Accept the dialog
        self.accept()
