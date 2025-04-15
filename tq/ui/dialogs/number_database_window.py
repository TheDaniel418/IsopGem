"""
Purpose: Provides a window for displaying TQ number database lookup results

This file is part of the tq pillar and serves as a UI component.
It is responsible for displaying database lookup results for a specific number,
including its properties, quadset, and references in other databases.

Key components:
- NumberDatabaseWindow: Main window class for displaying database lookup results

Dependencies:
- PyQt6: For the user interface components
- tq.services.tq_database_service: For database lookups
- tq.services.tq_analysis_service: For opening TQ Grid with numbers
- shared.services.number_properties_service: For number property calculations

Related files:
- tq/ui/widgets/ternary_transition_widget.py: Widget that initiates lookups
- tq/services/tq_database_service.py: Service that provides the lookup data
"""

from typing import Any, Dict

from loguru import logger
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from shared.ui.window_management import AuxiliaryWindow
from tq.services import tq_analysis_service, tq_database_service
from tq.utils.ternary_converter import decimal_to_ternary


class NumberDatabaseWindow(AuxiliaryWindow):
    """Window for displaying TQ number database lookup results."""

    def __init__(self, number: int, parent=None):
        """Initialize the Number Database window.

        Args:
            number: The decimal number to look up
            parent: The parent widget
        """
        # Initialize with proper title and window flags
        super().__init__(f"Number Database: {number}", parent)

        # Store the number being looked up
        self.number = number

        # Set minimum size
        self.setMinimumSize(800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create header with number information
        self._create_header(main_layout)

        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self._create_properties_tab()
        self._create_quadset_tab()
        self._create_references_tab()

        # Add action buttons
        self._create_action_buttons(main_layout)

        # Perform the database lookup
        self._perform_lookup()

        logger.debug(f"NumberDatabaseWindow initialized for number {number}")

    def _create_header(self, layout):
        """Create header section with basic number information.

        Args:
            layout: The layout to add the header to
        """
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        header_layout = QHBoxLayout(header_frame)

        # Create number label
        number_label = QLabel(f"Number: {self.number}")
        number_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(number_label)

        # Create ternary representation label
        ternary = decimal_to_ternary(self.number)
        ternary_label = QLabel(f"Ternary: {ternary}")
        ternary_label.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        header_layout.addWidget(ternary_label)

        # Add to main layout
        layout.addWidget(header_frame)

    def _create_properties_tab(self):
        """Create the properties tab."""
        properties_widget = QWidget()
        properties_layout = QVBoxLayout(properties_widget)

        # Create a scroll area for properties
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Create section for basic properties
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QGridLayout(basic_group)

        # We'll populate this with actual properties when data is available
        self.basic_properties_layout = basic_layout

        # Create section for special properties
        special_group = QGroupBox("Special Properties")
        special_layout = QGridLayout(special_group)

        # We'll populate this with actual properties when data is available
        self.special_properties_layout = special_layout

        # Add property sections to layout
        scroll_layout.addWidget(basic_group)
        scroll_layout.addWidget(special_group)
        scroll_layout.addStretch()

        # Set the scroll area content
        scroll_area.setWidget(scroll_content)
        properties_layout.addWidget(scroll_area)

        # Add to tab widget
        self.tab_widget.addTab(properties_widget, "Properties")

    def _create_quadset_tab(self):
        """Create the quadset tab."""
        quadset_widget = QWidget()
        quadset_layout = QVBoxLayout(quadset_widget)

        # Create a scroll area for quadset
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Create section for quadset information
        quadset_group = QGroupBox("Quadset Information")
        quadset_layout_inner = QGridLayout(quadset_group)

        # We'll populate this with actual properties when data is available
        self.quadset_layout = quadset_layout_inner

        # Create section for other quadsets this number is part of
        other_quadsets_group = QGroupBox("Other Quadsets")
        other_quadsets_layout = QVBoxLayout(other_quadsets_group)

        # Create a label for quadset info
        self.other_quadsets_label = QLabel(
            "Checking if this number is part of other quadsets..."
        )
        other_quadsets_layout.addWidget(self.other_quadsets_label)

        # Add quadset sections to layout
        scroll_layout.addWidget(quadset_group)
        scroll_layout.addWidget(other_quadsets_group)
        scroll_layout.addStretch()

        # Set the scroll area content
        scroll_area.setWidget(scroll_content)
        quadset_layout.addWidget(scroll_area)

        # Add to tab widget
        self.tab_widget.addTab(quadset_widget, "Quadset")

    def _create_references_tab(self):
        """Create the references tab."""
        references_widget = QWidget()
        references_layout = QVBoxLayout(references_widget)

        # Create a label for information
        info_label = QLabel("References to this number in calculation database:")
        references_layout.addWidget(info_label)

        # Create a table for references
        self.references_table = QTableWidget()
        self.references_table.setColumnCount(4)
        self.references_table.setHorizontalHeaderLabels(
            ["Text", "Method", "Tags", "Date"]
        )
        self.references_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.references_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        self.references_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        self.references_table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )

        references_layout.addWidget(self.references_table)

        # Add to tab widget
        self.tab_widget.addTab(references_widget, "References")

    def _create_action_buttons(self, layout):
        """Create action buttons at the bottom of the window.

        Args:
            layout: The layout to add the buttons to
        """
        buttons_layout = QHBoxLayout()

        # Create "Open in TQ Grid" button
        open_grid_button = QPushButton("Open in TQ Grid")
        open_grid_button.setToolTip("Open this number in TQ Grid for detailed analysis")
        open_grid_button.clicked.connect(self._open_in_tq_grid)
        buttons_layout.addWidget(open_grid_button)

        # Add spacer to push close button to the right
        buttons_layout.addStretch()

        # Create close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(close_button)

        # Add buttons layout to main layout
        layout.addLayout(buttons_layout)

    def _perform_lookup(self):
        """Perform database lookup for the number."""
        # Get the database service
        db_service = tq_database_service.get_instance()

        # Perform lookup and update UI
        results = db_service.lookup_number(self.number)
        self._update_ui_with_results(results)

    def _update_ui_with_results(self, results: Dict[str, Any]):
        """Update UI with lookup results.

        Args:
            results: The lookup results to display
        """
        # Update properties tab
        self._update_properties_tab(results)

        # Update quadset tab
        self._update_quadset_tab(results)

        # Update references tab
        self._update_references_tab(results)

    def _update_properties_tab(self, results: Dict[str, Any]):
        """Update properties tab with lookup results.

        Args:
            results: The lookup results to display
        """
        # Get number properties
        props = results.get("number_properties", {})

        # Clear existing layout items
        self._clear_layout(self.basic_properties_layout)
        self._clear_layout(self.special_properties_layout)

        # Update basic properties
        row = 0

        # Is prime?
        is_prime = props.get("is_prime", False)
        self.basic_properties_layout.addWidget(QLabel("Prime:"), row, 0)
        prime_value = QLabel("Yes" if is_prime else "No")
        if is_prime:
            prime_value.setStyleSheet("color: green; font-weight: bold;")
        self.basic_properties_layout.addWidget(prime_value, row, 1)
        row += 1

        # Is triangular?
        is_triangular = props.get("is_triangular", False)
        self.basic_properties_layout.addWidget(QLabel("Triangular:"), row, 0)
        triangular_value = QLabel("Yes" if is_triangular else "No")
        if is_triangular:
            triangular_value.setStyleSheet("color: green; font-weight: bold;")
        self.basic_properties_layout.addWidget(triangular_value, row, 1)
        row += 1

        # Is square?
        is_square = props.get("is_square", False)
        self.basic_properties_layout.addWidget(QLabel("Square:"), row, 0)
        square_value = QLabel("Yes" if is_square else "No")
        if is_square:
            square_value.setStyleSheet("color: green; font-weight: bold;")
        self.basic_properties_layout.addWidget(square_value, row, 1)
        row += 1

        # Is fibonacci?
        is_fibonacci = props.get("is_fibonacci", False)
        self.basic_properties_layout.addWidget(QLabel("Fibonacci:"), row, 0)
        fibonacci_value = QLabel("Yes" if is_fibonacci else "No")
        if is_fibonacci:
            fibonacci_value.setStyleSheet("color: green; font-weight: bold;")
        self.basic_properties_layout.addWidget(fibonacci_value, row, 1)
        row += 1

        # Update special properties
        row = 0

        # Factors
        factors = props.get("factors", [])
        self.special_properties_layout.addWidget(QLabel("Prime Factors:"), row, 0)
        factors_value = QLabel(
            ", ".join(str(f) for f in factors) if factors else "None"
        )
        self.special_properties_layout.addWidget(factors_value, row, 1)
        row += 1

        # Divisors
        divisors = props.get("divisors", [])
        self.special_properties_layout.addWidget(QLabel("Divisors:"), row, 0)
        divisors_value = QLabel(
            ", ".join(str(d) for d in divisors) if divisors else "None"
        )
        self.special_properties_layout.addWidget(divisors_value, row, 1)
        row += 1

        # Add triangular index if applicable
        if is_triangular:
            triangular_index = props.get("triangular_index", 0)
            self.special_properties_layout.addWidget(
                QLabel("Triangular Index:"), row, 0
            )
            self.special_properties_layout.addWidget(
                QLabel(str(triangular_index)), row, 1
            )
            row += 1

        # Add fibonacci index if applicable
        if is_fibonacci:
            fibonacci_index = props.get("fibonacci_index", 0)
            self.special_properties_layout.addWidget(QLabel("Fibonacci Index:"), row, 0)
            self.special_properties_layout.addWidget(
                QLabel(str(fibonacci_index)), row, 1
            )
            row += 1

    def _update_quadset_tab(self, results: Dict[str, Any]):
        """Update quadset tab with lookup results.

        Args:
            results: The lookup results to display
        """
        # Get quadset properties
        quadset = results.get("quadset_properties", {})

        # Clear existing layout items
        self._clear_layout(self.quadset_layout)

        # Add quadset information
        if "base" in quadset:
            self._display_modern_quadset(quadset)
        else:
            self._display_legacy_quadset(quadset)

        # Update other quadsets section
        is_in_quadset_info = results.get("is_in_quadset", {})
        is_in_quadset = is_in_quadset_info.get("is_part_of_quadset", False)

        if is_in_quadset and "base_number" in is_in_quadset_info:
            base_number = is_in_quadset_info["base_number"]
            self.other_quadsets_label.setText(
                f"This number is part of the quadset with base number {base_number}.\n"
                f"Click here to open the TQ Grid for {base_number}."
            )
            self.other_quadsets_label.setStyleSheet("font-weight: bold; color: blue;")
            self.other_quadsets_label.mousePressEvent = (
                lambda _: self._open_other_quadset(base_number)
            )
        else:
            self.other_quadsets_label.setText(
                "This number is not part of any other quadsets."
            )

    def _display_modern_quadset(self, quadset: Dict[str, Any]):
        """Display quadset using the modern schema.

        Args:
            quadset: The quadset properties to display
        """
        row = 0

        # Base number
        base_info = quadset.get("base", {})
        self.quadset_layout.addWidget(QLabel("Base Number:"), row, 0)
        self.quadset_layout.addWidget(QLabel(str(base_info.get("number", ""))), row, 1)
        self.quadset_layout.addWidget(QLabel("Ternary:"), row, 2)
        self.quadset_layout.addWidget(QLabel(str(base_info.get("ternary", ""))), row, 3)
        row += 1

        # Conrune
        conrune_info = quadset.get("conrune", {})
        self.quadset_layout.addWidget(QLabel("Conrune:"), row, 0)
        self.quadset_layout.addWidget(
            QLabel(str(conrune_info.get("number", ""))), row, 1
        )
        self.quadset_layout.addWidget(QLabel("Ternary:"), row, 2)
        self.quadset_layout.addWidget(
            QLabel(str(conrune_info.get("ternary", ""))), row, 3
        )
        row += 1

        # Ternary reversal
        reversal_info = quadset.get("ternary_reversal", {})
        self.quadset_layout.addWidget(QLabel("Ternary Reversal:"), row, 0)
        self.quadset_layout.addWidget(
            QLabel(str(reversal_info.get("number", ""))), row, 1
        )
        self.quadset_layout.addWidget(QLabel("Ternary:"), row, 2)
        self.quadset_layout.addWidget(
            QLabel(str(reversal_info.get("ternary", ""))), row, 3
        )
        row += 1

        # Reversal conrune
        reversal_conrune_info = quadset.get("reversal_conrune", {})
        self.quadset_layout.addWidget(QLabel("Reversal Conrune:"), row, 0)
        self.quadset_layout.addWidget(
            QLabel(str(reversal_conrune_info.get("number", ""))), row, 1
        )
        self.quadset_layout.addWidget(QLabel("Ternary:"), row, 2)
        self.quadset_layout.addWidget(
            QLabel(str(reversal_conrune_info.get("ternary", ""))), row, 3
        )
        row += 1

        # Quadset sum
        if "quadset_sum" in quadset:
            self.quadset_layout.addWidget(QLabel("Quadset Sum:"), row, 0)
            self.quadset_layout.addWidget(QLabel(str(quadset["quadset_sum"])), row, 1)

    def _display_legacy_quadset(self, quadset: Dict[str, Any]):
        """Display quadset using the legacy schema.

        Args:
            quadset: The quadset properties to display
        """
        row = 0

        # Base number
        self.quadset_layout.addWidget(QLabel("Base Number:"), row, 0)
        self.quadset_layout.addWidget(QLabel(str(quadset.get("number", ""))), row, 1)
        self.quadset_layout.addWidget(QLabel("Ternary:"), row, 2)
        self.quadset_layout.addWidget(QLabel(str(quadset.get("ternary", ""))), row, 3)
        row += 1

        # Conrune
        self.quadset_layout.addWidget(QLabel("Conrune:"), row, 0)
        self.quadset_layout.addWidget(QLabel(str(quadset.get("conrune", ""))), row, 1)
        row += 1

        # Reverse ternary
        self.quadset_layout.addWidget(QLabel("Reverse Ternary:"), row, 0)
        self.quadset_layout.addWidget(
            QLabel(str(quadset.get("reverse_ternary_decimal", ""))), row, 1
        )
        self.quadset_layout.addWidget(QLabel("Ternary:"), row, 2)
        self.quadset_layout.addWidget(
            QLabel(str(quadset.get("reverse_ternary", ""))), row, 3
        )
        row += 1

        # Reverse conrune
        self.quadset_layout.addWidget(QLabel("Reverse Conrune:"), row, 0)
        self.quadset_layout.addWidget(
            QLabel(str(quadset.get("reverse_conrune", ""))), row, 1
        )

    def _update_references_tab(self, results: Dict[str, Any]):
        """Update references tab with lookup results.

        Args:
            results: The lookup results to display
        """
        # Get calculation references
        references = results.get("calculation_references", [])

        # Update the table
        self.references_table.setRowCount(len(references))

        for i, ref in enumerate(references):
            # Input text
            text_item = QTableWidgetItem(ref.get("input_text", ""))
            self.references_table.setItem(i, 0, text_item)

            # Method
            method_item = QTableWidgetItem(ref.get("method", ""))
            self.references_table.setItem(i, 1, method_item)

            # Tags
            tags = ref.get("tags", [])
            tags_item = QTableWidgetItem(", ".join(tags) if tags else "")
            self.references_table.setItem(i, 2, tags_item)

            # Date
            created_at = ref.get("created_at", "")
            date_item = QTableWidgetItem(str(created_at) if created_at else "")
            self.references_table.setItem(i, 3, date_item)

    def _clear_layout(self, layout):
        """Clear all widgets from a layout.

        Args:
            layout: The layout to clear
        """
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _open_in_tq_grid(self):
        """Open the number in TQ Grid."""
        try:
            # Get the analysis service
            analysis_service = tq_analysis_service.get_instance()

            # Open the quadset analysis
            analysis_service.open_quadset_analysis(self.number)

        except Exception as e:
            logger.error(f"Error opening TQ Grid: {e}")

    def _open_other_quadset(self, base_number: int):
        """Open another quadset in TQ Grid.

        Args:
            base_number: The base number of the quadset to open
        """
        try:
            # Get the analysis service
            analysis_service = tq_analysis_service.get_instance()

            # Open the quadset analysis
            analysis_service.open_quadset_analysis(base_number)

        except Exception as e:
            logger.error(f"Error opening TQ Grid for {base_number}: {e}")

    def ensure_on_top(self):
        """Ensure this window appears on top of other windows.

        This method is called by the window manager to bring the window to the front.
        It uses multiple methods to ensure the window is visible and has focus.
        """
        # Apply focus operations to ensure we're visible and on top
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
        self.show()
        self.raise_()
        self.activateWindow()

        # Use delayed focus to ensure window ordering is applied after other events
        QTimer.singleShot(100, self._delayed_focus)

        logger.debug(f"Ensuring NumberDatabaseWindow for {self.number} stays on top")

    def _delayed_focus(self):
        """Apply delayed focus operations to ensure window stays on top."""
        if self.isVisible():
            self.raise_()
            self.activateWindow()
            logger.debug(
                f"Applied delayed focus to NumberDatabaseWindow for {self.number}"
            )


if __name__ == "__main__":
    """Simple demonstration of the Number Database window."""
    import sys

    from PyQt6.QtWidgets import QApplication

    # Initialize the database service
    tq_database_service.initialize()

    app = QApplication(sys.argv)
    window = NumberDatabaseWindow(13)  # Use 13 as an example
    window.show()
    sys.exit(app.exec())
