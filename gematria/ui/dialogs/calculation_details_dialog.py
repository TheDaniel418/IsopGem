"""
Purpose: Provides a detailed view of saved calculation results with editing capabilities

This file is part of the gematria pillar and serves as a UI component.
It is responsible for displaying detailed information about a calculation result,
including its input text, result value, calculation method, notes, and tags.
It allows users to edit notes, manage tags, and toggle favorite status.

Key components:
- CalculationDetailsDialog: Dialog for displaying and editing calculation details

Dependencies:
- PyQt6: For building the graphical user interface
- gematria.models: For working with calculation data
- gematria.services: For data access and persistence
- shared.services: For service access

Related files:
- gematria/ui/panels/calculation_history_panel.py: Panel that shows this dialog
- gematria/services/calculation_database_service.py: Service for data operations
"""


from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_result import CalculationResult
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.ui.dialogs.tag_selection_dialog import TagSelectionDialog
from shared.services.service_locator import ServiceLocator
from shared.services.tag_service import TagService


class CalculationDetailsDialog(QDialog):
    """Dialog for displaying and editing calculation details."""

    # Signal emitted when a calculation is updated
    calculationUpdated = pyqtSignal()

    def __init__(
        self, calculation: CalculationResult, calculation_service=None, parent=None
    ):
        """Initialize the dialog with a calculation.

        Args:
            calculation: The calculation to display
            calculation_service: Optional service for calculation operations. If None, will be retrieved from ServiceLocator.
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Calculation Details")

        # Store calculation
        self.calculation = calculation

        # Get services
        self.calculation_service = calculation_service or ServiceLocator.get(
            CalculationDatabaseService
        )
        self.tag_service = ServiceLocator.get(TagService)

        # Get tags for calculation
        self.tags = []
        if calculation.tags:
            for tag_id in calculation.tags:
                tag = self.tag_service.get_tag(tag_id)
                if tag:
                    self.tags.append(tag)

        # Initialize UI
        self._init_ui()

        # Set window properties
        self.resize(600, 500)
        self.setModal(True)

    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Input and result section
        input_group = QGroupBox("Calculation")
        input_layout = QVBoxLayout(input_group)

        # Input text
        input_label = QLabel("Input:")
        input_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        input_layout.addWidget(input_label)

        input_text = QLabel(self.calculation.input_text)
        input_text.setWordWrap(True)
        input_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        input_layout.addWidget(input_text)

        # Result value
        result_label = QLabel("Result:")
        result_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        input_layout.addWidget(result_label)

        result_text = QLabel(str(self.calculation.result_value))
        result_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        result_text.setFont(QFont("Arial", 14))
        input_layout.addWidget(result_text)

        # Method
        method_label = QLabel("Method:")
        method_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        input_layout.addWidget(method_label)

        method_text = QLabel(self._get_method_name())
        method_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        input_layout.addWidget(method_text)

        # Timestamp
        timestamp_label = QLabel("Date:")
        timestamp_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        input_layout.addWidget(timestamp_label)

        timestamp_text = QLabel(
            self.calculation.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        )
        timestamp_text.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        input_layout.addWidget(timestamp_text)

        layout.addWidget(input_group)

        # Tags section
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout(tags_group)

        self.tags_container = QWidget()
        self.tags_container_layout = QVBoxLayout(self.tags_container)
        self.tags_container_layout.setContentsMargins(0, 0, 0, 0)
        self._display_tags()

        tags_scroll = QScrollArea()
        tags_scroll.setWidgetResizable(True)
        tags_scroll.setWidget(self.tags_container)
        tags_layout.addWidget(tags_scroll)

        # Add buttons for tag management
        tags_button_layout = QHBoxLayout()

        self.edit_tags_button = QPushButton("Edit Tags")
        self.edit_tags_button.clicked.connect(self._on_edit_tags)
        tags_button_layout.addWidget(self.edit_tags_button)

        tags_layout.addLayout(tags_button_layout)
        layout.addWidget(tags_group)

        # Notes section
        notes_group = QGroupBox("Notes")
        notes_layout = QVBoxLayout(notes_group)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Add notes about this calculation...")
        if self.calculation.notes:
            self.notes_edit.setText(self.calculation.notes)
        notes_layout.addWidget(self.notes_edit)

        # Save notes button
        save_notes_button = QPushButton("Save Notes")
        save_notes_button.clicked.connect(self._on_save_notes)
        notes_layout.addWidget(save_notes_button)

        layout.addWidget(notes_group)

        # Favorite toggle and close buttons
        button_layout = QHBoxLayout()

        self.favorite_button = QPushButton(
            "★ Favorite" if self.calculation.favorite else "☆ Add to Favorites"
        )
        self.favorite_button.clicked.connect(self._on_toggle_favorite)
        if self.calculation.favorite:
            self.favorite_button.setStyleSheet("color: gold;")
        button_layout.addWidget(self.favorite_button)

        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _get_method_name(self) -> str:
        """Get a readable name for the calculation method.

        Returns:
            Readable method name
        """
        if (
            hasattr(self.calculation, "custom_method_name")
            and self.calculation.custom_method_name
        ):
            return self.calculation.custom_method_name

        if hasattr(self.calculation.calculation_type, "name"):
            # It's an enum, use its name
            return self.calculation.calculation_type.name.replace("_", " ").title()

        # It's a string, make it readable
        return str(self.calculation.calculation_type).replace("_", " ").title()

    def _display_tags(self):
        """Display tags in the tags container."""
        # Clear existing tags
        for i in reversed(range(self.tags_container_layout.count())):
            widget = self.tags_container_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add tags
        if self.tags:
            for tag in self.tags:
                tag_widget = QWidget()
                tag_layout = QHBoxLayout(tag_widget)
                tag_layout.setContentsMargins(0, 2, 0, 2)

                # Color indicator
                color_widget = QLabel()
                color_widget.setFixedSize(16, 16)
                color_widget.setStyleSheet(
                    f"background-color: {tag.color}; border-radius: 8px;"
                )
                tag_layout.addWidget(color_widget)

                # Tag name
                name_label = QLabel(tag.name)
                name_label.setFont(QFont("Arial", 10))
                tag_layout.addWidget(name_label)

                # Tag description (if available)
                if tag.description:
                    tag_layout.addStretch()
                    desc_label = QLabel(tag.description)
                    desc_label.setStyleSheet("color: #666;")
                    tag_layout.addWidget(desc_label)

                tag_layout.addStretch()
                self.tags_container_layout.addWidget(tag_widget)
        else:
            # No tags message
            no_tags = QLabel("No tags associated with this calculation")
            no_tags.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_tags.setStyleSheet("color: #999; margin: 10px;")
            self.tags_container_layout.addWidget(no_tags)

    def _on_edit_tags(self):
        """Handle edit tags button click."""
        # Get currently selected tag IDs
        selected_tag_ids = [tag.id for tag in self.tags]

        # Show tag selection dialog
        dialog = TagSelectionDialog(selected_tag_ids, self)
        if dialog.exec():
            # Get newly selected tags
            new_tag_ids = dialog.selected_tag_ids

            # Update calculation
            self.calculation.tags = new_tag_ids
            success = self.calculation_service.save_calculation(self.calculation)

            if success:
                # Refresh tags display
                self.tags = []
                for tag_id in new_tag_ids:
                    tag = self.tag_service.get_tag(tag_id)
                    if tag:
                        self.tags.append(tag)

                self._display_tags()
                self.calculationUpdated.emit()
            else:
                QMessageBox.warning(self, "Error", "Failed to update tags")

    def _on_save_notes(self):
        """Handle save notes button click."""
        # Get notes text
        notes = self.notes_edit.toPlainText()

        # Update calculation
        self.calculation.notes = notes
        success = self.calculation_service.save_calculation(self.calculation)

        if success:
            QMessageBox.information(self, "Success", "Notes saved successfully")
            self.calculationUpdated.emit()
        else:
            QMessageBox.warning(self, "Error", "Failed to save notes")

    def _on_toggle_favorite(self):
        """Handle toggle favorite button click."""
        # Toggle favorite status
        new_favorite = not self.calculation.favorite
        self.calculation.favorite = new_favorite

        # Update calculation
        success = self.calculation_service.save_calculation(self.calculation)

        if success:
            # Update button text and style
            self.favorite_button.setText(
                "★ Favorite" if new_favorite else "☆ Add to Favorites"
            )
            if new_favorite:
                self.favorite_button.setStyleSheet("color: gold;")
            else:
                self.favorite_button.setStyleSheet("")

            self.calculationUpdated.emit()
        else:
            QMessageBox.warning(self, "Error", "Failed to update favorite status")
