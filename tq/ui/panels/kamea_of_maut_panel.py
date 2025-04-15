"""
Purpose: Provides a panel for exploring the Kamea of Maut ternary fractal system

This file is part of the tq pillar and serves as a UI component.
It is responsible for displaying and analyzing the 27×27 Kamea of Maut,
which represents a fractal arrangement of ternary numbers with special properties.

Key components:
- KameaOfMautPanel: Main panel for displaying and interacting with the Kamea
- KameaGridWidget: Widget for rendering the Kamea grid
- KameaAnalysisTools: Tools for analyzing patterns and relationships in the Kamea

Dependencies:
- PyQt6: For the user interface components
- pandas: For loading and manipulating the Kamea data
- tq.utils.ternary_transition: For calculating transitions between numbers
- tq.utils.ternary_converter: For converting between decimal and ternary

Related files:
- tq/ui/tq_tab.py: Tab that hosts this panel
- assets/cvs/Decimal Kamea.csv: Decimal representation of the Kamea
- assets/cvs/Ternary Decimal.csv: Ternary representation of the Kamea
"""

import os
from typing import Dict, List, Optional, Tuple

import pandas as pd
from loguru import logger
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from tq.utils.ternary_converter import decimal_to_ternary, ternary_to_decimal
from tq.utils.ternary_transition import TernaryTransition


class KameaGridWidget(QWidget):
    """Widget for displaying the Kamea grid with interactive features."""

    # Signal emitted when a cell is selected
    cell_selected = pyqtSignal(int, int, int)  # row, col, value

    def __init__(self, parent=None):
        """Initialize the Kamea grid widget.

        Args:
            parent: The parent widget
        """
        super().__init__(parent)

        # Initialize grid properties
        self.grid_size = 27
        self.cell_size = 36  # Smaller cells to fit everything
        self.padding = 10  # Minimal padding

        # Set up widget properties with fixed size to ensure all cells are visible
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # Calculate exact size needed for 27x27 grid with cell size and padding
        grid_width = self.grid_size * self.cell_size + 2 * self.padding
        grid_height = self.grid_size * self.cell_size + 2 * self.padding
        self.setFixedSize(grid_width, grid_height)
        self.decimal_mode = True  # Start in decimal mode

        # Initialize data
        self.decimal_data = None
        self.ternary_data = None

        # Initialize selection and highlighting
        self.selected_cell = None
        self.highlighted_cells = []
        self.secondary_highlighted_cells = []  # For the secondary quadset (OctaSet)

        # Load Kamea data
        self._load_kamea_data()

    def _load_kamea_data(self):
        """Load the Kamea data from CSV files."""
        try:
            # Get the absolute path to the CSV files
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            decimal_path = os.path.join(base_dir, "assets", "cvs", "Decimal Kamea.csv")
            ternary_path = os.path.join(base_dir, "assets", "cvs", "Ternary Decimal.csv")

            # Load the data
            self.decimal_data = pd.read_csv(decimal_path, header=None).values
            self.ternary_data = pd.read_csv(ternary_path, header=None).values

            logger.debug(f"Loaded Kamea data: {self.decimal_data.shape} decimal, {self.ternary_data.shape} ternary")
        except Exception as e:
            logger.error(f"Error loading Kamea data: {e}")
            # Create empty grids if loading fails
            self.decimal_data = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
            self.ternary_data = [["0" for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def set_view_mode(self, decimal_mode: bool):
        """Set the view mode (decimal or ternary).

        Args:
            decimal_mode: True for decimal view, False for ternary view
        """
        self.decimal_mode = decimal_mode
        self.update()  # Redraw the widget

    def paintEvent(self, event):
        """Handle paint events to draw the Kamea grid.

        Args:
            event: The paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate the total grid size
        total_width = self.grid_size * self.cell_size + 2 * self.padding
        total_height = self.grid_size * self.cell_size + 2 * self.padding

        # Draw background
        painter.fillRect(0, 0, total_width, total_height, QColor(245, 245, 245))

        # Draw grid lines with different weights to show the fractal structure

        # Draw and color center rows and columns (axes) first
        center_row = self.grid_size // 2
        center_col = self.grid_size // 2

        # Fill center row with light green background
        center_y = self.padding + center_row * self.cell_size
        painter.fillRect(
            self.padding,
            center_y,
            total_width - 2 * self.padding,
            self.cell_size,
            QColor(230, 255, 230)  # Light green
        )

        # Fill center column with light green background
        center_x = self.padding + center_col * self.cell_size
        painter.fillRect(
            center_x,
            self.padding,
            self.cell_size,
            total_height - 2 * self.padding,
            QColor(230, 255, 230)  # Light green
        )

        # Draw the finest grid lines (for individual cells)
        painter.setPen(QPen(QColor(230, 230, 230), 1))  # Very light gray for regular grid lines

        # Draw horizontal lines
        for i in range(self.grid_size + 1):
            y = i * self.cell_size + self.padding
            painter.drawLine(self.padding, y, total_width - self.padding, y)

        # Draw vertical lines
        for i in range(self.grid_size + 1):
            x = i * self.cell_size + self.padding
            painter.drawLine(x, self.padding, x, total_height - self.padding)

        # Draw medium lines for 3×3 areas
        painter.setPen(QPen(QColor(180, 180, 180), 1))  # Medium gray for 3×3 grid lines

        # Draw horizontal lines for 3×3 areas, ensuring proper alignment
        # Create a list of all positions where 3×3 grid lines should be drawn
        positions_3x3 = []
        for i in range(0, self.grid_size + 1, 3):
            positions_3x3.append(i)

        # Draw horizontal lines for 3×3 areas
        for i in positions_3x3:
            y = i * self.cell_size + self.padding
            painter.drawLine(self.padding, y, total_width - self.padding, y)

        # Draw vertical lines for 3×3 areas
        for i in positions_3x3:
            x = i * self.cell_size + self.padding
            painter.drawLine(x, self.padding, x, total_height - self.padding)

        # Draw bold lines for 9×9 areas
        painter.setPen(QPen(QColor(80, 80, 80), 2))  # Darker gray and thicker for 9×9 grid lines

        # Draw horizontal lines for 9×9 areas, ensuring they go through all cells including center
        # The 9×9 areas should be at positions 0, 9, 18, 27 (with 0-based indexing)
        for i in [0, 9, 18, 27]:  # Explicitly define the positions
            y = i * self.cell_size + self.padding
            painter.drawLine(self.padding, y, total_width - self.padding, y)

        # Draw vertical lines for 9×9 areas
        for i in [0, 9, 18, 27]:  # Explicitly define the positions
            x = i * self.cell_size + self.padding
            painter.drawLine(x, self.padding, x, total_height - self.padding)

        # Draw cell contents
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = col * self.cell_size + self.padding
                y = row * self.cell_size + self.padding

                # Draw cell background based on selection/highlighting
                if (row, col) == self.selected_cell:
                    painter.fillRect(x + 1, y + 1, self.cell_size - 1, self.cell_size - 1, QColor(173, 216, 230))  # Light blue
                elif (row, col) in self.highlighted_cells:
                    painter.fillRect(x + 1, y + 1, self.cell_size - 1, self.cell_size - 1, QColor(255, 255, 200))  # Light yellow
                elif (row, col) in self.secondary_highlighted_cells:
                    painter.fillRect(x + 1, y + 1, self.cell_size - 1, self.cell_size - 1, QColor(220, 190, 255))  # Light purple for OctaSet
                # Special styling for cells at the intersection of axes
                elif row == self.grid_size // 2 and col == self.grid_size // 2:
                    # Origin point (0,0) gets a special color
                    painter.fillRect(x + 1, y + 1, self.cell_size - 1, self.cell_size - 1, QColor(200, 255, 200))  # Brighter green

                # Draw cell text with special colors for axes
                # Set text color based on cell position
                if row == self.grid_size // 2 or col == self.grid_size // 2:
                    # Cells on axes get dark green text
                    painter.setPen(QColor(0, 100, 0))  # Dark green for axis cells
                else:
                    # Regular cells get black text
                    painter.setPen(QColor(0, 0, 0))

                if self.decimal_mode and self.decimal_data is not None:
                    text = str(self.decimal_data[row][col])
                elif not self.decimal_mode and self.ternary_data is not None:
                    # Ensure ternary numbers are padded to 6 digits
                    ternary_text = str(self.ternary_data[row][col])
                    text = ternary_text.zfill(6)  # Pad with leading zeros to 6 digits
                else:
                    text = "?"

                # Adjust font size based on view mode
                font = painter.font()
                if self.decimal_mode:
                    font.setPointSize(8)  # Font for decimal numbers
                else:
                    font.setPointSize(7)  # Smaller font for 6-digit ternary numbers
                painter.setFont(font)

                # Draw the text centered in the cell
                painter.drawText(x, y, self.cell_size, self.cell_size, Qt.AlignmentFlag.AlignCenter, text)

    def mousePressEvent(self, event):
        """Handle mouse press events to select cells.

        Args:
            event: The mouse event
        """
        # Calculate which cell was clicked
        x = event.position().x() - self.padding
        y = event.position().y() - self.padding

        col = int(x // self.cell_size)
        row = int(y // self.cell_size)

        # Check if the click is within the grid
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            self.selected_cell = (row, col)

            # Get the value at this cell
            if self.decimal_mode and self.decimal_data is not None:
                value = self.decimal_data[row][col]
            elif not self.decimal_mode and self.ternary_data is not None:
                value = self.ternary_data[row][col]
            else:
                value = 0

            # Emit the signal with the selected cell information
            self.cell_selected.emit(row, col, value)

            # Update the display
            self.update()

    def highlight_cells(self, cells: List[Tuple[int, int]]):
        """Highlight specific cells in the grid.

        Args:
            cells: List of (row, col) tuples to highlight
        """
        self.highlighted_cells = cells
        self.update()

    def highlight_secondary_cells(self, cells: List[Tuple[int, int]]):
        """Highlight secondary cells (for OctaSet) with a different color.

        Args:
            cells: List of (row, col) tuples to highlight as secondary
        """
        self.secondary_highlighted_cells = cells
        self.update()

    def clear_highlights(self):
        """Clear all cell highlights."""
        self.highlighted_cells = []
        self.secondary_highlighted_cells = []
        self.update()

    def get_kamea_value(self, row: int, col: int, decimal: bool = True) -> any:
        """Get the value at a specific position in the Kamea.

        Args:
            row: The row index
            col: The column index
            decimal: Whether to return the decimal value (True) or ternary (False)

        Returns:
            The value at the specified position
        """
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            if decimal and self.decimal_data is not None:
                return self.decimal_data[row][col]
            elif not decimal and self.ternary_data is not None:
                return self.ternary_data[row][col]
        return None


class KameaOfMautPanel(QFrame):
    """Panel for exploring and analyzing the Kamea of Maut."""

    def __init__(self, parent=None):
        """Initialize the Kamea of Maut panel.

        Args:
            parent: The parent widget
        """
        super().__init__(parent)

        # Set up the panel
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create the layout with minimal margins to maximize space
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # No title or description to maximize space

        # Create the main content area
        content_layout = QHBoxLayout()

        # Create the Kamea grid widget
        self.kamea_grid = KameaGridWidget()
        self.kamea_grid.cell_selected.connect(self._on_cell_selected)

        # Create a scroll area for the grid with minimal frame
        grid_scroll = QScrollArea()
        grid_scroll.setWidgetResizable(True)
        grid_scroll.setFrameShape(QFrame.Shape.NoFrame)  # Remove frame border
        grid_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Hide vertical scrollbar
        grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)  # Hide horizontal scrollbar
        grid_scroll.setWidget(self.kamea_grid)

        # Add the grid to the content layout
        content_layout.addWidget(grid_scroll, 3)  # Give it more space

        # Create the control panel
        control_panel = self._create_control_panel()
        content_layout.addWidget(control_panel, 1)  # Give it less space

        # Add the content layout to the main layout with priority to the grid
        self.layout.addLayout(content_layout, 1)

        # Initialize the transition utility
        self.transition = TernaryTransition()

        logger.debug("KameaOfMautPanel initialized")

    def _create_control_panel(self) -> QWidget:
        """Create the control panel for interacting with the Kamea.

        Returns:
            The control panel widget
        """
        # Create the control panel widget with minimal margins
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(5)

        # Create the view mode group with compact layout
        view_mode_group = QGroupBox("View Mode")
        view_mode_layout = QVBoxLayout(view_mode_group)
        view_mode_layout.setContentsMargins(5, 10, 5, 5)
        view_mode_layout.setSpacing(2)

        # Create radio buttons for view mode
        self.decimal_radio = QRadioButton("Decimal")
        self.decimal_radio.setChecked(True)  # Default to decimal view
        self.ternary_radio = QRadioButton("Ternary")

        # Add radio buttons to a button group
        view_mode_button_group = QButtonGroup(self)
        view_mode_button_group.addButton(self.decimal_radio)
        view_mode_button_group.addButton(self.ternary_radio)

        # Connect radio buttons to change view mode
        self.decimal_radio.toggled.connect(self._on_view_mode_changed)

        # Add radio buttons to the layout
        view_mode_layout.addWidget(self.decimal_radio)
        view_mode_layout.addWidget(self.ternary_radio)

        # Add the view mode group to the control panel
        control_layout.addWidget(view_mode_group)

        # Create the coordinate input group with compact layout
        coord_group = QGroupBox("Coordinates")
        coord_layout = QGridLayout(coord_group)
        coord_layout.setContentsMargins(5, 10, 5, 5)
        coord_layout.setSpacing(2)

        # Add X coordinate input
        coord_layout.addWidget(QLabel("X:"), 0, 0)
        self.x_coord = QSpinBox()
        self.x_coord.setRange(-13, 13)  # -13 to +13 for 27×27 grid
        self.x_coord.setValue(0)
        coord_layout.addWidget(self.x_coord, 0, 1)

        # Add Y coordinate input
        coord_layout.addWidget(QLabel("Y:"), 1, 0)
        self.y_coord = QSpinBox()
        self.y_coord.setRange(-13, 13)  # -13 to +13 for 27×27 grid
        self.y_coord.setValue(0)
        coord_layout.addWidget(self.y_coord, 1, 1)

        # Add Go button
        go_button = QPushButton("Go to Coordinates")
        go_button.clicked.connect(self._on_go_to_coordinates)
        coord_layout.addWidget(go_button, 2, 0, 1, 2)

        # Add the coordinate group to the control panel
        control_layout.addWidget(coord_group)

        # Create the analysis group with compact layout
        analysis_group = QGroupBox("Basic Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        analysis_layout.setContentsMargins(5, 10, 5, 5)
        analysis_layout.setSpacing(2)

        # Add analysis buttons
        show_quadset_button = QPushButton("Show Quadset")
        show_quadset_button.clicked.connect(self._on_show_quadset)
        analysis_layout.addWidget(show_quadset_button)

        show_transitions_button = QPushButton("Show Transitions")
        show_transitions_button.clicked.connect(self._on_show_transitions)
        analysis_layout.addWidget(show_transitions_button)

        clear_button = QPushButton("Clear Highlights")
        clear_button.clicked.connect(self._on_clear_highlights)
        analysis_layout.addWidget(clear_button)

        # Add the analysis group to the control panel
        control_layout.addWidget(analysis_group)

        # Create the advanced analysis group
        adv_analysis_group = QGroupBox("Advanced Analysis")
        adv_analysis_layout = QVBoxLayout(adv_analysis_group)
        adv_analysis_layout.setContentsMargins(5, 10, 5, 5)
        adv_analysis_layout.setSpacing(2)

        # Add advanced analysis buttons
        bigram_button = QPushButton("Bigram Analysis")
        bigram_button.clicked.connect(self._on_bigram_analysis)
        adv_analysis_layout.addWidget(bigram_button)

        locator_button = QPushButton("Kamea Locator")
        locator_button.clicked.connect(self._on_kamea_locator)
        adv_analysis_layout.addWidget(locator_button)

        pattern_button = QPushButton("Pattern Finder")
        pattern_button.clicked.connect(self._on_pattern_finder)
        adv_analysis_layout.addWidget(pattern_button)

        # Add the advanced analysis group to the control panel
        control_layout.addWidget(adv_analysis_group)

        # Add information display area with compact layout
        info_group = QGroupBox("Cell Information")
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(5, 10, 5, 5)
        info_layout.setSpacing(2)

        # Add labels for displaying information
        self.position_label = QLabel("Position: ")
        info_layout.addWidget(self.position_label)

        self.decimal_label = QLabel("Decimal: ")
        info_layout.addWidget(self.decimal_label)

        self.ternary_label = QLabel("Ternary: ")
        info_layout.addWidget(self.ternary_label)

        self.kamea_locator_label = QLabel("Kamea Locator: ")
        info_layout.addWidget(self.kamea_locator_label)

        # Add the info group to the control panel
        control_layout.addWidget(info_group)

        # Add a spacer to push everything up
        control_layout.addStretch(1)

        return control_panel

    def _on_view_mode_changed(self):
        """Handle changes to the view mode (decimal/ternary)."""
        decimal_mode = self.decimal_radio.isChecked()
        self.kamea_grid.set_view_mode(decimal_mode)

    def _on_cell_selected(self, row: int, col: int, value: any):
        """Handle cell selection in the Kamea grid.

        Args:
            row: The selected row
            col: The selected column
            value: The value at the selected cell
        """
        # Convert grid coordinates to Cartesian coordinates
        x = col - self.kamea_grid.grid_size // 2
        y = self.kamea_grid.grid_size // 2 - row  # Invert Y since grid Y increases downward

        # Update the coordinate spinboxes
        self.x_coord.setValue(x)
        self.y_coord.setValue(y)

        # Update the information display
        self.position_label.setText(f"Position: ({x}, {y})")

        # Get both decimal and ternary values
        decimal_value = self.kamea_grid.get_kamea_value(row, col, True)
        ternary_value = self.kamea_grid.get_kamea_value(row, col, False)

        # Ensure ternary value is padded to 6 digits
        if ternary_value is not None:
            ternary_value = str(ternary_value).zfill(6)

        self.decimal_label.setText(f"Decimal: {decimal_value}")
        self.ternary_label.setText(f"Ternary: {ternary_value}")

        # Calculate Kamea Locator (placeholder - implement actual calculation)
        # This would extract the bigrams and convert to decimal
        self.kamea_locator_label.setText(f"Kamea Locator: (placeholder)")

        logger.debug(f"Selected cell at grid ({row}, {col}), coords ({x}, {y}), value: {value}")

    def _on_go_to_coordinates(self):
        """Handle the Go to Coordinates button click."""
        # Get the Cartesian coordinates
        x = self.x_coord.value()
        y = self.y_coord.value()

        # Convert to grid coordinates
        col = x + self.kamea_grid.grid_size // 2
        row = self.kamea_grid.grid_size // 2 - y  # Invert Y since grid Y increases downward

        # Check if the coordinates are valid
        if 0 <= row < self.kamea_grid.grid_size and 0 <= col < self.kamea_grid.grid_size:
            # Select the cell
            self.kamea_grid.selected_cell = (row, col)

            # Get the value and update information
            value = self.kamea_grid.get_kamea_value(row, col, self.decimal_radio.isChecked())
            self._on_cell_selected(row, col, value)

            # Update the display
            self.kamea_grid.update()

            logger.debug(f"Went to coordinates ({x}, {y}), grid ({row}, {col})")
        else:
            logger.warning(f"Invalid coordinates: ({x}, {y})")

    def _on_show_quadset(self):
        """Handle the Show Quadset button click."""
        # Get the currently selected cell
        if self.kamea_grid.selected_cell is None:
            logger.warning("No cell selected")
            return

        row, col = self.kamea_grid.selected_cell

        # Convert to Cartesian coordinates
        x = col - self.kamea_grid.grid_size // 2
        y = self.kamea_grid.grid_size // 2 - row

        # Calculate the primary quadset coordinates (flipping signs)
        quadset_coords = [
            (x, y),      # First quadrant
            (-x, y),     # Second quadrant
            (-x, -y),    # Third quadrant
            (x, -y)      # Fourth quadrant
        ]

        # Calculate the secondary quadset coordinates (reversing x and y)
        # This creates the other half of the OctaSet
        reversed_quadset_coords = [
            (y, x),      # Reversed coordinates
            (-y, x),     # Reversed with flipped y
            (-y, -x),    # Reversed with both flipped
            (y, -x)      # Reversed with flipped x
        ]

        # Convert primary quadset to grid coordinates
        primary_grid_coords = []
        for qx, qy in quadset_coords:
            grid_row = self.kamea_grid.grid_size // 2 - qy
            grid_col = qx + self.kamea_grid.grid_size // 2
            if 0 <= grid_row < self.kamea_grid.grid_size and 0 <= grid_col < self.kamea_grid.grid_size:
                primary_grid_coords.append((grid_row, grid_col))

        # Convert secondary quadset to grid coordinates
        secondary_grid_coords = []
        for qx, qy in reversed_quadset_coords:
            grid_row = self.kamea_grid.grid_size // 2 - qy
            grid_col = qx + self.kamea_grid.grid_size // 2
            if 0 <= grid_row < self.kamea_grid.grid_size and 0 <= grid_col < self.kamea_grid.grid_size:
                secondary_grid_coords.append((grid_row, grid_col))

        # Highlight the primary quadset with normal highlighting
        self.kamea_grid.highlight_cells(primary_grid_coords)

        # Highlight the secondary quadset with a different color
        # We'll add this functionality to the KameaGridWidget class
        self.kamea_grid.highlight_secondary_cells(secondary_grid_coords)

        # Calculate and display the QuadSum for the primary quadset
        quad_sum = 0
        for grid_row, grid_col in primary_grid_coords:
            value = self.kamea_grid.get_kamea_value(grid_row, grid_col, True)  # Get decimal value
            if value is not None:
                quad_sum += value

        # Calculate the sum for the secondary quadset
        secondary_sum = 0
        for grid_row, grid_col in secondary_grid_coords:
            value = self.kamea_grid.get_kamea_value(grid_row, grid_col, True)  # Get decimal value
            if value is not None:
                secondary_sum += value

        logger.debug(f"Primary Quadset for ({x}, {y}): {quadset_coords}, QuadSum: {quad_sum}")
        logger.debug(f"Secondary Quadset (reversed x,y): {reversed_quadset_coords}, Sum: {secondary_sum}")
        logger.debug(f"OctaSet total sum: {quad_sum + secondary_sum}")

    def _on_show_transitions(self):
        """Handle the Show Transitions button click."""
        # Get the currently selected cell
        if self.kamea_grid.selected_cell is None:
            logger.warning("No cell selected")
            return

        row, col = self.kamea_grid.selected_cell

        # Convert to Cartesian coordinates
        x = col - self.kamea_grid.grid_size // 2
        y = self.kamea_grid.grid_size // 2 - row

        # Cells to highlight
        cells_to_highlight = [(row, col)]  # Start with the selected cell
        transitions_info = []

        # Find cells that demonstrate the axis transition property
        # For horizontal axis transitions (across the X-axis)
        if y != 0:  # Not on the horizontal axis
            # Find the cell on the other side of the horizontal axis
            mirror_y = -y
            mirror_row = self.kamea_grid.grid_size // 2 - mirror_y
            mirror_col = col

            # Find the cell on the axis between them
            axis_y = 0
            axis_row = self.kamea_grid.grid_size // 2 - axis_y
            axis_col = col

            # Add these cells to the highlight list
            cells_to_highlight.extend([(mirror_row, mirror_col), (axis_row, axis_col)])

            # Get the ternary values
            val1 = self.kamea_grid.get_kamea_value(row, col, False)  # Ternary
            val2 = self.kamea_grid.get_kamea_value(mirror_row, mirror_col, False)  # Ternary
            axis_val = self.kamea_grid.get_kamea_value(axis_row, axis_col, False)  # Ternary

            # Calculate the transition
            if val1 and val2:
                try:
                    transition_result = self.transition.apply_transition(str(val1), str(val2))
                    transitions_info.append(f"Horizontal axis transition: {val1} + {val2} = {transition_result}, axis value: {axis_val}")
                except Exception as e:
                    logger.error(f"Error calculating transition: {e}")

        # For vertical axis transitions (across the Y-axis)
        if x != 0:  # Not on the vertical axis
            # Find the cell on the other side of the vertical axis
            mirror_x = -x
            mirror_row = row
            mirror_col = self.kamea_grid.grid_size // 2 + mirror_x

            # Find the cell on the axis between them
            axis_x = 0
            axis_row = row
            axis_col = self.kamea_grid.grid_size // 2 + axis_x

            # Add these cells to the highlight list
            cells_to_highlight.extend([(mirror_row, mirror_col), (axis_row, axis_col)])

            # Get the ternary values
            val1 = self.kamea_grid.get_kamea_value(row, col, False)  # Ternary
            val2 = self.kamea_grid.get_kamea_value(mirror_row, mirror_col, False)  # Ternary
            axis_val = self.kamea_grid.get_kamea_value(axis_row, axis_col, False)  # Ternary

            # Calculate the transition
            if val1 and val2:
                try:
                    transition_result = self.transition.apply_transition(str(val1), str(val2))
                    transitions_info.append(f"Vertical axis transition: {val1} + {val2} = {transition_result}, axis value: {axis_val}")
                except Exception as e:
                    logger.error(f"Error calculating transition: {e}")

        # Highlight all the cells
        self.kamea_grid.highlight_cells(cells_to_highlight)

        # Log all transition information
        for info in transitions_info:
            logger.debug(info)

    def _on_clear_highlights(self):
        """Handle the Clear Highlights button click."""
        self.kamea_grid.clear_highlights()

    def _on_bigram_analysis(self):
        """Handle the Bigram Analysis button click."""
        # Get the currently selected cell
        if self.kamea_grid.selected_cell is None:
            logger.warning("No cell selected for bigram analysis")
            return

        row, col = self.kamea_grid.selected_cell

        # Get the ternary value
        ternary_value = self.kamea_grid.get_kamea_value(row, col, False)
        if ternary_value is None:
            logger.warning("Could not get ternary value for selected cell")
            return

        # Ensure it's a string and padded to 6 digits
        ternary_str = str(ternary_value).zfill(6)

        # Extract the three bigrams (pairing from opposite ends)
        # For a 6-digit number, digit positions are 0-5 in the string
        # Digit 6 = position 0 (most significant/leftmost)
        # Digit 1 = position 5 (least significant/rightmost)
        bigram1 = ternary_str[0] + ternary_str[5]  # First bigram (digits 6 and 1)
        bigram2 = ternary_str[1] + ternary_str[4]  # Second bigram (digits 5 and 2)
        bigram3 = ternary_str[2] + ternary_str[3]  # Third bigram (digits 4 and 3)

        # Convert to decimal for easier understanding
        bigram1_dec = int(bigram1, 3)  # Base 3 to decimal
        bigram2_dec = int(bigram2, 3)
        bigram3_dec = int(bigram3, 3)

        # Create a simple message box with the bigram information
        from PyQt6.QtWidgets import QMessageBox

        msg = QMessageBox()
        msg.setWindowTitle("Bigram Analysis")
        msg.setText(f"Ternary Value: {ternary_str}")
        msg.setInformativeText(
            f"First Bigram: {bigram1} (decimal: {bigram1_dec})\n" +
            f"Second Bigram: {bigram2} (decimal: {bigram2_dec})\n" +
            f"Third Bigram: {bigram3} (decimal: {bigram3_dec})\n\n" +
            f"The third bigram determines the 9×9 region.\n" +
            f"The second bigram determines the 3×3 area within that region.\n" +
            f"The first bigram determines the specific cell within that 3×3 area."
        )
        msg.setIcon(QMessageBox.Icon.Information)

        # Add buttons for highlighting
        highlight_first = msg.addButton("Highlight Same Cell in 3×3 Areas", QMessageBox.ButtonRole.ActionRole)
        highlight_second = msg.addButton("Highlight Same Position in 3×3 Areas", QMessageBox.ButtonRole.ActionRole)
        highlight_third = msg.addButton("Highlight 9×9 Region", QMessageBox.ButtonRole.ActionRole)
        close_button = msg.addButton(QMessageBox.StandardButton.Close)

        # Show the dialog
        msg.exec()

        # Process the button click
        clicked_button = msg.clickedButton()

        # Clear any existing highlights
        self.kamea_grid.clear_highlights()

        # Handle highlighting based on which button was clicked
        if clicked_button == highlight_first:
            # Highlight cells with the same first bigram (9x9 area)
            self._highlight_cells_with_bigram(0, bigram1)

        elif clicked_button == highlight_second:
            # Highlight cells with the same second bigram (3x3 areas)
            self._highlight_cells_with_bigram(1, bigram2)

        elif clicked_button == highlight_third:
            # Highlight cells with the same third bigram (equivalent cells)
            self._highlight_cells_with_bigram(2, bigram3)

    def _highlight_cells_with_bigram(self, bigram_index, bigram_value):
        """Highlight cells with a matching bigram.

        Args:
            bigram_index: 0 for first bigram, 1 for second, 2 for third
            bigram_value: The bigram value to match
        """
        matching_cells = []

        # Determine which bigram we're matching
        if bigram_index == 0:
            logger.debug(f"Highlighting cells with first bigram {bigram_value} (same cell in 3x3 areas)")
        elif bigram_index == 1:
            logger.debug(f"Highlighting cells with second bigram {bigram_value} (same position in 3x3 areas)")
        elif bigram_index == 2:
            logger.debug(f"Highlighting cells with third bigram {bigram_value} (9x9 region)")

        # Search for cells with matching bigram
        for r in range(self.kamea_grid.grid_size):
            for c in range(self.kamea_grid.grid_size):
                value = self.kamea_grid.get_kamea_value(r, c, False)
                if value is not None:
                    cell_ternary = str(value).zfill(6)

                    # Extract the appropriate bigram based on the index
                    if bigram_index == 0:
                        # First bigram (digits 6 and 1)
                        cell_bigram = cell_ternary[0] + cell_ternary[5]
                    elif bigram_index == 1:
                        # Second bigram (digits 5 and 2)
                        cell_bigram = cell_ternary[1] + cell_ternary[4]
                    elif bigram_index == 2:
                        # Third bigram (digits 4 and 3)
                        cell_bigram = cell_ternary[2] + cell_ternary[3]

                    # Check if this cell matches the criteria
                    if cell_bigram == bigram_value:
                        matching_cells.append((r, c))

        # Highlight the matching cells
        if matching_cells:
            self.kamea_grid.highlight_cells(matching_cells)

            # Calculate the sum of the highlighted cells
            total_sum = 0
            for r, c in matching_cells:
                value = self.kamea_grid.get_kamea_value(r, c, True)  # Get decimal value
                if value is not None:
                    total_sum += value

            # Show the sum in a non-modal dialog
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
            from PyQt6.QtCore import Qt

            # Determine which bigram we highlighted
            bigram_type = ""
            if bigram_index == 0:
                bigram_type = "first bigram (same cell in 3×3 areas)"
            elif bigram_index == 1:
                bigram_type = "second bigram (same position in 3×3 areas)"
            elif bigram_index == 2:
                bigram_type = "third bigram (9×9 region)"

            # Create a non-modal dialog
            summary_dialog = QDialog(self, Qt.WindowType.Tool)
            summary_dialog.setWindowTitle("Bigram Highlight Summary")
            summary_dialog.setMinimumWidth(300)

            # Create layout
            layout = QVBoxLayout(summary_dialog)

            # Add information labels
            title_label = QLabel(f"Highlighted {len(matching_cells)} cells with {bigram_type}")
            title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
            layout.addWidget(title_label)

            layout.addWidget(QLabel(f"Bigram value: {bigram_value}"))
            layout.addWidget(QLabel(f"Decimal value: {int(bigram_value, 3)}"))
            layout.addWidget(QLabel(f"Sum of all highlighted values: {total_sum}"))

            # Add close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(summary_dialog.close)
            layout.addWidget(close_button)

            # Show the dialog without blocking
            summary_dialog.setModal(False)
            summary_dialog.show()

            logger.debug(f"Highlighted {len(matching_cells)} cells with matching bigram, sum: {total_sum}")

    def _on_kamea_locator(self):
        """Handle the Kamea Locator button click."""
        # Get the currently selected cell
        if self.kamea_grid.selected_cell is None:
            logger.warning("No cell selected for Kamea Locator")
            return

        row, col = self.kamea_grid.selected_cell

        # Convert to Cartesian coordinates
        x = col - self.kamea_grid.grid_size // 2
        y = self.kamea_grid.grid_size // 2 - row

        # Get the ternary value
        ternary_value = self.kamea_grid.get_kamea_value(row, col, False)
        if ternary_value is None:
            logger.warning("Could not get ternary value for selected cell")
            return

        # Ensure it's a string and padded to 6 digits
        ternary_str = str(ternary_value).zfill(6)

        # Extract the three bigrams (pairing from opposite ends)
        # For a 6-digit number, digit positions are 0-5 in the string
        # Digit 6 = position 0 (most significant/leftmost)
        # Digit 1 = position 5 (least significant/rightmost)
        bigram1 = ternary_str[0] + ternary_str[5]  # First bigram (digits 6 and 1)
        bigram2 = ternary_str[1] + ternary_str[4]  # Second bigram (digits 5 and 2)
        bigram3 = ternary_str[2] + ternary_str[3]  # Third bigram (digits 4 and 3)

        # Calculate the Kamea Locator (decimal values of the bigrams)
        # Order: 9×9 region (bigram3) - 3×3 area (bigram2) - cell (bigram1)
        locator = f"{int(bigram3, 3)}-{int(bigram2, 3)}-{int(bigram1, 3)}"

        # Update the Kamea Locator label
        self.kamea_locator_label.setText(f"Kamea Locator: {locator}")

        # Show more detailed information in a non-modal dialog
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        from PyQt6.QtCore import Qt

        # Create a non-modal dialog
        locator_dialog = QDialog(self, Qt.WindowType.Tool)
        locator_dialog.setWindowTitle("Kamea Locator")
        locator_dialog.setMinimumWidth(350)

        # Create layout
        layout = QVBoxLayout(locator_dialog)

        # Add information labels
        title_label = QLabel(f"Kamea Locator: {locator}")
        title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title_label)

        layout.addWidget(QLabel(f"Position: ({x}, {y})"))
        layout.addWidget(QLabel(f"Ternary Value: {ternary_str}"))

        # Add explanation
        layout.addWidget(QLabel("\nThe Kamea Locator is formed by converting each bigram to decimal:"))
        layout.addWidget(QLabel(f"Locator format: [9×9 region]-[3×3 area]-[cell]"))
        layout.addWidget(QLabel(f"Bigram 3 (9×9 region): {bigram3} → {int(bigram3, 3)}"))
        layout.addWidget(QLabel(f"Bigram 2 (3×3 area): {bigram2} → {int(bigram2, 3)}"))
        layout.addWidget(QLabel(f"Bigram 1 (cell in 3×3): {bigram1} → {int(bigram1, 3)}"))

        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(locator_dialog.close)
        layout.addWidget(close_button)

        # Show the dialog without blocking
        locator_dialog.setModal(False)
        locator_dialog.show()

    def _on_pattern_finder(self):
        """Handle the Pattern Finder button click."""
        # Create a non-modal dialog for pattern finding options
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
        from PyQt6.QtCore import Qt

        dialog = QDialog(self, Qt.WindowType.Tool)
        dialog.setWindowTitle("Pattern Finder")
        dialog.setMinimumWidth(300)
        dialog.setModal(False)

        layout = QVBoxLayout(dialog)

        # Create search type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Search Type:"))
        search_type = QComboBox()
        search_type.addItems(["Decimal Value", "Ternary Pattern", "Sum Value"])
        type_layout.addWidget(search_type)
        layout.addLayout(type_layout)

        # Create pattern input
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("Pattern:"))
        pattern_input = QLineEdit()
        pattern_layout.addWidget(pattern_input)
        layout.addLayout(pattern_layout)

        # Create buttons
        button_layout = QHBoxLayout()
        find_button = QPushButton("Find")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(find_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Connect buttons
        cancel_button.clicked.connect(dialog.reject)

        # Define the find action
        def on_find():
            pattern = pattern_input.text()
            search_mode = search_type.currentText()

            if not pattern:
                return

            # Find matching cells based on the search mode
            matching_cells = []

            if search_mode == "Decimal Value":
                try:
                    target = int(pattern)
                    # Search for cells with this decimal value
                    for row in range(self.kamea_grid.grid_size):
                        for col in range(self.kamea_grid.grid_size):
                            value = self.kamea_grid.get_kamea_value(row, col, True)
                            if value == target:
                                matching_cells.append((row, col))
                except ValueError:
                    logger.error(f"Invalid decimal value: {pattern}")

            elif search_mode == "Ternary Pattern":
                # Search for cells with this ternary pattern
                for row in range(self.kamea_grid.grid_size):
                    for col in range(self.kamea_grid.grid_size):
                        value = self.kamea_grid.get_kamea_value(row, col, False)
                        if value is not None and pattern in str(value).zfill(6):
                            matching_cells.append((row, col))

            elif search_mode == "Sum Value":
                try:
                    target = int(pattern)
                    # Search for quadsets that sum to this value
                    for row in range(self.kamea_grid.grid_size):
                        for col in range(self.kamea_grid.grid_size):
                            # Convert to Cartesian coordinates
                            x = col - self.kamea_grid.grid_size // 2
                            y = self.kamea_grid.grid_size // 2 - row

                            # Skip cells on axes (they don't form complete quadsets)
                            if x == 0 or y == 0:
                                continue

                            # Calculate the quadset
                            quadset_coords = [
                                (x, y),      # First quadrant
                                (-x, y),     # Second quadrant
                                (-x, -y),    # Third quadrant
                                (x, -y)      # Fourth quadrant
                            ]

                            # Convert to grid coordinates
                            grid_coords = []
                            for qx, qy in quadset_coords:
                                grid_row = self.kamea_grid.grid_size // 2 - qy
                                grid_col = qx + self.kamea_grid.grid_size // 2
                                if 0 <= grid_row < self.kamea_grid.grid_size and 0 <= grid_col < self.kamea_grid.grid_size:
                                    grid_coords.append((grid_row, grid_col))

                            # Calculate the sum
                            quad_sum = 0
                            for grid_row, grid_col in grid_coords:
                                value = self.kamea_grid.get_kamea_value(grid_row, grid_col, True)
                                if value is not None:
                                    quad_sum += value

                            # Check if the sum matches the target
                            if quad_sum == target:
                                matching_cells.extend(grid_coords)
                except ValueError:
                    logger.error(f"Invalid sum value: {pattern}")

            # Highlight the matching cells
            if matching_cells:
                self.kamea_grid.highlight_cells(matching_cells)
                logger.debug(f"Found {len(matching_cells)} cells matching pattern '{pattern}' in mode '{search_mode}'")

                # Calculate the sum of the highlighted cells
                total_sum = 0
                for r, c in matching_cells:
                    value = self.kamea_grid.get_kamea_value(r, c, True)  # Get decimal value
                    if value is not None:
                        total_sum += value

                # Show results in a non-modal dialog
                results_dialog = QDialog(self, Qt.WindowType.Tool)
                results_dialog.setWindowTitle("Pattern Finder Results")
                results_dialog.setMinimumWidth(300)

                results_layout = QVBoxLayout(results_dialog)

                title_label = QLabel(f"Found {len(matching_cells)} matching cells")
                title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
                results_layout.addWidget(title_label)

                results_layout.addWidget(QLabel(f"Search mode: {search_mode}"))
                results_layout.addWidget(QLabel(f"Pattern: {pattern}"))
                results_layout.addWidget(QLabel(f"Sum of all matching values: {total_sum}"))

                # Add close button
                close_results_button = QPushButton("Close")
                close_results_button.clicked.connect(results_dialog.close)
                results_layout.addWidget(close_results_button)

                # Show the results dialog without blocking
                results_dialog.setModal(False)
                results_dialog.show()
            else:
                # Show a message if no matches were found
                no_results_dialog = QDialog(self, Qt.WindowType.Tool)
                no_results_dialog.setWindowTitle("Pattern Finder Results")
                no_results_dialog.setMinimumWidth(300)

                no_results_layout = QVBoxLayout(no_results_dialog)

                title_label = QLabel("No matching cells found")
                title_label.setStyleSheet("font-weight: bold; font-size: 12pt;")
                no_results_layout.addWidget(title_label)

                no_results_layout.addWidget(QLabel(f"Search mode: {search_mode}"))
                no_results_layout.addWidget(QLabel(f"Pattern: {pattern}"))

                # Add close button
                close_no_results_button = QPushButton("Close")
                close_no_results_button.clicked.connect(no_results_dialog.close)
                no_results_layout.addWidget(close_no_results_button)

                # Show the no results dialog without blocking
                no_results_dialog.setModal(False)
                no_results_dialog.show()

                logger.warning(f"No cells found matching pattern '{pattern}' in mode '{search_mode}'")

            dialog.close()

        find_button.clicked.connect(on_find)

        # Show the dialog
        dialog.exec()


if __name__ == "__main__":
    """Simple demonstration of the Kamea of Maut panel."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = KameaOfMautPanel()
    panel.resize(1200, 800)
    panel.show()
    sys.exit(app.exec())
