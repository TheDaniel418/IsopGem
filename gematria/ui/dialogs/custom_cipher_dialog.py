"""Custom Cipher Dialog.

This module provides a dialog for creating and editing custom gematria ciphers.
"""

from typing import Dict, List, Optional, Union, cast

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_type import CalculationType, Language
from gematria.models.custom_cipher_config import CustomCipherConfig, LanguageType
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.services.gematria_service import GematriaService

# Define method type as a union of CalculationType and CustomCipherConfig
MethodType = Union[CalculationType, CustomCipherConfig]

NON_LATIN_LANGUAGES = [
    Language.HEBREW.value,
    Language.GREEK.value,
    Language.COPTIC.value,
    Language.ARABIC.value,  # Added Arabic
]


# ClosableButton class - a custom button that handles closing properly
class CloseButton(QPushButton):
    """Button that properly handles closing a dialog."""

    def __init__(self, text: str, dialog: QDialog) -> None:
        """Initialize the close button.

        Args:
            text: Button text
            dialog: Dialog to close
        """
        super().__init__(text)
        self.dialog = dialog
        self.clicked.connect(self._handle_click)

    def _handle_click(self) -> None:
        """Handle button click by hiding the dialog."""
        self.dialog.hide()


class CustomCipherDialog(QDialog):
    """Dialog for creating and editing custom gematria ciphers."""

    cipher_updated = pyqtSignal(CustomCipherConfig)

    def __init__(self, parent=None) -> None:
        """Initialize the custom cipher dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Custom Cipher Manager")
        self.resize(800, 600)

        # Make the dialog non-modal
        self.setModal(False)

        # Set window flags to allow staying on top, minimizing, and maximizing
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowCloseButtonHint
        )

        # Initialize the service
        self.service = CustomCipherService()

        # Current cipher being edited
        self.current_cipher: Optional[CustomCipherConfig] = None

        # Initialize UI
        self._init_ui()

        # Load existing ciphers
        self._load_ciphers()

    def _init_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Create split layout with cipher list on left, editor on right
        split_layout = QHBoxLayout()
        main_layout.addLayout(split_layout)

        # ===== Left side: Cipher list =====
        list_group = QGroupBox("Custom Ciphers")
        list_layout = QVBoxLayout(list_group)
        split_layout.addWidget(list_group, 1)

        # List actions
        list_actions = QHBoxLayout()
        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self._create_new_cipher)
        self.clone_btn = QPushButton("Clone")
        self.clone_btn.clicked.connect(self._clone_selected_cipher)
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self._delete_selected_cipher)

        list_actions.addWidget(self.new_btn)
        list_actions.addWidget(self.clone_btn)
        list_actions.addWidget(self.delete_btn)
        list_layout.addLayout(list_actions)

        # Cipher list (table)
        self.cipher_table = QTableWidget()
        self.cipher_table.setColumnCount(2)
        self.cipher_table.setHorizontalHeaderLabels(["Name", "Language"])
        self.cipher_table.horizontalHeader().setStretchLastSection(True)
        self.cipher_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.cipher_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.cipher_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cipher_table.clicked.connect(self._cipher_selected)

        list_layout.addWidget(self.cipher_table)

        # ===== Right side: Cipher editor =====
        editor_group = QGroupBox("Cipher Editor")
        editor_layout = QVBoxLayout(editor_group)
        split_layout.addWidget(editor_group, 2)

        # Create scroll area for the editor
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        editor_layout.addWidget(scroll)

        # Container for the scrollable content
        editor_container = QWidget()
        scroll.setWidget(editor_container)
        form_layout = QVBoxLayout(editor_container)

        # Cipher properties form
        properties_group = QGroupBox("Cipher Properties")
        properties_layout = QFormLayout(properties_group)
        form_layout.addWidget(properties_group)

        # Name field
        self.name_edit = QLineEdit()
        properties_layout.addRow("Name:", self.name_edit)

        # Language dropdown
        self.language_combo = QComboBox()
        self.language_combo.addItem("Hebrew", LanguageType.HEBREW)
        self.language_combo.addItem("Greek", LanguageType.GREEK)
        self.language_combo.addItem("English", LanguageType.ENGLISH)
        self.language_combo.addItem("Coptic", LanguageType.COPTIC)
        self.language_combo.addItem("Arabic", LanguageType.ARABIC)
        self.language_combo.currentIndexChanged.connect(self._language_changed)
        properties_layout.addRow("Language:", self.language_combo)

        # Description field
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        properties_layout.addRow("Description:", self.description_edit)

        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive_chk = QCheckBox("Case-sensitive")
        self.final_forms_chk = QCheckBox("Use final forms")

        options_layout.addWidget(self.case_sensitive_chk)
        options_layout.addWidget(self.final_forms_chk)
        options_layout.addStretch(1)
        properties_layout.addRow("Options:", options_layout)

        # Letter values
        self.letter_values_tab = QTabWidget()
        form_layout.addWidget(self.letter_values_tab)

        # Hebrew tab
        self.hebrew_tab = QWidget()
        hebrew_layout = QGridLayout(self.hebrew_tab)
        self._setup_hebrew_letter_grid(hebrew_layout)
        self.letter_values_tab.addTab(self.hebrew_tab, "Hebrew")

        # Greek tab
        self.greek_tab = QWidget()
        greek_layout = QGridLayout(self.greek_tab)
        self._setup_greek_letter_grid(greek_layout)
        self.letter_values_tab.addTab(self.greek_tab, "Greek")

        # English tab
        self.english_tab = QWidget()
        english_layout = QGridLayout(self.english_tab)
        self._setup_english_letter_grid(english_layout)
        self.letter_values_tab.addTab(self.english_tab, "English")

        # Button group at bottom
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_current_cipher)

        # Use our custom button class that handles closing properly
        self.cancel_btn = CloseButton("Close", self)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)

        # Disable editor until a cipher is selected
        self._set_editor_enabled(False)

    def _setup_hebrew_letter_grid(self, layout: QGridLayout) -> None:
        """Set up the grid of Hebrew letters and their value inputs.

        Args:
            layout: Layout to add the letter grid to
        """
        self.hebrew_inputs = {}

        # Regular Hebrew letters
        hebrew_letters = [
            "א",
            "ב",
            "ג",
            "ד",
            "ה",
            "ו",
            "ז",
            "ח",
            "ט",
            "י",
            "כ",
            "ל",
            "מ",
            "נ",
            "ס",
            "ע",
            "פ",
            "צ",
            "ק",
            "ר",
            "ש",
            "ת",
        ]

        # Final forms
        final_forms = ["ך", "ם", "ן", "ף", "ץ"]

        # Add regular letters
        for i, letter in enumerate(hebrew_letters):
            row = i // 6
            col = i % 6 * 2

            label = QLabel(letter)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 16pt;")

            spin = QSpinBox()
            spin.setRange(0, 10000)
            self.hebrew_inputs[letter] = spin

            layout.addWidget(label, row, col)
            layout.addWidget(spin, row, col + 1)

        # Add final forms
        final_label = QLabel("Final Forms:")
        layout.addWidget(final_label, 4, 0, 1, 2)

        for i, letter in enumerate(final_forms):
            label = QLabel(letter)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 16pt;")

            spin = QSpinBox()
            spin.setRange(0, 10000)
            self.hebrew_inputs[letter] = spin

            layout.addWidget(label, 5, i * 2)
            layout.addWidget(spin, 5, i * 2 + 1)

    def _setup_greek_letter_grid(self, layout: QGridLayout) -> None:
        """Set up the grid of Greek letters and their value inputs.

        Args:
            layout: Layout to add the letter grid to
        """
        self.greek_inputs = {}

        # Greek letters
        greek_letters = [
            "α",
            "β",
            "γ",
            "δ",
            "ε",
            "ζ",
            "η",
            "θ",
            "ι",
            "κ",
            "λ",
            "μ",
            "ν",
            "ξ",
            "ο",
            "π",
            "ρ",
            "σ",
            "τ",
            "υ",
            "φ",
            "χ",
            "ψ",
            "ω",
        ]

        # Add letters
        for i, letter in enumerate(greek_letters):
            row = i // 6
            col = i % 6 * 2

            label = QLabel(letter)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 16pt;")

            spin = QSpinBox()
            spin.setRange(0, 10000)
            self.greek_inputs[letter] = spin

            layout.addWidget(label, row, col)
            layout.addWidget(spin, row, col + 1)

    def _setup_english_letter_grid(self, layout: QGridLayout) -> None:
        """Set up the grid of English letters and their value inputs.

        Args:
            layout: Layout to add the letter grid to
        """
        self.english_inputs = {}

        # Create separate sections for uppercase and lowercase
        upper_group = QGroupBox("Uppercase")
        upper_layout = QGridLayout(upper_group)
        layout.addWidget(upper_group, 0, 0)

        lower_group = QGroupBox("Lowercase")
        lower_layout = QGridLayout(lower_group)
        layout.addWidget(lower_group, 1, 0)

        # Uppercase letters
        for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            row = i // 7
            col = i % 7 * 2

            label = QLabel(letter)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 14pt;")

            spin = QSpinBox()
            spin.setRange(0, 10000)
            self.english_inputs[letter] = spin

            upper_layout.addWidget(label, row, col)
            upper_layout.addWidget(spin, row, col + 1)

        # Lowercase letters
        for i, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
            row = i // 7
            col = i % 7 * 2

            label = QLabel(letter)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 14pt;")

            spin = QSpinBox()
            spin.setRange(0, 10000)
            self.english_inputs[letter] = spin

            lower_layout.addWidget(label, row, col)
            lower_layout.addWidget(spin, row, col + 1)

    def _load_ciphers(self) -> None:
        """Load existing ciphers from the service."""
        # Clear the table
        self.cipher_table.setRowCount(0)

        # Get all ciphers
        ciphers = self.service.get_ciphers()

        # If no ciphers exist, create default templates
        if not ciphers:
            self.service.create_default_templates()
            ciphers = self.service.get_ciphers()

        # Add to table
        self.cipher_table.setRowCount(len(ciphers))

        for i, cipher in enumerate(ciphers):
            name_item = QTableWidgetItem(cipher.name)
            name_item.setData(Qt.ItemDataRole.UserRole, cipher.id)

            language_item = QTableWidgetItem(cipher.language.name.capitalize())

            self.cipher_table.setItem(i, 0, name_item)
            self.cipher_table.setItem(i, 1, language_item)

        # Resize columns to content
        self.cipher_table.resizeColumnsToContents()

    def _cipher_selected(self) -> None:
        """Handle cipher selection from the table."""
        selected_rows = self.cipher_table.selectedItems()
        if not selected_rows:
            self._set_editor_enabled(False)
            return

        # Get the cipher ID from the selected row
        cipher_id = self.cipher_table.item(selected_rows[0].row(), 0).data(
            Qt.ItemDataRole.UserRole
        )

        # Load the cipher
        cipher = self.service.get_cipher(cipher_id)
        if not cipher:
            self._set_editor_enabled(False)
            return

        # Set as current cipher and update the editor
        self.current_cipher = cipher
        self._update_editor_from_cipher()
        self._set_editor_enabled(True)

    def _update_editor_from_cipher(self) -> None:
        """Update editor fields with the current cipher's values."""
        if not self.current_cipher:
            return

        # Update basic properties
        self.name_edit.setText(self.current_cipher.name)
        self.description_edit.setText(self.current_cipher.description)

        # Set language
        language_index = self.language_combo.findData(self.current_cipher.language)
        self.language_combo.setCurrentIndex(language_index)

        # Set options
        self.case_sensitive_chk.setChecked(self.current_cipher.case_sensitive)
        self.final_forms_chk.setChecked(self.current_cipher.use_final_forms)

        # Clear all letter inputs
        self._clear_all_letter_inputs()

        # Set letter values based on language
        letter_values = self.current_cipher.letter_values
        if self.current_cipher.language == LanguageType.HEBREW:
            for letter, spin in self.hebrew_inputs.items():
                spin.setValue(letter_values.get(letter, 0))

        elif self.current_cipher.language == LanguageType.GREEK:
            for letter, spin in self.greek_inputs.items():
                spin.setValue(letter_values.get(letter, 0))

        elif self.current_cipher.language == LanguageType.ENGLISH:
            for letter, spin in self.english_inputs.items():
                spin.setValue(letter_values.get(letter, 0))

        # Set active tab based on language
        if self.current_cipher.language == LanguageType.HEBREW:
            self.letter_values_tab.setCurrentIndex(0)
        elif self.current_cipher.language == LanguageType.GREEK:
            self.letter_values_tab.setCurrentIndex(1)
        elif self.current_cipher.language == LanguageType.ENGLISH:
            self.letter_values_tab.setCurrentIndex(2)

    def _clear_all_letter_inputs(self) -> None:
        """Clear all letter input fields."""
        for spin in self.hebrew_inputs.values():
            spin.setValue(0)

        for spin in self.greek_inputs.values():
            spin.setValue(0)

        for spin in self.english_inputs.values():
            spin.setValue(0)

    def _update_cipher_from_editor(self) -> bool:
        """Update the current cipher with values from the editor.

        Returns:
            True if successful, False if validation failed
        """
        if not self.current_cipher:
            return False

        # Validate name
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Cipher name cannot be empty")
            return False

        # Get language
        language = self.language_combo.currentData()

        # Create new config (or update existing)
        if self.current_cipher.name != name or self.current_cipher.language != language:
            # Creating a new config for name/language change to get a new ID
            old_id = self.current_cipher.id
            self.current_cipher = CustomCipherConfig(name, language)
        else:
            # Just update the existing config
            self.current_cipher.name = name

        # Update other properties
        self.current_cipher.description = self.description_edit.toPlainText()
        self.current_cipher.case_sensitive = self.case_sensitive_chk.isChecked()
        self.current_cipher.use_final_forms = self.final_forms_chk.isChecked()

        # Get letter values based on language
        letter_values = {}

        if language == LanguageType.HEBREW:
            for letter, spin in self.hebrew_inputs.items():
                value = spin.value()
                if value > 0:  # Only add non-zero values
                    letter_values[letter] = value

        elif language == LanguageType.GREEK:
            for letter, spin in self.greek_inputs.items():
                value = spin.value()
                if value > 0:  # Only add non-zero values
                    letter_values[letter] = value

        elif language == LanguageType.ENGLISH:
            for letter, spin in self.english_inputs.items():
                value = spin.value()
                if value > 0:  # Only add non-zero values
                    letter_values[letter] = value

        # Ensure we have at least one letter value
        if not letter_values:
            QMessageBox.warning(
                self, "Validation Error", "You must assign at least one letter value"
            )
            return False

        # Update the letter values
        self.current_cipher.letter_values = letter_values

        # Validate the config
        if not self.current_cipher.is_valid():
            QMessageBox.warning(
                self,
                "Validation Error",
                "The cipher configuration is invalid. Please check all settings.",
            )
            return False

        return True

    def _save_current_cipher(self) -> None:
        """Save the current cipher to the service."""
        if not self.current_cipher:
            logger.warning("No cipher to save - current_cipher is None")
            return

        if not self._update_cipher_from_editor():
            return

        # Save to service
        success = self.service.save_cipher(self.current_cipher)
        if success:
            # Emit signal to notify listeners
            self.cipher_updated.emit(self.current_cipher)

            # Refresh the list
            self._load_ciphers()

            QMessageBox.information(
                self,
                "Success",
                f"Cipher '{self.current_cipher.name}' saved successfully",
            )
        else:
            QMessageBox.warning(
                self, "Save Error", "Failed to save the cipher configuration"
            )

    def _create_new_cipher(self) -> None:
        """Create a new blank cipher."""
        # Create a new cipher with default values
        self.current_cipher = CustomCipherConfig(
            "New Cipher", LanguageType.HEBREW, "New custom cipher"
        )

        # Update the editor
        self._update_editor_from_cipher()
        self._set_editor_enabled(True)

    def _clone_selected_cipher(self) -> None:
        """Clone a cipher using the cipher selection dialog."""
        # Create and show the cipher selection dialog
        selection_dialog = CipherSelectionDialog(self)

        # Connect the signal to handle selection
        selection_dialog.cipher_selected.connect(self._handle_clone_selection)

        # Show the dialog (modal)
        selection_dialog.exec()

    def _handle_clone_selection(self, source_cipher: CustomCipherConfig) -> None:
        """Handle the selection of a cipher to clone.

        Args:
            source_cipher: The selected cipher to clone
        """
        # Create a clone with a new name
        self.current_cipher = CustomCipherConfig(
            f"{source_cipher.name} (Clone)",
            source_cipher.language,
            source_cipher.description,
        )

        # Copy settings
        self.current_cipher.case_sensitive = source_cipher.case_sensitive
        self.current_cipher.use_final_forms = source_cipher.use_final_forms
        self.current_cipher.letter_values = source_cipher.letter_values.copy()

        # Update the editor
        self._update_editor_from_cipher()
        self._set_editor_enabled(True)

    def _delete_selected_cipher(self) -> None:
        """Delete the selected cipher."""
        selected_rows = self.cipher_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(
                self, "No Selection", "Please select a cipher to delete"
            )
            return

        # Get the cipher ID from the selected row
        cipher_id = self.cipher_table.item(selected_rows[0].row(), 0).data(
            Qt.ItemDataRole.UserRole
        )
        cipher_name = self.cipher_table.item(selected_rows[0].row(), 0).text()

        # Confirm deletion
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the cipher '{cipher_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.No:
            return

        # Delete from service
        if self.service.delete_cipher(cipher_id):
            # Refresh the list
            self._load_ciphers()

            # Clear the editor if the deleted cipher was being edited
            if self.current_cipher and self.current_cipher.id == cipher_id:
                self.current_cipher = None
                self._set_editor_enabled(False)

            QMessageBox.information(
                self, "Success", f"Cipher '{cipher_name}' deleted successfully"
            )
        else:
            QMessageBox.warning(
                self, "Delete Error", f"Failed to delete the cipher '{cipher_name}'"
            )

    def _set_editor_enabled(self, enabled: bool) -> None:
        """Enable or disable the editor.

        Args:
            enabled: Whether to enable the editor
        """
        # Enable/disable all editor fields
        self.name_edit.setEnabled(enabled)
        self.language_combo.setEnabled(enabled)
        self.description_edit.setEnabled(enabled)
        self.case_sensitive_chk.setEnabled(enabled)
        self.final_forms_chk.setEnabled(enabled)
        self.letter_values_tab.setEnabled(enabled)
        self.save_btn.setEnabled(enabled)

        # Clear fields if disabled
        if not enabled:
            self.name_edit.clear()
            self.description_edit.clear()
            self.case_sensitive_chk.setChecked(False)
            self.final_forms_chk.setChecked(False)
            self._clear_all_letter_inputs()

    def _language_changed(self) -> None:
        """Handle language selection change."""
        language = self.language_combo.currentData()

        # Update UI elements based on language
        show_final_forms = language == LanguageType.HEBREW
        self.final_forms_chk.setVisible(show_final_forms)

        # Show appropriate tab
        if language == LanguageType.HEBREW:
            self.letter_values_tab.setCurrentIndex(0)
        elif language == LanguageType.GREEK:
            self.letter_values_tab.setCurrentIndex(1)
        elif language == LanguageType.ENGLISH:
            self.letter_values_tab.setCurrentIndex(2)

    def close_dialog(self) -> None:
        """Custom handler to close the dialog properly."""
        self.hide()

    def reject(self) -> None:
        """Override reject to hide instead of rejecting."""
        self.hide()

    def closeEvent(self, event):
        """Handle dialog close event.

        For non-modal behavior, check for unsaved changes before closing.

        Args:
            event: Close event
        """
        # Check if we have unsaved changes
        if self.current_cipher and self._has_unsaved_changes():
            # Ask user what to do
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them before closing?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )

            if response == QMessageBox.StandardButton.Save:
                # Try to save before hiding
                self._save_current_cipher()
                self.hide()
                event.ignore()
            elif response == QMessageBox.StandardButton.Cancel:
                # User canceled, don't close
                event.ignore()
            else:
                # Discard changes and hide
                self.hide()
                event.ignore()
        else:
            # No changes, hide instead of accepting close
            self.hide()
            event.ignore()

    def _has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes in the editor.

        Returns:
            True if there are unsaved changes, False otherwise
        """
        if not self.current_cipher:
            return False

        # Check name and description
        if self.name_edit.text() != self.current_cipher.name:
            return True

        if self.description_edit.toPlainText() != self.current_cipher.description:
            return True

        # Check language
        if self.language_combo.currentData() != self.current_cipher.language:
            return True

        # Check options
        if self.case_sensitive_chk.isChecked() != self.current_cipher.case_sensitive:
            return True

        if self.final_forms_chk.isChecked() != self.current_cipher.use_final_forms:
            return True

        # Check letter values based on current language
        language = self.language_combo.currentData()
        if language == LanguageType.HEBREW:
            for letter, spin in self.hebrew_inputs.items():
                current_value = self.current_cipher.letter_values.get(letter, 0)
                if spin.value() != current_value:
                    return True
        elif language == LanguageType.GREEK:
            for letter, spin in self.greek_inputs.items():
                current_value = self.current_cipher.letter_values.get(letter, 0)
                if spin.value() != current_value:
                    return True
        elif language == LanguageType.ENGLISH:
            for letter, spin in self.english_inputs.items():
                current_value = self.current_cipher.letter_values.get(letter, 0)
                if spin.value() != current_value:
                    return True

        return False


class CipherSelectionDialog(QDialog):
    """Dialog for selecting a cipher to clone from all available ciphers."""

    cipher_selected = pyqtSignal(CustomCipherConfig)

    def __init__(self, parent=None):
        """Initialize the cipher selection dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Select Calculation Method")
        self.setModal(True)
        self.resize(600, 500)

        # Initialize services
        self.gematria_service = GematriaService()
        self.custom_service = CustomCipherService()

        # Ensure we have default templates
        ciphers = self.custom_service.get_ciphers()
        if not ciphers:
            logger.debug("Creating default cipher templates")
            self.custom_service.create_default_templates()

        # Store calculation categories and methods
        self._method_categories: Dict[str, List[MethodType]] = {}

        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Language selection
        language_group = QGroupBox("Select Language")
        language_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        language_layout = QVBoxLayout(language_group)

        self._language_combo = QComboBox()
        self._language_combo.addItem("Hebrew", LanguageType.HEBREW)
        self._language_combo.addItem("Greek", LanguageType.GREEK)
        self._language_combo.addItem("English", LanguageType.ENGLISH)
        self._language_combo.addItem("Coptic", LanguageType.COPTIC)
        self._language_combo.addItem("Arabic", LanguageType.ARABIC)
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)
        self._language_combo.setStyleSheet("padding: 5px;")

        language_layout.addWidget(self._language_combo)
        layout.addWidget(language_group)

        # Category selection
        category_group = QGroupBox("Select Method Category")
        category_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        category_layout = QVBoxLayout(category_group)

        self._category_combo = QComboBox()
        self._category_combo.currentIndexChanged.connect(self._on_category_changed)
        self._category_combo.setStyleSheet("padding: 5px;")

        category_layout.addWidget(self._category_combo)
        layout.addWidget(category_group)

        # Method selection
        method_group = QGroupBox("Select Method")
        method_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        method_layout = QVBoxLayout(method_group)

        self._method_list = QListWidget()
        self._method_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self._method_list.setStyleSheet(
            """
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                border-bottom: 1px solid #ecf0f1;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """
        )
        self._method_list.itemDoubleClicked.connect(self._on_method_double_clicked)
        self._method_list.currentItemChanged.connect(self._on_method_selection_changed)

        method_layout.addWidget(self._method_list)
        layout.addWidget(method_group)

        # Button area
        button_layout = QHBoxLayout()

        self._select_btn = QPushButton("Select")
        self._select_btn.clicked.connect(self._on_select)
        self._select_btn.setEnabled(False)
        self._select_btn.setStyleSheet(
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
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
        )

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
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

        button_layout.addWidget(self._select_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch(1)

        layout.addLayout(button_layout)

        # Initialize with Hebrew and populate categories right away
        self._language_combo.setCurrentIndex(0)
        # Explicitly populate categories and methods on init
        self._populate_method_categories()

        # If we have categories, also populate methods
        if self._category_combo.count() > 0:
            self._populate_methods()

    def _on_language_changed(self):
        """Handle language selection change."""
        # Populate categories based on selected language
        self._populate_method_categories()

    def _on_category_changed(self):
        """Handle category selection change."""
        # Populate methods based on selected category
        self._populate_methods()

    def _on_method_selection_changed(self, current, previous):
        """Handle change in method selection."""
        self._select_btn.setEnabled(current is not None)

    def _on_method_double_clicked(self, item):
        """Handle double-click on a method item."""
        self._on_select()

    def _on_select(self):
        """Handle selection of a method."""
        if not self._method_list.currentItem():
            return

        # Get the selected calculation type or custom cipher
        data = self._method_list.currentItem().data(Qt.ItemDataRole.UserRole)

        if isinstance(data, CustomCipherConfig):
            # For custom cipher configs
            self.cipher_selected.emit(data)
            self.accept()
        elif isinstance(data, CalculationType):
            # For enum-based calculation types, create a new custom cipher
            # based on the selected calculation type

            # Get the language
            language = self._language_combo.currentData()

            # Create the name based on the calculation type
            display_name = data.name.replace("_", " ").title()
            if language == LanguageType.HEBREW:
                name = f"Custom {display_name}"
            elif language == LanguageType.GREEK:
                # Strip "GREEK_" prefix if present
                if display_name.startswith("Greek "):
                    display_name = display_name[6:]
                name = f"Custom {display_name}"
            else:
                name = f"Custom {display_name}"

            # Create a new custom cipher with template values
            # based on the calculation type
            cipher = self._create_custom_cipher_from_calc_type(data, name, language)

            if cipher:
                self.cipher_selected.emit(cipher)
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Failed to create custom cipher from the selected calculation type.",
                )

    def _create_custom_cipher_from_calc_type(
        self, calc_type: CalculationType, name: str, language: LanguageType
    ) -> Optional[CustomCipherConfig]:
        """Create a custom cipher from a calculation type.

        Args:
            calc_type: Calculation type to base the cipher on
            name: Name for the new cipher
            language: Language for the new cipher

        Returns:
            New custom cipher config, or None if creation failed
        """
        description = f"Custom cipher based on {calc_type.name}"
        cipher = CustomCipherConfig(name, language, description)

        # Hebrew standard letter values
        hebrew_standard = {
            "א": 1,
            "ב": 2,
            "ג": 3,
            "ד": 4,
            "ה": 5,
            "ו": 6,
            "ז": 7,
            "ח": 8,
            "ט": 9,
            "י": 10,
            "כ": 20,
            "ל": 30,
            "מ": 40,
            "נ": 50,
            "ס": 60,
            "ע": 70,
            "פ": 80,
            "צ": 90,
            "ק": 100,
            "ר": 200,
            "ש": 300,
            "ת": 400,
            "ך": 20,
            "ם": 40,
            "ן": 50,
            "ף": 80,
            "ץ": 90,
        }

        # Hebrew ordinal values
        hebrew_ordinal = {
            "א": 1,
            "ב": 2,
            "ג": 3,
            "ד": 4,
            "ה": 5,
            "ו": 6,
            "ז": 7,
            "ח": 8,
            "ט": 9,
            "י": 10,
            "כ": 11,
            "ל": 12,
            "מ": 13,
            "נ": 14,
            "ס": 15,
            "ע": 16,
            "פ": 17,
            "צ": 18,
            "ק": 19,
            "ר": 20,
            "ש": 21,
            "ת": 22,
            "ך": 11,
            "ם": 13,
            "ן": 14,
            "ף": 17,
            "ץ": 18,
        }

        # Hebrew reduced values
        hebrew_reduced = {
            "א": 1,
            "ב": 2,
            "ג": 3,
            "ד": 4,
            "ה": 5,
            "ו": 6,
            "ז": 7,
            "ח": 8,
            "ט": 9,
            "י": 1,
            "כ": 2,
            "ל": 3,
            "מ": 4,
            "נ": 5,
            "ס": 6,
            "ע": 7,
            "פ": 8,
            "צ": 9,
            "ק": 1,
            "ר": 2,
            "ש": 3,
            "ת": 4,
            "ך": 2,
            "ם": 4,
            "ן": 5,
            "ף": 8,
            "ץ": 9,
        }

        # Hebrew gadol (large) values
        hebrew_gadol = {
            "א": 1,
            "ב": 2,
            "ג": 3,
            "ד": 4,
            "ה": 5,
            "ו": 6,
            "ז": 7,
            "ח": 8,
            "ט": 9,
            "י": 10,
            "כ": 20,
            "ל": 30,
            "מ": 40,
            "נ": 50,
            "ס": 60,
            "ע": 70,
            "פ": 80,
            "צ": 90,
            "ק": 100,
            "ר": 200,
            "ש": 300,
            "ת": 400,
            "ך": 500,
            "ם": 600,
            "ן": 700,
            "ף": 800,
            "ץ": 900,
        }

        # Hebrew Mispar Meshupach (reversal) values
        hebrew_reversal = {
            "א": 400,
            "ב": 300,
            "ג": 200,
            "ד": 100,
            "ה": 90,
            "ו": 80,
            "ז": 70,
            "ח": 60,
            "ט": 50,
            "י": 40,
            "כ": 30,
            "ל": 20,
            "מ": 10,
            "נ": 9,
            "ס": 8,
            "ע": 7,
            "פ": 6,
            "צ": 5,
            "ק": 4,
            "ר": 3,
            "ש": 2,
            "ת": 1,
            "ך": 30,
            "ם": 10,
            "ן": 9,
            "ף": 6,
            "ץ": 5,
        }

        # Albam substitution
        hebrew_albam = {
            "א": 30,
            "ב": 40,
            "ג": 50,
            "ד": 60,
            "ה": 70,
            "ו": 80,
            "ז": 90,
            "ח": 100,
            "ט": 200,
            "י": 300,
            "כ": 400,
            "ל": 1,
            "מ": 2,
            "נ": 3,
            "ס": 4,
            "ע": 5,
            "פ": 6,
            "צ": 7,
            "ק": 8,
            "ר": 9,
            "ש": 10,
            "ת": 20,
            "ך": 400,
            "ם": 2,
            "ן": 3,
            "ף": 6,
            "ץ": 7,
        }

        # Atbash substitution
        hebrew_atbash = {
            "א": 400,
            "ב": 300,
            "ג": 200,
            "ד": 100,
            "ה": 90,
            "ו": 80,
            "ז": 70,
            "ח": 60,
            "ט": 50,
            "י": 40,
            "כ": 30,
            "ל": 20,
            "מ": 10,
            "נ": 9,
            "ס": 8,
            "ע": 7,
            "פ": 6,
            "צ": 5,
            "ק": 4,
            "ר": 3,
            "ש": 2,
            "ת": 1,
            "ך": 30,
            "ם": 10,
            "ן": 9,
            "ף": 6,
            "ץ": 5,
        }

        # Greek letter maps
        greek_standard = {
            "α": 1,
            "β": 2,
            "γ": 3,
            "δ": 4,
            "ε": 5,
            "ζ": 7,
            "η": 8,
            "θ": 9,
            "ι": 10,
            "κ": 20,
            "λ": 30,
            "μ": 40,
            "ν": 50,
            "ξ": 60,
            "ο": 70,
            "π": 80,
            "ρ": 100,
            "σ": 200,
            "τ": 300,
            "υ": 400,
            "φ": 500,
            "χ": 600,
            "ψ": 700,
            "ω": 800,
            "ς": 200,  # Final sigma
            "ϲ": 200,  # Lunate sigma
        }

        # Greek ordinal values
        greek_ordinal = {
            "α": 1,
            "β": 2,
            "γ": 3,
            "δ": 4,
            "ε": 5,
            "ζ": 6,
            "η": 7,
            "θ": 8,
            "ι": 9,
            "κ": 10,
            "λ": 11,
            "μ": 12,
            "ν": 13,
            "ξ": 14,
            "ο": 15,
            "π": 16,
            "ρ": 17,
            "σ": 18,
            "τ": 19,
            "υ": 20,
            "φ": 21,
            "χ": 22,
            "ψ": 23,
            "ω": 24,
            "ς": 18,  # Final sigma
            "ϲ": 18,  # Lunate sigma
        }

        # Greek reduced values
        greek_reduced = {
            "α": 1,
            "β": 2,
            "γ": 3,
            "δ": 4,
            "ε": 5,
            "ζ": 7,
            "η": 8,
            "θ": 9,
            "ι": 1,
            "κ": 2,
            "λ": 3,
            "μ": 4,
            "ν": 5,
            "ξ": 6,
            "ο": 7,
            "π": 8,
            "ρ": 1,
            "σ": 2,
            "τ": 3,
            "υ": 4,
            "φ": 5,
            "χ": 6,
            "ψ": 7,
            "ω": 8,
            "ς": 2,
        }

        # Greek reversal values
        greek_reversal = {
            "α": 800,
            "β": 700,
            "γ": 600,
            "δ": 500,
            "ε": 400,
            "ζ": 300,
            "η": 200,
            "θ": 100,
            "ι": 80,
            "κ": 70,
            "λ": 60,
            "μ": 50,
            "ν": 40,
            "ξ": 30,
            "ο": 20,
            "π": 10,
            "ρ": 9,
            "σ": 8,
            "τ": 7,
            "υ": 6,
            "φ": 5,
            "χ": 4,
            "ψ": 3,
            "ω": 1,
            "ς": 8,
        }

        # Greek Alpha-Mu cipher (similar to Hebrew Albam)
        greek_alpha_mu = {
            "α": 40,
            "β": 50,
            "γ": 60,
            "δ": 70,
            "ε": 80,
            "ζ": 90,
            "η": 100,
            "θ": 200,
            "ι": 300,
            "κ": 400,
            "λ": 500,
            "μ": 600,
            "ν": 1,
            "ξ": 2,
            "ο": 3,
            "π": 4,
            "ρ": 5,
            "σ": 6,
            "τ": 7,
            "υ": 8,
            "φ": 9,
            "χ": 10,
            "ψ": 20,
            "ω": 30,
            "ς": 6,
        }

        # Greek Alpha-Omega cipher (similar to Hebrew Atbash)
        greek_alpha_omega = {
            "α": 800,
            "β": 700,
            "γ": 600,
            "δ": 500,
            "ε": 400,
            "ζ": 300,
            "η": 200,
            "θ": 100,
            "ι": 80,
            "κ": 70,
            "λ": 60,
            "μ": 50,
            "ν": 40,
            "ξ": 30,
            "ο": 20,
            "π": 10,
            "ρ": 9,
            "σ": 8,
            "τ": 7,
            "υ": 6,
            "φ": 5,
            "χ": 4,
            "ψ": 3,
            "ω": 1,
            "ς": 8,
        }

        # Greek building value
        greek_building = {
            "α": 1,  # 1
            "β": 3,  # 1+2
            "γ": 6,  # 1+2+3
            "δ": 10,  # 1+2+3+4
            "ε": 15,  # 1+2+3+4+5
            "ζ": 21,  # 1+2+3+4+5+6
            "η": 28,  # 1+2+3+4+5+6+7
            "θ": 36,  # 1+2+3+4+5+6+7+8
            "ι": 45,  # 1+2+3+4+5+6+7+8+9
            "κ": 55,  # 1+2+..+10
            "λ": 66,  # 1+2+..+11
            "μ": 78,  # 1+2+..+12
            "ν": 91,  # 1+2+..+13
            "ξ": 105,  # 1+2+..+14
            "ο": 120,  # 1+2+..+15
            "π": 136,  # 1+2+..+16
            "ρ": 153,  # 1+2+..+17
            "σ": 171,  # 1+2+..+18
            "τ": 190,  # 1+2+..+19
            "υ": 210,  # 1+2+..+20
            "φ": 231,  # 1+2+..+21
            "χ": 253,  # 1+2+..+22
            "ψ": 276,  # 1+2+..+23
            "ω": 300,  # 1+2+..+24
            "ς": 171,  # same as sigma
            "ϲ": 171,  # same as sigma
        }

        # Greek hidden value
        greek_hidden = {
            "α": 531,  # alpha without alpha
            "β": 309,  # beta without beta
            "γ": 82,  # gamma without gamma
            "δ": 336,  # delta without delta
            "ε": 860,  # epsilon without epsilon
            "ζ": 309,  # zeta without zeta
            "η": 301,  # eta without eta
            "θ": 309,  # theta without theta
            "ι": 1101,  # iota without iota
            "κ": 162,  # kappa without kappa
            "λ": 48,  # lambda without lambda
            "μ": 400,  # mu without mu
            "ν": 400,  # nu without nu
            "ξ": 10,  # xi without xi
            "ο": 290,  # omicron without omicron
            "π": 10,  # pi without pi
            "ρ": 800,  # rho without rho
            "σ": 54,  # sigma without sigma
            "τ": 401,  # tau without tau
            "υ": 850,  # upsilon without upsilon
            "φ": 10,  # phi without phi
            "χ": 10,  # chi without chi
            "ψ": 10,  # psi without psi
            "ω": 0,  # omega without omega
            "ς": 54,  # final sigma without sigma
            "ϲ": 54,  # lunate sigma without sigma
        }

        # Greek full name value
        greek_full_name = {
            "α": 532,  # alpha
            "β": 311,  # beta
            "γ": 85,  # gamma
            "δ": 340,  # delta
            "ε": 865,  # epsilon
            "ζ": 316,  # zeta
            "η": 309,  # eta
            "θ": 318,  # theta
            "ι": 1111,  # iota
            "κ": 182,  # kappa
            "λ": 78,  # lambda
            "μ": 440,  # mu
            "ν": 450,  # nu
            "ξ": 70,  # xi
            "ο": 360,  # omicron
            "π": 90,  # pi
            "ρ": 900,  # rho
            "σ": 254,  # sigma
            "τ": 701,  # tau
            "υ": 1250,  # upsilon
            "φ": 510,  # phi
            "χ": 610,  # chi
            "ψ": 710,  # psi
            "ω": 800,  # omega
            "ς": 254,  # final sigma
            "ϲ": 254,  # lunate sigma
        }

        # Greek additive value
        greek_additive = {
            "α": 1,
            "β": 2,
            "γ": 3,
            "δ": 4,
            "ε": 5,
            "ζ": 7,
            "η": 8,
            "θ": 9,
            "ι": 10,
            "κ": 20,
            "λ": 30,
            "μ": 40,
            "ν": 50,
            "ξ": 60,
            "ο": 70,
            "π": 80,
            "ρ": 100,
            "σ": 200,
            "τ": 300,
            "υ": 400,
            "φ": 500,
            "χ": 600,
            "ψ": 700,
            "ω": 800,
            "ς": 200,
            "ϲ": 200,
        }

        # Use appropriate letter values based on the calculation type
        if language == LanguageType.HEBREW:
            if calc_type == CalculationType.HEBREW_STANDARD_VALUE:
                cipher.letter_values = hebrew_standard.copy()
            elif calc_type == CalculationType.HEBREW_ORDINAL_VALUE:
                cipher.letter_values = hebrew_ordinal.copy()
            elif calc_type == CalculationType.HEBREW_SMALL_REDUCED_VALUE:
                cipher.letter_values = hebrew_reduced.copy()
            elif calc_type == CalculationType.HEBREW_INTEGRAL_REDUCED_VALUE:
                cipher.letter_values = hebrew_reduced.copy()
            elif calc_type == CalculationType.HEBREW_FINAL_LETTER_VALUES:
                cipher.letter_values = hebrew_gadol.copy()
                cipher.use_final_forms = True
            elif calc_type == CalculationType.HEBREW_REVERSE_STANDARD_VALUES:
                cipher.letter_values = hebrew_reversal.copy()
            elif calc_type == CalculationType.HEBREW_ALBAM_SUBSTITUTION:
                cipher.letter_values = hebrew_albam.copy()
            elif calc_type == CalculationType.HEBREW_ATBASH_SUBSTITUTION:
                cipher.letter_values = hebrew_atbash.copy()
            else:
                cipher.letter_values = hebrew_standard.copy()

        elif language == LanguageType.GREEK:
            if calc_type == CalculationType.GREEK_STANDARD_VALUE:
                cipher.letter_values = greek_standard.copy()
            elif calc_type == CalculationType.GREEK_ORDINAL_VALUE:
                cipher.letter_values = greek_ordinal.copy()
            elif calc_type == CalculationType.GREEK_SQUARE_VALUE:
                cipher.letter_values = greek_standard.copy()
            elif calc_type == CalculationType.GREEK_REVERSE_STANDARD_VALUES:
                cipher.letter_values = greek_reversal.copy()
            elif calc_type == CalculationType.GREEK_ALPHAMU_SUBSTITUTION:
                cipher.letter_values = greek_alpha_mu.copy()
            elif calc_type == CalculationType.GREEK_ALPHAOMEGA_SUBSTITUTION:
                cipher.letter_values = greek_alpha_omega.copy()
            elif calc_type == CalculationType.GREEK_BUILDING_VALUE_CUMULATIVE:
                cipher.letter_values = greek_building.copy()
            elif calc_type == CalculationType.GREEK_HIDDEN_LETTER_NAME_VALUE:
                cipher.letter_values = greek_hidden.copy()
            elif calc_type == CalculationType.GREEK_SUM_OF_LETTER_NAMES:
                cipher.letter_values = greek_full_name.copy()
            elif (
                calc_type
                == CalculationType.GREEK_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS
            ):
                cipher.letter_values = greek_additive.copy()
            else:
                cipher.letter_values = greek_standard.copy()

        elif language == LanguageType.ENGLISH:
            if calc_type == CalculationType.ENGLISH_TQ_STANDARD_VALUE:
                cipher.letter_values = {
                    "a": 1,
                    "b": 2,
                    "c": 3,
                    "d": 4,
                    "e": 5,
                    "f": 6,
                    "g": 7,
                    "h": 8,
                    "i": 9,
                    "j": 10,
                    "k": 11,
                    "l": 12,
                    "m": 13,
                    "n": 14,
                    "o": 15,
                    "p": 16,
                    "q": 17,
                    "r": 18,
                    "s": 19,
                    "t": 20,
                    "u": 21,
                    "v": 22,
                    "w": 23,
                    "x": 24,
                    "y": 25,
                    "z": 26,
                }
            else:
                cipher.letter_values = {
                    letter: i + 1
                    for i, letter in enumerate("abcdefghijklmnopqrstuvwxyz")
                }

        # Set appropriate properties
        cipher.methods = []

        # Hebrew methods
        if calc_type in [
            CalculationType.HEBREW_STANDARD_VALUE,
            CalculationType.HEBREW_ORDINAL_VALUE,
            CalculationType.HEBREW_FINAL_LETTER_VALUES,
            CalculationType.HEBREW_BUILDING_VALUE_CUMULATIVE,
            CalculationType.HEBREW_TRIANGULAR_VALUE,
            CalculationType.HEBREW_INDIVIDUAL_SQUARE_VALUE,
            CalculationType.HEBREW_SUM_OF_LETTER_NAMES_STANDARD,
            CalculationType.HEBREW_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS,
            CalculationType.HEBREW_REVERSE_STANDARD_VALUES,
            CalculationType.HEBREW_ALBAM_SUBSTITUTION,
            CalculationType.HEBREW_ATBASH_SUBSTITUTION,
            CalculationType.HEBREW_SMALL_REDUCED_VALUE,
            CalculationType.HEBREW_INTEGRAL_REDUCED_VALUE,
            CalculationType.HEBREW_SUM_OF_LETTER_NAMES_FINALS,
            CalculationType.HEBREW_PRODUCT_OF_LETTER_NAMES_STANDARD,
            CalculationType.HEBREW_PRODUCT_OF_LETTER_NAMES_FINALS,
            CalculationType.HEBREW_HIDDEN_VALUE_STANDARD,
            CalculationType.HEBREW_HIDDEN_VALUE_FINALS,
            CalculationType.HEBREW_FACE_VALUE_STANDARD,
            CalculationType.HEBREW_FACE_VALUE_FINALS,
            CalculationType.HEBREW_BACK_VALUE_STANDARD,
            CalculationType.HEBREW_BACK_VALUE_FINALS,
            CalculationType.HEBREW_SUM_OF_LETTER_NAMES_STANDARD_PLUS_LETTERS,
            CalculationType.HEBREW_SUM_OF_LETTER_NAMES_FINALS_PLUS_LETTERS,
            CalculationType.HEBREW_STANDARD_VALUE_PLUS_ONE,
            CalculationType.HEBREW_CUBED_VALUE,
        ]:
            cipher.language = LanguageType.HEBREW

        # Greek methods
        elif calc_type in [
            CalculationType.GREEK_STANDARD_VALUE,
            CalculationType.GREEK_ORDINAL_VALUE,
            CalculationType.GREEK_SQUARE_VALUE,
            CalculationType.GREEK_REVERSE_STANDARD_VALUES,
            CalculationType.GREEK_ALPHAMU_SUBSTITUTION,
            CalculationType.GREEK_ALPHAOMEGA_SUBSTITUTION,
            CalculationType.GREEK_BUILDING_VALUE_CUMULATIVE,
            CalculationType.GREEK_HIDDEN_LETTER_NAME_VALUE,
            CalculationType.GREEK_SUM_OF_LETTER_NAMES,
            CalculationType.GREEK_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS,
            CalculationType.GREEK_CUBED_VALUE,
            CalculationType.GREEK_NEXT_LETTER_VALUE,
            CalculationType.GREEK_CYCLICAL_PERMUTATION_VALUE,
            CalculationType.GREEK_SMALL_REDUCED_VALUE,
            CalculationType.GREEK_DIGITAL_VALUE,
            CalculationType.GREEK_DIGITAL_ORDINAL_VALUE,
            CalculationType.GREEK_ORDINAL_SQUARE_VALUE,
            CalculationType.GREEK_PRODUCT_OF_LETTER_NAMES,
            CalculationType.GREEK_FACE_VALUE,
            CalculationType.GREEK_BACK_VALUE,
            CalculationType.GREEK_SUM_OF_LETTER_NAMES_PLUS_LETTERS,
            CalculationType.GREEK_STANDARD_VALUE_PLUS_ONE,
            CalculationType.GREEK_ALPHABET_REVERSAL_SUBSTITUTION,
            CalculationType.GREEK_PAIR_MATCHING_SUBSTITUTION,
        ]:
            cipher.language = LanguageType.GREEK

        # English methods
        elif calc_type in [CalculationType.ENGLISH_TQ_STANDARD_VALUE]:
            cipher.language = LanguageType.ENGLISH

        else:
            cipher.language = LanguageType.ENGLISH

        return cipher

    def _populate_method_categories(self) -> None:
        """Populate the method categories based on selected language."""
        # Clear existing categories
        self._category_combo.clear()

        # Get selected language
        language = self._language_combo.currentData()

        if language == LanguageType.HEBREW:
            hebrew_categories: Dict[str, List[MethodType]] = {
                "Standard Methods": [
                    CalculationType.HEBREW_STANDARD_VALUE,
                    CalculationType.HEBREW_ORDINAL_VALUE,
                    CalculationType.HEBREW_SMALL_REDUCED_VALUE,
                    CalculationType.HEBREW_INTEGRAL_REDUCED_VALUE,
                ],
                "Advanced Methods": [
                    CalculationType.HEBREW_FINAL_LETTER_VALUES,
                    CalculationType.HEBREW_REVERSE_STANDARD_VALUES,
                ],
                "Substitution Ciphers": [
                    CalculationType.HEBREW_ALBAM_SUBSTITUTION,
                    CalculationType.HEBREW_ATBASH_SUBSTITUTION,
                ],
            }

            # Add custom ciphers category if available
            hebrew_custom_ciphers = self.custom_service.get_ciphers(LanguageType.HEBREW)
            if hebrew_custom_ciphers:
                hebrew_categories["Custom Methods"] = cast(
                    List[MethodType], hebrew_custom_ciphers
                )

            # Store the categories and their methods
            self._method_categories = hebrew_categories

            # Add the categories to the combobox
            for category in hebrew_categories.keys():
                self._category_combo.addItem(category)

            # Set default category to Standard Methods
            self._category_combo.setCurrentIndex(0)

        elif language == LanguageType.GREEK:
            greek_categories: Dict[str, List[MethodType]] = {
                "Standard Methods": [
                    CalculationType.GREEK_STANDARD_VALUE,
                    CalculationType.GREEK_ORDINAL_VALUE,
                    CalculationType.GREEK_SQUARE_VALUE,
                    CalculationType.GREEK_REVERSE_STANDARD_VALUES,
                ],
                "Advanced Methods": [
                    CalculationType.GREEK_ALPHAMU_SUBSTITUTION,
                    CalculationType.GREEK_ALPHAOMEGA_SUBSTITUTION,
                ],
                "Substitution Ciphers": [
                    CalculationType.GREEK_BUILDING_VALUE_CUMULATIVE,
                    CalculationType.GREEK_HIDDEN_LETTER_NAME_VALUE,
                    CalculationType.GREEK_SUM_OF_LETTER_NAMES,
                    CalculationType.GREEK_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS,
                ],
            }

            # Add custom ciphers category if available
            greek_custom_ciphers = self.custom_service.get_ciphers(LanguageType.GREEK)
            if greek_custom_ciphers:
                greek_categories["Custom Methods"] = cast(
                    List[MethodType], greek_custom_ciphers
                )

            # Store the categories and their methods
            self._method_categories = greek_categories

            # Add the categories to the combobox
            for category in greek_categories.keys():
                self._category_combo.addItem(category)

            # Set default category to Standard Methods
            self._category_combo.setCurrentIndex(0)

        elif language == LanguageType.ENGLISH:
            english_categories: Dict[str, List[MethodType]] = {
                "TQ Methods": [CalculationType.ENGLISH_TQ_STANDARD_VALUE]
            }

            # Add custom ciphers category if available
            english_custom_ciphers = self.custom_service.get_ciphers(
                LanguageType.ENGLISH
            )
            if english_custom_ciphers:
                english_categories["Custom Methods"] = cast(
                    List[MethodType], english_custom_ciphers
                )

            # Store the categories and their methods
            self._method_categories = english_categories

            # Add the categories to the combobox
            for category in english_categories.keys():
                self._category_combo.addItem(category)

            # Set default category (only one for English)
            self._category_combo.setCurrentIndex(0)

        elif language == LanguageType.ARABIC:
            arabic_categories: Dict[str, List[MethodType]] = {
                "Standard Abjad": [CalculationType.ARABIC_STANDARD_ABJAD]
            }
            # Add custom ciphers category if available
            arabic_custom_ciphers = self.custom_service.get_ciphers(LanguageType.ARABIC)
            if arabic_custom_ciphers:
                arabic_categories["Custom Methods"] = cast(
                    List[MethodType], arabic_custom_ciphers
                )

            self._method_categories = arabic_categories
            for category in arabic_categories.keys():
                self._category_combo.addItem(category)
            if self._category_combo.count() > 0:
                self._category_combo.setCurrentIndex(0)

    def _populate_methods(self) -> None:
        """Populate the methods list based on selected category."""
        self._method_list.clear()

        category = self._category_combo.currentText()
        if not category or category not in self._method_categories:
            return

        methods = self._method_categories[category]

        # Add methods to list
        for method in methods:
            if isinstance(method, CalculationType):
                # Handle enum-based calculation types
                display_name = method.name.replace("_", " ").title()

                # For Greek methods, remove the "GREEK_" prefix
                if display_name.startswith("Greek "):
                    display_name = display_name[6:]

                item = QListWidgetItem(display_name)
                item.setData(Qt.ItemDataRole.UserRole, method)

                # Set tooltip with more information about the method
                tooltip = self._get_method_description(method)
                item.setToolTip(tooltip)

                self._method_list.addItem(item)
            elif isinstance(method, CustomCipherConfig):
                # Handle custom cipher configs
                item = QListWidgetItem(method.name)
                item.setData(Qt.ItemDataRole.UserRole, method)

                # Set tooltip with cipher description
                if method.description:
                    item.setToolTip(method.description)
                else:
                    item.setToolTip(
                        f"Custom {method.language.name.capitalize()} cipher"
                    )

                self._method_list.addItem(item)

        # Enable select button if there are methods
        has_methods = self._method_list.count() > 0
        self._select_btn.setEnabled(has_methods)

        # Auto-select the first item if available
        if has_methods:
            self._method_list.setCurrentRow(0)

    def _get_method_description(self, method: CalculationType) -> str:
        """Get a description for a calculation method.

        Args:
            method: The calculation method

        Returns:
            A description of the method
        """
        # Hebrew Standard & Ordinal
        if method == CalculationType.HEBREW_STANDARD_VALUE:
            return "Hebrew: Standard value (Mispar Hechrachi). Each letter has its numerical value."
        elif method == CalculationType.HEBREW_ORDINAL_VALUE:
            return "Hebrew: Ordinal value (Mispar Siduri). Each letter is counted based on its position."

        # Hebrew Reduction Methods
        elif method == CalculationType.HEBREW_SMALL_REDUCED_VALUE:  # Was MISPAR_KATAN
            return "Hebrew: Small/Reduced Value (Mispar Katan). Reduces letter values to a single digit."
        elif (
            method == CalculationType.HEBREW_INTEGRAL_REDUCED_VALUE
        ):  # Was MISPAR_MISPARI or conceptually MISPAR_KATAN_MISPARI
            return "Hebrew: Integral Reduced Value (Mispar Mispari). Sums the digits of each letter's value."

        # Hebrew Final Letters & Reversals
        elif method == CalculationType.HEBREW_FINAL_LETTER_VALUES:  # Was MISPAR_GADOL
            return "Hebrew: Final Letter Values (Mispar Sofit/Gadol). Final letters have values 500-900."
        elif (
            method == CalculationType.HEBREW_REVERSE_STANDARD_VALUES
        ):  # Was MISPAR_MESHUPACH
            return "Hebrew: Reverse Standard Values (Mispar Meshupach). Letter values are reversed (e.g., Alef=400)."

        # Hebrew Substitutions
        elif method == CalculationType.HEBREW_ALBAM_SUBSTITUTION:  # Was ALBAM
            return "Hebrew: Albam cipher. First letter is exchanged with 12th, 2nd with 13th, etc."
        elif method == CalculationType.HEBREW_ATBASH_SUBSTITUTION:  # Was ATBASH
            return "Hebrew: Atbash cipher. First letter exchanged with last, second with second-to-last, etc."

        # Hebrew Mathematical Operations
        elif (
            method == CalculationType.HEBREW_BUILDING_VALUE_CUMULATIVE
        ):  # Was MISPAR_BONEH
            return "Hebrew: Building Value (Mispar Bone'eh). Cumulative sum of letter values."
        elif method == CalculationType.HEBREW_TRIANGULAR_VALUE:  # Was MISPAR_KIDMI
            return "Hebrew: Triangular Value (Mispar Kidmi). Sum of values from Alef to the letter."
        elif (
            method == CalculationType.HEBREW_INDIVIDUAL_SQUARE_VALUE
        ):  # Was MISPAR_PERATI
            return "Hebrew: Individual Square Value (Mispar Perati/Bone'eh). Each letter's value is squared."
        elif method == CalculationType.HEBREW_CUBED_VALUE:  # Was MISPAR_MESHULASH
            return (
                "Hebrew: Cubed Value (Mispar Meshulash). Each letter's value is cubed."
            )

        # Hebrew Full Spelling Methods
        elif (
            method == CalculationType.HEBREW_SUM_OF_LETTER_NAMES_STANDARD
        ):  # Was MISPAR_SHEMI
            return "Hebrew: Sum of Letter Names - Standard (Mispar Shemi). Sums values of spelled-out letter names."
        elif method == CalculationType.HEBREW_SUM_OF_LETTER_NAMES_FINALS:
            return "Hebrew: Sum of Letter Names - Finals (Mispar Shemi Sofit). Uses final values in name spellings."
        elif method == CalculationType.HEBREW_PRODUCT_OF_LETTER_NAMES_STANDARD:
            return "Hebrew: Product of Letter Names - Standard. Multiplies values of spelled-out letter names."
        elif method == CalculationType.HEBREW_PRODUCT_OF_LETTER_NAMES_FINALS:
            return "Hebrew: Product of Letter Names - Finals. Multiplies using final values in name spellings."
        elif method == CalculationType.HEBREW_HIDDEN_VALUE_STANDARD:
            return "Hebrew: Hidden Value - Standard (Mispar Ne'elam). Name value minus letter value."
        elif method == CalculationType.HEBREW_HIDDEN_VALUE_FINALS:
            return "Hebrew: Hidden Value - Finals (Mispar Ne'elam Sofit). Name (finals) value minus letter value."
        elif method == CalculationType.HEBREW_FACE_VALUE_STANDARD:
            return "Hebrew: Face Value - Standard (Mispar HaPanim). First letter name + rest standard."
        elif method == CalculationType.HEBREW_FACE_VALUE_FINALS:
            return "Hebrew: Face Value - Finals (Mispar HaPanim Sofit). First letter name (finals) + rest standard."
        elif method == CalculationType.HEBREW_BACK_VALUE_STANDARD:
            return "Hebrew: Back Value - Standard (Mispar HaAchor). Rest standard + last letter name."
        elif method == CalculationType.HEBREW_BACK_VALUE_FINALS:
            return "Hebrew: Back Value - Finals (Mispar HaAchor Sofit). Rest standard + last letter name (finals)."

        # Hebrew Collective Methods
        elif (
            method == CalculationType.HEBREW_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS
        ):  # Was MISPAR_MUSAFI
            return "Hebrew: Collective Value (Mispar Kolel). Standard value plus number of letters."
        elif method == CalculationType.HEBREW_SUM_OF_LETTER_NAMES_STANDARD_PLUS_LETTERS:
            return "Hebrew: Name Collective - Standard (Mispar Shemi Kolel). Sum of names + letters."
        elif method == CalculationType.HEBREW_SUM_OF_LETTER_NAMES_FINALS_PLUS_LETTERS:
            return "Hebrew: Name Collective - Finals (Mispar Shemi Kolel Sofit). Sum of names (finals) + letters."
        elif method == CalculationType.HEBREW_STANDARD_VALUE_PLUS_ONE:
            return "Hebrew: Standard Value + 1 (Ragil plus Kolel). Standard value plus one."

        # Greek Standard & Ordinal
        elif method == CalculationType.GREEK_STANDARD_VALUE:  # Was GREEK_ISOPSOPHY
            return "Greek: Standard Value (Isopsophy). Traditional Greek letter values."
        elif method == CalculationType.GREEK_ORDINAL_VALUE:  # Was GREEK_ORDINAL
            return "Greek: Ordinal Value. Each letter numbered by position in alphabet."

        # Greek Mathematical Operations (Basic)
        elif method == CalculationType.GREEK_SQUARE_VALUE:  # Was GREEK_SQUARED
            return "Greek: Square Value. Square of standard Greek letter values."
        elif method == CalculationType.GREEK_CUBED_VALUE:  # Was GREEK_KYVOS
            return "Greek: Cubed Value (Kyvos). Cube of standard Greek letter values."
        elif method == CalculationType.GREEK_TRIANGULAR_VALUE:  # Was GREEK_TRIANGULAR
            return "Greek: Triangular Value. Triangular number of each letter's standard value."
        elif (
            method == CalculationType.GREEK_BUILDING_VALUE_CUMULATIVE
        ):  # Was GREEK_BUILDING
            return "Greek: Building Value. Cumulative value of letters as spelled out."

        # Greek Substitutions & Advanced
        elif (
            method == CalculationType.GREEK_REVERSE_STANDARD_VALUES
        ):  # Was GREEK_REVERSAL
            return "Greek: Reverse Standard Values. Letter values are reversed (α=800, ω=1)."
        elif method == CalculationType.GREEK_ALPHAMU_SUBSTITUTION:  # Was GREEK_ALPHA_MU
            return "Greek: Alpha-Mu Substitution. First half of alphabet exchanged with second."
        elif (
            method == CalculationType.GREEK_ALPHAOMEGA_SUBSTITUTION
        ):  # Was GREEK_ALPHA_OMEGA
            return (
                "Greek: Alpha-Omega Substitution (Values). Atbash-like value mapping."
            )
        elif method == CalculationType.GREEK_NEXT_LETTER_VALUE:  # Was GREEK_EPOMENOS
            return "Greek: Next Letter Value (Epomenos). Value of the following letter."
        elif (
            method == CalculationType.GREEK_CYCLICAL_PERMUTATION_VALUE
        ):  # Was GREEK_KYKLIKI
            return "Greek: Cyclical Permutation. Text permuted (abc->bca) then valued."

        # Greek Full Spelling & Name Values
        elif (
            method == CalculationType.GREEK_HIDDEN_LETTER_NAME_VALUE
        ):  # Was GREEK_HIDDEN
            return "Greek: Hidden Letter Name Value. Letter name value minus the letter itself."
        elif method == CalculationType.GREEK_SUM_OF_LETTER_NAMES:  # Was GREEK_FULL_NAME
            return "Greek: Sum of Letter Names. Value of the full letter name."

        # Greek Collective
        elif (
            method == CalculationType.GREEK_COLLECTIVE_VALUE_STANDARD_PLUS_LETTERS
        ):  # Was GREEK_ADDITIVE
            return "Greek: Collective Value. Standard value plus number of letters."

        # Greek - Additional Methods from Docs
        elif method == CalculationType.GREEK_SMALL_REDUCED_VALUE:
            return "Greek: Small Reduced Value. Reduces standard letter values to a single digit."
        elif method == CalculationType.GREEK_DIGITAL_VALUE:
            return "Greek: Digital Value. Sums digits of each letter's standard value."
        elif method == CalculationType.GREEK_DIGITAL_ORDINAL_VALUE:
            return "Greek: Digital Ordinal Value. Sums digits of each letter's ordinal value."
        elif method == CalculationType.GREEK_ORDINAL_SQUARE_VALUE:
            return (
                "Greek: Ordinal Square Value. Each letter's ordinal value is squared."
            )
        elif method == CalculationType.GREEK_PRODUCT_OF_LETTER_NAMES:
            return "Greek: Product of Letter Names. Multiplies values of spelled-out letter names."
        elif method == CalculationType.GREEK_FACE_VALUE:
            return "Greek: Face Value. First letter name value + rest standard values."
        elif method == CalculationType.GREEK_BACK_VALUE:
            return (
                "Greek: Back Value. Standard values of rest + last letter name value."
            )
        elif method == CalculationType.GREEK_SUM_OF_LETTER_NAMES_PLUS_LETTERS:
            return (
                "Greek: Name Collective Value. Sum of letter names + number of letters."
            )
        elif method == CalculationType.GREEK_STANDARD_VALUE_PLUS_ONE:
            return "Greek: Standard Value + 1. Standard value plus one."
        elif method == CalculationType.GREEK_ALPHABET_REVERSAL_SUBSTITUTION:
            return (
                "Greek: Alphabet Reversal Substitution. True Atbash (α=ω letter swap)."
            )
        elif method == CalculationType.GREEK_PAIR_MATCHING_SUBSTITUTION:
            return "Greek: Pair Matching Substitution (e.g. α=λ). Needs full cipher definition."

        # English TQ Methods
        elif method == CalculationType.ENGLISH_TQ_STANDARD_VALUE:  # Was TQ_ENGLISH
            return (
                "English: TQ Standard Value. Uses Trigrammaton Qabbalah letter values."
            )
        elif method == CalculationType.ENGLISH_TQ_REDUCED_VALUE:
            return (
                "English: TQ Reduced Value. Standard TQ sum reduced to a single digit."
            )
        elif method == CalculationType.ENGLISH_TQ_SQUARE_VALUE:
            return (
                "English: TQ Square Value. Each letter's TQ value squared, then summed."
            )
        elif method == CalculationType.ENGLISH_TQ_TRIANGULAR_VALUE:
            return "English: TQ Triangular Value. Triangular number of each letter's TQ value."
        elif method == CalculationType.ENGLISH_TQ_LETTER_POSITION_VALUE:
            return "English: TQ Letter Position. TQ value multiplied by its position in the word."

        # Coptic Methods
        elif method == CalculationType.COPTIC_STANDARD_VALUE:
            return "Coptic: Standard Value. Uses standard Coptic letter values."
        elif method == CalculationType.COPTIC_REDUCED_VALUE:
            return (
                "Coptic: Reduced Value. Standard Coptic sum reduced to a single digit."
            )

        elif method == CalculationType.ARABIC_STANDARD_ABJAD:
            return "Arabic: Standard Abjad (Hawwaz). Traditional Arabic letter values."

        else:
            # Fallback for any enums not explicitly handled (should not happen if all are covered)
            # or if a non-enum somehow gets here.
            name = method.name if hasattr(method, "name") else str(method)
            return f"{name.replace('_', ' ').title()} - Custom or unclassified method."
