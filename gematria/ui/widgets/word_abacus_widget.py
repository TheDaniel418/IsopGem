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

from typing import Dict, List, Optional, Union, cast

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
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
from gematria.models.calculation_type import CalculationType
from gematria.models.custom_cipher_config import CustomCipherConfig, LanguageType
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.services.gematria_service import GematriaService
from gematria.services.history_service import HistoryService
from gematria.ui.dialogs.custom_cipher_dialog import CustomCipherDialog

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
        self._language_combo.addItems(["Hebrew", "Greek", "English"])
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)
        input_layout.addWidget(QLabel("Language:"), 0, 0)
        input_layout.addWidget(self._language_combo, 0, 1)

        # Input text field
        self._input_label = QLabel("Enter Hebrew text:")
        self._input_field = QLineEdit()
        self._input_field.setPlaceholderText("Type text here...")
        self._input_field.textChanged.connect(self._on_input_changed)
        input_layout.addWidget(self._input_label, 1, 0)
        input_layout.addWidget(self._input_field, 1, 1)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Create a group box for calculation methods
        method_group = QGroupBox("Calculation Method")
        method_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        method_layout = QGridLayout()

        # Type selection (categories)
        method_layout.addWidget(QLabel("Type:"), 0, 0)
        self._type_combo = QComboBox()
        method_layout.addWidget(self._type_combo, 0, 1)

        # Method selection (specific calculations)
        method_layout.addWidget(QLabel("Method:"), 1, 0)
        self._method_combo = QComboBox()
        method_layout.addWidget(self._method_combo, 1, 1)

        # Custom cipher button
        self._custom_cipher_button = QPushButton("Manage Custom Ciphers")
        self._custom_cipher_button.clicked.connect(self._open_custom_cipher_manager)
        method_layout.addWidget(self._custom_cipher_button, 2, 0, 1, 2)

        # Connect signals
        self._type_combo.currentIndexChanged.connect(self._on_type_changed)
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
        self._populate_method_categories()
        self._language_combo.setCurrentIndex(0)  # Default to Hebrew

    def _populate_method_categories(self) -> None:
        """Populate the calculation type categories based on the selected language."""
        language = self._language_combo.currentText()
        self._type_combo.clear()

        if language == "Hebrew":
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
                    CalculationType.MISPAR_HAAKHOR,
                    CalculationType.MISPAR_HAMERUBAH_HAKLALI,
                    CalculationType.MISPAR_HAPANIM,
                ],
                "Substitution Ciphers": [
                    CalculationType.MISPAR_MESHUPACH,
                    CalculationType.ALBAM,
                    CalculationType.ATBASH,
                ],
            }

            # Add custom ciphers category if available
            hebrew_custom_ciphers = self._custom_cipher_service.get_ciphers(
                LanguageType.HEBREW
            )
            if hebrew_custom_ciphers:
                hebrew_categories["Custom Methods"] = cast(
                    List[MethodType], hebrew_custom_ciphers
                )

            # Store the categories and their methods
            self._method_categories = hebrew_categories

            # Add the categories to the combobox
            for category in hebrew_categories.keys():
                self._type_combo.addItem(category)

            # Set default category to Standard Methods
            self._type_combo.setCurrentIndex(0)

        elif language == "Greek":
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
            greek_custom_ciphers = self._custom_cipher_service.get_ciphers(
                LanguageType.GREEK
            )
            if greek_custom_ciphers:
                greek_categories["Custom Methods"] = cast(
                    List[MethodType], greek_custom_ciphers
                )

            # Store the categories and their methods
            self._method_categories = greek_categories

            # Add the categories to the combobox
            for category in greek_categories.keys():
                self._type_combo.addItem(category)

            # Set default category to Standard Methods
            self._type_combo.setCurrentIndex(0)

        elif language == "English":
            english_categories: Dict[str, List[MethodType]] = {
                "TQ Methods": [CalculationType.TQ_ENGLISH]
            }

            # Add custom ciphers category if available
            english_custom_ciphers = self._custom_cipher_service.get_ciphers(
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
                self._type_combo.addItem(category)

            # Set default category (only one for English)
            self._type_combo.setCurrentIndex(0)

    def _populate_methods(self) -> None:
        """Populate the methods combobox based on selected category."""
        self._method_combo.clear()

        category = self._type_combo.currentText()
        if not category or category not in self._method_categories:
            return

        methods = self._method_categories[category]

        # Add methods to combo box
        for method in methods:
            if isinstance(method, CalculationType):
                # Handle enum-based calculation types
                display_name = method.name.replace("_", " ").title()
                self._method_combo.addItem(display_name, method)
            elif isinstance(method, CustomCipherConfig):
                # Handle custom cipher configs
                display_name = method.name
                self._method_combo.addItem(display_name, method)

        # Set the first method as default
        if methods:
            self._method_combo.setCurrentIndex(0)

    def _on_language_changed(self, language_index_or_text: Union[int, str]) -> None:
        """Handle language selection change.

        Args:
            language_index_or_text: Index of the selected language or the language text
        """
        # Get the language text if an index was provided
        if isinstance(language_index_or_text, int):
            language = self._language_combo.itemText(language_index_or_text)
        else:
            language = language_index_or_text

        # Update the input label based on the language
        self._input_label.setText(f"Enter {language} text:")

        # Clear the input field
        self._input_field.clear()

        # Populate the method categories for the selected language
        self._populate_method_categories()

    def _on_type_changed(self, index: int) -> None:
        """Handle method type selection changes.

        Args:
            index: The selected index in the combo box
        """
        self._populate_methods()

    def _on_input_changed(self, text: str) -> None:
        """Handle text input changes.

        Args:
            text: The new text value
        """
        # Enable calculate button if text is not empty
        self._calc_button.setEnabled(bool(text.strip()))

    def _on_method_changed(self, index: int) -> None:
        """Handle calculation method changes.

        Args:
            index: The selected index in the combo box
        """
        # This method can be expanded if needed

    def _calculate(self) -> None:
        """Handle calculate button click."""
        from loguru import logger

        logger.debug("WordAbacusWidget._calculate called")

        input_text = self._input_field.text().strip()
        if not input_text:
            return

        # Get selected calculation type
        selected_index = self._method_combo.currentIndex()
        calc_type = self._method_combo.itemData(selected_index)

        # Perform calculation
        result_value = self._calculation_service.calculate(input_text, calc_type)
        print(f"Calculation result: {input_text} = {result_value}")

        # Update result display
        self._result_value.setText(str(result_value))

        # Enable the "Send to PolyCalc" button
        self._send_to_polycalc_button.setEnabled(True)

        # Create calculation result and add to history
        from loguru import logger

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
        from loguru import logger

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

        # Reset to defaults based on current language
        language = self._language_combo.currentText()
        self._populate_method_categories()
        self._type_combo.setCurrentIndex(0)

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
        self._populate_method_categories()

    def _connect_signals(self) -> None:
        """Connect UI signals to handlers."""
        # Connect combo box and input field signals
        self._language_combo.currentTextChanged.connect(self._on_language_changed)
        self._type_combo.currentTextChanged.connect(self._on_type_changed)
        self._method_combo.currentTextChanged.connect(self._on_method_changed)
        self._input_field.textChanged.connect(self._on_input_changed)

        # Connect buttons
        self._calc_button.clicked.connect(self._calculate)
        self._custom_cipher_button.clicked.connect(self._open_custom_cipher_manager)

    def _update_ui(self) -> None:
        """Update UI state based on current values."""
        # Populate method categories based on selected language
        self._populate_method_categories()

        # Update input field validation based on selected language
        self._on_language_changed(self._language_combo.currentText())

        # Enable/disable calculation button based on input
        self._on_input_changed(self._input_field.text())
