"""Import Word List Dialog.

This module provides a dialog for importing word lists from CSV, ODS, or Excel spreadsheets.
Users can map columns to database fields and preview data before import.
"""

import os
from typing import Dict, Optional

import pandas as pd
from loguru import logger
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_type import (
    CalculationType,
    language_from_text,
)
from gematria.services.calculation_database_service import CalculationDatabaseService
from gematria.services.gematria_service import GematriaService


class ImportWordListDialog(QDialog):
    """Dialog for importing word lists from spreadsheets."""

    # Signal emitted when the import is complete
    import_complete = pyqtSignal(int)  # Number of words imported

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initialize services
        self._gematria_service = GematriaService()
        self._db_service = CalculationDatabaseService()

        # Initialize data containers
        self._dataframe: Optional[pd.DataFrame] = None
        self._column_mapping: Dict[str, str] = {}
        self._header_row: int = 0
        self._file_path: str = ""
        self._file_type: str = ""
        self._selected_sheet: str = ""
        self._preview_rows: int = 10

        # Initialize UI
        self._setup_ui()

        # Set dialog properties
        self.setWindowTitle("Import Word/Phrase List")
        self.setMinimumSize(800, 600)
        self.setModal(True)

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout()

        # File Selection Section
        file_group = QGroupBox("File Selection")
        file_layout = QGridLayout()

        self._file_path_label = QLabel("No file selected")
        select_file_button = QPushButton("Select File")
        select_file_button.clicked.connect(self._select_file)

        file_layout.addWidget(QLabel("File:"), 0, 0)
        file_layout.addWidget(self._file_path_label, 0, 1)
        file_layout.addWidget(select_file_button, 0, 2)

        # Header row selection
        self._header_spin = QSpinBox()
        self._header_spin.setMinimum(1)
        self._header_spin.setMaximum(10)
        self._header_spin.setValue(1)
        self._header_spin.valueChanged.connect(self._update_preview)

        file_layout.addWidget(QLabel("Header Row (1 = first row):"), 1, 0)
        file_layout.addWidget(self._header_spin, 1, 1)

        # Sheet selection for Excel files
        self._sheet_combo = QComboBox()
        self._sheet_combo.setEnabled(False)
        self._sheet_combo.currentTextChanged.connect(self._change_sheet)

        file_layout.addWidget(QLabel("Sheet:"), 2, 0)
        file_layout.addWidget(self._sheet_combo, 2, 1)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Column Mapping Section
        mapping_group = QGroupBox("Column Mapping")
        mapping_layout = QGridLayout()

        # Word/Phrase column selection
        self._word_column_combo = QComboBox()
        self._word_column_combo.currentTextChanged.connect(
            lambda text: self._update_column_mapping("word", text)
        )

        # Notes column selection
        self._notes_column_combo = QComboBox()
        self._notes_column_combo.currentTextChanged.connect(
            lambda text: self._update_column_mapping("notes", text)
        )

        # Tags column selection
        self._tags_column_combo = QComboBox()
        self._tags_column_combo.currentTextChanged.connect(
            lambda text: self._update_column_mapping("tags", text)
        )

        mapping_layout.addWidget(QLabel("Word/Phrase Column:"), 0, 0)
        mapping_layout.addWidget(self._word_column_combo, 0, 1)

        mapping_layout.addWidget(QLabel("Notes Column:"), 1, 0)
        mapping_layout.addWidget(self._notes_column_combo, 1, 1)

        mapping_layout.addWidget(QLabel("Tags Column:"), 2, 0)
        mapping_layout.addWidget(self._tags_column_combo, 2, 1)

        # Checkbox to enable auto-detection of language
        self._detect_language_checkbox = QCheckBox("Auto-detect language for each word")
        self._detect_language_checkbox.setChecked(True)
        mapping_layout.addWidget(self._detect_language_checkbox, 3, 0, 1, 2)

        # Calculate with all methods checkbox
        self._calc_all_methods_checkbox = QCheckBox(
            "Calculate using all available methods"
        )
        self._calc_all_methods_checkbox.setChecked(True)
        mapping_layout.addWidget(self._calc_all_methods_checkbox, 4, 0, 1, 2)

        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)

        # Preview Section
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout()

        self._preview_table = QTableWidget()
        self._preview_table.setAlternatingRowColors(True)
        preview_layout.addWidget(self._preview_table)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Import Progress
        self._progress_bar = QProgressBar()
        self._progress_bar.setVisible(False)
        layout.addWidget(self._progress_bar)

        # Buttons
        button_layout = QHBoxLayout()

        self._import_button = QPushButton("Import")
        self._import_button.setEnabled(False)
        self._import_button.clicked.connect(self._import_data)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self._import_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _select_file(self) -> None:
        """Open a file dialog to select a spreadsheet file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Spreadsheet File",
            "",
            "Spreadsheet Files (*.csv *.xlsx *.xls *.ods);;All Files (*)",
        )

        if not file_path:
            return

        self._file_path = file_path
        self._file_path_label.setText(os.path.basename(file_path))

        # Determine file type
        _, ext = os.path.splitext(file_path.lower())
        self._file_type = ext

        # If Excel file, populate sheet names
        if ext in [".xlsx", ".xls"]:
            self._load_excel_sheets()
        else:
            # For CSV and ODS, just load the data
            self._sheet_combo.setEnabled(False)
            self._sheet_combo.clear()
            self._load_data()

    def _load_excel_sheets(self) -> None:
        """Load sheet names from an Excel file."""
        try:
            # Load Excel file
            xl = pd.ExcelFile(self._file_path)

            # Update sheet combo box
            self._sheet_combo.clear()
            # Ensure all sheet names are strings
            sheet_names = [str(name) for name in xl.sheet_names]
            self._sheet_combo.addItems(sheet_names)
            self._sheet_combo.setEnabled(True)

            # Select first sheet
            if sheet_names:
                self._selected_sheet = str(sheet_names[0])
                self._load_data()

        except Exception as e:
            logger.error(f"Error loading Excel sheets: {e}")
            QMessageBox.critical(
                self, "Error Loading File", f"Could not load Excel sheets: {str(e)}"
            )

    def _change_sheet(self, sheet_name: str) -> None:
        """Change the selected Excel sheet.

        Args:
            sheet_name: Name of the sheet to load
        """
        if sheet_name:
            self._selected_sheet = sheet_name
            self._load_data()

    def _load_data(self) -> None:
        """Load data from the selected file."""
        try:
            # Read data based on file type
            if self._file_type == ".csv":
                # For pandas, header=0 means use the first row as header
                header_param = (
                    self._header_spin.value() - 1
                )  # Convert from 1-indexed UI to 0-indexed pandas
                self._dataframe = pd.read_csv(self._file_path, header=header_param)
            elif self._file_type in [".xlsx", ".xls"]:
                header_param = self._header_spin.value() - 1
                self._dataframe = pd.read_excel(
                    self._file_path,
                    sheet_name=self._selected_sheet,
                    header=header_param,
                )
            elif self._file_type == ".ods":
                header_param = self._header_spin.value() - 1
                self._dataframe = pd.read_excel(
                    self._file_path, engine="odf", header=header_param
                )
            else:
                raise ValueError(f"Unsupported file type: {self._file_type}")

            # Update column mappings
            self._update_column_combos()

            # Update preview
            self._update_preview()

            # Enable import button
            self._import_button.setEnabled(True)

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            QMessageBox.critical(
                self, "Error Loading File", f"Could not load data: {str(e)}"
            )

    def _update_column_combos(self) -> None:
        """Update column mapping combo boxes with available columns."""
        if self._dataframe is None:
            return

        # Get column names
        columns = list(self._dataframe.columns)

        # Clear and update combo boxes
        self._word_column_combo.clear()
        self._notes_column_combo.clear()
        self._tags_column_combo.clear()

        self._word_column_combo.addItems([str(col) for col in columns])
        self._notes_column_combo.addItems([""] + [str(col) for col in columns])
        self._tags_column_combo.addItems([""] + [str(col) for col in columns])

        # Try to auto-select columns based on names
        for col in columns:
            col_lower = col.lower()
            if any(term in col_lower for term in ["word", "phrase", "text"]):
                self._word_column_combo.setCurrentText(col)
            elif any(term in col_lower for term in ["note", "description", "comment"]):
                self._notes_column_combo.setCurrentText(col)
            elif any(term in col_lower for term in ["tag", "category", "label"]):
                self._tags_column_combo.setCurrentText(col)

        # Set initial column mappings
        word_column = self._word_column_combo.currentText()
        notes_column = self._notes_column_combo.currentText()
        tags_column = self._tags_column_combo.currentText()

        self._update_column_mapping("word", word_column)
        self._update_column_mapping("notes", notes_column)
        self._update_column_mapping("tags", tags_column)

    def _update_column_mapping(self, field: str, column: str) -> None:
        """Update the mapping between database fields and spreadsheet columns.

        Args:
            field: Database field name
            column: Spreadsheet column name
        """
        if column:
            self._column_mapping[field] = column
        elif field in self._column_mapping:
            del self._column_mapping[field]

    def _update_preview(self) -> None:
        """Update the preview table with data from the file."""
        if self._dataframe is None or not self._file_path:
            return

        # Get updated header row parameter (0-indexed for pandas)
        header_param = self._header_spin.value() - 1

        try:
            # Reload data with the new header row
            if self._file_type == ".csv":
                self._dataframe = pd.read_csv(self._file_path, header=header_param)
            elif self._file_type in [".xlsx", ".xls"]:
                self._dataframe = pd.read_excel(
                    self._file_path,
                    sheet_name=self._selected_sheet,
                    header=header_param,
                )
            elif self._file_type == ".ods":
                self._dataframe = pd.read_excel(
                    self._file_path, engine="odf", header=header_param
                )

            # Update column mappings after reloading
            self._update_column_combos()
        except Exception as e:
            logger.error(f"Error updating header row: {e}")
            return

        # Get data for preview
        preview_df = self._dataframe.head(self._preview_rows)

        # Update table
        self._preview_table.setRowCount(len(preview_df))
        self._preview_table.setColumnCount(len(preview_df.columns))

        # Set headers
        self._preview_table.setHorizontalHeaderLabels(list(preview_df.columns))

        # Populate data
        for row_idx, (_, row) in enumerate(preview_df.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self._preview_table.setItem(row_idx, col_idx, item)

        # Resize columns to content
        self._preview_table.resizeColumnsToContents()

    def _import_data(self) -> None:
        """Import the data from the spreadsheet into the database."""
        if self._dataframe is None or "word" not in self._column_mapping:
            QMessageBox.warning(
                self,
                "Invalid Configuration",
                "Please select a column for Word/Phrase field.",
            )
            return

        word_column = self._column_mapping["word"]
        notes_column = self._column_mapping.get("notes", "")
        tags_column = self._column_mapping.get("tags", "")

        auto_detect = self._detect_language_checkbox.isChecked()
        calc_all_methods = self._calc_all_methods_checkbox.isChecked()

        # Create progress tracking
        self._progress_bar.setVisible(True)
        self._progress_bar.setMinimum(0)
        total_rows = len(self._dataframe)
        self._progress_bar.setMaximum(total_rows)
        self._progress_bar.setValue(0)

        # Disable import button
        self._import_button.setEnabled(False)

        # Import each word
        import_count = 0
        for i, (_, row) in enumerate(self._dataframe.iterrows()):
            # Update progress - use counter index which is guaranteed to be int
            self._progress_bar.setValue(i + 1)

            # Get word/phrase
            word = str(row[word_column])
            if not word or word.lower() == "nan":
                continue

            # Get notes and tags if available
            notes = ""
            if notes_column and notes_column in row:
                notes = str(row[notes_column])
                if notes.lower() == "nan":
                    notes = ""

            tags = []
            if tags_column and tags_column in row:
                tags_str = str(row[tags_column])
                if tags_str and tags_str.lower() != "nan":
                    # Split tags by comma or semicolon
                    tags = [t.strip() for t in tags_str.replace(";", ",").split(",")]
                    tags = [t for t in tags if t]  # Filter out empty tags

            # Auto-detect language if enabled
            language = None
            if auto_detect:
                language = language_from_text(word)

            if language:
                # Get all calculation methods for the detected language
                if calc_all_methods:
                    # Get all calculation types for the language
                    calc_types = CalculationType.get_types_for_language(language)

                    # Calculate and save for each type
                    for calc_type in calc_types:
                        self._gematria_service.calculate_and_save(
                            text=word,
                            calculation_type=calc_type,
                            notes=notes,
                            tags=tags,
                        )
                        import_count += 1
                else:
                    # Use default method for the language
                    default_type = CalculationType.get_default_for_language(language)
                    if default_type:
                        self._gematria_service.calculate_and_save(
                            text=word,
                            calculation_type=default_type,
                            notes=notes,
                            tags=tags,
                        )
                        import_count += 1

        # Show completion message
        QMessageBox.information(
            self,
            "Import Complete",
            f"Successfully imported {import_count} word calculations.",
        )

        # Emit completion signal
        self.import_complete.emit(import_count)

        # Close dialog
        self.accept()
