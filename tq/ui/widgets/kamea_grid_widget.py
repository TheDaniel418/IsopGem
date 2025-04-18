"""
Purpose: Provides a widget for displaying the Kamea grid with interactive features

This file is part of the tq pillar and serves as a UI component.
It is responsible for rendering the Kamea grid and handling user interactions.

Key components:
- KameaGridWidget: Widget for rendering and interacting with the Kamea grid

Dependencies:
- PyQt6: For the user interface components
- tq.viewmodels.kamea_viewmodel: For the Kamea view model

Related files:
- tq/ui/panels/kamea_of_maut_panel.py: Panel that hosts this widget
- tq/viewmodels/kamea_viewmodel.py: View model that provides data and operations
- tq/services/kamea_service.py: Service that provides business logic
"""

import math
from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QPainter, QPen
from PyQt6.QtWidgets import QDialog, QLabel, QMenu, QSizePolicy, QVBoxLayout, QWidget

from tq.utils.difftrans_calculator import DiffTransCalculator
from tq.viewmodels.kamea_viewmodel import KameaViewModel


class KameaGridWidget(QWidget):
    """Widget for displaying the Kamea grid with interactive features."""

    # Signal emitted when a cell is selected
    cell_selected = pyqtSignal(int, int, int)  # row, col, value

    def __init__(self, view_model: Optional[KameaViewModel] = None, parent=None):
        """Initialize the Kamea grid widget.

        Args:
            view_model: The view model to use (creates a new one if None)
            parent: The parent widget
        """
        super().__init__(parent)

        # Set up the view model
        self.view_model = view_model or KameaViewModel()

        # Initialize grid properties
        self.grid_size = self.view_model.kamea_service.grid_size
        self.cell_size = 36  # Smaller cells to fit everything
        self.padding = 10  # Minimal padding

        # Set up widget properties with fixed size to ensure all cells are visible
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # Calculate exact size needed for 27x27 grid with cell size and padding
        grid_width = self.grid_size * self.cell_size + 2 * self.padding
        grid_height = self.grid_size * self.cell_size + 2 * self.padding
        self.setFixedSize(grid_width, grid_height)

        # Initialize selection state
        self.selected_cell = None

        self.current_highlight_colors = {}  # {(row, col): color}

    def paintEvent(self, _):
        """Handle paint events to draw the Kamea grid, including colored highlights."""
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

        # Draw center row (horizontal axis)
        painter.setPen(QPen(QColor(200, 200, 255), 2))
        painter.drawLine(
            self.padding,
            self.padding + center_row * self.cell_size,
            self.padding + self.grid_size * self.cell_size,
            self.padding + center_row * self.cell_size,
        )

        # Draw center column (vertical axis)
        painter.drawLine(
            self.padding + center_col * self.cell_size,
            self.padding,
            self.padding + center_col * self.cell_size,
            self.padding + self.grid_size * self.cell_size,
        )

        # Draw 9x9 grid lines (level 1 fractal)
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        for i in range(0, self.grid_size, 9):
            # Skip the center lines which are already drawn
            if i != center_row and i != 0 and i != self.grid_size:
                # Horizontal lines
                painter.drawLine(
                    self.padding,
                    self.padding + i * self.cell_size,
                    self.padding + self.grid_size * self.cell_size,
                    self.padding + i * self.cell_size,
                )
            if i != center_col and i != 0 and i != self.grid_size:
                # Vertical lines
                painter.drawLine(
                    self.padding + i * self.cell_size,
                    self.padding,
                    self.padding + i * self.cell_size,
                    self.padding + self.grid_size * self.cell_size,
                )

        # Draw 3x3 grid lines (level 2 fractal)
        painter.setPen(QPen(QColor(220, 220, 220), 1))
        for i in range(0, self.grid_size, 3):
            # Skip the lines that are already drawn
            if i % 9 != 0 and i != center_row:
                # Horizontal lines
                painter.drawLine(
                    self.padding,
                    self.padding + i * self.cell_size,
                    self.padding + self.grid_size * self.cell_size,
                    self.padding + i * self.cell_size,
                )
            if i % 9 != 0 and i != center_col:
                # Vertical lines
                painter.drawLine(
                    self.padding + i * self.cell_size,
                    self.padding,
                    self.padding + i * self.cell_size,
                    self.padding + self.grid_size * self.cell_size,
                )

        # Draw 1x1 grid lines (individual cells)
        painter.setPen(QPen(QColor(240, 240, 240), 0.5))
        for i in range(1, self.grid_size):
            if i % 3 != 0:  # Skip the lines that are already drawn
                # Horizontal lines
                painter.drawLine(
                    self.padding,
                    self.padding + i * self.cell_size,
                    self.padding + self.grid_size * self.cell_size,
                    self.padding + i * self.cell_size,
                )
                # Vertical lines
                painter.drawLine(
                    self.padding + i * self.cell_size,
                    self.padding,
                    self.padding + i * self.cell_size,
                    self.padding + self.grid_size * self.cell_size,
                )

        # Draw outer border
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(
            self.padding,
            self.padding,
            self.grid_size * self.cell_size,
            self.grid_size * self.cell_size,
        )

        # Draw colored highlights first (additive, persistent)
        for (row, col), color in self.current_highlight_colors.items():
            cell_x = self.padding + col * self.cell_size
            cell_y = self.padding + row * self.cell_size
            painter.fillRect(
                cell_x, cell_y, self.cell_size, self.cell_size, QColor(color)
            )
            painter.setPen(QPen(QColor(color), 2))
            painter.drawRect(cell_x, cell_y, self.cell_size, self.cell_size)

        # Draw primary highlighted cells (purple) AFTER drawing cell values
        if (
            hasattr(self.view_model, "highlighted_cells")
            and self.view_model.highlighted_cells
        ):
            primary_cells = self.view_model.highlighted_cells
            for row, col in primary_cells:
                cell_x = self.padding + col * self.cell_size
                cell_y = self.padding + row * self.cell_size
                # Fill the cell with a semi-transparent color
                painter.fillRect(
                    cell_x,
                    cell_y,
                    self.cell_size,
                    self.cell_size,
                    QColor(160, 32, 240, 100),  # Purple color with lower opacity
                )
                # Draw a border around the cell
                painter.setPen(
                    QPen(QColor(160, 32, 240), 2)
                )  # Purple color, thicker pen
                painter.drawRect(cell_x, cell_y, self.cell_size, self.cell_size)

        # Draw secondary highlighted cells (pastel green)
        if (
            hasattr(self.view_model, "secondary_highlighted_cells")
            and self.view_model.secondary_highlighted_cells
        ):
            secondary_cells = self.view_model.secondary_highlighted_cells
            for row, col in secondary_cells:
                cell_x = self.padding + col * self.cell_size
                cell_y = self.padding + row * self.cell_size
                # Fill the cell with a semi-transparent color
                painter.fillRect(
                    cell_x,
                    cell_y,
                    self.cell_size,
                    self.cell_size,
                    QColor(144, 238, 144, 100),  # Light pastel green with lower opacity
                )
                # Draw a border around the cell
                painter.setPen(QPen(QColor(0, 128, 0), 2))  # Green color, thicker pen
                painter.drawRect(cell_x, cell_y, self.cell_size, self.cell_size)

        # Draw cell values AFTER highlighting cells
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell_x = self.padding + col * self.cell_size
                cell_y = self.padding + row * self.cell_size

                # Get the value to display
                if self.view_model.decimal_mode:
                    value = self.view_model.kamea_service.get_kamea_value(
                        row, col, True
                    )
                else:
                    value = self.view_model.kamea_service.get_kamea_value(
                        row, col, False
                    )

                if value is not None:
                    # Adjust font size based on the value length
                    text = str(value)
                    font = painter.font()
                    if len(text) > 3:
                        font.setPointSize(7)
                    else:
                        font.setPointSize(9)
                    painter.setFont(font)

                    # Draw the text centered in the cell
                    painter.drawText(
                        cell_x,
                        cell_y,
                        self.cell_size,
                        self.cell_size,
                        Qt.AlignmentFlag.AlignCenter,
                        text,
                    )

        # Draw selected cell LAST
        if self.selected_cell:
            row, col = self.selected_cell
            cell_x = self.padding + col * self.cell_size
            cell_y = self.padding + row * self.cell_size
            painter.setPen(QPen(Qt.GlobalColor.red, 2))
            painter.drawRect(cell_x, cell_y, self.cell_size, self.cell_size)

        # Draw vector field if enabled
        if self.view_model.show_vectors and hasattr(self.view_model, "vectors"):
            # Draw vectors
            for v in self.view_model.vectors:
                if len(v) == 6 and v[4] == -1:
                    # DiffTrans vector with color: (origin_row, origin_col, row_res, col_res, -1, color)
                    row1, col1, row2, col2, difference, color = v
                    x1 = self.padding + col1 * self.cell_size + self.cell_size / 2
                    y1 = self.padding + row1 * self.cell_size + self.cell_size / 2
                    x2 = self.padding + col2 * self.cell_size + self.cell_size / 2
                    y2 = self.padding + row2 * self.cell_size + self.cell_size / 2
                    painter.setPen(QPen(QColor(color), 2))
                elif len(v) == 5 and v[4] == -1:
                    # Legacy DiffTrans vector: (origin_row, origin_col, row_res, col_res, -1)
                    row1, col1, row2, col2, difference = v
                    x1 = self.padding + col1 * self.cell_size + self.cell_size / 2
                    y1 = self.padding + row1 * self.cell_size + self.cell_size / 2
                    x2 = self.padding + col2 * self.cell_size + self.cell_size / 2
                    y2 = self.padding + row2 * self.cell_size + self.cell_size / 2
                    color = QColor(
                        160, 32, 240, 200
                    )  # Purple color with higher opacity
                    painter.setPen(QPen(color, 2))
                else:
                    # Old logic for regular vectors: (row, col, dx, dy, difference)
                    row, col, dx, dy, difference = v
                    x1 = self.padding + col * self.cell_size + self.cell_size / 2
                    y1 = self.padding + row * self.cell_size + self.cell_size / 2
                    conrune_row = row - dy  # Invert y for screen coordinates
                    conrune_col = col + dx
                    x2 = (
                        self.padding + conrune_col * self.cell_size + self.cell_size / 2
                    )
                    y2 = (
                        self.padding + conrune_row * self.cell_size + self.cell_size / 2
                    )
                    if (
                        hasattr(self.view_model, "color_by_diff")
                        and self.view_model.color_by_diff
                    ):
                        if (
                            self.view_model.max_vector_diff
                            > self.view_model.min_vector_diff
                        ):
                            norm_diff = (
                                difference - self.view_model.min_vector_diff
                            ) / (
                                self.view_model.max_vector_diff
                                - self.view_model.min_vector_diff
                            )
                        else:
                            norm_diff = 0.5
                        norm_diff = max(0.0, min(1.0, norm_diff))
                        hue = int(240 - norm_diff * 240)
                        saturation = 200 + int(55 * norm_diff)
                        value = 200 + int(55 * norm_diff)
                        hue = max(0, min(359, hue))
                        saturation = max(0, min(255, saturation))
                        value = max(0, min(255, value))
                        color = QColor.fromHsv(hue, saturation, value, 200)
                    else:
                        color = QColor(255, 0, 0, 150)
                    painter.setPen(QPen(color, 1))
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

                # Calculate midpoint for arrowhead (80% along the line)
                arrow_pos = 0.8  # Position arrowhead at 80% of the way
                mid_x = x1 + (x2 - x1) * arrow_pos
                mid_y = y1 + (y2 - y1) * arrow_pos

                # Draw arrowhead
                angle = math.atan2(y2 - y1, x2 - x1)

                # Use larger arrowhead for differential transformation vector
                if len(v) == 5 and v[4] == -1:
                    arrow_size = (
                        7  # Larger arrow for differential transformation vector
                    )
                else:
                    arrow_size = 5  # Standard size for regular vectors

                arrow_x1 = int(mid_x - arrow_size * math.cos(angle - math.pi / 6))
                arrow_y1 = int(mid_y - arrow_size * math.sin(angle - math.pi / 6))
                arrow_x2 = int(mid_x - arrow_size * math.cos(angle + math.pi / 6))
                arrow_y2 = int(mid_y - arrow_size * math.sin(angle + math.pi / 6))

                painter.drawLine(int(mid_x), int(mid_y), arrow_x1, arrow_y1)
                painter.drawLine(int(mid_x), int(mid_y), arrow_x2, arrow_y2)

            # Draw legend
            self.draw_color_legend(painter)

    def draw_color_legend(self, painter: QPainter) -> None:
        """Draw a color legend for the vector field.

        Args:
            painter: The QPainter to use
        """
        if (
            not hasattr(self.view_model, "color_by_diff")
            or not self.view_model.color_by_diff
        ):
            return

        # Set up legend dimensions
        legend_width = 100
        legend_height = 20
        legend_x = self.width() - legend_width - 10
        legend_y = 10

        # Draw gradient rectangle with HSV colors
        for i in range(legend_width):
            norm_diff = i / legend_width
            # Use HSV color space for better variation
            # Map difference to hue (0-359 degrees)
            hue = int(240 - norm_diff * 240)  # Blue (240) to Red (0)
            saturation = 200 + int(55 * norm_diff)  # More saturated for higher values
            value = 200 + int(55 * norm_diff)  # Brighter for higher values
            color = QColor.fromHsv(hue, saturation, value, 200)

            painter.setPen(QPen(color, 1))
            painter.drawLine(
                int(legend_x + i),
                int(legend_y),
                int(legend_x + i),
                int(legend_y + legend_height),
            )

        # Draw border
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawRect(
            int(legend_x), int(legend_y), int(legend_width), int(legend_height)
        )

        # Draw min/max labels
        painter.drawText(
            int(legend_x - 5),
            int(legend_y + legend_height + 15),
            "Min",
        )
        painter.drawText(
            int(legend_x + legend_width - 10),
            int(legend_y + legend_height + 15),
            "Max",
        )

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
            if self.view_model.decimal_mode:
                value = self.view_model.kamea_service.get_kamea_value(row, col, True)
            else:
                value = self.view_model.kamea_service.get_kamea_value(row, col, False)

            if value is None:
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
        self.view_model.highlighted_cells = cells
        self.update()

    def highlight_secondary_cells(self, cells: List[Tuple[int, int]]):
        """Highlight secondary cells (for OctaSet) with a different color.

        Args:
            cells: List of (row, col) tuples to highlight as secondary
        """
        self.view_model.secondary_highlighted_cells = cells
        self.update()

    def highlight_cells_with_colors(self, color_map):
        """Additively highlight cells with specific colors. First color wins for each cell."""
        for cell, color in color_map.items():
            if cell not in self.current_highlight_colors:
                self.current_highlight_colors[cell] = color
        self.update()

    def get_current_highlight_colors(self):
        """Return the current highlight color mapping."""
        return dict(self.current_highlight_colors)

    def clear_highlights(self):
        """Clear all cell highlights, including colored highlights."""
        self.current_highlight_colors.clear()
        if hasattr(self.view_model, "highlighted_cells"):
            self.view_model.clear_highlights()
        self.view_model.highlighted_cells = None
        self.view_model.secondary_highlighted_cells = None
        self.update()

    def draw_vector_field(self, vectors, color_by_diff=True):
        """Draw a vector field on the Kamea grid.

        Args:
            vectors: List of (row, col, dx, dy, difference) tuples
            color_by_diff: Whether to color vectors by difference value
        """
        self.view_model.vectors = vectors
        self.view_model.show_vectors = True
        self.view_model.color_by_diff = color_by_diff

        # Calculate min and max differences for color scaling
        if vectors:
            self.view_model.min_vector_diff = min(v[4] for v in vectors)
            self.view_model.max_vector_diff = max(v[4] for v in vectors)
        else:
            self.view_model.min_vector_diff = 0
            self.view_model.max_vector_diff = 1

        self.update()

    def clear_vector_field(self):
        """Clear the vector field."""
        self.view_model.clear_vectors()
        self.update()

    def set_view_mode(self, decimal_mode: bool):
        """Set the view mode.

        Args:
            decimal_mode: Whether to show decimal values (True) or ternary (False)
        """
        self.view_model.set_view_mode(decimal_mode)
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
        return self.view_model.kamea_service.get_kamea_value(row, col, decimal)

    def get_highlighted_cells(self):
        """Return the list of all currently highlighted cells (primary and color highlights)."""
        cells = set()
        if (
            hasattr(self.view_model, "highlighted_cells")
            and self.view_model.highlighted_cells
        ):
            cells.update(self.view_model.highlighted_cells)
        if self.current_highlight_colors:
            cells.update(self.current_highlight_colors.keys())
        return list(cells)

    def contextMenuEvent(self, event):
        """Show context menu on right-click for highlighted cells."""
        # Calculate which cell was clicked
        x = event.x() - self.padding
        y = event.y() - self.padding
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)
        # Only show menu if cell is highlighted
        highlighted = False
        if (
            hasattr(self.view_model, "highlighted_cells")
            and self.view_model.highlighted_cells
        ):
            highlighted = (row, col) in self.view_model.highlighted_cells
        if not highlighted and self.current_highlight_colors:
            highlighted = (row, col) in self.current_highlight_colors
        if not highlighted:
            return
        menu = QMenu(self)
        info_action = QAction("Show Quadset Info", self)
        menu.addAction(info_action)

        def show_info():
            self._show_quadset_info_popup(row, col)

        info_action.triggered.connect(show_info)
        menu.exec(event.globalPos())

    def _show_quadset_info_popup(self, row, col):
        """Show a non-modal popup with quadset info for the given cell."""
        # Gather quadset info using the service
        kamea_service = self.view_model.kamea_service
        x, y = kamea_service.convert_grid_to_cartesian(row, col)
        quadset_coords = kamea_service.get_quadset_coordinates(x, y)
        # Get decimal values
        quadset_decimals = []
        for qx, qy in quadset_coords:
            grid_row, grid_col = kamea_service.convert_cartesian_to_grid(qx, qy)
            val = kamea_service.get_kamea_value(grid_row, grid_col, True)
            quadset_decimals.append(val)
        # Conrune pairs (using first two and last two as pairs)
        if len(quadset_decimals) == 4:
            a, b, c, d = quadset_decimals
            conrune_pair1 = (a, b)
            conrune_pair2 = (c, d)
            diff1 = abs(a - b)
            diff2 = abs(c - d)
            difftrans = DiffTransCalculator.compute_difftrans([a, b, c, d])
            difftrans_tern = difftrans["padded_ternary"]
            difftrans_dec = difftrans["decimal"]
        else:
            a = b = c = d = diff1 = diff2 = difftrans_tern = difftrans_dec = None
        # Create the popup
        popup = QDialog(self)
        popup.setWindowTitle("Quadset Info")
        popup.setModal(False)
        layout = QVBoxLayout(popup)
        layout.addWidget(QLabel(f"Quadset coordinates: {quadset_coords}"))
        layout.addWidget(QLabel(f"Decimal values: {quadset_decimals}"))
        if len(quadset_decimals) == 4:
            layout.addWidget(QLabel(f"Conrune pairs: ({a}, {b}), ({c}, {d})"))
            layout.addWidget(QLabel(f"Differentials: |a-b| = {diff1}, |c-d| = {diff2}"))
            layout.addWidget(QLabel(f"DiffTrans (ternary): {difftrans_tern}"))
            layout.addWidget(QLabel(f"DiffTrans (decimal): {difftrans_dec}"))
        else:
            layout.addWidget(QLabel("(Incomplete quadset, cannot compute all values)"))
        popup.setLayout(layout)
        popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        popup.show()
