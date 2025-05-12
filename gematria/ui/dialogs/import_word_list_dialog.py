"""
Purpose: Provides a dialog for importing word/phrase lists into the Word List Abacus.

This file is part of the gematria pillar and serves as a UI component.
It provides a dialog interface for users to import lists of words and phrases
from various sources like text files or clipboard.

Key components:
- ImportWordListDialog: Dialog for importing word lists

Dependencies:
- PyQt6: For UI components
"""

import csv
import os
from typing import Dict, List, Optional, Union

from loguru import logger
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Import Language enum
from gematria.models.calculation_type import Language

# Imports for ODS handling
try:
    from odf import table as odf_table
    from odf import teletype as odf_teletype
    from odf import text as odf_text
    from odf.opendocument import load as odf_load

    ODFPY_AVAILABLE = True
except ImportError:
    ODFPY_AVAILABLE = False
    logger.warning("odfpy library not found. ODS file import will be disabled.")


class ImportWordListDialog(QDialog):
    """Dialog for importing word lists into the Word List Abacus."""

    # Signal emitted when import is complete with list of words, language, and count
    # Updated to emit a list of dictionaries: [{'word': str, 'notes': Optional[str], 'tags': Optional[List[str]]}, ...]
    import_complete = pyqtSignal(list, Language, int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Import Word/Phrase List")
        self.setMinimumSize(600, 500)
        self._word_list = []
        self._selected_language: Language = Language.HEBREW  # Default language

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Source selection group
        source_label = QLabel("Select Import Source:")
        source_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(source_label)

        # Source radio buttons
        source_group = QWidget()
        source_layout = QHBoxLayout(source_group)
        source_layout.setContentsMargins(0, 0, 0, 0)

        self._file_radio = QRadioButton("From File")
        self._clipboard_radio = QRadioButton("From Clipboard")
        self._manual_radio = QRadioButton("Manual Entry")

        # Default selection
        self._file_radio.setChecked(True)

        # Connect signals
        self._file_radio.toggled.connect(self._update_source_ui)
        self._clipboard_radio.toggled.connect(self._update_source_ui)
        self._manual_radio.toggled.connect(self._update_source_ui)

        source_layout.addWidget(self._file_radio)
        source_layout.addWidget(self._clipboard_radio)
        source_layout.addWidget(self._manual_radio)
        source_layout.addStretch()

        layout.addWidget(source_group)

        # File import controls
        self._file_group = QWidget()
        file_layout = QHBoxLayout(self._file_group)
        file_layout.setContentsMargins(0, 0, 0, 0)

        self._file_path_label = QLabel("No file selected")
        file_layout.addWidget(self._file_path_label)

        self._browse_button = QPushButton("Browse...")
        self._browse_button.clicked.connect(self._browse_for_file)
        file_layout.addWidget(self._browse_button)

        layout.addWidget(self._file_group)

        # Language selection
        language_selection_label = QLabel("Language of Words:")
        language_selection_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(language_selection_label)

        self._language_combo = QComboBox()
        for lang in Language:
            if (
                lang != Language.UNKNOWN
            ):  # Don't include UNKNOWN as a selectable import language
                self._language_combo.addItem(lang.value, lang)
        self._language_combo.setCurrentText(
            self._selected_language.value
        )  # Set default
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)
        layout.addWidget(self._language_combo)

        # Format options
        format_label = QLabel("Format Options:")
        format_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(format_label)

        format_group = QWidget()
        format_layout = QHBoxLayout(format_group)
        format_layout.setContentsMargins(0, 0, 0, 0)

        self._delimiter_label = QLabel("Delimiter:")
        format_layout.addWidget(self._delimiter_label)

        self._delimiter_combo = QComboBox()
        self._delimiter_combo.addItems(
            ["Line Break", "Comma", "Tab", "Space", "Semicolon"]
        )
        format_layout.addWidget(self._delimiter_combo)

        format_layout.addStretch()

        self._has_header_check = QCheckBox("First row is header")
        format_layout.addWidget(self._has_header_check)

        layout.addWidget(format_group)

        # Preview/edit area
        preview_label = QLabel("Preview/Edit:")
        preview_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(preview_label)

        self._preview_text = QTextEdit()
        self._preview_text.setPlaceholderText(
            "Words/phrases will appear here for preview or editing.\n"
            "Each line will be treated as a separate word or phrase if 'Line Break' is delimiter.\n"
            "Otherwise, the selected delimiter will be used from loaded content."
        )
        layout.addWidget(self._preview_text)

        # Action buttons
        button_group = QWidget()
        button_layout = QHBoxLayout(button_group)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self._load_button = QPushButton("Load")
        self._load_button.clicked.connect(self._load_from_source)
        button_layout.addWidget(self._load_button)

        button_layout.addStretch()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # Import button
        self._import_button = QPushButton("Import")
        self._import_button.setEnabled(False)
        self._import_button.clicked.connect(self._import_word_list)
        self._import_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            """
        )
        button_layout.addWidget(self._import_button)

        layout.addWidget(button_group)

        # Initial UI update
        self._update_source_ui()

    def _update_source_ui(self) -> None:
        """Update UI based on selected source."""
        # File controls visibility
        self._file_group.setVisible(self._file_radio.isChecked())

        # Delimiter options relevance
        format_controls_enabled = (
            self._file_radio.isChecked() or self._clipboard_radio.isChecked()
        )
        self._delimiter_label.setEnabled(format_controls_enabled)
        self._delimiter_combo.setEnabled(format_controls_enabled)
        self._has_header_check.setEnabled(format_controls_enabled)

        # Edit capability based on source
        self._preview_text.setReadOnly(not self._manual_radio.isChecked())
        self._load_button.setEnabled(not self._manual_radio.isChecked())

        # If manual entry, enable import button based on content
        if self._manual_radio.isChecked():
            self._import_button.setEnabled(
                bool(self._preview_text.toPlainText().strip())
            )
        else:
            self._import_button.setEnabled(False)

    def _browse_for_file(self) -> None:
        """Open file dialog to select a text file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Word List File",
            "",
            "Text Files (*.txt);;CSV Files (*.csv);;LibreOffice Calc (*.ods);;All Files (*)",
        )

        if file_path:
            self._file_path_label.setText(os.path.basename(file_path))
            self._file_path_label.setToolTip(file_path)  # Keep tooltip for user hover
            self._file_path_label.setProperty(
                "file_path", file_path
            )  # Store full path as property
        else:
            # Clear the property if no file is selected or dialog is cancelled
            self._file_path_label.setText("No file selected")
            self._file_path_label.setToolTip("")
            self._file_path_label.setProperty("file_path", None)

    def _load_from_source(self) -> None:
        """Load content from the selected source."""
        try:
            if self._file_radio.isChecked():
                self._load_from_file()
            elif self._clipboard_radio.isChecked():
                self._load_from_clipboard()
            # No need for manual case as it's handled directly in the text edit

            # Enable import if content is loaded
            self._import_button.setEnabled(
                bool(self._preview_text.toPlainText().strip())
            )

        except Exception as e:
            logger.error(f"Error loading words: {e}")
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred while loading the word list: {str(e)}",
                QMessageBox.StandardButton.Ok,
            )

    def _load_from_file(self) -> None:
        """Load words from the selected file."""
        file_path = self._file_path_label.property("file_path")

        if (
            not file_path
        ):  # Check if file_path is None or empty after retrieving from property
            QMessageBox.warning(self, "Warning", "Please select a file first.")
            return

        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        content_items: List[
            Dict[str, Union[str, Optional[List[str]]]]
        ] = []  # List of dicts

        try:
            if file_extension == ".txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    # For TXT, assume each line is a word, no separate notes/tags columns
                    lines = f.readlines()
                    for line in lines:
                        content_items.append(
                            {"word": line.strip(), "notes": None, "tags": []}
                        )
            elif file_extension == ".csv":
                content_items = self._parse_csv_content(file_path)
            elif file_extension == ".ods":
                if ODFPY_AVAILABLE:
                    content_items = self._parse_ods_content(file_path)
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "ODS file support is not available. Please install the 'odfpy' library.",
                    )
                    return
            # Add elif for .xlsx if openpyxl is to be supported
            # elif file_extension in [".xlsx", ".xlsm"]:
            #     if OPENPYXL_AVAILABLE:
            #         content_items = self._parse_excel_content(file_path)
            #     else:
            #         QMessageBox.critical(self, "Error", "Excel file support (openpyxl) is not available.")
            #         return
            else:
                QMessageBox.warning(
                    self,
                    "Unsupported File",
                    f"File type {file_extension} is not supported.",
                )
                return

            # Enhanced preview content
            preview_lines = []
            for item in content_items[
                :50
            ]:  # Preview up to 50 items to keep it manageable
                line_parts = []
                if item.get("word"):
                    line_parts.append(f"Word: {item['word']}")
                if item.get("notes"):
                    notes_snippet = item["notes"][:50] + (
                        "..." if len(item["notes"]) > 50 else ""
                    )
                    line_parts.append(f"Notes: {notes_snippet}")
                if item.get("tags") and isinstance(item["tags"], list) and item["tags"]:
                    tags_str = ", ".join(item["tags"][:5])  # Show up to 5 tags
                    if len(item["tags"]) > 5:
                        tags_str += ", ..."
                    line_parts.append(f"Tags: [{tags_str}]")
                preview_lines.append(" | ".join(line_parts))

            self._preview_text.setPlainText("\n".join(preview_lines))
            self._word_list = content_items  # Store the list of dicts
            self._import_button.setEnabled(bool(self._word_list))
            logger.info(f"Loaded {len(self._word_list)} items from {file_path}")

        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            QMessageBox.critical(self, "Error", f"Could not load file: {e}")
            self._preview_text.clear()
            self._word_list = []
            self._import_button.setEnabled(False)

    def _parse_ods_content(
        self, file_path: str
    ) -> List[Dict[str, Union[str, Optional[List[str]]]]]:
        """Parse content from an ODS file."""
        if not ODFPY_AVAILABLE:
            logger.error("Attempted to parse ODS content but odfpy is not available.")
            return []

        logger.debug("--- ODS PARSE GRANULAR DEBUGGER V2 ---")
        logger.debug(f"Value of odf_table module itself: {odf_table}")
        logger.debug(f"Type of odf_table module itself: {type(odf_table)}")
        try:
            logger.debug(
                f"Value of odf_table.Table (direct access prior to getattr): {odf_table.Table}"
            )
            logger.debug(
                f"Type of odf_table.Table (direct access prior to getattr): {type(odf_table.Table)}"
            )
        except AttributeError:
            logger.debug(
                "AttributeError: odf_table.Table does not exist for direct access."
            )
        except Exception as e:
            logger.debug(f"Error accessing odf_table.Table directly: {e}")

        # Explicitly get types from the odf.table module to ensure they are valid for isinstance
        ODFTableType = getattr(odf_table, "Table", None)  # This is <function Table ...>
        ODFTableRowType = getattr(
            odf_table, "TableRow", None
        )  # This is <function TableRow ...>
        ODFTableCellType = getattr(
            odf_table, "TableCell", None
        )  # This is <function TableCell ...>

        logger.debug("--- AFTER GETATTR ---")
        logger.debug(f"Value of ODFTableType (from getattr): {ODFTableType}")
        logger.debug(f"Type of ODFTableType (from getattr): {type(ODFTableType)}")
        logger.debug(f"Value of ODFTableRowType (from getattr): {ODFTableRowType}")
        logger.debug(f"Type of ODFTableRowType (from getattr): {type(ODFTableRowType)}")
        logger.debug(f"Value of ODFTableCellType (from getattr): {ODFTableCellType}")
        logger.debug(
            f"Type of ODFTableCellType (from getattr): {type(ODFTableCellType)}"
        )

        if not all([ODFTableType, ODFTableRowType, ODFTableCellType]):
            logger.error(
                "Critical error (Caught by 'if not all'): Could not dynamically resolve odfpy Table, TableRow, or TableCell functions. "
                "One or more of them resolved to None via getattr."
            )
            return []

        # Define expected qnames directly as tuples.
        TABLE_NAMESPACE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
        EXPECTED_TABLE_QNAME = (TABLE_NAMESPACE, "table")
        EXPECTED_ROW_QNAME = (TABLE_NAMESPACE, "table-row")
        EXPECTED_CELL_QNAME = (TABLE_NAMESPACE, "table-cell")

        logger.debug(f"Expected QName for Table: {EXPECTED_TABLE_QNAME}")
        logger.debug(f"Expected QName for TableRow: {EXPECTED_ROW_QNAME}")
        logger.debug(f"Expected QName for TableCell: {EXPECTED_CELL_QNAME}")

        content_items: List[Dict[str, Union[str, Optional[List[str]]]]] = []
        doc = odf_load(file_path)
        has_header = self._has_header_check.isChecked()

        tables = doc.spreadsheet.getElementsByType(ODFTableType)  # Use resolved type

        if not tables:
            logger.warning(f"No tables found in ODS file: {file_path}")
            return []

        sheet = tables[0]
        if not (hasattr(sheet, "qname") and sheet.qname == EXPECTED_TABLE_QNAME):
            logger.warning(
                f"First sheet retrieved (qname: {getattr(sheet, 'qname', 'N/A')}) is not a table element as expected (expected {EXPECTED_TABLE_QNAME}). Aborting ODS parse."
            )
            return []

        word_col_idx, notes_col_idx, tags_col_idx = -1, -1, -1

        actual_rows = sheet.getElementsByType(ODFTableRowType)  # Use resolved type
        num_rows = len(actual_rows)

        if num_rows == 0:
            logger.info(f"Sheet in {file_path} has no rows.")
            return []

        note_header_aliases = ["notes", "note", "description", "desc", "details"]
        tag_header_aliases = ["tags", "tag", "keywords", "category", "categories"]

        if has_header:
            header_row_element = actual_rows[0]
            if (
                hasattr(header_row_element, "qname")
                and header_row_element.qname == EXPECTED_ROW_QNAME
            ):
                header_cells = header_row_element.getElementsByType(ODFTableCellType)
                num_cols_in_header = len(header_cells)
                for i, cell_element in enumerate(header_cells):
                    if (
                        hasattr(cell_element, "qname")
                        and cell_element.qname == EXPECTED_CELL_QNAME
                    ):
                        cell_text = (
                            odf_teletype.extractText(cell_element).strip().lower()
                        )
                        if cell_text == "word":
                            word_col_idx = i
                        elif cell_text in note_header_aliases:
                            notes_col_idx = i
                        elif cell_text in tag_header_aliases:
                            tags_col_idx = i

                if (
                    word_col_idx == -1 and num_cols_in_header > 0
                ):  # If "word" header not found, default to first col
                    word_col_idx = 0
                # No positional fallback for notes and tags if their headers are not found
            else:  # Header row not a proper table-row
                has_header = False
                logger.warning(
                    "Header row was not a TableRow element, treating as no header."
                )
                if num_rows > 0:  # If there are data rows, first col is word
                    word_col_idx = 0
                # notes_col_idx and tags_col_idx remain -1

        if not has_header:
            if num_rows > 0:  # If there are data rows, first col is word
                word_col_idx = 0
            # notes_col_idx and tags_col_idx remain -1 (no notes/tags if no header)

        start_row_index_in_actual_rows = 1 if has_header else 0
        for r_idx in range(start_row_index_in_actual_rows, num_rows):
            row_element = actual_rows[r_idx]
            if not (
                hasattr(row_element, "qname")
                and row_element.qname == EXPECTED_ROW_QNAME
            ):
                logger.warning(
                    f"Skipping row {r_idx} as its qname ({getattr(row_element, 'qname', 'N/A')}) is not a table-row (expected {EXPECTED_ROW_QNAME})."
                )
                continue

            cells_in_row = row_element.getElementsByType(ODFTableCellType)
            num_cells_in_current_row = len(cells_in_row)
            word, notes, tags_str = None, None, None

            if word_col_idx != -1 and num_cells_in_current_row > word_col_idx:
                cell = cells_in_row[word_col_idx]
                if hasattr(cell, "qname") and cell.qname == EXPECTED_CELL_QNAME:
                    word = odf_teletype.extractText(cell).strip()

            if notes_col_idx != -1 and num_cells_in_current_row > notes_col_idx:
                cell = cells_in_row[notes_col_idx]
                if hasattr(cell, "qname") and cell.qname == EXPECTED_CELL_QNAME:
                    notes = odf_teletype.extractText(cell).strip() or None

            if tags_col_idx != -1 and num_cells_in_current_row > tags_col_idx:
                cell = cells_in_row[tags_col_idx]
                if hasattr(cell, "qname") and cell.qname == EXPECTED_CELL_QNAME:
                    tags_str = odf_teletype.extractText(cell).strip() or None

            tags_list = [t.strip() for t in tags_str.split(",")] if tags_str else []

            if word:  # Only add if a word was found
                content_items.append({"word": word, "notes": notes, "tags": tags_list})

        return content_items

    def _parse_csv_content(
        self, file_path: str
    ) -> List[Dict[str, Union[str, Optional[List[str]]]]]:
        """Parse content from a CSV file."""
        content_items: List[Dict[str, Union[str, Optional[List[str]]]]] = []
        has_header = self._has_header_check.isChecked()

        word_col_idx, notes_col_idx, tags_col_idx = -1, -1, -1

        note_header_aliases = ["notes", "note", "description", "desc", "details"]
        tag_header_aliases = ["tags", "tag", "keywords", "category", "categories"]

        with open(file_path, mode="r", encoding="utf-8", newline="") as csvfile:
            reader = csv.reader(csvfile)

            first_row_data = None
            try:
                first_row_data = next(reader)
            except StopIteration:
                return []  # Empty file

            if has_header:
                num_cols_in_header = len(first_row_data)
                for i, header_text in enumerate(first_row_data):
                    header_text_lower = header_text.strip().lower()
                    if header_text_lower == "word":
                        word_col_idx = i
                    elif header_text_lower in note_header_aliases:
                        notes_col_idx = i
                    elif header_text_lower in tag_header_aliases:
                        tags_col_idx = i

                if (
                    word_col_idx == -1 and num_cols_in_header > 0
                ):  # Default word to first col if not found by header
                    word_col_idx = 0
                # No positional fallback for notes and tags
            else:  # No header
                if len(first_row_data) > 0:  # First col is word
                    word_col_idx = 0
                # notes_col_idx and tags_col_idx remain -1

                # Process the first row as data if it wasn't a header
                word, notes, tags_str = None, None, None
                if word_col_idx != -1 and len(first_row_data) > word_col_idx:
                    word = first_row_data[word_col_idx].strip()
                # Notes and tags will be None as their col_idx are -1 if no header
                if notes_col_idx != -1 and len(first_row_data) > notes_col_idx:
                    notes = first_row_data[notes_col_idx].strip() or None
                if tags_col_idx != -1 and len(first_row_data) > tags_col_idx:
                    tags_str = first_row_data[tags_col_idx].strip() or None

                tags_list = [t.strip() for t in tags_str.split(",")] if tags_str else []
                if word:  # Only add if a word was found
                    content_items.append(
                        {"word": word, "notes": notes, "tags": tags_list}
                    )

            # Process remaining rows
            for row_data in reader:
                word, notes, tags_str = None, None, None
                if word_col_idx != -1 and len(row_data) > word_col_idx:
                    word = row_data[word_col_idx].strip()
                # Notes and tags will be None if their col_idx are -1
                if notes_col_idx != -1 and len(row_data) > notes_col_idx:
                    notes = row_data[notes_col_idx].strip() or None
                if tags_col_idx != -1 and len(row_data) > tags_col_idx:
                    tags_str = row_data[tags_col_idx].strip() or None

                tags_list = [t.strip() for t in tags_str.split(",")] if tags_str else []
                if word:  # Only add if a word was found
                    content_items.append(
                        {"word": word, "notes": notes, "tags": tags_list}
                    )
        return content_items

    def _load_from_clipboard(self) -> None:
        """Load content from the clipboard."""
        from PyQt6.QtGui import QGuiApplication

        clipboard = QGuiApplication.clipboard()
        content = clipboard.text()

        if not content:
            QMessageBox.warning(
                self,
                "Empty Clipboard",
                "The clipboard is empty or does not contain text.",
                QMessageBox.StandardButton.Ok,
            )
            return

        # Process based on selected delimiter
        delimiter = self._get_delimiter()
        words = []

        if delimiter == "\n":
            words = [line.strip() for line in content.split("\n") if line.strip()]
        else:
            words = [word.strip() for word in content.split(delimiter) if word.strip()]

        # Apply header handling
        if self._has_header_check.isChecked() and words:
            words = words[1:]

        # Set the preview text
        self._preview_text.setPlainText("\n".join(words))

    def _get_delimiter(self) -> str:
        """Get the actual delimiter character based on the selection.

        Returns:
            The delimiter character
        """
        delimiter_text = self._delimiter_combo.currentText()
        if delimiter_text == "Line Break":
            return "\n"
        elif delimiter_text == "Comma":
            return ","
        elif delimiter_text == "Tab":
            return "\t"
        elif delimiter_text == "Space":
            return " "
        elif delimiter_text == "Semicolon":
            return ";"
        return "\n"  # Default

    def _import_word_list(self) -> None:
        """Finalize the import and emit the signal."""
        # For manual entry/edits, parse the preview text.
        # For file/clipboard, self._word_list is already populated with dicts.

        final_items_to_import: List[Dict[str, Union[str, Optional[List[str]]]]] = []

        if self._manual_radio.isChecked() or (
            self._clipboard_radio.isChecked() and not self._word_list
        ):  # if clipboard was empty or manual mode
            text_content = self._preview_text.toPlainText()
            if not text_content.strip():
                QMessageBox.warning(self, "Empty List", "The list is empty.")
                return

            delimiter_str = self._get_delimiter()
            lines = []
            if delimiter_str == "\n":  # Line break
                lines = text_content.splitlines()
            else:
                # This simple split might not be robust enough if words/phrases contain the delimiter.
                # For manual entry, it's usually one item per line, or simple delimiters.
                # A more robust CSV-like parsing for manual entry with arbitrary delimiters is complex.
                # Assuming simple splitting is okay for preview/manual entry.
                lines = text_content.split(delimiter_str)

            for line in lines:
                # For manual entry, assume only words are provided, no distinct notes/tags columns.
                # Users would type "word, note, tag1;tag2" and need to parse that single line, which is beyond simple delimiter.
                # So, for now, treat each delimited item as just a 'word'.
                stripped_line = line.strip()
                if stripped_line:
                    final_items_to_import.append(
                        {"word": stripped_line, "notes": None, "tags": []}
                    )

        elif self._word_list and isinstance(
            self._word_list[0], dict
        ):  # Loaded from file (ODS/CSV)
            final_items_to_import = self._word_list

        elif self._word_list:  # Loaded from TXT file or old clipboard (list of strings)
            for item_str in self._word_list:
                if isinstance(item_str, str) and item_str.strip():
                    final_items_to_import.append(
                        {"word": item_str.strip(), "notes": None, "tags": []}
                    )

        if not final_items_to_import:
            QMessageBox.warning(self, "Empty List", "No words to import.")
            return

        word_count = len(final_items_to_import)
        self.import_complete.emit(
            final_items_to_import, self._selected_language, word_count
        )
        logger.info(
            f"Emitting import_complete with {word_count} items for language {self._selected_language.value}"
        )
        self.accept()

    def get_word_list(
        self,
    ) -> List[Dict[str, Union[str, Optional[List[str]]]]]:  # Changed return type
        """Return the list of imported words with their associated data."""
        return self._word_list  # self._word_list now stores list of dicts

    def get_selected_language(self) -> Language:
        """Get the selected language for the import.

        Returns:
            The selected language
        """
        return self._selected_language

    def _on_language_changed(self) -> None:
        """Handle language selection change."""
        selected_data = self._language_combo.currentData()
        if isinstance(selected_data, Language):
            self._selected_language = selected_data
            logger.debug(f"Import language changed to: {self._selected_language.value}")
        else:
            # Fallback or error if data is not Language enum as expected
            # This shouldn't happen if addItem was done correctly
            logger.error(
                f"Unexpected data type for language combo: {type(selected_data)}"
            )
            # Default to a known language or handle error
            self._selected_language = Language.HEBREW  # Or some other safe default


# Example usage (for testing the dialog independently)
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = ImportWordListDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        words = dialog.get_word_list()
        language = dialog.get_selected_language()
        logger.info(f"Imported words ({language.value}): {words}")
    sys.exit(app.exec())
