"""Custom Cipher Dialog.

This module provides a dialog for creating and editing custom gematria ciphers.
"""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    cast,
)

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

from gematria.models.calculation_type import CalculationType
from gematria.models.custom_cipher_config import CustomCipherConfig, LanguageType
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.services.gematria_service import GematriaService

# Define method type as a union of CalculationType and CustomCipherConfig
MethodType = Union[CalculationType, CustomCipherConfig]


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

        # Greek standard values
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
            "ς": 200,
        }

        # Greek ordinal values
        greek_ordinal = {
            "α": 1,
            "β": 2,
            "γ": 3,
            "δ": 4,
            "ε": 5,
            "ζ": 7,
            "η": 8,
            "θ": 9,
            "ι": 10,
            "κ": 11,
            "λ": 12,
            "μ": 13,
            "ν": 14,
            "ξ": 15,
            "ο": 16,
            "π": 17,
            "ρ": 18,
            "σ": 19,
            "τ": 20,
            "υ": 21,
            "φ": 22,
            "χ": 23,
            "ψ": 24,
            "ω": 25,
            "ς": 19,
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

        # TQ English values
        english_tq = {
            "i": 0,
            "I": 0,
            "l": 1,
            "L": 1,
            "c": 2,
            "C": 2,
            "h": 3,
            "H": 3,
            "p": 4,
            "P": 4,
            "a": 5,
            "A": 5,
            "x": 6,
            "X": 6,
            "j": 7,
            "J": 7,
            "w": 8,
            "W": 8,
            "t": 9,
            "T": 9,
            "o": 10,
            "O": 10,
            "g": 11,
            "G": 11,
            "f": 12,
            "F": 12,
            "e": 13,
            "E": 13,
            "r": 14,
            "R": 14,
            "s": 15,
            "S": 15,
            "q": 16,
            "Q": 16,
            "k": 17,
            "K": 17,
            "y": 18,
            "Y": 18,
            "z": 19,
            "Z": 19,
            "b": 20,
            "B": 20,
            "m": 21,
            "M": 21,
            "v": 22,
            "V": 22,
            "d": 23,
            "D": 23,
            "n": 24,
            "N": 24,
            "u": 25,
            "U": 25,
        }

        # English A=1 through Z=26
        english_ordinal = {}
        for i, letter in enumerate("abcdefghijklmnopqrstuvwxyz"):
            english_ordinal[letter] = i + 1

        # Use appropriate letter values based on the calculation type
        if language == LanguageType.HEBREW:
            if calc_type == CalculationType.MISPAR_HECHRACHI:
                cipher.letter_values = hebrew_standard.copy()
            elif calc_type == CalculationType.MISPAR_SIDURI:
                cipher.letter_values = hebrew_ordinal.copy()
            elif calc_type == CalculationType.MISPAR_KATAN:
                cipher.letter_values = hebrew_reduced.copy()
            elif calc_type == CalculationType.MISPAR_KATAN_MISPARI:
                # Same as reduced for initialization
                cipher.letter_values = hebrew_reduced.copy()
            elif calc_type == CalculationType.MISPAR_GADOL:
                cipher.letter_values = hebrew_gadol.copy()
                cipher.use_final_forms = True
            elif calc_type == CalculationType.MISPAR_MESHUPACH:
                cipher.letter_values = hebrew_reversal.copy()
            elif calc_type == CalculationType.ALBAM:
                cipher.letter_values = hebrew_albam.copy()
            elif calc_type == CalculationType.ATBASH:
                cipher.letter_values = hebrew_atbash.copy()
            else:
                # For other types, use standard values
                cipher.letter_values = hebrew_standard.copy()

        elif language == LanguageType.GREEK:
            if calc_type == CalculationType.GREEK_ISOPSOPHY:
                cipher.letter_values = greek_standard.copy()
            elif calc_type == CalculationType.GREEK_ORDINAL:
                cipher.letter_values = greek_ordinal.copy()
            elif calc_type == CalculationType.GREEK_REDUCED:
                cipher.letter_values = greek_reduced.copy()
            elif calc_type == CalculationType.GREEK_INTEGRAL_REDUCED:
                # Same as reduced for initialization
                cipher.letter_values = greek_reduced.copy()
            elif calc_type == CalculationType.GREEK_REVERSAL:
                cipher.letter_values = greek_reversal.copy()
            elif calc_type == CalculationType.GREEK_ALPHA_MU:
                cipher.letter_values = greek_alpha_mu.copy()
            elif calc_type == CalculationType.GREEK_ALPHA_OMEGA:
                cipher.letter_values = greek_alpha_omega.copy()
            else:
                # For other types, use standard values
                cipher.letter_values = greek_standard.copy()

        elif language == LanguageType.ENGLISH:
            if calc_type == CalculationType.TQ_ENGLISH:
                cipher.letter_values = english_tq.copy()
                cipher.case_sensitive = True
            else:
                # For other types, use English A=1 through Z=26
                cipher.letter_values = english_ordinal.copy()

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
                    CalculationType.MISPAR_HECHRACHI,
                    CalculationType.MISPAR_SIDURI,
                    CalculationType.MISPAR_KATAN,
                    CalculationType.MISPAR_KATAN_MISPARI,
                ],
                "Advanced Methods": [
                    CalculationType.MISPAR_GADOL,
                    CalculationType.MISPAR_BONEH,
                    CalculationType.MISPAR_KIDMI,
                    CalculationType.MISPAR_NEELAM,
                    CalculationType.MISPAR_PERATI,
                    CalculationType.MISPAR_SHEMI,
                    CalculationType.MISPAR_MUSAFI,
                ],
                "Substitution Ciphers": [
                    CalculationType.MISPAR_MESHUPACH,
                    CalculationType.ALBAM,
                    CalculationType.ATBASH,
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
                    CalculationType.GREEK_ISOPSOPHY,
                    CalculationType.GREEK_ORDINAL,
                    CalculationType.GREEK_REDUCED,
                    CalculationType.GREEK_INTEGRAL_REDUCED,
                ],
                "Advanced Methods": [
                    CalculationType.GREEK_LARGE,
                    CalculationType.GREEK_BUILDING,
                    CalculationType.GREEK_TRIANGULAR,
                    CalculationType.GREEK_HIDDEN,
                    CalculationType.GREEK_INDIVIDUAL_SQUARE,
                    CalculationType.GREEK_FULL_NAME,
                    CalculationType.GREEK_ADDITIVE,
                    CalculationType.GREEK_SQUARED,
                ],
                "Substitution Ciphers": [
                    CalculationType.GREEK_REVERSAL,
                    CalculationType.GREEK_ALPHA_MU,
                    CalculationType.GREEK_ALPHA_OMEGA,
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
                "TQ Methods": [CalculationType.TQ_ENGLISH]
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

    def _get_method_description(self, method: Any) -> str:
        """Get a description for a calculation method.

        Args:
            method: Calculation method (can be enum or custom)

        Returns:
            Description text
        """
        # Handle standard calculation types
        if isinstance(method, CalculationType):
            # Hebrew methods
            if method == CalculationType.MISPAR_HECHRACHI:
                return "Standard values (א=1, ב=2, ..., ת=400)"
            elif method == CalculationType.MISPAR_SIDURI:
                return "Ordinal values (א=1, ב=2, ..., ת=22)"
            elif method == CalculationType.MISPAR_KATAN:
                return "Reduced values (single digit where possible)"
            elif method == CalculationType.MISPAR_KATAN_MISPARI:
                return "Integral reduced values (convergence to a single digit)"
            elif method == CalculationType.MISPAR_GADOL:
                return "Large values with final forms 500-900"
            elif method == CalculationType.MISPAR_BONEH:
                return "Cumulative value of letters as word is spelled"
            elif method == CalculationType.MISPAR_KIDMI:
                return "Sum of all letters up to the current letter in the alphabet"
            elif method == CalculationType.MISPAR_NEELAM:
                return "Value of letter name without the letter itself"
            elif method == CalculationType.MISPAR_PERATI:
                return "Each letter value is squared individually"
            elif method == CalculationType.MISPAR_SHEMI:
                return "Value of the full letter name"
            elif method == CalculationType.MISPAR_MUSAFI:
                return "Adds the number of letters to the value"
            elif method == CalculationType.MISPAR_HAAKHOR:
                return "Value of the letter name"
            elif method == CalculationType.MISPAR_HAMERUBAH_HAKLALI:
                return "Square of standard value"
            elif method == CalculationType.MISPAR_HAPANIM:
                return "Value of the full letter name"
            elif method == CalculationType.MISPAR_MESHUPACH:
                return "Letter values reversed (א=400, ת=1)"
            elif method == CalculationType.ALBAM:
                return "Letter substitution cipher (א↔ל, ב↔מ, etc.)"
            elif method == CalculationType.ATBASH:
                return "Letter substitution cipher (א↔ת, ב↔ש, etc.)"

            # Greek methods
            elif method == CalculationType.GREEK_ISOPSOPHY:
                return "Standard Greek values (α=1, β=2, ..., ω=800)"
            elif method == CalculationType.GREEK_ORDINAL:
                return "Greek ordinal values (α=1, β=2, ..., ω=24)"
            elif method == CalculationType.GREEK_REDUCED:
                return "Greek reduced values (single digit where possible)"
            elif method == CalculationType.GREEK_INTEGRAL_REDUCED:
                return "Greek integral reduced values (convergence to a single digit)"
            elif method == CalculationType.GREEK_LARGE:
                return "Greek large values with extended values"
            elif method == CalculationType.GREEK_BUILDING:
                return "Greek cumulative values"
            elif method == CalculationType.GREEK_TRIANGULAR:
                return "Greek triangular values"
            elif method == CalculationType.GREEK_HIDDEN:
                return "Greek hidden values"
            elif method == CalculationType.GREEK_INDIVIDUAL_SQUARE:
                return "Greek individual squared values"
            elif method == CalculationType.GREEK_FULL_NAME:
                return "Greek full name values"
            elif method == CalculationType.GREEK_ADDITIVE:
                return "Greek additive values"
            elif method == CalculationType.GREEK_SQUARED:
                return "Greek squared values"
            elif method == CalculationType.GREEK_REVERSAL:
                return "Greek reversal values (α=800, ω=1)"
            elif method == CalculationType.GREEK_ALPHA_MU:
                return "Greek Alpha-Mu cipher (similar to Hebrew Albam)"
            elif method == CalculationType.GREEK_ALPHA_OMEGA:
                return "Greek Alpha-Omega cipher (similar to Hebrew Atbash)"

            # English methods
            elif method == CalculationType.TQ_ENGLISH:
                return "Trigrammaton Qabalah English values"

        # For custom methods or unhandled enum values
        method_name = method.name if hasattr(method, "name") else str(method)
        return f"Custom calculation method: {method_name}"
