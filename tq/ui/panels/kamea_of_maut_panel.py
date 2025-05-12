"""
Purpose: Provides a panel for exploring the Kamea of Maut ternary fractal system

This file is part of the tq pillar and serves as a UI component.
It is responsible for displaying and analyzing the 27×27 Kamea of Maut,
which represents a fractal arrangement of ternary numbers with special properties.

Key components:
- KameaOfMautPanel: Main panel for displaying and interacting with the Kamea

Dependencies:
- PyQt6: For the user interface components
- tq.ui.widgets.kamea_grid_widget: For the Kamea grid display
- tq.viewmodels.kamea_viewmodel: For the Kamea view model
- tq.services.kamea_service: For the Kamea business logic

Related files:
- tq/ui/tq_tab.py: Tab that hosts this panel
- tq/ui/widgets/kamea_grid_widget.py: Widget for rendering the Kamea grid
- tq/viewmodels/kamea_viewmodel.py: View model for the Kamea
- tq/services/kamea_service.py: Service for Kamea operations
"""

from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from tq.services.kamea_service import KameaService
from tq.ui.widgets.kamea_grid_widget import KameaGridWidget
from tq.ui.widgets.temple_position_analyzer import TemplePositionDialog
from tq.utils.difftrans_calculator import DiffTransCalculator
from tq.viewmodels.kamea_viewmodel import KameaViewModel

# Import visualization components conditionally
# These will be imported in the handler methods when needed


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

        # Create the service and view model
        self.kamea_service = KameaService()
        self.view_model = KameaViewModel(self.kamea_service)

        # Create the layout with minimal margins to maximize space
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # No title or description to maximize space

        # Create the main content area
        content_layout = QHBoxLayout()

        # Create the Kamea grid widget
        self.kamea_grid = KameaGridWidget(self.view_model)
        self.kamea_grid.cell_selected.connect(self._on_cell_selected)

        # Create the control panel
        control_panel = self._create_control_panel()

        # Add a scroll area for the control panel to ensure it fits
        control_scroll = QScrollArea()
        control_scroll.setWidget(control_panel)
        control_scroll.setWidgetResizable(True)
        control_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        control_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        control_scroll.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding
        )
        control_scroll.setMinimumWidth(300)  # Fixed width for control panel
        control_scroll.setMaximumWidth(300)  # Fixed width for control panel

        # Add the grid and control panel to the content layout
        content_layout.addWidget(self.kamea_grid)
        content_layout.addWidget(control_scroll)

        # Add the content layout to the main layout
        self.layout.addLayout(content_layout)

        self._bigram_windows = []  # Track all open bigram analysis windows
        self._kamea_locator_windows = []  # Track all open Kamea Locator windows
        self._pattern_finder_windows = []  # Track all open Pattern Finder windows
        self._temple_position_windows = (
            []
        )  # Track all open Temple Position Analyzer windows
        self._family_network_windows = (
            []
        )  # Track all open Family Network Visualization windows
        self._integrated_network_windows = (
            []
        )  # Track all open Integrated Network Explorer windows

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

        # Create the coordinate navigation group with compact layout
        coord_group = QGroupBox("Coordinate Navigation")
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

        # Create the quadset analysis group with compact layout
        quadset_group = QGroupBox("Quadset Analysis")
        quadset_layout = QVBoxLayout(quadset_group)
        quadset_layout.setContentsMargins(5, 10, 5, 5)
        quadset_layout.setSpacing(2)

        # Add Show Quadset button
        show_quadset_button = QPushButton("Show Quadset")
        show_quadset_button.clicked.connect(self._on_show_quadset)
        quadset_layout.addWidget(show_quadset_button)

        # Add Show Transitions button
        show_transitions_button = QPushButton("Show Transitions")
        show_transitions_button.clicked.connect(self._on_show_transitions)
        quadset_layout.addWidget(show_transitions_button)

        # Add Clear Highlights button
        clear_highlights_button = QPushButton("Clear Highlights")
        clear_highlights_button.clicked.connect(self._on_clear_highlights)
        quadset_layout.addWidget(clear_highlights_button)

        # Add the quadset group to the control panel
        control_layout.addWidget(quadset_group)

        # Create the difference vector field group with compact layout
        vector_field_group = QGroupBox("Difference Vector Field")
        vector_field_layout = QVBoxLayout(vector_field_group)
        vector_field_layout.setContentsMargins(5, 10, 5, 5)
        vector_field_layout.setSpacing(2)

        # Add mode selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        mode_layout.addWidget(mode_label)

        # Create radio buttons for mode selection
        self.range_mode_radio = QRadioButton("Range")
        self.range_mode_radio.setChecked(True)  # Default to range mode
        self.specific_mode_radio = QRadioButton("Specific Value")

        # Add radio buttons to a button group
        mode_button_group = QButtonGroup(self)
        mode_button_group.addButton(self.range_mode_radio)
        mode_button_group.addButton(self.specific_mode_radio)

        # Connect radio buttons to change mode
        self.range_mode_radio.toggled.connect(self._on_vector_mode_changed)

        # Add radio buttons to the layout
        mode_layout.addWidget(self.range_mode_radio)
        mode_layout.addWidget(self.specific_mode_radio)

        vector_field_layout.addLayout(mode_layout)

        # Add range controls
        self.range_control_widget = QWidget()
        range_control_layout = QHBoxLayout(self.range_control_widget)
        range_control_layout.setContentsMargins(0, 0, 0, 0)

        # Minimum difference
        min_diff_label = QLabel("Min:")
        self.min_diff_input = QSpinBox()
        self.min_diff_input.setRange(0, 364)  # Maximum difference is 364
        self.min_diff_input.setValue(0)  # Start from 0 to include all differences
        range_control_layout.addWidget(min_diff_label)
        range_control_layout.addWidget(self.min_diff_input)

        # Maximum difference
        max_diff_label = QLabel("Max:")
        self.max_diff_input = QSpinBox()
        self.max_diff_input.setRange(0, 364)  # Maximum difference is 364
        self.max_diff_input.setValue(364)  # Set to maximum possible value
        range_control_layout.addWidget(max_diff_label)
        range_control_layout.addWidget(self.max_diff_input)

        vector_field_layout.addWidget(self.range_control_widget)

        # Add specific value control
        self.specific_control_widget = QWidget()
        specific_control_layout = QHBoxLayout(self.specific_control_widget)
        specific_control_layout.setContentsMargins(0, 0, 0, 0)

        # Specific difference value
        specific_diff_label = QLabel("Value:")
        self.specific_diff_input = QSpinBox()
        self.specific_diff_input.setRange(0, 364)  # Maximum difference is 364
        self.specific_diff_input.setValue(1)  # Default to 1
        specific_control_layout.addWidget(specific_diff_label)
        specific_control_layout.addWidget(self.specific_diff_input)

        vector_field_layout.addWidget(self.specific_control_widget)

        # Initially hide the specific control
        self.specific_control_widget.setVisible(False)

        # Add color control
        self.color_by_diff = QCheckBox("Color by Difference")
        self.color_by_diff.setChecked(True)
        vector_field_layout.addWidget(self.color_by_diff)

        # Add single vector button for highlighted cells
        show_highlighted_vectors_button = QPushButton(
            "Show Vectors for Highlighted Cells"
        )
        show_highlighted_vectors_button.setToolTip(
            "Display quadset vectors for all highlighted cells (must be valid Conrune cells)."
        )
        show_highlighted_vectors_button.clicked.connect(
            self._on_show_vectors_for_highlighted_cells
        )
        vector_field_layout.addWidget(show_highlighted_vectors_button)

        # Add DiffTrans toggle
        self.difftrans_toggle = QCheckBox("Show DiffTrans")
        self.difftrans_toggle.setToolTip(
            "Show vectors from the origin to the DiffTrans cell for each highlighted quadset."
        )
        self.difftrans_toggle.stateChanged.connect(self._on_difftrans_toggle)
        vector_field_layout.addWidget(self.difftrans_toggle)

        clear_vectors_button = QPushButton("Clear Vectors")
        clear_vectors_button.clicked.connect(self._on_clear_difference_vectors)
        vector_field_layout.addWidget(clear_vectors_button)

        # Add to control panel
        control_layout.addWidget(vector_field_group)

        # Create the advanced analysis group with compact layout
        adv_analysis_group = QGroupBox("Advanced Analysis")
        adv_analysis_layout = QVBoxLayout(adv_analysis_group)
        adv_analysis_layout.setContentsMargins(5, 10, 5, 5)
        adv_analysis_layout.setSpacing(2)

        # Add Bigram Analysis button
        bigram_button = QPushButton("Bigram Analysis")
        bigram_button.clicked.connect(self._on_bigram_analysis)
        adv_analysis_layout.addWidget(bigram_button)

        locator_button = QPushButton("Kamea Locator")
        locator_button.clicked.connect(self._on_kamea_locator)
        adv_analysis_layout.addWidget(locator_button)

        pattern_button = QPushButton("Pattern Finder")
        pattern_button.clicked.connect(self._on_pattern_finder)
        adv_analysis_layout.addWidget(pattern_button)

        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        adv_analysis_layout.addWidget(separator)

        # Add Temple Position Analyzer button
        temple_position_button = QPushButton("Temple Position Analyzer")
        temple_position_button.clicked.connect(self._on_temple_position_analyzer)
        adv_analysis_layout.addWidget(temple_position_button)

        # Add Family Network Visualization button
        family_network_button = QPushButton("Family Network Visualization")
        family_network_button.clicked.connect(self._on_family_network_visualization)
        adv_analysis_layout.addWidget(family_network_button)

        # Add Integrated Network Explorer button
        integrated_network_button = QPushButton("Integrated Network Explorer")
        integrated_network_button.clicked.connect(self._on_integrated_network_explorer)
        adv_analysis_layout.addWidget(integrated_network_button)

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

        # Add the information group to the control panel
        control_layout.addWidget(info_group)

        # Add a spacer to push everything up
        control_layout.addStretch(1)

        return control_panel

    def _on_view_mode_changed(self):
        """Handle changes to the view mode (decimal/ternary)."""
        decimal_mode = self.decimal_radio.isChecked()
        self.kamea_grid.set_view_mode(decimal_mode)

    def _on_vector_mode_changed(self):
        """Handle changes to the vector field mode (range/specific)."""
        range_mode = self.range_mode_radio.isChecked()
        self.range_control_widget.setVisible(range_mode)
        self.specific_control_widget.setVisible(not range_mode)

    def _on_cell_selected(self, row: int, col: int, value: any):
        """Handle cell selection in the Kamea grid.

        Args:
            row: The selected row
            col: The selected column
            value: The value at the selected cell
        """
        # Get cell information from the view model
        cell_info = self.view_model.select_cell(row, col)

        # Update the coordinate spinboxes
        self.x_coord.setValue(cell_info["x"])
        self.y_coord.setValue(cell_info["y"])

        # Update the information display
        self.position_label.setText(f"Position: ({cell_info['x']}, {cell_info['y']})")
        self.decimal_label.setText(f"Decimal: {cell_info['decimal_value']}")
        self.ternary_label.setText(f"Ternary: {cell_info['ternary_value']}")
        self.kamea_locator_label.setText(f"Kamea Locator: {cell_info['kamea_locator']}")

    def _on_go_to_coordinates(self):
        """Handle the Go to Coordinates button click."""
        # Get the Cartesian coordinates
        x = self.x_coord.value()
        y = self.y_coord.value()

        # Convert to grid coordinates
        row, col = self.kamea_service.convert_cartesian_to_grid(x, y)

        # Check if the coordinates are valid
        if (
            0 <= row < self.kamea_service.grid_size
            and 0 <= col < self.kamea_service.grid_size
        ):
            # Select the cell
            self.kamea_grid.selected_cell = (row, col)

            # Get the value and update information
            value = self.kamea_service.get_kamea_value(
                row, col, self.decimal_radio.isChecked()
            )
            self._on_cell_selected(row, col, value)

            # Update the display
            self.kamea_grid.update()
        else:
            logger.warning(f"Invalid coordinates: ({x}, {y})")

    def _on_show_quadset(self):
        """Handle the Show Quadset button click."""
        # Check if a cell is selected
        if self.kamea_grid.selected_cell is None:
            logger.warning("No cell selected")
            return

        # First, clear any existing highlights
        self.kamea_grid.clear_highlights()

        row, col = self.kamea_grid.selected_cell

        # Convert to Cartesian coordinates
        x, y = self.kamea_service.convert_grid_to_cartesian(row, col)

        # Show the quadset
        self.view_model.show_quadset(x, y)

        # Force a complete repaint
        self.kamea_grid.update()

    def _on_show_transitions(self):
        """Handle the Show Transitions button click."""
        if self.kamea_grid.selected_cell is None:
            logger.warning("No cell selected. Please select a cell first.")
            return
        row, col = self.kamea_grid.selected_cell
        result = self.view_model.show_conrune_transition(row, col)
        if result is None:
            logger.warning(
                "Could not calculate conrune transition for the selected cell."
            )
            return
        self.kamea_grid.highlight_cells([result["original_pos"], result["conrune_pos"]])
        self.kamea_grid.update()

    def _on_clear_highlights(self):
        """Handle the Clear Highlights button click."""
        self.kamea_grid.clear_highlights()

    def _on_show_vectors_for_highlighted_cells(self):
        """Show quadset vectors for all highlighted cells if they are valid Conrune cells."""
        highlighted_cells = (
            self.kamea_grid.get_highlighted_cells()
        )  # Should return list of (row, col)
        if not highlighted_cells:
            logger.warning("No cells are highlighted.")
            return
        # Check all highlighted cells are valid Conrune cells
        invalid_cells = []
        all_vectors = []
        for row, col in highlighted_cells:
            ternary_value = self.kamea_service.get_kamea_value(row, col, decimal=False)
            if ternary_value is None:
                invalid_cells.append((row, col))
                continue
            conrune_value = self.kamea_service.get_conrune_pair(str(ternary_value))
            if conrune_value is None:
                invalid_cells.append((row, col))
                continue
            x, y = self.kamea_service.convert_grid_to_cartesian(row, col)
            vectors = self.kamea_service.get_quadset_vectors(x, y)
            all_vectors.extend(vectors)
        if invalid_cells:
            logger.warning(
                "All highlighted cells must be valid Conrune cells to display vectors."
            )
            return
        # Show all vectors at once
        self.view_model.vectors = all_vectors
        self.view_model.show_vectors = True
        self.kamea_grid.update()
        # Also update DiffTrans vectors if toggle is on
        if self.difftrans_toggle.isChecked():
            self._show_difftrans_vectors()

    def _on_clear_difference_vectors(self):
        """Handle the Clear Vectors button click."""
        self.kamea_grid.clear_vector_field()

    def _on_bigram_analysis(self):
        """Handle the Bigram Analysis button click."""
        if self.kamea_grid.selected_cell is None:
            logger.warning("No cell selected. Please select a cell first.")
            return
        row, col = self.kamea_grid.selected_cell
        bigram_info = self.view_model.show_bigram_analysis(row, col)
        if "error" in bigram_info:
            logger.warning(bigram_info["error"])
            return
        import traceback

        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import (
            QComboBox,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        class BigramAnalysisWindow(QWidget):
            def __init__(self, parent, bigram_info, highlight_callback):
                super().__init__(parent)
                self.setWindowTitle("Bigram Analysis")
                self.setMinimumWidth(400)
                self.setWindowFlag(Qt.WindowType.Window, True)
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
                layout = QVBoxLayout(self)
                layout.addWidget(
                    QLabel(f"Ternary Value: {bigram_info['ternary_value']}")
                )
                layout.addWidget(
                    QLabel(
                        f"First Bigram (6-1): {bigram_info['bigram1']} (Decimal: {bigram_info['bigram1_dec']})"
                    )
                )
                layout.addWidget(
                    QLabel(
                        f"Second Bigram (5-2): {bigram_info['bigram2']} (Decimal: {bigram_info['bigram2_dec']})"
                    )
                )
                layout.addWidget(
                    QLabel(
                        f"Third Bigram (4-3): {bigram_info['bigram3']} (Decimal: {bigram_info['bigram3_dec']})"
                    )
                )
                # Only one dropdown for bigram type
                highlight_layout = QHBoxLayout()
                highlight_layout.addWidget(QLabel("Highlight cells with same:"))
                bigram_combo = QComboBox()
                bigram_combo.addItem("First Bigram (6-1)", 0)
                bigram_combo.addItem("Second Bigram (5-2)", 1)
                bigram_combo.addItem("Third Bigram (4-3)", 2)
                highlight_layout.addWidget(bigram_combo)
                layout.addLayout(highlight_layout)
                button_layout = QHBoxLayout()
                highlight_button = QPushButton("Highlight Matching Cells")

                def on_highlight():
                    bigram_index = bigram_combo.currentData()
                    # Get the bigram value from the selected cell's info
                    if bigram_index == 0:
                        bigram_value = bigram_info["bigram1"]
                    elif bigram_index == 1:
                        bigram_value = bigram_info["bigram2"]
                    else:
                        bigram_value = bigram_info["bigram3"]
                    highlight_callback(bigram_index, bigram_value)

                highlight_button.clicked.connect(on_highlight)
                button_layout.addWidget(highlight_button)
                close_button = QPushButton("Close")
                close_button.clicked.connect(self.close)
                button_layout.addWidget(close_button)
                layout.addLayout(button_layout)

        # Use the generic window removal method
        def _remove_bigram_window(window):
            self._remove_window(window, self._bigram_windows)

        try:
            win = BigramAnalysisWindow(
                None, bigram_info, self._highlight_matching_bigram
            )
            self._bigram_windows.append(win)
            win.show()
        except Exception as e:
            logger.error(
                f"Exception creating/showing BigramAnalysisWindow: {e}\n{traceback.format_exc()}"
            )
            if hasattr(self, "window_manager") and self.window_manager is not None:
                try:
                    win = BigramAnalysisWindow(
                        None, bigram_info, self._highlight_matching_bigram
                    )
                    self._bigram_windows.append(win)
                    self.window_manager.open_window(
                        "bigram_analysis", win, "Bigram Analysis"
                    )
                except Exception as e2:
                    logger.error(
                        f"window_manager fallback also failed: {e2}\n{traceback.format_exc()}"
                    )

    def _highlight_matching_bigram(self, bigram_index: int, bigram_value: str):
        """Highlight cells with a matching bigram.

        Args:
            bigram_index: 0 for first bigram, 1 for second, 2 for third
            bigram_value: The bigram value to match
        """
        # Get highlight information from the view model
        self.view_model.highlight_cells_with_bigram(bigram_index, bigram_value)

        # Update the display
        self.kamea_grid.update()

    def _on_kamea_locator(self):
        """Handle the Kamea Locator button click."""

        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import (
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QSpinBox,
            QVBoxLayout,
            QWidget,
        )

        class KameaLocatorWindow(QWidget):
            def __init__(self, parent, selected_cell, kamea_service, locate_callback):
                super().__init__(parent)
                self.setWindowTitle("Kamea Locator")
                self.setMinimumWidth(400)
                self.setWindowFlag(Qt.WindowType.Window, True)
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
                layout = QVBoxLayout(self)
                layout.addWidget(
                    QLabel(
                        "The Kamea Locator uses a region-area-cell format to locate cells in the Kamea."
                    )
                )
                layout.addWidget(QLabel("Format: region(0-8)-area(0-8)-cell(0-8)"))
                layout.addWidget(
                    QLabel("Region corresponds to the 9×9 region (third bigram).")
                )
                layout.addWidget(
                    QLabel(
                        "Area corresponds to the 3×3 area within a region (second bigram)."
                    )
                )
                layout.addWidget(
                    QLabel(
                        "Cell corresponds to the position within an area (first bigram)."
                    )
                )
                input_layout = QGridLayout()
                input_layout.addWidget(QLabel("Region:"), 0, 0)
                region_input = QSpinBox()
                region_input.setRange(0, 8)
                input_layout.addWidget(region_input, 0, 1)
                input_layout.addWidget(QLabel("Area:"), 1, 0)
                area_input = QSpinBox()
                area_input.setRange(0, 8)
                input_layout.addWidget(area_input, 1, 1)
                input_layout.addWidget(QLabel("Cell:"), 2, 0)
                cell_input = QSpinBox()
                cell_input.setRange(0, 8)
                input_layout.addWidget(cell_input, 2, 1)
                layout.addLayout(input_layout)
                if selected_cell is not None:
                    row, col = selected_cell
                    ternary_value = kamea_service.get_kamea_value(row, col, False)
                    if ternary_value is not None:
                        ternary_value = str(ternary_value).zfill(6)
                        kamea_locator = kamea_service.calculate_kamea_locator(
                            ternary_value
                        )
                        layout.addWidget(
                            QLabel(f"Selected Cell Locator: {kamea_locator}")
                        )
                        try:
                            region, area, cell = map(int, kamea_locator.split("-"))
                            region_input.setValue(region)
                            area_input.setValue(area)
                            cell_input.setValue(cell)
                        except Exception as e:
                            logger.error(f"Error parsing Kamea Locator: {e}")
                button_layout = QHBoxLayout()
                locate_button = QPushButton("Locate Cell")
                locate_button.clicked.connect(
                    lambda: locate_callback(
                        region_input.value(), area_input.value(), cell_input.value()
                    )
                )
                button_layout.addWidget(locate_button)
                close_button = QPushButton("Close")
                close_button.clicked.connect(self.close)
                button_layout.addWidget(close_button)
                layout.addLayout(button_layout)

        # Use the generic window removal method
        def _remove_locator_window(window):
            self._remove_window(window, self._kamea_locator_windows)

        try:
            win = KameaLocatorWindow(
                None,
                self.kamea_grid.selected_cell,
                self.kamea_service,
                self._locate_cell_by_locator,
            )
            self._kamea_locator_windows.append(win)
            win.destroyed.connect(lambda: _remove_locator_window(win))
            win.show()
        except Exception as e:
            logger.error(f"Exception creating/showing KameaLocatorWindow: {e}")

    def _on_pattern_finder(self):
        """Handle the Pattern Finder button click."""

        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import (
            QComboBox,
            QHBoxLayout,
            QLabel,
            QListWidget,
            QPushButton,
            QVBoxLayout,
            QWidget,
        )

        class PatternFinderWindow(QWidget):
            def __init__(
                self, parent, find_callback, show_pairs_callback, highlight_callback
            ):
                super().__init__(parent)
                self.setWindowTitle("Pattern Finder")
                self.setMinimumWidth(600)
                self.setMinimumHeight(400)
                self.setWindowFlag(Qt.WindowType.Window, True)
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
                layout = QVBoxLayout(self)
                layout.addWidget(
                    QLabel("Find patterns in the Kamea grid based on various criteria.")
                )
                pattern_layout = QHBoxLayout()
                pattern_layout.addWidget(QLabel("Pattern Type:"))
                pattern_combo = QComboBox()
                pattern_combo.addItem("Cells with Same Difference", "difference")
                pattern_combo.addItem("Cells with Same Sum", "sum")
                pattern_layout.addWidget(pattern_combo)
                layout.addLayout(pattern_layout)
                # Step 1: Quadsum list
                quadsum_label = QLabel("Quadsums:")
                layout.addWidget(quadsum_label)
                self.quadsum_list = QListWidget()
                layout.addWidget(self.quadsum_list)
                # Step 2: PairSum groupings
                pairs_label = QLabel("Conrune Pair Sums:")
                layout.addWidget(pairs_label)
                self.pairs_list = QListWidget()
                layout.addWidget(self.pairs_list)
                button_layout = QHBoxLayout()
                find_button = QPushButton("Find Patterns")
                find_button.clicked.connect(
                    lambda: find_callback(
                        pattern_combo.currentData(), self.quadsum_list, self.pairs_list
                    )
                )
                button_layout.addWidget(find_button)
                show_pairs_button = QPushButton("Show Pair Groups")
                show_pairs_button.clicked.connect(
                    lambda: show_pairs_callback(
                        pattern_combo.currentData(), self.quadsum_list, self.pairs_list
                    )
                )
                button_layout.addWidget(show_pairs_button)
                highlight_button = QPushButton("Highlight Selected Group")
                highlight_button.clicked.connect(
                    lambda: highlight_callback(
                        pattern_combo.currentData(), self.quadsum_list, self.pairs_list
                    )
                )
                button_layout.addWidget(highlight_button)
                close_button = QPushButton("Close")
                close_button.clicked.connect(self.close)
                button_layout.addWidget(close_button)
                layout.addLayout(button_layout)

        # Use the generic window removal method
        def _remove_pattern_window(window):
            self._remove_window(window, self._pattern_finder_windows)

        try:
            win = PatternFinderWindow(
                None,
                self._find_patterns,
                self._show_pair_groups,
                self._highlight_selected_pair_group,
            )
            self._pattern_finder_windows.append(win)
            win.destroyed.connect(lambda w=win: _remove_pattern_window(w))
            win.show()
        except Exception as e:
            logger.error(f"Exception creating/showing PatternFinderWindow: {e}")

    def _find_patterns(self, pattern_type: str, quadsum_list, pairs_list):
        """Step 1: Find patterns and populate the Quadsum list."""
        quadsum_list.clear()
        pairs_list.clear()
        if pattern_type == "sum":
            # Build quadsum -> (pairA, pairB) -> [quadsets]
            seen_quadsets = set()
            quadsum_dict = {}  # quadsum: {(pairA, pairB): [quadsets]}
            for x in range(-13, 14):
                for y in range(-13, 14):
                    if x == 0 or y == 0:
                        continue
                    if x < 0 or (x == 0 and y < 0):
                        continue
                    quadset_coords = self.kamea_service.get_quadset_coordinates(x, y)
                    quadset_grid_positions = []
                    for qx, qy in quadset_coords:
                        (
                            grid_row,
                            grid_col,
                        ) = self.kamea_service.convert_cartesian_to_grid(qx, qy)
                        if (
                            0 <= grid_row < self.kamea_service.grid_size
                            and 0 <= grid_col < self.kamea_service.grid_size
                        ):
                            quadset_grid_positions.append((grid_row, grid_col))
                    if len(quadset_grid_positions) != 4:
                        continue
                    quadset_key = tuple(sorted(quadset_grid_positions))
                    if quadset_key in seen_quadsets:
                        continue
                    seen_quadsets.add(quadset_key)
                    values = [
                        self.kamea_service.get_kamea_value(r, c, True)
                        for r, c in quadset_grid_positions
                    ]
                    if None in values:
                        continue
                    quadsum = sum(values)
                    # Split into two Conrune pairs (first two, last two)
                    pairA = values[0] + values[1]
                    pairB = values[2] + values[3]
                    pair_tuple = tuple(sorted((pairA, pairB)))
                    if quadsum not in quadsum_dict:
                        quadsum_dict[quadsum] = {}
                    if pair_tuple not in quadsum_dict[quadsum]:
                        quadsum_dict[quadsum][pair_tuple] = []
                    quadsum_dict[quadsum][pair_tuple].append(
                        list(quadset_grid_positions)
                    )
            self._last_quadsum_dict = quadsum_dict
            for quadsum in sorted(quadsum_dict.keys()):
                total = sum(len(v) for v in quadsum_dict[quadsum].values())
                quadsum_list.addItem(f"{quadsum} ({total} quadsets)")
        else:
            # Default difference logic (cell-based)
            patterns = self.view_model.find_patterns(pattern_type)
            for key, cells in sorted(patterns.items(), key=lambda x: int(x[0])):
                if len(cells) > 1:
                    label = f"Difference {key}: {len(cells)} cells"
                    quadsum_list.addItem(label)
            self._last_quadsum_dict = None

    def _show_pair_groups(self, pattern_type: str, quadsum_list, pairs_list):
        """Step 2: Show (PairSumA, PairSumB) groupings for the selected Quadsum."""
        pairs_list.clear()
        if pattern_type != "sum" or not self._last_quadsum_dict:
            return
        selected_items = quadsum_list.selectedItems()
        if not selected_items:
            return
        selected_text = selected_items[0].text()
        quadsum = int(selected_text.split()[0])
        pair_dict = self._last_quadsum_dict.get(quadsum, {})
        for pair_tuple, quadsets in sorted(pair_dict.items()):
            pairs_list.addItem(
                f"({pair_tuple[0]}, {pair_tuple[1]}) : {len(quadsets)} quadsets"
            )

    def _highlight_selected_pair_group(
        self, pattern_type: str, quadsum_list, pairs_list
    ):
        """Additively highlight all quadsets in the selected (PairSumA, PairSumB) group for the selected Quadsum.
        Previously highlighted cells remain until 'Clear Highlights' is pressed on the main UI.
        If a cell is already highlighted, its color is not changed (first group wins).
        """
        if pattern_type != "sum" or not self._last_quadsum_dict:
            return
        selected_quadsum = quadsum_list.selectedItems()
        selected_pair = pairs_list.selectedItems()
        if not selected_quadsum or not selected_pair:
            logger.warning("No quadsum or pair group selected")
            return
        quadsum = int(selected_quadsum[0].text().split()[0])
        pair_text = selected_pair[0].text()
        import re

        match = re.match(r"\((\d+),\s*(\d+)\)", pair_text)
        if not match:
            logger.warning(f"Could not parse pair tuple from: {pair_text}")
            return
        pair_tuple = (int(match.group(1)), int(match.group(2)))
        if pair_tuple not in self._last_quadsum_dict[quadsum]:
            logger.warning(f"Pair group {pair_tuple} not found for quadsum {quadsum}")
            return
        quadsets = self._last_quadsum_dict[quadsum][pair_tuple]
        palette = [
            "#e6194b",
            "#3cb44b",
            "#ffe119",
            "#4363d8",
            "#f58231",
            "#911eb4",
            "#46f0f0",
            "#f032e6",
            "#bcf60c",
            "#fabebe",
            "#008080",
            "#e6beff",
            "#9a6324",
            "#fffac8",
            "#800000",
            "#aaffc3",
            "#808000",
            "#ffd8b1",
            "#000075",
            "#808080",
            "#ffffff",
            "#000000",
        ]
        # Get current highlights/colors if available
        color_map = {}
        if hasattr(self.kamea_grid, "get_current_highlight_colors"):
            color_map = dict(self.kamea_grid.get_current_highlight_colors())
        elif hasattr(self.kamea_grid, "current_highlight_colors"):
            color_map = dict(self.kamea_grid.current_highlight_colors)
        all_cells = set(color_map.keys())
        for idx, quadset in enumerate(quadsets):
            color = palette[idx % len(palette)]
            for cell in quadset:
                if cell not in color_map:
                    color_map[cell] = color
                all_cells.add(cell)
        if hasattr(self.kamea_grid, "highlight_cells_with_colors"):
            self.kamea_grid.highlight_cells_with_colors(color_map)
        else:
            self.kamea_grid.highlight_cells(list(all_cells))

    def _locate_cell_by_locator(self, region: int, area: int, cell: int):
        """Locate a cell by its Kamea Locator components.

        Args:
            region: The region component (0-8)
            area: The area component (0-8)
            cell: The cell component (0-8)
        """
        cell_position = self.view_model.locator_to_cell(region, area, cell)
        if cell_position is None:
            logger.warning(f"Could not find cell with locator {region}-{area}-{cell}")
            return
        row, col = cell_position
        self.kamea_grid.selected_cell = (row, col)
        value = self.kamea_service.get_kamea_value(
            row, col, self.decimal_radio.isChecked()
        )
        self._on_cell_selected(row, col, value)
        self.kamea_grid.update()

    def _on_difftrans_toggle(self):
        """Handle toggling of the Show DiffTrans checkbox."""
        if self.difftrans_toggle.isChecked():
            self._show_difftrans_vectors()
        else:
            self._clear_difftrans_vectors()
        self.kamea_grid.update()

    def _show_difftrans_vectors(self):
        """Compute and draw DiffTrans vectors for all highlighted quadsets, using the same color mapping as highlights."""
        highlighted_cells = self.kamea_grid.get_highlighted_cells()
        if not highlighted_cells:
            return
        # Find unique quadsets from highlighted cells
        quadsets = []
        seen = set()
        for row, col in highlighted_cells:
            x, y = self.kamea_service.convert_grid_to_cartesian(row, col)
            quadset = tuple(self.kamea_service.get_quadset_coordinates(x, y))
            if len(quadset) == 4 and quadset not in seen:
                quadsets.append(quadset)
                seen.add(quadset)
        # Try to get the color mapping from the grid highlights
        color_map = {}
        if hasattr(self.kamea_grid, "get_current_highlight_colors"):
            color_map = dict(self.kamea_grid.get_current_highlight_colors())
        elif hasattr(self.kamea_grid, "current_highlight_colors"):
            color_map = dict(self.kamea_grid.current_highlight_colors)
        # Palette fallback (should match highlight function)
        palette = [
            "#e6194b",
            "#3cb44b",
            "#ffe119",
            "#4363d8",
            "#f58231",
            "#911eb4",
            "#46f0f0",
            "#f032e6",
            "#bcf60c",
            "#fabebe",
            "#008080",
            "#e6beff",
            "#9a6324",
            "#fffac8",
            "#800000",
            "#aaffc3",
            "#808000",
            "#ffd8b1",
            "#000075",
            "#808080",
            "#ffffff",
            "#000000",
        ]
        # Build a mapping from quadset to color (using the first cell in each quadset as key)
        quadset_color_map = {}
        for idx, quadset in enumerate(quadsets):
            # Try to get the color from the color_map (using any cell in the quadset)
            color = None
            for cell in quadset:
                if cell in color_map:
                    color = color_map[cell]
                    break
            if color is None:
                color = palette[idx % len(palette)]
            quadset_color_map[quadset] = color
        difftrans_vectors = []
        for quadset in quadsets:
            color = quadset_color_map[quadset]
            # Get decimal values for each cell in the quadset
            values = []
            for qx, qy in quadset:
                grid_row, grid_col = self.kamea_service.convert_cartesian_to_grid(
                    qx, qy
                )
                val = self.kamea_service.get_kamea_value(grid_row, grid_col, True)
                if val is None:
                    break
                values.append(val)
            if len(values) != 4:
                continue
            # Use DiffTransCalculator for canonical DiffTrans calculation
            difftrans = DiffTransCalculator.compute_difftrans(values)
            pos = self.kamea_service.find_cell_position(difftrans["padded_ternary"])
            if pos is None:
                continue
            row_res, col_res = pos
            # Enhanced debugging: print all relevant info
            print("\n--- DiffTrans Debug ---")
            print(f"Quadset values: {values}")
            print(
                f"DiffTrans (decimal): {difftrans['decimal']}, (ternary): {difftrans['padded_ternary']}"
            )
            print(f"Expected endpoint: ({row_res}, {col_res})")
            value_at_endpoint = self.kamea_service.get_kamea_value(
                row_res, col_res, True
            )
            print(f"Value at endpoint: {value_at_endpoint}")
            origin_row, origin_col = self.kamea_service.convert_cartesian_to_grid(0, 0)
            difftrans_vectors.append(
                (origin_row, origin_col, row_res, col_res, -1, color)
            )
        # Store and draw these vectors
        if not hasattr(self.view_model, "difftrans_vectors"):
            self.view_model.difftrans_vectors = []
        self.view_model.difftrans_vectors = difftrans_vectors
        # Merge with normal vectors for display
        all_vectors = getattr(self.view_model, "vectors", [])
        # Remove any previous difftrans vectors (difference == -1)
        all_vectors = [v for v in all_vectors if not (len(v) >= 5 and v[4] == -1)]
        all_vectors += difftrans_vectors
        self.view_model.vectors = all_vectors
        self.view_model.show_vectors = True
        self.kamea_grid.update()

    def _clear_difftrans_vectors(self):
        """Remove DiffTrans vectors from the display."""
        if hasattr(self.view_model, "difftrans_vectors"):
            # Remove only the DiffTrans vectors (marked with difference == -1)
            self.view_model.vectors = [
                v for v in getattr(self.view_model, "vectors", []) if v[2] != -1
            ]
            self.view_model.difftrans_vectors = []
        self.kamea_grid.update()

    def _on_temple_position_analyzer(self):
        """Handle the Temple Position Analyzer button click."""
        # Check if a cell is selected
        if self.kamea_grid.selected_cell is None:
            logger.warning("No cell selected. Please select a cell first.")
            return

        # Get the selected cell
        row, col = self.kamea_grid.selected_cell

        # Create the Temple Position Analyzer dialog
        dialog = TemplePositionDialog(self, self.kamea_service, row, col)

        # Track the dialog
        self._temple_position_windows.append(dialog)

        # Connect the dialog's finished signal to remove it from the list
        dialog.finished.connect(
            lambda: self._remove_window(dialog, self._temple_position_windows)
        )

        # Show the dialog
        dialog.show()

    def _on_family_network_visualization(self):
        """Handle the Family Network Visualization button click."""
        # Check if WebEngine is available
        try:
            from tq.ui.widgets.family_network_visualizer import (
                WEBENGINE_AVAILABLE,
                FamilyNetworkDialog,
            )

            # Create the Family Network Visualization dialog
            dialog = FamilyNetworkDialog(self, self.kamea_service)

            # Track the dialog
            self._family_network_windows.append(dialog)

            # Connect the dialog's finished signal to remove it from the list
            dialog.finished.connect(
                lambda: self._remove_window(dialog, self._family_network_windows)
            )

            # Show the dialog
            dialog.show()

            # Show a warning if WebEngine is not available
            if not WEBENGINE_AVAILABLE:
                logger.warning(
                    "PyQt6.QtWebEngineWidgets is not installed. The visualization will be limited."
                )

        except ImportError as e:
            logger.error(f"Error importing Family Network Visualizer: {e}")

    def _on_integrated_network_explorer(self):
        """Handle the Integrated Network Explorer button click (now managed by WindowManager)."""
        try:
            from tq.ui.widgets.integrated_network_explorer import (
                WEBENGINE_AVAILABLE,
                IntegratedNetworkDialog,
            )

            # Create the Integrated Network Explorer window as a true top-level window (parent=None)
            dialog = IntegratedNetworkDialog(None, self.kamea_service)
            # Use WindowManager if available
            if hasattr(self, "window_manager") and self.window_manager is not None:
                self.window_manager.open_window("ikna_explorer", dialog)
            else:
                dialog.show()
            if not WEBENGINE_AVAILABLE:
                logger.warning(
                    "PyQt6.QtWebEngineWidgets is not installed. The visualization will be limited."
                )
        except ImportError as e:
            logger.error(f"Error importing Integrated Network Explorer: {e}")

    def _remove_window(self, window, window_list):
        """Remove a window from a window list.

        Args:
            window: The window to remove
            window_list: The list to remove it from
        """
        if window in window_list:
            window_list.remove(window)


if __name__ == "__main__":
    """Simple demonstration of the Kamea of Maut panel."""
    import sys

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = KameaOfMautPanel()
    panel.resize(1200, 800)
    panel.show()
    sys.exit(app.exec())
