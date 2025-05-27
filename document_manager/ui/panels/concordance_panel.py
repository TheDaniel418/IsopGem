"""
Concordance Panel for Document Manager.

This panel provides a comprehensive interface for managing KWIC concordances,
including viewing, searching, filtering, and exporting concordance data.
"""

from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from document_manager.models.kwic_concordance import (
    ConcordanceExportFormat,
    ConcordanceTable,
)
from document_manager.services.concordance_service import ConcordanceService
from document_manager.services.document_service import DocumentService
from document_manager.ui.dialogs.concordance_creation_dialog import (
    ConcordanceCreationDialog,
)
from shared.services.service_locator import ServiceLocator


class ConcordancePanel(QWidget):
    """Panel for managing KWIC concordances."""

    def __init__(self, parent=None):
        """Initialize the concordance panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Get services from ServiceLocator
        self.concordance_service = ServiceLocator.get(ConcordanceService)
        self.document_service = ServiceLocator.get(DocumentService)

        # Current data
        self.current_concordance: Optional[ConcordanceTable] = None
        self.concordance_tables: List[Dict] = []

        # Search timer for debouncing
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)

        self._setup_ui()
        self._connect_signals()
        self._load_concordance_tables()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("KWIC Concordances")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Action buttons
        self.create_button = QPushButton("Create New Concordance")
        self.create_button.setStyleSheet(
            "QPushButton { background-color: #3498db; color: white; padding: 8px 16px; border: none; border-radius: 4px; }"
        )
        header_layout.addWidget(self.create_button)

        self.refresh_button = QPushButton("Refresh")
        header_layout.addWidget(self.refresh_button)

        layout.addLayout(header_layout)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Concordance list and controls
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Concordance viewer
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([300, 700])

    def _create_left_panel(self) -> QWidget:
        """Create the left panel with concordance list and controls."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Concordance tables list
        tables_group = QGroupBox("Concordance Tables")
        tables_layout = QVBoxLayout(tables_group)

        # Search/filter
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search concordances...")
        search_layout.addWidget(self.search_input)
        tables_layout.addLayout(search_layout)

        # Tables list
        self.tables_table = QTableWidget()
        self.tables_table.setColumnCount(4)
        self.tables_table.setHorizontalHeaderLabels(
            ["Name", "Entries", "Created", "Tags"]
        )

        # Configure table
        header = self.tables_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        self.tables_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tables_table.setAlternatingRowColors(True)
        self.tables_table.setSortingEnabled(True)

        tables_layout.addWidget(self.tables_table)

        # Table management buttons
        table_buttons_layout = QHBoxLayout()
        self.delete_table_button = QPushButton("Delete")
        self.delete_table_button.setEnabled(False)
        self.export_table_button = QPushButton("Export")
        self.export_table_button.setEnabled(False)
        table_buttons_layout.addWidget(self.delete_table_button)
        table_buttons_layout.addWidget(self.export_table_button)
        table_buttons_layout.addStretch()
        tables_layout.addLayout(table_buttons_layout)

        layout.addWidget(tables_group)

        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)

        self.stats_label = QLabel("Loading statistics...")
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(stats_group)

        return widget

    def _create_right_panel(self) -> QWidget:
        """Create the right panel with concordance viewer."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Concordance info
        info_group = QGroupBox("Concordance Information")
        info_layout = QVBoxLayout(info_group)

        self.info_label = QLabel("Select a concordance table to view details")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)

        layout.addWidget(info_group)

        # Search and filter controls
        filter_group = QGroupBox("Search & Filter")
        filter_layout = QVBoxLayout(filter_group)

        # Search controls
        search_controls_layout = QHBoxLayout()

        self.keyword_filter = QLineEdit()
        self.keyword_filter.setPlaceholderText("Filter by keyword...")
        search_controls_layout.addWidget(QLabel("Keyword:"))
        search_controls_layout.addWidget(self.keyword_filter)

        self.document_filter = QComboBox()
        self.document_filter.addItem("All Documents")
        search_controls_layout.addWidget(QLabel("Document:"))
        search_controls_layout.addWidget(self.document_filter)

        self.clear_filters_button = QPushButton("Clear Filters")
        search_controls_layout.addWidget(self.clear_filters_button)

        filter_layout.addLayout(search_controls_layout)

        # Context search
        context_layout = QHBoxLayout()
        self.left_context_filter = QLineEdit()
        self.left_context_filter.setPlaceholderText("Left context contains...")
        self.right_context_filter = QLineEdit()
        self.right_context_filter.setPlaceholderText("Right context contains...")

        context_layout.addWidget(QLabel("Left context:"))
        context_layout.addWidget(self.left_context_filter)
        context_layout.addWidget(QLabel("Right context:"))
        context_layout.addWidget(self.right_context_filter)

        filter_layout.addLayout(context_layout)

        layout.addWidget(filter_group)

        # Concordance entries table
        entries_group = QGroupBox("Concordance Entries")
        entries_layout = QVBoxLayout(entries_group)

        # Results info
        self.results_label = QLabel("No concordance selected")
        entries_layout.addWidget(self.results_label)

        # Entries table
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(6)
        self.entries_table.setHorizontalHeaderLabels(
            ["Keyword", "Left Context", "Right Context", "Document", "Position", "Line"]
        )

        # Configure entries table
        entries_header = self.entries_table.horizontalHeader()
        entries_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        entries_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        entries_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        entries_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        entries_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        entries_header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.entries_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.entries_table.setAlternatingRowColors(True)
        self.entries_table.setSortingEnabled(True)

        entries_layout.addWidget(self.entries_table)

        # Entry details
        self.entry_details = QTextEdit()
        self.entry_details.setMaximumHeight(100)
        self.entry_details.setPlaceholderText("Select an entry to view full context")
        self.entry_details.setReadOnly(True)
        entries_layout.addWidget(QLabel("Full Context:"))
        entries_layout.addWidget(self.entry_details)

        layout.addWidget(entries_group)

        return widget

    def _connect_signals(self):
        """Connect UI signals to handlers."""
        # Header buttons
        self.create_button.clicked.connect(self._create_concordance)
        self.refresh_button.clicked.connect(self._load_concordance_tables)

        # Tables list
        self.search_input.textChanged.connect(self._on_search_changed)
        self.tables_table.itemSelectionChanged.connect(self._on_table_selection_changed)
        self.delete_table_button.clicked.connect(self._delete_selected_table)
        self.export_table_button.clicked.connect(self._export_selected_table)

        # Filters
        self.keyword_filter.textChanged.connect(self._on_filter_changed)
        self.document_filter.currentTextChanged.connect(self._on_filter_changed)
        self.left_context_filter.textChanged.connect(self._on_filter_changed)
        self.right_context_filter.textChanged.connect(self._on_filter_changed)
        self.clear_filters_button.clicked.connect(self._clear_filters)

        # Entries table
        self.entries_table.itemSelectionChanged.connect(
            self._on_entry_selection_changed
        )

    def _load_concordance_tables(self):
        """Load concordance tables from the database."""
        try:
            self.concordance_tables = self.concordance_service.list_concordances()
            self._populate_tables_list()
            self._update_statistics()
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Failed to load concordance tables: {str(e)}"
            )

    def _populate_tables_list(self):
        """Populate the concordance tables list."""
        # Filter tables based on search
        search_text = self.search_input.text().lower()
        filtered_tables = []

        for table in self.concordance_tables:
            if (
                not search_text
                or search_text in table["name"].lower()
                or (
                    table["description"] and search_text in table["description"].lower()
                )
                or any(search_text in tag.lower() for tag in table.get("tags", []))
            ):
                filtered_tables.append(table)

        # Update table
        self.tables_table.setRowCount(len(filtered_tables))

        for row, table in enumerate(filtered_tables):
            # Name
            name_item = QTableWidgetItem(table["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, table["id"])
            self.tables_table.setItem(row, 0, name_item)

            # Entry count
            count_item = QTableWidgetItem(str(table["entry_count"]))
            self.tables_table.setItem(row, 1, count_item)

            # Created date
            created_item = QTableWidgetItem(table["created_at"].strftime("%Y-%m-%d"))
            self.tables_table.setItem(row, 2, created_item)

            # Tags
            tags_text = ", ".join(table.get("tags", []))
            tags_item = QTableWidgetItem(tags_text)
            self.tables_table.setItem(row, 3, tags_item)

    def _update_statistics(self):
        """Update the statistics display."""
        try:
            stats = self.concordance_service.get_statistics()
            stats_text = f"""
            Total Tables: {stats['total_tables']}
            Total Entries: {stats['total_entries']}
            Unique Keywords: {stats['unique_keywords']}
            Unique Documents: {stats['unique_documents']}
            """
            self.stats_label.setText(stats_text.strip())
        except Exception as e:
            self.stats_label.setText(f"Error loading statistics: {str(e)}")

    def _on_search_changed(self):
        """Handle search text changes."""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms delay

    def _perform_search(self):
        """Perform the actual search."""
        self._populate_tables_list()

    def _on_table_selection_changed(self):
        """Handle table selection changes."""
        selected_items = self.tables_table.selectedItems()
        if selected_items:
            # Get the table ID from the first column
            row = selected_items[0].row()
            name_item = self.tables_table.item(row, 0)
            table_id = name_item.data(Qt.ItemDataRole.UserRole)

            self._load_concordance_table(table_id)
            self.delete_table_button.setEnabled(True)
            self.export_table_button.setEnabled(True)
        else:
            self.current_concordance = None
            self._clear_concordance_display()
            self.delete_table_button.setEnabled(False)
            self.export_table_button.setEnabled(False)

    def _load_concordance_table(self, table_id: str):
        """Load a specific concordance table."""
        try:
            self.current_concordance = self.concordance_service.get_concordance(
                table_id
            )
            if self.current_concordance:
                self._display_concordance_info()
                self._populate_document_filter()
                self._display_concordance_entries()
            else:
                QMessageBox.warning(self, "Error", "Concordance table not found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load concordance: {str(e)}")

    def _display_concordance_info(self):
        """Display information about the current concordance."""
        if not self.current_concordance:
            return

        info_text = f"""
        <b>Name:</b> {self.current_concordance.name}<br>
        <b>Description:</b> {self.current_concordance.description or 'None'}<br>
        <b>Keywords:</b> {', '.join(self.current_concordance.keywords)}<br>
        <b>Documents:</b> {len(self.current_concordance.document_ids)}<br>
        <b>Entries:</b> {len(self.current_concordance.entries)}<br>
        <b>Created:</b> {self.current_concordance.created_at.strftime('%Y-%m-%d %H:%M:%S')}<br>
        <b>Tags:</b> {', '.join(self.current_concordance.tags) if self.current_concordance.tags else 'None'}
        """
        self.info_label.setText(info_text)

    def _populate_document_filter(self):
        """Populate the document filter dropdown."""
        self.document_filter.clear()
        self.document_filter.addItem("All Documents")

        if self.current_concordance:
            # Get unique document names
            doc_names = set(
                entry.document_name for entry in self.current_concordance.entries
            )
            for doc_name in sorted(doc_names):
                self.document_filter.addItem(doc_name)

    def _display_concordance_entries(self):
        """Display the concordance entries."""
        if not self.current_concordance:
            self.entries_table.setRowCount(0)
            self.results_label.setText("No concordance selected")
            return

        # Apply filters
        filtered_entries = self._apply_filters()

        # Update results label
        total_entries = len(self.current_concordance.entries)
        filtered_count = len(filtered_entries)
        self.results_label.setText(
            f"Showing {filtered_count} of {total_entries} entries"
        )

        # Populate table
        self.entries_table.setRowCount(len(filtered_entries))

        for row, entry in enumerate(filtered_entries):
            # Keyword
            keyword_item = QTableWidgetItem(entry.keyword)
            keyword_item.setData(Qt.ItemDataRole.UserRole, entry)
            self.entries_table.setItem(row, 0, keyword_item)

            # Left context
            left_item = QTableWidgetItem(entry.left_context)
            self.entries_table.setItem(row, 1, left_item)

            # Right context
            right_item = QTableWidgetItem(entry.right_context)
            self.entries_table.setItem(row, 2, right_item)

            # Document
            doc_item = QTableWidgetItem(entry.document_name)
            self.entries_table.setItem(row, 3, doc_item)

            # Position
            pos_item = QTableWidgetItem(str(entry.position))
            self.entries_table.setItem(row, 4, pos_item)

            # Line
            line_item = QTableWidgetItem(
                str(entry.line_number) if entry.line_number else ""
            )
            self.entries_table.setItem(row, 5, line_item)

    def _apply_filters(self) -> List:
        """Apply current filters to concordance entries."""
        if not self.current_concordance:
            return []

        entries = self.current_concordance.entries

        # Keyword filter
        keyword_text = self.keyword_filter.text().strip().lower()
        if keyword_text:
            entries = [e for e in entries if keyword_text in e.keyword.lower()]

        # Document filter
        doc_filter = self.document_filter.currentText()
        if doc_filter != "All Documents":
            entries = [e for e in entries if e.document_name == doc_filter]

        # Left context filter
        left_text = self.left_context_filter.text().strip().lower()
        if left_text:
            entries = [e for e in entries if left_text in e.left_context.lower()]

        # Right context filter
        right_text = self.right_context_filter.text().strip().lower()
        if right_text:
            entries = [e for e in entries if right_text in e.right_context.lower()]

        return entries

    def _on_filter_changed(self):
        """Handle filter changes."""
        if self.current_concordance:
            self._display_concordance_entries()

    def _clear_filters(self):
        """Clear all filters."""
        self.keyword_filter.clear()
        self.document_filter.setCurrentIndex(0)
        self.left_context_filter.clear()
        self.right_context_filter.clear()

    def _on_entry_selection_changed(self):
        """Handle entry selection changes."""
        selected_items = self.entries_table.selectedItems()
        if selected_items:
            # Get the entry from the first column
            row = selected_items[0].row()
            keyword_item = self.entries_table.item(row, 0)
            entry = keyword_item.data(Qt.ItemDataRole.UserRole)

            if entry:
                # Display full context
                full_context = (
                    f"{entry.left_context} **{entry.keyword}** {entry.right_context}"
                )
                self.entry_details.setText(full_context)
        else:
            self.entry_details.clear()

    def _clear_concordance_display(self):
        """Clear the concordance display."""
        self.info_label.setText("Select a concordance table to view details")
        self.entries_table.setRowCount(0)
        self.results_label.setText("No concordance selected")
        self.entry_details.clear()
        self.document_filter.clear()
        self.document_filter.addItem("All Documents")

    def _create_concordance(self):
        """Open the concordance creation dialog."""
        dialog = ConcordanceCreationDialog(
            self.concordance_service, self.document_service, self
        )
        dialog.concordanceCreated.connect(self._on_concordance_created)
        dialog.exec()

    def _on_concordance_created(self, table_id: str):
        """Handle when a new concordance is created."""
        self._load_concordance_tables()
        # Select the newly created concordance
        for row in range(self.tables_table.rowCount()):
            item = self.tables_table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == table_id:
                self.tables_table.selectRow(row)
                break

    def _delete_selected_table(self):
        """Delete the selected concordance table."""
        selected_items = self.tables_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        name_item = self.tables_table.item(row, 0)
        table_id = name_item.data(Qt.ItemDataRole.UserRole)
        table_name = name_item.text()

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the concordance table '{table_name}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.concordance_service.delete_concordance(table_id):
                    self._load_concordance_tables()
                    QMessageBox.information(
                        self, "Success", "Concordance table deleted successfully"
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "Failed to delete concordance table"
                    )
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to delete concordance: {str(e)}"
                )

    def _export_selected_table(self):
        """Export the selected concordance table."""
        if not self.current_concordance:
            return

        # Get export format from user
        formats = ["CSV", "TSV", "JSON", "HTML", "TXT"]
        format_choice, ok = QInputDialog.getItem(
            self, "Export Format", "Choose export format:", formats, 0, False
        )

        if not ok:
            return

        # Map format choice to file extension and filter
        format_map = {
            "CSV": ("csv", "CSV Files (*.csv)"),
            "TSV": ("tsv", "TSV Files (*.tsv)"),
            "JSON": ("json", "JSON Files (*.json)"),
            "HTML": ("html", "HTML Files (*.html)"),
            "TXT": ("txt", "Text Files (*.txt)"),
        }

        file_ext, file_filter = format_map.get(
            format_choice, ("csv", "CSV Files (*.csv)")
        )

        # Create export format
        export_format = ConcordanceExportFormat(
            format_type=file_ext.lower(), include_metadata=True, include_statistics=True
        )

        # Get save location
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Concordance",
            f"{self.current_concordance.name}.{file_ext}",
            f"{file_filter};;All Files (*.*)",
        )

        if filename:
            try:
                # Export data
                exported_data = self.concordance_service.export_concordance(
                    self.current_concordance.id, export_format
                )

                # Save to file
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(exported_data)

                QMessageBox.information(
                    self, "Success", f"Concordance exported to {filename}"
                )

            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to export concordance: {str(e)}"
                )
