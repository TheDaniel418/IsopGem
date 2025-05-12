"""
Purpose: Provides panel for word grouping and chain calculations in gematria.

This file is part of the gematria pillar and serves as a UI component.
It provides functionality for organizing words into groups and creating
calculation chains between words from different groups.

Key components:
- WordGroupChainPanel: Panel for managing word groups and calculation chains

Dependencies:
- PyQt6: For UI components
- gematria.models.calculation_result: For storing calculation results
- gematria.services.gematria_service: For gematria calculations
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from gematria.models.calculation_result import CalculationResult

# Check if TQ module is available
try:
    from tq.services import tq_analysis_service
    from tq.services.geometric_transition_service import (
        get_instance as get_geo_transition_service,
    )

    TQ_AVAILABLE = True
except ImportError:
    TQ_AVAILABLE = False


class WordGroup:
    """Represents a group of words with their gematria values."""

    def __init__(self, name: str, group_id: str = None):
        """Initialize a word group.

        Args:
            name: The display name of the group
            group_id: Optional unique ID for the group (generated if not provided)
        """
        self.name = name
        self.group_id = group_id or str(uuid.uuid4())
        self.words = []  # List of (word, value, calculation_type) tuples

    def add_word(self, word: str, value: int, calculation_type: str) -> None:
        """Add a word to the group.

        Args:
            word: The word to add
            value: The gematria value of the word
            calculation_type: The calculation method used
        """
        self.words.append((word, value, calculation_type))

    def remove_word(self, index: int) -> None:
        """Remove a word from the group by index.

        Args:
            index: The index of the word to remove
        """
        if 0 <= index < len(self.words):
            self.words.pop(index)


class Chain:
    """Represents a calculation chain between words from different groups."""

    def __init__(self, name: str, chain_id: str = None):
        """Initialize a calculation chain.

        Args:
            name: The display name of the chain
            chain_id: Optional unique ID for the chain (generated if not provided)
        """
        self.name = name
        self.chain_id = chain_id or str(uuid.uuid4())
        # List of (group_id, word_index, operation) tuples
        # where operation is applied *after* this word's value ('+', '-', '*', '/', None for last item)
        self.links = []
        self.result = None  # Final calculated result

    def add_link(
        self, group_id: str, word_index: int, operation: Optional[str] = None
    ) -> None:
        """Add a link to the chain.

        Args:
            group_id: The ID of the group containing the word
            word_index: The index of the word in the group
            operation: The operation to apply after this word's value
        """
        self.links.append((group_id, word_index, operation))

    def calculate(self, groups: Dict[str, WordGroup]) -> int:
        """Calculate the result of the chain.

        Args:
            groups: Dictionary of group_id -> WordGroup

        Returns:
            The calculated result
        """
        if not self.links:
            return 0

        result = 0
        prev_value = None
        prev_op = None

        for i, (group_id, word_index, operation) in enumerate(self.links):
            # Get the word and its value
            if group_id not in groups:
                raise ValueError(f"Group {group_id} not found")

            group = groups[group_id]
            if word_index >= len(group.words):
                raise ValueError(
                    f"Word index {word_index} out of range in group {group.name}"
                )

            word, value, _ = group.words[word_index]

            # Apply the previous operation
            if i == 0:
                # First item, just store the value
                result = value
            else:
                # Apply the operation from the previous link
                if prev_op == "+":
                    result += value
                elif prev_op == "-":
                    result -= value
                elif prev_op == "*":
                    result *= value
                elif prev_op == "/":
                    if value == 0:
                        raise ValueError("Division by zero")
                    result /= value

            # Store the current operation for the next iteration
            prev_op = operation

        self.result = result
        return result


class WordGroupChainPanel(QWidget):
    """Panel for organizing words into groups and creating calculation chains."""

    chain_calculated = pyqtSignal(Chain)

    def __init__(self, parent=None, window_manager=None):
        """Initialize the panel.

        Args:
            parent: Parent widget
            window_manager: Window manager instance for managing windows
        """
        super().__init__(parent)
        self._groups = {}  # Dictionary of group_id -> WordGroup
        self._chains = []  # List of Chain objects
        self._selected_group_id = None
        self._window_manager = window_manager  # Store the window manager
        self._setup_ui()

        # Setup context menus for all tables
        self._setup_context_menus()

        logger.debug("WordGroupChainPanel initialized")

    def _setup_ui(self):
        """Initialize the UI components."""
        # Main layout with split view
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Word Groups & Chain Calculator")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Create a master splitter for the entire interface (3 panes)
        master_splitter = QSplitter(Qt.Orientation.Horizontal)

        # ===== LEFT PANE: Word Library =====
        word_library_widget = QWidget()
        word_library_layout = QVBoxLayout(word_library_widget)
        word_library_layout.setContentsMargins(5, 5, 5, 5)

        # Header for the word library
        word_library_header = QLabel("Word Library")
        word_library_header.setStyleSheet("font-size: 14px; font-weight: bold;")
        word_library_layout.addWidget(word_library_header)

        # Table showing all available words
        self._word_library_table = QTableWidget(0, 2)  # Columns: Word, Value
        self._word_library_table.setHorizontalHeaderLabels(["Word", "Value"])
        self._word_library_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._word_library_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self._word_library_table.setSelectionMode(
            QTableWidget.SelectionMode.MultiSelection
        )
        self._word_library_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        word_library_layout.addWidget(self._word_library_table)

        # Buttons for word library
        word_library_buttons = QHBoxLayout()

        import_words_btn = QPushButton("Import Words")
        import_words_btn.clicked.connect(self._import_words_from_results)
        import_words_btn.setToolTip("Import words from calculation results")
        word_library_buttons.addWidget(import_words_btn)

        # Create Group button - creates a new group from selected words
        create_group_btn = QPushButton("Create Group")
        create_group_btn.clicked.connect(self._create_group_from_selection)
        create_group_btn.setToolTip("Create a new group from selected words")
        word_library_buttons.addWidget(create_group_btn)

        add_to_group_btn = QPushButton("Add to Group")
        add_to_group_btn.clicked.connect(self._add_selected_words_to_group)
        add_to_group_btn.setToolTip("Add selected words to the current group")
        self._add_to_group_btn = (
            add_to_group_btn  # Store reference for enabling/disabling
        )
        self._add_to_group_btn.setEnabled(
            False
        )  # Initially disabled until a group is selected
        word_library_buttons.addWidget(add_to_group_btn)

        add_manual_word_btn = QPushButton("Add Manual Word")
        add_manual_word_btn.clicked.connect(self._add_manual_word_to_library)
        add_manual_word_btn.setToolTip("Add a word manually to the library")
        word_library_buttons.addWidget(add_manual_word_btn)

        word_library_layout.addLayout(word_library_buttons)

        # Add search/filter field
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        self._word_filter = QLineEdit()
        self._word_filter.setPlaceholderText("Filter words...")
        self._word_filter.textChanged.connect(self._filter_word_library)
        filter_layout.addWidget(self._word_filter)
        word_library_layout.addLayout(filter_layout)

        # Add the word library to the master splitter
        master_splitter.addWidget(word_library_widget)

        # ===== MIDDLE PANE: Groups and Chains =====
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setContentsMargins(5, 5, 5, 5)

        # Create a splitter for the two sections in the middle
        middle_splitter = QSplitter(Qt.Orientation.Vertical)

        # === Top section: Word Groups ===
        groups_widget = QWidget()
        groups_layout = QVBoxLayout(groups_widget)
        groups_layout.setContentsMargins(0, 0, 0, 0)

        groups_header = QLabel("Word Groups")
        groups_header.setStyleSheet("font-size: 14px; font-weight: bold;")
        groups_layout.addWidget(groups_header)

        # Group list with rename/remove buttons
        self._groups_list = QListWidget()
        self._groups_list.currentItemChanged.connect(self._on_group_selected)
        groups_layout.addWidget(self._groups_list)

        # Group buttons - only Rename and Remove now
        group_buttons = QHBoxLayout()

        rename_group_btn = QPushButton("Rename")
        rename_group_btn.clicked.connect(self._rename_selected_group)
        group_buttons.addWidget(rename_group_btn)

        remove_group_btn = QPushButton("Remove")
        remove_group_btn.clicked.connect(self._remove_selected_group)
        group_buttons.addWidget(remove_group_btn)

        groups_layout.addLayout(group_buttons)

        # Words in selected group
        groups_layout.addWidget(QLabel("Words in Selected Group:"))
        self._words_table = QTableWidget(0, 2)  # Columns: Word, Value
        self._words_table.setHorizontalHeaderLabels(["Word", "Value"])
        self._words_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._words_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self._words_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._words_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        groups_layout.addWidget(self._words_table)

        # Word operation buttons
        word_buttons = QHBoxLayout()

        remove_word_btn = QPushButton("Remove from Group")
        remove_word_btn.clicked.connect(self._remove_selected_word)
        word_buttons.addWidget(remove_word_btn)

        groups_layout.addLayout(word_buttons)

        # Add groups widget to middle splitter
        middle_splitter.addWidget(groups_widget)

        # === Bottom section: Calculation Chains ===
        chains_widget = QWidget()
        chains_layout = QVBoxLayout(chains_widget)
        chains_layout.setContentsMargins(0, 0, 0, 0)

        chains_header = QLabel("Calculation Chains")
        chains_header.setStyleSheet("font-size: 14px; font-weight: bold;")
        chains_layout.addWidget(chains_header)

        # Chain list
        self._chains_list = QListWidget()
        self._chains_list.currentItemChanged.connect(self._on_chain_selected)
        chains_layout.addWidget(self._chains_list)

        # Chain buttons
        chain_buttons = QHBoxLayout()

        add_chain_btn = QPushButton("New Chain")
        add_chain_btn.clicked.connect(self._create_new_chain)
        chain_buttons.addWidget(add_chain_btn)

        rename_chain_btn = QPushButton("Rename")
        rename_chain_btn.clicked.connect(self._rename_selected_chain)
        chain_buttons.addWidget(rename_chain_btn)

        remove_chain_btn = QPushButton("Remove")
        remove_chain_btn.clicked.connect(self._remove_selected_chain)
        chain_buttons.addWidget(remove_chain_btn)

        chains_layout.addLayout(chain_buttons)

        # Chain builder/editor
        chains_layout.addWidget(QLabel("Chain Builder:"))

        self._chain_builder = QTableWidget(0, 4)  # Word, Group, Value, Operation
        self._chain_builder.setHorizontalHeaderLabels(
            ["Word", "Group", "Value", "Operation"]
        )
        self._chain_builder.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._chain_builder.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self._chain_builder.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self._chain_builder.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        chains_layout.addWidget(self._chain_builder)

        # Chain operation buttons
        chain_op_buttons = QHBoxLayout()

        add_link_btn = QPushButton("Add Link")
        add_link_btn.clicked.connect(self._add_link_to_chain)
        chain_op_buttons.addWidget(add_link_btn)

        remove_link_btn = QPushButton("Remove Link")
        remove_link_btn.clicked.connect(self._remove_selected_link)
        chain_op_buttons.addWidget(remove_link_btn)

        calculate_btn = QPushButton("Calculate Chain")
        calculate_btn.clicked.connect(self._calculate_current_chain)
        chain_op_buttons.addWidget(calculate_btn)

        # Add "Send to Geometric Transitions" button if TQ module is available
        if TQ_AVAILABLE:
            geo_trans_btn = QPushButton("Send to Geometric Transitions")
            geo_trans_btn.clicked.connect(self._send_to_geometric_transitions)
            geo_trans_btn.setToolTip("Create a polygon with vertices from chain values")
            chain_op_buttons.addWidget(geo_trans_btn)

        chains_layout.addLayout(chain_op_buttons)

        # Chain result
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("Result:"))
        self._result_label = QLabel("---")
        self._result_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        result_layout.addWidget(self._result_label)
        result_layout.addStretch()
        chains_layout.addLayout(result_layout)

        # Add chains widget to middle splitter
        middle_splitter.addWidget(chains_widget)

        # Set initial splitter sizes for middle section
        middle_splitter.setSizes([300, 400])

        # Add middle splitter to layout
        middle_layout.addWidget(middle_splitter)

        # Add middle widget to master splitter
        master_splitter.addWidget(middle_widget)

        # ===== RIGHT PANE: Chain Combinations =====
        combinations_widget = QWidget()
        combinations_layout = QVBoxLayout(combinations_widget)
        combinations_layout.setContentsMargins(5, 5, 5, 5)

        combinations_header = QLabel("Chain Combinations")
        combinations_header.setStyleSheet("font-size: 14px; font-weight: bold;")
        combinations_layout.addWidget(combinations_header)

        # Generate button
        generate_buttons = QHBoxLayout()

        generate_btn = QPushButton("Generate All Combinations")
        generate_btn.clicked.connect(self._generate_all_combinations)
        generate_btn.setToolTip(
            "Generate all possible combinations of words from groups (addition only)"
        )
        generate_buttons.addWidget(generate_btn)

        clear_combinations_btn = QPushButton("Clear Results")
        clear_combinations_btn.clicked.connect(self._clear_combinations)
        generate_buttons.addWidget(clear_combinations_btn)

        combinations_layout.addLayout(generate_buttons)

        # Combinations table
        self._combinations_table = QTableWidget()
        self._combinations_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self._combinations_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self._combinations_table.setAlternatingRowColors(True)
        combinations_layout.addWidget(self._combinations_table)

        # Button to create chain from selected combination
        create_chain_btn = QPushButton("Create Chain from Selected Combination")
        create_chain_btn.clicked.connect(self._create_chain_from_combination)
        combinations_layout.addWidget(create_chain_btn)

        # Add combinations widget to master splitter
        master_splitter.addWidget(combinations_widget)

        # Set initial splitter sizes for entire interface
        master_splitter.setSizes([300, 500, 400])

        # Add the master splitter to the layout
        layout.addWidget(master_splitter)

        # Initialize word library
        self._all_words = (
            []
        )  # List of (word, value, method) tuples for internal storage
        self._refresh_word_library()

        # Store combinations data
        self._combinations = (
            []
        )  # List of (value, [(group_id, word_index, word, value), ...]) tuples

    def _setup_context_menus(self):
        """Set up right-click context menus for all tables."""
        # Word Library table
        self._word_library_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._word_library_table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(self._word_library_table, pos)
        )

        # Words in group table
        self._words_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._words_table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(self._words_table, pos)
        )

        # Chain builder table
        self._chain_builder.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._chain_builder.customContextMenuRequested.connect(
            lambda pos: self._show_chain_builder_context_menu(pos)
        )

        # Combinations table
        self._combinations_table.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._combinations_table.customContextMenuRequested.connect(
            lambda pos: self._show_context_menu(self._combinations_table, pos)
        )

    def _show_context_menu(self, table, position):
        """Show the context menu for a table.

        Args:
            table: The table widget that triggered the context menu
            position: Position of the click
        """
        # Get the item at the position
        item = table.itemAt(position)
        if not item:
            return

        # Try to get a numeric value from the item
        value = None

        # Check if the item has a numeric value directly
        try:
            value = int(item.text())
        except (ValueError, TypeError):
            # If not a direct number, check for pattern like "word (123)"
            import re

            match = re.search(r"\((\d+)\)", item.text())
            if match:
                value = int(match.group(1))
            else:
                # Check if it has value in UserRole
                user_data = item.data(Qt.ItemDataRole.UserRole)
                if isinstance(user_data, int):
                    value = user_data
                elif (
                    isinstance(user_data, tuple)
                    and len(user_data) > 0
                    and isinstance(user_data[0], int)
                ):
                    value = user_data[0]

        # If we found a numeric value, show the context menu
        if value is not None:
            menu = QMenu(self)

            # Only show the Quadset Analysis option if TQ is available
            if TQ_AVAILABLE:
                send_action = menu.addAction(f"Send {value} to Quadset Analysis")
                send_action.triggered.connect(
                    lambda: self._send_to_quadset_analysis(value)
                )

            # Only show menu if it has actions
            if not menu.isEmpty():
                menu.exec(table.viewport().mapToGlobal(position))

    def _show_chain_builder_context_menu(self, position):
        """Show the context menu for the chain builder table.

        Args:
            position: Position of the right-click
        """
        menu = QMenu(self)

        # Only proceed if a chain is selected
        current_item = self._chains_list.currentItem()
        if current_item and self._chain_builder.rowCount() > 0:
            # Add option to send to Geometric Transitions
            if TQ_AVAILABLE:
                geo_trans_action = menu.addAction("Send Chain to Geometric Transitions")
                geo_trans_action.triggered.connect(self._send_to_geometric_transitions)

            # Add other actions for the chain if needed
            # ...

            # Get the item at the position to support value-specific actions
            item = self._chain_builder.itemAt(position)
            if item:
                row = item.row()
                value_item = self._chain_builder.item(row, 2)  # Value column

                if value_item:
                    try:
                        value = int(value_item.text())

                        # Add "Send to Quadset Analysis" for the specific value
                        if TQ_AVAILABLE:
                            quadset_action = menu.addAction(
                                f"Send {value} to Quadset Analysis"
                            )
                            quadset_action.triggered.connect(
                                lambda: self._send_to_quadset_analysis(value)
                            )
                    except (ValueError, TypeError):
                        pass

        # Show the menu if it has actions
        if not menu.isEmpty():
            menu.exec(self._chain_builder.viewport().mapToGlobal(position))

    def _send_to_quadset_analysis(self, value):
        """Send a numeric value to the Quadset Analysis.

        Args:
            value: The numeric value to analyze
        """
        if not TQ_AVAILABLE:
            QMessageBox.warning(
                self,
                "Feature Unavailable",
                "The TQ module is not available in this installation.",
            )
            return

        try:
            # Use the tq_analysis_service to open the analysis window
            analysis_service = tq_analysis_service.get_instance()
            analysis_service.open_quadset_analysis(value)
            logger.debug(f"Sent value {value} to Quadset Analysis")
        except Exception as e:
            logger.error(f"Error opening Quadset Analysis window: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while opening Quadset Analysis: {str(e)}",
            )

    def _send_to_geometric_transitions(self):
        """Send the current chain to the Geometric Transitions panel.

        This function creates a polygon in the Geometric Transitions panel where:
        - The number of sides equals the number of words in the chain
        - The vertex values are set to the values of each word in the chain
        """
        # Check if TQ module is available
        if not TQ_AVAILABLE:
            QMessageBox.warning(
                self,
                "Feature Unavailable",
                "The TQ module is not available in this installation.",
            )
            return

        # Check if a chain is selected
        current_item = self._chains_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self,
                "No Chain Selected",
                "Please select a chain to send to Geometric Transitions.",
            )
            return

        # Get the chain ID and chain object
        chain_id = current_item.data(Qt.ItemDataRole.UserRole)
        chain = next((c for c in self._chains if c.chain_id == chain_id), None)
        if not chain:
            QMessageBox.warning(
                self,
                "Chain Not Found",
                "The selected chain could not be found.",
            )
            return

        try:
            # Extract the values and labels for all words in the chain
            values = []
            labels = []

            for group_id, word_index, _ in chain.links:
                if group_id in self._groups:
                    group = self._groups[group_id]
                    if word_index < len(group.words):
                        word, value, _ = group.words[word_index]
                        values.append(value)
                        labels.append(word)

            # Use the geometric_transition_service to open the panel
            geo_service = get_geo_transition_service()
            geo_service.open_geometric_transition(
                values, labels, f"Geometric Transitions - Chain: {chain.name}"
            )

            logger.debug(f"Sent chain '{chain.name}' to Geometric Transitions")
        except Exception as e:
            logger.error(f"Error sending chain to Geometric Transitions: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while sending chain to Geometric Transitions: {str(e)}",
            )

    def _create_new_group(self, default_name: str = None) -> None:
        """Create a new word group.

        Args:
            default_name: Optional default name for the new group
        """
        name, ok = QInputDialog.getText(
            self,
            "New Group",
            "Enter group name:",
            text=default_name or f"Group {len(self._groups) + 1}",
        )

        if ok and name:
            group = WordGroup(name)
            self._groups[group.group_id] = group

            # Add to list with stored group_id
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, group.group_id)
            self._groups_list.addItem(item)

            # Select the new group
            self._groups_list.setCurrentItem(item)
            self._selected_group_id = group.group_id

            logger.debug(f"Created new group: {name} with ID {group.group_id}")

    def _rename_selected_group(self) -> None:
        """Rename the currently selected group."""
        current_item = self._groups_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select a group to rename."
            )
            return

        group_id = current_item.data(Qt.ItemDataRole.UserRole)
        group = self._groups.get(group_id)
        if not group:
            logger.error(f"Group with ID {group_id} not found")
            return

        name, ok = QInputDialog.getText(
            self, "Rename Group", "Enter new group name:", text=group.name
        )

        if ok and name:
            group.name = name
            current_item.setText(name)
            logger.debug(f"Renamed group to: {name}")

    def _remove_selected_group(self) -> None:
        """Remove the currently selected group."""
        current_item = self._groups_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select a group to remove."
            )
            return

        group_id = current_item.data(Qt.ItemDataRole.UserRole)
        group = self._groups.get(group_id)
        if not group:
            logger.error(f"Group with ID {group_id} not found")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the group '{group.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            # Remove from dictionary
            del self._groups[group_id]

            # Remove from list
            row = self._groups_list.row(current_item)
            self._groups_list.takeItem(row)

            # Clear selected group
            if self._selected_group_id == group_id:
                self._selected_group_id = None
                self._update_words_table()

            logger.debug(f"Removed group: {group.name}")

    def _on_group_selected(self, current, previous) -> None:
        """Handle group selection change."""
        self._selected_group_id = (
            current.data(Qt.ItemDataRole.UserRole) if current else None
        )
        self._update_words_table()

        # Enable/disable the add to group button
        self._add_to_group_btn.setEnabled(self._selected_group_id is not None)

    def _update_words_table(self) -> None:
        """Update the words table for the selected group."""
        self._words_table.setRowCount(0)

        if not self._selected_group_id:
            return

        group = self._groups.get(self._selected_group_id)
        if not group:
            logger.error(f"Group with ID {self._selected_group_id} not found")
            return

        # Add words to table
        for i, (word, value, _) in enumerate(group.words):
            self._words_table.insertRow(i)

            word_item = QTableWidgetItem(word)
            self._words_table.setItem(i, 0, word_item)

            value_item = QTableWidgetItem(str(value))
            value_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            value_item.setData(Qt.ItemDataRole.UserRole, value)  # Store numeric value
            self._words_table.setItem(i, 1, value_item)

    def _remove_selected_word(self) -> None:
        """Remove the selected word from the current group."""
        if not self._selected_group_id:
            return

        group = self._groups.get(self._selected_group_id)
        if not group:
            return

        current_row = self._words_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a word to remove.")
            return

        # Remove from group
        group.remove_word(current_row)

        # Update table
        self._update_words_table()

    def _create_new_chain(self) -> None:
        """Create a new calculation chain."""
        name, ok = QInputDialog.getText(
            self,
            "New Chain",
            "Enter chain name:",
            text=f"Chain {len(self._chains) + 1}",
        )

        if ok and name:
            chain = Chain(name)
            self._chains.append(chain)

            # Add to list with stored chain_id
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, chain.chain_id)
            self._chains_list.addItem(item)

            # Select the new chain
            self._chains_list.setCurrentItem(item)

            # Clear builder table
            self._chain_builder.setRowCount(0)

            logger.debug(f"Created new chain: {name} with ID {chain.chain_id}")

    def _rename_selected_chain(self) -> None:
        """Rename the currently selected chain."""
        current_item = self._chains_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select a chain to rename."
            )
            return

        chain_id = current_item.data(Qt.ItemDataRole.UserRole)
        chain = next((c for c in self._chains if c.chain_id == chain_id), None)
        if not chain:
            logger.error(f"Chain with ID {chain_id} not found")
            return

        name, ok = QInputDialog.getText(
            self, "Rename Chain", "Enter new chain name:", text=chain.name
        )

        if ok and name:
            chain.name = name
            current_item.setText(name)
            logger.debug(f"Renamed chain to: {name}")

    def _remove_selected_chain(self) -> None:
        """Remove the currently selected chain."""
        current_item = self._chains_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select a chain to remove."
            )
            return

        chain_id = current_item.data(Qt.ItemDataRole.UserRole)
        chain = next((c for c in self._chains if c.chain_id == chain_id), None)
        if not chain:
            logger.error(f"Chain with ID {chain_id} not found")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the chain '{chain.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            # Remove from list
            self._chains.remove(chain)

            # Remove from list widget
            row = self._chains_list.row(current_item)
            self._chains_list.takeItem(row)

            # Clear builder table
            self._chain_builder.setRowCount(0)

            logger.debug(f"Removed chain: {chain.name}")

    def _on_chain_selected(self, current, previous) -> None:
        """Handle chain selection change.

        Args:
            current: Current selected item
            previous: Previously selected item
        """
        if current:
            chain_id = current.data(Qt.ItemDataRole.UserRole)
            chain = next((c for c in self._chains if c.chain_id == chain_id), None)
            if chain:
                self._update_chain_builder(chain)

    def _update_chain_builder(self, chain: Chain) -> None:
        """Update the chain builder table with the current chain.

        Args:
            chain: The chain to display
        """
        # Clear the table
        self._chain_builder.setRowCount(0)

        if not chain or not chain.links:
            return

        # Set row count
        self._chain_builder.setRowCount(len(chain.links))

        # Add links
        for i, (group_id, word_index, operation) in enumerate(chain.links):
            # Get the group and word
            if group_id not in self._groups:
                continue

            group = self._groups[group_id]
            if word_index >= len(group.words):
                continue

            word, value, _ = group.words[word_index]

            # Word column (0)
            word_item = QTableWidgetItem(word)
            word_item.setFlags(word_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._chain_builder.setItem(i, 0, word_item)

            # Group column (1)
            group_item = QTableWidgetItem(group.name)
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._chain_builder.setItem(i, 1, group_item)

            # Value column (2)
            value_item = QTableWidgetItem(str(value))
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._chain_builder.setItem(i, 2, value_item)

            # Operation column (3)
            if operation:
                op_combo = QComboBox()
                op_combo.addItems(["+", "-", "*", "/"])
                op_combo.setCurrentText(operation)
                op_combo.currentTextChanged.connect(
                    lambda op, row=i: self._update_operation(row, op)
                )
                self._chain_builder.setCellWidget(i, 3, op_combo)

        # Display the current result if available
        if chain.result is not None:
            self._result_label.setText(str(chain.result))
        else:
            self._result_label.setText("---")

    def _add_link_to_chain(self) -> None:
        """Add a link to the current chain."""
        # Check if a chain is selected
        if not self._chains_list.currentItem():
            QMessageBox.warning(
                self, "No Chain Selected", "Please select or create a chain first."
            )
            return

        chain_idx = self._chains_list.currentRow()
        if chain_idx < 0 or chain_idx >= len(self._chains):
            return

        chain = self._chains[chain_idx]

        # If there are no groups with words, show message
        if not any(len(group.words) > 0 for group in self._groups.values()):
            QMessageBox.warning(
                self,
                "No Words Available",
                "Please add words to at least one group before creating a chain.",
            )
            return

        # Create dialog for selecting a word from any group
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Word to Chain")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)

        # Table to show all words from all groups
        table = QTableWidget(0, 3)  # Group, Word, Value
        table.setHorizontalHeaderLabels(["Group", "Word", "Value"])
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Populate table with all words from all groups
        row = 0
        for group_id, group in self._groups.items():
            if not group.words:
                continue

            for word_idx, (word, value, _) in enumerate(group.words):
                table.insertRow(row)

                group_item = QTableWidgetItem(group.name)
                group_item.setData(Qt.ItemDataRole.UserRole, (group_id, word_idx))

                word_item = QTableWidgetItem(word)
                value_item = QTableWidgetItem(str(value))
                value_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )

                table.setItem(row, 0, group_item)
                table.setItem(row, 1, word_item)
                table.setItem(row, 2, value_item)

                row += 1

        layout.addWidget(table)

        # Operation selection for all but the first link
        operation_layout = QHBoxLayout()

        if chain.links:  # If this is not the first link, ask for operation
            operation_layout.addWidget(QLabel("Operation:"))
            operation_combo = QComboBox()
            operation_combo.addItems(["+", "-", "*", "/"])
            operation_layout.addWidget(operation_combo)
        else:
            operation_combo = None

        layout.addLayout(operation_layout)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Add to Chain")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Set up signals
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        # Execute dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get selected word
            selected_items = table.selectedItems()
            if not selected_items:
                return

            row = selected_items[0].row()
            group_item = table.item(row, 0)
            group_id, word_idx = group_item.data(Qt.ItemDataRole.UserRole)

            # Get operation
            operation = operation_combo.currentText() if operation_combo else None

            # Add to chain
            if chain.links:
                # If we already have links, set the operation for the last link
                chain.links[-1] = (chain.links[-1][0], chain.links[-1][1], operation)

            # Add the new link
            chain.add_link(group_id, word_idx, None)

            # Update chain builder
            self._update_chain_builder(chain)

            logger.debug(f"Added link to chain '{chain.name}'")

        # Update the chain builder
        self._update_chain_builder(chain)

    def _remove_selected_link(self) -> None:
        """Remove the selected link from the current chain."""
        # Check if we have a selected chain
        current_item = self._chains_list.currentItem()
        if not current_item:
            return

        chain_id = current_item.data(Qt.ItemDataRole.UserRole)
        chain = next((c for c in self._chains if c.chain_id == chain_id), None)
        if not chain:
            return

        # Check if we have a selected link
        current_row = self._chain_builder.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a link to remove.")
            return

        # Remove the link
        if current_row < len(chain.links):
            chain.links.pop(current_row)

            # Update operation for previous link if this was not the last one
            if current_row > 0 and current_row == len(chain.links):
                chain.links[current_row - 1] = (
                    chain.links[current_row - 1][0],
                    chain.links[current_row - 1][1],
                    None,  # Clear operation for new last link
                )

            # Update builder
            self._update_chain_builder(chain)

    def _update_operation(self, row: int, operation: str) -> None:
        """Update the operation for a link in the current chain.

        Args:
            row: The row index in the builder table
            operation: The new operation
        """
        # Check if we have a selected chain
        current_item = self._chains_list.currentItem()
        if not current_item:
            return

        chain_id = current_item.data(Qt.ItemDataRole.UserRole)
        chain = next((c for c in self._chains if c.chain_id == chain_id), None)
        if not chain or row >= len(chain.links):
            return

        # Update the operation
        group_id, word_index, _ = chain.links[row]
        chain.links[row] = (group_id, word_index, operation)

    def _calculate_current_chain(self) -> None:
        """Calculate the current chain result."""
        # Check if we have a selected chain
        current_item = self._chains_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select a chain to calculate."
            )
            return

        chain_id = current_item.data(Qt.ItemDataRole.UserRole)
        chain = next((c for c in self._chains if c.chain_id == chain_id), None)
        if not chain:
            logger.error(f"Chain with ID {chain_id} not found")
            return

        # Check if the chain has links
        if not chain.links:
            QMessageBox.warning(self, "Empty Chain", "The selected chain has no links.")
            return

        # Calculate
        try:
            result = chain.calculate(self._groups)
            self._result_label.setText(str(result))

            # Emit signal
            self.chain_calculated.emit(chain)

            logger.debug(f"Calculated chain '{chain.name}' with result {result}")
        except ValueError as e:
            QMessageBox.critical(self, "Calculation Error", str(e))
            logger.error(f"Calculation error: {e}")

    def _add_selected_words_to_group(self) -> None:
        """Add words selected in the library to the current group."""
        if not self._selected_group_id:
            QMessageBox.warning(
                self, "No Group Selected", "Please select a group to add words to."
            )
            return

        # Get selected rows
        selected_rows = set()
        for item in self._word_library_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(
                self,
                "No Words Selected",
                "Please select one or more words from the library.",
            )
            return

        # Get the current group
        group = self._groups.get(self._selected_group_id)
        if not group:
            return

        # Add selected words to the group
        for row in sorted(selected_rows):
            word = self._word_library_table.item(row, 0).text()
            value = int(self._word_library_table.item(row, 1).text())

            # Check if word is already in the group
            for existing_word, _, _ in group.words:
                if existing_word == word:
                    # Skip duplicates
                    continue

            group.add_word(word, value, "Manual Entry")

        # Update the words table for the group
        self._update_words_table()

        # Deselect all words in the library
        self._word_library_table.clearSelection()

        logger.debug(f"Added selected words to group '{group.name}'")

    def _add_manual_word_to_library(self) -> None:
        """Add a manually entered word to the library."""
        # Get the word from user
        word, ok = QInputDialog.getText(
            self, "Add Word to Library", "Enter the word or phrase:"
        )

        if not ok or not word.strip():
            return

        # Get the value from user
        value, ok = QInputDialog.getInt(
            self,
            "Add Word to Library",
            f"Enter numerical value for '{word}':",
            0,
            0,
            999999,
            1,
        )

        if not ok:
            return

        # Add to the library
        self._all_words.append((word, value, "Manual Entry"))
        self._refresh_word_library()

        logger.debug(f"Added manual word to library: {word} = {value}")

    def _filter_word_library(self) -> None:
        """Filter the word library based on the filter text."""
        filter_text = self._word_filter.text().lower()

        for row in range(self._word_library_table.rowCount()):
            word = self._word_library_table.item(row, 0).text().lower()

            # Show row if filter is empty or word contains filter text
            should_show = not filter_text or filter_text in word
            self._word_library_table.setRowHidden(row, not should_show)

    def _refresh_word_library(self) -> None:
        """Refresh the word library table with all words."""
        self._word_library_table.setRowCount(len(self._all_words))

        for i, (word, value, method) in enumerate(self._all_words):
            word_item = QTableWidgetItem(word)
            word_item.setFlags(
                word_item.flags() & ~Qt.ItemFlag.ItemIsEditable
            )  # Make read-only

            value_item = QTableWidgetItem(str(value))
            value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            value_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )

            self._word_library_table.setItem(i, 0, word_item)
            self._word_library_table.setItem(i, 1, value_item)

        # Apply current filter
        self._filter_word_library()

    def import_calculation_results(self, results: List[CalculationResult]) -> bool:
        """Import calculation results into the panel.

        Args:
            results: List of calculation results

        Returns:
            True if imported successfully, False otherwise
        """
        if not results:
            logger.warning("No calculation results provided to import")
            return False

        logger.debug(
            f"Importing {len(results)} calculation results into word group chain panel"
        )

        # Add each result to our word library
        for i, result in enumerate(results):
            # Get the word text - try different possible attribute names
            if hasattr(result, "input_text"):
                word = result.input_text
            else:
                word = str(result)  # Fallback to string representation

            # Get the value - try different possible attribute names
            if hasattr(result, "result_value"):
                value = result.result_value
            elif hasattr(result, "total_value"):
                value = result.total_value
            elif hasattr(result, "value"):
                value = result.value
            else:
                value = 0  # Default fallback

            # Store method in the tuple for internal reference, even though we don't display it
            method = "Imported"

            # Skip if it's already in the library (avoid duplicates)
            if any(w[0] == word for w in self._all_words):
                logger.debug(f"Skipping duplicate word: {word}")
                continue

            logger.debug(
                f"Adding word {i+1}/{len(results)}: '{word}' with value {value}"
            )
            self._all_words.append((word, value, method))

        logger.debug(f"Added {len(self._all_words)} words to library")

        # Force refresh the word library display
        self._refresh_word_library()

        # Create a default group if none exists yet
        if not self._groups:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            group_name = f"Imported Group ({timestamp})"
            self._create_new_group(group_name)
            logger.debug(f"Created default group: {group_name}")

        # Show message to user
        QMessageBox.information(
            self,
            "Import Complete",
            f"Added {len(results)} words to the library.\n\n"
            f"Select words from the library and use 'Add to Group' to organize them.",
        )

        return True

    def _import_words_from_results(self) -> None:
        """Import words from calculation results.

        This is a placeholder method that would typically be called by external
        components. The actual import functionality is handled by the
        import_calculation_results method, which would be called from the window.
        """
        QMessageBox.information(
            self,
            "Import Words",
            "To import words, use the Word List Abacus calculator and then click 'Word Groups & Chains'.\n\n"
            "You can also add words manually using the 'Add Manual Word' button.",
        )

    def _create_group_from_selection(self) -> None:
        """Create a new group from words selected in the Word Library."""
        # Get selected rows
        selected_rows = set()
        for item in self._word_library_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(
                self,
                "No Words Selected",
                "Please select one or more words from the library to create a group.",
            )
            return

        # Get group name from user
        name, ok = QInputDialog.getText(
            self,
            "New Group",
            "Enter group name:",
            text=f"Group {len(self._groups) + 1}",
        )

        if not ok or not name:
            return

        # Create the group
        group = WordGroup(name)
        self._groups[group.group_id] = group

        # Add to list with stored group_id
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, group.group_id)
        self._groups_list.addItem(item)

        # Add selected words to group
        for row in sorted(selected_rows):
            word = self._word_library_table.item(row, 0).text()
            value = int(self._word_library_table.item(row, 1).text())

            # Add to group
            group.add_word(word, value, "Selected")

        # Select the new group
        self._groups_list.setCurrentItem(item)
        self._selected_group_id = group.group_id

        # Update the words table
        self._update_words_table()

        # Clear selection in word library
        self._word_library_table.clearSelection()

        logger.debug(f"Created new group '{name}' with {len(group.words)} words")

    def _generate_all_combinations(self) -> None:
        """Generate all possible combinations of words from groups (addition only)."""
        # Check if we have at least 2 groups
        if len(self._groups) < 2:
            QMessageBox.warning(
                self,
                "Not Enough Groups",
                "You need at least 2 groups to generate combinations. Please create more groups.",
            )
            return

        # Check if groups have words
        empty_groups = [g.name for g in self._groups.values() if not g.words]
        if empty_groups:
            QMessageBox.warning(
                self,
                "Empty Groups",
                f"The following groups are empty: {', '.join(empty_groups)}.\n"
                "Please add words to all groups before generating combinations.",
            )
            return

        # Clear previous combinations
        self._combinations = []

        # Get the list of groups with their words
        groups_data = []
        for group_id, group in self._groups.items():
            words_data = []
            for idx, (word, value, _) in enumerate(group.words):
                words_data.append((idx, word, value))
            groups_data.append((group_id, group.name, words_data))

        # Show progress dialog for long operations
        group_count = len(groups_data)
        word_counts = [len(g[2]) for g in groups_data]
        total_combinations = 1
        for count in word_counts:
            total_combinations *= count

        progress = QProgressDialog(
            "Generating combinations...", "Cancel", 0, total_combinations, self
        )
        progress.setWindowTitle("Generating Combinations")
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        # Generate all combinations using recursion
        current_combination = []
        processed = 0

        def generate_recursive(group_index):
            nonlocal processed

            if group_index >= len(groups_data):
                # We have a complete combination
                total_value = sum(item[3] for item in current_combination)
                self._combinations.append((total_value, current_combination.copy()))
                processed += 1
                progress.setValue(processed)
                if progress.wasCanceled():
                    return False
                return True

            group_id, group_name, words = groups_data[group_index]

            for idx, word, value in words:
                # Add this word to the current combination
                current_combination.append((group_id, idx, word, value))

                # Continue to the next group
                if not generate_recursive(group_index + 1):
                    return False

                # Remove this word for the next iteration
                current_combination.pop()

            return True

        # Start the recursive generation
        if not generate_recursive(0) or progress.wasCanceled():
            # User canceled
            self._combinations = []
            progress.close()
            return

        progress.close()

        # Sort combinations by value
        self._combinations.sort()

        # Update the table
        self._update_combinations_table()

        # Show info message
        QMessageBox.information(
            self,
            "Combinations Generated",
            f"Generated {len(self._combinations)} combinations.\n\n"
            "Select any combination to create a chain from it.",
        )

    def _update_combinations_table(self) -> None:
        """Update the combinations table with current combinations."""
        # Clear the table
        self._combinations_table.clear()

        # Exit if no combinations
        if not self._combinations:
            self._combinations_table.setRowCount(0)
            self._combinations_table.setColumnCount(0)
            return

        # Determine number of columns needed (value + one per group)
        group_count = len(
            set(
                item[0] for _, combination in self._combinations for item in combination
            )
        )

        # Set up the table
        self._combinations_table.setRowCount(len(self._combinations))
        self._combinations_table.setColumnCount(group_count + 1)  # +1 for sum column

        # Set the header labels
        header_labels = ["Value"]
        for group_id, group in self._groups.items():
            header_labels.append(f"Group: {group.name}")
        self._combinations_table.setHorizontalHeaderLabels(
            header_labels[: group_count + 1]
        )

        # Adjust column widths
        self._combinations_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        for i in range(1, group_count + 1):
            self._combinations_table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Stretch
            )

        # Populate the table
        for row, (value, combination) in enumerate(self._combinations):
            # Value column (sum)
            value_item = QTableWidgetItem(str(value))
            value_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            value_item.setData(Qt.ItemDataRole.UserRole, (value, combination))
            self._combinations_table.setItem(row, 0, value_item)

            # Word columns (one per group)
            group_to_column = {}
            column = 1

            # Sort combination items by group ID to ensure consistent ordering
            for group_id, idx, word, value in sorted(combination, key=lambda x: x[0]):
                if group_id not in group_to_column:
                    group_to_column[group_id] = column
                    column += 1

                col = group_to_column[group_id]
                if col < self._combinations_table.columnCount():
                    word_item = QTableWidgetItem(f"{word} ({value})")
                    self._combinations_table.setItem(row, col, word_item)

    def _clear_combinations(self) -> None:
        """Clear the combinations table."""
        self._combinations = []
        self._update_combinations_table()
        QMessageBox.information(
            self, "Combinations Cleared", "The combinations table has been cleared."
        )

    def _create_chain_from_combination(self) -> None:
        """Create a new chain from a selected combination."""
        # Check if a combination is selected
        current_row = self._combinations_table.currentRow()
        if current_row < 0 or current_row >= len(self._combinations):
            QMessageBox.warning(
                self, "No Selection", "Please select a combination from the table."
            )
            return

        # Get the selected combination
        value_item = self._combinations_table.item(current_row, 0)
        if not value_item:
            return

        total_value, combination = value_item.data(Qt.ItemDataRole.UserRole)

        # Create a new chain
        name, ok = QInputDialog.getText(
            self,
            "New Chain",
            "Enter chain name:",
            text=f"Chain {len(self._chains) + 1} (Sum: {total_value})",
        )

        if not ok or not name:
            return

        # Create the chain
        chain = Chain(name)

        # Add links for each word in the combination
        for i, (group_id, word_index, _, _) in enumerate(combination):
            # For all but the last link, add a '+' operation
            operation = "+" if i < len(combination) - 1 else None
            chain.add_link(group_id, word_index, operation)

        # Add to chains list
        self._chains.append(chain)

        # Add to list with stored chain_id
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, chain.chain_id)
        self._chains_list.addItem(item)

        # Select the new chain
        self._chains_list.setCurrentItem(item)

        # Update the chain builder
        self._update_chain_builder(chain)

        # Calculate the chain
        try:
            result = chain.calculate(self._groups)
            self._result_label.setText(str(result))

            # Emit signal
            self.chain_calculated.emit(chain)

            logger.debug(f"Created chain from combination: {name} with result {result}")
        except ValueError as e:
            QMessageBox.critical(self, "Calculation Error", str(e))
            logger.error(f"Calculation error: {e}")

        # Show confirmation
        QMessageBox.information(
            self,
            "Chain Created",
            f"Created new chain '{name}' with value {total_value}.\n\n"
            "The chain is now selected in the Chain Builder panel.",
        )
