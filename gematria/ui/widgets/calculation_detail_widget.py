"""Widget for displaying calculation details.

This module provides a widget for displaying detailed information about a calculation result.
"""

from typing import Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import get_calculation_type_name
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.ui.dialogs.edit_tags_window import EditTagsWindow
from shared.ui.widgets.rtf_editor.rich_text_editor_widget import RichTextEditorWidget

# Import the TQ analysis service for sending numbers to Quadset Analysis
try:
    from tq.services import tq_analysis_service

    TQ_AVAILABLE = True
except ImportError:
    TQ_AVAILABLE = False


class CalculationDetailWidget(QWidget):
    """Widget for displaying detailed information about a calculation result."""

    calculation_updated = pyqtSignal(CalculationResult)

    def __init__(
        self,
        calculation_db_service: CalculationDatabaseService,
        custom_cipher_service: CustomCipherService,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Initialize the calculation detail widget.

        Args:
            calculation_db_service: Service for database operations
            custom_cipher_service: Service for custom cipher operations
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculation_db_service = calculation_db_service
        self.custom_cipher_service = custom_cipher_service
        self.calculation: Optional[CalculationResult] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Title
        self.title_label = QLabel("Calculation Details")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)

        # Main container
        main_layout = QHBoxLayout()

        # Left side - Basic info
        left_group = QGroupBox("Basic Information")
        form_layout = QFormLayout(left_group)

        self.input_label = QLabel()
        form_layout.addRow("Input:", self.input_label)

        self.value_label = QLabel()
        form_layout.addRow("Value:", self.value_label)

        self.method_label = QLabel()
        form_layout.addRow("Method:", self.method_label)

        self.date_label = QLabel()
        form_layout.addRow("Date:", self.date_label)

        self.favorite_checkbox = QCheckBox("Favorite")
        self.favorite_checkbox.toggled.connect(self._on_favorite_toggled)
        form_layout.addRow("", self.favorite_checkbox)

        # Add TQ Analysis button
        if TQ_AVAILABLE:
            self.tq_analysis_btn = QPushButton("Send to Quadset Analysis")
            self.tq_analysis_btn.setToolTip("Analyze this number in the TQ Grid")
            self.tq_analysis_btn.clicked.connect(self._send_to_quadset_analysis)
            form_layout.addRow("", self.tq_analysis_btn)

        main_layout.addWidget(left_group)

        # Right side - Notes and tags
        right_group = QGroupBox("Notes and Tags")
        right_layout = QVBoxLayout(right_group)

        # Notes area
        notes_label = QLabel("Notes:")
        self.notes_edit = RichTextEditorWidget(
            parent=self,
            show_menubar=False,  # No menu bar in widget
            show_statusbar=True,  # Show status bar for word count
            compact_mode=True    # Use compact mode for widget
        )
        self.notes_edit.get_text_edit().setPlaceholderText("Enter notes about this calculation using rich text formatting...")
        right_layout.addWidget(notes_label)
        right_layout.addWidget(self.notes_edit)

        # Tags area
        tags_layout = QHBoxLayout()
        tags_label = QLabel("Tags:")
        self.tags_label = QLabel()
        self.tags_label.setWordWrap(True)
        self.edit_tags_btn = QPushButton("Edit Tags")
        self.edit_tags_btn.clicked.connect(self._edit_tags)

        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self.tags_label, 1)  # Give it stretch
        tags_layout.addWidget(self.edit_tags_btn)

        right_layout.addLayout(tags_layout)

        # Buttons for notes
        notes_btn_layout = QHBoxLayout()
        self.save_notes_btn = QPushButton("Save Notes")
        self.save_notes_btn.clicked.connect(self._save_notes)

        notes_btn_layout.addStretch()
        notes_btn_layout.addWidget(self.save_notes_btn)
        right_layout.addLayout(notes_btn_layout)

        main_layout.addWidget(right_group)

        layout.addLayout(main_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Delete button
        delete_layout = QHBoxLayout()
        self.delete_btn = QPushButton("Delete Calculation")
        self.delete_btn.clicked.connect(self._delete_calculation)

        delete_layout.addStretch()
        delete_layout.addWidget(self.delete_btn)
        layout.addLayout(delete_layout)

    def set_calculation(self, calculation: CalculationResult) -> None:
        """Set the calculation to display.

        Args:
            calculation: The calculation result to display
        """
        self.calculation = calculation
        self._update_display()

    def _update_display(self) -> None:
        """Update the display with the current calculation."""
        if not self.calculation:
            return

        # Update basic info
        self.input_label.setText(self.calculation.input_text)
        self.value_label.setText(str(self.calculation.result_value))

        # Method name
        if self.calculation.custom_method_name:
            method_name = f"Custom: {self.calculation.custom_method_name}"
        else:
            method_name = get_calculation_type_name(self.calculation.calculation_type)
        self.method_label.setText(method_name)

        # Date
        date_str = (
            self.calculation.created_at.strftime("%Y-%m-%d %H:%M")
            if self.calculation.created_at
            else "Unknown"
        )
        self.date_label.setText(date_str)

        # Favorite
        self.favorite_checkbox.setChecked(self.calculation.favorite)

        # Notes
        if self.calculation.notes:
            # Check if notes contain HTML formatting
            if '<' in self.calculation.notes and '>' in self.calculation.notes:
                self.notes_edit.set_html(self.calculation.notes)
            else:
                self.notes_edit.set_plain_text(self.calculation.notes)
        else:
            self.notes_edit.set_plain_text("")

        # Tags
        tag_names = self.calculation_db_service.get_calculation_tag_names(
            self.calculation
        )
        self.tags_label.setText(", ".join(tag_names) if tag_names else "No tags")

        # Enable/disable TQ Analysis button based on whether the result is a valid integer
        if TQ_AVAILABLE and hasattr(self, "tq_analysis_btn"):
            try:
                int(self.calculation.result_value)
                self.tq_analysis_btn.setEnabled(True)
            except (ValueError, TypeError):
                self.tq_analysis_btn.setEnabled(False)
                self.tq_analysis_btn.setToolTip(
                    "Only integer values can be sent to Quadset Analysis"
                )

    def _on_favorite_toggled(self, checked: bool) -> None:
        """Handle toggling the favorite status.

        Args:
            checked: Whether the checkbox is checked
        """
        if not self.calculation:
            return

        # Update calculation
        self.calculation.favorite = checked

        # Save to database
        if hasattr(self.calculation_db_service, "toggle_favorite"):
            self.calculation_db_service.toggle_favorite(self.calculation.id, checked)
        else:
            # Fallback method if toggle_favorite doesn't exist
            self.calculation.favorite = checked
            self.calculation_db_service.save_calculation(self.calculation)

        # Emit signal that calculation was updated
        self.calculation_updated.emit(self.calculation)

    def _save_notes(self) -> None:
        """Save the notes for the current calculation."""
        if not self.calculation:
            return

        # Get notes content - prefer HTML if there's formatting, otherwise plain text
        if self.notes_edit.is_modified() or self.notes_edit.get_html() != self.notes_edit.get_plain_text():
            # There's rich formatting, save as HTML
            notes = self.notes_edit.get_html()
        else:
            # No special formatting, save as plain text
            notes = self.notes_edit.get_plain_text()

        # Update calculation
        self.calculation.notes = notes

        # Save to database
        if hasattr(self.calculation_db_service, "update_notes"):
            self.calculation_db_service.update_notes(self.calculation.id, notes)
        else:
            # Fallback method if update_notes doesn't exist
            self.calculation_db_service.save_calculation(self.calculation)

        # Mark the editor as unmodified since we just saved
        self.notes_edit.set_modified(False)
        
        # Show success message
        QMessageBox.information(self, "Success", "Notes saved successfully")

        # Emit signal that calculation was updated
        self.calculation_updated.emit(self.calculation)

    def _delete_calculation(self) -> None:
        """Delete the current calculation."""
        if not self.calculation:
            return

        # Delete from database
        self.calculation_db_service.delete_calculation(self.calculation.id)

        # Clear the display
        self.calculation = None
        self.setVisible(False)

    def _edit_tags(self) -> None:
        """Open the edit tags window for the current calculation."""
        if not self.calculation:
            return

        # Create and show the edit tags window
        edit_tags_window = EditTagsWindow(self.calculation.id, parent=self)
        edit_tags_window.show()

        # Refresh the display when the window is closed
        edit_tags_window.destroyed.connect(self._refresh_after_edit)

    def _refresh_after_edit(self) -> None:
        """Refresh the calculation display after editing tags."""
        if not self.calculation:
            return

        # Refresh the calculation from the database
        updated_calculation = self.calculation_db_service.get_calculation(
            self.calculation.id
        )
        if updated_calculation:
            self.calculation = updated_calculation
            self._update_display()
            # Emit signal that calculation was updated
            self.calculation_updated.emit(self.calculation)

    def _send_to_quadset_analysis(self) -> None:
        """Send the calculation result to the TQ Quadset Analysis (TQ Grid)."""
        if not self.calculation or not TQ_AVAILABLE:
            return

        try:
            # Convert the result to an integer
            value = int(self.calculation.result_value)

            # Open the TQ Grid with this number
            tq_analysis_service.get_instance().open_quadset_analysis(value)

        except (ValueError, TypeError):
            QMessageBox.warning(
                self,
                "Invalid Value",
                "Only integer values can be sent to Quadset Analysis.",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while opening Quadset Analysis: {str(e)}",
            )
