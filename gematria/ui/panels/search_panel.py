"""Gematria Search panel.

This module provides a panel implementation for searching the Gematria database
for calculations based on various criteria.
"""

from typing import Any, Dict, List, Optional, cast

from loguru import logger
from PyQt6.QtCore import QRegularExpression, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_result import CalculationResult
from gematria.models.calculation_type import CalculationType, Language
from gematria.models.custom_cipher_config import CustomCipherConfig
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.custom_cipher_service import CustomCipherService
from gematria.ui.widgets.calculation_detail_widget import CalculationDetailWidget
from shared.ui.window_management import WindowManager


class SearchPanel(QWidget):
    """Panel for searching the Gematria database."""

    # Signal emitted when a search result is selected
    result_selected = pyqtSignal(CalculationResult)

    def __init__(
        self,
        calculation_db_service: CalculationDatabaseService,
        custom_cipher_service: CustomCipherService,
        window_manager: Optional[WindowManager] = None,
        parent: Optional[QWidget] = None,
    ):
        """Initialize the search panel.

        Args:
            calculation_db_service: Service for database operations
            custom_cipher_service: Service for custom cipher operations
            window_manager: Window manager for opening additional windows
            parent: Parent widget
        """
        super().__init__(parent)
        self.calculation_db_service = calculation_db_service
        self.custom_cipher_service = custom_cipher_service
        self.selected_calculation: Optional[CalculationResult] = None

        # Store window manager
        self.window_manager = window_manager

        # If no window manager is provided, try to find it in the parent chain
        if self.window_manager is None:
            self.window_manager = self._find_window_manager()

        self._setup_ui()

    def _find_window_manager(self) -> Optional[WindowManager]:
        """Find the window manager by traversing the parent widget hierarchy.

        Returns:
            The window manager if found, None otherwise
        """
        # Start with the current parent
        current = self.parent()

        # Walk up the parent chain until we find a window manager or run out of parents
        while current is not None:
            # Check if parent has window_manager attribute
            if hasattr(current, "window_manager"):
                manager = getattr(current, "window_manager")
                if isinstance(manager, WindowManager):
                    return manager

            # Check children of current widget
            for child in current.children():
                if isinstance(child, WindowManager):
                    return child

            # Move up to parent
            current = current.parent()

        # If we get here, no window manager was found
        logger.warning("No window manager found in parent widget chain")
        return None

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Gematria Search")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Search criteria area
        criteria_layout = QHBoxLayout()

        # Left side - text and value search
        left_group = QGroupBox("Search Criteria")
        left_layout = QFormLayout()

        # Text search
        self.text_search = QLineEdit()
        self.text_search.setPlaceholderText("Enter text to search...")
        left_layout.addRow("Text:", self.text_search)

        self.exact_text_match = QCheckBox("Exact match")
        left_layout.addRow("", self.exact_text_match)

        # Value search
        value_layout = QHBoxLayout()
        self.value_min = QSpinBox()
        self.value_min.setRange(0, 999999)
        self.value_min.setSpecialValueText("Min")

        self.value_max = QSpinBox()
        self.value_max.setRange(0, 999999)
        self.value_max.setSpecialValueText("Max")

        value_layout.addWidget(self.value_min)
        value_layout.addWidget(QLabel("-"))
        value_layout.addWidget(self.value_max)

        left_layout.addRow("Value range:", value_layout)

        # Exact value - Changed from QSpinBox to QLineEdit with numeric validation
        self.exact_value = QLineEdit()
        self.exact_value.setPlaceholderText("Enter exact value...")
        # Only allow numbers with a validator
        validator = QRegularExpressionValidator(QRegularExpression("^[0-9]*$"))
        self.exact_value.setValidator(validator)
        left_layout.addRow("Exact value:", self.exact_value)

        left_group.setLayout(left_layout)
        criteria_layout.addWidget(left_group)

        # Right side - method filter
        right_group = QGroupBox("Additional Filters")
        right_layout = QFormLayout()

        # Language/Method filter
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Any Language", "Hebrew", "Greek", "English"])
        self.language_combo.currentIndexChanged.connect(self._update_method_combo)
        right_layout.addRow("Language:", self.language_combo)

        self.method_combo = QComboBox()
        self.method_combo.addItem("Any Method")
        right_layout.addRow("Method:", self.method_combo)

        # Other filters
        self.favorites_only = QCheckBox("Favorites only")
        right_layout.addRow("", self.favorites_only)

        self.has_tags = QCheckBox("Has tags")
        right_layout.addRow("", self.has_tags)

        self.has_notes = QCheckBox("Has notes")
        right_layout.addRow("", self.has_notes)

        right_group.setLayout(right_layout)
        criteria_layout.addWidget(right_group)

        layout.addLayout(criteria_layout)

        # Buttons row
        button_layout = QHBoxLayout()

        self.search_button = QPushButton("Search")
        self.search_button.setIcon(QIcon.fromTheme("search"))
        self.search_button.clicked.connect(self._perform_search)

        self.clear_button = QPushButton("Clear")
        self.clear_button.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_button.clicked.connect(self._clear_search)

        button_layout.addStretch()
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.clear_button)

        layout.addLayout(button_layout)

        # Results table
        self.results_table = QTableWidget(0, 5)
        self.results_table.setHorizontalHeaderLabels(
            ["Text", "Value", "Method", "Date", "★"]
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.results_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.results_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results_table.itemSelectionChanged.connect(self._on_result_selected)
        # Connect double-click to view details in a separate window
        self.results_table.itemDoubleClicked.connect(self._open_detail_window)

        layout.addWidget(self.results_table)

        # Initialize method combo
        self._update_method_combo()

    def _update_method_combo(self) -> None:
        """Update the method combo box based on the selected language."""
        self.method_combo.clear()
        self.method_combo.addItem("Any Method")

        language_idx = self.language_combo.currentIndex()

        # Get calculation types for selected language
        if language_idx == 0:  # Any Language
            methods = CalculationType.get_all_types()
        elif language_idx == 1:  # Hebrew
            methods = CalculationType.get_types_for_language(Language.HEBREW)
        elif language_idx == 2:  # Greek
            methods = CalculationType.get_types_for_language(Language.GREEK)
        elif language_idx == 3:  # English
            methods = CalculationType.get_types_for_language(Language.ENGLISH)
        else:
            methods = []

        # Add standard methods to combo
        for method in methods:
            self.method_combo.addItem(method.display_name, method)

        # Add separator and custom methods if applicable
        if language_idx > 0:
            language = [Language.HEBREW, Language.GREEK, Language.ENGLISH][
                language_idx - 1
            ]
            custom_methods = self.custom_cipher_service.get_methods_for_language(
                language
            )

            if custom_methods:
                self.method_combo.insertSeparator(self.method_combo.count())
                for custom_method in custom_methods:
                    custom_method_obj: CustomCipherConfig = custom_method
                    # Store the custom method name as a string, not as a CalculationType
                    self.method_combo.addItem(
                        f"Custom: {custom_method_obj.name}", custom_method_obj.name
                    )

    def _perform_search(self) -> None:
        """Perform search based on current criteria."""
        criteria: Dict[str, Any] = {}

        # Text criteria
        if self.text_search.text():
            if self.exact_text_match.isChecked():
                criteria["input_text"] = self.text_search.text()
            else:
                criteria["input_text_like"] = f"%{self.text_search.text()}%"

        # Value criteria - Updated to handle the QLineEdit instead of QSpinBox
        exact_value_text = self.exact_value.text().strip()
        if exact_value_text:
            try:
                criteria["result_value"] = int(exact_value_text)
            except ValueError:
                # If text is not a valid integer, ignore it
                pass
        else:
            if self.value_min.value() > 0:
                criteria["result_value_min"] = self.value_min.value()
            if self.value_max.value() > 0:
                criteria["result_value_max"] = self.value_max.value()

        # Language/Method filter
        language_idx = self.language_combo.currentIndex()
        if language_idx > 0:
            language = [Language.HEBREW, Language.GREEK, Language.ENGLISH][
                language_idx - 1
            ]
            criteria["language"] = language

        method_idx = self.method_combo.currentIndex()
        if method_idx > 0:
            method_data = self.method_combo.currentData()
            if isinstance(method_data, CalculationType):
                criteria["calculation_type"] = method_data
            elif isinstance(method_data, str):
                criteria["custom_method_name"] = method_data

        # Other filters
        if self.favorites_only.isChecked():
            criteria["favorite"] = True

        if self.has_tags.isChecked():
            criteria["has_tags"] = True

        if self.has_notes.isChecked():
            criteria["has_notes"] = True

        # Perform search
        results = self.calculation_db_service.search_calculations(criteria)
        self._display_results(results)

    def _clear_search(self) -> None:
        """Clear all search fields."""
        self.text_search.clear()
        self.exact_text_match.setChecked(False)
        self.value_min.setValue(0)
        self.value_max.setValue(0)
        self.exact_value.clear()  # Changed from setValue(0) to clear()
        self.language_combo.setCurrentIndex(0)
        self.method_combo.setCurrentIndex(0)
        self.favorites_only.setChecked(False)
        self.has_tags.setChecked(False)
        self.has_notes.setChecked(False)

        # Clear results
        self.results_table.setRowCount(0)
        self.selected_calculation = None

    def _display_results(self, results: List[CalculationResult]) -> None:
        """Display search results in the table.

        Args:
            results: List of calculation results to display
        """
        self.results_table.setRowCount(0)
        self.selected_calculation = None

        if not results:
            return

        self.results_table.setRowCount(len(results))

        for i, result in enumerate(results):
            # Text column
            text_item = QTableWidgetItem(result.input_text)
            text_item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_table.setItem(i, 0, text_item)

            # Value column
            value_item = QTableWidgetItem(str(result.result_value))
            self.results_table.setItem(i, 1, value_item)

            # Method column
            method_name = self._get_method_name(result)
            method_item = QTableWidgetItem(method_name)
            self.results_table.setItem(i, 2, method_item)

            # Date column
            date_str = (
                result.created_at.strftime("%Y-%m-%d %H:%M")
                if result.created_at
                else ""
            )
            date_item = QTableWidgetItem(date_str)
            self.results_table.setItem(i, 3, date_item)

            # Favorite column
            favorite_item = QTableWidgetItem("★" if result.favorite else "")
            favorite_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_table.setItem(i, 4, favorite_item)

    def _get_method_name(self, calculation: CalculationResult) -> str:
        """Get the display name for a calculation method.

        Args:
            calculation: The calculation result

        Returns:
            Display name for the calculation method
        """
        if calculation.custom_method_name:
            return f"Custom: {calculation.custom_method_name}"

        if isinstance(calculation.calculation_type, CalculationType):
            return calculation.calculation_type.display_name

        if isinstance(calculation.calculation_type, str):
            # Try to find a matching CalculationType
            for calc_type in CalculationType.get_all_types():
                if calc_type.name == calculation.calculation_type:
                    return calc_type.display_name

        # Fallback
        return str(calculation.calculation_type)

    def _on_result_selected(self) -> None:
        """Handle selection change in the results table."""
        selected_items = self.results_table.selectedItems()
        if not selected_items:
            self.selected_calculation = None
            return

        # Get the calculation result from the first column
        row = selected_items[0].row()
        self.selected_calculation = cast(
            CalculationResult,
            self.results_table.item(row, 0).data(Qt.ItemDataRole.UserRole),
        )

        # Emit signal that result was selected
        self.result_selected.emit(self.selected_calculation)

    def _open_detail_window(self, item: QTableWidgetItem) -> None:
        """Open calculation details in a separate window.

        Args:
            item: The table item that was double-clicked
        """
        if not self.selected_calculation or not self.window_manager:
            return

        # Create detail widget
        detail_widget = CalculationDetailWidget(
            self.calculation_db_service, self.custom_cipher_service
        )
        detail_widget.set_calculation(self.selected_calculation)

        # Generate a unique window ID based on the calculation
        window_id = f"calculation_detail_{self.selected_calculation.id}"
        window_title = f"Calculation Details - {self.selected_calculation.input_text}"

        # Open the detail widget in a new window
        self.window_manager.open_window(window_id, detail_widget, window_title)
