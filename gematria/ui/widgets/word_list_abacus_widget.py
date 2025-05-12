"""
Purpose: Core widget implementation for the Gematria Word List Abacus.

This file is part of the gematria pillar and serves as a UI component.
It provides the core widget for calculating gematria values for lists of words,
supporting multiple calculation methods and custom ciphers.

Key components:
- WordListAbacusWidget: Core widget for Word List Abacus calculations

Dependencies:
- PyQt6: For UI components
- gematria.services.gematria_service: For gematria calculation service
- gematria.services.custom_cipher_service: For custom cipher management
- gematria.services.history_service: For calculation history management
- gematria.models.calculation_result: For storing calculation results
- gematria.models.calculation_type: For calculation method types
"""

import csv
import uuid
from datetime import datetime

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType, Language
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.services.gematria_service import GematriaService
from gematria.services.history_service import HistoryService
from gematria.ui.widgets.virtual_keyboard_widget import VirtualKeyboardWidget


class WordListAbacusWidget(QWidget):
    """Widget for calculating gematria values for lists of words."""

    # Signal emitted when calculations are performed - sends a list of results
    calculations_performed = pyqtSignal(list)

    def __init__(
        self,
        calculation_service: GematriaService,
        custom_cipher_service: CustomCipherService,
        history_service: HistoryService,
    ) -> None:
        """Initialize WordListAbacusWidget.

        Args:
            calculation_service: Service for performing gematria calculations
            custom_cipher_service: Service for managing custom ciphers
            history_service: Service for managing calculation history
        """
        super().__init__()
        self._calculation_service = calculation_service
        self._custom_cipher_service = custom_cipher_service
        self._history_service = history_service
        self._virtual_keyboard = None

        # Store calculation results
        self._current_results = []

        # Initialize UI components
        self._setup_ui()

        # Connect signals
        self._connect_signals()

        # Set initial state
        self._update_ui()

    def _setup_ui(self) -> None:
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)

        # Input section
        input_group = QGroupBox("Word List Input")
        input_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        input_layout = QVBoxLayout()

        # Language selection
        lang_layout = QHBoxLayout()
        self._language_combo = QComboBox()
        self._language_combo.addItems(["Hebrew", "Greek", "English"])
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)

        lang_layout.addWidget(QLabel("Language:"))
        lang_layout.addWidget(self._language_combo)
        lang_layout.addStretch()

        input_layout.addLayout(lang_layout)

        # Word list input
        self._word_list_label = QLabel("Enter words (one per line):")
        self._word_list_input = QTextEdit()
        self._word_list_input.setPlaceholderText("Enter words here, one per line...")

        input_layout.addWidget(self._word_list_label)

        # Add word list input and keyboard button in a horizontal layout
        input_hbox = QHBoxLayout()
        input_layout.addLayout(input_hbox)

        input_hbox.addWidget(self._word_list_input)

        # Virtual keyboard button (for Hebrew/Greek)
        keyboard_layout = QVBoxLayout()
        self._vk_button = QPushButton("⌨️")
        self._vk_button.setToolTip("Open Virtual Keyboard")
        self._vk_button.setFixedWidth(36)
        self._vk_button.clicked.connect(self._show_virtual_keyboard)
        keyboard_layout.addWidget(self._vk_button)
        keyboard_layout.addStretch()
        input_hbox.addLayout(keyboard_layout)

        # Method selection
        method_layout = QVBoxLayout()
        method_label = QLabel("Select Calculation Methods:")
        method_label.setStyleSheet("font-weight: bold;")
        method_layout.addWidget(method_label)

        # Method type combo
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Method Category:"))
        self._method_type_combo = QComboBox()
        self._method_type_combo.currentIndexChanged.connect(self._on_type_changed)
        type_layout.addWidget(self._method_type_combo)
        type_layout.addStretch()
        method_layout.addLayout(type_layout)

        # Method checkboxes container (will be populated dynamically)
        self._method_container = QWidget()
        self._method_layout = QVBoxLayout(self._method_container)
        self._method_layout.setContentsMargins(0, 0, 0, 0)
        self._method_checkboxes = {}  # To store method checkboxes

        method_layout.addWidget(self._method_container)
        input_layout.addLayout(method_layout)

        # Add calculate button at the bottom of input panel
        calculate_layout = QHBoxLayout()
        self._calc_button = QPushButton("Calculate")
        self._calc_button.setEnabled(False)  # Disabled until text is entered
        self._calc_button.clicked.connect(self._calculate)
        self._calc_button.setStyleSheet(
            "background-color: #2ecc71; color: white; font-weight: bold; padding: 10px 20px;"
        )
        calculate_layout.addStretch()
        calculate_layout.addWidget(self._calc_button)

        input_layout.addLayout(calculate_layout)
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Results section
        results_group = QGroupBox("Calculation Results")
        results_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        results_layout = QVBoxLayout()

        # Results table
        self._results_table = QTableWidget(0, 3)  # Rows, Columns (Word, Method, Value)
        self._results_table.setHorizontalHeaderLabels(["Word", "Method", "Value"])
        self._results_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._results_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._results_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )

        results_layout.addWidget(self._results_table)

        # Summary section
        summary_layout = QHBoxLayout()
        summary_layout.addWidget(QLabel("Word Count:"))
        self._word_count_label = QLabel("0")
        self._word_count_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self._word_count_label)

        summary_layout.addSpacing(20)

        summary_layout.addWidget(QLabel("Selected Methods:"))
        self._method_count_label = QLabel("0")
        self._method_count_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self._method_count_label)

        summary_layout.addSpacing(20)

        summary_layout.addWidget(QLabel("Total Calculations:"))
        self._calc_count_label = QLabel("0")
        self._calc_count_label.setStyleSheet("font-weight: bold;")
        summary_layout.addWidget(self._calc_count_label)

        summary_layout.addStretch()

        results_layout.addLayout(summary_layout)

        # Filter options
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by Value:"))
        self._filter_input = QLineEdit()
        self._filter_input.setPlaceholderText("Enter a value to filter results...")
        self._filter_input.textChanged.connect(self._apply_filter)
        filter_layout.addWidget(self._filter_input)

        results_layout.addLayout(filter_layout)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Set the default language to match the combo box
        self._current_language = Language.HEBREW

        # Initialize methods for the current language
        self._populate_method_categories()

    def _connect_signals(self) -> None:
        """Connect UI signals to handlers."""
        self._word_list_input.textChanged.connect(self._on_word_list_changed)

    def _update_ui(self) -> None:
        """Update UI state based on current selections."""
        # Update the virtual keyboard button based on language
        self._update_virtual_keyboard_button()

    def _populate_method_categories(self) -> None:
        """Populate the method categories dropdown based on the current language."""
        self._method_type_combo.clear()

        language_text = self._language_combo.currentText().lower()

        try:
            self._current_language = Language(language_text)

            # Add standard categories
            self._method_type_combo.addItem("Standard Methods")

            # Add custom ciphers category if there are custom ciphers for this language
            custom_ciphers = self._custom_cipher_service.get_methods_for_language(
                self._current_language
            )
            if custom_ciphers:
                self._method_type_combo.addItem("Custom Ciphers")

            # Select the first category
            self._method_type_combo.setCurrentIndex(0)

            # This will trigger _on_type_changed which will populate the methods
        except (ValueError, KeyError):
            logger.error(f"Invalid language: {language_text}")

    def _populate_methods(self) -> None:
        """Populate the method selection area with checkboxes."""
        # Clear existing checkboxes and the map
        for key, (checkbox, _) in self._method_checkboxes.items():
            self._method_layout.removeWidget(checkbox)
            checkbox.deleteLater()
        self._method_checkboxes = {}

        # Determine which methods to show based on the current category
        category = self._method_type_combo.currentText()
        language_text = self._language_combo.currentText().lower()

        try:
            language = Language(language_text)

            if category == "Standard Methods":
                # Show standard methods for the current language
                method_types = CalculationType.get_types_for_language(language)

                for method_type in method_types:
                    checkbox = QCheckBox(method_type.display_name)
                    # Store the method_type name as the key and a tuple of (checkbox, method_type) as the value
                    key = f"std_{method_type.name}"
                    self._method_checkboxes[key] = (checkbox, method_type)
                    self._method_layout.addWidget(checkbox)

                    # Select the default method
                    if method_type == CalculationType.get_default_for_language(
                        language
                    ):
                        checkbox.setChecked(True)

            elif category == "Custom Ciphers":
                # Show custom ciphers for the current language
                custom_ciphers = self._custom_cipher_service.get_methods_for_language(
                    language
                )

                for cipher in custom_ciphers:
                    checkbox = QCheckBox(cipher.name)
                    # Store the cipher name as the key and a tuple of (checkbox, cipher) as the value
                    key = f"custom_{cipher.name}"
                    self._method_checkboxes[key] = (checkbox, cipher)
                    self._method_layout.addWidget(checkbox)

                    # Select first custom cipher by default
                    if custom_ciphers and cipher == custom_ciphers[0]:
                        checkbox.setChecked(True)

        except (ValueError, KeyError):
            logger.error(f"Invalid language: {language_text}")

    def _on_language_changed(self, index: int) -> None:
        """Handle language selection change.

        Args:
            index: The index of the selected language in the combo box
        """
        language = self._language_combo.itemText(index)

        # Update the word list input label
        self._word_list_label.setText(f"Enter {language} words (one per line):")

        # Update method categories for the selected language
        self._populate_method_categories()

        # Update virtual keyboard button
        self._update_virtual_keyboard_button()

    def _on_type_changed(self, index: int) -> None:
        """Handle method type selection changes.

        Args:
            index: The selected index in the combo box
        """
        self._populate_methods()

    def _on_word_list_changed(self) -> None:
        """Handle word list text changes."""
        # Enable the calculate button if there's text
        text = self._word_list_input.toPlainText().strip()
        self._calc_button.setEnabled(bool(text))

        # Update word count
        if text:
            lines = [line.strip() for line in text.split("\n")]
            words = [line for line in lines if line]  # Filter out empty lines
            self._word_count_label.setText(str(len(words)))
        else:
            self._word_count_label.setText("0")

        # Update calculation count
        self._update_calculation_count()

    def _update_calculation_count(self) -> None:
        """Update the calculation count label based on selected items."""
        word_count = int(self._word_count_label.text())

        # Count selected methods
        method_count = sum(
            1
            for _, (checkbox, _) in self._method_checkboxes.items()
            if checkbox.isChecked()
        )
        self._method_count_label.setText(str(method_count))

        # Calculate total calculations
        calc_count = word_count * method_count
        self._calc_count_label.setText(str(calc_count))

    def _update_virtual_keyboard_button(self) -> None:
        """Update the virtual keyboard button visibility based on language."""
        language = self._language_combo.currentText()
        # Only show keyboard for Hebrew and Greek
        self._vk_button.setVisible(language in ["Hebrew", "Greek"])

    def _calculate(self) -> None:
        """Handle calculate button click to process the word list."""
        # Get all words from the input
        text = self._word_list_input.toPlainText().strip()
        if not text:
            return

        lines = [line.strip() for line in text.split("\n")]
        words = [line for line in lines if line]  # Filter out empty lines

        if not words:
            return

        # Get selected calculation methods
        selected_methods = []
        for key, (checkbox, method) in self._method_checkboxes.items():
            if checkbox.isChecked():
                selected_methods.append(method)

        if not selected_methods:
            QMessageBox.warning(
                self,
                "No Methods Selected",
                "Please select at least one calculation method.",
                QMessageBox.StandardButton.Ok,
            )
            return

        # Clear previous results
        self._current_results = []
        self._results_table.setRowCount(0)

        # Calculate results for each word and method
        for word in words:
            for method in selected_methods:
                try:
                    # Calculate the value
                    result_value = self._calculation_service.calculate(word, method)

                    # Create a calculation result object
                    result = CalculationResult(
                        id=str(uuid.uuid4()),
                        input_text=word,
                        calculation_type=method,
                        result_value=result_value,
                        timestamp=datetime.now(),
                    )

                    # Add to results list
                    self._current_results.append(result)

                    # Add to results table
                    self._add_result_to_table(result)

                except Exception as e:
                    logger.error(f"Error calculating {word} with {method}: {e}")

        # Emit signal with all results
        self.calculations_performed.emit(self._current_results)

        # Update calculation count
        self._update_calculation_count()

        # Clear filter
        self._filter_input.clear()

    def _add_result_to_table(self, result: CalculationResult) -> None:
        """Add a calculation result to the results table.

        Args:
            result: The calculation result to add
        """
        row = self._results_table.rowCount()
        self._results_table.insertRow(row)

        # Word item
        word_item = QTableWidgetItem(result.input_text)
        self._results_table.setItem(row, 0, word_item)

        # Method item
        if hasattr(result.calculation_type, "display_name"):
            method_name = result.calculation_type.display_name
        elif hasattr(result.calculation_type, "name"):
            method_name = result.calculation_type.name
        else:
            method_name = str(result.calculation_type)

        method_item = QTableWidgetItem(method_name)
        self._results_table.setItem(row, 1, method_item)

        # Value item - right-aligned
        value_item = QTableWidgetItem(str(result.result_value))
        value_item.setTextAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        value_item.setData(
            Qt.ItemDataRole.UserRole, result.result_value
        )  # Store for filtering

        # Set bold font for value
        font = QFont()
        font.setBold(True)
        value_item.setFont(font)

        self._results_table.setItem(row, 2, value_item)

    def _apply_filter(self, filter_text: str) -> None:
        """Filter the results table based on the value.

        Args:
            filter_text: The filter text (should be a number)
        """
        if not filter_text.strip():
            # Show all rows
            for row in range(self._results_table.rowCount()):
                self._results_table.setRowHidden(row, False)
            return

        try:
            filter_value = int(filter_text)

            # Check each row
            for row in range(self._results_table.rowCount()):
                value_item = self._results_table.item(row, 2)
                if value_item:
                    value = value_item.data(Qt.ItemDataRole.UserRole)
                    self._results_table.setRowHidden(row, value != filter_value)

        except ValueError:
            # Invalid number, don't filter
            for row in range(self._results_table.rowCount()):
                self._results_table.setRowHidden(row, False)

    def _show_virtual_keyboard(self) -> None:
        """Show the floating virtual keyboard for the current language."""
        language = self._language_combo.currentText()
        if language not in ("Hebrew", "Greek"):
            return

        if self._virtual_keyboard:
            self._virtual_keyboard.close()

        self._virtual_keyboard = VirtualKeyboardWidget(language=language, parent=self)
        self._virtual_keyboard.key_pressed.connect(self._handle_virtual_key)
        self._virtual_keyboard.show()
        self._virtual_keyboard.raise_()
        self._virtual_keyboard.activateWindow()

    def _handle_virtual_key(self, key: str) -> None:
        """Handle key press from the virtual keyboard.

        Args:
            key: The key that was pressed
        """
        if key == "<BACKSPACE>":
            # Delete the character before the cursor
            cursor = self._word_list_input.textCursor()
            cursor.deletePreviousChar()
        elif key == "<CLEAR>":
            # Clear the current line
            cursor = self._word_list_input.textCursor()
            cursor.select(cursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
        else:
            # Insert the character at the cursor position
            self._word_list_input.insertPlainText(key)

    def refresh_methods(self) -> None:
        """Refresh the method selection after custom ciphers change."""
        self._populate_method_categories()

    def update_word_list(self) -> None:
        """Update the word list after import."""
        # This is called after words are imported via ImportWordListDialog
        # Get the parent panel to access the import dialog
        if hasattr(self.parent(), "word_list_abacus_panel"):
            panel = self.parent().word_list_abacus_panel
            if hasattr(panel, "_import_dialog") and panel._import_dialog:
                imported_words = panel._import_dialog.get_word_list()
                if imported_words:
                    # Add imported words to the text edit
                    current_text = self._word_list_input.toPlainText().strip()
                    if current_text:
                        # If there's already text, add a newline
                        current_text += "\n"
                    new_text = current_text + "\n".join(imported_words)
                    self._word_list_input.setPlainText(new_text)
                    logger.info(
                        f"Added {len(imported_words)} words to the word list input"
                    )

        # Enable calculate button if there's text
        self._calc_button.setEnabled(bool(self._word_list_input.toPlainText().strip()))

        # Update word count
        self._on_word_list_changed()

    def export_results(self) -> None:
        """Export the calculation results to a CSV file."""
        if not self._current_results:
            QMessageBox.information(
                self,
                "No Results",
                "There are no results to export.",
                QMessageBox.StandardButton.Ok,
            )
            return

        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        # Ensure file has .csv extension
        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(["Word", "Method", "Value"])

                # Write data
                for result in self._current_results:
                    if hasattr(result.calculation_type, "display_name"):
                        method_name = result.calculation_type.display_name
                    elif hasattr(result.calculation_type, "name"):
                        method_name = result.calculation_type.name
                    else:
                        method_name = str(result.calculation_type)

                    writer.writerow(
                        [result.input_text, method_name, result.result_value]
                    )

            QMessageBox.information(
                self,
                "Export Successful",
                f"Results exported to {file_path}",
                QMessageBox.StandardButton.Ok,
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Error exporting results: {e}",
                QMessageBox.StandardButton.Ok,
            )
            logger.error(f"Error exporting results: {e}")

    def reset(self) -> None:
        """Reset the widget to its initial state."""
        # Clear word list input
        self._word_list_input.clear()

        # Clear results
        self._results_table.setRowCount(0)
        self._current_results = []

        # Clear filter
        self._filter_input.clear()

        # Reset counters
        self._word_count_label.setText("0")
        self._method_count_label.setText("0")
        self._calc_count_label.setText("0")

        # Select default language and method
        self._language_combo.setCurrentIndex(0)  # Hebrew
