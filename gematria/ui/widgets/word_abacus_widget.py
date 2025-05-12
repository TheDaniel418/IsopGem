"""
Purpose: Provides a widget for performing gematria calculations

This file is part of the gematria pillar and serves as a UI component.
It provides a calculator interface that allows users to perform gematria
calculations on Hebrew, Greek, or English text using various methods.

Key components:
- WordAbacusWidget: Main calculator widget with language and method selection

Dependencies:
- PyQt6: For building the graphical user interface
- gematria.services.gematria_service: For performing the actual calculations
- gematria.models.calculation_type: For the available calculation methods

Related files:
- gematria/services/gematria_service.py: Service for performing calculations
- gematria/models/calculation_result.py: Model for storing calculation results
- gematria/ui/dialogs/custom_cipher_dialog.py: For managing custom ciphers
"""

from typing import List, Optional, Union, cast

from loguru import logger
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType, Language
from gematria.models.custom_cipher_config import CustomCipherConfig, LanguageType
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.services.gematria_service import GematriaService
from gematria.services.history_service import HistoryService
from gematria.ui.dialogs.custom_cipher_dialog import CustomCipherDialog
from gematria.ui.widgets.virtual_keyboard_widget import VirtualKeyboardWidget

# Import the polygon service for sending values to the Regular Polygon Calculator

# Define method type as a union of CalculationType and CustomCipherConfig
MethodType = Union[CalculationType, CustomCipherConfig]


class WordAbacusWidget(QWidget):
    """Widget for calculating gematria values."""

    # Signal emitted when a calculation is performed
    calculation_performed = pyqtSignal(CalculationResult)

    def __init__(
        self,
        calculation_service: GematriaService,
        custom_cipher_service: CustomCipherService,
        history_service: HistoryService,
    ) -> None:
        """Initialize WordAbacusWidget.

        Args:
            calculation_service: Service for performing gematria calculations
            custom_cipher_service: Service for managing custom ciphers
            history_service: Service for managing calculation history
        """
        super().__init__()
        self._calculation_service = calculation_service
        self._custom_cipher_service = custom_cipher_service
        self._history_service = history_service
        self._custom_cipher_dialog: Optional[CustomCipherDialog] = None

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

        # Title with divider
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 10)

        title_label = QLabel("Word Abacus")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        title_layout.addWidget(title_label)

        # Add a horizontal line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #bdc3c7;")
        title_layout.addWidget(line)

        layout.addWidget(title_container)

        # Create a group box for input
        input_group = QGroupBox("Text Input")
        input_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        input_layout = QGridLayout()

        # Language selection
        self._language_combo = QComboBox()
        self._language_combo.addItems(
            ["Hebrew", "Greek", "English", "Coptic", "Arabic"]
        )
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)

        # New QHBoxLayout for Language and Transliteration toggle
        lang_translit_hbox = QHBoxLayout()
        lang_translit_hbox.addWidget(self._language_combo)
        self._transliterate_chk = QCheckBox("Transliterate Latin")
        self._transliterate_chk.setToolTip(
            "If checked, attempts to transliterate Latin input to the selected script before calculation."
        )
        self._transliterate_chk.setChecked(False)  # Default to unchecked
        lang_translit_hbox.addWidget(self._transliterate_chk)
        lang_translit_hbox.addStretch(
            1
        )  # Add stretch to push checkbox to the right of combo, or let them be compact

        input_layout.addWidget(QLabel("Language:"), 0, 0)
        input_layout.addLayout(lang_translit_hbox, 0, 1)

        # Input text field and virtual keyboard button
        self._input_label = QLabel("Enter Hebrew text:")
        self._input_field = QLineEdit()
        self._input_field.setPlaceholderText("Type text here...")
        self._input_field.textChanged.connect(self._on_input_changed)
        input_layout.addWidget(self._input_label, 1, 0)

        # Add input field and keyboard button in a horizontal layout
        input_hbox = QHBoxLayout()
        input_hbox.addWidget(self._input_field)
        self._vk_button = QPushButton("⌨️")
        self._vk_button.setToolTip("Open Virtual Keyboard")
        self._vk_button.setFixedWidth(36)
        self._vk_button.clicked.connect(self._show_virtual_keyboard)
        input_hbox.addWidget(self._vk_button)
        input_layout.addLayout(input_hbox, 1, 1)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Create a group box for calculation methods
        method_group = QGroupBox("Calculation Method")
        method_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        method_layout = QGridLayout()

        # Method selection (specific calculations)
        method_layout.addWidget(QLabel("Method:"), 0, 0)
        self._method_combo = QComboBox()
        method_layout.addWidget(self._method_combo, 0, 1)

        # Custom cipher button
        self._custom_cipher_button = QPushButton("Manage Custom Ciphers")
        self._custom_cipher_button.clicked.connect(self._open_custom_cipher_manager)
        method_layout.addWidget(self._custom_cipher_button, 1, 0, 1, 2)

        self._method_combo.currentIndexChanged.connect(self._on_method_changed)

        method_group.setLayout(method_layout)
        layout.addWidget(method_group)

        # Calculate button and result in a nice group box
        result_group = QGroupBox("Calculation")
        result_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        result_layout = QHBoxLayout()

        self._calc_button = QPushButton("Calculate")
        self._calc_button.setStyleSheet(
            "background-color: #3498db; color: white; font-weight: bold; padding: 8px 16px;"
        )
        # Connection to _calculate is handled in _connect_signals
        self._calc_button.setEnabled(False)  # Disabled until text is entered

        # Add "Send to PolyCalc" button
        self._send_to_polycalc_button = QPushButton("Send to PolyCalc")
        self._send_to_polycalc_button.setStyleSheet(
            "background-color: #27ae60; color: white; font-weight: bold; padding: 8px 16px;"
        )
        self._send_to_polycalc_button.setEnabled(
            False
        )  # Disabled until calculation is performed
        self._send_to_polycalc_button.clicked.connect(self._send_to_polygon_calculator)

        self._result_label = QLabel("Result: ")
        self._result_value = QLabel("0")
        self._result_value.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #2c3e50;"
        )

        result_layout.addWidget(self._calc_button)
        result_layout.addWidget(self._send_to_polycalc_button)
        result_layout.addWidget(self._result_label)
        result_layout.addWidget(self._result_value)
        result_layout.addStretch()

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        # History section
        history_group = QGroupBox("Calculation History")
        history_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        history_layout = QVBoxLayout()

        self._history_table = QTableWidget(0, 5)  # Rows, Columns
        self._history_table.setHorizontalHeaderLabels(
            ["Input", "Method", "Result", "Time", "Notes"]
        )
        self._history_table.setStyleSheet(
            "QHeaderView::section { background-color: #ecf0f1; }"
        )
        self._history_table.horizontalHeader().setStretchLastSection(True)
        history_layout.addWidget(self._history_table)

        # Clear history button
        clear_button = QPushButton("Clear History")
        clear_button.setStyleSheet(
            "background-color: #e74c3c; color: white; font-weight: bold;"
        )
        clear_button.clicked.connect(self.clear_history)
        history_layout.addWidget(clear_button)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # Set the layout spacing
        layout.setSpacing(15)
        self.setLayout(layout)

        # Initialize the language-specific UI
        self._populate_methods_for_selected_language()
        self._language_combo.setCurrentIndex(0)  # Default to Hebrew

        # Track the virtual keyboard dialog
        self._virtual_keyboard = None
        self._update_virtual_keyboard_button()

    def _populate_methods_for_selected_language(self) -> None:
        """Populate the methods combobox based on the selected language."""
        self._method_combo.clear()

        current_language_str = self._language_combo.currentText()
        language_enum: Optional[Language] = None

        if current_language_str == "Hebrew":
            language_enum = Language.HEBREW
        elif current_language_str == "Greek":
            language_enum = Language.GREEK
        elif current_language_str == "English":
            language_enum = Language.ENGLISH
        elif current_language_str == "Coptic":
            language_enum = Language.COPTIC
        elif current_language_str == "Arabic":
            language_enum = Language.ARABIC

        all_methods_for_combo: List[MethodType] = []

        if language_enum:
            # Add standard calculation types for the language
            standard_types = CalculationType.get_types_for_language(language_enum)
            all_methods_for_combo.extend(standard_types)

            # Add custom ciphers for the language
            # Ensure LanguageType enum exists and maps correctly from our Language enum
            try:
                lang_type_for_custom = LanguageType(
                    language_enum.value.lower()
                )  # Map our Language to CustomCipher's LanguageType
                custom_ciphers = self._custom_cipher_service.get_ciphers(
                    lang_type_for_custom
                )
                all_methods_for_combo.extend(cast(List[MethodType], custom_ciphers))
            except ValueError as e:
                logger.error(f"Could not get LanguageType for {language_enum}: {e}")

        # Populate the combo box
        for method_item in all_methods_for_combo:
            if isinstance(method_item, CalculationType):
                self._method_combo.addItem(
                    method_item.display_name, method_item
                )  # Use .display_name
            elif isinstance(method_item, CustomCipherConfig):
                self._method_combo.addItem(method_item.name, method_item)
            # else: unknown type, could log or ignore

        if all_methods_for_combo:
            self._method_combo.setCurrentIndex(0)
        else:
            # Optionally, add a placeholder if no methods are available
            self._method_combo.addItem("No methods available", None)

    def _on_language_changed(self, language_index_or_text: Union[int, str]) -> None:
        """Handle language selection change.

        Args:
            language_index_or_text: Index of the selected language or the language text
        """
        if isinstance(language_index_or_text, int):
            language = self._language_combo.itemText(language_index_or_text)
        else:
            language = language_index_or_text

        self._input_label.setText(f"Enter {language} text:")
        self._input_field.clear()
        self._populate_methods_for_selected_language()
        self._update_virtual_keyboard_button()

    def _on_method_changed(self, index: int) -> None:
        """Handle calculation method changes.

        Args:
            index: The selected index in the combo box
        """
        # This method can be expanded if needed

    def _calculate(self) -> None:
        """Handle calculate button click."""
        logger.debug("WordAbacusWidget._calculate called")

        input_text = self._input_field.text().strip()
        if not input_text:
            return

        # Get selected calculation type
        selected_index = self._method_combo.currentIndex()
        calc_type = self._method_combo.itemData(selected_index)
        transliterate = self._transliterate_chk.isChecked()

        # Perform calculation
        result_value = self._calculation_service.calculate(
            input_text, calc_type, transliterate_input=transliterate
        )
        print(f"Calculation result: {input_text} = {result_value}")

        # Update result display
        self._result_value.setText(str(result_value))

        # Enable the "Send to PolyCalc" button
        self._send_to_polycalc_button.setEnabled(True)

        # Create calculation result and add to history
        method_name = self._method_combo.currentText()
        if isinstance(calc_type, CustomCipherConfig):
            # For custom ciphers, we need to handle the history differently
            result = CalculationResult(
                input_text=input_text,
                calculation_type="CUSTOM_CIPHER",  # Use a string identifier instead of None
                result_value=result_value,
                custom_method_name=f"Custom: {method_name}",
            )
        else:
            # For standard calculation types
            result = CalculationResult(
                input_text=input_text,
                calculation_type=calc_type,
                result_value=result_value,
            )

        logger.debug(f"Created calculation result with ID: {result.id}")

        # Add to in-memory history service (for the history table in this widget)
        # This is the same history service instance that was passed from the panel
        self._history_service.add_calculation(result)

        # Update history table
        self._update_history_table()

        # Emit signal with calculation result
        # This will be caught by the WordAbacusPanel which will store the calculation
        # and re-emit the signal for the MainPanel to switch to the history tab
        self.calculation_performed.emit(result)

    def _update_history_table(self) -> None:
        """Update the history table with the latest calculations."""
        logger.debug("WordAbacusWidget._update_history_table called")

        history = self._history_service.get_history()
        logger.debug(f"Got {len(history)} items from history service")

        # Clear existing rows
        self._history_table.setRowCount(0)

        # Add new rows
        for i, calc in enumerate(history):
            self._history_table.insertRow(i)
            display_dict = calc.to_display_dict()
            logger.debug(
                f"Adding row {i} to history table: {calc.input_text} = {calc.result_value} (ID: {calc.id})"
            )

            for j, column in enumerate(["Input", "Method", "Result", "Time", "Notes"]):
                item = QTableWidgetItem(display_dict[column])
                self._history_table.setItem(i, j, item)

        # Resize columns to content
        self._history_table.resizeColumnsToContents()
        logger.debug(
            f"History table updated with {self._history_table.rowCount()} rows"
        )

    def clear_history(self) -> None:
        """Clear the calculation history."""
        self._history_service.clear_history()
        self._update_history_table()

    def reset_calculator(self) -> None:
        """Reset the calculator to its initial state."""
        self._input_field.clear()
        self._result_value.setText("0")
        self._transliterate_chk.setChecked(False)  # Reset transliterate checkbox

        # Reset to defaults based on current language
        language = self._language_combo.currentText()
        self._populate_methods_for_selected_language()
        self._method_combo.setCurrentIndex(0)

        self._calc_button.setEnabled(False)
        self._send_to_polycalc_button.setEnabled(False)

    def _send_to_polygon_calculator(self) -> None:
        """Send the current calculation result to the Regular Polygon Calculator."""
        # Get the current result value
        try:
            result_value = float(self._result_value.text())
        except ValueError:
            # If the result is not a valid number, do nothing
            return

        # Use the SendToPolygonDialog to let the user choose options
        from gematria.ui.dialogs.send_to_polygon_dialog import SendToPolygonDialog

        # Create and show the dialog
        dialog = SendToPolygonDialog(result_value, self)
        dialog.exec()

    def _open_custom_cipher_manager(self) -> None:
        """Open the custom cipher manager dialog."""
        # Create the dialog if it doesn't exist or is closed
        if (
            self._custom_cipher_dialog is None
            or not self._custom_cipher_dialog.isVisible()
        ):
            self._custom_cipher_dialog = CustomCipherDialog(self)

            # Connect the cipher updated signal to refresh our UI
            self._custom_cipher_dialog.cipher_updated.connect(
                self._on_custom_cipher_updated
            )

        # Show the dialog (non-modal)
        self._custom_cipher_dialog.show()
        self._custom_cipher_dialog.raise_()
        self._custom_cipher_dialog.activateWindow()

    def _on_custom_cipher_updated(self, cipher: CustomCipherConfig) -> None:
        """Handle updates to custom ciphers.

        Args:
            cipher: The updated custom cipher
        """
        # Refresh the method categories to include any new or updated ciphers
        self._populate_methods_for_selected_language()

    def _connect_signals(self) -> None:
        """Connect UI signals to handlers."""
        # Connect combo box and input field signals
        self._language_combo.currentTextChanged.connect(self._on_language_changed)
        self._method_combo.currentTextChanged.connect(self._on_method_changed)
        self._input_field.textChanged.connect(self._on_input_changed)

        # Connect buttons
        self._calc_button.clicked.connect(self._calculate)
        self._custom_cipher_button.clicked.connect(self._open_custom_cipher_manager)

    def _update_ui(self) -> None:
        """Update UI state based on current values."""
        # Populate methods based on selected (default) language
        self._populate_methods_for_selected_language()

        # Update input field validation based on selected language
        self._on_language_changed(self._language_combo.currentText())

        # Enable/disable calculation button based on input
        self._on_input_changed(self._input_field.text())

    def _update_virtual_keyboard_button(self) -> None:
        """Show or hide the virtual keyboard button based on selected language."""
        selected_language_text = self._language_combo.currentText()
        if selected_language_text in [
            Language.HEBREW.value,
            Language.GREEK.value,
            Language.COPTIC.value,
            Language.ARABIC.value,
        ]:
            self._vk_button.show()
        else:  # Hides for English, "All Methods", etc.
            self._vk_button.hide()
            if self._virtual_keyboard and self._virtual_keyboard.isVisible():
                self._virtual_keyboard.hide()

    def _show_virtual_keyboard(self) -> None:
        """Show the virtual keyboard for the selected language."""
        current_language = self._language_combo.currentText()
        if current_language in [
            Language.HEBREW.value,
            Language.GREEK.value,
            Language.COPTIC.value,
            Language.ARABIC.value,
        ]:
            if (
                self._virtual_keyboard is None
                or self._virtual_keyboard.language != current_language
            ):
                self._virtual_keyboard = VirtualKeyboardWidget(
                    language=current_language, parent=self
                )
                self._virtual_keyboard.key_pressed.connect(self._handle_virtual_key)

            # Position the keyboard near the input field or button
            button_pos = self._vk_button.mapToGlobal(
                self._vk_button.rect().bottomLeft()
            )
            self._virtual_keyboard.move(button_pos.x(), button_pos.y())
            self._virtual_keyboard.show()
        else:
            if self._virtual_keyboard is not None:
                self._virtual_keyboard.hide()

    def _handle_virtual_key(self, key: str) -> None:
        """Handle key press from the virtual keyboard."""
        if key == "<BACKSPACE>":
            cursor_pos = self._input_field.cursorPosition()
            text = self._input_field.text()
            if cursor_pos > 0:
                text = text[: cursor_pos - 1] + text[cursor_pos:]
                self._input_field.setText(text)
                self._input_field.setCursorPosition(cursor_pos - 1)
        elif key == "<CLEAR>":
            self._input_field.clear()
        else:
            cursor_pos = self._input_field.cursorPosition()
            text = self._input_field.text()
            text = text[:cursor_pos] + key + text[cursor_pos:]
            self._input_field.setText(text)
            self._input_field.setCursorPosition(cursor_pos + len(key))

    def _on_input_changed(self, text: str) -> None:
        """Handle input text changes."""
        # Enable/disable calculation button based on input
        self._calc_button.setEnabled(bool(text))
        self._send_to_polycalc_button.setEnabled(bool(text))
